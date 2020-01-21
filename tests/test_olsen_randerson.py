"""Test the Olsen-Randerson downscaling."""
import numpy as np
import numpy.testing as np_tst

from hypothesis import given, assume
from hypothesis.extra.numpy import arrays
from hypothesis.strategies import floats

import olsen_randerson

TEST_LENGTH = 6
"""Number of time periods in test."""
UNREASONABLY_LARGE_FLUX_MAGNITUDE = 1e30
"""A flux that is unreasonably large in magnitude.

Needed to provide bounds for fluxes
"""


# Not entirely sure what units Photosynthetically Active Radiation is
# usually reported in, but I think 1e30 is bigger than anything that
# would be relevant.
@given(
    arrays(
        np.float, (3, 5), elements=floats(min_value=0, allow_infinity=False)
    ),
    arrays(
        np.float, (TEST_LENGTH, 3, 5),
        elements=floats(min_value=0, max_value=1e30)
    ).filter(
        lambda par: np.all(np.any(par != 0, axis=0))
    )
)
def test_olsen_randerson_gpp_once(flux_gpp, par):
    """Test single downscaling of GPP."""
    assume(np.all(np.any(par != 0, axis=0)))
    flux_gpp_downscaled = olsen_randerson.olsen_randerson_gpp_once(
        flux_gpp, par
    )
    assert flux_gpp_downscaled.shape == par.shape
    assert np.all(flux_gpp_downscaled >= 0)
    flux_gpp_downscaled_upscaled = flux_gpp_downscaled.sum(axis=0)
    assert flux_gpp_downscaled_upscaled.shape == flux_gpp.shape
    np_tst.assert_allclose(flux_gpp_downscaled_upscaled,
                           flux_gpp * TEST_LENGTH,
                           atol=1e-100)


@given(arrays(np.float, (3, 5),
              elements=floats(min_value=0, max_value=+UNREASONABLY_LARGE_FLUX_MAGNITUDE)),
       arrays(np.float, (TEST_LENGTH, 3, 5),
              elements=floats(min_value=-100, max_value=100)))
def test_olsen_randerson_resp_once(flux_resp, temperature):
    """Test single downscaling of respiration."""
    flux_resp_downscaled = olsen_randerson.olsen_randerson_resp_once(
        flux_resp, temperature
    )
    assert flux_resp_downscaled.shape == temperature.shape
    assert np.all(flux_resp_downscaled >= 0)
    flux_resp_downscaled_upscaled = flux_resp_downscaled.sum(axis=0)
    assert flux_resp_downscaled_upscaled.shape == flux_resp.shape
    np_tst.assert_allclose(flux_resp_downscaled_upscaled,
                           flux_resp * TEST_LENGTH,
                           atol=1e-100)


@given(
    arrays(
        np.float, (3, 5),
        elements=floats(min_value=-UNREASONABLY_LARGE_FLUX_MAGNITUDE,
                        max_value=+UNREASONABLY_LARGE_FLUX_MAGNITUDE)
    ),
    arrays(
        np.float, (TEST_LENGTH, 3, 5),
        elements=floats(min_value=-100, max_value=100)
    ),
    arrays(
        np.float, (TEST_LENGTH, 3, 5),
        elements=floats(min_value=0, max_value=1e30)
    ).filter(
        lambda par: np.all(np.any(par != 0, axis=0))
    )
)
def test_olsen_randerson_once(flux_nee, temperature, par):
    """Test single downscaling of NEE."""
    assume(np.all(np.any(par != 0, axis=0)))
    flux_nee_downscaled = olsen_randerson.olsen_randerson_once(
        flux_nee, temperature, par
    )
    assert flux_nee_downscaled.shape == temperature.shape
    flux_nee_downscaled_upscaled = flux_nee_downscaled.sum(axis=0)
    assert flux_nee_downscaled_upscaled.shape == flux_nee.shape
    np_tst.assert_allclose(flux_nee_downscaled_upscaled,
                           flux_nee * TEST_LENGTH,
                           atol=1e-100)
