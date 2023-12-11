#pragma once
#include <zephyr.h>
#include <nrfx_saadc.h>

#define SAADC_CHANNEL_NUM_APP 	1
//the buffer size is equal to number of enable channel
#define SAADC_BUFFER_SIZE		SAADC_CHANNEL_NUM_APP

typedef struct{
	nrfx_saadc_channel_t channel[SAADC_CHANNEL_NUM_APP];
	uint8_t channel_mask;
	nrf_saadc_resolution_t resolution;
	nrf_saadc_oversample_t oversampling;
	nrfx_saadc_adv_config_t adv_config;
	uint8_t irq_priority; 
}saadc_app_t;

/*@brief init saadc for the application
*/
void saadc_init_app(void);

/*@biref trigger one sampling and return saadd data from the data buffer
*/
uint16_t get_saadc_data (void);

/*@brief use to test the saddc module
 *capture and display the data
*/
void saadc_test(void);