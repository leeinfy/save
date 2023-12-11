#pragma once
#include <zephyr.h>
#include <nrfx_timer.h>

typedef void (*timer_app_cb_t) (void);

typedef struct{
    nrfx_timer_config_t config;
    uint32_t time_us;
    timer_app_cb_t event_cb;
}timer_app_t;

/*@brief init timer for the application
*/
void timer_init_app(void);

/*@brief do not use this function in application
 *this function is use by the HAL driver as a timer interrupt event handler
*/
void timer_event_handler (nrf_timer_event_t event_type, void* p_context);

/*@biref start the timer 
*/
void timer_start_app(void);

/*@brief stop the timer
*/
void timer_stop_app(void);

/*@brief assign the application layer call back function of timer0 
*/
void set_timer_app_cb(timer_app_cb_t event_cb);

/*@brief test the timer
*/
void timer_test(void);