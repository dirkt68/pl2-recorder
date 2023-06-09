import time
import RPi.GPIO as GPIO
import rtmidi

midiin = rtmidi.RtMidiIn()

# note setup :: note/octave = (servo0, sol1, sol2, sol3, sol4, sol5, servo6, servo7)
# solenoids are SOL_OPEN/SOL_CLOSED, servos are SERVO_CLOSED, SERVO_HALF, SERVO_OPEN
class Notes():
    # pins
    SERVO_0 = 36
    SOL_1 = 3
    SOL_2 = 5
    SOL_3 = 7
    SOL_4 = 11
    SOL_5 = 13
    SOL_6 = 15
    FAN = 16
    SERVO_6 = 38
    SERVO_7 = 40

    # servos
    # ! need to find which value corresponds to fully open/half/closed
    SERVO_0_OPEN = 40
    SERVO_0_HALF = 50
    SERVO_0_CLOSED = 60

    SERVO_6_OPEN = 60
    SERVO_6_HALF = 50 
    SERVO_6_CLOSED = 40

    SERVO_7_OPEN = 40
    SERVO_7_HALF = 50 
    SERVO_7_CLOSED = 60

    # solenoid
    SOL_OPEN = False
    SOL_CLOSED = True

    FAN_HIGH = 65
    FAN_MID = 55
    FAN_LOW = 45

    # notes to physical positions
    PHYS_NOTE_DICT = {#         FAN         0           1           2           3           4           5           6               7
        "C5":   (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_CLOSED),
        "C#5":  (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_HALF),
        "D5":   (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_OPEN),
        "D#5":  (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_HALF, SERVO_7_OPEN),
        "E5":   (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_OPEN, SERVO_7_OPEN),
        "F5":   (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SERVO_6_CLOSED, SERVO_7_CLOSED),
        "F#5":  (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_OPEN),
        "G5":   (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
        "G#5":  (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SERVO_6_HALF, SERVO_7_OPEN),
        "A5":   (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
        "A#5":  (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
        "B5":   (FAN_LOW, SERVO_0_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
        "C6":   (FAN_MID, SERVO_0_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
        "C#6":  (FAN_MID, SERVO_0_OPEN, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
        "D6":   (FAN_MID, SERVO_0_OPEN, SOL_OPEN, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
        "D#6":  (FAN_MID, SERVO_0_OPEN, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_CLOSED),
        "E6":   (FAN_MID, SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_OPEN, SERVO_7_OPEN),
        "F6":   (FAN_MID, SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SERVO_6_CLOSED, SERVO_7_OPEN),
        "F#6":  (FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SERVO_6_OPEN, SERVO_7_OPEN),
        "G6":   (FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
        "G#6":  (FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
        "A6":   (FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
        "A#6":  (FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_OPEN),
        "B6":   (FAN_HIGH,SERVO_0_HALF, SOL_OPEN, SOL_OPEN, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SERVO_6_OPEN, SERVO_7_OPEN),
        "C7":   (FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SERVO_6_OPEN, SERVO_7_OPEN),
        "C#7":  (FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SERVO_6_OPEN, SERVO_7_CLOSED),
        "D7":   (FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SERVO_6_CLOSED, SERVO_7_OPEN),
    }

    def __init__(self):
        self.GPIOInit()


    def playPianoNote(self, midi):
        note = midi.getMidiNoteName(midi.getNoteNumber())
        if midi.isNoteOn():
          print('ON: ',note)
          self.fan.start(Notes.PHYS_NOTE_DICT[note][0])
          self.servo0.start(Notes.PHYS_NOTE_DICT[note][1])
          GPIO.output(Notes.SOL_1, Notes.PHYS_NOTE_DICT[note][2])
          GPIO.output(Notes.SOL_2, Notes.PHYS_NOTE_DICT[note][3])
          GPIO.output(Notes.SOL_3, Notes.PHYS_NOTE_DICT[note][4])
          GPIO.output(Notes.SOL_4, Notes.PHYS_NOTE_DICT[note][5])
          GPIO.output(Notes.SOL_5, Notes.PHYS_NOTE_DICT[note][6])
          self.servo6.start(Notes.PHYS_NOTE_DICT[note][7])
          self.servo7.start(Notes.PHYS_NOTE_DICT[note][8])

        elif midi.isNoteOff():
          print('OFF:', note)
        
        GPIO.output(Notes.SOL_6, Notes.SOL_CLOSED)

    def GPIOInit(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        GPIO.setup(Notes.SERVO_0, GPIO.OUT)
        GPIO.setup(Notes.SOL_1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(Notes.SOL_2, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(Notes.SOL_3, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(Notes.SOL_4, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(Notes.SOL_5, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(Notes.SOL_6, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(Notes.SERVO_6, GPIO.OUT)
        GPIO.setup(Notes.SERVO_7, GPIO.OUT)
        GPIO.setup(Notes.FAN, GPIO.OUT)

        self.fan = GPIO.PWM(Notes.FAN, 100)
        self.servo0 = GPIO.PWM(Notes.SERVO_0, 200)
        self.servo6 = GPIO.PWM(Notes.SERVO_6, 200)
        self.servo7 = GPIO.PWM(Notes.SERVO_7, 200)

        self.fan.stop()
        self.servo0.stop()
        self.servo6.stop()
        self.servo7.stop()


    def GPIOClean(self):
        self.fan.stop()
        self.servo0.stop()
        GPIO.output(Notes.SOL_1, Notes.SOL_OPEN)
        GPIO.output(Notes.SOL_2, Notes.SOL_OPEN)
        GPIO.output(Notes.SOL_3, Notes.SOL_OPEN)
        GPIO.output(Notes.SOL_4, Notes.SOL_OPEN)
        GPIO.output(Notes.SOL_5, Notes.SOL_OPEN)
        GPIO.output(Notes.SOL_6, Notes.SOL_OPEN)
        self.servo6.stop()
        self.servo7.stop()

   
    def spoolFan(self):
        spooltime = 2 
        timer = time.time()
        while time.time() - timer <= spooltime:
            self.fan.start(Notes.FAN_HIGH)


def piano(notesObject):
    ports = range(midiin.getPortCount())
    if ports:
        for i in ports:
            print(midiin.getPortName(i))
        print("Opening port 1!")
        midiin.openPort(1)


        while True:
            m = midiin.getMessage(250) # some timeout in ms
            if m:
                notesObject.playPianoNote(m)
    else:
        print('NO MIDI INPUT PORTS!')
