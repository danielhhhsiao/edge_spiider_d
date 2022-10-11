import os
import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	
	parser.add_argument("file1",type=str,help="bootloader hex-file path. Example /home/pi/xx.hex")
	parser.add_argument("file2",type=str,help="app hex-file path. Example /home/pi/xx.hex")
	args = parser.parse_args()
	#Read file
	in1 = open(args.file1,'r')
	in2 = open(args.file2,'r')
	out = open('output.hex','w')
	
	lines_in1 = [i for i in in1]
	lines_in2 = [i for i in in2]
	del lines_in1[-1]
	lines = lines_in1 + lines_in2
	for line in lines:
		out.write(line)
	
	in1.close()
	in2.close()
	out.close()
	
	
