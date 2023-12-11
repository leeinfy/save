import glob
import sys
from ast import Num
from platform import platform

import serial.tools.list_ports as stl


def get_arduino_ports():
    port_list = []
    if sys.platform == 'win32':
        comm_port_lst = []
        port_list = stl.comports()
        num_connections = len(port_list)
        for i in range(0,num_connections):
            port_str = str(port_list[i])

            split_port = port_str.split(' ')
            comm_port_lst.append(split_port[0])
        return comm_port_lst
        
    elif sys.platform == 'darwin':
        ar_ports_lst = []
        port_list = glob.glob('/dev/tty.*')
        for p in port_list:
            ar_ports_lst.append(p)
        return ar_ports_lst

    elif sys.platform == 'linux':
        ar_ports_lst = []
        port_list_1 = glob.glob('/dev/ttyUSB*')
        port_list_2 = glob.glob('/dev/ttyACM*')
        ar_ports_lst.extend(port_list_1)
        ar_ports_lst.extend(port_list_2)
        return ar_ports_lst
