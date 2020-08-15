import serial
import numpy as np
import time
import matplotlib.pyplot as plt

maxBytes = 90000
byteCounter = 0
dataBuffer = np.zeros(maxBytes + 1020)

arduino = serial.Serial()
arduino.port = '/dev/cu.usbmodem14141'
arduino.baudrate = 7372800
startTime = time.perf_counter()
arduino.open()
randomString=b'ENDTRANSACTION';

bytesWritten = arduino.write(b'y')

while byteCounter < maxBytes:
    bytesAvailable = arduino.in_waiting
    dataBuffer[byteCounter:byteCounter+bytesAvailable] = \
            np.frombuffer(arduino.read_until(randomString, size=bytesAvailable), dtype='uint8')
    byteCounter += bytesAvailable
    print(byteCounter)

arduino.close()

endTime = time.perf_counter()
deltaTime = endTime - startTime
byteRate = maxBytes / deltaTime
bitRate = byteRate * 8

print(f'Byte Rate: {byteRate}')
print(f'Bitrate: {bitRate}')
np.savetxt('arduino_raw_data.csv', dataBuffer, delimiter=',')
