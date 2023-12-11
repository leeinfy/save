"""
This is a example device using the PortedDevice interface.

You can find the guide in `guides/device driver.md`
"""

import threading
import time

import numpy as np
from devices.ported_device import PortedDevice


class ExampleDevice(PortedDevice):
    def __init__(self) -> None:
        super().__init__()
        self._thread_running = False

    def get_name(self) -> str:
        return "My Example Device"

    def scan_ports(self) -> list[str]:
        return ['good port', 'bad port 1', 'bad port 2']

    def try_connect(self, port: str) -> bool:
        if port == 'good port':
            # start the data generator thread
            self._thread = threading.Thread(target=self._thread_main)
            self._thread_running = True
            self._thread.start()
            print('example device connected!')
            return True
        else:
            print('bad port! example device not connected')
            return False
    
    def try_disconnect(self) -> bool:
        self._thread_running = False
        self._thread.join()
        return True
    
    def list_channels(self) -> list[str]:
        return []
    
    def enable_channel(self, channel: str, state: bool = True):
        pass

    def is_channel_enabled(self, channel: str) -> bool:
        return True
    

    def _thread_main(self):
        print('data generation thread started')

        current_time = 0

        while self._thread_running:
            time.sleep(0.1)

            xs = np.linspace(current_time, current_time + 0.1, 20)
            ys = np.sin(xs * 10)

            current_time += 0.1

            self.event_new_data.fire('channel name', xs, ys)
