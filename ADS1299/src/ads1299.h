#include <zephyr.h>
#include  "ads1299_reg.h"

//System CMD
//wake-up from standby mode
#define ADS1299_WAKEUP_CMD 0x02
//enter standby mode
#define ADS1299_STANDBY_CMD 0x04
//reset the device
#define ADS1299_RESET_CMD 0x06
//start and restart(synchronize) conversions
#define ADS1299_START_CMD 0x08
//stop conversion
#define ADS1299_STOP_CMD 0x0A

//Data Read CMD
//default mode, enable read data continuous mode
#define ADS1299_RDATAC_CMD 0x10
//stop read ata continuously mode
#define ADS1299_SDATAC_CMD 0x11
//read tat by command
#define ADS1299_RDATA_CMD 0x12

//Register Read CMD
//start is the starting register address for read or write commands
//size is the number of reg want to read or write
#define ADS1299_RREG_CMD(start,size) {0b00100000 | start, size}
#define ADS1299_WREG_CMD(start,size) {0b01000000 | start, size}

uint8_t read_ads1299_reg(uint8_t*, uint8_t, uint8_t);

uint8_t write_ads1299_reg(uint8_t*, uint8_t, uint8_t);