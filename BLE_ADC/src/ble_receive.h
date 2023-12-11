#pragma once
#include <zephyr.h>
#include "ble.h"
#include "ble_send.h"

extern struct k_msgq host_command_msgq;

enum host_valid_command{
    ENABLE_ADC_SAMPLEING = 1,
};

void process_host_command_thread(void);