import abc
from typing import Any

from device import Device


class PortedDevice(Device):
    """A common class to reduce some boilerplate code"""

    def __init__(self) -> None:
        super().__init__()
        self._connected = False

    @abc.abstractmethod
    def scan_ports(self) -> list[str]:
        """scan available ports to connect, return them as a list"""
        pass
    
    def connect(self, **params: Any):
        success = self.try_connect(params['port'])
        print(success)
        if self._connected != success:
            self._connected = success
            self.event_connection_state_changed.fire(success)

    @abc.abstractmethod
    def try_connect(self, port: str) -> bool:
        """try to connect the device on the port. Return true if succeed, false if failed"""
        pass

    def disconnect(self):
        success = self.try_disconnect()
        if self._connected != (not success):
            self._connected = not success
            self.event_connection_state_changed.fire(not success)

    @abc.abstractmethod
    def try_disconnect(self) -> bool:
        """try to disconnect the device on the port. Return true if succeed, false if failed"""
        pass

    def is_connected(self) -> bool:
        return self._connected
