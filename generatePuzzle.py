import random
from math import sqrt
from svgwrite import Drawing
from svgwrite.container import Group


class SudokuGenerator:
    def __init__(self, n_hints=20):
        self.n_hints = n_hints
        self.size = 9
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]

    def is_valid(self, num, row, col):
        """Check if placing a number is valid."""
        for i in range(self.size):
            if self.grid[row][i] == num or self.grid[i][col] == num:
                return False

        box_start_row = row - row % 3
        box_start_col = col - col % 3

        for i in range(3):
            for j in range(3):
                if self.grid[box_start_row + i][box_start_col + j] == num:
                    return False

        return True

    def fill_grid(self):
        """Fill the entire grid recursively."""
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == 0:
                    random_numbers = list(range(1, self.size + 1))
                    random.shuffle(random_numbers)

                    for num in random_numbers:
                        if self.is_valid(num, row, col):
                            self.grid[row][col] = num

                            if self.fill_grid():
                                return True

                            self.grid[row][col] = 0

                    return False
        return True

    def remove_numbers(self):
        """Remove numbers to create a puzzle with n hints."""
        cells_to_remove = self.size ** 2 - self.n_hints
        while cells_to_remove > 0:
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)

            if self.grid[row][col] != 0:
                self.grid[row][col] = 0
                cells_to_remove -= 1

    def generate_puzzle(self):
        """Generate a Sudoku puzzle."""
        self.fill_grid()
        self.remove_numbers()
        return self.grid

class SolverSudoku:
    def solve(self, grid, row, col, num):
        for x in range(9):
            if grid[row][x] == num:
                return False

        for x in range(9):
            if grid[x][col] == num:
                return False

        startRow = row - row % 3
        startCol = col - col % 3
        for i in range(3):
            for j in range(3):
                if grid[i + startRow][j + startCol] == num:
                    return False
        return True

    def Suduko(self, grid, row, col):

        if (row == 9 - 1 and col == 9):
            return True
        if col == 9:
            row += 1
            col = 0
        if grid[row][col] > 0:
            return self.Suduko(grid, row, col + 1)
        for num in range(1, 9 + 1):

            if self.solve(grid, row, col, num):

                grid[row][col] = num
                if self.Suduko(grid, row, col + 1):
                    return True
            grid[row][col] = 0
        return False


def create_puzzle_svg(filename="Puzzle", grid=[]):
    filename = filename if filename.endswith(".svg") else filename + ".svg"
    
    grid_size = len(grid)
    cell_size = 40
    grid_font_size = 20
    grid_outline_width = 5
    grid_width = grid_size * cell_size
    grid_height = grid_size * cell_size

    dwg = Drawing(filename, size=(grid_width, grid_height))
    grid_group = Group()

    # Draw cells and text
    for row in range(grid_size):
        for col in range(grid_size):
            cell_x = col * cell_size
            cell_y = row * cell_size

            char_x = cell_x + cell_size // 2
            char_y = cell_y + cell_size // 2
            value = str(grid[row][col]) if grid[row][col] != 0 else ""
            grid_group.add(dwg.text(value, insert=(char_x, char_y), text_anchor="middle",
                                    alignment_baseline="central", font_size=grid_font_size, fill='black'))

            grid_group.add(dwg.rect(insert=(cell_x, cell_y), size=(
                cell_size, cell_size), fill='none', stroke='black', stroke_width=1))

    # Add thicker lines for 3x3 subgrids
    for i in range(1, grid_size):
        if i % 3 == 0:
            # Horizontal line
            y = i * cell_size
            dwg.add(dwg.line(start=(0, y), end=(grid_width, y), stroke='black', stroke_width=3))
            # Vertical line
            x = i * cell_size
            dwg.add(dwg.line(start=(x, 0), end=(x, grid_height), stroke='black', stroke_width=3))

    dwg.add(grid_group)

    # Add outer grid border
    dwg.add(dwg.rect(insert=(0, 0), size=(
        grid_width, grid_height), fill='none', stroke='red', stroke_width=grid_outline_width))

    dwg.save()

def displayGrid(grid):
    for i in range(9):
        for j in range(9):
            print(grid[i][j], end=" ")
        print()


if __name__ == "__main__":
    # Minimum number of hints required to have a unique solution to a Sudoku puzzle is 17, so n_hints should always be>= 17
    n_hints = 20
    sudoku = SudokuGenerator(n_hints)
    solver = SolverSudoku()
    grid = sudoku.generate_puzzle()

    print('\n', '*'*5, 'PUZZLE GRID', '*'*5)
    displayGrid(grid)
    create_puzzle_svg("Puzzle", grid)

    if (solver.Suduko(grid, 0, 0)):
        print('\n', '*'*5, 'SOLUTION', '*'*5)
        displayGrid(grid)
        create_puzzle_svg("Solution", grid)
    else:
        print("No Solution exist:(")

