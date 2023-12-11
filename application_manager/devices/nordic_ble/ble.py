import logging
from enum import Enum

from blatann import BleDevice, gap
from blatann.services import nordic_uart

from . import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

peer = None
target_addr = None

class BleStatus(Enum):
    BleSuccess = 0
    BleErrorNoPeer = 1
    BleErrorSendFailed = 2

class NordicBle(object):
    def __init__(self) -> None:
        self.ble_dongle = None
        self.scan_reports = None
        self.target_peer_addr = None
        self.peer = None  # this is referencing the nordic dev kit in our case
        self.peer_service = None  # this is the service on nordic dev kit that we will be talking to.
        self.on_rx_callback = None  # TODO: store the rx callback here for higher level callers
        self.rx_counter = -1  # our special BLE stack has a receive message counter to warn against package lost
        self.lost_packets = 0


    def connect_peer(self, dongle_port=config.DEFAULT_COM_PORT, peer_name=config.DEFAULT_BLE_SERVICE):
        self.ble_dongle = BleDevice(dongle_port)
        self.ble_dongle.configure()
        self.ble_dongle.open(clear_bonding_data=True) 

        # scan for peers (aka ble devices that are advertising in the area)
        logger.info("Scanning...")
        # Set scanning for 4 seconds
        self.ble_dongle.scanner.set_default_scan_params(timeout_seconds=4)

        self.scan_report_collection = self.ble_dongle.scanner.start_scan().scan_reports

        for report in self.scan_report_collection:
            if not report.duplicate:
                logging.info(report.advertise_data.local_name)
                logging.info(report.peer_address)

                if str(report.advertise_data.local_name) == peer_name:
                    logging.info(report.peer_address)
                    self.target_peer_addr = report.peer_address
                    break
        
        # attempt to connect to the ble peer now that we have its address
        self.ble_dongle.set_default_peripheral_connection_params(7.5, 30, 4000, 0)
        self.peer = self.ble_dongle.connect(self.target_peer_addr).wait()
        if not self.peer:
            return BleStatus.BleErrorNoPeer
        logger.debug("Connected, conn_handle: {}".format(self.peer.conn_handle))
        self.peer.exchange_mtu(247).wait(timeout=10)
        logger.debug("Exchange MTU completed.")

        self.peer.update_phy(2).wait(timeout=10)

        # a connect peer offers a bunch of services, discover them and save them
        _, event_args = self.peer.discover_services().wait(exception_on_timeout=False)
        logger.debug("Service discovery complete! status: {}".format(event_args.status))

        # debug print out database
        logger.debug(self.peer.database)

        # initialize the service we are after, which is the UART service. TODO: this needs to be renamed.
        self.peer_service = nordic_uart.find_nordic_uart_service(self.peer.database)
        if not self.peer_service:
            logger.error("Failed to find Nordic UART service in peripheral database")
            self.peer.disconnect().wait()
            self.ble_dongle.close()

        # initialize the service
        self.peer_service.initialize().wait(5)

        # register local callback
        self.peer_service.on_data_received.register(self._data_rx_cb)

        return BleStatus.BleSuccess
    

    def disconnect_peer(self):
        if self.peer is not None:
            self.peer.disconnect().wait()

        if self.ble_dongle is not None:
            self.ble_dongle.close()


    def register_data_receive_cb(self, recv_callback):
        self.on_rx_callback = recv_callback


    def _data_rx_cb(self, service, data):

        # look at header (1st) byte of data here and check that counter is correct
        if self.rx_counter != -1 and self.rx_counter+1 != data[0]:
            self.lost_packets += 1
            logger.error("Counter value incorrect, expected: {0} , received: {1}".format(self.rx_counter+1, data[0]))
        
        # Update counter
        self.rx_counter = data[0]
        if self.rx_counter == 255:
            # since counter is only a single byte, then after 255, the next one is 0
            self.rx_counter = -1

        if self.on_rx_callback:
            self.on_rx_callback(service, data)


    def send_data(self, data):
        if self.peer_service is not None:
            self.peer_service.write(data).wait(10)
            return BleStatus.BleSuccess
        else:
            logger.error("Unable to send. No peer detected. Call connect_peer() first.")
        
        return BleStatus.BleErrorSendFailed


    def _find_target_addr(self, reports, peer_name):

        for report in reports:
            if not report.duplicate:
            # logging.info(report.advertise_data.local_name)
            # logging.info(report.peer_address)

                if str(report.advertise_data.local_name) == peer_name:
                    logging.info(report.peer_address)
                    return report.peer_address

        return None
    

    def __del__(self) -> None:

        if self.peer is not None:
            self.peer.disconnect().wait()

        if self.ble_dongle is not None:
            self.ble_dongle.close()

        self.ble_dongle = None
        self.scan_reports = None
        self.target_peer_addr = None
        self.peer_service = None


if __name__ == '__main__':
    
    # Temporary testing program, move to main application later
    def on_data_rx(service, data):
        """
        Called whenever data is received on the RX line of the Nordic UART Service
        :param service: the service the data was received from
        :type service: nordic_uart.service.NordicUartClient
        :param data: The data that was received
        :type data: bytes
        """
        logger.info("Received data (len {}): '{}'".format(len(data), data))

    nordic_ble = NordicBle()
    nordic_ble.connect_peer()
    nordic_ble.register_data_receive_cb(on_data_rx)

    while True:
        continue
