# -*- coding: UTF-8 -*-

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os.path
from setuptools import setup

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def readme( ):

  with open( os.path.abspath(
    os.path.join(
      os.path.dirname( __file__ ),
      'README.md' ) ) ) as f:

    return f.read( )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

setup(
  name = 'polyphemus',
  version = '0.1',
  description = 'Scraping Odysee video data',
  long_description = readme( ),
  author = 'Bellingcat',
  packages = [
    'polyphemus' ],
  install_requires = [
    'requests >= 2.27.0',
    'beautifulsoup4 >= 4.10.0',
    'pandas >= 1.4.0'],
  include_package_data = True,
  zip_safe = False )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#