#include "ble.h"

#include <logging/log.h>
LOG_MODULE_REGISTER(ble, CONFIG_LOG_DEFAULT_LEVEL);

//advertising data
static const struct bt_data ad_data [] = {
    BT_DATA_BYTES(BT_DATA_FLAGS, BT_LE_AD_NO_BREDR),
    BT_DATA(BT_DATA_NAME_COMPLETE, CONFIG_BT_DEVICE_NAME, sizeof(CONFIG_BT_DEVICE_NAME)-1),
} ;

struct bt_conn* client = NULL;

static ble_app_t  ble_priv_app;

K_MSGQ_DEFINE(host_command_msgq, sizeof(host_command_t), 10, 1);
 
//set up ble configurate variables
static void ble_app_priv_set(void){
    ble_priv_app.adv_param =  *BT_LE_ADV_CONN;
    ble_priv_app.conn_param = *BT_LE_CONN_PARAM_DEFAULT;
    ble_priv_app.phy_param = *BT_CONN_LE_PHY_PARAM(BT_GAP_LE_PHY_2M,BT_GAP_LE_PHY_2M);
    ble_priv_app.nus_service_enabled = 0;
}

//on connected callback function
static void on_connected_cb (struct bt_conn *conn, uint8_t err){
    if (err != 0){
        LOG_ERR("bluetoth connection error (%u)", err);
        return;
    }
    client = bt_conn_ref(conn);
    LOG_INF("bluetooth client connected");
    dk_set_led_on(DK_LED1);

    int error;
    error = bt_conn_le_phy_update(conn, &ble_priv_app.phy_param);
    if (error != 0){
        LOG_ERR("bluetooth phy update fail (%d)", error);
    }

    error = bt_conn_le_data_len_update(conn, &ble_priv_app.data_len_param);
    if (error != 0){
        LOG_ERR("bluetotth data len update fail (%d)", error);
    }
}

//on disconnected callback function
static void on_disconnected_cb (struct bt_conn *conn, uint8_t reason){
    bt_conn_unref(conn);
    LOG_INF("bluetooth client disconnected reason(%u)", reason);
}

//on connection param update callback function
static void on_conn_param_updated_cb (struct bt_conn *conn, uint16_t interval, uint16_t latency, uint16_t timeout){
    double connection_interval = interval*1.25;
    uint16_t supervision_timeout = timeout*10;
    LOG_INF("connection parameters update: interval %.2f ms, latency %d intervals, timeout %d ms", connection_interval, latency, supervision_timeout);
}

static const char *phy2str(uint8_t phy)
{
	switch (phy) {
	case 0: return "No packets";
	case BT_GAP_LE_PHY_1M: return "LE 1M";
	case BT_GAP_LE_PHY_2M: return "LE 2M";
	case BT_GAP_LE_PHY_CODED: return "LE Coded";
	default: return "Unknown";
	}
}

//On phy updated callback function
static void on_phy_updated_cb (struct bt_conn *conn, struct bt_conn_le_phy_info * param){
    LOG_INF("LE PHY updated: TX PHY %s, RX PHY %s\n", phy2str(param->tx_phy), phy2str(param->rx_phy));
}

static void on_data_len_updated_cb(struct bt_conn *conn, struct bt_conn_le_data_len_info *info){
    LOG_INF("LE data len updated: TX (len: %d time: %d)"
	       " RX (len: %d time: %d)\n", info->tx_max_len,
	       info->tx_max_time, info->rx_max_len, info->rx_max_time);
}

//connection call back register
static struct bt_conn_cb ble_conn_cb = {
    .connected = on_connected_cb,
    .disconnected = on_disconnected_cb,
    .le_param_updated = on_conn_param_updated_cb,
    .le_phy_updated = on_phy_updated_cb,
    .le_data_len_updated = on_data_len_updated_cb,
};

static void nus_send_enabled(enum bt_nus_send_status status){
    ble_priv_app.nus_service_enabled = 1;
    LOG_DBG("NUS services is subscribed");
}

static void nus_received(struct bt_conn *conn, const uint8_t* const data, uint16_t len){
    host_command_t host_msg = {
        .command = data[0],
        .value = data[1],
    };
    k_msgq_put(&host_command_msgq, &host_msg, K_NO_WAIT);
    LOG_DBG("NUS message received and push to message queue");
}

static struct bt_nus_cb nus_cb ={
    .send_enabled = nus_send_enabled,
    .received = nus_received,
};


void init_ble_app(void){
    ble_app_priv_set();    
    int err;
    //enable the bluetooth module
    err = bt_enable(NULL);
    if (err !=0){
        LOG_ERR("bt_enable err (%x)", err);
    }

    //wait for the bluetooth device to get ready
    while(!bt_is_ready()){
        k_sleep(K_MSEC(1));
    }

    //assign a connection callback register
    bt_conn_cb_register(&ble_conn_cb);

    err = bt_nus_init(&nus_cb);
    if (err != 0){
        LOG_ERR("bt_nus_init error (%x)", err);
    }

    //start advertising with default connectable advertising param 
    err = bt_le_adv_start(&ble_priv_app.adv_param, ad_data, ARRAY_SIZE(ad_data), NULL, 0);
    if (err !=0){
        LOG_ERR("bt_le_adv_start err (%x)", err);
    }
    LOG_INF("bluetooth initilization SUCCESS");
}

void ble_test_send(void){
    uint8_t data = 0;
    while (1){
        if (ble_priv_app.nus_service_enabled){
            bt_nus_send(client, &data, 1);
        }
        data++;
        k_sleep(K_SECONDS(1));
    }
}