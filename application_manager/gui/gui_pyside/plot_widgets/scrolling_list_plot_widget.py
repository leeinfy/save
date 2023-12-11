from typing import Optional

import numpy as np
import PySide6.QtCore
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..abstract_plot_widget import AbstractPlotWidget
from ..abstract_scrolling_plot_widget import AbstractScrollingPlotWidget
from .scrolling_single_plot_widget import ScrollingSinglePlotWidget


class ScrollingListPlotWidget(QWidget, AbstractScrollingPlotWidget):
    def __init__(self):
        super().__init__()

        self._main_layout = QVBoxLayout()
        self.setLayout(self._main_layout)

        self._channel_widget_dict: dict[str, ScrollingSinglePlotWidget] = {}

    def add_channel(self, name: str, color: str = 'red'):
        assert name not in self._channel_widget_dict, f'cannot add channel with duplicate name {name}'
        plot_widget = ScrollingSinglePlotWidget(color)
        self._main_layout.addWidget(plot_widget)
        self._channel_widget_dict[name] = plot_widget

    def list_channels(self) -> list[str]:
        """return a list of channel names. These names will be passed into the push_data function"""
        return list(self._channel_widget_dict.keys())
    
    def push_data(self, channel: str, xs: np.ndarray, ys: np.ndarray):
        """push a segment of new data to the given channel. Call `redraw` after this to show the new data"""
        if channel not in self._channel_widget_dict:
            print(f'channel {channel} is not registered, ignoring')
            return
        self._channel_widget_dict[channel].push_single_data(xs, ys)
    
    def redraw(self):
        """redraw the graph to show the new data"""
        for widget in self._channel_widget_dict.values():
            widget.redraw()

    def set_render_count(self, count: int):
        for widget in self._channel_widget_dict.values():
            widget.set_render_count(count)
    
    def set_time_range(self, range: float):
        for widget in self._channel_widget_dict.values():
            widget.set_time_range(range)
    
    def clear_plot(self):
        for widget in self._channel_widget_dict.values():
            widget.clear_plot()