import argparse
from generatePuzzle import createPuzzleSet
from createBook import create_sudoku_book
import shutil
import random
import uuid
from pathlib import Path


def remove_run_directory(puzzle_dir, puzzle_root):
    """Remove only this invocation's generated directory."""
    target = puzzle_dir.resolve()
    if target.parent != puzzle_root.resolve() or not target.name.startswith("run-"):
        raise ValueError("Refusing to remove a directory outside the puzzle run")
    shutil.rmtree(target)


def validate_arguments(args):
    counts = [args.easy, args.medium, args.advanced, args.grandmaster]
    if any(count < 0 for count in counts) or sum(counts) == 0:
        raise ValueError("Puzzle counts must be nonnegative, with at least one puzzle overall.")
    
    if any(not 24 <= hints <= 81 for hints in [args.easy_hints, args.medium_hints,
                                               args.advanced_hints, args.grandmaster_hints]):
        raise ValueError("Requested hints must be between 24 and 81.")


def generate_puzzle_sets(args, puzzle_dir):
    difficulty_configs = {
        'E': (args.easy, args.easy_hints, 3),
        'M': (args.medium, args.medium_hints, 5),
        'A': (args.advanced, args.advanced_hints, 7),
        'G': (args.grandmaster, args.grandmaster_hints, 9)
    }

    global_counter = 1
    previous_solution = None
    links = {}
    for mode, (count, hints, placeholders) in difficulty_configs.items():
        if count > 0:
            previous_solution = createPuzzleSet(
                mode, count, hints, placeholders,
                start_number=1, global_start=global_counter,
                previous_solution=previous_solution,
                puzzle_folder=puzzle_dir,
                links=links,
            )
            global_counter += count
    return links


def main(argv=None):
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
        ("-gh", "--grandmaster-hints", 27, "Number of hints for grandmaster mode")
    ]
    
    for short_opt, long_opt, default, help_text in difficulty_args:
        parser.add_argument(short_opt, long_opt, type=int, default=default, help=help_text)
    
    for short_opt, long_opt, default, help_text in hint_args:
        parser.add_argument(short_opt, long_opt, type=int, default=default, help=help_text)
    
    parser.add_argument("-d", "--delete", action="store_true", default=False,
                       help="Delete puzzles after book creation")
    parser.add_argument("-ct", "--cover-text", action="store_true", default=False,
                       help="Add text in the cover page")
    parser.add_argument("--seed", type=int, help="Reproduce a generated book")

    args = parser.parse_args(argv)

    try:
        print("\nInitializing LEAP puzzle book generation...\n")
        
        validate_arguments(args)
        if args.seed is not None:
            random.seed(args.seed)
        puzzle_root = Path.cwd() / "puzzles"
        puzzle_root.mkdir(exist_ok=True)
        if puzzle_root.resolve().parent != Path.cwd().resolve():
            raise ValueError("Puzzle directory must be inside the current directory")
        puzzle_dir = puzzle_root / f"run-{uuid.uuid4().hex[:12]}"
        puzzle_dir.mkdir(parents=True)
        
        print("Generating puzzle sets...")
        links = generate_puzzle_sets(args, str(puzzle_dir))
        print("Puzzle generation completed successfully.\n")
        
        print("Creating puzzle book...")
        assets = Path(__file__).resolve().parent / "Assets"
        background_images = {
            'cover': str(assets / "Cover.png"),
            'index': str(assets / "Index.png"),
            'instructions': str(assets / "Instructions.png"),
            'transition': str(assets / "Transition.png"),
            'puzzle': str(assets / "PageBackground.jpg"),
            'solutions': str(assets / "PageBackground.jpg")
        }
        
        create_sudoku_book(str(puzzle_dir), args.name, background_images,
                           args.cover_text, links_by_number=links)
        print("Book creation completed successfully.\n")
        
        if args.delete:
            print("Cleaning up temporary files...")
            remove_run_directory(puzzle_dir, puzzle_root)
            print("Cleanup completed successfully.\n")
            
        print("Process completed successfully!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if 'puzzle_dir' in locals() and puzzle_dir.exists():
            remove_run_directory(puzzle_dir, puzzle_root)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
