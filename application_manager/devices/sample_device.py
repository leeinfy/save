import threading
import time
from typing import Any, Optional

import numpy as np
from device import Device


class SampleDevice(Device):

    channel_names = [
        'gyro_x',
        'gyro_y',
        'gyro_z',
        'gyro_r1',
        'gyro_r2',
        'gyro_r3',
        'ch0',
        'ch1',
        'ch2',
        'ch3',
        'ch4',
        'ch5',
        'ch6',
        'ch7',
        'ch8',
    ]

    def __init__(self) -> None:
        super().__init__()
        self._connected = False
        self._channel_states = {}

        self._data_gen_thread: Optional[threading.Thread] = None
    
    def get_name(self) -> str:
        return 'Sample Device ' + str(hash(self))
    
    def connect(self, **params):
        print(f'Sample device {self} connected with params {params}')
        self._connected = True
        self.event_connection_state_changed.fire(self._connected)

        self._data_gen_thread = threading.Thread(target=self._data_generator_thread_main)
        self._data_gen_thread.start()

    def disconnect(self):
        print(f'Sample device {self} disconnected')
        self._connected = False
        self.event_connection_state_changed.fire(self._connected)

        if self._data_gen_thread is not None:
            self._data_gen_thread.join()
            self._data_gen_thread = None

    def is_connected(self) -> bool:
        return self._connected
    
    def list_channels(self) -> list[str]:
        return self.channel_names
    
    def enable_channel(self, channel: str, state: bool = True):
        if channel not in self.channel_names:
            return
        self._channel_states[channel] = state
    
    def is_channel_enabled(self, channel: str) -> bool:
        return self._channel_states[channel] if channel in self._channel_states else False

    def _data_generator_thread_main(self):
        time_cursor = 0.0
        time_step = 0.1
        while self._connected:
            time.sleep(time_step)
            xs = np.linspace(time_cursor, time_cursor + time_step, 50)

            # try generate data for each channel
            if self.is_channel_enabled('gyro_x'):
                self.event_new_data.fire('gyro_x', xs, np.sin(xs))

            if self.is_channel_enabled('gyro_y'):
                self.event_new_data.fire('gyro_y', xs, np.sin(xs * 2))
            
            if self.is_channel_enabled('gyro_z'):
                self.event_new_data.fire('gyro_z', xs, np.sin(xs * 3))
            
            if self.is_channel_enabled('gyro_r1'):
                self.event_new_data.fire('gyro_r1', xs, np.mod(xs, 5))
            
            if self.is_channel_enabled('gyro_r2'):
                self.event_new_data.fire('gyro_r2', xs, np.mod(xs, 4))
            
            if self.is_channel_enabled('gyro_r3'):
                self.event_new_data.fire('gyro_r3', xs, np.mod(xs, 3))
            
            for i in range(8):
                name = f'ch{i}'
                if self.is_channel_enabled(name):
                    self.event_new_data.fire(name, xs, np.sin(xs*2*i) * np.sin(xs / 2))
            
            time_cursor += time_step
