import sys
import time
import RPi.GPIO as GPIO
import threading
is_py2 = sys.version[0] == '2'
if is_py2:
	import Queue as queue
else:
	import queue as queue
 
# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

mtime = lambda: int(round(time.time()*1000))

class ws2801(threading.Thread):
	def __init__(self, queue, PIXEL_COUNT = 64):
		self.PIXEL_COUNT = PIXEL_COUNT
		SPI_PORT   = 0
		SPI_DEVICE = 0
		self.pixels = Adafruit_WS2801.WS2801Pixels(self.PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)
		self.pixels.clear()
		self.pixels.show() 
		return
	
	# Define the wheel function to interpolate between different hues.
	def wheel(self, pos):
		if pos < 85:
			return Adafruit_WS2801.RGB_to_color(pos * 3, 255 - pos * 3, 0)
		elif pos < 170:
			pos -= 85
			return Adafruit_WS2801.RGB_to_color(255 - pos * 3, 0, pos * 3)
		else:
			pos -= 170
			return Adafruit_WS2801.RGB_to_color(0, pos * 3, 255 - pos * 3)
 
	# Define rainbow cycle function to do a cycle of all hues.
	def rainbow_cycle_successive(self, wait=0.1):
		for i in range(self.pixels.count()):
			# tricky math! we use each pixel as a fraction of the full 96-color wheel
			# (thats the i / strip.numPixels() part)
			# Then add in j which makes the colors go around per pixel
			# the % 96 is to make the wheel cycle around
			self.pixels.set_pixel(i, self.wheel(((i * 256 // self.pixels.count())) % 256) )
			self.pixels.show()
			if wait > 0:
				time.sleep(wait)
 
	def rainbow_cycle(self, wait=0.005):
		for j in range(256): # one cycle of all 256 colors in the wheel
			for i in range(self.pixels.count()):
				self.pixels.set_pixel(i, self.wheel(((i * 256 // self.pixels.count()) + j) % 256) )
			self.pixels.show()
			if wait > 0:
				time.sleep(wait)
	 
	def rainbow_colors(self, wait=0.05):
		for j in range(256): # one cycle of all 256 colors in the wheel
			for i in range(self.pixels.count()):
				self.pixels.set_pixel(i, self.wheel(((256 // self.pixels.count() + j)) % 256) )
			self.pixels.show()
			if wait > 0:
				time.sleep(wait)
 
	def brightness_decrease(self, transitionTime=1.0, steps=50):
		dt = transitionTime/float(steps)
		#first build an array for the rgb transition values, for each pixel
		il = self.pixels.count()
		rt = [None]*il
		gt = [None]*il
		bt = [None]*il
		for i in range(il):
			r, g, b = self.pixels.get_pixel_rgb(i)
			#print(rt)
			#print(i)
			#print(rt[i])
			rt[i] = [(float(j)/float(steps))*r for j in range(steps+1)]
			gt[i] = [(float(j)/float(steps))*g for j in range(steps+1)]
			bt[i] = [(float(j)/float(steps))*b for j in range(steps+1)]
		#then step through the arrays
		for j in range(steps-1, -1, -1):
			for i in range(il):
				#print("brightness_decrease, rgb = "+str(int(rt[i][j]))+","+str(int(gt[i][j]))+","+str(int(bt[i][j])))					
				self.pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( int(rt[i][j]), int(gt[i][j]), int(bt[i][j]) ))
			self.pixels.show()
			time.sleep(dt)
 
	def appear_from_back(self, color=(255, 0, 255)):
		pos = 0
		for i in range(self.pixels.count()):
			for j in reversed(range(i, self.pixels.count())):
				self.pixels.clear()
				# first set all pixels at the begin
				for k in range(i):
					self.pixels.set_pixel(k, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
				# set then the pixel at position j
				self.pixels.set_pixel(j, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
				self.pixels.show()
				time.sleep(0.01)
	
	def fadeFromEnd(self, transTime = 4.0, rootPoint=0, targetColor=(255,200,100)):
		N = self.pixels.count()
		Nsteps = 150
		dt = transTime / float(Nsteps)
		#print("should take "+str(dt*Nsteps)+" seconds")

		for i in range(Nsteps):
			for x in range(N):
				rgb = [0,0,0]
				for j in range(len(rgb)):
					#m is slope of the color gradient. should be negative
					#strongly affects the rollout appearance
					#smaller abs(m) = faster rollout
					m=-0.75
					b = (i/float(Nsteps)) * (targetColor[j]-m*N)
					rgb[j] = int(m*x+b)
					if rgb[j]<=0:
						rgb[j]=0
					if rgb[j]>=targetColor[j]:
						rgb[j]=targetColor[j]
				#print(rgb)
				self.pixels.set_pixel(x, Adafruit_WS2801.RGB_to_color(rgb[0], rgb[1], rgb[2]))
			self.pixels.show() # contains a sleep(0.002), Nsteps affects total time
			time.sleep(dt)
		
 
if __name__ == "__main__":
	print("Starting lightshow")
	
	try:
		ledstrip = ws2801(queue.Queue())
		
		#ledstrip.rainbow_cycle_successive(0.1)
		#ledstrip.rainbow_cycle(0.01)
		#ledstrip.brightness_decrease()
		#ledstrip.rainbow_colors()
		starttime = mtime()
		ledstrip.fadeFromEnd()
		endtime = mtime()
		lengthtime = (endtime - starttime)/1000.0
		print(str(lengthtime)+" seconds")
		#ledstrip.brightness_decrease()
		
	except KeyboardInterrupt:
		print('Exiting')
	finally:
		ledstrip.brightness_decrease(1.0, 40)
