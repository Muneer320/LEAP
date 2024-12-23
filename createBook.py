from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
from svglib.svglib import svg2rlg
import os
import re


class SudokuBookCreator:
    def __init__(self, output_filename="Sudoku_Book.pdf"):
        self.output_filename = output_filename
        self.width, self.height = A4
        self.margin = 50
        # Reduced puzzle size to 60% of previous size
        self.puzzle_size = min((self.width - 2 * self.margin),
                               (self.height - 4 * self.margin)) * 0.6

    def format_placeholder(self, line):
        """Format placeholder text from R1C2 format to readable format."""
        match = re.match(
            r'([a-z])\s*=\s*R(\d+)C(\d+)\s*(?:\[=[0-9]\])?', line.strip())
        if match:
            letter, row, col = match.groups()
            # return f"{letter} = Row {row} Column {col}"
            return letter, row, col
        return line.strip()

    def get_next_puzzle_placeholders(self, current_puzzle_number, puzzles_folder):
        """Get placeholder information for the next puzzle."""
        # List and sort all relevant files in the directory
        puzzle_files = sorted(os.listdir(puzzles_folder))

        # Build the current puzzle pattern to match the filename
        current_pattern = rf"^{current_puzzle_number}\.\s*([A-Z]\d+)\.svg$"

        for index, filename in enumerate(puzzle_files):
            match = re.match(current_pattern, filename)
            if match:
                # Extract the puzzle identifier (e.g., "E2")
                current_identifier = match.group(1)

                # Determine the next puzzle identifier (increment the digit)
                letter, digit = re.match(
                    r"([A-Z])(\d+)", current_identifier).groups()
                next_identifier = f"{letter}{int(digit) + 1}"

                # Construct the placeholder filename for the next puzzle
                next_placeholder_file = f"{
                    current_puzzle_number + 1}. {next_identifier}_placeholders.txt"
                placeholder_path = os.path.join(
                    puzzles_folder, next_placeholder_file)

                if os.path.exists(placeholder_path):
                    # Read and format the placeholder file
                    with open(placeholder_path, 'r') as f:
                        return [self.format_placeholder(line) for line in f]

        return []

    def create_cover_page(self, c, cover_background=None):
        """Create an attractive cover page for the puzzle book."""
        if cover_background and os.path.exists(cover_background):
            c.drawImage(cover_background, 0, 0, self.width, self.height)

        c.setFont("Helvetica-Bold", 36)
        title = "Linked Sudoku Puzzles"
        c.drawCentredString(self.width/2, self.height - 200, title)

        c.setFont("Helvetica", 18)
        subtitle = "Each puzzle unlocks the next challenge"
        c.drawCentredString(self.width/2, self.height - 250, subtitle)

        c.showPage()

    def create_instructions_page(self, c, instructions_background=None):
        """Create a comprehensive instructions page with examples."""
        if instructions_background and os.path.exists(instructions_background):
            c.drawImage(instructions_background, 0, 0, self.width, self.height)

        # Title
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(self.width/2, self.height - 80,
                            "How to Play Linked Sudoku")

        # Introduction
        c.setFont("Helvetica", 12)
        intro_text = (
            "Welcome to Linked Sudoku! This unique puzzle book connects each puzzle to the next, "
            "creating an engaging chain of challenges. Each solution becomes a key to unlock the next puzzle."
        )
        text_width = self.width - (2 * self.margin)
        text_object = c.beginText(self.margin, self.height - 120)
        text_object.setFont("Helvetica", 12)
        wrapped_text = self._wrap_text(intro_text, "Helvetica", 12, text_width)
        for line in wrapped_text:
            text_object.textLine(line)
        c.drawText(text_object)

        # Basic Rules Section
        y_position = self.height - 180
        c.setFont("Helvetica-Bold", 16)
        c.drawString(self.margin, y_position, "Basic Sudoku Rules:")

        basic_rules = [
            "• Fill in the 9×9 grid with numbers 1-9",
            "• Each row must contain all numbers 1-9",
            "• Each column must contain all numbers 1-9",
            "• Each 3×3 box must contain all numbers 1-9"
        ]

        c.setFont("Helvetica", 12)
        for rule in basic_rules:
            y_position -= 20
            c.drawString(self.margin + 10, y_position, rule)

        # Linked Puzzle System
        y_position -= 40
        c.setFont("Helvetica-Bold", 16)
        c.drawString(self.margin, y_position, "How The Linked System Works:")

        y_position -= 30
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, y_position, "Step 1: Solve the First Puzzle")

        y_position -= 20
        c.setFont("Helvetica", 12)
        step1_text = (
            "Start with Puzzle E1 - a standard Sudoku puzzle with no special rules. "
            "Solve it completely using regular Sudoku rules."
        )
        wrapped_text = self._wrap_text(step1_text, "Helvetica", 12, text_width)
        for line in wrapped_text:
            c.drawString(self.margin + 10, y_position, line)
            y_position -= 15

        y_position -= 15
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, y_position, "Step 2: Use the Link Table")

        y_position -= 20
        c.setFont("Helvetica", 12)
        step2_text = (
            "Below each puzzle, you'll find a link table. It shows which numbers you need "
            "to carry forward to the next puzzle. For example:"
        )
        wrapped_text = self._wrap_text(step2_text, "Helvetica", 12, text_width)
        for line in wrapped_text:
            c.drawString(self.margin + 10, y_position, line)
            y_position -= 15

        # Example Table
        y_position -= 20
        table_data = [
            ["Letter", "Row", "Column", "Value"],
            ["a", "2", "4", "__"],
            ["b", "5", "7", "__"],
            ["c", "8", "1", "__"]
        ]

        col_widths = [60, 60, 60, 60]
        row_height = 20
        x_start = self.margin + 50

        # Draw table
        c.setFont("Helvetica-Bold", 10)
        for col, header in enumerate(table_data[0]):
            c.drawString(x_start + sum(col_widths[:col]), y_position, header)

        c.setFont("Helvetica", 10)
        for row in range(1, len(table_data)):
            y_position -= row_height
            for col, value in enumerate(table_data[row]):
                c.drawString(
                    x_start + sum(col_widths[:col]), y_position, value)

        y_position -= 40
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, y_position,
                     "Step 3: Fill in Starting Numbers")

        y_position -= 20
        c.setFont("Helvetica", 12)
        step3_text = (
            "Look at your solution for the previous puzzle. Find the numbers in the positions "
            "specified by the link table. These numbers become your starting points in the "
            "next puzzle, replacing the letters (a, b, c, etc.)."
        )
        wrapped_text = self._wrap_text(step3_text, "Helvetica", 12, text_width)
        for line in wrapped_text:
            c.drawString(self.margin + 10, y_position, line)
            y_position -= 15

        # Difficulty Levels
        y_position -= 25
        c.setFont("Helvetica-Bold", 16)
        c.drawString(self.margin, y_position, "Difficulty Levels:")

        difficulty_levels = [
            "E: Easy Mode - Easy puzzles with more number hints and less placeholders (a, b, c, etc.)",
            "M: Medium Mode - Balanced puzzles with less number hints and more placeholders",
            "A: Advanced Mode - Complex patterns with fewer number hints and more placeholders",
            "G: Grandmaster Mode - Expert-level challenges with minimal number hints and many placeholders"
        ]

        c.setFont("Helvetica", 12)
        for level in difficulty_levels:
            y_position -= 20
            c.drawString(self.margin + 10, y_position, level)

        # Add page number
        c.setFont("Helvetica", 12)
        c.drawCentredString(self.width/2, self.margin, "Instructions")

        c.showPage()

    def _wrap_text(self, text, font_name, font_size, max_width):
        """Helper method to wrap text to fit within a specified width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            line_width = pdfmetrics.stringWidth(
                ' '.join(current_line), font_name, font_size)
            if line_width > max_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def create_mode_transition_page(self, c, mode, background=None):
        """Create a transition page for a new mode."""
        if background and os.path.exists(background):
            c.drawImage(background, 0, 0, self.width, self.height)

        # Mode titles with descriptions
        mode_info = {
            'E': {
                'title': 'EASY MODE',
                'subtitle': 'Perfect for beginners and warming up'
            },
            'M': {
                'title': 'MEDIUM MODE',
                'subtitle': 'Challenge yourself with intermediate techniques'
            },
            'A': {
                'title': 'ADVANCED MODE',
                'subtitle': 'Test your advanced solving strategies'
            },
            'G': {
                'title': 'GRANDMASTER MODE',
                'subtitle': 'Ultimate challenges for Sudoku masters'
            }
        }

        # Draw main title
        title = mode_info[mode]['title']
        subtitle = mode_info[mode]['subtitle']

        # Draw title
        # c.setFont("Times-Italic", 36)
        c.setFont("Times-BoldItalic", 36)
        c.drawCentredString(self.width/2, self.height/2 + 20, title)

        # Draw subtitle
        c.setFont("Helvetica", 18)
        c.drawCentredString(self.width/2, self.height/2 - 30, subtitle)

        c.showPage()

    def add_puzzle_page(self, c, svg_path, puzzle_number, puzzle_background=None):
        """Add a puzzle page with proper formatting and metadata."""
        if puzzle_background and os.path.exists(puzzle_background):
            c.drawImage(puzzle_background, 0, 0, self.width, self.height)

        # Add the puzzle SVG
        drawing = svg2rlg(svg_path)
        if drawing:
            # Calculate scaling to fit the reduced size while maintaining aspect ratio
            scale = min(
                self.puzzle_size / drawing.width,
                self.puzzle_size / drawing.height
            ) * 1.2   # Increased scale slightly
            drawing.scale(scale, scale)

            # Center the drawing on the page
            x_pos = (self.width - drawing.width * scale) / 2
            y_pos = (self.height - drawing.height * scale) / \
                2 + 120  # Moved up slightly

            renderPDF.draw(drawing, c, x_pos, y_pos)

        # Add placeholder information for the next puzzle
        # Add placeholder information for the next puzzle
        placeholders = self.get_next_puzzle_placeholders(
            puzzle_number, os.path.dirname(svg_path))
        if placeholders:
            # Calculate the initial Y position based on the number of rows
            # Total height needed for table including header
            table_height = len(placeholders) * 18 + 25
            y_start = min(self.height - self.margin -
                          table_height, self.margin + 200)

            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(self.width / 2, y_start +
                                50, "For Next Puzzle")

            # Calculate table width and center it
            # Widths for Row, Column, Value
            column_widths = [50, 100, 100, 100]
            table_width = sum(column_widths)
            x_start = (self.width - table_width) / 2

            # Set column positions relative to the centered start
            x_positions = [
                x_start + column_widths[0] / 2,  # Center of first column
                # Center of second column
                x_start + column_widths[0] + column_widths[1] / 2,
                x_start + column_widths[0] + column_widths[1] + \
                column_widths[2] / 2,  # Center of third column
                # Center of fourth column
                x_start + column_widths[0] + column_widths[1] + \
                column_widths[2] + column_widths[3] / 2,
            ]

            c.setFont("Helvetica-Bold", 12)

            # Add table header
            c.drawCentredString(x_positions[1], y_start, "Row")
            c.drawCentredString(x_positions[2], y_start, "Column")
            c.drawCentredString(x_positions[3], y_start, "Value")

            # Add table data
            for i, placeholder in enumerate(placeholders):
                y_position = y_start - (i + 1) * 18
                letter, row, col = placeholder
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(x_positions[0], y_position, letter.strip())
                c.setFont("Helvetica", 12)
                c.drawCentredString(x_positions[1], y_position, row)
                c.drawCentredString(x_positions[2], y_position, col)
                c.drawCentredString(x_positions[3], y_position, "__")

        # Get puzzle identifier from filename (e.g., "E1" from "2. E1.svg")
        puzzle_id = re.search(r'[EMAG]\d+', os.path.basename(svg_path)).group()

        # Add page number at bottom
        c.setFont("Helvetica", 12)
        c.drawCentredString(self.width/2, self.margin, puzzle_id)

        c.showPage()

    def add_solutions_section(self, c, puzzles_folder, solutions_background=None):
        """Add the solutions section with solutions arranged in a 3x3 grid, grouped by difficulty."""
        # Solutions cover page
        if solutions_background and os.path.exists(solutions_background):
            c.drawImage(solutions_background, 0, 0, self.width, self.height)

        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(self.width/2, self.height/2, "SOLUTIONS")
        c.showPage()

        # Get all puzzle files and sort them
        puzzle_files = [f for f in os.listdir(puzzles_folder)
                        if f.endswith('.svg') and not f.endswith('S.svg')]
        puzzle_files.sort(key=lambda x: int(re.search(r'(\d+)', x).group()))

        # Group puzzles by difficulty
        difficulty_groups = {
            'E': {'files': [], 'name': 'Easy Mode'},
            'M': {'files': [], 'name': 'Medium Mode'},
            'A': {'files': [], 'name': 'Advanced Mode'},
            'G': {'files': [], 'name': 'Grandmaster Mode'}
        }

        for puzzle_file in puzzle_files:
            # Get E/M/A/G from filename
            difficulty = puzzle_file[puzzle_file.find('.')+2]
            if difficulty in difficulty_groups:
                difficulty_groups[difficulty]['files'].append(puzzle_file)

        # Calculate grid layout parameters
        solutions_per_page = 9
        rows, cols = 3, 3

        # Calculate individual solution size (reduced to fit 9 per page)
        solution_width = (self.width - 2 * self.margin) / cols
        solution_height = (self.height - 3 * self.margin) / \
            rows  # Extra margin for title
        solution_size = min(solution_width, solution_height) * \
            0.8  # 80% of available space

        # Process solutions by difficulty
        for difficulty, group in difficulty_groups.items():
            puzzle_files = group['files']

            # Skip if no puzzles for this difficulty
            if not puzzle_files:
                continue

            # Process solutions in groups of 9
            for i in range(0, len(puzzle_files), solutions_per_page):
                if solutions_background and os.path.exists(solutions_background):
                    c.drawImage(solutions_background, 0,
                                0, self.width, self.height)

                # Add difficulty mode title at the top
                c.setFont("Helvetica-Bold", 24)
                c.drawCentredString(
                    self.width/2, self.height - self.margin, group['name'])

                # Process each solution in the current group
                for j, puzzle_file in enumerate(puzzle_files[i:i + solutions_per_page]):
                    row = j // cols
                    col = j % cols

                    solution_file = puzzle_file.replace('.svg', 'S.svg')
                    solution_path = os.path.join(puzzles_folder, solution_file)

                    if os.path.exists(solution_path):
                        drawing = svg2rlg(solution_path)
                        if drawing:
                            # Calculate position for this solution
                            scale = min(
                                solution_size / drawing.width,
                                solution_size / drawing.height
                            )
                            drawing.scale(scale, scale)

                            # Calculate centered position within grid cell
                            cell_center_x = self.margin + col * solution_width + solution_width/2
                            cell_center_y = self.height - \
                                (2*self.margin + row *
                                 solution_height + solution_height/2)

                            x_pos = cell_center_x - (drawing.width * scale) / 2
                            y_pos = cell_center_y - \
                                (drawing.height * scale) / 2

                            renderPDF.draw(drawing, c, x_pos, y_pos)

                            # Add solution ID below each solution
                            puzzle_id = re.search(
                                r'[EMAG]\d+', puzzle_file).group()
                            c.setFont("Helvetica", 10)
                            c.drawCentredString(cell_center_x,
                                                y_pos - 20,  # Position below the solution
                                                f"Solution - {puzzle_id}")

                # Add page number
                c.setFont("Helvetica", 12)
                page_num = (i // solutions_per_page) + 1
                total_pages = (len(puzzle_files) +
                               solutions_per_page - 1) // solutions_per_page
                c.drawCentredString(self.width/2, self.margin,
                                    f"{group['name']} - Page {page_num} of {total_pages}")

                c.showPage()

    def create_book(self, puzzles_folder, backgrounds=None):
        """Create the complete puzzle book with transition pages for modes."""
        if backgrounds is None:
            backgrounds = {}

        c = canvas.Canvas(self.output_filename, pagesize=A4)

        # Create cover and instructions with their specific backgrounds
        self.create_cover_page(c, backgrounds.get('cover'))
        self.create_instructions_page(c, backgrounds.get('instructions'))

        # Sort puzzle files numerically and group by mode
        puzzle_files = [f for f in os.listdir(puzzles_folder)
                        if f.endswith('.svg') and not f.endswith('S.svg')]
        puzzle_files.sort(key=lambda x: int(re.search(r'(\d+)', x).group()))

        # Track the current mode to know when to insert transition pages
        current_mode = None

        # Add puzzle pages with mode transitions
        for puzzle_file in puzzle_files:
            puzzle_path = os.path.join(puzzles_folder, puzzle_file)
            puzzle_number = int(re.search(r'(\d+)', puzzle_file).group())

            # Extract mode from filename (E/M/A/G)
            mode = puzzle_file[puzzle_file.find('.')+2]

            # If mode changes or it's the first puzzle, add transition page
            if mode != current_mode:
                self.create_mode_transition_page(
                    c, mode, backgrounds.get('puzzle'))
                current_mode = mode

            self.add_puzzle_page(
                c, puzzle_path, puzzle_number, backgrounds.get('puzzle'))

        # Add solutions section with its background
        solutions_background = backgrounds.get('solutions')
        if solutions_background and os.path.exists(solutions_background):
            c.drawImage(solutions_background, 0, 0, self.width, self.height)

        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(self.width/2, self.height/2, "SOLUTIONS")
        c.showPage()

        self.add_solutions_section(
            c, puzzles_folder, backgrounds.get('solutions'))

        c.save()


def createSudokuBook(puzzles_folder, output_filename="Sudoku_Book.pdf", backgrounds=None):
    """
    Main function to create the Sudoku book.
    backgrounds: dict with keys 'cover', 'instructions', 'puzzle', 'solutions'
    containing paths to background images for each section
    """
    creator = SudokuBookCreator(output_filename)
    creator.create_book(puzzles_folder, backgrounds)


if __name__ == "__main__":
    backgrounds = {
        'cover': "Assets/Background.png",
        'instructions': "Assets/Background.png",
        'puzzle': "Assets/pageBackground.png",
        'solutions': "Assets/pageBackground.png"
    }
    createSudokuBook("puzzles", "Linked_Sudoku_Puzzles.pdf", backgrounds)
