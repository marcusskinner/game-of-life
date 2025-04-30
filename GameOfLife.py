import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import time

class GameOfLife:
    
    def __init__(self, filepath = None, shape=(10, 10), resolution=(480, 480), birth_rule="3", survival_rule="23", background_color=(255, 255, 255), cell_color=(0, 0, 0)):
        
        # error checking
        if shape[0] >= resolution[0] or shape[1] >= resolution[1]:
            print("Cell width cannot be less than 1 pixel!")

        # set the visualization frame
        self.background_color = background_color
        self.cell_color = cell_color
        self.resolution = resolution
        self.frame = (np.ones((resolution[0], resolution[1], 3)) * background_color).astype('uint8')

        if filepath is None:
            # a matrix to track the occupancy of a cell
            self.game_state = np.zeros(shape=shape).astype('int')
            self.shape = shape
            self.cell_pixels = (resolution[0]//self.shape[0], resolution[1]//self.shape[1])
        else:
            self.read_file(filepath)

        # set rules
        # the standard to input rules into a game of life is to use a pattern string
        self.birth_values = np.array(list(birth_rule)).astype('int')
        self.survival_values = np.array(list(survival_rule)).astype('int')

        # general info needed for some functions
        self.num_cells = self.shape[0] * self.shape[1]
        self.num_rows = self.shape[0]
        self.num_cols = self.shape[1]
        
        # a matrix to track the number of adjacent cells that are occupied for each cell
        self.cell_neighbors = np.zeros(shape=self.shape).astype('int')

        # a filter to compute the number of neighbors each cell has
        self.neighbor_kernel = np.array([[1, 1, 1],
                                         [1, 0, 1],
                                         [1, 1, 1]])

    """
    Function super ugly but F it
    """
    def read_file(self, filepath):
        file = open(filepath, 'r')
        lines = file.readlines()

        # create game_state
        self.shape = (len(lines), len(lines[0]))
        self.game_state = np.zeros(shape=self.shape).astype('int')
        self.cell_pixels = (self.resolution[0]//self.shape[0], self.resolution[1]//self.shape[1])

        for i, line in enumerate(lines):
    
            chars = list(line)
            
            try:
                chars.remove('\n')
            except:
                pass

            for j, c in enumerate(chars):

                if c == 'O':
                    self.set_cell(i, j)
            
                   
        
    def set_cell(self, row, col):
        self.game_state[row, col] = 1
        self.frame[row * self.cell_pixels[0]:(row + 1) * self.cell_pixels[0], col * self.cell_pixels[1]:(col+1)*self.cell_pixels[1]] = self.cell_color

    
    def unset_cell(self, row, col):
        self.game_state[row, col] = 0
        self.frame[row * self.cell_pixels[0]:(row + 1) * self.cell_pixels[0], col * self.cell_pixels[1]:(col+1)*self.cell_pixels[1]] = self.background_color

    
    def set_random_cells(self, num_cells):
        # get an array of unique cell indices
        cell_idx = np.random.choice(np.linspace(0, self.num_cells-1, self.num_cells).astype('int'), size = num_cells, replace=False)
        
        for i in range(num_cells):
            curr_row = cell_idx[i]//self.num_cols
            curr_col = cell_idx[i] % self.num_rows

            self.set_cell(curr_row, curr_col)
        
            
    def get_neighbors(self):
        """
        So I was researching how to use an FFT to find oscillations in a pattern, but came across this article https://medium.com/100-days-of-algorithms/day-50-conways-game-of-life-aa6b7c9200e8
        which you can apply the convolution to the game state by first applying a fourier transform. Well, not just to the game of life but any 2D filter in general. 
        Super cool but I didn't think of it myself so decided to not do it and opt for normal image filtering techniques. Still really cool.
        """
        # pad the game state before applying convolution
        cell_occupancy = np.pad(self.game_state, ((2, 2), (2, 2)))

        # go through each cell and apply convolution
        # we do only one for loop because prettier imo
        for i in range(self.num_cells):
            curr_row = i // self.num_cols + 2
            curr_col = i % self.num_rows + 2

            self.cell_neighbors[curr_row - 2, curr_col - 2] = np.sum(np.multiply(self.neighbor_kernel, cell_occupancy[curr_row-1:curr_row+2, curr_col-1:curr_col+2]))

    def apply_survival(self):
        # find cells that do not survive
        idx = np.where(~np.isin(self.cell_neighbors, self.survival_values))

        # unset cells
        for i in range(idx[0].shape[0]):
            self.unset_cell(idx[0][i], idx[1][i])

    
    def apply_birth(self):
        # find cells to birth
        idx = np.where(np.isin(self.cell_neighbors, self.birth_values))

        # set cells
        for i in range(idx[0].shape[0]):
            self.set_cell(idx[0][i], idx[1][i])

    
    def update(self):
        print(self.game_state)
        self.get_neighbors()
        self.apply_survival()
        self.apply_birth()


    def run(self, fps=60):
        """
        Displays a visual representation of the game state, updating continuously
        """
        while(True):
            
            start_time = time.time()
            
            self.update()

            cv.imshow('Game of Life', self.frame)
            
            # exit when spacebar is pressed
            key = cv.waitKey(1) & 0xFF 
        
            # Exit if the spacebar is pressed
            if key == ord(' '):
                break

            # sleep to keep framerate
            run_time = time.time() - start_time

            time.sleep(max(0, 1/fps - run_time))