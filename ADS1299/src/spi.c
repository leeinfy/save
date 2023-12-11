#include "spi.h"

#define ICM_SPIM_SCLK_PIN           (37)      //p1.05
#define ICM_SPIM_MOSI_PIN           (47)
#define ICM_SPIM_MISO_PIN           (45)
#define ICM_SPIM_SS_PIN             (43)

static const nrfx_spim_t spi_dev = NRFX_SPIM_INSTANCE(1);

void spi_init(void){
        nrfx_err_t err;
        nrfx_spim_uninit(&spi_dev);
        nrfx_spim_config_t config = NRFX_SPIM_DEFAULT_CONFIG(ICM_SPIM_SCLK_PIN,
                                                             ICM_SPIM_MOSI_PIN,
                                                             ICM_SPIM_MISO_PIN,
                                                             ICM_SPIM_SS_PIN);
        config.frequency = NRF_SPIM_FREQ_4M;
	    err = nrfx_spim_init(&spi_dev, &config, NULL, NULL);
	    if (err != NRFX_SUCCESS) {
		    printk("Failed to initialize ICM_SPI: 0x%0x\n", err);
		return ;
	    }
        printk("ICM_SPI_IINT SUCCESS");
}

uint8_t spi_send_receive(uint8_t * send_buf, size_t send_length, uint8_t * recv_buf, size_t recv_length){
        int err = 0;

        nrfx_spim_xfer_desc_t xfer_desc = NRFX_SPIM_XFER_TRX(send_buf, send_length, recv_buf, recv_length);

        err = nrfx_spim_xfer(&spi_dev, &xfer_desc, 0);
        if (err != NRFX_SUCCESS) {
            printk("ICM_SPI transfer FAIL: 0x%0x\n", err);
            return 1;
	    }
        return 0;
}
