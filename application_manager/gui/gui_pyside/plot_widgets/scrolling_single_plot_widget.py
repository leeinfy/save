import numpy as np

from .scrolling_plot_widget import ScrollingPlotWidget


class ScrollingSinglePlotWidget(ScrollingPlotWidget):
    def __init__(self, color: str = 'red') -> None:
        super().__init__()
        super().add_channel('c', color)
    
    def push_data(self, channel: str, xs: np.ndarray, ys: np.ndarray):
        return super().push_data('c', xs, ys)

    def push_single_data(self, xs: np.ndarray, ys: np.ndarray):
        return super().push_data('c', xs, ys)
    
    def add_channel(self, name: str, color: str):
        """Cannot add channel to a single channel plot. This will do nothing"""
        pass