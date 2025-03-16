from machine import Pin, SPI, I2C, UART
from drivers import sdcard
from drivers import gtu7 as gpsdriver
from drivers import bmp180 as bmp180driver
from ssd1306 import SSD1306_I2C

import os
import time
import _thread


def log_error(message, error=None):
    """Logger function for consistent logging"""
    print("[ERROR]:", message)
    if error:
        print("Details:", error)
    print("Hint: Check the wiring or follow troubleshooting steps from previous lessons.\n")

    
def init_oled():
    """Initialize the SSD1306 OLED Display module"""
    # https://www.tomshardware.com/how-to/oled-display-raspberry-pi-pico
    i2c = I2C(0,
            sda=Pin(16),
            scl=Pin(17),
            freq = 400000)
    
    oled = SSD1306_I2C(128, 64, i2c) # width is 128, height is 64
    
    oled.fill(0)   # Clear the OLED display object
    oled.text("Hello, students!", 0, 0)
    oled.show()    # Display the text
    time.sleep(2)  # Wait for `x` seconds
    oled.fill(0)   # Reset the display
    oled.show()    # Display the reset display
    
    return oled


def init_bmp180(test=True):
    """Initialize the BMP180 module"""
    bus =  I2C(0,
               sda=Pin(16),
               scl=Pin(17),
               freq=400000)

    bmp180 = bmp180driver.BMP180(bus)
    
    bmp180.oversample_sett = 2 # Accuracy, as defined in driver docs: https://github.com/micropython-IMU/micropython-bmp180
    bmp180.baseline = 101325   # Baseline pressure, as defined in driver docs: https://github.com/micropython-IMU/micropython-bmp180

    if test:
        try:
            assert isinstance(bmp180.temperature, float)
        except AssertionError:
            oled.text("BMP180_TEMP: ERR", 0, 0)
        else:
            oled.text("BMP180_TEMP: OK", 0, 0)

        try:
            assert isinstance(bmp180.pressure, float)
        except AssertionError:
            oled.text("BMP180_PRES: ERR", 0,10)
        else:
            oled.text("BMP180_PRES: OK", 0, 10)

        try:
            assert isinstance(bmp180.altitude, float)
        except AssertionError:
            oled.text("BMP180_ALTI: ERR", 0, 20)
        else:
            oled.text("BMP180_ALTI: OK", 0, 20)
            
        oled.show()

    return bmp180


def init_gtu7(test=True):
    """Initialize the GTU-7 GPS module"""
    uart = UART(1,
                baudrate=9600,
                timeout=3600,
                tx=Pin(4),
                rx=Pin(5))

    gtu7 = gpsdriver.GTU7(uart)
    
    if test:
        try:
            assert len(gtu7.gpgga()) == 4
        except AssertionError:
            oled.text("GTU7_GPGGA : ERR", 0, 30)
        else:
            oled.text("GTU7_GPGGA : OK", 0, 30)

        try:
            assert len(gtu7.gprmc()) == 5
        except AssertionError:
            oled.text("GTU7_GPRMC : ERR", 0,40)
        else:
            oled.text("GTU7_GPRMC : OK", 0, 40)
            
        oled.show()

    return gtu7


def init_sdcard(folder, test=True):
    """Initialize the SD Card module and create a folder on the SD card"""
    spi = machine.SPI(1,
                      baudrate=1000000,     # 1 MHz
                      sck=machine.Pin(10),  # Pico GPIO Pin 10
                      mosi=machine.Pin(11), # Pico GPIO Pin 11
                      miso=machine.Pin(12)) # Pico GPIO Pin 12
    cs = machine.Pin(13, machine.Pin.OUT)   # Pico GPIO Pin 13
    
    time.sleep(1) # Add a small delay before attempting to mount
    sd = sdcard.SDCard(spi, cs)
    os.mount(sd,folder)
    
    if test:
        try:
            assert folder[1:] in os.listdir()
        except AssertionError:
            oled.text("SD_CARD    : ERR", 0, 50)
        else:
            oled.text("SD_CARD    : OK", 0, 50)
            
        oled.show()


def write_csv_to_sdcard(folder, file_name, dataset, header=None):
    """Write data collected to a CSV file located on the SD card"""
    with open(folder + '/' + file_name,'a+') as csv_out:
        if header:
            dataset = header
            
        for data in dataset:
            if data == dataset[-1]:
                # If last element in the dataset, don't add a comma.
                csv_out.write('"'+str(data)+'"')
            else:
                csv_out.write('"'+str(data)+'",')
        csv_out.write('\n')


def read_csv_from_sdcard(folder, file_name):
    """Read data from the CSV file stored on the SD card"""
    csv_data = []
    with open(folder + '/' + file_name,'r') as csv_in:
        for line in csv_in:
            line=line.rstrip('\n')
            line=line.rstrip('\r')
            csv_data.append(line.split(','))

    return csv_data


def delete_files_from_sdcard_folder(folder):
    """Delete all the files from the SD card for a clean start"""
    for file in os.listdir(folder):
        try:
            os.remove(folder + '/' + file)
        except Exception as e:
            pass
            
            
if __name__ == "__main__":
    """Main function"""
    led = Pin(25, Pin.OUT)  # Assign onboard LED to variable
    led.toggle()            # Toggle on the onboard LED to indicate processing has started
    
    
    # -------------------------------------------------------------------------------- #
    # MODULE 1 (START): SSD1306 OLED Display
    # Uncomment these lines after wiring this module.
    
    try:
        oled = init_oled()      # Initialize the OLED display module
    except Exception as e:
        log_error("Failed to display message on the OLED display.", e)
        raise SystemExit
    
    # MODULE 1 (END)
    # -------------------------------------------------------------------------------- #
    
    
    try:
        ...
        # -------------------------------------------------------------------------------- #
        # MODULE 1 (START): SD Card
        # Uncomment these lines after wiring this module.
        
        sd_dir = '/sd'          # Directory created on SD card at root '/'. Expected format is '/<string>'. Example: '/sd'
        init_sdcard(sd_dir)     # Initialize the SD Card
        
        # MODULE 2 (END)
        # -------------------------------------------------------------------------------- #
        
    #    bmp180 = init_bmp180()  # Initialize the BMP_180 (Temp/Pressure module)
    #    gtu7 = init_gtu7()      # Initialize the GT-U7 (GPS module)

    #    delete_files_from_sdcard_folder('/sd') # Uncomment this to delete a folder and its contents.
        
        # Start a new thread and power off the OLED after a certain amount of time (in seconds)
    #    oled_off = lambda: (time.sleep(30), oled.poweroff())
    #    _thread.start_new_thread(oled_off, ())

    #    csv_header = [
    #        "date",
    #        "time",
    #        "latitude",
    #        "longitude",
    #        "velocity",
    #        "numSatellites",
    #        "temperature",
    #        "pressure",
    #        "altitude",
    #        ]
    #    write_csv_to_sdcard(sd_dir, "data.csv", None, csv_header) # Initialize CSV header
        
    #    for x in range(10):
    #        temp = bmp180.temperature  # Capture temperature, assign to `temp` variable
    #        p = bmp180.pressure        # Capture pressure, assign to `p` variable
    #        altitude = bmp180.altitude # Capture altitude, assign to `altitude` variable
            
    #        gpgga = gtu7.gpgga() # Capture NMEA GPGGA GPS data (http://aprs.gids.nl/nmea/#gga)
    #        gprmc = gtu7.gprmc() # Capture NMEA GPRMC GPS data (http://aprs.gids.nl/nmea/#rmc)
            
    #        data = [gprmc[0], gprmc[1], gprmc[2], gprmc[3], gprmc[4], gpgga[3], temp, p, altitude]
            
    #        write_csv_to_sdcard(sd_dir, "data.csv", data)
            
    except Exception as e:
        log_error("Failed to initialize module.", e)

        oled.fill(0)
        oled.text(str(e), 0, 0)
        oled.show()
        
        raise SystemExit
       
    # Read all the rows from the CSV and print them to the console.
    #for row in read_csv_from_sdcard(sd_dir, "data.csv"):
    #    print(row)
    
    led.toggle() # Toggle off the onboard LED to indicate processing has completed
