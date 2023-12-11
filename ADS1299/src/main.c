#include <zephyr/kernel.h>
#include <nrfx_spim.h>
#include <stdio.h>
#include "ads1299.h"

int main(void)
{       spi_init();
        uint8_t data_buffer[27] = {0};
        start_ads1299();
        while(1){
                read_data_ads1299(data_buffer, 27);
                for(int i=0;i<27;i++){
                        printf("%d ", data_buffer[i]);
                }
                printf("stop\n");
                k_sleep(K_SECONDS(1));
        }
        return 0;
}
