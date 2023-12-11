from .ported_device import PortedDevice


class USBTestDevice(PortedDevice):
    def __init__(self) -> None:
        super().__init__()
        pass

    def get_name(self) -> str:
        return 'USB Test Device'
    
    def scan_ports(self) -> list[str]:
        # implement your scan ports here. The returned port name will be displayed on the gui.
        return ['test', 'hello', 'world']
    
    def try_connect(self, port: str) -> bool:
        # try to connect to the port, return true if successful
        print(f'try_connect called with port = {port}')
        return True
    
    def try_disconnect(self) -> bool:
        # try to disconnect from the device, return true if successful
        print(f'try_disconnect called')
        return True
    
    def list_channels(self) -> list[str]:
        return ['channel 1']

    def enable_channel(self, channel: str, state: bool = True):
        print(f'enable_channel called with channel={channel}, state={state}')
        if channel == 'channel 1':
            # add your enable channel code here
            # state = true means enable, state = false means disable
            pass
    
    def is_channel_enabled(self, channel: str) -> bool:
        if channel == 'channel 1':
            # add your code here. return true if the channel is enabled
            pass
        return False




if __name__ == '__main__':
    device = USBTestDevice()