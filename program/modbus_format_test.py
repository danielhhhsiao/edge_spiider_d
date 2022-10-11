from Library.sample import modbus_process
import numpy as np

def printHex(arr):
	print("byte arr: [ ",end="")
	for a in arr:
		print(hex(a),end=" ")
	print(" ]")

print("\n------------------------------------------ LSB")
print("Testing float32")
print("target is 123.456 (IEEE754)")
data = 0x42f6e979
print("input data hex("+hex(data)+")","bit({:032b})".format(data))
arr = np.array([data],dtype=np.uint32)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2float32("LSB",arr))

print("\n------------------------------------------ LSB")
print("Testing float32")
print("target is 3.14159 (IEEE754)")
data = 0x40490fd0
print("input data hex("+hex(data)+")","bit({:032b})".format(data))
arr = np.array([data],dtype=np.uint32)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2float32("LSB",arr))

print("\n------------------------------------------ LSB")
print("Testing int8")
print("target is -3")
data = 0xFD
print("input data hex("+hex(data)+")","bit({:08b})".format(data))
arr = np.array([data],dtype=np.uint8)
printHex(arr)
print("output",modbus_process.byte2int8("LSB",arr))


print("\n------------------------------------------ LSB")
print("Testing int16")
print("target is -3")
data = 0xFFFD
print("input data hex("+hex(data)+")","bit({:016b})".format(data))
arr = np.array([data],dtype=np.uint16)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2int16("LSB",arr))

print("\n------------------------------------------ LSB")
print("Testing int32")
print("target is -3")
data = 0xFFFFFFFD
print("input data hex("+hex(data)+")","bit({:032b})".format(data))
arr = np.array([data],dtype=np.uint32)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2int32("LSB",arr))


print("\n------------------------------------------ LSB")
print("Testing uint8")
print("target is 200")
data = 0xc8
print("input data hex("+hex(data)+")","bit({:08b})".format(data))
arr = np.array([data],dtype=np.uint8)
printHex(arr)
print("output",modbus_process.byte2uint8("LSB",arr))


print("\n------------------------------------------ LSB")
print("Testing uint16")
print("target is 40000")
data = 0x9c40
print("input data hex("+hex(data)+")","bit({:016b})".format(data))
arr = np.array([data],dtype=np.uint16)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2uint16("LSB",arr))


print("\n------------------------------------------ LSB")
print("Testing uint32")
print("target is 3000000000")
data = 0xb2d05e00
print("input data hex("+hex(data)+")","bit({:08b})".format(data))
arr = np.array([data],dtype=np.uint32)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2uint32("LSB",arr))


print("\n------------------------------------------ LSB")
print("Testing BCD")
print("target is 1234")
data = 0x1234
print("input data hex("+hex(data)+")","bit({:016b})".format(data))
arr = np.array([data],dtype=np.uint16)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2BCD("LSB",arr))

print("\n------------------------------------------ LSB")
print("Testing bit8")
print("target is 11110101")
data = 0xF5
print("input data hex("+hex(data)+")","bit({:08b})".format(data))
arr = np.array([data],dtype=np.uint8)
printHex(arr)
print("output",modbus_process.byte2bit8("LSB",arr))

print("\n------------------------------------------ LSB")
print("Testing bit16")
print("target is 1111111100110101")
data = 0xFF35
print("input data hex("+hex(data)+")","bit({:016b})".format(data))
arr = np.array([data],dtype=np.uint16)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2bit16("LSB",arr))



print("\n------------------------------------------ MSB")
print("Testing float32")
print("target is 123.456 (IEEE754)")
data = 0x42f6e979
data = int('{:032b}'.format(data)[::-1],2)
print("input data hex("+hex(data)+")","bit({:032b})".format(data))
arr = np.array([data],dtype=np.uint32)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2float32("MSB",arr))

print("\n------------------------------------------ MSB")
print("Testing float32")
print("target is 3.14159 (IEEE754)")
data = 0x40490fd0
data = int('{:032b}'.format(data)[::-1],2)
print("input data hex("+hex(data)+")","bit({:032b})".format(data))
arr = np.array([data],dtype=np.uint32)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2float32("MSB",arr))

print("\n------------------------------------------ MSB")
print("Testing int8")
print("target is -3")
data = 0xFD
data = int('{:08b}'.format(data)[::-1],2)
print("input data hex("+hex(data)+")","bit({:08b})".format(data))
arr = np.array([data],dtype=np.uint8)
printHex(arr)
print("output",modbus_process.byte2int8("MSB",arr))


print("\n------------------------------------------ MSB")
print("Testing int16")
print("target is -3")
data = 0xFFFD
data = int('{:016b}'.format(data)[::-1],2)
print("input data hex("+hex(data)+")","bit({:016b})".format(data))
arr = np.array([data],dtype=np.uint16)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2int16("MSB",arr))

print("\n------------------------------------------ MSB")
print("Testing int32")
print("target is -3")
data = 0xFFFFFFFD
data = int('{:032b}'.format(data)[::-1],2)
print("input data hex("+hex(data)+")","bit({:032b})".format(data))
arr = np.array([data],dtype=np.uint32)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2int32("MSB",arr))


print("\n------------------------------------------ MSB")
print("Testing uint8")
print("target is 200")
data = 0xc8
data = int('{:08b}'.format(data)[::-1],2)
print("input data hex("+hex(data)+")","bit({:08b})".format(data))
arr = np.array([data],dtype=np.uint8)
printHex(arr)
print("output",modbus_process.byte2uint8("MSB",arr))


print("\n------------------------------------------ MSB")
print("Testing uint16")
print("target is 40000")
data = 0x9c40
data = int('{:016b}'.format(data)[::-1],2)
print("input data hex("+hex(data)+")","bit({:016b})".format(data))
arr = np.array([data],dtype=np.uint16)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2uint16("MSB",arr))


print("\n------------------------------------------ MSB")
print("Testing uint32")
print("target is 3000000000")
data = 0xb2d05e00
data = int('{:032b}'.format(data)[::-1],2)
print("input data hex("+hex(data)+")","bit({:08b})".format(data))
arr = np.array([data],dtype=np.uint32)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2uint32("MSB",arr))


print("\n------------------------------------------ MSB")
print("Testing BCD")
print("target is 1234")
data = 0x1234
data = int('{:016b}'.format(data)[::-1],2)
print("input data hex("+hex(data)+")","bit({:016b})".format(data))
arr = np.array([data],dtype=np.uint16)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2BCD("MSB",arr))

print("\n------------------------------------------ MSB")
print("Testing bit8")
print("target is 11110101")
data = 0xF5
data = int('{:08b}'.format(data)[::-1],2)
print("input data hex("+hex(data)+")","bit({:08b})".format(data))
arr = np.array([data],dtype=np.uint8)
printHex(arr)
print("output",modbus_process.byte2bit8("MSB",arr))

print("\n------------------------------------------ MSB")
print("Testing bit16")
print("target is 1111111100110101")
data = 0xFF35
data = int('{:016b}'.format(data)[::-1],2)
print("input data hex("+hex(data)+")","bit({:016b})".format(data))
arr = np.array([data],dtype=np.uint16)
arr.dtype = np.uint8
arr = arr[::-1] ##serial is high byte first
printHex(arr)
print("output",modbus_process.byte2bit16("MSB",arr))


