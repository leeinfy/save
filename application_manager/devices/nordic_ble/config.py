from enum import Enum

# Store all constants and configuration parameters here.


# Constants for BLE dongle and peer name
DEFAULT_COM_PORT = "COM8"  # TODO: this number may change, write a loop to try them all
DEFAULT_BLE_SERVICE = "Nordic_BCI_Service"

# Behavior of Plotting
DEFAULT_CHANNEL_MAX_DP_LENGTH = 10000 # this isn't good, we need to somehow keep flushing data to file 

# Communication Protol between Host and Nordic DK
class NordicBleMessageCode(Enum):
    CodeSetRate = 1
    CodeSetStimEnMask = 2
    CodeSetStimMag = 3
    CodeSetRecMask = 4
    CodeSetStimPolMask = 5
    CodeSetStimConfig = 6
    CodeEnableRecording = 7
    CodeDisableRecording = 8
    CodeTriggerStim = 9

SLAVE_MSG_COUNTER_START = 0
SLAVE_MSG_COUNTER_SIZE = 1
SLAVE_MSG_CHANNEL_MASK_START = 1
SLAVE_MSG_CHANNEL_MASK_SIZE = 2
SLAVE_MSG_CHANNEL_DATA_START = 3
SLAVE_MSG_PC_DATA_SIZE = 2 # per channel data size = 2 bytes per channel

# Intan Related Constants
INTAN_AC_DATA_MULTIPLIER_MV = 0.195 / 1000
INTAN_AC_DATA_SUBTRACTOR = 32768
INTAN_MAX_CHANNELS = 16
INTAN_AC_DATA = True  # by default always receiving AC data. Set to false if testing DC data.
INTAN_SAMPLE_DATA_FROM_RHS = False  #TODO: Make this configurable from GUI