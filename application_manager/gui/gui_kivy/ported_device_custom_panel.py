
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown

from devices.ported_device import PortedDevice
from typing import Optional


class PortedDeviceCustomPanel(BoxLayout):

    def __init__(self, device: PortedDevice) -> None:
        super().__init__()
        self.device = device
        self.device.event_connection_state_changed.subscribe(self.set_connected)

        self.orientation = 'vertical'
        self.size_hint_y = None

        self.combo_box = ComboBox()
        self.add_widget(self.combo_box)

        self.refresh_button = Button()
        self.refresh_button.text = 'refresh'
        self.add_widget(self.refresh_button)

        self.connect_button = Button()
        self.connect_button.text = 'Connect'
        self.add_widget(self.connect_button)

        self.refresh_button.bind(on_release = self._on_refresh_clicked)
        self.connect_button.bind(on_press = self._on_connect_button_clicked)
        
        self.set_connected(self.device.is_connected())
    
    def set_connected(self, connected: bool):
        if connected:
            self.connect_button.text = 'Disconnect'
        else:
            self.connect_button.text = 'Connect'
    
    def _on_connect_button_clicked(self, instance):
        print(instance)
        if(self.device.is_connected()):
            self.device.disconnect()
        else:
            self.device.connect(port = self.combo_box.get_active_item())
    
    def _on_refresh_clicked(self, instance):
        ports = self.device.scan_ports()
        self.combo_box.clear_item()
        for port in ports:
            self.combo_box.add_item(port)


class ComboBox(Button):
    def __init__(self):
        self.register_event_type('on_select')
        super().__init__()

        self._items = []
        self.active_item = None

        self.dropdown = DropDown()
        self.bind(on_press = self._on_click)
        self.dropdown.bind(on_select = self._on_dropdown_select)

    def add_item(self, text: str):
        self._items.append(text)
        if self.active_item is None:
            self.dropdown.select(text)

    def clear_item(self):
        self._items.clear()
        self.active_item = None
    
    def get_active_item(self) -> Optional[str]:
        return self.active_item
    
    def _on_click(self, instance):
        self.dropdown.clear_widgets()
        for item in self._items:
            btn = Button(text=item, size_hint_y=None, height=25)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
        self.dropdown.open(self)
    
    def _on_dropdown_select(self, instance, value):
        self.active_item = value
        self.text = value
        self.dispatch('on_select', value)

    def on_select(self, text):
        """kivy has to define a method with the same name for events"""
        pass