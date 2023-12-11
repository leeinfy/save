/*
 * Copyright (c) 2012-2014 Wind River Systems, Inc.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr.h>

#include "saadc.h"
#include "timer.h"
#include "ble_data_buf.h"
#include "ble.h"
#include "ble_send.h"
#include "ble_receive.h"

#include <logging/log.h>
LOG_MODULE_REGISTER(main, CONFIG_LOG_DEFAULT_LEVEL);

void main(void){

	timer_init_app();
	saadc_init_app();
	init_ble_app();

	init_ble_send_app();
	timer_start_app();
}

K_THREAD_DEFINE(ble_data_send_thread, 1024, ble_data_send_thread_func, NULL, NULL, NULL, -10, 0, 0);

K_THREAD_DEFINE(ble_host_command, 1024, process_host_command_thread, NULL, NULL, NULL, -11, 0, 0);