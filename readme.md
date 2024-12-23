# 🎮 LEAP - Linked Enigmas And Puzzles

Ever wished Sudoku puzzles were more... connected? ~~<sub>Me neighter</sub>~~ Well, **LEAP** is exactly that - a Sudoku book generator that creates puzzles that are linked together like a chain of mathematical DNA. 🧬

## 🧩 What's This All About?

*LEAP* is the spiritual successor to [**BOOP (Book of Organized Puzzles)**](https://github.com/Muneer320/BOOP), trading word searches for Sudoku with a twist. While BOOP organized random words into themed word searches, LEAP creates Sudoku puzzles where each one holds the key to solving the next. It's like a puzzle inception! 🌀

### The Secret Sauce 🤫

- First puzzle: Regular Sudoku (boring, I know)
- Following puzzles: Sudoku + secret placeholders (a, b, c...)
- To solve puzzle #2, you need the solution from puzzle #1
- The more advanced the mode, the more placeholders you get (because I'm evil like that)

## 🚀 Quick Start

```bash
python main.py -n "My_Awesome_Sudoku_Book"
```

That's it! Your book will be ready faster than you can say "what's a nonogram?"

### Feeling Fancy? Try These Arguments:

```bash
python main.py \
  -n "SUPER_SUDOKU" \
  -e 15    # Easy puzzles (for beginners)
  -m 10    # Medium puzzles (for coffee breaks)
  -a 5     # Advanced puzzles (for lunch breaks)
  -g 3     # Grandmaster puzzles (for quitting your job)
  -ct      # Add text over your cover (because why not?)
```

## 📋 Requirements

- Python 3.x
- A love for puzzles
- Coffee (optional but recommended)

## 📦 Installation

1. Clone this repo
2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Create puzzles:

```bash
python main.py
```

## 🎨 Features

- 4 difficulty modes (Easy to "Why am I doing this to myself?")
- Automated puzzle generation
- Professional PDF output with:
  - Cover page
  - Index
  - Instructions
  - Mode transition pages
  - Solutions (for cheaters)

## ⚙️ Customization

Adjust these arguments to make your perfect puzzle book:

| Argument          |      Description      | Default |
| :---------------- | :-------------------: | :-----: |
| -n, --name        |       Book name       | "LEAP"  |
| -e, --easy        |     Easy puzzles      |   15    |
| -m, --medium      |    Medium puzzles     |   10    |
| -a, --advanced    |   Advanced puzzles    |    5    |
| -g, --grandmaster |  Grandmaster puzzles  |    3    |
| -eh, --easy_hints |    Easy mode hints    |   40    |
| -ct, --cover-text |    Add cover text     |  False  |
| -d, --delete      | Delete puzzles folder |  Fasle  |

## 🎯 Pro Tips

1. Start with easy mode (trust me)
2. Each puzzle takes ~30 seconds to solve (or hours if you're like me)
3. Solutions are at the back (no judging ~~<sup>cheater</sup>~~)

## 🤝 Contributing

Found a bug? Want to add more evil features? PRs welcome!

## 📜 License

[MIT (Make It Tougher) License](LICENSE)

## 🙏 Acknowledgments

Special thanks to [**BOOP**](https://github.com/Muneer320/BOOP) for paving the way and to coffee for making this possible. Also Claude for bug fixes.

---

Remember: In LEAP, skipping puzzles is not just cheating - it's impossible! 😈
<sup>Unless you're a grandmaster, which you aren't you f...</sup>

_"Life is like a Sudoku puzzle - sometimes you need to go back to move forward."_ - Ancient Puzzle Proverb (probably)
