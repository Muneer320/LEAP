import argparse
from generatePuzzle import create_puzzle_set
import os


def main():
    parser = argparse.ArgumentParser(
        description="Create a book of linked Sudoku puzzles.")
    parser.add_argument("-e", "--easy", type=int, default=15,
                        help="Number of easy mode puzzles to generate")
    parser.add_argument("-m", "--medium", type=int, default=10,
                        help="Number of medium mode puzzles to generate")
    parser.add_argument("-a", "--advanced", type=int, default=5,
                        help="Number of advanced mode puzzles to generate")
    parser.add_argument("-g", "--grandmaster", type=int, default=3,
                        help="Number of grandmaster mode puzzles to generate")
    parser.add_argument("-d", "--delete", action="store_true",
                        default=False, help="Delete puzzles after making the book")
    parser.add_argument("-eh", "--easy_hints", type=int,
                        default=40, help="Number of hints for easy mode puzzles")
    parser.add_argument("-mh", "--medium_hints", type=int,
                        default=36, help="Number of hints for medium mode puzzles")
    parser.add_argument("-hh", "--hard_hints", type=int,
                        default=27, help="Number of hints for hard mode puzzles")
    parser.add_argument("-gh", "--grandmaster_hints", type=int,
                        default=18, help="Number of hints for grandmaster mode puzzles")

    args = parser.parse_args()

    # Placeholders Count
    easy_placeholders = 3
    medium_placeholders = 5
    advanced_placeholders = 7
    grandmaster_placeholders = 9

    # Create necessary directories
    os.makedirs("puzzles", exist_ok=True)

    global_counter = 1

    if args.easy > 0:
        create_puzzle_set('E', args.easy, args.easy_hints,
                          easy_placeholders, start_number=1, global_start=global_counter)
        global_counter += args.easy

    if args.medium > 0:
        create_puzzle_set('M', args.medium, args.medium_hints,
                          medium_placeholders, start_number=1, global_start=global_counter)
        global_counter += args.medium

    if args.advanced > 0:
        create_puzzle_set('A', args.advanced, args.hard_hints,
                          advanced_placeholders, start_number=1, global_start=global_counter)
        global_counter += args.advanced

    if args.grandmaster > 0:
        create_puzzle_set('G', args.grandmaster, args.grandmaster_hints,
                          grandmaster_placeholders, start_number=1, global_start=global_counter)

    if args.delete:
        # Implementation for cleanup...
        pass


if __name__ == "__main__":
    main()
