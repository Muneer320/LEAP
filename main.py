import argparse
from generatePuzzle import createPuzzleSet
from createBook import create_sudoku_book
import os
import shutil


def validate_arguments(args):
    if any(count < 1 for count in [args.easy, args.medium, args.advanced, args.grandmaster]):
        raise ValueError("Each difficulty mode must have at least one puzzle.")
    
    if any(hints < 18 for hints in [args.easy_hints, args.medium_hints, 
                                   args.advanced_hints, args.grandmaster_hints]):
        raise ValueError("Each mode must have at least 18 hints for puzzle validity.")


def generate_puzzle_sets(args):
    difficulty_configs = {
        'E': (args.easy, args.easy_hints, 3),
        'M': (args.medium, args.medium_hints, 5),
        'A': (args.advanced, args.advanced_hints, 7),
        'G': (args.grandmaster, args.grandmaster_hints, 9)
    }

    global_counter = 1
    for mode, (count, hints, placeholders) in difficulty_configs.items():
        if count > 0:
            createPuzzleSet(mode, count, hints, placeholders, 
                          start_number=1, global_start=global_counter)
            global_counter += count


def main():
    parser = argparse.ArgumentParser(description="Create a book of linked Sudoku puzzles.")
    
    parser.add_argument("-n", "--name", type=str, default="LEAP",
                       help="Name of the book")
    
    difficulty_args = [
        ("-e", "--easy", 15, "Number of easy mode puzzles"),
        ("-m", "--medium", 10, "Number of medium mode puzzles"),
        ("-a", "--advanced", 5, "Number of advanced mode puzzles"),
        ("-g", "--grandmaster", 3, "Number of grandmaster mode puzzles")
    ]
    
    hint_args = [
        ("-eh", "--easy-hints", 40, "Number of hints for easy mode"),
        ("-mh", "--medium-hints", 36, "Number of hints for medium mode"),
        ("-ah", "--advanced-hints", 27, "Number of hints for advanced mode"),
        ("-gh", "--grandmaster-hints", 18, "Number of hints for grandmaster mode")
    ]
    
    for short_opt, long_opt, default, help_text in difficulty_args:
        parser.add_argument(short_opt, long_opt, type=int, default=default, help=help_text)
    
    for short_opt, long_opt, default, help_text in hint_args:
        parser.add_argument(short_opt, long_opt, type=int, default=default, help=help_text)
    
    parser.add_argument("-d", "--delete", action="store_true", default=False,
                       help="Delete puzzles after book creation")
    parser.add_argument("-ct", "--cover-text", action="store_true", default=False,
                       help="Add text in the cover page")

    args = parser.parse_args()

    try:
        print("\nInitializing LEAP puzzle book generation...\n")
        
        validate_arguments(args)
        os.makedirs("puzzles", exist_ok=True)
        
        print("Generating puzzle sets...")
        generate_puzzle_sets(args)
        print("Puzzle generation completed successfully.\n")
        
        print("Creating puzzle book...")
        background_images = {
            'cover': "Assets/Cover.png",
            'index': "Assets/Index.png",
            'instructions': "Assets/Instructions.png",
            'transition': "Assets/Transition.png",
            'puzzle': "Assets/PageBackground.jpg",
            'solutions': "Assets/PageBackground.jpg"
        }
        
        create_sudoku_book("puzzles", args.name, background_images, args.cover_text)
        print("Book creation completed successfully.\n")
        
        if args.delete:
            print("Cleaning up temporary files...")
            shutil.rmtree("puzzles")
            print("Cleanup completed successfully.\n")
            
        print("Process completed successfully!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        shutil.rmtree("puzzles", ignore_errors=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())