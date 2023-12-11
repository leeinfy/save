#include <zephyr/kernel.h>
#include <nrfx_spim.h>
#include <stdio.h>

void spi_init(void);
uint8_t spi_send_receive(uint8_t * send_buf, size_t send_length, uint8_t * recv_buf, size_t recv_length);