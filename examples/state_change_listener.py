# Copyright (C) 2018 O.S. Systems Software LTDA.
"""
Sample script that cancels the update download action after receiving the
"enter download" state.
"""

import signal
import sys

import updatehub.listener


SCL = updatehub.listener.StateChangeListener()


def signal_handler(*args):  # pylint: disable=unused-argument
    SCL.stop()
    sys.exit(0)


def download_callback(state, command):
    """
    Callback that will be called after the "enter download" is received.
    """
    print("CALLBACK: " + state)
    print("Canceling the command...")
    command.cancel()
    print("Done!")


def error_callback(error_message, command):
    """
    Callback to be called after receiving an error state.
    """
    print("ERROR: " + error_message)
    command.proceed()
    print("Done!")


def rebooting_callback(state, _command):
    """
    Callback that will be called after the "enter download" is received.
    """
    print("CALLBACK: " + state)
    print("Stopping listener...")
    SCL.stop()
    sys.exit(0)


def main():
    """
    Main method. Instantiates a StateChangeListener, adds callbacks to the
    "enter download" state and the error state and then starts the listener.
    """
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    SCL.on_state_change(updatehub.listener.State.DOWNLOAD,
                        download_callback)
    SCL.on_state_change(updatehub.listener.State.REBOOT,
                        rebooting_callback)
    SCL.on_error(error_callback)

    SCL.start()

if __name__ == '__main__':
    main()
