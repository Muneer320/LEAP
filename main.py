import argparse
from generatePuzzle import createPuzzleSet
from createBook import createSudokuBook
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
    parser.add_argument("-ah", "--advanced_hints", type=int,
                        default=27, help="Number of hints for advanced mode puzzles")
    parser.add_argument("-gh", "--grandmaster_hints", type=int,
                        default=18, help="Number of hints for grandmaster mode puzzles")

    args = parser.parse_args()


    print("Starting LEAP...\n\n")

    # Placeholders Count
    easy_placeholders = 3
    medium_placeholders = 5
    advanced_placeholders = 7
    grandmaster_placeholders = 9


    print("Generating puzzles...\n")

    # Create necessary directories
    os.makedirs("puzzles", exist_ok=True)

    global_counter = 1


    if args.easy > 0:
        createPuzzleSet('E', args.easy, args.easy_hints,
                        easy_placeholders, start_number=1, global_start=global_counter)
        global_counter += args.easy

    if args.medium > 0:
        createPuzzleSet('M', args.medium, args.medium_hints,
                        medium_placeholders, start_number=1, global_start=global_counter)
        global_counter += args.medium

    if args.advanced > 0:
        createPuzzleSet('A', args.advanced, args.advanced_hints,
                        advanced_placeholders, start_number=1, global_start=global_counter)
        global_counter += args.advanced

    if args.grandmaster > 0:
        createPuzzleSet('G', args.grandmaster, args.grandmaster_hints,
                        grandmaster_placeholders, start_number=1, global_start=global_counter)

    print("All puzzles generated successfully.\n")

    print("Creating book...\n")
    # Make the book
    backgrounds = {
        'cover': "Assets/Background.png",
        'instructions': "Assets/Background.png",
        'puzzle': "Assets/pageBackground.png",
        'solutions': "Assets/pageBackground.png"
    }
    createSudokuBook("puzzles", "Linked_Sudoku_Puzzles.pdf", backgrounds)

    print("Book created successfully.\n")

    if args.delete:
        print("Deleting puzzles...\n")
        import shutil
        shutil.rmtree("puzzles")
        print("Puzzles deleted successfully.\n")


if __name__ == "__main__":
    main()
