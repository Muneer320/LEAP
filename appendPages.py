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
                letter, digit = re.match(r"([A-Z])(\d+)", current_identifier).groups()
                next_identifier = f"{letter}{int(digit) + 1}"
                
                # Construct the placeholder filename for the next puzzle
                next_placeholder_file = f"{current_puzzle_number + 1}. {next_identifier}_placeholders.txt"
                placeholder_path = os.path.join(puzzles_folder, next_placeholder_file)
                
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
        """Create an instructions page explaining linked puzzles."""
        if instructions_background and os.path.exists(instructions_background):
            c.drawImage(instructions_background, 0, 0, self.width, self.height)

        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(self.width/2, self.height - 100, "How to Play")

        instructions = [
            "1. Start with Puzzle 1 - a regular Sudoku puzzle.",
            "2. Solve the puzzle completely.",
            "3. Notice the letter placeholders (a, b, c, etc.) in the next puzzle.",
            "4. Use your solution from the previous puzzle to find the values",
            "   for these placeholders.",
            "5. Continue solving puzzles to unlock more challenges!"
        ]

        c.setFont("Helvetica", 14)
        y_position = self.height - 150
        for line in instructions:
            y_position -= 30
            c.drawString(self.margin + 20, y_position, line)

        # Add page number
        c.setFont("Helvetica", 12)
        c.drawCentredString(self.width/2, self.margin, "Instructions")

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
            y_pos = (self.height - drawing.height * scale) / 2 + 120  # Moved up slightly

            renderPDF.draw(drawing, c, x_pos, y_pos)

        # Add placeholder information for the next puzzle
        # Add placeholder information for the next puzzle
        placeholders = self.get_next_puzzle_placeholders(puzzle_number, os.path.dirname(svg_path))
        if placeholders:
            # Calculate the initial Y position based on the number of rows
            table_height = len(placeholders) * 18 + 25  # Total height needed for table including header
            y_start = min(self.height - self.margin - table_height, self.margin + 200)

            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(self.width / 2, y_start + 50, "For Next Puzzle")

            # Calculate table width and center it
            column_widths = [50, 100, 100, 100]  # Widths for Row, Column, Value
            table_width = sum(column_widths)
            x_start = (self.width - table_width) / 2

            # Set column positions relative to the centered start
            x_positions = [
                x_start + column_widths[0] / 2,  # Center of first column
                x_start + column_widths[0] + column_widths[1] / 2,  # Center of second column
                x_start + column_widths[0] + column_widths[1] + column_widths[2] / 2,  # Center of third column
                x_start + column_widths[0] + column_widths[1] + column_widths[2] + column_widths[3] / 2,  # Center of fourth column
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
        """Add the solutions section with proper formatting."""
        # Solutions cover page
        if solutions_background and os.path.exists(solutions_background):
            c.drawImage(solutions_background, 0, 0, self.width, self.height)

        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(self.width/2, self.height/2, "SOLUTIONS")
        c.showPage()

        # Add individual solution pages
        puzzle_files = [f for f in os.listdir(puzzles_folder)
                        if f.endswith('.svg') and not f.endswith('S.svg')]
        puzzle_files.sort(key=lambda x: int(re.search(r'(\d+)', x).group()))

        for puzzle_file in puzzle_files:
            if solutions_background and os.path.exists(solutions_background):
                c.drawImage(solutions_background, 0,
                            0, self.width, self.height)

            solution_file = puzzle_file.replace('.svg', 'S.svg')
            solution_path = os.path.join(puzzles_folder, solution_file)

            if os.path.exists(solution_path):
                drawing = svg2rlg(solution_path)
                if drawing:
                    scale = min(
                        self.puzzle_size / drawing.width,
                        self.puzzle_size / drawing.height
                    )
                    drawing.scale(scale, scale)
                    x_pos = (self.width - drawing.width * scale) / 2
                    y_pos = (self.height - drawing.height * scale) / 2
                    renderPDF.draw(drawing, c, x_pos, y_pos)

                # Add solution page number
                puzzle_id = re.search(r'[EMAG]\d+', puzzle_file).group()
                c.setFont("Helvetica", 12)
                c.drawCentredString(self.width/2, self.margin,
                                    f"Solution - {puzzle_id}")

                c.showPage()

    def create_book(self, puzzles_folder, backgrounds=None):
        """Create the complete puzzle book with different backgrounds for different sections."""
        if backgrounds is None:
            backgrounds = {}

        c = canvas.Canvas(self.output_filename, pagesize=A4)

        # Create cover and instructions with their specific backgrounds
        self.create_cover_page(c, backgrounds.get('cover'))
        self.create_instructions_page(c, backgrounds.get('instructions'))

        # Sort puzzle files numerically
        puzzle_files = [f for f in os.listdir(puzzles_folder)
                        if f.endswith('.svg') and not f.endswith('S.svg')]
        puzzle_files.sort(key=lambda x: int(re.search(r'(\d+)', x).group()))

        # Add puzzle pages
        for puzzle_file in puzzle_files:
            puzzle_path = os.path.join(puzzles_folder, puzzle_file)
            puzzle_number = int(re.search(r'(\d+)', puzzle_file).group())
            self.add_puzzle_page(
                c, puzzle_path, puzzle_number, backgrounds.get('puzzle'))

        # Add solutions section with its background
        self.add_solutions_section(
            c, puzzles_folder, backgrounds.get('solutions'))

        c.save()


def create_sudoku_book(puzzles_folder, output_filename="Sudoku_Book.pdf", backgrounds=None):
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
    create_sudoku_book("puzzles", "Linked_Sudoku_Puzzles.pdf", backgrounds)
