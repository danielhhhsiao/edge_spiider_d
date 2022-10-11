
sudo cython --embed -o AT32_OTA.c AT32_OTA.py -3
sudo gcc -Os -I /usr/include/python3.7m -o AT32_OTA_37 AT32_OTA.c -lpython3.7m -lpthread -lm -lutil -ldl
sudo rm AT32_OTA.c
sudo chmod 777 AT32_OTA_37
