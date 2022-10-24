import io
import struct
import cmath
import math
import time

"""Class of useful functions to process music files"""
class Signal:
	# CONSTANTS
	# formatting string
	FMT_4B_LE = "<L"
	FMT_ALL_ATTRS = "<HHLLHH"
	
	# timing information
	SAMPLE_RATE = 44_100
	# 1/10 of a second
	WINDOW_TIMING = 4410

	# PUBLIC METHODS
	@staticmethod
	def freq_from_song(bytestream, DEBUG=False):
		"""Generate frequency list from given audio file
			Audio file must be given in WAVE format
			Returns frequency list and time taken if DEBUG is True,
			otherwise returns frequency list and 0"""

		# time length of function if wanted
		if DEBUG:
			timerStart = time.perf_counter()

		completeSignal = Signal._unpackWAVE(bytestream)

		freqList = []
		offset = 0

		while True:
			try:
				# attempt to create new bin
				if offset == 0:
					newBin = completeSignal[offset:(offset + Signal.WINDOW_TIMING + 441)]
				else:
					newBin = completeSignal[offset - 441:(offset + Signal.WINDOW_TIMING + 441)]
			except IndexError:
				# break loop at the end of list
				break

			if len(newBin) == 0:
				break

			# check if length of bin is a power of 2
			if not Signal._isPowerOfTwo(len(newBin)):
				# if not power of 2, pad end of signal
				paddingAmt = Signal._calcNextPowerOf2(len(newBin)) - len(newBin)
				newBin.extend([00] * paddingAmt)

			# take fft of bin
			binList = Signal._fft(newBin)
			# only need first half, second half is complex conjugates
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
			freqOfBin = (maxMagIDX * Signal.SAMPLE_RATE) / len(binList)

			freqList.append(freqOfBin)
			offset += Signal.WINDOW_TIMING
		
		if DEBUG:
			timer = time.perf_counter() - timerStart
			return freqList, timer

		return freqList, 0


	# PRIVATE METHODS
	@staticmethod
	def _fft(signalList):
		# based on cooley-tukey algorithm from wikipedia and youtube
		# INPUT LIST MUST BE POWER OF 2

		# find length of signal
		sizeOfList = len(signalList)
		# if finally done, return the last element
		if sizeOfList == 1:
			return signalList

		# calculate omega of the current block
		omega = Signal._calcOmega(sizeOfList)
	
		# get even and odd values of the signal
		signalListEven = signalList[::2]
		signalListOdd = signalList[1::2]

		# recursively calculate fft of smaller and smaller values
		newSigListEven = Signal._fft(signalListEven)
		newSigListOdd = Signal._fft(signalListOdd)

		# create new list of zeroes based on size
		mainList = [0] * sizeOfList

		# process even and odd lists
		for i in range(sizeOfList // 2):
			mainList[i] = newSigListEven[i] + ((omega ** i) * newSigListOdd[i])
			mainList[i + sizeOfList // 2] = newSigListEven[i] - ((omega ** i) * newSigListOdd[i])

		return mainList


	@staticmethod
	def _calcNextPowerOf2(length):
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


	@staticmethod
	def _unpackSignal(signalList, blockAlignValue):
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


	@staticmethod
	def _unpackWAVE(rawSignal):
		# convert bytes to file object
		wavefile = io.BytesIO(rawSignal)

		# ignore first 4 bytes of header (RIFF header, will awlways be)
		_ = wavefile.read(4)
		lengthOfFile = struct.unpack(Signal.FMT_4B_LE, wavefile.read(4))[0]  # get length of file
		# ignore next 4 bytes (denotes if WAVE file, will always be)
		_ = wavefile.read(4)

		# read file until end of file, plus 8 because we read the first 8 bytes already
		while wavefile.tell() < lengthOfFile + 8:
			# find parent of the current block
			parent = wavefile.read(4)
			# find length of the remainder of block
			try:
				currentLength = struct.unpack(Signal.FMT_4B_LE, wavefile.read(4))[0]
			except struct.error:
				# if struct no longer able to read, most likely out of bounds
				break

			# decide what to do with the current block
			if parent == b'fmt ':
				fmtData = wavefile.read(currentLength)
				# parse fmtData
				fmtTag, numChannels, framerate, avgBytesPerSecond, blockAlignVal, bitsPerSample = struct.unpack(Signal.FMT_ALL_ATTRS, fmtData)
			elif parent == b'data':
				# grab raw signal data
				readSignal = wavefile.read(currentLength)
				parsedSignal = Signal._unpackSignal(readSignal, blockAlignVal)
			else:
				# if uneedeed info, skip current block
				wavefile.seek(currentLength, 1)

		return parsedSignal


	@staticmethod
	def _calcOmega(N):
		return cmath.exp((2j * cmath.pi) / N)


	@staticmethod
	def _isPowerOfTwo(n): 
		return (n != 0) and (n & (n - 1) == 0)

	
