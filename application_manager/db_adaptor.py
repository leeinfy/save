import abc
from device import Device
class DBAdaptor(abc.ABC):
    
    def add_channel(self, device: Device, channel: str):
        """Include a channel in the recording"""

    def remove_channel(self, device: Device, channel: str):
        """Remove a channel from the recording"""

    def clear_channels(self):
        """Remove all channels"""

    def get_channels(self) -> set[tuple[Device, str]]:
        """list included channels"""
        return set()

    def start_recording(self):
        """Start recording"""

    def stop_recording(self):
        """Stop recording"""
    
    def is_recording(self) -> bool:
        """Check if recording is on"""
        return False
