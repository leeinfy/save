from .abstract_plot_widget import AbstractPlotWidget


class AbstractScrollingPlotWidget(AbstractPlotWidget):
    """The base interface for all scrolling widgets"""
    
    def set_time_range(self, range: float):
        """return a list of channel names. These names will be passed into the push_data function"""
        raise NotImplementedError()
    
    def set_render_count(self, count: int):
        """set the number of packets being rendered"""
        raise NotImplementedError()
    
    def clear_plot(self):
        """clear all queued data"""
        raise NotImplementedError()