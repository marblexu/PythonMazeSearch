from random import randint, choice
from GameMap import *
from AStarSearch import *
from enum import Enum

class MAZE_GENERATOR_TYPE(Enum):
	RECURSIVE_BACKTRACKER = 0,
	RANDOM_PRIM = 1,
	RECURSIVE_DIVISION = 2,
	UNION_FIND_SET = 3,

generator_types = {MAZE_GENERATOR_TYPE.RECURSIVE_BACKTRACKER:"Backtrack", 
					MAZE_GENERATOR_TYPE.RANDOM_PRIM:"Random Prim",
					MAZE_GENERATOR_TYPE.RECURSIVE_DIVISION:"Division",
					MAZE_GENERATOR_TYPE.UNION_FIND_SET:"Union Find"}

# recursive division algorithm
def recursiveDivision(map, x, y, width, height, wall_value):
	# start must be a odd number, wall_index must be a even number
	def getWallIndex(start, length):
		assert length >= 3
		wall_index = randint(start + 1, start + length - 2)
		#print("start:%d len:%d wall_index:%d" % (start, length, wall_index))
		if wall_index % 2 == 1:
			wall_index -= 1
		return wall_index
	
	# must check adjacent entry of four margin entries, 
	# if adjacent entry is movable, must set the margin entry as the hole
	def generateHoles(map, x, y, width, height, wall_x, wall_y):
		holes = []

		hole_entrys = [(randint(x, wall_x -1), wall_y), (randint(wall_x + 1, x + width -1), wall_y),
						(wall_x, randint(y, wall_y -1)), (wall_x, randint(wall_y + 1, y + height - 1))]
		margin_entrys = [(x, wall_y), (x+width-1, wall_y), (wall_x, y), (wall_x, y + height-1)]
		adjacent_entrys = [(x-1, wall_y), (x+width, wall_y), (wall_x, y - 1), (wall_x, y + height)]
		for i in range(4):
			adj_x, adj_y = (adjacent_entrys[i][0], adjacent_entrys[i][1])
			if map.isValid(adj_x, adj_y) and map.isMovable(adj_x, adj_y):
				map.setMap(margin_entrys[i][0], margin_entrys[i][1], MAP_ENTRY_TYPE.MAP_EMPTY)
			else:
				holes.append(hole_entrys[i])
		#print("(%d,%d, %d,%d), wall(%d,%d) hole(%d)" % (x, y, width, height, wall_x, wall_y, len(holes)))
		ignore_hole = randint(0, len(holes)-1)
		for i in range(0, len(holes)):
			if i != ignore_hole:
				map.setMap(holes[i][0], holes[i][1], MAP_ENTRY_TYPE.MAP_EMPTY)
	
	
	if width <= 1 or height <= 1:
		return
	
	#generate a row and a column wall index, they must be even number
	wall_x, wall_y = (getWallIndex(x, width), getWallIndex(y, height))
	
	#set horizontal and vertical lines to wall
	for i in range(x, x+width):
		map.setMap(i, wall_y, wall_value)
	for i in range(y, y+height):
		map.setMap(wall_x, i, wall_value)
	
	#create three holes
	generateHoles(map, x, y, width, height, wall_x, wall_y)
	
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

# find unvisited adjacent entries of four possible entris
# then add random one of them to checklist and mark it as visited
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
		#print("(%d, %d) => %s" % (x, y, str(direction)))
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
		# if not find any unvisited adjacent entry
		return False

# random prim algorithm
def randomPrim(map, width, height):			
	startX, startY = (randint(0, width-1), randint(0, height-1))
	print("start(%d, %d)" % (startX, startY))
	map.setMap(2*startX+1, 2*startY+1, MAP_ENTRY_TYPE.MAP_EMPTY)
	
	checklist = []
	checklist.append((startX, startY))
	while len(checklist):
		# select a random entry from checklist
		entry = choice(checklist)	
		if not checkAdjacentPos(map, entry[0], entry[1], width, height, checklist):
			# the entry has no unvisited adjacent entry, so remove it from checklist
			checklist.remove(entry)
		
def doRandomPrim(map):
	# set all entries of map to wall
	map.resetMap(MAP_ENTRY_TYPE.MAP_BLOCK)	
	randomPrim(map, (map.width-1)//2, (map.height-1)//2)

# recursive backtracker algorithm
def recursiveBacktracker(map, width, height):
	startX, startY = (randint(0, width-1), randint(0, height-1))
	print("start(%d, %d)" % (startX, startY))
	map.setMap(2*startX+1, 2*startY+1, MAP_ENTRY_TYPE.MAP_EMPTY)
	
	checklist = [] 
	checklist.append((startX, startY))
	while len(checklist):
		# use checklist as a stack, get entry from the top of stack 
		entry = checklist[-1]
		if not checkAdjacentPos(map, entry[0], entry[1], width, height, checklist):
			# the entry has no unvisited adjacent entry, so remove it from checklist
			checklist.remove(entry)

def doRecursiveBacktracker(map):
	# set all entries of map to wall
	map.resetMap(MAP_ENTRY_TYPE.MAP_BLOCK)	
	recursiveBacktracker(map, (map.width-1)//2, (map.height-1)//2)

def unionFindSet(map, width, height):
	# find the root of the tree which the node belongs to
	def findSet(parent, index):
		if index != parent[index]:
			return findSet(parent, parent[index])
		return parent[index]
	
	def getNodeIndex(x, y):
		return x * height + y
	
	# union two unconnected trees
	def unionSet(parent, index1, index2, weightlist):
		root1 = findSet(parent, index1)
		root2 = findSet(parent, index2)
		if root1 == root2:
			return
		if root1 != root2:
			# take the high weight tree as the root, 
			# make the whole tree balance to achieve everage search time O(logN)
			if weightlist[root1] > weightlist[root2]:
				parent[root2] = root1
				weightlist[root1] += weightlist[root2]
			else:
				parent[root1] = root2
				weightlist[root2] += weightlist[root2]
	
	# For Debug: print the generate tree
	def printPath(parent, x, y):
		node = x * height + y
		path = '(' + str(node//height) +','+ str(node%height)+')'
		node = parent[node]
		while node != parent[node]:
			path = '(' + str(node//height) +','+ str(node%height)+') <= ' + path
			node = parent[node]
		path = '(' + str(node//height) +','+ str(node%height)+') <= ' + path
		print(path)

	def printTree(parent):
		for x in range(width):
			for y in range(height):
				printPath(parentlist, x, y)
			
	def checkAdjacentPos(map, x, y, width, height, parentlist, weightlist):
		directions = []
		node1 = getNodeIndex(x,y)
		root1 = findSet(parentlist, node1)
		# check four adjacent entries, add any unconnected entries
		if x > 0:		
			root2 = findSet(parentlist, getNodeIndex(x-1, y))
			if root1 != root2:
				directions.append(WALL_DIRECTION.WALL_LEFT)
					
		if y > 0:
			root2 = findSet(parentlist, getNodeIndex(x, y-1))
			if root1 != root2:
				directions.append(WALL_DIRECTION.WALL_UP)

		if x < width -1:
			root2 = findSet(parentlist, getNodeIndex(x+1, y))
			if root1 != root2:
				directions.append(WALL_DIRECTION.WALL_RIGHT)
			
		if y < height -1:
			root2 = findSet(parentlist, getNodeIndex(x, y+1))
			if root1 != root2:
				directions.append(WALL_DIRECTION.WALL_DOWN)
			
		if len(directions):
			# choose one of the unconnected adjacent entries
			direction = choice(directions)
			if direction == WALL_DIRECTION.WALL_LEFT:
				adj_x, adj_y = (x-1, y)
				map.setMap(2*x, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)				
			elif direction == WALL_DIRECTION.WALL_UP:
				adj_x, adj_y = (x, y-1)
				map.setMap(2*x+1, 2*y, MAP_ENTRY_TYPE.MAP_EMPTY)
			elif direction == WALL_DIRECTION.WALL_RIGHT:
				adj_x, adj_y = (x+1, y)
				map.setMap(2*x+2, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)
			elif direction == WALL_DIRECTION.WALL_DOWN:
				adj_x, adj_y = (x, y+1)
				map.setMap(2*x+1, 2*y+2, MAP_ENTRY_TYPE.MAP_EMPTY)
			
			node2 = getNodeIndex(adj_x, adj_y)
			unionSet(parentlist, node1, node2, weightlist)
			return True
		else:
			# the four adjacent entries are all connected, so can remove this entry
			return False
			
	parentlist = [x*height+y for x in range(width) for y in range(height)]
	weightlist = [1 for x in range(width) for y in range(height)] 
	checklist = []
	for x in range(width):
		for y in range(height):
			checklist.append((x,y))
			# set all entries to empty
			map.setMap(2*x+1, 2*y+1, MAP_ENTRY_TYPE.MAP_EMPTY)
		
	while len(checklist):
		# select a random entry from checklist
		entry = choice(checklist)
		if not checkAdjacentPos(map, entry[0], entry[1], width, height, parentlist, weightlist):
			checklist.remove(entry)

	#printTree(parentlist)
			
def doUnionFindSet(map):
	# set all entries of map to wall
	map.resetMap(MAP_ENTRY_TYPE.MAP_BLOCK)
	unionFindSet(map, (map.width-1)//2, (map.height-1)//2)
	
def generateMap(map, type):
	if type == MAZE_GENERATOR_TYPE.RECURSIVE_BACKTRACKER:
		doRecursiveBacktracker(map)
	elif type == MAZE_GENERATOR_TYPE.RANDOM_PRIM:
		doRandomPrim(map)
	elif type == MAZE_GENERATOR_TYPE.RECURSIVE_DIVISION:
		doRecursiveDivision(map)
	elif type == MAZE_GENERATOR_TYPE.UNION_FIND_SET:
		doUnionFindSet(map)
	
def run():
	WIDTH = 31
	HEIGHT = 21
	
	map = Map(WIDTH, HEIGHT)
	generateMap(map, MAZE_GENERATOR_TYPE.UNION_FIND_SET)
	source = map.generatePos((1,1),(1,HEIGHT-1))
	dest = map.generatePos((WIDTH-2,WIDTH-2),(1,HEIGHT-1))
	print("source:", source)
	print("dest:", dest)
	AStarSearch(map, source, dest)
	map.showMap()	
	

if __name__ == "__main__":
	run()	
