from hashlib import new
from . import config

"""
Use this file to store any Intan parsing/convertion algorithms.
And any Intan specific configuration commands
"""

# Get byte n of an integer
def get_byte_n(val, n):
    # This function assumes 0th byte is least significant byte.
    return ((val >> (n*8)) & 0xff)


# Get bit n of an integer
def get_bit_n(val, n):
    # This function assumes 0th bit is least significant byte.
    return ((val >> (n)) & 0x1)


#Convert raw Intan AC channel data to millivolt
def intan_convert_ac_to_mv(raw_val: int) -> float:
    mv_val = 0
    if config.INTAN_SAMPLE_DATA_FROM_RHS:
        mv_val = (raw_val - config.INTAN_AC_DATA_SUBTRACTOR) * config.INTAN_AC_DATA_MULTIPLIER_MV
    else:
        mv_val = (raw_val - 0x8000) * config.INTAN_AC_DATA_MULTIPLIER_MV
    return mv_val


#Convert raw Intan DC channel data to mv
def intan_convert_dc_to_mv(raw_val: int) -> float:

    mv_val = ((raw_val &0x3ff) - 512) * (-19.23)

    return mv_val


#Construct a bytearray containing information to set Pos Stim Magnitude for Channel
def intan_set_stim_mag(channel: int, mag: int) -> bytearray:
    # each parameter is expected to be 16 bits, so must be broken down into byte chunks for transmission
    
    new_data = [config.NordicBleMessageCode.CodeSetStimMag.value]
    new_data.append(get_byte_n(channel, 0)) # least sig. byte has to go first
    new_data.append(get_byte_n(channel, 1))
    new_data.append(get_byte_n(mag, 0))
    new_data.append(get_byte_n(mag, 1))

    return bytearray(new_data)


def intan_set_send_stim_mask(mask: int) -> bytearray:
    # each parameter is expected to be 16 bits, so must be broken down into byte chunks for transmission
    
    new_data = [config.NordicBleMessageCode.CodeTriggerStim.value]
    new_data.append(get_byte_n(mask, 0)) # least sig. byte has to go first
    new_data.append(get_byte_n(mask, 1))

    return bytearray(new_data)


#Construct a bytearray containing information to set stimulation enable mask
def intan_set_stim_en_mask(mask: int) -> bytearray:
    # each parameter is expected to be 16 bits, so must be broken down into byte chunks for transmission
    
    new_data = [config.NordicBleMessageCode.CodeSetStimEnMask.value]
    new_data.append(get_byte_n(mask, 0)) # least sig. byte has to go first
    new_data.append(get_byte_n(mask, 1))

    return bytearray(new_data)


#Construct a bytearray containing information to set recording enable mask
def intan_set_stim_pol_mask(mask: int) -> bytearray:
    # each parameter is expected to be 16 bits, so must be broken down into byte chunks for transmission
    
    new_data = [config.NordicBleMessageCode.CodeSetStimPolMask.value]
    new_data.append(get_byte_n(mask, 0)) # least sig. byte has to go first
    new_data.append(get_byte_n(mask, 1))

    return bytearray(new_data)


#Construct a bytearray containing information to set recording enable mask
def intan_set_rec_en_mask(mask: int) -> bytearray:
    # each parameter is expected to be 16 bits, so must be broken down into byte chunks for transmission
    
    new_data = [config.NordicBleMessageCode.CodeSetRecMask.value]
    new_data.append(get_byte_n(mask, 0)) # least sig. byte has to go first
    new_data.append(get_byte_n(mask, 1))

    return bytearray(new_data)


#Construct a bytearray containing information to set stim configuration for a channel
def intan_set_stim_config(channel_num: int, pos_mag: int, neg_mag: int, pos_pulse_width: int, neg_pulse_width: int, period: int, num_cycles: int) -> bytearray:

    new_data = [config.NordicBleMessageCode.CodeSetStimConfig.value]

    # the ordering of bytes must be the same on the firmware side, specifically incoming_message_stim_config_t
    # This copies incoming_message_stim_config_t in C code
    new_data.append(get_byte_n(channel_num, 0))
    new_data.append(get_byte_n(channel_num, 1))
    new_data.append(get_byte_n(pos_mag, 0))
    new_data.append(get_byte_n(pos_mag, 1))
    new_data.append(get_byte_n(neg_mag, 0))
    new_data.append(get_byte_n(neg_mag, 1))
    new_data.append(get_byte_n(pos_pulse_width, 0))
    new_data.append(get_byte_n(pos_pulse_width, 1))
    new_data.append(get_byte_n(neg_pulse_width, 0))
    new_data.append(get_byte_n(neg_pulse_width, 1))
    new_data.append(get_byte_n(period, 0))
    new_data.append(get_byte_n(period, 1))
    new_data.append(get_byte_n(num_cycles, 0))
    new_data.append(get_byte_n(num_cycles, 1))

    return bytearray(new_data)


#Construct a bytearray containing information to enable recording
def intan_enable_recording():

    new_data = [config.NordicBleMessageCode.CodeEnableRecording.value]

    return bytearray(new_data)

#Construct a bytearray containing information to disable recording
def intan_disable_recording():

    new_data = [config.NordicBleMessageCode.CodeDisableRecording.value]

    return bytearray(new_data)