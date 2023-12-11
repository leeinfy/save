#pragma once
#include <zephyr.h>
#include <string.h>
// the storage size is set to equal to BLE NUS service MTU
#define STORAGE_BUFFER_SIZE 120

//the variable type is depend on the adc resolution
typedef uint16_t data_buffer_storage_t[STORAGE_BUFFER_SIZE];

//need more than 1 buffer two form a ring buffer system
#define NUM_OF_BUFFER 2

typedef enum{
    IDLE = 0,
    IN_USE,
    FULL,
}data_buffer_status_t;

typedef struct{
    data_buffer_storage_t data;
    uint8_t data_count;
    data_buffer_status_t status;
    uint16_t data_offset;
}data_buffer_t;

typedef struct{
    data_buffer_t buffer[NUM_OF_BUFFER];
    uint8_t current_buffer_in_use;
}ring_data_buffer_t;

extern ring_data_buffer_t ring_data_buffer;

data_buffer_t* init_data_buffer(void);

/*@brief write the data to current data buffer
*/
data_buffer_t* write_data_buffer(data_buffer_t* buffer, uint16_t data);

void clear_data_buffer(data_buffer_t* buffer);

data_buffer_t* get_full_buffer(void);
