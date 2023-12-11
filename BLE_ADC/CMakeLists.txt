# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(BLE_ADC)

target_sources(app PRIVATE src/main.c
                           src/saadc.c
                           src/timer.c
                           src/ble.c
                           src/ble_data_buf.c
                           src/ble_send.c
                           src/ble_receive.c)

