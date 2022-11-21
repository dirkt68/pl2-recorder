# PYTHON LIBRARIES
import subprocess
import time

# USER LIBRARIES
from signalProcessing import Signal
from constants import freq_to_notes, usable_notes

# CONSTANTS
# filenames and executable
filename = "songs\Hot Cross Buns Test.mp3"
exe = "ffmpeg.exe"

# bandpass filtering constants
LOW_FILTER = 65.41 # start at C2
HIGH_FILTER = 9000.00 # end at range of useful instruments

# debug print flag
DEBUG = True


def findUsableNote(note):
    if note in usable_notes:
        return note
    elif note[-1] < usable_notes[0][-1]:
        return note[:-1] + usable_notes[0][-1]
    elif note[-1] > usable_notes[-1][-1]:
        return note[:-1] + usable_notes[-1][-1]


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

    # get frequency list from song
    freqList, timeSpent = Signal.freq_from_song(output.stdout, DEBUG)
    # if DEBUG: 
    #     print(freqList)
    #     print(f"Time spent: {timeSpent} seconds\n")

    # start loop
    while True:
        tempFreqList = []
        # count how many times each frequency is the same
        try:
            # pop item off the list
            tempFreqList.append(freqList.pop(0))
        except IndexError:
            break

        while True:
            try:
                if freqList[0] != tempFreqList[0] and freqList[1] != tempFreqList[0]:
                    break
                elif freqList[0] != tempFreqList[0] and freqList[1] == tempFreqList[0]:
                    tempFreqList.append(tempFreqList[0])
                tempFreqList.append(freqList.pop(0))
            except IndexError:
                break

        # divide by time window size (1/10 of a second)
        timeToPlay = len(tempFreqList) / 10

        # get frequency
        unmodFreq = tempFreqList[0]

        # throw away unnecessary frequencies
        if (unmodFreq < LOW_FILTER or unmodFreq > HIGH_FILTER) and unmodFreq != 0:
            continue

        # find note from frequency
        foundNote = None
        for key in freq_to_notes:
            # find +-5 percent of range
            keyUpper = key * 1.05
            keyLower = key * 0.95

            # if the frequency within the range, use that number
            if unmodFreq >= keyLower and unmodFreq <= keyUpper:
                foundNote = freq_to_notes[key]

        trueNote = findUsableNote(foundNote)
        print(trueNote)

        # set a timer to play note for that long
        timer = time.time()
        while time.time() - timer <= timeToPlay:
            # send GPIO signal corresponding to note for that length of time
                # ! need to know which GPIO pins are connected to which solenoid 
            continue



if __name__ == '__main__':
    main()
