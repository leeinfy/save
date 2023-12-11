
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput

from devices.sample_device import SampleDevice


class SampleDeviceCustomPanel(BoxLayout):

    def __init__(self, device: SampleDevice) -> None:
        super().__init__()
        self.device = device
        self.device.event_connection_state_changed.subscribe(self.set_connected)

        self.orientation = 'vertical'
        self.size_hint_y = None

        self.text_edit = TextInput()
        self.add_widget(self.text_edit)
        self.button = Button()
        self.button.text = 'Connect'
        self.add_widget(self.button)

        channel_button = Button()
        channel_button.text = 'toggle channel (should not need to click)'
        channel_button.bind(on_press = lambda instance: self.device.enable_channel('sample channel', not self.device.is_channel_enabled('sample channel')))
        self.add_widget(channel_button)

        self.button.bind(on_press = self._on_custom_gui_button_clicked)
        
        self.set_connected(self.device.is_connected())
    
    def set_connected(self, connected: bool):
        if connected:
            self.button.text = 'Disconnect'
        else:
            self.button.text = 'Connect'
    
    def _on_custom_gui_button_clicked(self, instance):
        print(instance)
        if(self.device.is_connected()):
            self.device.disconnect()
        else:
            self.device.connect(text_edit = self.text_edit.text)
