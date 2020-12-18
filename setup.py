#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sentry-dingtalk-ecool
==============

An extension for Sentry which integrates with Dingtalk. It will send
notifications to dingtalk robot with rich event info.

:copyright: (c) 2020 by Ang Yi Quan, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from setuptools import setup, find_packages

# See http://stackoverflow.com/questions/9352656/python-assertionerror-when-running-nose-tests-with-coverage
# for why we need to do this.
from multiprocessing import util


tests_require = []

install_requires = [
    "sentry>=20.0.0",
]


setup(
    name="sentry-dingtalk",
    version="1.1.0",
    keywords="sentry dingding dingtalk",
    author="Ang Yi Quan",
    author_email="ayq3490@gmail.com",
    url="https://github.com/lostncg/sentry-dingtalk",
    description="A Sentry extension which integrates with Dingtalk robot.",
    long_description=__doc__,
    long_description_content_type="text/markdown",
    license="BSD",
    platforms="any",
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    test_suite="nose.collector",
    entry_points={
        "sentry.plugins": ["sentry_dingtalk = sentry_dingtalk.plugin:DingtalkPlugin"],
    },
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
)
