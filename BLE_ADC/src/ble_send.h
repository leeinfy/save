#pragma once
#include <zephyr.h>
#include "saadc.h"
#include "timer.h"
#include "ble_data_buf.h"
#include "ble.h"
#include <stdio.h>

#define BLE_DATA_LENGTH 240

typedef struct{
    bool sampling_enabled;
    data_buffer_t* p_buffer;
}ble_send_thread_app_t;

extern ble_send_thread_app_t ble_send_app;

typedef struct{
    uint8_t  data_length;
    uint8_t sensor_index;
    uint16_t data_offset;
    uint8_t data[BLE_DATA_LENGTH];
}adc_protocol_t;

void init_ble_send_app(void);

void ble_data_send_thread_func (void);