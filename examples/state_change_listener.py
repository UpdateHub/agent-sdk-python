# Copyright (C) 2018 O.S. Systems Software LTDA.

from __future__ import print_function

import updatehub


def callback(action, state, command):
    print("CALLBACK: " + action + " " + state)
    print("Canceling the command...")
    command.cancel()
    print("Done!")


def error_callback(error_message, command):
    print("ERROR: " + error_message)
    print("Sending the retry in 10 seconds command...")
    command.try_again(10)
    print("Done!")


def main():
    scl = updatehub.StateChangeListener()
    scl.on_state_change(updatehub.Action.ENTER,
                        updatehub.State.DOWNLOADING,
                        callback)
    scl.on_error(error_callback)

    scl.start()


if __name__ == '__main__':
    main()
