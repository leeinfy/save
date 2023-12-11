#include "ble_send.h"
#include <logging/log.h>
LOG_MODULE_REGISTER(ble_send, CONFIG_LOG_DEFAULT_LEVEL);

K_SEM_DEFINE(buffer_full_sem, 0, 16);

ble_send_thread_app_t ble_send_app;

static uint16_t ble_data_counter = 0;

static void ble_send_buffer(data_buffer_t* buffer){
    adc_protocol_t send_msg = {0};
    send_msg.data_length = 244;
    send_msg.sensor_index = 6;
    send_msg.data_offset = buffer->data_offset;
    memcpy(send_msg.data, buffer->data, BLE_DATA_LENGTH);
    bt_nus_send(client, (uint8_t *)&send_msg, 244);
    clear_data_buffer(buffer);
}

static void add_saadc_data_to_ble_buf(void){
    if (!ble_send_app.sampling_enabled) return;
    data_buffer_t* buffer = write_data_buffer(ble_send_app.p_buffer, get_saadc_data());
    ble_data_counter ++;
    //data_buffer_t* buffer = write_data_buffer(ble_send_app.p_buffer, test_counter++);
    if (buffer != ble_send_app.p_buffer){
        ble_send_app.p_buffer = buffer;
        buffer->data_offset = ble_data_counter;
        k_sem_give(&buffer_full_sem);
    }
}

void init_ble_send_app(void){
    ble_send_app.sampling_enabled = 0;
    ble_send_app.p_buffer = init_data_buffer();
    set_timer_app_cb(add_saadc_data_to_ble_buf);
}

void ble_data_send_thread_func (void){
    while(1){
        if (k_sem_take(&buffer_full_sem, K_FOREVER) != 0){
            continue;
        }
        data_buffer_t* full_buffer = get_full_buffer();
        ble_send_buffer(full_buffer);
    }
}