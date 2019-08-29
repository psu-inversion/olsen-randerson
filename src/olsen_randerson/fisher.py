"""Modifications to the downscaling by Fisher et al. (2016).

Changes from the Olsen-Randerson downscaling are primarily to prevent
discontinuities at month change.

I do not know whether the rolling windows used in Fisher et al. (2016)
were centered on the given time or ending on the given time.  At
present, this code uses rolling windows ending on the given day,
because that is easy to get pandas to do.
"""

from . import NEP_TO_GPP_FACTOR, Q10, T0

INPUT_FREQUENCY = "1M"
"""The frequency at which the input data are given.

Used to ensure the downscaled fluxes match the predictions of the
original fluxes.
"""


def downscale_timeseries(flux_nee, temperature, par):
    """Downscale the columns of flux_nee.

    The parts of the downscaled flux corresponding to the first and
    last time periods in the original flux will be incomplete.  It is
    recommended to provide an extra time period on each end to avoid
    this.

    Parameters
    ----------
    flux_nee : pd.DataFrame[N_large, M]
        Net Ecosystem Exchange, at the large timesteps.
        Must have datetime index.
        Positive indicates carbon is entering the atmosphere.
        Units must have time in denominator.
    temperature : pd.DataFrame[N, M]
        Temperature at the small timesteps.
        Must have datetime index with a set frequency
        Unit is expected to be degrees Celsius.
    par : pd.DataFrame[N, M]
        Photosynthetically active radiation at the small timesteps.
        Must be greather than or equal to zero.
        Must have datetime index with a set frequency.

    Returns
    -------
    flux_nee : pd.DataFrame[N, M]

    References
    ----------
    Fisher, J. B., Sikka, M., Huntzinger, D. N., Schwalm, C., and Liu,
    J., 2016: Technical note: 3-hourly temporal downscaling of monthly
    global terrestrial biosphere model net ecosystem exchange,
    *Biogeosciences*, vol. 13, no. 14, 4271--4277,
    :doi:`10.5194/bg-13-4271-2016`.
    """
    estimated_gpp = -NEP_TO_GPP_FACTOR * flux_nee
    flux_gpp = downscale_gpp_timeseries(
        estimated_gpp, par
    )
    flux_resp = downscale_resp_timeseries(
        estimated_gpp + flux_nee, temperature
    )
    downscaled_nee = flux_resp - flux_gpp
    return downscaled_nee


def downscale_gpp_timeseries(flux_gpp, par):
    """Downscale the columns of flux_nee.

    Parameters
    ----------
    flux_gpp : pd.DataFrame[N_large, M]
        Gross Primary productivity at the larger timesteps.
        Must have a datetime index.
        Units must have time in the denominator.
    par : pd.DataFrame[N, M]
        Photosynthetically active radiation at the small timesteps.
        Must be greather than or equal to zero.
        Must have datetime index with a set frequency.

    Returns
    -------
    flux_gpp : pd.DataFrame[N, M]

    References
    ----------
    Fisher, J. B., Sikka, M., Huntzinger, D. N., Schwalm, C., and Liu,
    J., 2016: Technical note: 3-hourly temporal downscaling of monthly
    global terrestrial biosphere model net ecosystem exchange,
    *Biogeosciences*, vol. 13, no. 14, 4271--4277,
    :doi:`10.5194/bg-13-4271-2016`.
    """
    # This is mean over thirty days prior to the given day.
    # I can't figure out how to get a centered window.
    par_mean = par.rolling("30D").mean()
    # Get the GPP timeseries to the same timestep as par
    flux_gpp_baseline = flux_gpp.resample(
        par.index.freq
    ).interpolate(method="time")
    # This would be where I would deal with the first and last several
    # timesteps.
    return flux_gpp_baseline / par_mean * par


def downscale_resp_timeseries(flux_resp, temperature):
    """Downscale the columns of flux_resp.

    Parameters
    ----------
    flux_resp : pd.DataFrame[N_large, M]
        Respiration fluxes at the larger timesteps.
        Must have a datetime index.
        Units must have time in denominator.
    temperature : pd.DataFrame[N, M]
        Temperature at the small timesteps.
        Must have datetime index with a set frequency
        Unit is expected to be degrees Celsius.

    Returns
    -------
    flux_resp : pd.DataFrame[N, M]

    References
    ----------
    Fisher, J. B., Sikka, M., Huntzinger, D. N., Schwalm, C., and Liu,
    J., 2016: Technical note: 3-hourly temporal downscaling of monthly
    global terrestrial biosphere model net ecosystem exchange,
    *Biogeosciences*, vol. 13, no. 14, 4271--4277,
    :doi:`10.5194/bg-13-4271-2016`.
    """
    resp_scaling = Q10 ** ((temperature - T0) / 10)
    # This is mean over thirty days prior to the given day.
    # I can't figure out how to get a centered window.
    resp_mean = resp_scaling.rolling("30D").mean()
    # Get the Respiration timeseries on the same timestep as
    # temperature
    flux_resp_baseline = flux_resp.resample(
        temperature.index.freq
    ).interpolate(method="time")
    # This is where I would deal with the first and last several
    # timesteps.
    return flux_resp_baseline / resp_mean * resp_scaling
