
sudo cython --embed -o server.c server.py -3
sudo gcc -Os -I /usr/include/python3.9 -o server server.c -lpython3.9 -lpthread -lm -lutil -ldl
sudo rm server.c
sudo chmod 777 server
