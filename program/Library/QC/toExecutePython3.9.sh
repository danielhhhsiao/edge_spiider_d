sudo cython --embed -o QC_LED.c QC_LED.py -3
sudo gcc -Os -I /usr/include/python3.9 -o QC_LED QC_LED.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm QC_LED.c
sudo chmod 777 QC_LED

sudo cython --embed -o QC_battery.c QC_battery.py -3
sudo gcc -Os -I /usr/include/python3.9 -o QC_battery QC_battery.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm QC_battery.c
sudo chmod 777 QC_battery

sudo cython --embed -o QC_DIO.c QC_DIO.py -3
sudo gcc -Os -I /usr/include/python3.9 -o QC_DIO QC_DIO.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm QC_DIO.c
sudo chmod 777 QC_DIO

sudo cython --embed -o QC_I2C.c QC_I2C.py -3
sudo gcc -Os -I /usr/include/python3.9 -o QC_I2C QC_I2C.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm QC_I2C.c
sudo chmod 777 QC_I2C

sudo cython --embed -o QC_VIB.c QC_VIB.py -3
sudo gcc -Os -I /usr/include/python3.9 -o QC_VIB QC_VIB.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm QC_VIB.c
sudo chmod 777 QC_VIB

sudo cython --embed -o QC_DAQ.c QC_DAQ.py -3
sudo gcc -Os -I /usr/include/python3.9 -o QC_DAQ QC_DAQ.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm QC_DAQ.c
sudo chmod 777 QC_DAQ
