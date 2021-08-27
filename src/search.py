import sys

class Node():
    def __init__(self, state, parent, action):
        self.state   = state
        self.parent  = parent
        self.action  = action

class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self,state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class Maze():
    def __init__(self, filename): # ime fajla se dobija iz kompajlerske naredbe =python3 what_to_compile args...=
        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read() # procita ceo maze fajl

        # Validate start and goal - can't have more than one start or endpoint
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width of maze
        contents = contents.splitlines() # splitplines uzima ceo sadrzaj "contents"(maze file) i pravi niz recenica koje prelama na osnovu line break-a
        self.height = len(contents) # broj recenica(redova u dokumentu) = visini maze-a
        self.width = max(len(line) for line in contents) # visina maze-a je najduza "recenica" u nizu contents(1 karakter = 1 "kolona")

        # Keep track of walls
        self.walls = [] # self.walls - class field of Maze, it's a matrix which translates a character into True(if character is #)/False(everything else)
        for i in range(self.height): # iterate through every row
            row = [] # keep track of walls for particular row (or index i)
            for j in range(self.width): # iterate through every "column" in that particular "row", effectively making i,j counters a "field" in the maze
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j) # this is where we define the starting point for the Maze using class field "self.start"
                        row.append(False) # we also append False to the current row because starting point isn't a wall
                    elif contents[i][j] == "B":
                        self.goal = (i, j) # this is where we define the end point for the Maze using class field "self.goal"
                        row.append(False) # we also append False to the current row because goal point isn't a wall
                    elif contents[i][j] == " ":
                        row.append(False) # "empty" cells( spaces ) are paths where we can move, so not walls
                    else:
                        row.append(True) # everything else( we're only left with "#" ) is a wall
                except IndexError:
                    row.append(False)
            self.walls.append(row) # every time we complete a row, append it to the "matrix" self.walls

        self.solution = None # initialize the solution field


    def print(self): # just prints out the current state of the Maze
        # solution is an ordered pair of values (actions, states), first being a list of actions taken, second being a list of states/cells visited
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()


    def neighbors(self, state): # determines neighbours of the given state - state is a pair of numbers (row, column) (not a tuple!)
        row, col = state # which is why we can extract it like this
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                # action is viable IFF:
                # NOTE we move into an empty space(not a wall) ^ - reminder: walls is a True/False matrix, where 1 cell says whether it's a wall or not
                # NOTE we don't "fall out" of the map/matrix horizontally, so if the row-value isn't negative or greater than the height of the maze
                # NOTE we don't "fall out" of the map/matrix vertically, so if the column-value isn't negative or greater than the width of the maze
                result.append((action, (r, c)))
        return result


    def solve(self):
        """Finds a solution to maze, if one exists."""

        # Keep track of number of states explored
        self.num_explored = 0

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = set() # keep track of states we have explored so we don't end up in a loop!

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if frontier.empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None: # if it's none, it means we've reached the start node
                    actions.append(node.action)
                    cells.append(node.state) # cell = state
                    node = node.parent # move upwards the hierarchy through parent pointer
                actions.reverse() # the actions we took in order
                cells.reverse() # the "cells" of a matrix we visited in order
                self.solution = (actions, cells)
                return

            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            for action, state in self.neighbors(node.state): # neighbors returns a list of ordered pairs (action, state/cell we can go to)
                if not frontier.contains_state(state) and state not in self.explored:
                    # IFF the state isn't already in the frontier(no need for duplicates) and if we haven't explored it already ( to avoid loops ),
                    # only then perform the following:
                    child = Node(state=state, parent=node, action=action) # create a Node we can visit with an action
                    frontier.add(child) # append it to the frontier


    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw

        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    (
                        ( (j * cell_size + cell_border, i * cell_size + cell_border),
                          ( (j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border) )
                    ),
                    fill=fill
                )

        img.save(filename)

if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

m = Maze(sys.argv[1]) # sys.argv is array of arguments we pass into the compiler: python3 file-to-compile args...
print("Maze:")
m.print() # prints the entire maze
print("Solving...")
m.solve() # solves the maze
print("States Explored:", m.num_explored) # prints the number of states explored (we keep track of that)
print("Solution:")
m.print() # prints the solution somehow (?)
m.output_image("maze.png", show_explored=True) # prints the solution image
