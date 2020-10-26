# Copyright (C) 2018 O.S. Systems Software LTDA.
"""
Sample script that cancels the update download action after receiving the
"enter download" state.
"""

import signal
import sys

import updatehub.listener


SCL = updatehub.listener.StateChange()


def signal_handler(*args):  # pylint: disable=unused-argument
    SCL.stop()
    sys.exit(0)


def download_callback(_state, handler):
    print("function called when starting the Download state")
    print("it will cancel the transition")
    handler.cancel()


def install_callback(_state, handler):
    print("function called when starting the Install state")
    handler.proceed()


def rebooting_callback(_state, _handler):
    print("function called when starting the reboot state")
    SCL.stop()
    sys.exit(0)


def main():
    """
    Main method. Instantiates a StateChange, adds callbacks to the
    download state and the install state and then starts the listener.
    """
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    SCL.on_state(updatehub.listener.State.DOWNLOAD, download_callback)
    SCL.on_state(updatehub.listener.State.INSTALL, install_callback)
    SCL.on_state(updatehub.listener.State.REBOOT, rebooting_callback)

    SCL.start()

if __name__ == '__main__':
    main()
