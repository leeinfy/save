#include "ble_receive.h"
#include <logging/log.h>
LOG_MODULE_REGISTER(host_command, CONFIG_LOG_DEFAULT_LEVEL);

void process_host_command_thread(void){
    host_command_t host_msg;
    while(1){
        k_msgq_get(&host_command_msgq, &host_msg, K_FOREVER);

        switch(host_msg.command){
            case ENABLE_ADC_SAMPLEING:{
                if(host_msg.value != ble_send_app.sampling_enabled) {
                    if (host_msg.value == 1) LOG_INF("enable sampling");
                    else if (host_msg.value == 0) LOG_INF("disable sampling");
                    ble_send_app.sampling_enabled = host_msg.value;
                }
                break;
            }
            default:{
                LOG_INF("Unknown host message");
                break;
            }
        }
    }
}