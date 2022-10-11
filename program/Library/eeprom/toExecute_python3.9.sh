sudo cython --embed -o eeprom_at24c256.c eeprom_at24c256.py -3
sudo gcc -Os -I /usr/include/python3.9 -o eeprom eeprom_at24c256.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm eeprom_at24c256.c
sudo chmod 777 eeprom
