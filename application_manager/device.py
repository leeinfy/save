import abc
from typing import Any
from PySide6.QtWidgets import QWidget
from utils.events import Event
import numpy as np

class Device(abc.ABC):
    """
    The interface for a device. Any device managed by the application manager should inherit this class.

    Some devices may need fast non-blocking operations, or just need run something on the background.
    You can use threads and processes inside your device class to full fill those requirement.

    events:
    - event_new_data -- fire this when you want to push received data to the app manager
    - event_connection_state_changed -- fire this when your device connection state changed

    Things worth noticing about threads/processes:
    - Method calls can be from the gui thread, which is a different thread than your own.
    Make sure that does not break your code.
    - the event_new_data event is thread safe and can be fired from a different thread.
    - the event_connection_state_changed can be hooked to GUI functions, try not to call it from another thread. (TODO: add call_delayed support to event)
    """

    def __init__(self) -> None:
        super().__init__()
        self.event_connection_state_changed = Event(bool)  # (new_connection_state)
        self.event_new_data = Event(str, np.ndarray, np.ndarray)  # (channel, xs, ys)

    @abc.abstractmethod
    def get_name(self) -> str:
        """return the label displayed on the GUI.
        Ideally this should be different for each instance, since there can be multiple device of the same class"""
        pass

    @abc.abstractmethod
    def connect(self, params: dict[str, Any]):
        """
        Try to connect to the physical device with the given parameters.
        If the connection status changed after call, fire the event_connection_state_changed event.
        """
        pass

    @abc.abstractmethod
    def disconnect(self):
        """
        Try to disconnect the physical device.
        If the connection status changed after call, fire the event_connection_state_changed event.
        App manager will call this before exit (TODO).
        """
        pass

    @abc.abstractmethod
    def is_connected(self) -> bool:
        """
        Return the connection status of this device.
        """
        pass

    @abc.abstractmethod
    def list_channels(self) -> list[str]:
        """Return the list of channel available in this device"""
        pass

    @abc.abstractmethod
    def enable_channel(self, channel: str, state: bool = True):
        """Toggle the enable state of the channel. If state is False, disable the channel."""
        pass

    def disable_channel(self, channel: str):
        """Convenient method to disable a channel"""
        self.enable_channel(channel, False)

    @abc.abstractmethod
    def is_channel_enabled(self, channel: str) -> bool:
        """Checks if the channel is enabled"""
        pass

