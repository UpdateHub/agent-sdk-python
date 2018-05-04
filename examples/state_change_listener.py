# Copyright (C) 2018 O.S. Systems Software LTDA.
"""
Sample script that cancels the update download action after receiving the
"enter download" state.
"""

from __future__ import print_function

import updatehub


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
    scl = updatehub.StateChangeListener()
    scl.on_state_change(updatehub.Action.ENTER,
                        updatehub.State.DOWNLOADING,
                        callback)
    scl.on_error(error_callback)

    scl.start()


if __name__ == '__main__':
    main()
