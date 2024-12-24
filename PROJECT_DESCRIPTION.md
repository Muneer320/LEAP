# LEAP project description

LEAP generates printable books of linked Sudoku puzzles. The first puzzle can be solved on its own. Each later puzzle replaces some given digits with letters. The previous puzzle's solution supplies the value of each letter through row and column coordinates printed in a link table.

## Generation

1. Generate a filled 9×9 Sudoku grid.
2. Remove clues one at a time, keeping a removal only when the remaining grid has one solution. The requested hint count is a target; uniqueness takes priority.
3. For linked pages, choose distinct digit values to display as letters. Check that treating those letters as unknown leaves at least two solutions. This is the dependency check.
4. Pick coordinates from the previous solution that contain those digit values. The link table on the previous page gives the reader those coordinates.
5. Render puzzle and solution SVGs, then assemble the PDF with a cover, index, instructions, tier dividers, puzzle pages, and solutions.

The chain continues when a new difficulty tier begins. The first puzzle in the book has no link, even if the book starts at a later tier.

## Scope and limits

- Sudoku uniqueness is verified after letter values are known. Without those values, linked pages are deliberately ambiguous. This establishes a dependency on the previous solution; it does not prove that every reader would need to solve that page to infer the values.
- Easy, medium, advanced, and grandmaster specify clue targets and the number of letter values. They are not ratings of human solving difficulty.
- A book is rendered through intermediate SVGs and text link tables. Those files are kept by default for inspection and can be removed with `-d`.
- Python 3.12 or newer is required. A fixed `--seed` reproduces puzzle and link choices.

See [README.md](README.md) for setup and options.
