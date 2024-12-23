import argparse
from generatePuzzle import createPuzzleSet
from createBook import createSudokuBook
import os


def main():
    parser = argparse.ArgumentParser(
        description="Create a book of linked Sudoku puzzles.")
    parser.add_argument("-n", "--name", type=str, default="LEAP",
                        help="Name of the book")
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
    parser.add_argument("-ct", "--cover-text", action="store_true",
                        default=False, help="Add text in the cover page")

    args = parser.parse_args()


    # Check each mode has at least one puzzle
    if any([args.easy < 1, args.medium < 1, args.advanced < 1, args.grandmaster < 1]):
        print("Each mode must have at least one puzzle.")
        return

    # Check each mode has at least 18 hints [Minimum number of hints for a valid Sudoku puzzle]
    if any([args.easy_hints < 18, args.medium_hints < 18, args.advanced_hints < 18, args.grandmaster_hints < 18]):
        print("Each mode must have at least 18 hints.")
        return


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
        'cover': "Assets/Cover.png",
        'instructions': "Assets/Instructions.png",
        'transition': "Assets/Transition.png",
        'puzzle': "Assets/PageBackground.jpg",
        'solutions': "Assets/PageBackground.jpg"
    }
    createSudokuBook("puzzles", args.name, backgrounds, args.cover_text)

    print("Book created successfully.\n")

    if args.delete:
        print("Deleting puzzles...\n")
        import shutil
        shutil.rmtree("puzzles")
        print("Puzzles deleted successfully.\n")


if __name__ == "__main__":
    main()
