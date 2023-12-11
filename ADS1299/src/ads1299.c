#include "ads1299.h"
#include "spi.h"

uint8_t read_ads1299_reg(uint8_t* buffer, uint8_t start, uint8_t size){
        uint8_t tx[2] = ADS1299_RREG_CMD(start, size);
        int err = spi_send_receive(tx,2,buffer,size);
        if (err != 0){
                return 1;
        }
        return 0;
}

void start_ads1299(){
        uint8_t tx = ADS1299_START_CMD;
        int err = spi_send_receive(&tx,1,NULL,0);
        if (err != 0){
                printf("spi err\n");
        }
}

uint8_t write_ads1299_reg(uint8_t* buffer, uint8_t start, uint8_t size){
        uint8_t tx_cmd[2] = ADS1299_WREG_CMD(start, size);
        uint8_t tx[2+size];
        memcpy(tx,tx_cmd,2);
        memcpy(tx+2,buffer,size);
        int err = spi_send_receive(tx,2+size,NULL,0);
        if (err != 0){
                printf("spi err\n");
        }
}

void read_data_ads1299(uint8_t* buffer, uint8_t size){
        uint8_t tx = ADS1299_RDATA_CMD;
        int err = spi_send_receive(&tx,1,buffer,size);
        if (err != 0){
                printf("spi err\n");
        }
}