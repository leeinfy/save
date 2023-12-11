from typing import Optional
from queue import SimpleQueue

from device import Device
from db_adaptor import DBAdaptor
from utils.events import Event
import numpy as np

class ApplicationManager:
    """
    A class that provide standard interface to devices and data buffering.

    Note on multi threading:
    - methods that modify the buffer pool (subscribe/unsubscribe device data) are not thread safe yet!
    Call them from the same thread only! (TODO: make this thread safe)
    """

    instance: Optional['ApplicationManager'] = None

    def __init__(self) -> None:
        # singleton
        assert ApplicationManager.instance is None, 'Only one application manager is allowed'
        ApplicationManager.instance = self

        # variables
        self._devices: list[Device] = []
        self._database_adaptors: list[DBAdaptor] = []
        # map (device, channel) to all its subscribers, then to the subscriber's own queue.
        # this way there can be multiple subscribers for one device
        self._device_data_pool: dict[tuple[Device, str], dict[str, SimpleQueue[tuple[np.ndarray, np.ndarray]]]] = {}

        # callbacks
        self.event_devices_changed = Event()  # indicate device list has changed
        self.event_device_added = Event(Device)  # a new device is added
        self.event_device_deleted = Event(Device)  # a device is deleted

        self.event_device_connected = Event(Device)  # device connected
        self.event_device_disconnected = Event(Device)  # device disconnected

    @classmethod
    def get_instance(cls) -> 'ApplicationManager':
        """Return the global instance of application manager.
        Will raise an assertion error if there is no global instance created yet."""
        assert cls.instance is not None, 'Device manager is not created yet.'
        return cls.instance

    def list_devices(self) -> list[Device]:
        """return a list of all device managed by the manager"""
        return self._devices.copy()
    
    def list_connected_devices(self) -> list[Device]:
        """return a list of device that is connected"""
        return list(filter(lambda dev: dev.is_connected(), self._devices))
    
    def add_device(self, new_device: Device):
        """add a device to the manager"""
        if new_device not in self._devices:
            new_device.event_connection_state_changed.subscribe(lambda new_status: self._on_device_connection_changed(new_device, new_status))
            
            self._devices.append(new_device)
            self.event_device_added.fire(new_device)
            self.event_devices_changed.fire()

            new_device.event_new_data.subscribe(lambda channel, xs, ys: self._on_new_data(new_device, channel, xs, ys))

    def remove_device(self, device: Device):
        """remove a device from the manager"""
        if(device in self._devices):
            self._devices.remove(device)
            self.event_device_deleted.fire(device)


    def subscribe_device_data(self, device: Device, channel: str, sub_id: str):
        """
        Tell the manager data from this device is interested, any data from this device will be added to a queue.
        `sub_id` is a unique string for each data subscriber, this way different subscriber will not mess up each other's queue
        
        This method also calls device.enableChannel() if no other subscribers exist. You don't need to call it again.
        """
        assert device is not None
        assert channel is not None
        pair = (device, channel)
        if pair not in self._device_data_pool:
            self._device_data_pool[pair] = {sub_id: SimpleQueue()}
            device.enable_channel(channel)
        else:
            self._device_data_pool[pair][sub_id] = SimpleQueue()
    
    def unsubscribe_device_data(self, device: Device, channel: str, sub_id: str):
        """
        Tell the manager this device is no longer interested by the subscriber.
        
        This method also calls device.disableChannel() if subscribers are empty. You don't need to call it again.
        """
        assert device is not None
        assert channel is not None
        pair = (device, channel)
        self._device_data_pool[pair].pop(sub_id)
        if len(self._device_data_pool[pair]) == 0:
            device.disable_channel(channel)
            self._device_data_pool.pop(pair)
    
    def unsubscribe_all_device_data(self, sub_id: str):
        """unsubscribe all device under this sub id"""
        keys_to_remove = set()
        for key, val in self._device_data_pool.items():
            try:
                val.pop(sub_id)
                if len(val) == 0:
                    key[0].disable_channel(key[1])
                    keys_to_remove.add(key)
            except KeyError:
                pass

        for key in keys_to_remove:
            self._device_data_pool.pop(key)

    def read_device_data(self, device: Device, channel: str, sub_id: str) -> tuple[np.ndarray, np.ndarray]:
        """
        Read one data packet from the queue.
        Will return an item only if one is immediately available. Otherwise raise a `queue.Empty` exception.
        """
        pair = (device, channel)
        return self._device_data_pool[pair][sub_id].get_nowait()
    
    def get_device_data_queue(self, device: Device, channel: str, sub_id: str) -> SimpleQueue[tuple[np.ndarray, np.ndarray]]:
        """Get the data queue for this device directly."""
        pair = (device, channel)
        return self._device_data_pool[pair][sub_id]

    # private methods

    def _on_device_connection_changed(self, device: Device, connection: bool):
        if connection:
            self.event_device_connected.fire(device)
        else:
            self.event_device_disconnected.fire(device)

    def _on_new_data(self, device: Device, channel: str, xs: np.ndarray, ys: np.ndarray):
        pair = (device, channel)
        if pair in self._device_data_pool.keys():
            # device data is interested, push data into all subscriber queues
            for queue in self._device_data_pool[pair].values():
                queue.put((xs, ys))