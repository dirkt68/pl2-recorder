import subprocess
import io
import struct
import cmath
import math

# just for visualization
from matplotlib import pyplot as plt


# SHORT FUNCTIONS
# if power of two, number would look like 1000, 10000, etc.
# subtracting by 1 would make the number look like 0111, 01111
# ANDing together would result in a perfect zero
# if not power of two, number - 1 & number would not produce a zero
def isPowerOfTwo(n): return (n != 0) and (n & (n - 1) == 0)


# CONSTANTS
# filenames and executable
filename = "scale_test.mp3"
exe = "ffmpeg.exe"

SAMPLE_RATE = 44_100
# 88200 bytes per second
# 1/10 of a second = 8_820
WINDOW_TIMING = 4_100

# format strings for unpacking
FMT_4B_LE = "<L"
FMT_ALL_ATTRS = "<HHLLHH"

# debug print flag
DEBUG = False

# FUNCTIONS
def calcNextPowerOf2(length):
    # decrement by one in case of already power of 2
    length -= 1

    # right shift all bits to force number to roll over
    length |= length >> 1
    length |= length >> 2
    length |= length >> 4
    length |= length >> 8
    length |= length >> 16

    # return rolled over number
    return length + 1


def unpackSignal(signalList, blockAlignValue):
    # < <- little endian
    # h <- short
    FMT = "<h"  # format string in order to convert signal to a signed 16bit number
    parsedSignal = list()

    for offset in range(0, len(signalList), blockAlignValue):
        # acquire sample from signal based on block align (should be 2 bytes per block)
        sample = struct.unpack(FMT, signalList[offset:offset+blockAlignValue])
        # append value from tuple into signal
        parsedSignal.append(sample[0])

    return parsedSignal


def unpackWAVE(rawSignal):
    # convert bytes to file object
    wavefile = io.BytesIO(rawSignal)

    # ignore first 4 bytes of header (RIFF header, will awlways be)
    _ = wavefile.read(4)
    lengthOfFile = struct.unpack(FMT_4B_LE, wavefile.read(4))[0]  # get length of file
    # ignore next 4 bytes (denotes if WAVE file, will always be)
    _ = wavefile.read(4)

    # read file until end of file, plus 8 becayse we read the first 8 bytes already
    while wavefile.tell() < lengthOfFile + 8:
        # find parent of the current block
        parent = wavefile.read(4)
        # find length of the remainder of block
        try:
            currentLength = struct.unpack(FMT_4B_LE, wavefile.read(4))[0]
        except struct.error:
            # if struct no longer able to read, most likely out of bounds
            break

        # decide what to do with the current block
        if parent == b'fmt ':
            fmtData = wavefile.read(currentLength)
            # parse fmtData
            fmtTag, numChannels, framerate, avgBytesPerSecond, blockAlignVal, bitsPerSample = struct.unpack(FMT_ALL_ATTRS, fmtData)
            if DEBUG:
                print(f"Format tag: {fmtTag}\nNumber of channels: {numChannels}\nFramerate: {framerate}\nBytes per Second: {avgBytesPerSecond}\nBlock Alignment Size: {blockAlignVal}\nBits per Sample: {bitsPerSample}")
        elif parent == b'data':
            # grab raw signal data
            readSignal = wavefile.read(currentLength)
            parsedSignal = unpackSignal(readSignal, blockAlignVal)
        else:
            # if uneedeed info, skip current block
            wavefile.seek(currentLength, 1)

    return parsedSignal


def calcOmega(N):
    return cmath.exp((2j * cmath.pi) / N)


def fft(signaList):
    # based on cooley-tukey algorithm from wikipedia and youtube
    # INPUT LIST MUST BE POWER OF 2

    # find length of signal
    sizeOfList = len(signaList)
    # if finally done, return the last element
    if sizeOfList == 1:
        return signaList

    # calculate omega of the current block
    omega = calcOmega(sizeOfList)
    
    # get even and odd values of the signal
    signaListEven = signaList[::2]
    signaListOdd = signaList[1::2]

    # recursively calculate fft of smaller and smaller values
    newSigListEven = fft(signaListEven)
    newSigListOdd = fft(signaListOdd)

    # create new list of zeroes based on size
    mainList = [0] * sizeOfList

    # process even and odd lists
    for i in range(sizeOfList // 2):
        mainList[i] = newSigListEven[i] + ((omega ** i) * newSigListOdd[i])
        mainList[i + sizeOfList // 2] = newSigListEven[i] - ((omega ** i) * newSigListOdd[i])
    
    return mainList


# MAIN PROGRAM
def main():
    # define command to run when decoding mp3
    cmd = [exe, 		# ffmpeg executable
           "-i", 		# input
           filename, 	# name of input file (mp3)
           "-ab",		# set bitrate
           "128k",		# bitrate of input file
           "-acodec",   # set audio codec
           "pcm_s16le",  # using PCM signed 16-bit little-endian
           "-map",		# map audio streams
           "0:a",		# from file 0, take only audio
           "-sn",		# ignore any subtitle
           "-vn",		# ignore any video
           "-ac",       # set channels
           "1",	        # mono
           "-y",		# override output
           "-f",		# set output format
           "wav",		# wav format
           "pipe:1"]    # pipe output to stdout and stderr

    # subprocess command, piping outputs to this program
    output = subprocess.run(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, bufsize=10**8)

    if DEBUG:
        print(str(output.stderr))
        print("*** End of subprocess output ***\n")

    completeSignal = unpackWAVE(output.stdout)

    freqList = []
    offset = 0

    while True:
        try:
            # attempt to create new bin
            newBin = completeSignal[offset:(offset + WINDOW_TIMING)]
        except IndexError:
            # break loop at the end of list
            break

        if len(newBin) == 0:
            break

        # check if length of bin is a power of 2
        if not isPowerOfTwo(len(newBin)):
            # if not power of 2, pad end of signal
            paddingAmt = calcNextPowerOf2(len(newBin)) - len(newBin)
            newBin.extend([00] * paddingAmt)

        # take fft of bin
        binList = fft(newBin)
        # only need first half, second half is 1. past nyquist frequency and 2. complex conjugates
        binList = binList[:len(binList) // 2]
        # take absolute values
        binList = list(map(abs, binList))

        magOfFreq = []
        for idx in range(0, len(binList) // 2):
            # real values are at the even parts of the list
            # imaginary values are at the odd parts of the lists
            re = binList[2 * idx]
            im = binList[2 * idx + 1]
            # calculate the magnitude of the value at the given index
            magOfFreq.append(math.sqrt((re * re) + (im * im)))

        maxMagIDX = magOfFreq.index(max(magOfFreq))
        freqOfBin = (maxMagIDX * SAMPLE_RATE) / len(newBin)

        freqList.append(freqOfBin)
        offset += WINDOW_TIMING


    print(freqList)



if __name__ == '__main__':
    main()
