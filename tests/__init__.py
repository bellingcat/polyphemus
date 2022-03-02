# -*- coding: UTF-8 -*-

"""This file seems to be necessary for `pytest-cov` to correctly compute code
coverage, when the tests are run from the project root directory with the
command:

  $ pytest

Though this file does not seem to be necessary when running the tests with the
command:

  $ python -m pytest

This seems to be a known issue with the `pytest` and `coverage` packages:

  * https://github.com/pytest-dev/pytest-cov/issues/401
  * https://stackoverflow.com/q/47287721/13026442

There's probably a clever way to fix this using `pytest.ini` or `.coveragerc`
files, but until I figure that out, this will have to do.

"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#