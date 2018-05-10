# Copyright (C) 2018 O.S. Systems Software LTDA.
"""
This is the updatehub agent package SDK for the Python language. With this
package it's possible to access information about a running updatehub agent,
such as current states, log information and also force a new version probe.

For more information please access http://docs.updatehub.io/
"""


__version__ = '1.0.0'


def get_version():
    """
    Returns the current version of the package.
    """
    return __version__
