import serial
import time

ser = serial.Serial('COM6',9600)

file=open('sample.csv', 'r+')

while 1:
    line=file.readline()
    if not line:
        break
    ser.write(line.encode())
    time.sleep(2)
