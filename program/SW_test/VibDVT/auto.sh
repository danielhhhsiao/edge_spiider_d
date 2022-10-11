#!/bin/s

#parameter:
#						bus	cs	fs		time	ch		scale		commend
python3	VibrationHub.py	0	0	1000	0  		000001	2,2,2,2,2,2	"sensor scan 00"
python3	VibrationHub.py	0	1	1000	0  		000001	2,2,2,2,2,2	"sensor scan 01" 
python3	VibrationHub.py	0	0	4000	30  	110000	4,8,2,2,2,2	"sampling" 

