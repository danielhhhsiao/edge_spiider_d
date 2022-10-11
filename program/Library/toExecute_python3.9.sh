
sudo cython --embed -o ADCHub.c ADCHub.py -3
sudo gcc -Os -I /usr/include/python3.9 -o DAQ_module ADCHub.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm ADCHub.c
sudo chmod 777 DAQ_module

sudo cython --embed -o VibrationHub.c VibrationHub.py -3
sudo gcc -Os -I /usr/include/python3.9 -o Vib_module VibrationHub.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm VibrationHub.c
sudo chmod 777 Vib_module

sudo cython --embed -o I2Ccheck.c I2Ccheck.py -3
sudo gcc -Os -I /usr/include/python3.9 -o I2Ccheck I2Ccheck.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm I2Ccheck.c
sudo chmod 777 I2Ccheck

sudo cython --embed -o DIOtest.c DIOtest.py -3
sudo gcc -Os -I /usr/include/python3.9 -o DIOtest DIOtest.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm DIOtest.c
sudo chmod 777 DIOtest
