# Copyright (C) 2018 O.S. Systems Software LTDA.

import updatehub


def callback(action, state, command):
    print("CALLBACK: " + action + " " + state)
    command.cancel()

def error_callback(error_message, command):
    print("ERROR: " + error_message)
    command.try_again(10)

def main():
    scl = updatehub.StateChangeListener()
    scl.on(updatehub.Action.ENTER, updatehub.State.DOWNLOADING, callback)
    scl.on_error(error_callback)

    scl.start()

if __name__ == '__main__':
    main()
