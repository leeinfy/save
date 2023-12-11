import numpy as np
from pyqtgraph import PlotDataItem, PlotItem, PlotWidget, mkPen

from ..abstract_plot_widget import AbstractPlotWidget
from ..abstract_scrolling_plot_widget import AbstractScrollingPlotWidget


class ScrollingPlotWidget(PlotWidget, AbstractScrollingPlotWidget):
    def __init__(self) -> None:
        super().__init__()
        self._data_queues: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {}
        self._data_items: dict[str, PlotDataItem] = {}

        self._render_count = 10
        self._view_range = 10
        self._latest_x = 0

        self._plot_item: PlotItem = self.getPlotItem()
        self._plot_item.getViewBox().setMouseEnabled(x=False)
        self._plot_item.setDownsampling(10, True, 'subsample')

    def add_channel(self, name: str, color: str):
        assert name not in self._data_queues, f'cannot add data channel with duplicate name {name}'
        self._data_queues[name] = []

        data_item = self._plot_item.plot([], [], pen=mkPen(color))
        self._data_items[name] = data_item

        
    def list_channels(self) -> list[str]:
        return list(self._data_queues.keys())
    
    def push_data(self, channel: str, xs: np.ndarray, ys: np.ndarray):
        if channel not in self._data_queues:
            print(f'channel {channel} is not registered, ignoring')
            return
        data_queue = self._data_queues[channel]

        # put in queue, remove old data
        data_queue.append((xs, ys))
        while len(data_queue) > self._render_count:
            data_queue.pop(0)

    def clear_plot(self):
        for queue in self._data_queues.values():
            queue.clear()
        for data_item in self._data_items.values():
            data_item.setData([], [])
        self.setXRange(-self._view_range, 0)
    
    def set_time_range(self, range: float):
        """set the x display range"""
        self._view_range = range

    def set_render_count(self, count: int):
        """set the number of packets being rendered"""
        self._render_count = count


    def redraw(self):
        for channel, data_queue in self._data_queues.items():
            data_item = self._data_items[channel]
            if len(data_queue) > 0:
                xs, ys = self.concat_data_queue(data_queue)
                data_item.setData(xs, ys)
                self._latest_x = float(xs[-1])
        
        # update view range
        self.setXRange(self._latest_x - self._view_range, self._latest_x)
    
    @staticmethod
    def concat_data_queue(queue: list[tuple[np.ndarray, np.ndarray]]):
        """utility function to concat data queue into a whole np array"""
        xs = []
        ys = []
        for x, y in queue:
            xs.append(x)
            ys.append(y)
        xs = np.concatenate(xs, axis=0)
        ys = np.concatenate(ys, axis=0)
        return xs, ys