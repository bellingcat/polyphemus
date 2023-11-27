# -*- coding: UTF-8 -*-

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os.path

from setuptools import setup


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#


def readme():
    with open(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "README.md"))
    ) as f:
        return f.read()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

setup(
    name="polyphemus",
    version="0.2",
    description="Scraping Odysee video data",
    long_description=readme(),
    author="Bellingcat",
    packages=["polyphemus"],
    install_requires=["requests", "beautifulsoup4", "pandas"],
    extras_require={
        "docs": [
            "sphinx >= 3.3.1",
            "sphinx_rtd_theme >= 0.5",
        ],
        "tests": [
            "pytest >= 6.1.2",
            "pytest-cov >= 2.10.1",
            "pytest-html >= 3.0.0",
            "pytest-metadata >= 1.10.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={"console_scripts": ["polyphemus = polyphemus._cli:main"]},
)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
