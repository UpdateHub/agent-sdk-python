# Copyright (C) 2018 O.S. Systems Software LTDA.
"""
Sample script that cancels the update download action after receiving the
"enter download" state.
"""

from __future__ import print_function

import signal
import sys
import time

import updatehub


SCL = updatehub.StateChangeListener()


def signal_handler(*args):  # pylint: disable=unused-argument
    SCL.stop()
    sys.exit(0)


def callback(action, state, command):
    """
    Callback that will be called after the "enter download" is received.
    """
    print("CALLBACK: " + action + " " + state)
    print("Canceling the command...")
    command.cancel()
    print("Done!")


def error_callback(error_message, command):
    """
    Callback to be called after receiving an error state.
    """
    print("ERROR: " + error_message)
    print("Sending the retry in 10 seconds command...")
    command.try_again(10)
    print("Done!")


def main():
    """
    Main method. Instantiates a StateChangeListener, adds callbacks to the
    "enter download" state and the error state and then starts the listener.
    """
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    SCL.on_state_change(updatehub.Action.ENTER,
                        updatehub.State.DOWNLOADING,
                        callback)
    SCL.on_error(error_callback)

    SCL.start()

    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
