#!/usr/bin/env python
from __future__ import print_function

import sys

from setuptools import setup

if sys.version_info < (3, 6):
    error = """
    SenseMe supports Python 3.6 and above. Python 2.7 is not supported and will not work.

    Python {py} detected.

    Please install using pip3 on Python3.6 or above. 
    """.format(py='.'.join([str(v) for v in sys.version_info[:3]]))

    print(error, file=sys.stderr)
    sys.exit(1)


long_description = """HaikuHome SenseMe API for fans and lights.

A simple library to automate control and monitoring of network connected
 HaikuHome SenseMe devices.

Python 3.6 or above is required.
"""

setup(
    name="SenseMe",
    version="0.1.3",
    description="HaikuHome SenseMe API for fans and lights",
    author="Tom Faulkner",
    author_email="tomfaulkner@gmail.com",
    url="https://github.com/TomFaulkner/SenseMe",
    packages=["senseme", "senseme.lib", "bin"],
    license="GPL3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Home Automation"
    ],
    keywords="HaikuHome SenseMe fan light home automation bigassfans",
    python_requires=">=3.6",
    scripts=['bin/senseme_cli']
)
