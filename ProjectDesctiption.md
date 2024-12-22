# LEAP - Linked Enigmas And Puzzles

## Project Overview
A unique puzzle book concept where each Sudoku puzzle is linked to the previous one, creating a chain of interconnected challenges. Solvers must complete each puzzle in sequence to obtain information needed for the next puzzle.

## How It Works

### Basic Concept
1. The first puzzle is a standard Sudoku with normal number hints
2. Subsequent puzzles contain both numbers and placeholder letters (a, b, c, etc.)
3. Each puzzle includes instructions for converting the placeholder letters using positions from the previous puzzle's solution
4. Solving each puzzle provides the information needed to begin the next one

### Example Sequence

#### Puzzle 1 (Page 1)
```
Standard Sudoku puzzle with regular number hints
5 _ 4 | _ 8 _ | _ 2 _
_ 8 _ | 2 _ 4 | _ _ _
...

Instructions for next puzzle:
a = number in Row 3, Column 5
b = number in Row 7, Column 2
```

#### Puzzle 2 (Page 2)
```
Partially filled Sudoku with placeholders
_ a 3 | _ _ _ | _ _ 3
_ 7 _ | 1 b _ | 4 _ _
...
```

### Features

#### Progressive Difficulty
- Initial puzzles use fewer placeholders (2-3)
- Later puzzles may increase placeholder count (3-4)
- Core puzzle difficulty also increases gradually

#### Error Prevention
1. Solutions will be provided at the back of the book, organized by page number
2. Each puzzle designed to have a unique solution
3. Minimal placeholders per puzzle to reduce complexity
4. Visual validation possible through Sudoku's standard rules

#### Page Layout
- One puzzle per page
- Clear grid layout with ample space
- Dedicated area for placeholder instructions
- Optional mini-grid for tracking letter-to-number mappings

## Technical Requirements

### Puzzle Generation
1. Minimum of 25-30 given numbers per puzzle to ensure unique solutions
2. Placeholders positioned in different 3x3 boxes for easier solving
3. Valid Sudoku rules maintained even with placeholders
4. Each puzzle solution verified for uniqueness

### Book Structure
1. Cover Page
2. Introduction and Rules
3. Index Page
4. Puzzle Pages (one per page)
5. Solution Section
   - Complete solutions for all puzzles
   - Organized by page number
   - Clearly formatted for easy reference

## Example Puzzle Chain

### Example: First Three Puzzles

#### Puzzle 1:
```
5 3 4 | 6 8 1 | 7 2 9
6 8 1 | 2 7 4 | 3 5 8
...

(Regular Sudoku with ~30 given numbers)
Instructions:
a = number in Row 4, Column 6 (= 3)
b = number in Row 8, Column 3 (= 7)
```

#### Puzzle 2:
```
5 a 4 | 6 8 1 | 7 2 9
6 8 1 | 2 b 4 | 3 5 8
...

Instructions:
a = number in Row 1, Column 8 (= 5)
b = number in Row 3, Column 1 (= 1)
c = number in Row 5, Column 4 (= 7)
```

#### Puzzle 3:
```
a 3 _ | _ 8 d | _ 2 _
_ 8 _ | _ _ 4 | _ _ _
...

Instructions:
a = number in Row 1, Column 1 (= 5)
b = number in Row 2, Column 7 (= 4)
c = number in Row 4, Column 6 (= 9)
```

## Implementation Notes

1. Book Generation
   - Automated puzzle generation with difficulty scaling
   - Verification of unique solutions
   - Placeholder position optimization
   - Solution validation

2. Quality Control
   - Test solving of complete chains
   - Verification of instruction clarity
   - Difficulty progression testing
   - Error propagation checks

3. User Experience
   - Clear instructions
   - Consistent formatting
   - Adequate solving space
   - Easy-to-reference solutions

## Future Enhancements
- Multiple difficulty levels
- Alternative puzzle types (Kakuro, etc.)
- Digital companion app for validation
- Achievement system for completing chains