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
BUTTON_HEIGHT = 2
SCREEN_WIDTH = REC_WIDTH * REC_SIZE
SCREEN_HEIGHT = (REC_HEIGHT + BUTTON_HEIGHT) * REC_SIZE

class Button():
	def __init__(self, screen, type, x, y):
		self.screen = screen
		self.width = REC_SIZE * 7
		self.height = REC_SIZE * 2
		self.button_color = (128,128,128)
		self.text_color = [(0,255,0), (255,0,0)]
		self.font = pygame.font.SysFont(None, REC_SIZE*3//2)
		
		self.rect = pygame.Rect(0, 0, self.width, self.height)
		self.rect.topleft = (x, y)
		self.type = type
		self.init_msg()
		
	def init_msg(self):
		self.msg_image = self.font.render(generator_types[self.type], True, self.text_color[0], self.button_color)
		self.msg_image_rect = self.msg_image.get_rect()
		self.msg_image_rect.center = self.rect.center
		
	def draw(self):
		self.screen.fill(self.button_color, self.rect)
		self.screen.blit(self.msg_image, self.msg_image_rect)
	
	def click(self, game):
		game.maze_type = self.type
		self.msg_image = self.font.render(generator_types[self.type], True, self.text_color[1], self.button_color)
	
	def unclick(self):
		self.msg_image = self.font.render(generator_types[self.type], True, self.text_color[0], self.button_color)

class Game():
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
		self.clock = pygame.time.Clock()
		self.map = Map(REC_WIDTH, REC_HEIGHT)
		self.mode = 0
		self.maze_type = MAZE_GENERATOR_TYPE.RANDOM_PRIM
		self.buttons = []
		self.buttons.append(Button(self.screen, MAZE_GENERATOR_TYPE.RECURSIVE_BACKTRACKER, 0, 0))
		self.buttons.append(Button(self.screen, MAZE_GENERATOR_TYPE.RANDOM_PRIM, REC_SIZE * 8, 0))
		self.buttons.append(Button(self.screen, MAZE_GENERATOR_TYPE.RECURSIVE_DIVISION, REC_SIZE * 16, 0))
		self.buttons.append(Button(self.screen, MAZE_GENERATOR_TYPE.UNION_FIND_SET, REC_SIZE * 24, 0))
		self.buttons[0].click(self)

	def play(self):
		self.clock.tick(30)
		
		pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(0, 0, SCREEN_WIDTH, BUTTON_HEIGHT*REC_SIZE))
		for button in self.buttons:
			button.draw()

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
				pygame.draw.rect(self.screen, color, pygame.Rect(REC_SIZE*x, REC_SIZE*(y+BUTTON_HEIGHT), REC_SIZE, REC_SIZE))
		
	def generateMaze(self):
		if self.mode >= 4:
			self.mode = 0
		if self.mode == 0:
			generateMap(self.map, self.maze_type)
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

def check_buttons(game, mouse_x, mouse_y):
	for button in game.buttons:
		if button.rect.collidepoint(mouse_x, mouse_y):
			button.click(game)
			for tmp in game.buttons:
				if tmp != button:
					tmp.unclick()
			break

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
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			check_buttons(game, mouse_x, mouse_y)
			