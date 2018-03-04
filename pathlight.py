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
from ws2801 import ws2801

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s (%(threadName)-10s) %(message)s',)

GPIO.setmode(GPIO.BCM)

class Pathlight(object):
	def __init__(self, sensorPins):
		self.sendsorPins = sensorPins
		self.led = ws2801(queue.Queue())

		self.initSensors(sensorPins)
		return

	def initSensors(self, sensorPins):
		self.sensors = []
		for pin in sensorPins	:
			self.sensors.append(MotionSensor(self, pin))
		return


	def shutdown(self):
		self.led.brightness_decrease(.01, 10)
		GPIO.cleanup()
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
			#self.parent.leds[0].queue.put([100, 0, 100])
			self.parent.led.fadeFromEnd(4.5)
		else:
			print('---------- motion exited')
			#self.parent.leds[0].queue.put([100, 100, 100])
			self.parent.led.brightness_decrease(2.0, 100)
		#print(time.time())
		return True


def boundedValue(n, smallest, largest):
	return max(smallest, min(n, largest))



if __name__ == '__main__':

	motionSensors = [26]
	pa = Pathlight(motionSensors)

	try:
		i = 0
		while True:
			i = i+1
			time.sleep(2)
	except KeyboardInterrupt:
		print('Exiting')

	finally:
		pa.shutdown()
