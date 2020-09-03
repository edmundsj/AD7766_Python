import numpy as np

"""
Convert a twos-complement set of bytes (1, 2, 3, etc.) into a floating-point value.
"""
def twosToInteger(twosBytes, firstByte='msb', bytesPerInteger=3):
    number = 0.0
    numberBytes = len(twosBytes)
    numberIntegers = int(numberBytes / bytesPerInteger)
    twosBytes = twosBytes.reshape(numberIntegers, bytesPerInteger)

    if(firstByte == 'msb'):
        for i in range(bytesPerInteger):
            number += np.power(256, bytesPerInteger - 1 - i) * twosBytes[:, i]

        isNegative = (twosBytes[:, 0] & 0b10000000) != 0 # checks the MSB of the twos complement number
        number -= np.power(2, 8*bytesPerInteger)*isNegative
    elif(firstByte == 'lsb'):
        for i in range(bytesPerInteger):
            number += np.power(256, i) * twosBytes[i]

        isNegative = bool(twosBytes[-1] & 0b10000000)
        number -= np.power(2, 8*bytesPerInteger)*isNegative

    return number


"""
Converts the AD7766 count to a differential voltage
"""
def countToVoltage(data, numberBits=24, maxVoltage=5):
    conversionFactor = maxVoltage / pow(2.0, numberBits)
    return np.multiply(data, conversionFactor)

