from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.clock import Clock

from application_manager import ApplicationManager
from devices.sample_device import SampleDevice
from devices.ported_device import PortedDevice
from device import Device
from queue import Empty
import numpy as np

from .sample_device_custom_panel import SampleDeviceCustomPanel
from .ported_device_custom_panel import PortedDeviceCustomPanel

import math

class MainLayout(BoxLayout):
    SUB_ID = 'kivy_sub_id'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'

        left_box = BoxLayout()
        left_box.orientation = 'vertical'
        left_box.size_hint_x = 0.2
        left_box.size_hint_min_x = 200

        right_box = BoxLayout()
        right_box.orientation = 'vertical'
        right_box.size_hint_x = 0.8

        self.add_widget(left_box)
        self.add_widget(right_box)

        scroll = ScrollView(size_hint=(1, 1))
        left_box.add_widget(scroll)

        self.scroll_widget = BoxLayout()
        self.scroll_widget.orientation = 'vertical'
        self.scroll_widget.spacing = 10
        self.scroll_widget.size_hint_y = None
        scroll.add_widget(self.scroll_widget)

        self.combo_box = Button()
        self.combo_box.text = 'This is a test button'
        right_box.add_widget(self.combo_box)
        self.combo_box.size_hint_y = None
        self.combo_box.size

        self.timer_event = Clock.schedule_interval(self._on_timer, 1 / 20.0)


        self.graph_widget = Graph(xlabel='Time', ylabel='Data', x_ticks_minor=5,
                      x_ticks_major=25, y_ticks_major=1,
                      y_grid_label=True, x_grid_label=True, padding=5,
                      x_grid=True, y_grid=True, xmin=-0, xmax=100, ymin=-1, ymax=1)
        # plot = MeshLinePlot(color=[1, 0, 0, 1])
        # self.graph_widget.add_plot(plot)

        right_box.add_widget(self.graph_widget)

        self.active_device = None

        manager = ApplicationManager.get_instance()
        for device in manager.list_devices():
            self._add_device_custom_gui(device)
        manager.event_device_connected.subscribe(self._on_manager_device_connected)

    def _add_device_custom_gui(self, device: Device):
        if isinstance(device, SampleDevice):
            custom_panel = SampleDeviceCustomPanel(device)
        elif isinstance(device, PortedDevice):
            custom_panel = PortedDeviceCustomPanel(device)
        else:
            raise NotImplementedError('device gui not implemented in kivy')

        self.scroll_widget.add_widget(custom_panel)

    def _set_active_device(self, device: Device):
        manager = ApplicationManager.get_instance()
        manager.unsubscribe_all_device_data(self.SUB_ID)
        self.active_device = device
        if device is not None:
            manager.subscribe_device_data(device, 'channel 1', self.SUB_ID)


    def _on_timer(self, delta):
        manager = ApplicationManager.get_instance()
        if self.active_device is not None:
            try:
                xs, ys = manager.read_device_data(self.active_device, 'channel 1', self.SUB_ID)
            except Empty:
                return
            plot = MeshLinePlot(color=[1, 0, 0, 1])
            plot.points = np.stack((xs, ys), 1)
            self.graph_widget.add_plot(plot)
            if xs[-1] > self.graph_widget.xmax:
                new_xmax = float(xs[-1]) + 10
                delta = new_xmax - self.graph_widget.xmax
                self.graph_widget.xmax = new_xmax
                self.graph_widget.xmin += delta

    def _on_manager_device_connected(self, device: Device):
        self._set_active_device(device)
        print('device connected:', device)


class MainApp(App):
    def build(self):
        return MainLayout()
