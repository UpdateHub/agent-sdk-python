# Copyright (C) 2018 O.S. Systems Software LTDA.

from __future__ import print_function

import io
import os
import socket
import threading


from enum import Enum
from enum import unique


__version__ = '0.0.1'


def get_version():
    return __version__


@unique  # pylint: disable=too-few-public-methods
class Action(Enum):
    ENTER = "enter"
    LEAVE = "leave"


@unique  # pylint: disable=too-few-public-methods
class State(Enum):
    IDLE = "idle"
    POLL = "poll"
    PROBE = "probe"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    INSTALLING = "installing"
    INSTALLED = "installed"
    EXIT = "exit"
    ERROR = "error"
    REBOOTING = "rebooting"


class StateCommand(object):
    def __init__(self, connection):
        self._connection = connection

    def cancel(self):
        self._send_message(StateChangeListener.CANCEL_MESSAGE)

    def try_again(self, seconds):
        message = StateChangeListener.TRY_AGAIN_MESSAGE + " " + str(seconds)
        self._send_message(message)

    def _send_message(self, message):
        self._connection.send(message.encode())


class MalformedState(Exception):
    pass


class StateError(Exception):
    pass


class StateChangeListener(object):
    SDK_TRIGGER_FILENAME = ("/usr/share/updatehub/state-change-callbacks.d/"
                            "10-updatehub-sdk-statechange-trigger")
    SOCKET_PATH = "/run/updatehub-statechange.sock"
    CANCEL_MESSAGE = "cancel"
    TRY_AGAIN_MESSAGE = "try_again"

    def __init__(self):
        self.error_handlers = []
        self.listeners = {}
        self.sock = None
        self.running = False
        self.thread = threading.Thread(target=self._loop)

    def on_state_change(self, action, state, callback):
        key = action.value + "_" + state.value
        if self.listeners.get(key) is None:
            self.listeners[key] = []
        self.listeners[key].append(callback)

    def on_error(self, callback):
        self.error_handlers.append(callback)

    def start(self):
        if not os.path.isfile(StateChangeListener.SDK_TRIGGER_FILENAME):
            print("updatehub-sdk-statechange-trigger not found!")
            exit(1)

        self.running = True
        self.thread.start()

    @classmethod
    def _get_state(cls, line):
        parts = line.split(' ')

        if parts[0] == "error":
            raise StateError(" ".join(parts[1:]))

        if len(parts) < 2:
            raise MalformedState()

        return parts[0], parts[1]

    @classmethod
    def _readline(cls, conn):
        buff = io.BytesIO()
        while True:
            data = conn.recv(16)
            buff.write(data)
            if b'\n' in data:
                break
        return buff.getvalue().splitlines()[0].decode("utf-8")

    def _loop(self):
        while self.running:
            try:
                self._connect()
                self._wait_for_state()
            except OSError as exception:
                if self.running is False and exception.errno == 9:
                    pass
                else:
                    self.running = False
                    raise exception
            except Exception as exception:
                self.running = False
                raise exception
            finally:
                self.sock.close()

    def stop(self):
        self.running = False
        self.sock.close()
        self.thread.join()

    def _wait_for_state(self):
        while True:
            conn = None
            try:
                conn = self.sock.accept()[0]
                line = self._readline(conn)
                action, state = self._get_state(line)
                self._emit(action, state, conn)
            except StateError as exception:
                self._throw_error(exception, conn)
            finally:
                if conn is not None:
                    conn.close()

    def _connect(self):
        if os.path.exists(StateChangeListener.SOCKET_PATH):
            os.remove(StateChangeListener.SOCKET_PATH)

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(StateChangeListener.SOCKET_PATH)
        self.sock.listen(1)

    def _emit(self, action, state, connection):
        key = action + "_" + state
        for callback in self.listeners.get(key) or []:
            command = StateCommand(connection)
            callback(action, state, command)

    def _throw_error(self, exception, connection):
        for callback in self.error_handlers:
            command = StateCommand(connection)
            callback(str(exception), command)
