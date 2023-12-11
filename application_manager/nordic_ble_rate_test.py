import sys
from typing import Optional
from queue import Empty
import time

import numpy as np


from application_manager import ApplicationManager
from device import Device
from devices.sample_device import SampleDevice
from devices.nordic_ble.nordic_ble import NordicBLE

from devices.nordic_ble.find_arduino_ports import get_arduino_ports

# setup app manager
app_manager = ApplicationManager()

nordic_device = NordicBLE()
app_manager.add_device(nordic_device)

ports = get_arduino_ports()
print(f'{len(ports)} ports detected.')
if len(ports) == 0:
    exit()
for i, port in enumerate(ports):
    print(f'[{i}] - {port}')

selection = int(input('Select port to connect to: '))
nordic_device.connect({'port': ports[selection]})
time.sleep(3)

nordic_device.set_rate(20)
time.sleep(1)
nordic_device.set_rec_en_mask(0b1)
time.sleep(1)
nordic_device.enable_recording()
time.sleep(1)

time.sleep(15)

nordic_device.disconnect()
