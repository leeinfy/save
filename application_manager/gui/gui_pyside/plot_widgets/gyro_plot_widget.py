from typing import Optional

import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..abstract_plot_widget import AbstractPlotWidget
from ..abstract_scrolling_plot_widget import AbstractScrollingPlotWidget
from .scrolling_plot_widget import ScrollingPlotWidget


class GyroPlotWidget(QWidget, AbstractScrollingPlotWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self._location_plot_widget = ScrollingPlotWidget()
        layout.addWidget(self._location_plot_widget)
        self._rotation_plot_widget = ScrollingPlotWidget()
        layout.addWidget(self._rotation_plot_widget)

        self._location_plot_widget.add_channel('x', 'red')
        self._location_plot_widget.add_channel('y', 'green')
        self._location_plot_widget.add_channel('z', 'blue')

        self._rotation_plot_widget.add_channel('r1', 'cyan')
        self._rotation_plot_widget.add_channel('r2', 'yellow')
        self._rotation_plot_widget.add_channel('r3', 'magenta')
        
    def list_channels(self) -> list[str]:
        return ['x', 'y', 'z', 'r1', 'r2', 'r3']
    
    def push_data(self, channel: str, xs: np.ndarray, ys: np.ndarray):
        if channel in ('x', 'y', 'z'):
            self._location_plot_widget.push_data(channel, xs, ys)
        else:
            self._rotation_plot_widget.push_data(channel, xs, ys)
    
    def clear_plot(self):
        self._location_plot_widget.clear_plot()
        self._rotation_plot_widget.clear_plot()
    
    def set_time_range(self, range: float):
        """set the x display range"""
        self._location_plot_widget.set_time_range(range)
        self._rotation_plot_widget.set_time_range(range)

    def set_render_count(self, count: int):
        """set the number of packets being rendered"""
        self._location_plot_widget.set_render_count(count)
        self._rotation_plot_widget.set_render_count(count)

    def redraw(self):
        self._location_plot_widget.redraw()
        self._rotation_plot_widget.redraw()
