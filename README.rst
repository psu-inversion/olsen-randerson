===============
olsen-randerson
===============

Functions to perform the downscaling described in
[OlsenRanderson2004]_ and some of that described in [Fisheretal2016]_.

The support for the [Fisheretal2016]_ downscaling is incomplete.  In
particular, the rolling windows are not centered and the net flux does
not match the original.

Dependencies
============

The Olsen-Randerson downscaling functions depend on
`numpy <https://numpy.org/>`_, and the Fisher functions
additionally require `pandas <https://pandas.pydata.org>`_.

Testing
=======
To run the tests, run ``tox`` in the package root directory.
Tox will take care of installing the test dependencies.

References
==========

.. [Fisheretal2016] Fisher, J. B., Sikka, M., Huntzinger, D. N.,
    Schwalm, C., and Liu, J., 2016: Technical note: 3-hourly temporal
    downscaling of monthly global terrestrial biosphere model net
    ecosystem exchange, *Biogeosciences*, vol. 13, no. 14, 4271--4277,
    doi:`10.5194/bg-13-4271-2016 <https://dx.doi.org/10.5194/bg-13-4271-2016>`_.

.. [OlsenRanderson2004] Olsen, Seth C. and James T. Randerson, 2004.
    "Differences between surface and column atmospheric CO2 and
    implications for carbon cycle research," *Journal of Geophysical
    Research: Atmospheres* vol. 109, no. D2, D02301.
    doi:`10.1029/2003JD003968 <https://dx.doi.org/10.1029/2003JD003968>`_.
