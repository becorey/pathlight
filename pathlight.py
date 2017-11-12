import sys
import time
import math
import threading
is_py2 = sys.version[0] == '2'
if is_py2:
	import Queue as queue
else:
	import queue as queue
import RPi.GPIO as GPIO
import logging

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s (%(threadName)-10s) %(message)s',)

GPIO.setmode(GPIO.BCM)

class Pathlight(object):
	def __init__(self, sensorPins, ledPins):
		self.sendsorPins = sensorPins
		self.ledPins = ledPins
		
		self.initSensors(sensorPins)
		self.initLeds(ledPins)
		return
	
	def initSensors(self, sensorPins):
		self.sensors = []
		for pin in sensorPins	:
			self.sensors.append(MotionSensor(self, pin))
		return
	
	def initLeds(self, ledPins):
		self.leds = []
		for rgb in ledPins:
			self.leds.append(Led(self, rgb, 30, queue.Queue()))
		return
		
	def shutdown(self):
		GPIO.cleanup()
		for le in self.leds:
			le.shutdown.set()
		return


class MotionSensor(object):
	def __init__(self, parent, pin):
		self.parent = parent
		self.pin = pin
		GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.motionSensed)
		return
		
	def motionSensed(self, pin):
		val = GPIO.input(pin)
		if val:
			print('++++++++++ motion entered ++++++++++')
			self.parent.leds[0].queue.put([100, 0, 100])
		else:
			print('---------- motion exited')
			self.parent.leds[0].queue.put([100, 100, 100])
		print(time.time())
		return True


class Led(threading.Thread):
	def __init__(self, parent, pins, updateFrequency, queue):
		self.parent = parent
		self.pins = pins
		self.pwm = [None] * len(self.pins)
		self.updateFrequency = updateFrequency
		self.brightness = [0] * len(self.pins)
		self.targetBrightness = 0
		self.transition = []
		
		threading.Thread.__init__(self)
		self.daemon = False
		self.queue = queue
		self.shutdown = threading.Event()
		
		#each R,G,B pin
		for i,pin in enumerate(self.pins):
			GPIO.setup(pin, GPIO.OUT)
			GPIO.output(pin, 1)
			self.pwm[i] = GPIO.PWM(pin, 60)
			self.pwm[i].start(100.0)
		
		self.start()
		return
	
	def run(self):
		while True:
			#check for shutdown
			if self.shutdown.isSet():
				for pin in self.pins:
					pin.pwm.stop()
				GPIO.cleanup()
				break
			#check the queue
			try:
				q = self.queue.get(False) #get(False) is nonblocking
			except queue.Empty:
				q = None
			if q == 'shutdown':
				self.shutdown.set()
			if q != None:
				#logging.debug(str(q)+" on the queue")
				if q != self.brightness:
					r = [self.brightness[0], q[0]]
					g = [self.brightness[1], q[1]]
					b = [self.brightness[2], q[2]]
					trans = self.sinTransition([r, g, b], 40)
					self.transition.extend(trans)
				self.queue.task_done()
			self.setRGB()
			time.sleep(1.0/self.updateFrequency)
		return
	
	def sinTransition(self, vals, nSteps):
		# first, build lists for r,g, and b
		# lists[0] = [r1, r2, r3, ...]
		# lists[1] = [b1, b2, b3, ...]
		lists = [None] * len(vals)
		for i,val in enumerate(vals):
			startVal = val[0]
			endVal = val[1]
			dif = (endVal-startVal)
			lists[i] = [startVal + dif*(0.5-0.5*math.cos(2.0*math.pi*(1.0/nSteps)/2.0*x)) for x in range(nSteps)]
		#then compose into array of RGB triplets
		# [ [r1,b1,g1], [r2,b2,g2], ... ]
		transition = [None] * nSteps
		for i in range(nSteps):
			transition[i] = [lists[0][i], lists[1][i], lists[2][i]]
		return transition

	
	def setRGB(self):
		#logging.debug(str(self.pin)+" "+str(self.transition))
		if len(self.transition)>0:
			#set brightness to first value on the transition array
			#print('transition = '+str(self.transition))
			for i,rgb in enumerate(self.transition[0]):
				#print('i = '+str(i))
				#print('brightness='+str(self.brightness))
				#print('rgb = '+str(rgb))
				self.brightness[i] = boundedValue(rgb, 0.0, 100.0)
				self.pwm[i].ChangeDutyCycle(self.brightness[i])
			#remove that first element from transition
			self.transition.pop(0)
		

def boundedValue(n, smallest, largest):
	return max(smallest, min(n, largest))



if __name__ == '__main__':
		
	motionSensors = [18]
	leds = [[6, 13, 19]]
	pa = Pathlight(motionSensors, leds)
	
	try:
		i = 0
		while True:
			#led = pa.leds[0]
			#j = i%3
			#if j == 0:
			#	led.queue.put([0.0, 100.0, 100.0])
			#elif j == 1:
			#	led.queue.put([100.0, 0.0, 100.0])
			#elif j == 2:
			#	led.queue.put([100.0, 100.0, 0.0])

			i = i+1
			time.sleep(2)
	except KeyboardInterrupt:
		print('Exiting')
		
	finally:
		pa.shutdown()
