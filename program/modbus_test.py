import serial
import time

def CRC_16(arr):
	key = 0xA001
	crc = 0xFFFF
	for new in arr:
		for _ in range(8):
			if (crc^new) & 1:
				crc = (crc >> 1)^ key
			else:
				crc >>= 1
			new>>=1
	return crc>>8 , crc&0xFF
	
def getModbusArr(slave_address,function_code,register,register_count):
	arr = [slave_address&0xFF,function_code&0xFF,register>>8,register&0xFF,register_count>>8,register_count&0xFF]
	hi,lo = CRC_16(arr)
	arr.append(lo)
	arr.append(hi)
	return arr
	
def translateModbusArr(slave_address,function_code,arr):
	ret = []
	arr = list(arr)
	if len(arr)<5:
		print(arr)
		return ret
		
	if arr[0]!=slave_address:
		print(arr)
		return ret
		
	if arr[1]!=function_code:
		print(arr)
		return ret
		
	crc_h,crc_l = CRC_16(arr[:-2])
	if crc_h!= arr[-1] or crc_l!= arr[-2] :
		print(arr)
		return ret
		
	length = arr[2]//2
	
	for i in range(length):
		index = 3+i*2
		ret.append(arr[index]<<8|arr[index+1])
	return ret
		
portName = "/dev/ttyUSB0"
buad = 9600
parity = serial.PARITY_NONE
length = 8
stopBit = serial.STOPBITS_ONE

slave_address = 0x01
function_code = 0x03
register = 0x00
register_count = 0x40
response_time = 100

delay = 0.01+1/(buad/10)

while True:
	port = serial.Serial(portName,buad,parity=parity, bytesize=length , stopbits = stopBit)
	data = getModbusArr(slave_address,function_code,register,register_count)

	port.write(data)

	startTime = time.time()
	while port.out_waiting>0:
		time.sleep(delay)
		
	time.sleep(response_time/1000)

	lastLan = -1
	while lastLan!=port.in_waiting or port.in_waiting<5:
		lastLan = port.in_waiting
		time.sleep(delay)

	dataLen = port.in_waiting
	rec = port.read(dataLen)
	finishTime = time.time()-startTime
	#print(rec)
	
	print(translateModbusArr(slave_address,function_code,rec)[-1],1/finishTime)

port.close()

