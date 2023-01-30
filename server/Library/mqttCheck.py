import paho.mqtt.client as mqtt
import io
import sys


def mqttCheckStatus(ip, port, user, passwd):
	print('Hostname: '+ip)
	print('Port: '+port)
	print('user: '+user)
	print('password: '+passwd)	
	print('')
	print('=====Test Result=====')
	try:
		client =mqtt.Client()
		client.username_pw_set(user,passwd)
		client.connect(ip, int(port), 60)
		print("MQTT connect success.")	
		client.disconnect()
	except:
		print("MQTT connect failed.")
		return 1
	return 0

if __name__=="__main__":
	
	ip=str(sys.argv[1])
	port=str(sys.argv[2])
	user=str(sys.argv[3])
	pwd=str(sys.argv[4])
	mqttCheckStatus(ip,port,user,pwd)
	
	#mqttCheckStatus('broker.hivemq.com',1883,'','')
