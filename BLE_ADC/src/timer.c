#include "timer.h"
#include <logging/log.h>

//saadc log module setup
LOG_MODULE_REGISTER(timer, CONFIG_LOG_DEFAULT_LEVEL);

//enable this when testing the timer
#include <zephyr/drivers/gpio.h>
#define GPIO_PIN 26
const struct device* gpio0_dev = DEVICE_DT_GET(DT_NODELABEL(gpio0));
////////////////////

static const nrfx_timer_t timer0_instance = NRFX_TIMER_INSTANCE(0);

static timer_app_t timer0_app_priv;

/*@biref set up the timer parameter 
*/
static void timer_app_priv_set(void){
    //set timer configurate to default
    nrfx_timer_config_t timer_default_config = NRFX_TIMER_DEFAULT_CONFIG;
    timer0_app_priv.config = timer_default_config;

    //set the period to 500us =  2kHz
    timer0_app_priv.time_us = 500;

    timer0_app_priv.event_cb = NULL;
}

void timer_event_handler (nrf_timer_event_t event_type, void* p_context){
    switch (event_type){
        case NRF_TIMER_EVENT_COMPARE0:
            timer0_app_priv.event_cb();
            LOG_DBG("timer app event triggered");
            break;
        default:
            break;
    }
}


void timer_init_app(void){
    timer_app_priv_set();
    nrfx_err_t err;

    //zephyr os, enalbe timer0 interrupt signal
    IRQ_DIRECT_CONNECT(TIMER0_IRQn, 0, nrfx_timer_0_irq_handler, 0);
    irq_enable(TIMER0_IRQn);

    err = nrfx_timer_init(&timer0_instance, &timer0_app_priv.config, timer_event_handler);
    if (err != NRFX_SUCCESS){
		LOG_ERR("nrfx_timer_init err(%x)", err);
		return;
	} 

    //get the tick of 500us
    uint32_t ticks = nrfx_timer_us_to_ticks(&timer0_instance, timer0_app_priv.time_us);
    LOG_DBG("timer ticks (%u)", ticks);

    

    //set channel 0 to compare mode
    nrfx_timer_extended_compare(&timer0_instance, NRF_TIMER_CC_CHANNEL0, ticks, NRF_TIMER_SHORT_COMPARE0_CLEAR_MASK, true);

    if (nrfx_timer_is_enabled(&timer0_instance)){
        nrfx_timer_disable(&timer0_instance);
        nrfx_timer_clear(&timer0_instance);
    }

    LOG_INF("timer initlization SUCCESS");
}

void timer_start_app(void){
    nrfx_timer_enable(&timer0_instance);
    if (nrfx_timer_is_enabled(&timer0_instance)){
        LOG_INF("timer START");
    }
}

void timer_stop_app(void){
    nrfx_timer_disable(&timer0_instance);
    nrfx_timer_clear(&timer0_instance);
}

void set_timer_app_cb(timer_app_cb_t event_cb){
    timer0_app_priv.event_cb = event_cb;
}

//function cast the gpio toggle into timer_app_cb_t
static void gpio_timer_cb (void){
    int err;
    err = gpio_pin_toggle(gpio0_dev,(gpio_pin_t)GPIO_PIN);
    if(err != 0){
        LOG_ERR("gpio toogle fail (%d)", err);
    }
}

void timer_test(void){
    while (!device_is_ready(gpio0_dev)){
        k_sleep(K_MSEC(1));
    }

    int err;
    err = gpio_pin_configure(gpio0_dev, (gpio_pin_t)GPIO_PIN, GPIO_OUTPUT);
    if (err != 0){
        LOG_DBG("GPIO pin config err (%d)", err);
    }

    timer_init_app();
	set_timer_app_cb(gpio_timer_cb);
	timer_start_app();
    while(1){
        k_sleep(K_SECONDS(1));
    }
}