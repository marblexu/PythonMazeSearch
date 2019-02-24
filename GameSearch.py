import pygame
from pygame.locals import *
from sys import exit
from random import randint
from GameMap import *
from MazeGenerator import *
from AStarSearch import *

REC_SIZE = 20
REC_WIDTH = 31 # must be odd number
REC_HEIGHT = 31 # must be odd number
SCREEN_WIDTH = REC_WIDTH * REC_SIZE
SCREEN_HEIGHT = REC_HEIGHT * REC_SIZE

class Game():
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
		self.clock = pygame.time.Clock()
		self.map = Map(SCREEN_WIDTH//REC_SIZE, SCREEN_HEIGHT//REC_SIZE)
		self.mode = 0
		
	def play(self):
		self.clock.tick(30)
			
		for y in range(self.map.height):
			for x in range(self.map.width):
				type = self.map.getType(x, y)
				if type == MAP_ENTRY_TYPE.MAP_EMPTY:
					color = (255, 255, 255)
				elif type == MAP_ENTRY_TYPE.MAP_BLOCK:
					color = (0, 0, 0)
				elif type == MAP_ENTRY_TYPE.MAP_TARGET:
					color = (255, 0, 0)
				else:
					color = (0, 255, 0)
				pygame.draw.rect(self.screen, color, pygame.Rect(REC_SIZE*x, REC_SIZE*y, REC_SIZE, REC_SIZE))
		
	def generateMaze(self):
		if self.mode >= 4:
			self.mode = 0
		if self.mode == 0:
			generateMap(self.map)
		elif self.mode == 1:
			self.source = self.map.generatePos((1,1),(1, self.map.height-2))
			self.dest = self.map.generatePos((self.map.width-2, self.map.width-2), (1, self.map.height-2))
			self.map.setMap(self.source[0], self.source[1], MAP_ENTRY_TYPE.MAP_TARGET)
			self.map.setMap(self.dest[0], self.dest[1], MAP_ENTRY_TYPE.MAP_TARGET)
		elif self.mode == 2:
			AStarSearch(self.map, self.source, self.dest)
			self.map.setMap(self.source[0], self.source[1], MAP_ENTRY_TYPE.MAP_TARGET)
			self.map.setMap(self.dest[0], self.dest[1], MAP_ENTRY_TYPE.MAP_TARGET)
		else:
			self.map.resetMap(MAP_ENTRY_TYPE.MAP_EMPTY)
		self.mode += 1
		
game = Game()
while True:
	game.play()
	pygame.display.update()
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()
		if event.type == pygame.KEYDOWN:
			game.generateMaze()
			break
			