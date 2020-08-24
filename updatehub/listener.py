# Copyright (C) 2018 O.S. Systems Software LTDA.
"""
Use this package to be notified of changes on the current state of the
updatehub agent by registering callbacks.
"""

import io
import os
import socket
import threading

from enum import Enum
from enum import unique


@unique  # pylint: disable=too-few-public-methods
class State(Enum):
    """
    A enum class that contains all states of the updatehub agent.

    :IDLE: triggered when the agent enters a idle state (doing nothing).
    :POLL: triggered when the agent is waiting to probe the server for a new
           update on the expected schedule.
    :PROBE: triggered when the agent is probing the server for a new update.
    :DOWNLOADING: triggered when the agent is downloading a new update.
    :DOWNLOADED: triggered when the agent has finished downloading a new
                 update.
    :INSTALLING: triggered when the agent is installing a new update.
    :INSTALLED: triggered when the agent has finished installing a new update.
    :REBOOTING: triggered when the agent is rebooting the device.
    :EXIT: triggered when the agent has finished execution and has exited.
    :ERROR: triggered when the agent has encountered an error.
    """
    IDLE = "idle"
    POLL = "poll"
    PROBE = "probe"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    INSTALLING = "installing"
    INSTALLED = "installed"
    REBOOTING = "rebooting"
    EXIT = "exit"
    ERROR = "error"


class StateCommand:
    """
    A command class whose objects can be used to send commands back to the
    agent.
    """
    CANCEL_MESSAGE = "cancel"
    """
    The cancel command message to be sent back to the agent to stop whatever it
    is doing.
    """
    TRY_AGAIN_MESSAGE = "try_again"
    """
    The try_again command message to be sent back to the agent to try again
    something. This message is also accompanied by a delay integer, expressed
    in seconds, which is a parameter for the try_again method (see bellow).
    """

    def __init__(self, connection):
        """
        Initializes the command object.

        :connection: an already open socket connection to the agent.
        :return: None
        """
        self._connection = connection

    def cancel(self):
        """
        Cancels the current action on the agent.
        """
        self._send_message(StateCommand.CANCEL_MESSAGE)

    def try_again(self, delay):
        """
        Tell the agent to try the action again after some time.

        :seconds: the time delay in seconds to try the action again.
        """
        message = StateCommand.TRY_AGAIN_MESSAGE + " " + str(delay)
        self._send_message(message)

    def _send_message(self, message):
        self._connection.send(message.encode())


class MalformedState(Exception):
    """
    Exception class raised on errors of the communication protocol on the
    socket.
    """


class StateError(Exception):
    """
    Exception class raised when receiving errors from the agent execution.
    """


class StateChangeListener:
    """
    Listener class for the agent. Objects from this class monitor a Unix socket
    that will receive data from the agent, and triggers registered callbacks
    methods.

    The listener uses a thread to monitor the agent. On each received message
    the listener check the message against every registered callback,
    triggering it when it matches the state and the action associated with the
    callback.

    Keep in mind that this means that the callback must be ready to act out of
    the context of the main program thread.
    """

    SDK_TRIGGER_FILENAME = ("/usr/share/updatehub/state-change-callbacks.d/"
                            "10-updatehub-sdk-statechange-trigger")
    """
    Program called by the agent to push a state change through the Unix
    socket. It must be present and on this location for the listener to work.

    A copy of this program can be found here:
    https://raw.githubusercontent.com/updatehub/meta-updatehub/master/recipes-core/updatehub/updatehub-sdk-statechange-trigger/10-updatehub-sdk-statechange-trigger
    """

    SOCKET_PATH = "/run/updatehub-statechange.sock"
    """
    The Unix socket path. It's always recreated when starting a new listener.
    """

    @classmethod
    def _get_state(cls, line):
        parts = line.split(' ')

        if parts[0] == "error":
            raise StateError(" ".join(parts[1:]))

        if len(parts) < 1:
            raise MalformedState()

        return parts[0]

    @classmethod
    def _readline(cls, conn):
        buff = io.BytesIO()
        while True:
            data = conn.recv(16)
            buff.write(data)
            if b'\n' in data:
                break
        return buff.getvalue().splitlines()[0].decode("utf-8")

    def __init__(self):
        """
        Creates a new listener.
        """
        self.error_handlers = []
        self.listeners = {}
        self.sock = None
        self.running = False
        self.thread = threading.Thread(target=self._loop)

    def on_state_change(self, state, callback):
        """
        Adds a new callback method to a state change.

        :state: the monitored state for this callback.
        :callback: the method that will be called once a message containing the
        state being entered is received by the listener.
        """
        key = state.value
        if self.listeners.get(key) is None:
            self.listeners[key] = []
        self.listeners[key].append(callback)

    def on_error(self, callback):
        """
        Adds a new callback method to an error state.

        :callback: the method that will be called once an error message is
        received by the listener.
        """
        self.error_handlers.append(callback)

    def start(self):
        """
        Starts the listener. This method fails and exits the program if the
        updatehub-sdk-statechange-trigger program is not found at the expected
        path (see the SDK_TRIGGER_FILENAME constante above).
        """
        if not os.path.isfile(StateChangeListener.SDK_TRIGGER_FILENAME):
            print("WARNING: updatehub-sdk-statechange-trigger not found on",
                  StateChangeListener.SDK_TRIGGER_FILENAME)

        self.running = True
        self.thread.start()

    def stop(self):
        """
        Stops the listener. This method will disable the listener thread loop,
        close the Unix socket and wait for the thread to finish execution.
        """
        self.running = False
        socket_path = os.getenv("UH_LISTENER_TEST",
                                default=StateChangeListener.SOCKET_PATH)

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(socket_path)
        client.close()
        if threading.current_thread() != self.thread:
            self.thread.join()

    def _loop(self):
        while self.running:
            try:
                self._connect()
                self._wait_for_state()
            except Exception as exception:
                print(exception)
                self.running = False
                raise exception
            finally:
                self.sock.close()

    def _wait_for_state(self):
        while True:
            conn = None
            try:
                conn = self.sock.accept()[0]
                if not self.running:
                    break
                line = self._readline(conn)
                state = self._get_state(line)
                self._emit(state, conn)
            except StateError as exception:
                self._throw_error(exception, conn)
            finally:
                if conn is not None:
                    conn.close()

    def _connect(self):
        socket_path = os.getenv("UH_LISTENER_TEST",
                                default=StateChangeListener.SOCKET_PATH)

        if os.path.exists(socket_path):
            os.remove(socket_path)

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(socket_path)
        self.sock.listen(1)

    def _emit(self, state, connection):
        for callback in self.listeners.get(state) or []:
            command = StateCommand(connection)
            callback(state, command)

    def _throw_error(self, exception, connection):
        for callback in self.error_handlers:
            command = StateCommand(connection)
            callback(str(exception), command)
