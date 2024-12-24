"""Generate linked Sudoku puzzles and their SVG pages."""

import os
import random
from itertools import combinations

from svgwrite import Drawing


def count_solutions(grid, limit=2):
    """Count Sudoku solutions up to limit without changing the input grid."""
    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        raise ValueError("Sudoku grid must be 9 by 9")
    rows = [0] * 9
    columns = [0] * 9
    boxes = [0] * 9
    empty = []
    for row in range(9):
        for col in range(9):
            value = grid[row][col]
            if value == 0:
                empty.append((row, col))
                continue
            if not isinstance(value, int) or not 1 <= value <= 9:
                raise ValueError("Grid must contain digits 0 through 9")
            bit = 1 << value
            box = (row // 3) * 3 + col // 3
            if rows[row] & bit or columns[col] & bit or boxes[box] & bit:
                return 0
            rows[row] |= bit
            columns[col] |= bit
            boxes[box] |= bit

    def search(remaining):
        if remaining == 0:
            return 1
        best = -1
        best_mask = 0
        best_count = 10
        for index in range(remaining):
            row, col = empty[index]
            box = (row // 3) * 3 + col // 3
            mask = 0x3FE & ~(rows[row] | columns[col] | boxes[box])
            choices = mask.bit_count()
            if choices == 0:
                return 0
            if choices < best_count:
                best, best_mask, best_count = index, mask, choices
                if choices == 1:
                    break
        empty[best], empty[remaining - 1] = empty[remaining - 1], empty[best]
        row, col = empty[remaining - 1]
        box = (row // 3) * 3 + col // 3
        total = 0
        mask = best_mask
        while mask and total < limit:
            bit = mask & -mask
            mask -= bit
            rows[row] |= bit
            columns[col] |= bit
            boxes[box] |= bit
            total += search(remaining - 1)
            rows[row] ^= bit
            columns[col] ^= bit
            boxes[box] ^= bit
        empty[best], empty[remaining - 1] = empty[remaining - 1], empty[best]
        return min(total, limit)

    return search(len(empty))


class SudokuGenerator:
    def __init__(self, n_hints=30):
        self.n_hints = n_hints
        self.grid = [[0] * 9 for _ in range(9)]

    def is_valid(self, value, row, col):
        if value in self.grid[row] or any(self.grid[index][col] == value for index in range(9)):
            return False
        box_row = row - row % 3
        box_col = col - col % 3
        return all(self.grid[box_row + dr][box_col + dc] != value
                   for dr in range(3) for dc in range(3))

    def fill_grid(self):
        for row in range(9):
            for col in range(9):
                if self.grid[row][col] == 0:
                    numbers = list(range(1, 10))
                    random.shuffle(numbers)
                    for value in numbers:
                        if self.is_valid(value, row, col):
                            self.grid[row][col] = value
                            if self.fill_grid():
                                return True
                            self.grid[row][col] = 0
                    return False
        return True

    def remove_numbers(self):
        """Remove clues only while the puzzle retains one solution."""
        cells = [(row, col) for row in range(9) for col in range(9)]
        random.shuffle(cells)
        clues = 81
        for row, col in cells:
            if clues <= self.n_hints:
                break
            value = self.grid[row][col]
            self.grid[row][col] = 0
            if count_solutions(self.grid) == 1:
                clues -= 1
            else:
                self.grid[row][col] = value
        return clues

    def generate_puzzle(self):
        self.fill_grid()
        self.remove_numbers()
        return self.grid


class EnhancedSudokuGenerator(SudokuGenerator):
    def __init__(self, difficulty, puzzle_number, n_hints, n_placeholders=0,
                 global_number=1, previous_solution=None, puzzle_folder="puzzles"):
        super().__init__(n_hints)
        self.difficulty = difficulty
        self.puzzle_number = puzzle_number
        self.n_placeholders = n_placeholders
        self.global_number = global_number
        self.previous_solution = previous_solution
        self.puzzle_folder = puzzle_folder
        self.link_entries = []

    def choose_placeholders(self, puzzle_grid):
        """Find digits whose hidden clues make the puzzle ambiguous without the link."""
        available = sorted({value for row in puzzle_grid for value in row if value})
        if len(available) < self.n_placeholders:
            return None
        choices = list(combinations(available, self.n_placeholders))
        random.shuffle(choices)
        for values in choices:
            hidden = [[0 if value in values else value for value in row]
                      for row in puzzle_grid]
            if count_solutions(hidden) > 1:
                return values
        return None

    def generate_linked_puzzle(self):
        """Generate a unique puzzle and link it to the previous solution."""
        needs_link = self.global_number > 1 and self.n_placeholders > 0
        if needs_link and self.previous_solution is None:
            raise ValueError("A linked puzzle needs the previous solution")
        for _ in range(20):
            self.grid = [[0] * 9 for _ in range(9)]
            self.fill_grid()
            solution_grid = [row[:] for row in self.grid]
            self.actual_hints = self.remove_numbers()
            numeric_grid = [row[:] for row in self.grid]
            values = self.choose_placeholders(numeric_grid) if needs_link else ()
            if values is not None:
                break
        else:
            raise RuntimeError("Could not generate a puzzle with the requested link")

        os.makedirs(self.puzzle_folder, exist_ok=True)
        stem = f"{self.global_number}. {self.difficulty}{self.puzzle_number}"
        createPuzzleSvg(os.path.join(self.puzzle_folder, stem + "S"), solution_grid)
        puzzle_grid = [row[:] for row in numeric_grid]
        if needs_link:
            with open(os.path.join(self.puzzle_folder, stem + "_placeholders.txt"),
                      "w", encoding="utf-8") as handle:
                for index, value in enumerate(values):
                    letter = chr(97 + index)
                    coordinates = [(row, col) for row in range(9) for col in range(9)
                                   if self.previous_solution[row][col] == value]
                    row, col = random.choice(coordinates)
                    handle.write(f"{letter} = R{row + 1}C{col + 1} [={value}]\n")
                    self.link_entries.append((letter, str(row + 1), str(col + 1)))
                    puzzle_grid = [[letter if cell == value else cell for cell in line]
                                   for line in puzzle_grid]
        createPuzzleSvg(os.path.join(self.puzzle_folder, stem), puzzle_grid)
        return puzzle_grid, solution_grid


def createPuzzleSet(difficulty_level, num_puzzles, num_hints, num_placeholders=0,
                    start_number=1, global_start=1, previous_solution=None,
                    puzzle_folder="puzzles", links=None):
    """Create one difficulty tier, returning its final solution for the next tier."""
    for index in range(num_puzzles):
        generator = EnhancedSudokuGenerator(
            difficulty=difficulty_level,
            puzzle_number=start_number + index,
            n_hints=num_hints,
            n_placeholders=num_placeholders,
            global_number=global_start + index,
            previous_solution=previous_solution,
            puzzle_folder=puzzle_folder,
        )
        _, previous_solution = generator.generate_linked_puzzle()
        if links is not None:
            links[global_start + index] = generator.link_entries
    return previous_solution


def createPuzzleSvg(filename="Puzzle", grid=None):
    """Render one Sudoku grid as an SVG."""
    grid = grid if grid is not None else []
    filename = filename if filename.endswith(".svg") else filename + ".svg"
    cell_size = 40
    grid_width = len(grid) * cell_size
    drawing = Drawing(filename, size=(grid_width, grid_width))
    for row in range(len(grid)):
        for col in range(len(grid)):
            x, y = col * cell_size, row * cell_size
            value = "" if grid[row][col] == 0 else str(grid[row][col])
            drawing.add(drawing.text(value, insert=(x + 20, y + 20),
                                     text_anchor="middle", alignment_baseline="central",
                                     font_size=20, fill="black"))
            drawing.add(drawing.rect(insert=(x, y), size=(cell_size, cell_size),
                                     fill="none", stroke="black", stroke_width=1))
    for index in range(3, len(grid), 3):
        position = index * cell_size
        drawing.add(drawing.line(start=(0, position), end=(grid_width, position),
                                 stroke="black", stroke_width=3))
        drawing.add(drawing.line(start=(position, 0), end=(position, grid_width),
                                 stroke="black", stroke_width=3))
    drawing.add(drawing.rect(insert=(0, 0), size=(grid_width, grid_width),
                             fill="none", stroke="red", stroke_width=5))
    drawing.save()


if __name__ == "__main__":
    puzzle = SudokuGenerator(30).generate_puzzle()
    print("Clues:", sum(value > 0 for row in puzzle for value in row))
    print("Solutions:", count_solutions(puzzle))
