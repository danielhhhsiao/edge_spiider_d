import paho.mqtt.client as mqtt
import random
import json
import datetime
import time

broker = "broker.hivemq.com"
port = 1883
topic = 'TEST/GOGO'

client_id = f'python-mqtt-{random.randint(0,1000)}'


def connect_mqtt():
	def on_connect(client, userdata, flags, rc):
		if rc == 0:
			print("Connect to MQTT Broker.")
		else:
			print("Failed to connect.")
			
	client = mqtt.Client(client_id)
	client.on_connect = on_connect
	client.username_pw_set("auo","auo0000")
	client.connect(broker, port)
	
	return client

def subscribe(client):
	def on_message(client,userdata,msg):
		print(f"Received {msg.payload.decode()} from {msg.topic} topic")
		
	client.subscribe(topic)
	client.on_message = on_message
		
def run():
	client = connect_mqtt()
	subscribe(client)
	client.loop_forever()

if __name__ == '__main__':
	run()
