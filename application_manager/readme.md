# Application Manager Documents

Application manager is the new PC & Mobile side app architecture.

## What is this

Application manager is a "middle layer" that decouples the device driver (code that connect & decode), the GUI (code that display data), and the data logger (code that store received data to files). It provides a standardized interface for each of the above part and allows (almost) arbitrary combination of different implementations.

Application manager is written in python3 and the only dependency is numpy. It can run on mobile platforms with the help of Kivy.

## Guides

- [How to write a new device driver](<guides/device driver.md>)
- How to write a new DB adaptor? (TODO)
- How to write a new GUI? (TODO)

## Project Structure

The `ApplicationManager` class is in the `application_manager.py`. It does 4 things:
1. Keep a list of registered devices
2. Keep a data subscriber list, enable/disable channels on devices when needed 
3. Listen to the push_data event from devices, cache the data for each subscriber
4. Listen to the connect/disconnect event from devices, send notifications to gui through another event

The **device interface** is in `device.py`. All device driver should extend this class. There is also a second level class `PortedDevice` in `devices/ported_device.py`, which implemented some boilerplate code for devices that only require a 'port' parameter (any string) for connection.

The **database adaptor** (db adaptor) interface is in `db_adaptor.py`. All db adaptors should extend this class

**Implementations of the device interface** are in the `devices` folder. Create a sub-folder if you need more than one py file

**Implementations of the db adaptor interface** are in the `db_adaptor` folder. Create a sub-folder if you need more than one py file

The `gui` folder contains all GUI implementations. Each sub-folder contains a implementation using one specific gui framework. Each are independent and has its own main window.

The **main entry** is the `main.py`. This file instantiate the application manager, then import & execute the selected GUI system.
