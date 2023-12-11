import numpy as np


# cannot use Abc because meta class would conflict with Qt
class AbstractPlotWidget:
    """The base interface for all plotting widgets"""
    def list_channels(self) -> list[str]:
        """return a list of channel names. These names will be passed into the push_data function"""
        raise NotImplementedError()
    
    def push_data(self, channel: str, xs: np.ndarray, ys: np.ndarray):
        """push a segment of new data to the given channel. Call `redraw` after this to show the new data"""
        raise NotImplementedError()
    
    def redraw(self):
        """redraw the graph to show the new data"""
        raise NotImplementedError()