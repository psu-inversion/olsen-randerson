"""Test the Fisher et al. downscaling."""
import functools
import operator

import numpy as np
import numpy.testing as np_tst
import pandas as pd

from hypothesis import given, assume
from hypothesis.extra.numpy import arrays
from hypothesis.strategies import floats

import olsen_randerson.fisher

MONTH_CENTER_INDEX = pd.to_datetime([
    "2014-12-15",
    "2015-01-15",
    "2015-02-14",
    "2015-03-15",
    "2015-04-15",
    "2015-05-15",
    "2015-06-15",
    "2015-07-15",
    "2015-08-15",
    "2015-09-15",
    "2015-10-15",
    "2015-11-15",
    "2015-12-15",
    "2016-01-15",
])
DAYS_PER_MONTH = pd.Series([31, 31, 28, 31, 30, 31, 30,
                            31, 31, 30, 31, 30, 31, 31],
                           index=MONTH_CENTER_INDEX)
COLUMNS = ["A", "B", "C"]

DOWNSCALED_INDEX = pd.date_range("2014-12-15T00:00:00",
                                 "2016-01-15T23:59:59",
                                 freq="1D")


@given(
    arrays(
        float, (len(MONTH_CENTER_INDEX), len(COLUMNS)),
        elements=floats(min_value=0, allow_infinity=False)
    ).map(
        functools.partial(pd.DataFrame,
                          index=MONTH_CENTER_INDEX,
                          columns=COLUMNS)
    ),
    arrays(
        float, (len(DOWNSCALED_INDEX), len(COLUMNS)),
        elements=floats(min_value=0, max_value=1e30)
    ).filter(lambda par: np.all(np.any(par != 0, axis=0))).map(
        functools.partial(pd.DataFrame,
                          index=DOWNSCALED_INDEX,
                          columns=COLUMNS)
    )
)
def test_downscale_gpp_timeseries(flux_gpp, par):
    """Test downscaling of GPP."""
    assume(np.all(np.any(par != 0, axis=0)))
    flux_gpp_downscaled = olsen_randerson.fisher.downscale_gpp_timeseries(
        flux_gpp, par
    )
    assert flux_gpp_downscaled.shape == par.shape
    assert np.all(flux_gpp_downscaled.iloc[1:-1] >= 0)
    flux_gpp_downscaled_upscaled = flux_gpp_downscaled.resample(
        olsen_randerson.fisher.INPUT_FREQUENCY
    ).sum()
    assert flux_gpp_downscaled_upscaled.shape == flux_gpp.shape
    # # I can only enforce equality for the NEE, not GPP and Resp
    # # separately, in the Fisher et al. framework.


@given(
    arrays(
        float, (len(MONTH_CENTER_INDEX), len(COLUMNS)),
        elements=floats(min_value=0, max_value=1e30)
    ).map(
        functools.partial(pd.DataFrame,
                          index=MONTH_CENTER_INDEX,
                          columns=COLUMNS)
    ),
    arrays(
        float, (len(DOWNSCALED_INDEX), len(COLUMNS)),
        elements=floats(min_value=-100, max_value=100)
    ).map(
        functools.partial(pd.DataFrame,
                          index=DOWNSCALED_INDEX,
                          columns=COLUMNS)
    )
)
def test_downscale_resp_timeseries(flux_resp, temperature):
    """Test downscaling of Respiration."""
    flux_resp_downscaled = olsen_randerson.fisher.downscale_resp_timeseries(
        flux_resp, temperature
    )
    assert flux_resp_downscaled.shape == temperature.shape
    # assert np.all(flux_resp_downscaled.iloc[1:-1, :] >= 0)
    np_tst.assert_array_compare(
        operator.ge,
        flux_resp_downscaled.iloc[1:-1, :],
        0
    )
    flux_resp_downscaled_upscaled = flux_resp_downscaled.resample(
        olsen_randerson.fisher.INPUT_FREQUENCY
    ).sum()
    assert flux_resp_downscaled_upscaled.shape == flux_resp.shape
    # # I can only enforce equality for the NEE, not GPP and Resp
    # # separately, in the Fisher et al. framework.


@given(
    arrays(
        float, (len(MONTH_CENTER_INDEX), len(COLUMNS)),
        elements=floats(min_value=-1e30, max_value=1e30)
    ).map(
        functools.partial(pd.DataFrame,
                          index=MONTH_CENTER_INDEX,
                          columns=COLUMNS)
    ),
    arrays(
        float, (len(DOWNSCALED_INDEX), len(COLUMNS)),
        elements=floats(min_value=-100, max_value=100)
    ).map(
        functools.partial(pd.DataFrame,
                          index=DOWNSCALED_INDEX,
                          columns=COLUMNS)
    ),
    arrays(
        float, (len(DOWNSCALED_INDEX), len(COLUMNS)),
        elements=floats(min_value=0, max_value=1e30)
    ).filter(lambda par: np.all(np.any(par != 0, axis=0))).map(
        functools.partial(pd.DataFrame,
                          index=DOWNSCALED_INDEX,
                          columns=COLUMNS)
    )
)
def test_downscale_nee_timeseries(flux_nee, temperature, par):
    """Test downscaling of NEE."""
    flux_nee_downscaled = olsen_randerson.fisher.downscale_timeseries(
        flux_nee, temperature, par
    )
    assert flux_nee_downscaled.shape == temperature.shape
    flux_nee_downscaled_upscaled = flux_nee_downscaled.resample(
        olsen_randerson.fisher.INPUT_FREQUENCY
    ).sum()
    assert flux_nee_downscaled_upscaled.shape == flux_nee.shape
