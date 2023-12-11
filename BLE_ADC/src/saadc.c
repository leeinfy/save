#include "saadc.h"
#include <logging/log.h>

//saadc log module setup
LOG_MODULE_REGISTER(saadc, CONFIG_LOG_DEFAULT_LEVEL);

static nrf_saadc_value_t saadc_buffer[SAADC_BUFFER_SIZE] = {0};
// static nrf_saadc_value_t saadc_buffer2[SAADC_BUFFER_SIZE] = {0};

static saadc_app_t saadc_app_priv;

/*@brief set up the saadc parameter for the driver
*/
static void saadc_app_priv_set(void){
	//set saadc channel config, we only use 1 channel single end
	nrfx_saadc_channel_t saadc_channel_config = NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN0,0);
	saadc_app_priv.channel[0] = saadc_channel_config;

	//set the channel mask
	saadc_app_priv.channel_mask = 0;
	for (int i=0;i<SAADC_CHANNEL_NUM_APP;i++){
		saadc_app_priv.channel_mask |= (1<<i);
	}

	//set the saadc resolution to 8 bit
	saadc_app_priv.resolution = NRF_SAADC_RESOLUTION_14BIT;

	//disable oversampling
	saadc_app_priv.oversampling = NRF_SAADC_OVERSAMPLE_DISABLED;

	//set saadc default interrupt priority
	saadc_app_priv.irq_priority = NRFX_SAADC_DEFAULT_CONFIG_IRQ_PRIORITY;
}

// static void nrfx_saadc_event_handler(nrfx_saadc_evt_t const *p_event){
// }

void saadc_init_app(void){
	saadc_app_priv_set();

	nrfx_err_t err;

	err = nrfx_saadc_init(saadc_app_priv.irq_priority);
	if (err != NRFX_SUCCESS){
		LOG_ERR("nrfx_saadc_init err(%x)", err);
	}

	for (int i=0;i<SAADC_CHANNEL_NUM_APP;i++){
		err = nrfx_saadc_channel_config(&saadc_app_priv.channel[i]);
		if (err != NRFX_SUCCESS){
			LOG_ERR("nrfx_saadc_channel(%d)_config err(%x)", i, err);
			return;
		}
	}

	//set up the saadc in simple mode, use blocking manner
	err = nrfx_saadc_simple_mode_set(saadc_app_priv.channel_mask, saadc_app_priv.resolution, saadc_app_priv.oversampling, NULL);
	if (err != NRFX_SUCCESS){
		LOG_ERR("nrfx_saadc_simple_mode_set err(%x)", err);
		return;
	}

	//set up buffer 1 and 2 for double buffered conversions
	err = nrfx_saadc_buffer_set(saadc_buffer, SAADC_BUFFER_SIZE);
	if (err != NRFX_SUCCESS){
		LOG_ERR("nrfx_saadc_buffer1_set err(%x)", err);
		return;
	}
	//only 1 buffer is needed for blocking manner
	// err = nrfx_saadc_buffer_set(saadc_buffer2, SAADC_BUFFER_SIZE);
	// if (err != NRFX_SUCCESS){
	// 	LOG_DBG("nrfx_saadc_buffer2_set err(%x)", err);
	// 	return;
	// }

	LOG_INF("saadc initialization SUCCESS");
}

uint16_t get_saadc_data (void){
	nrfx_saadc_mode_trigger();
	return saadc_buffer[0];
}

void saadc_test(void){
	saadc_init_app();

	while(1){
		nrfx_saadc_mode_trigger();
		LOG_INF("BUFFER 1 (%u)", saadc_buffer[0]);
		// LOG_INF("BUFFER 2 (%u)", saadc_buffer2[0]);
		k_sleep(K_SECONDS(1));
	}
	
}