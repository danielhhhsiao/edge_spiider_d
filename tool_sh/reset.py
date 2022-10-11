import os
import RPi.GPIO as GPIO
import time
from datetime import datetime
	
def script(cmd):
	log = True
	p = os.popen(cmd)
	t = p.read()
	if log:
		print(t)
	p.close()
		
def resetI2C():
	script("rmmod i2c_dev")
	script("rmmod i2c_bcm2835")
	script("modprobe i2c_bcm2835")
	script("modprobe i2c_dev")
	
	#have to work i2c
	script("i2cdetect -y 1") 

	
def run():
	serviceList = [
		'webServer.service',
		'mainProgram.service',
		'hostAP_check.service',
		'OTA_check.service',
		'statusServer.service',
		'start_NTP.service'
	]
	i2c_sck_pin = 3
	ST1_pin = 12
	ST2_pin = 13
	holdTime = 5
	reverse = True
	resetFlag = False
	
	GPIO.setwarnings(False)
	if GPIO.getmode()==-1 or GPIO.getmode()==None:
		GPIO.setmode(GPIO.BCM)
	GPIO.setup(ST1_pin,GPIO.OUT)
	GPIO.setup(ST2_pin,GPIO.OUT)
	GPIO.setup(i2c_sck_pin, GPIO.IN,pull_up_down=GPIO.PUD_UP)

	timeStr = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d_%H-%M-%S")
	print("Start",timeStr)
	GPIO.output(ST1_pin,0^reverse)
	GPIO.output(ST2_pin,0^reverse)
    
	if GPIO.input(i2c_sck_pin):
		#not do reset
		print("Not do thing")
		#restart i2c bus
		resetI2C()
		return 
		
	for s in serviceList:
		print("Stop service",s)
		script("systemctl stop "+s)
		#force cloas ST1/ST2
		GPIO.output(ST1_pin,0^reverse)
		GPIO.output(ST2_pin,0^reverse)
	
	startTime = time.time()
	GPIO.output(ST1_pin,1^reverse)
	
	print("Wait release pin")
	while not GPIO.input(i2c_sck_pin):
		if time.time()-startTime>=holdTime:
			resetFlag = True
			GPIO.output(ST2_pin,1^reverse)
	print("Hold time:",time.time()-startTime)
	print("resetFlag",resetFlag)
	
	#restart i2c bus
	resetI2C()
	
	if resetFlag:
		time.sleep(1)
		#reset config
		print("reset config")
		script("rm /home/pi/default/device.ini_ub")
		script("rm /home/pi/program/system.ini_ub")
		script("rm /home/pi/program/work.ini_ub")
		script("cp /home/pi/default/original_device.ini /home/pi/default/device.ini ")
		script("cp /home/pi/default/system.ini /home/pi/program/system.ini ")
		script("cp /home/pi/default/work.ini /home/pi/program/work.ini ")
		
		
		#clear file
		print("clear file")
		script("rm /home/pi/program/LocalSaved/*")
		
		#reset wifi connection information
		print("reset wifi connection information")
		script("/home/pi/tool_sh/wifi_disconnect.sh")
		
		#clear static network IP setting
		print("clear static network IP setting")
		script("/home/pi/tool_sh/ip_setting.sh -- -- -- -- -- -- -- -- --")
		
		#reset AP setting
		print("reset AP setting")
		script("hostname raspberry")
		
		time.sleep(1)
		
		GPIO.output(ST2_pin,0^reverse)
		script("/bin/hostAP_check.sh >> /home/pi/Desktop/test.txt")
		script("(sleep 5 ; shutdown -r 0 )&")
		
	
	else: 
		#keep to work
		GPIO.output(ST1_pin,0^reverse)
		GPIO.output(ST2_pin,0^reverse)
		
		for s in serviceList:
			print("Start saervice:",s)
			script("systemctl start "+s)
	
if __name__ == "__main__":
	run()
	
