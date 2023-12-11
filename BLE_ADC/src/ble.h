#pragma once
#include <bluetooth/bluetooth.h>
#include <bluetooth/gap.h>
#include <bluetooth/conn.h>
#include <bluetooth/services/nus.h>
#include <dk_buttons_and_leds.h>

typedef struct{
    struct bt_le_adv_param adv_param;
    struct bt_le_conn_param conn_param;
    struct bt_conn_le_phy_param phy_param;
    struct bt_conn_le_data_len_param data_len_param;
    bool nus_service_enabled;
    void (*received) (struct bt_conn *conn, const uint8_t * const data, uint16_t len);
}ble_app_t;

extern struct bt_conn* client;

typedef struct __attribute__((packed,aligned(1))) {
    uint8_t command;
    uint8_t value;
}host_command_t;

/*@brief start the bluetooth advertising on application layer
*/
void init_ble_app(void);

void ble_test_send();