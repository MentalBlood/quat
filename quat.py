import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QTimer
from math import cos, sin, pi, sqrt
from random import randint, shuffle

resx, resy = int(input('Horizontal resolution: ')), int(input('Vertical resolution: '))
presets = [	[[70, 30, 4, 4, 6], 'Harmonic'],
			[[80, 27, 3, 7, 9], 'Fast'],
			[[100, 20, 3, 8, 10], 'Very fast'],
			[[60, 50, 3, 3, 7], 'Many'],
			[[50, 100, 3, 4, 5], 'Plenty'],
			[[40, 150, 3, 4, 6], 'Nu ochen mnogo'],
			[[70, 20, 3, 11, 11], 'SPEED']]
print()
if int(input('0 - Presets\n1 - Custom\n')):
	a = int(input('\nSquare side length: '))
	N = int(input('Number of squares: '))
	connectivity = int(input('Max number of near squares for every square (on start): '))
	vmin, vmax = float(input('Min speed (pi/2 per second): ')), float(input('Max speed: '))
else:
	print('\n---Presets---')
	for i in range(len(presets)): print(i, '-', presets[i][1])
	a, N, connectivity, vmin, vmax = presets[int(input())][0]

br = 	[
			[[1, 0], [1, 1], [0, 1]],
			[[-1, 0], [-1, 1], [0, 1]],
			[[-1, 0], [-1, -1], [0, -1]],
			[[0, -1], [1, -1], [1, 0]]
		]
gx_change90, gy_change90 	= [[-1, 0, 1, 0], [0, -1, 0, 1]], [[0, -1, 0, 1], [1, 0, -1, 0]]
gx_change180, gy_change180 	= [-1, -1, 1, 1], [1, -1, -1, 1]
bindings = [[0, 1], [1, 2], [2, 3], [0, 3]]
dots0 = [[-a/2, a/2], [-a/2, -a/2], [a/2, -a/2], [a/2, a/2]]
a90 = pi/2

def sign(a):
	if a < 0: return -1
	return 1

def coherent(m):
	N = len(m)
	visited, visiting = [m[0]], [m[0]]
	while len(visited) != N:
		v = visiting
		visiting = []
		for c in v:
			for ngc in m:
				if ((abs(c[0]-ngc[0]) == 1 and c[1] == ngc[1]) or (abs(c[1]-ngc[1]) == 1 and c[0] == ngc[0])) and not (ngc in visited):
					visiting.append(ngc)
					visited.append(ngc)
		if not visiting: return len(visited) == N
	return True

def near_squares(s, squares):
	ns = []
	for square in squares:
		if (abs(square[0]-s[0]) == 1 and square[1] == s[1]) or (abs(square[1]-s[1]) == 1 and square[0] == s[0]): ns.append(square)
	return ns

class Square():
	__slots__ = ['dots', 'x', 'y', 'gx', 'gy', 'plan_rotate_data', 'rotating']
	def __init__(self, x, y):
		self.dots = [[x-a/2, y+a/2], [x-a/2, y-a/2], [x+a/2, y-a/2], [x+a/2, y+a/2]]
		self.x, self.y, self.gx, self.gy = x, y, x//a, y//a
		self.plan_rotate_data = [0, 0, 0, 1]
		self.rotating = False
	def elemental_rotate(self, rdot, angle):
		c, s = cos(angle), sin(angle)
		for dot in self.dots:
			dot[0], dot[1] = (dot[0] - rdot[0] - self.x)*c - (dot[1] - rdot[1] - self.y)*s + rdot[0] + self.x, (dot[0] - rdot[0] - self.x)*s + (dot[1] - rdot[1] - self.y)*c + rdot[1] + self.y
	def draw(self, painter):
		for binding in bindings: painter.drawLine(self.dots[binding[0]][0], self.dots[binding[0]][1], self.dots[binding[1]][0], self.dots[binding[1]][1])
	def check90_180(self, rdot0_index, squares, cad = 1):
		magic = cad*2 - 1
		for square in squares:
			if [magic*(square.gx - self.gx), magic*(square.gy - self.gy)] in br[rdot0_index]: return
		swto = [[square.gx, square.gy] for square in squares]
		swto.remove([self.gx, self.gy])
		gx90 = self.gx + gx_change90[cad][rdot0_index]
		gy90 = self.gy + gy_change90[cad][rdot0_index]
		gx180 = self.gx + gx_change180[rdot0_index]
		gy180 = self.gy + gy_change180[rdot0_index]
		p90 = coherent(swto + [[gx90, gy90]])
		if not (0 < gx90 < resx // a and 0 < gy90 < resy // a): return
		p180 = True
		for square in squares:
			if square != self and ([magic*(square.gx - gx90), magic*(square.gy - gy90)] in br[(rdot0_index + magic) % 4]):
				p180 = False
				break
		if p180: p180 = coherent(swto + [[gx180, gy180]]) and 0 < gx180 < resx // a and 0 < gy180 < resy // a
		if randint(0, 1) and p90: return a90 * magic
		elif p180: return pi * magic
	def plan_possible_rotate(self, squares):
		for square in squares:
			if ((square.gx - self.gx)**2 + (square.gy - self.gy)**2 < 12) and square.rotating: return
		angle = []
		for rdot in self.dots:
			ok = False
			for square in squares:
				if rdot in square.dots and square != self:
					ok = True
					break
			if not ok: continue
			rdot0_index = dots0.index([rdot[0] - self.x, rdot[1] - self.y])
			ang = [self.check90_180(rdot0_index, squares), self.check90_180(rdot0_index, squares, 0)]
			if ang[0]:
				if ang[1]: angle.append([ang[randint(0,1)], rdot, rdot0_index])
				else: angle.append([ang[0], rdot, rdot0_index])
			else:
				if ang[1]: angle.append([ang[1], rdot, rdot0_index])
		if angle:
			angle = angle[randint(0, len(angle) - 1)]
			cad = (sign(angle[0]) + 1)//2
			if abs(angle[0]) == a90:
				self.gx += gx_change90[cad][angle[2]]
				self.gy += gy_change90[cad][angle[2]]
			else:
				self.gx += gx_change180[angle[2]]
				self.gy += gy_change180[angle[2]]
			self.plan_rotate_data = [dots0[self.dots.index(angle[1])], abs(angle[0]), int(abs(angle[0])/pi*180/randint(vmin, vmax)), sign(angle[0])]
			self.rotating = True
	def rotate(self):
		if self.plan_rotate_data[2] > 0:
			self.elemental_rotate(self.plan_rotate_data[0], self.plan_rotate_data[3]*self.plan_rotate_data[1]/self.plan_rotate_data[2])
			self.plan_rotate_data[1] -= self.plan_rotate_data[1]/self.plan_rotate_data[2]
			self.plan_rotate_data[2] -= 1
			if self.plan_rotate_data[2] <= 0:
				for dot in self.dots: dot[0], dot[1] = round(dot[0]), round(dot[1])
				self.x, self.y = self.gx*a, self.gy*a
				self.dots = [[self.x-a/2, self.y+a/2], [self.x-a/2, self.y-a/2], [self.x+a/2, self.y-a/2], [self.x+a/2, self.y+a/2]]
				self.rotating = False
				return 1
		else: return 1
		return 0
	def ROTATE(self, squares):
		if self.rotating: self.rotate()
		else: self.plan_possible_rotate(squares)

def coherent_squares(N):
	s = [[resx//(2*a), resy//(2*a)]]
	for i in range(N):
		ok = False
		try_n = 0
		while not ok:
			try_n += 1
			if try_n == 15000 // a: return False
			ok = False
			ngc = [randint(3, resx//a-3), randint(3, resy//a-3)]
			while ngc in s: ngc = [randint(3, resx//a-3), randint(3, resy//a-3)]
			ns = near_squares(ngc, s)
			ok1 = True
			for near_square in ns:
				if len(near_squares(near_square, s + [ngc])) > connectivity:
					ok1 = False
					break
			if not ok1: continue
			for c in s:
				if (abs(c[0]-ngc[0]) == 1 and c[1] == ngc[1]) or (abs(c[1]-ngc[1]) == 1 and c[0] == ngc[0]):
					s.append(ngc)
					ok = True
					break
	return [Square(gc[0]*a, gc[1]*a) for gc in s]

class drawer(QWidget):
	def __init__(self):
		super().__init__()
		self.initiation()
		self.timer = QTimer()
		self.timer.timeout.connect(self.process_timeout)
		self.timer.start(10)
		self.update()
	def process_timeout(self):
		for square in self.squares: square.ROTATE(self.squares)
		self.update()
	def initiation(self):
		self.setGeometry(0, 0, resx, resy)
		self.setWindowTitle('Quat')
		p = self.palette()
		p.setColor(self.backgroundRole(), Qt.black)
		self.setPalette(p)
		self.squares = False
		while not self.squares: self.squares = coherent_squares(N)
		self.show()
	def paintEvent(self, e):
		painter = QPainter()
		painter.begin(self)
		painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
		painter.drawLine(0, 0, resx, 0)
		painter.drawLine(0, 0, 0, resy)
		painter.drawLine(resx, 0, resx - 1, resy - 1)
		painter.drawLine(0, resy, resx - 1, resy - 1)
		for square in self.squares: square.draw(painter)
		painter.end()
		self.show()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	w = drawer()
	sys.exit(app.exec_())

