# LEAP — Linked Enigmas And Puzzles

LEAP makes printable Sudoku books where each puzzle after the first borrows a few values from the previous puzzle's solution. Solve one grid, use the coordinates in its link table to decode the letters in the next, and continue through the book. The chain carries across difficulty tiers.

It started as a follow-up to [BOOP](https://github.com/Muneer320/BOOP), this time with Sudoku and a link between pages.

## Try it

Use Python 3.12 or newer. The code uses modern f-strings and needs the packages in `requirements.txt`.

```bash
python -m pip install -r requirements.txt
python main.py -e 2 -m 1 -a 0 -g 0 --seed 42 -n My_Sudoku_Book -d
```

This writes `My_Sudoku_Book.pdf` in the current directory. The `--seed` flag reproduces the puzzles and link values. Without `-d`, LEAP keeps the intermediate SVGs and link tables in a new `puzzles/run-*` directory. Each run gets its own directory, so an earlier run is not mixed into a later book. With `-d`, LEAP removes only that run's intermediates after the PDF is made.

[A two-puzzle sample book](examples/Linked_Sudoku_Puzzles.pdf) is included.

## How the link works

The first page is an ordinary Sudoku. On the next page, some given digits are shown as letters. A link table on the previous page tells you which row and column of its completed solution supplies each letter's value. The same letter represents the same digit everywhere in its puzzle.

For each generated puzzle, LEAP checks that the grid has exactly one Sudoku solution after those values are supplied. It also checks that hiding the letters leaves more than one solution. The second check makes the previous solution useful for resolving the next puzzle. It does not measure how hard a puzzle feels to a human solver.

Clues are removed only while the numeric puzzle stays unique. A requested hint count is a target: if more clues cannot be removed without losing uniqueness, LEAP keeps the extra clues. The PDF includes solutions at the back.

## Options

| Option | Meaning | Default |
|---|---|---:|
| `-n`, `--name` | PDF filename | `LEAP` |
| `-e`, `--easy` | Easy puzzles | 15 |
| `-m`, `--medium` | Medium puzzles | 10 |
| `-a`, `--advanced` | Advanced puzzles | 5 |
| `-g`, `--grandmaster` | Grandmaster puzzles | 3 |
| `-eh`, `--easy-hints` | Easy clue target | 40 |
| `-mh`, `--medium-hints` | Medium clue target | 36 |
| `-ah`, `--advanced-hints` | Advanced clue target | 27 |
| `-gh`, `--grandmaster-hints` | Grandmaster clue target | 27 |
| `--seed` | Repeat the same puzzles and links | Random |
| `-ct`, `--cover-text` | Print the title on the cover | Off |
| `-d`, `--delete` | Remove this run's intermediate files | Off |

Set any tier count to zero to skip it. At least one puzzle is required. Hint targets must be from 24 to 81; the generator may retain more than requested. Grandmaster pages use more letters than easy pages, but the program does not provide a formal difficulty rating.

## Project files

- `generatePuzzle.py` creates Sudoku grids, verifies uniqueness, chooses links, and renders SVGs.
- `createBook.py` arranges the SVGs, tables, backgrounds, and solutions in a PDF.
- `main.py` handles arguments and runs the book generator.
- `Assets/` contains the page artwork.
- [PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md) explains the design and limits.

Run the chain checks with `python -m unittest discover -s tests -v`.

## License

[MIT](LICENSE)
