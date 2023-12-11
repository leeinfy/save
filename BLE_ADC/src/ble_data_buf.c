#include "ble_data_buf.h"
#include <logging/log.h>

//ble data buffer log module setup
LOG_MODULE_REGISTER(ble_data_buf, CONFIG_LOG_DEFAULT_LEVEL);

ring_data_buffer_t ring_data_buffer;

data_buffer_t* init_data_buffer(void){
    memset(&ring_data_buffer, 0, sizeof(ring_data_buffer_t));
    ring_data_buffer.buffer[0].status = IN_USE;
    return &ring_data_buffer.buffer[0];
}

data_buffer_t* write_data_buffer(data_buffer_t* buffer, uint16_t data){
    if (buffer->data_count < STORAGE_BUFFER_SIZE ){
        buffer->data[buffer->data_count] = data;
        buffer->data_count = buffer->data_count + 1;
    }
    if (buffer->data_count == STORAGE_BUFFER_SIZE){   
        buffer->status = FULL;
        uint8_t next_idle_buffer = ring_data_buffer.current_buffer_in_use;
        for(int i=0; i<NUM_OF_BUFFER; i++){
            next_idle_buffer = (next_idle_buffer + 1) % NUM_OF_BUFFER;
            if (ring_data_buffer.buffer[next_idle_buffer].status == IDLE){
                ring_data_buffer.buffer[next_idle_buffer].status = IN_USE;
                ring_data_buffer.current_buffer_in_use = next_idle_buffer;
                return &ring_data_buffer.buffer[next_idle_buffer];
            }
        }
        LOG_ERR("no storage avaliable");
    }
    return buffer;
}

void clear_data_buffer(data_buffer_t* buffer){
    memset(buffer, 0, sizeof(data_buffer_t));
}

data_buffer_t* get_full_buffer(void){
    for(int i=0; i<NUM_OF_BUFFER; i++){
        if (ring_data_buffer.buffer[i].status == FULL){
            return &ring_data_buffer.buffer[i];
        }
    }
    return NULL;
}