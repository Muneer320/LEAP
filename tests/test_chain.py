import random
import re
import tempfile
import unittest
from pathlib import Path

from createBook import SudokuBookCreator
from generatePuzzle import EnhancedSudokuGenerator, count_solutions


class ChainTests(unittest.TestCase):
    def test_solver_counts_without_mutating_grid(self):
        grid = [[0] * 9 for _ in range(9)]
        self.assertEqual(count_solutions(grid), 2)
        self.assertEqual(grid, [[0] * 9 for _ in range(9)])
        grid[0][0] = grid[0][1] = 1
        self.assertEqual(count_solutions(grid), 0)

    def test_cross_tier_link_requires_previous_solution(self):
        random.seed(13)
        with tempfile.TemporaryDirectory() as folder:
            first = EnhancedSudokuGenerator("E", 1, 40, 3, 1, puzzle_folder=folder)
            first_puzzle, first_solution = first.generate_linked_puzzle()
            self.assertEqual(count_solutions(first_puzzle), 1)
            self.assertEqual(sum(bool(value) for row in first_puzzle for value in row), 40)

            second = EnhancedSudokuGenerator("M", 1, 36, 5, 2,
                                             previous_solution=first_solution,
                                             puzzle_folder=folder)
            linked, solution = second.generate_linked_puzzle()
            link_file = Path(folder) / "2. M1_placeholders.txt"
            self.assertTrue(link_file.exists())
            lines = link_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 5)
            values = {}
            for line in lines:
                match = re.fullmatch(r"([a-e]) = R([1-9])C([1-9]) \[=([1-9])\]", line)
                self.assertIsNotNone(match)
                letter, row, col, value = match.groups()
                self.assertEqual(first_solution[int(row) - 1][int(col) - 1], int(value))
                values[letter] = int(value)
            resolved = [[values.get(cell, cell) for cell in row] for row in linked]
            hidden = [[0 if isinstance(cell, str) else cell for cell in row] for row in linked]
            self.assertEqual(count_solutions(resolved), 1)
            self.assertEqual(count_solutions(hidden), 2)
            for row in range(9):
                for col in range(9):
                    if resolved[row][col]:
                        self.assertEqual(resolved[row][col], solution[row][col])

            creator = SudokuBookCreator()
            next_table = creator.fetch_next_puzzle_placeholders(1, folder)
            self.assertEqual(len(next_table), 5)
            self.assertEqual(next_table[0][0], "a")
            link_file.unlink()
            creator = SudokuBookCreator(links_by_number={2: second.link_entries})
            self.assertEqual(creator.fetch_next_puzzle_placeholders(1, folder),
                             second.link_entries)

    def test_low_hint_request_keeps_unique_fallback(self):
        random.seed(17)
        with tempfile.TemporaryDirectory() as folder:
            generator = EnhancedSudokuGenerator("G", 1, 24, 9, 1,
                                                puzzle_folder=folder)
            puzzle, _ = generator.generate_linked_puzzle()
            clues = sum(bool(value) for row in puzzle for value in row)
            self.assertGreaterEqual(clues, 24)
            self.assertEqual(count_solutions(puzzle), 1)

    def test_seed_reproduces_grids_and_links(self):
        def generate(folder):
            random.seed(99)
            first = EnhancedSudokuGenerator("E", 1, 40, 3, 1, puzzle_folder=folder)
            first_puzzle, first_solution = first.generate_linked_puzzle()
            second = EnhancedSudokuGenerator("M", 1, 36, 5, 2,
                                             previous_solution=first_solution,
                                             puzzle_folder=folder)
            second_puzzle, second_solution = second.generate_linked_puzzle()
            links = (Path(folder) / "2. M1_placeholders.txt").read_text(encoding="utf-8")
            return first_puzzle, first_solution, second_puzzle, second_solution, links

        with tempfile.TemporaryDirectory() as first_folder, tempfile.TemporaryDirectory() as second_folder:
            self.assertEqual(generate(first_folder), generate(second_folder))


if __name__ == "__main__":
    unittest.main()
