from random import randint, choice
from GameMap import *
from AStarSearch import *

def recursiveDivision(map, x, y, width, height, wall_value):
	# start must be a odd number, wall_index must be a even number
	def getWallIndex(start, length):
		assert length >= 3
		wall_index = randint(start + 1, start + length - 2)
		print("start:%d len:%d wall_index:%d" % (start, length, wall_index))
		if wall_index % 2 == 1:
			wall_index -= 1
		return wall_index
	
	# must check adjacent entry of four margin entries, 
	# if adjacent entry is movable, do nothing, otherwise set margin entry to wall
	def processMarginEntry(map, x, y, width, height, wall_x, wall_y, wall_value):
		margin_entrys = [(x, wall_y), (x+width-1, wall_y), (wall_x, y), (wall_x, y + height-1)]
		adjacent_entrys = [(x-1, wall_y), (x+width, wall_y), (wall_x, y - 1), (wall_x, y + height)]
		for i in range(4):
			x, y = (adjacent_entrys[i][0], adjacent_entrys[i][1])
			if map.isValid(x, y) and map.isMovable(x, y):
				pass
			else:
				map.setMap(margin_entrys[i][0], margin_entrys[i][1], wall_value)
	
	def getMeaningHole(start, end):
		len = end - start + 1
		return randint(start + len//4, end - len//4)
		
	if width <= 2 or height <= 2:
		return
	
	#generate a row and a column wall index, they must be even number
	wall_x, wall_y = (getWallIndex(x, width), getWallIndex(y, height))
	
	# must check adjacent entry of four margin entries is movable
	processMarginEntry(map, x, y, width, height, wall_x, wall_y, wall_value)
	
	for i in range(x+1, x+width-1):
		map.setMap(i, wall_y, wall_value)
	for i in range(y+1, y+height-1):
		map.setMap(wall_x, i, wall_value)
	
	#generate four holes, and create three holes
	holes = []
	print("(%d,%d) - (%d,%d), wall(%d,%d)" % (x, y, x + width -1, y + height - 1, wall_x, wall_y))
	holes.append((getMeaningHole(x, wall_x -1), wall_y))
	holes.append((getMeaningHole(wall_x + 1, x + width -1), wall_y))
	holes.append((wall_x, getMeaningHole(y, wall_y -1)))
	holes.append((wall_x, getMeaningHole(wall_y + 1, y + height - 1)))
	ignore_hole = randint(0, 3)
	for i in range(0,4):
		if i != ignore_hole:
			map.setMap(holes[i][0], holes[i][1], MAP_ENTRY_TYPE.MAP_EMPTY)
	
	recursiveDivision(map, x, y, wall_x - x, wall_y - y, wall_value)
	recursiveDivision(map, x, wall_y + 1, wall_x - x, y + height - wall_y -1, wall_value)
	recursiveDivision(map, wall_x + 1, y, x + width - wall_x -1, wall_y - y, wall_value)
	recursiveDivision(map, wall_x + 1, wall_y + 1, x + width - wall_x -1, y + height - wall_y -1, wall_value)

def doRecursiveDivision(map):
	# draw four margin wall lines
	for x in range(0, map.width):
		map.setMap(x, 0, MAP_ENTRY_TYPE.MAP_BLOCK)
		map.setMap(x, map.height-1, MAP_ENTRY_TYPE.MAP_BLOCK)
	
	for y in range(0, map.height):
		map.setMap(0, y, MAP_ENTRY_TYPE.MAP_BLOCK)
		map.setMap(map.width-1, y, MAP_ENTRY_TYPE.MAP_BLOCK)
		
	recursiveDivision(map, 1, 1, map.width - 2, map.height - 2, MAP_ENTRY_TYPE.MAP_BLOCK)


def randomPrim(map, width, height):
		
	def checkAdjacentPos(map, x, y, width, height, checklist):
		directions = []
		if x > 0:
			if not map.isVisited(2*(x-1)+1, 2*y+1):
				directions.append(WALL_DIRECTION.WALL_LEFT)
				
		if y > 0:
			if not map.isVisited(2*x+1, 2*(y-1)+1):
				directions.append(WALL_DIRECTION.WALL_UP)

		if x < width -1:
			if not map.isVisited(2*(x+1)+1, 2*y+1):
				directions.append(WALL_DIRECTION.WALL_RIGHT)
		
		if y < height -1:
			if not map.isVisited(2*x+1, 2*(y+1)+1):
				directions.append(WALL_DIRECTION.WALL_DOWN)
		
		if len(directions):
			direction = choice(directions)
			print("(%d, %d) => %s" % (x, y, str(direction)))
			if direction == WALL_DIRECTION.WALL_LEFT:
				map.setMap(2*(x-1)+1, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)
				map.setMap(2*x, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)
				checklist.append((x-1, y))
			elif direction == WALL_DIRECTION.WALL_UP:
				map.setMap(2*x+1, 2*(y-1)+1, MAP_ENTRY_TYPE.MAP_EMPTY)
				map.setMap(2*x+1, 2*y, MAP_ENTRY_TYPE.MAP_EMPTY)
				checklist.append((x, y-1))
			elif direction == WALL_DIRECTION.WALL_RIGHT:
				map.setMap(2*(x+1)+1, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)
				map.setMap(2*x+2, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)
				checklist.append((x+1, y))
			elif direction == WALL_DIRECTION.WALL_DOWN:
				map.setMap(2*x+1, 2*(y+1)+1, MAP_ENTRY_TYPE.MAP_EMPTY)
				map.setMap(2*x+1, 2*y+2, MAP_ENTRY_TYPE.MAP_EMPTY)
				checklist.append((x, y+1))
			return True
		else:
			return False
			
	start = (randint(0, width), randint(0, height))
	map.setMap(2*start[0], 2*start[1], MAP_ENTRY_TYPE.MAP_EMPTY)
	print("start(%d, %d)" % (start[0], start[1]))
	checklist = []
	checklist.append(start)
	while len(checklist):
		entry = choice(checklist)
		print(entry)		
		if not checkAdjacentPos(map, entry[0], entry[1], width, height, checklist):
			checklist.remove(entry)
	
		
def doRandomPrim(map):
	map.resetMap(MAP_ENTRY_TYPE.MAP_BLOCK)
	
	randomPrim(map, (map.width-1)//2, (map.height-1)//2)
		
def generateMap(map):
	#doRecursiveDivision(map)
	doRandomPrim(map)
	
def run():
	WIDTH = 31
	HEIGHT = 31
	
	map = Map(WIDTH, HEIGHT)
	generateMap(map)
	#source = map.generatePos((1,1),(1,HEIGHT-1))
	#dest = map.generatePos((WIDTH-2,WIDTH-2),(1,HEIGHT-1))
	#print("source:", source)
	#print("dest:", dest)
	#AStarSearch(map, source, dest)
	map.showMap()	
	

if __name__ == "__main__":
	run()	
	
	
	
	
	