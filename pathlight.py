import sys
import time
import math
import threading
import Queue
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class Pathlight(object):
	def __init__(self, sensorPins, ledPins):
		self.initSensors(sensorPins)
		self.initLeds(ledPins)
		return
	
	def initSensors(self, sensorPins):
		return
	
	def initLeds(self, ledPins):
		return


class MotionSensor(object):
	def __init__(self):
		return

def motionSensed(self):
	print('motion sensed')
	print(time.time())
	print(self)
	return True
	
motionSensors = [[18, GPIO.IN, GPIO.BOTH, motionSensed]]

class Led(threading.Thread):
	def __init__(self, pin, queue):
		Thread.__init__(self)
		self.daemon = False
		self.queue = queue
		self.shutdown = Event()
		
		GPIO.setup(pin, GPIO.OUT)
		GPIO.output(pin, 0)
		self.pwm = GPIO.PWM(pin, 50)
		self.pwm.start(0)
		
		self.start()
		return
	
	def run(self):
		while True:
			#check for shutdown
			if self.shutdown.isSet():
				break
			#check the queue
			try:
				q = self.queue.get(False) #get(False) is nonblocking
			except Queue.Empty:
				q = None
			if q == 'shutdown':
				self.shutdown.set()
			if q:
				logging.debug(str(q)+" on the queue")
				self.target_brightness = q
				self.queue.task_done()

			self.setBrightness(nsteps)
		
		return
	
	def setBrightness(self):
		dif = math.fabs(self.target_brightness-self.brightness)
		if dif > 1:
			self.brightness = self.target_brightness
			self.pwm.changeDutyCycle(self.target_brightness)
	
		return

leds = [6, 13, 19, 26]

for ms in motionSensors	:
	GPIO.setup(ms[0], ms[1])
	if ms[2]:
		GPIO.add_event_detect(ms[0], ms[2], callback=ms[3])

for led in leds:
	GPIO.setup(led, GPIO.OUT)


if __name__ == '__main__':
	#GPIO.setmode(GPIO.BCM)
		
	pa = Pathlight([18], [6, 13, 19, 26])
	
	try:
		i = 0
		while True:
			j = i%len(leds)
			for index,led in enumerate(leds):
				if j==index:
					GPIO.output(led, GPIO.HIGH)
				else:
					GPIO.output(led, GPIO.LOW)

			i = i+1
			time.sleep(1)
	except KeyboardInterrupt:
		print('Exiting')
	finally:
		GPIO.cleanup()
		sys.exit(0)
