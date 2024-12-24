import random
from svgwrite import Drawing
from svgwrite.container import Group
import os


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


class EnhancedSudokuGenerator(SudokuGenerator):
    def __init__(self, difficulty, puzzle_number, n_hints, n_placeholders=0, global_number=1):
        super().__init__(n_hints)
        self.difficulty = difficulty
        self.puzzle_number = puzzle_number
        self.n_placeholders = n_placeholders
        self.puzzle_folder = "puzzles"
        self.global_number = global_number
        self.coordinates_file = f"{self.puzzle_folder}/{self.global_number}. {
            self.difficulty}{self.puzzle_number}_coordinates.txt"

    def update_coordinates_file(self, solution_grid):
        """Create coordinates file for the current puzzle."""
        os.makedirs(self.puzzle_folder, exist_ok=True)

        coordinates_dict = {}
        for num in range(1, 10):
            coordinates = []
            for i in range(9):
                for j in range(9):
                    if solution_grid[i][j] == num:
                        coordinates.append(f"R{i+1}C{j+1}")
            coordinates_dict[num] = coordinates

        with open(self.coordinates_file, 'w') as f:
            for num, coords in coordinates_dict.items():
                random.shuffle(coords)
                f.write(f"{num}: {', '.join(coords)}\n")

    def generate_linked_puzzle(self):
        """Generate a puzzle with placeholders if needed."""
        self.fill_grid()
        solution_grid = [row[:] for row in self.grid]

        solution_filename = f"{
            self.puzzle_folder}/{self.global_number}. {self.difficulty}{self.puzzle_number}S"
        createPuzzleSvg(solution_filename, solution_grid)

        self.update_coordinates_file(solution_grid)
        self.remove_numbers()
        puzzle_grid = [row[:] for row in self.grid]

        if self.n_placeholders > 0 and self.puzzle_number > 1:
            prev_coord_file = f"{self.puzzle_folder}/{self.global_number -
                                                      1}. {self.difficulty}{self.puzzle_number-1}_coordinates.txt"

            if os.path.exists(prev_coord_file):
                placeholders = {}
                available_numbers = []
                used_values = set()

                for i in range(9):
                    for j in range(9):
                        if puzzle_grid[i][j] != 0:
                            available_numbers.append((puzzle_grid[i][j], i, j))

                random.shuffle(available_numbers)

                coord_mapping = {}
                with open(prev_coord_file, 'r') as f:
                    for line in f:
                        if ': ' in line:
                            num, coords = line.strip().split(': ')
                            coord_mapping[int(num)] = coords.split(', ')

                placeholder_idx = 0
                for num, i, j in available_numbers:
                    if placeholder_idx >= self.n_placeholders:
                        break

                    if num not in used_values and num in coord_mapping and coord_mapping[num]:
                        placeholder = chr(97 + placeholder_idx)
                        coord = random.choice(coord_mapping[num])
                        placeholders[placeholder] = f"{coord} [={num}]"
                        used_values.add(num)

                        for x in range(9):
                            for y in range(9):
                                if puzzle_grid[x][y] == num:
                                    puzzle_grid[x][y] = placeholder

                        placeholder_idx += 1

                with open(f"{self.puzzle_folder}/{self.global_number}. {self.difficulty}{self.puzzle_number}_placeholders.txt", 'w') as f:
                    for placeholder, coord in placeholders.items():
                        f.write(f"{placeholder} = {coord}\n")

        puzzle_filename = f"{
            self.puzzle_folder}/{self.global_number}. {self.difficulty}{self.puzzle_number}"
        createPuzzleSvg(puzzle_filename, puzzle_grid)

        return puzzle_grid, solution_grid


def createPuzzleSet(difficulty_level, num_puzzles, num_hints, num_placeholders=0, start_number=1, global_start=1):
    """Create a set of puzzles for a specific difficulty level."""
    os.makedirs("puzzles", exist_ok=True)

    for i in range(num_puzzles):
        puzzle_number = start_number + i
        global_number = global_start + i
        generator = EnhancedSudokuGenerator(
            difficulty=difficulty_level,
            puzzle_number=puzzle_number,
            n_hints=num_hints,
            n_placeholders=num_placeholders,
            global_number=global_number
        )
        puzzle_grid, solution_grid = generator.generate_linked_puzzle()


def createPuzzleSvg(filename="Puzzle", grid=[]):
    filename = filename if filename.endswith(".svg") else filename + ".svg"

    grid_size = len(grid)
    cell_size = 40
    grid_font_size = 20
    grid_outline_width = 5
    grid_width = grid_size * cell_size
    grid_height = grid_size * cell_size

    dwg = Drawing(filename, size=(grid_width, grid_height))
    grid_group = Group()

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

    for i in range(1, grid_size):
        if i % 3 == 0:
            # Horizontal line
            y = i * cell_size
            dwg.add(dwg.line(start=(0, y), end=(grid_width, y),
                    stroke='black', stroke_width=3))
            # Vertical line
            x = i * cell_size
            dwg.add(dwg.line(start=(x, 0), end=(x, grid_height),
                    stroke='black', stroke_width=3))

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
    createPuzzleSvg("Puzzle", grid)

    if (solver.Suduko(grid, 0, 0)):
        print('\n', '*'*5, 'SOLUTION', '*'*5)
        displayGrid(grid)
        createPuzzleSvg("Solution", grid)
    else:
        print("No Solution exist:(")
