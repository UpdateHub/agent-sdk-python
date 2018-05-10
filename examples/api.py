# Copyright (C) 2018 O.S. Systems Software LTDA.
"""
Example to describe methods available on the API.
"""

from __future__ import print_function

from updatehub.api import Api


def main():
    """
    The execution of the program is simple: instantiate the API object and
    access every method available to it, printing it's return to STDOUT. The
    last method is the abort download to prevent any unwanted updates.
    """
    api = Api()
    print(api.get_info())
    print("")
    print(api.get_log())
    print("")
    print(api.probe())
    print("")
    print(api.probe("http://www.example.com:8080"))
    print("")
    print(api.abort_download())


if __name__ == '__main__':
    main()
