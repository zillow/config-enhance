__VERSION__ = "1.2.0"

import os
from setuptools import setup

def read(fname):
    '''Utility function to read the README file.'''
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# figure out what the install will need
install_requires = ["setuptools==0.9.8"]
tests_require = ["nose==1.1.2", "nosexcover==1.0.8", "coverage==3.5.2"] + install_requires

setup(
    name = "config-enhance",
    version = __VERSION__,
    author = "Jonathan Ultis",
    author_email = "jonathanu@zillow.com",
    description = read("README.md"),
    zip_safe = True,
    license = read("LICENSE"),
    keywords = "zillow",
    url = "https://stash.zillow.local/projects/LIBS/repos/egg.config-enhance/browse",
    packages = ['config_enhance'],
    long_description = read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
    ],
    install_requires = install_requires,
    tests_require = tests_require,
    test_suite = "nose.collector"
    )
