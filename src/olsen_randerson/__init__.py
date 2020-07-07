"""Temporal downscaling of fluxes following Olsen and Randerson (2004)."""
import numpy as np

from .__version__ import VERSION as __version__  # noqa: F401

NPP_TO_GPP_FACTOR = 2
"""Conversion factor to estimate GPP from NEE

The downscaling needs :abbr:`GPP (Gross Primary Productivity)`, but
often only :abbr:`NPP (Net Primary Productivity)` is available.  This
describes how to turn the latter into an estimate of the former.
"""
Q10 = 1.5
"""The :math:`Q_{10}` value used in the Olsen and Randerson downscaling.

It is the factor by which the respiration increases when the
temperature increases by ten degrees.
"""
T0 = 30
"""Baseline temperature for Olsen-Randerson downscaling.

Should be near the center of the temperature range.
"""


def olsen_randerson_once(
        flux_npp,
        flux_rh,
        temperature,
        par
):
    """Perform the Olson Randerson downscaling for a single month.

    Parameters
    ----------
    flux_npp : np.ndarray[...]
        Biogenic :abbr:`NPP (Net Primary Productivity)`, usually at
        monthly timescale.  Units must include time in the
        denominator.
    flux_rh : np.ndarray[...]
        Biogenic :abbr:`Rh (heterotrophic respiration)`, usually at
        monthly timescale.  Units must include time in the
        denominator.
    temperature : np.ndarray[N, ...]
        Temperature in Celsius, at the downscaled resolution.
        Units are expected to be degrees Celsius.
    par : np.ndarray[N, ...]
        :abbr:`PAR (Photosynthetically Active Radiation)`, at the
        downscaled resolution.
        :abbr:`PAR (Photosynthetically Active Radiation)` is defined
        to be greater than or equal to zero.

    Returns
    -------
    flux_nee : np.ndarray[N, ...]
        The downscaled :abbr:`NEP (Net Ecosystem Productivity)`.
        (positive is uptake by plants).

    References
    ----------
    Olsen, Seth C. and James T. Randerson, 2004.  "Differences between
    surface and column atmospheric CO2 and implications for carbon
    cycle research," *Journal of Geophysical Research: Atmospheres*
    vol. 109, no. D2, D02301.  :doi:`10.1029/2003JD003968`.

    Examples
    --------
    >>> time = np.arange(0, 3, .1)
    >>> par = -np.cos(2 * np.pi * time)
    >>> par[par < 0] = 0
    >>> temperature = 10 - 10 * np.cos(2 * np.pi * time)
    >>> # First item in row alternates between midnight and noon
    >>> olsen_randerson_once(np.array(5), np.array(0), temperature, par)
    array([-3.20043607, -3.4581163 , -4.2353102 ,  4.10768819, 18.33559721,
           23.70071827, 18.33559721,  4.10768819, -4.2353102 , -3.4581163 ,
           -3.20043607, -3.4581163 , -4.2353102 ,  4.10768819, 18.33559721,
           23.70071827, 18.33559721,  4.10768819, -4.2353102 , -3.4581163 ,
           -3.20043607, -3.4581163 , -4.2353102 ,  4.10768819, 18.33559721,
           23.70071827, 18.33559721,  4.10768819, -4.2353102 , -3.4581163 ])

    """
    assert par.shape == temperature.shape
    assert flux_npp.shape == flux_rh.shape
    # It is plausible that NPP < 0 in some seasons; I should probably
    # use different assumptions then.  GPP = - NPP, Rauto = -2 NPP?
    estimated_gpp = NPP_TO_GPP_FACTOR * flux_npp
    flux_gpp = olsen_randerson_gpp_once(
        estimated_gpp, par
    )
    flux_resp = olsen_randerson_resp_once(
        # Rauto
        estimated_gpp - flux_npp +
        # Rh
        flux_rh,
        temperature
    )
    return flux_gpp - flux_resp


def olsen_randerson_gpp_once(flux_gpp, par):
    """Downscale the GPP following Olsen and Randerson (2004).

    Parameters
    ----------
    flux_gpp : np.ndarray[...]
        The :abbr:`GPP (Gross Primary Productivity)` to downscale.
        Units must include time in denominator.
        :abbr:`GPP (Gross Primary Productivity)` is defined to be
        greater than or equal to zero.
    par : np.ndarray[N, ...]
        :abbr:`PAR (Photosynthetically Active Radiation)` at
        downscaled frequency.
        Will be used for the :abbr:`GPP (Gross Primary Productivity)`
        downscaling.
        :abbr:`PAR (Photosynthetically Active Radiation)` is defined
        to be greater than or equal to zero.

    Returns
    -------
    flux_gpp : np.ndarray[N, ...]
        The downscaled :abbr:`GPP (Gross Primary Productivity)`

    References
    ----------
    Olsen, Seth C. and James T. Randerson, 2004.  "Differences between
    surface and column atmospheric CO2 and implications for carbon
    cycle research," *Journal of Geophysical Research: Atmospheres*
    vol. 109, no. D2, D02301.  :doi:`10.1029/2003JD003968`.

    Examples
    --------
    >>> olsen_randerson_gpp_once(np.array(2.), np.array([0., 1, 1]))
    array([0., 3., 3.])
    >>> olsen_randerson_gpp_once(np.array(2.), np.array([0., 2, 2]))
    array([0., 3., 3.])
    """
    par_total = par.mean(axis=0)
    return (flux_gpp / par_total)[np.newaxis, ...] * par


def olsen_randerson_resp_once(flux_resp, temperature):
    """Downscale the respiration following Olsen and Randerson (2004).

    Parameters
    ----------
    flux_resp : np.ndarray[...]
        The original respiration fluxes to downscale.
        Units must include time in the denominator.
        Respiration fluxes are defined to be greater than or equal to zero.
    temperature : np.ndarray[N, ...]
        The temperature at the downscaled frequency.
        Expected units are degrees Celsius.

    Returns
    -------
    flux_resp : np.ndarray[N, ...]
        The downscaled respiration fluxes.

    References
    ----------
    Olsen, Seth C. and James T. Randerson, 2004.  "Differences between
    surface and column atmospheric CO2 and implications for carbon
    cycle research," *Journal of Geophysical Research: Atmospheres*
    vol. 109, no. D2, D02301.  :doi:`10.1029/2003JD003968`.

    Examples
    --------
    >>> olsen_randerson_resp_once(np.array(19./12.), np.array([0., 10., 20.]))
    array([1.  , 1.5 , 2.25])
    """
    resp_scaling = Q10 ** ((temperature - T0) / 10)
    resp_total = resp_scaling.mean(axis=0)
    return (flux_resp / resp_total)[np.newaxis, ...] * resp_scaling
