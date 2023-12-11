# Device Driver Guide

## What is a device driver
In short, device driver is some code that communicate with the device, then convert the communication to a standard format(numpy array) that the application manager can understand. It may also have abilities to discover, connect to and config the device.

## How to write a device driver?
Currently, there are two ways of doing it:
1. extending the `PortedDevice` class
2. extending the `Device` class

#1 is the preferred way if you do not need the extra customizability #2 is giving you. If your device can be connected using a "port" name info, either physical or virtual, use #1 (should cover 99% of devices).

### Extending PortedDevice class
The proted device has the following lifecycle:
1. Scan ports
2. Connect to the physical device on the choosen port
3. Receive data, convert format, then push to app manager
4. Disconnect
5. Return to step 1

The **scan port**, **connect** and **disconnect** are usually triggered by user, and you implement them in the provided call back functions. **Receive data** should happen at the background repeatly when the device is connected, usually you need to start a thread or a new process for this.

Now let's do it step by step!

---

First of all, go to the `devices` folder and create a new .py file. All device drivers are placed in this folder. If you plan to use more than one python file, create a subfolder in `devices`. For the sake of this guide, we will create a `example.py` and a class named `ExampleDevice` which generates fake data when connected. Import required classes and extend the PortedDevice class:

```python
import threading
import time

import numpy as np
from devices.ported_device import PortedDevice


class SampleDevice(PortedDevice):
    pass
```

Now if you try to instantiate your `ExampleDevice` class, there will be some error saying abstract methods not implemented. Below is a list of abstract methods you must override before the class can function normally:
1. get_name
2. scan_ports
3. try_connect
4. try_disconnect
5. list_channels
6. enable_channel
7. is_channel_enabled

We will look at them one by one.

**1. get_name(self) -> str:**

This literally return the string name of the device. The returned name is displayed in GUI so user can identify control panels for different devices.

Ideally, every instance of this device driver should return a different name, so there will be no confusion when mutiple devices of the same type is connected. Buf for now, we can just return a constant value.

```python
def get_name(self) -> str:
    return "My Example Device"
```

**2. scan_ports(self) -> list[str]:**

This should scan and return a list of port names the user can connect to. The list will be displayed on GUI, and when user click connect, the selected string will be passed to `try_connect`.

For example, if you want to use USB ports, you should scan available ports on the system and return a list like `['COM1', 'COM3', 'COM4']`.

In this example, we just return a hard coded list.

```python
def scan_ports(self) -> list[str]:
    return ['good port', 'bad port 1', 'bad port 2']
```

**3. try_connect(self, port: str) -> bool:**

This will be called whe user clicks connect. The selected port string will be passed in using the `port` param. You should try to connect to your physical device, and return `True` if succeed, return `False` if connection failed.

Here we will connect only if the port is a good port, and print the result.

```python
def try_connect(self, port: str) -> bool:
    if port == 'good port':
        # TODO: start the data generator thread
        print('example device connected!')
        return True
    else:
        print('bad port! example device not connected')
        return False
```

**4. try_disconnect(self) -> bool:**

This is the same idea as the `try_connect`. You should now try to disconnect your device, return True if succeed, False if failed.

Here we assume disconnection is always successful.

```python
def try_disconnect(self) -> bool:
    return True
```

**Almost done so far!**

We have already implemented the most important ones. The 5, 6, 7 are related to channels and may not be necessary in many cases, so we will cover them later. Let's test our device first!

Let's put some dummy functions there so the abstract method check can pass.
```python
def list_channels(self) -> list[str]:
    return []

def enable_channel(self, channel: str, state: bool = True):
    pass

def is_channel_enabled(self, channel: str) -> bool:
    return True
```

Now create a new `test.py` (or any name you like) as they main entry. This file must be in the root dir (the `application_manager` folder) or the imports may not work. Paste the following code into it:

```python
import sys

from application_manager import ApplicationManager
from devices.example_device import ExampleDevice

# these are gui imports
from PySide6.QtWidgets import QApplication
from gui.gui_pyside.main_window import MainWindow


# creat an app manager instance
app_manager = ApplicationManager()

# add your new device
device = ExampleDevice()
app_manager.add_device(device)

# start the gui
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
```

I assume you are using a desktop for developing, so above code uses the PySide6 GUI. If any package is missing, install it.

The main window should pop up when you run the code, you can click "refresh", then connect & disconnect the example device and see if everything works. (We havn't add any data generation code, so nothing will show on the plot, that's normal)

**Adding data generation**

Let's add the data generation code now.

The idea is when your device is connected, you start a new thread. The thread will generate some sine wave every 0.1 second and push it to the app manager. When the device is disconnected, you stop the thread.

In real application, the thread will do some thing more complicated, such as reading byte codes from sockets and decode it.

Add a new method in the `ExampleDevice` class to serve as the main function of the new thread. We also need a variable to control the thread, so we set it in the `__init__` method:

```python
def __init__(self) -> None:
    super().__init__()
    self._thread_running = False

def _thread_main(self):
    print('data generation thread started')
    current_time = 0
    while self._thread_running:
        time.sleep(0.1)
        xs = np.linspace(current_time, current_time + 0.1, 20)
        ys = np.sin(xs * 10)
        current_time += 0.1
        self.event_new_data.fire('channel name', xs, ys)
```

The line `self.event_new_data.fire('channel name', xs, ys)` is where you push the data to the application manager. You can call multiple times for multiple channel, and this method is thread safe.

Now we should start the thread when connected and end it when disconnected. Modify the `try_connect` and `try_disconnect` as following:

```python
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
```

Now run the `test.py` again. You should see the device working. 

(When this guide is written, the GUI cannot subscribe channels automatically yet, so still nothing will show on the plot. You can add some print statements in the thread to see if it is running.)

**What about the channel related stuff?**

(TODO)

### Extending Device class
(TODO)