import time
from typing import Any

import numpy as np
from device import Device
from devices.ported_device import PortedDevice
from PySide6.QtWidgets import QComboBox, QPushButton, QVBoxLayout, QWidget

from . import ble, config, intan_helper
from .find_arduino_ports import get_arduino_ports

# TODO:
# need formalize channel & start recording related interface
# need rename methods

class NordicBLE(PortedDevice):

    def __init__(self) -> None:
        super().__init__()
        self.nordic_ble = ble.NordicBle()
        self._channel_cursors = {}
        self._raw_data_queues: dict[int, list[int]] = {}

    def get_name(self) -> str:
        return 'Nordic BLE Device'

    def scan_ports(self) -> list[str]:
        return get_arduino_ports()

    def try_connect(self, port: str) -> bool:
        # Start BLE 
        try:
            self.nordic_ble.connect_peer(dongle_port=port)
        except Exception as e:
            print('error connecting to peer!')
            print(e)
            return False
        # self.nordic_ble.register_data_receive_cb(self._on_data_rx)
        self.nordic_ble.register_data_receive_cb(self._on_data_rx)

        # enable the default setup
        time.sleep(3)
        self.set_rate(1)
        self.set_rec_en_mask(0b1000111111110000)
        self.enable_recording()
        print('nordic ble connected')
        return True

    def try_disconnect(self) -> bool:
        self.disable_recording()
        self.nordic_ble.disconnect_peer()
        return True
    
    def list_channels(self) -> list[str]:
        return [
            'ch4',
            'ch5',
            'ch6',
            'ch7',
            'ch8',
            'ch9',
            'ch10',
            'ch11',
            'gyro0',
            'gyro1',
            'gyro2',
            'gyro3',
            'gyro4',
            'gyro5',
        ]

    def enable_channel(self, channel: str, state: bool = True):
        print('enable channel called, not implemented')
    
    def is_channel_enabled(self, channel: str) -> bool:
        print('is channel enabled called, not implemented')
        return False

    # device controlling functions

    def set_rate(self, rate: int):
        rate_message = [config.NordicBleMessageCode.CodeSetRate.value, rate]
        self.nordic_ble.send_data(bytearray(rate_message))
        time.sleep(2)

    def enable_recording(self):
        data = intan_helper.intan_enable_recording()
        self.nordic_ble.send_data(data)
        time.sleep(2)
    
    def disable_recording(self):
        data = intan_helper.intan_disable_recording()
        self.nordic_ble.send_data(data)
        time.sleep(2)

    def set_rec_en_mask(self, mask):
        new_mask = intan_helper.intan_set_rec_en_mask(mask)
        self.nordic_ble.send_data(new_mask)
        time.sleep(2)

    def _on_data_rx(self, service, data):
        data_dict = decode_packet(service, data)
        for key, val in data_dict.items():
            if key in self._raw_data_queues:
                data_queue = self._raw_data_queues[key]
            else:
                data_queue = []
                self._raw_data_queues[key] = data_queue
            data_queue.extend(val)
        self._check_and_push_data_event()
    
    def _check_and_push_data_event(self):
        """check the raw data queue, if there is enough data, trigger a push to the app manager"""
        for key, raw_data in self._raw_data_queues.items():
            if key == 15:
                # this is the gyro channel
                # select 10's multiple and remove from the original queue
                full_len = len(raw_data)
                nearest_ten_multiple = 10 * (full_len // 10)
                if nearest_ten_multiple == 0:
                    # no enough data yet
                    continue
                selected_data = raw_data[0: nearest_ten_multiple]
                del raw_data[0: nearest_ten_multiple]
                
                selected_data = list(map(unint16_to_int16, selected_data))
                batch_ys = np.asarray(selected_data, dtype=np.float32)
                batch_ys = batch_ys.reshape((-1, 10)).T

                for gyro_axis in range(6):
                    name = f'gyro{gyro_axis}'
                    ys = batch_ys[gyro_axis]
                    # calculate time
                    if name not in self._channel_cursors:
                        cursor = 0
                    else:
                        cursor = self._channel_cursors[name]
                    sample_period = 1 / 100
                    delta_time = ys.size * sample_period
                    self._channel_cursors[name] = cursor + delta_time
                    xs = np.linspace(cursor, cursor + delta_time - sample_period, ys.size)
                    self.event_new_data.fire(name, xs, ys)

            else:
                # this is a normal channel, always push

                # convert to voltage
                if config.INTAN_AC_DATA:
                    raw_data_float = map(intan_helper.intan_convert_ac_to_mv, raw_data)
                else:
                    raw_data_float = map(intan_helper.intan_convert_dc_to_mv, raw_data)


                name = f'ch{key}'
                if name not in self._channel_cursors:
                    cursor = 0
                else:
                    cursor = self._channel_cursors[name]
                ys = np.asarray(list(raw_data_float), dtype=np.float32)
                raw_data.clear()
                sample_period = 1 / 1000
                delta_time = ys.size * sample_period
                xs = np.linspace(cursor, cursor + delta_time - sample_period, ys.size)
                self.event_new_data.fire(name, xs, ys)
                self._channel_cursors[name] = cursor + delta_time


def decode_packet(service, data) -> dict[int, list[int]]:

    if len(data) < 5:
        print("Received packet length < 5. Can't process. Ignore packet.")
        return {}

    channel_mask = data[config.SLAVE_MSG_CHANNEL_MASK_START+1] << 8 | data[config.SLAVE_MSG_CHANNEL_MASK_START]

    # Check that we have received correct number of bytes
    min_expected_bytes = bin(channel_mask).count("1") * config.SLAVE_MSG_PC_DATA_SIZE
    min_expected_bytes += config.SLAVE_MSG_COUNTER_SIZE
    min_expected_bytes += config.SLAVE_MSG_CHANNEL_MASK_SIZE

    if (len(data) < min_expected_bytes):
        print("Incorrect number of bytes received, expected at least {0}, but received {1} bytes.".format(min_expected_bytes, len(data)))

    # now store all the actual channel data
    channels = [i for i in range(config.INTAN_MAX_CHANNELS) if (channel_mask & (1 << i))]
    pos = config.SLAVE_MSG_CHANNEL_DATA_START
    # a "set" here refers to a group of channel data where exactly 1 channel data is present for each bit set in channel mask
    set_size = len(channels) * config.SLAVE_MSG_PC_DATA_SIZE

    channel_data = [[] for i in range(config.INTAN_MAX_CHANNELS)]

    while (pos < len(data) and ((pos + set_size) <= len(data))):

        for channel in channels:

            if config.INTAN_AC_DATA:
                ac_data = data[pos+1] << 8 | data[pos] #transmission is LSB first
                channel_data[channel].append(ac_data)
            else:
                # logger.debug(dc_data)
                dc_data = (data[pos+1] & 0x3) << 8 | data[pos] # and with 0x3 because DC data is only 10 bits
                channel_data[channel].append(dc_data)

            pos += 2

    data_dict: dict[int, list[int]] = {}
    for i in range(len(channel_data)):
        if len(channel_data[i]) == 0:
            continue
        data_dict[i] = channel_data[i]
    return data_dict


def unint16_to_int16(val: int) -> int:
    if val >= (1 << 15):
        return val - (1 << 16)
    return val

if __name__ == '__main__':
    NordicBLE()