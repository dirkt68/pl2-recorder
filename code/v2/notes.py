import time
import RPi.GPIO as GPIO
from rpi_hardware_pwm import HardwarePWM
import rtmidi

# note setup :: note/octave = (servo0, sol1, sol2, sol3, sol4, sol5, servo6, servo7)
# solenoids are SOL_OPEN/SOL_CLOSED, servos are SERVO_CLOSED, SERVO_HALF, SERVO_OPEN
class Notes():
	# pins
	SERVO_0 = 36
	SOL_1 = 3
	SOL_2 = 5
	SOL_3 = 8
	SOL_4 = 11
	SOL_5 = 13
	SOL_6 = 15
	# FAN = 16
	# fan is controlled by channel 0 for HardwarePWM
	SERVO_6 = 38
	SERVO_7 = 40

	# servos
	SERVO_0_OPEN = 0.8
	SERVO_0_HALF = 0.75
	SERVO_0_CLOSED = 0.7

	SERVO_6_OPEN = 0.75
	SERVO_6_HALF = 1
	SERVO_6_CLOSED = 1.1

	SERVO_7_OPEN = 1.1
	SERVO_7_HALF = 1
	SERVO_7_CLOSED = 0.9

	# solenoid
	SOL_OPEN = False
	SOL_CLOSED = True

	FAN_HIGH = 70
	FAN_MID = 60
	FAN_LOW = 50

	# notes to physical positions
	PHYS_NOTE_DICT = {#			FAN			0			1			2			3			4			5			6				7
		"C5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_CLOSED),
		"C#5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_HALF),
		"D5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_OPEN),
		"D#5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_HALF, SERVO_7_OPEN),
		"E5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_OPEN, SERVO_7_OPEN),
		"F5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SERVO_6_CLOSED, SERVO_7_CLOSED),
		"F#5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_OPEN),
		"G5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
		"G#5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SERVO_6_HALF, SERVO_7_OPEN),
		"A5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
		"A#5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
		"B5":	(FAN_HIGH, SERVO_0_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
		"C6":	(FAN_HIGH, SERVO_0_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
		"C#6":	(FAN_HIGH, SERVO_0_OPEN, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
		"D6":	(FAN_HIGH, SERVO_0_OPEN, SOL_OPEN, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
		"D#6":	(FAN_HIGH, SERVO_0_OPEN, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_CLOSED),
		"E6":	(FAN_HIGH, SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SERVO_6_OPEN, SERVO_7_OPEN),
		"F6":	(FAN_HIGH, SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SERVO_6_CLOSED, SERVO_7_OPEN),
		"F#6":	(FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SERVO_6_OPEN, SERVO_7_OPEN),
		"G6":	(FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
		"G#6":	(FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
		"A6":	(FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_OPEN, SERVO_6_OPEN, SERVO_7_OPEN),
		"A#6":	(FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SERVO_6_CLOSED, SERVO_7_OPEN),
		"B6":	(FAN_HIGH,SERVO_0_HALF, SOL_OPEN, SOL_OPEN, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SERVO_6_OPEN, SERVO_7_OPEN),
		"C7":	(FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_OPEN, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SERVO_6_OPEN, SERVO_7_OPEN),
		"C#7":	(FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SERVO_6_OPEN, SERVO_7_CLOSED),
		"D7":	(FAN_HIGH,SERVO_0_HALF, SOL_CLOSED, SOL_OPEN, SOL_CLOSED, SOL_CLOSED, SOL_OPEN, SERVO_6_CLOSED, SERVO_7_OPEN),
	}


	def __init__(self):
		self.GPIOInit()
		self.GPIOClean()


	def playNote(self, note, length):
		GPIO.output(Notes.SOL_6, Notes.SOL_CLOSED)
		timer = time.time()
		while time.time() - timer <= length:
			if note is None or note == "-":
				GPIO.output(Notes.SOL_6, Notes.SOL_OPEN)
				continue

			self.fan.change_duty_cycle(Notes.PHYS_NOTE_DICT[note][0])
			self.servo0.start(Notes.PHYS_NOTE_DICT[note][1])
			GPIO.output(Notes.SOL_1, Notes.PHYS_NOTE_DICT[note][2])
			GPIO.output(Notes.SOL_2, Notes.PHYS_NOTE_DICT[note][3])
			GPIO.output(Notes.SOL_3, Notes.PHYS_NOTE_DICT[note][4])
			GPIO.output(Notes.SOL_4, Notes.PHYS_NOTE_DICT[note][5])
			GPIO.output(Notes.SOL_5, Notes.PHYS_NOTE_DICT[note][6])
			self.servo6.start(Notes.PHYS_NOTE_DICT[note][7])
			self.servo7.start(Notes.PHYS_NOTE_DICT[note][8])


	def GPIOInit(self):
		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)

		GPIO.setup(Notes.SOL_1, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(Notes.SOL_2, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(Notes.SOL_3, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(Notes.SOL_4, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(Notes.SOL_5, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(Notes.SOL_6, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(Notes.SERVO_0, GPIO.OUT)
		GPIO.setup(Notes.SERVO_6, GPIO.OUT)
		GPIO.setup(Notes.SERVO_7, GPIO.OUT)

		self.fan = HardwarePWM(0, 500)
		self.servo0 = GPIO.PWM(Notes.SERVO_0,5)
		self.servo6 = GPIO.PWM(Notes.SERVO_6,5)
		self.servo7 = GPIO.PWM(Notes.SERVO_7,5)



	def GPIOClean(self):
		self.fan.stop()
		self.servo0.start(0)
		GPIO.output(Notes.SOL_1, Notes.SOL_OPEN)
		GPIO.output(Notes.SOL_2, Notes.SOL_OPEN)
		GPIO.output(Notes.SOL_3, Notes.SOL_OPEN)
		GPIO.output(Notes.SOL_4, Notes.SOL_OPEN)
		GPIO.output(Notes.SOL_5, Notes.SOL_OPEN)
		GPIO.output(Notes.SOL_6, Notes.SOL_OPEN)
		self.servo6.start(0)
		self.servo7.start(0)
		print("cleaned")

	
	def spoolFan(self):
		self.fan.start(Notes.FAN_HIGH)
		spooltime = 3.5 
		timer = time.time()
		while time.time() - timer <= spooltime:
			continue


	def playPianoNote(self, midi):
		note = midi.getMidiNoteName(midi.getNoteNumber())
		if midi.isNoteOn() and int(note[-1]) >= 5 and int(note[-1]) < 8:
			# print('ON: ',note)
			self.fan.change_duty_cycle(Notes.PHYS_NOTE_DICT[note][0])
			self.servo0.start(Notes.PHYS_NOTE_DICT[note][1])
			GPIO.output(Notes.SOL_1, Notes.PHYS_NOTE_DICT[note][2])
			GPIO.output(Notes.SOL_2, Notes.PHYS_NOTE_DICT[note][3])
			GPIO.output(Notes.SOL_3, Notes.PHYS_NOTE_DICT[note][4])
			GPIO.output(Notes.SOL_4, Notes.PHYS_NOTE_DICT[note][5])
			GPIO.output(Notes.SOL_5, Notes.PHYS_NOTE_DICT[note][6])
			self.servo6.start(Notes.PHYS_NOTE_DICT[note][7])
			self.servo7.start(Notes.PHYS_NOTE_DICT[note][8])

		else:
			# print('OFF:', note)
			GPIO.output(Notes.SOL_6, Notes.SOL_CLOSED)
        
