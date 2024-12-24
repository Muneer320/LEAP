from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from svglib.svglib import svg2rlg
import os
import re


class SudokuBookCreator:
    def __init__(self, output_filename="Sudoku_Book.pdf", include_cover_text=False, background_images=None):
        self.output_filename = output_filename
        self.page_width, self.page_height = A4
        self.page_margin = 50
        self.grid_size = min((self.page_width - 2 * self.page_margin),
                            (self.page_height - 4 * self.page_margin)) * 0.6
        self.include_cover_text = include_cover_text
        self.background_images = background_images if background_images else {}

    def parse_placeholder_format(self, line):
        match = re.match(r'([a-z])\s*=\s*R(\d+)C(\d+)\s*(?:\[=[0-9]\])?', line.strip())
        return (match.groups() if match else line.strip())

    def fetch_next_puzzle_placeholders(self, current_number, puzzle_dir):
        puzzle_files = sorted(os.listdir(puzzle_dir))
        current_pattern = rf"^{current_number}\.\s*([A-Z]\d+)\.svg$"

        for index, filename in enumerate(puzzle_files):
            match = re.match(current_pattern, filename)
            if match:
                current_id = match.group(1)
                letter, digit = re.match(r"([A-Z])(\d+)", current_id).groups()
                next_id = f"{letter}{int(digit) + 1}"
                next_placeholder_file = f"{current_number + 1}. {next_id}_placeholders.txt"
                placeholder_path = os.path.join(puzzle_dir, next_placeholder_file)

                if os.path.exists(placeholder_path):
                    with open(placeholder_path, 'r') as f:
                        return [self.parse_placeholder_format(line) for line in f]
        return []

    def _render_index_content(self, canvas_obj, mode_data):
        if self.background_images.get('index'):
            canvas_obj.drawImage(self.background_images['index'], 0, 0, 
                               self.page_width, self.page_height)
        
        canvas_obj.setFont("Helvetica-Bold", 28)
        canvas_obj.drawCentredString(self.page_width/2, self.page_height - 80, "Index")

        def start_new_page():
            canvas_obj.showPage()
            if self.background_images.get('index'):
                canvas_obj.drawImage(self.background_images['index'], 0, 0, self.page_width, self.page_height)
            canvas_obj.setFont("Helvetica-Bold", 28)
            canvas_obj.drawCentredString(self.page_width/2, self.page_height - 80, "Index")
            return self.page_height - 150

        y_position = self.page_height - 150
        circle_radius = 8
        circle_spacing = 25
        left_margin = self.page_margin

        for mode, data in mode_data.items():
            if not data['puzzles']:
                continue

            # Check space before writing mode title
            if y_position < 80:
                y_position = start_new_page()

            canvas_obj.setFont("Times-Bold", 16)
            mode_name = data['name']
            mode_width = canvas_obj.stringWidth(mode_name, "Times-Bold", 16)
            canvas_obj.drawString(left_margin, y_position, mode_name)
            canvas_obj.line(left_margin, y_position - 2, left_margin + mode_width, y_position - 2)
            y_position -= 30

            circles_per_row = min(10, len(data['puzzles']))
            total_width = (circles_per_row - 1) * circle_spacing
            x_start = (self.page_width - total_width) / 2
            current_x = x_start
            count = 0

            for puzzle_id in data['puzzles']:
                # Check space before drawing circles
                if y_position < 60:
                    y_position = start_new_page()
                canvas_obj.circle(current_x, y_position + circle_radius, circle_radius)
                canvas_obj.setFont("Helvetica", 8)
                canvas_obj.drawCentredString(current_x, y_position - 10, puzzle_id)

                current_x += circle_spacing
                count += 1

                if count % circles_per_row == 0 and count < len(data['puzzles']):
                    y_position -= 35
                    current_x = x_start

            y_position -= 60

    def _render_mode_transition(self, canvas_obj, mode):
        if self.background_images.get('transition'):
            canvas_obj.drawImage(self.background_images['transition'], 
                               0, 0, self.page_width, self.page_height)

        mode_info = {
            'E': ('EASY MODE', 'Perfect for beginners and warming up'),
            'M': ('MEDIUM MODE', 'Challenge yourself with intermediate techniques'),
            'A': ('ADVANCED MODE', 'Test your advanced solving strategies'),
            'G': ('GRANDMASTER MODE', 'Ultimate challenges for Sudoku masters')
        }

        title, subtitle = mode_info.get(mode, ('UNKNOWN MODE', ''))
        
        canvas_obj.setFont("Times-BoldItalic", 36)
        canvas_obj.drawCentredString(self.page_width/2, self.page_height/2 + 20, title)

        canvas_obj.setFont("Helvetica", 18)
        canvas_obj.drawCentredString(self.page_width/2, self.page_height/2 - 30, subtitle)

        canvas_obj.showPage()

    def _render_puzzle_page(self, canvas_obj, puzzle_path, puzzle_number):
        if self.background_images.get('puzzle'):
            canvas_obj.drawImage(self.background_images['puzzle'], 
                               0, 0, self.page_width, self.page_height)

        drawing = svg2rlg(puzzle_path)
        if drawing:
            scale = min(self.grid_size / drawing.width,
                       self.grid_size / drawing.height) * 1.2
            drawing.scale(scale, scale)

            x_pos = (self.page_width - drawing.width * scale) / 2
            y_pos = (self.page_height - drawing.height * scale) / 2 + 120

            renderPDF.draw(drawing, canvas_obj, x_pos, y_pos)

        placeholders = self.fetch_next_puzzle_placeholders(
            puzzle_number, os.path.dirname(puzzle_path))
        
        if placeholders:
            self._render_placeholder_table(canvas_obj, placeholders)

        puzzle_id = re.search(r'[EMAG]\d+', os.path.basename(puzzle_path)).group()
        canvas_obj.setFont("Helvetica", 12)
        canvas_obj.drawCentredString(self.page_width/2, self.page_margin, puzzle_id)

        canvas_obj.showPage()

    def _render_placeholder_table(self, canvas_obj, placeholders):
        table_height = len(placeholders) * 18 + 25
        y_start = min(self.page_height - self.page_margin - table_height, 
                     self.page_margin + 200)

        canvas_obj.setFont("Helvetica-Bold", 18)
        canvas_obj.drawCentredString(self.page_width/2, y_start + 50, "For Next Puzzle")

        column_widths = [50, 100, 100, 100]
        table_width = sum(column_widths)
        x_start = (self.page_width - table_width) / 2

        x_positions = [
            x_start + column_widths[0] / 2,
            x_start + column_widths[0] + column_widths[1] / 2,
            x_start + column_widths[0] + column_widths[1] + column_widths[2] / 2,
            x_start + sum(column_widths[:-1]) + column_widths[3] / 2
        ]

        canvas_obj.setFont("Helvetica-Bold", 12)
        canvas_obj.drawCentredString(x_positions[1], y_start, "Row")
        canvas_obj.drawCentredString(x_positions[2], y_start, "Column")
        canvas_obj.drawCentredString(x_positions[3], y_start, "Value")

        for i, placeholder in enumerate(placeholders):
            y_position = y_start - (i + 1) * 18
            letter, row, col = placeholder
            
            canvas_obj.setFont("Helvetica-Bold", 12)
            canvas_obj.drawCentredString(x_positions[0], y_position, letter.strip())
            
            canvas_obj.setFont("Helvetica", 12)
            canvas_obj.drawCentredString(x_positions[1], y_position, row)
            canvas_obj.drawCentredString(x_positions[2], y_position, col)
            canvas_obj.drawCentredString(x_positions[3], y_position, "__")

    def _render_solutions_section(self, canvas_obj, puzzle_dir):
        if self.background_images.get('transition'):
            canvas_obj.drawImage(self.background_images['transition'], 
                               0, 0, self.page_width, self.page_height)

        canvas_obj.setFont("Helvetica-Bold", 36)
        canvas_obj.drawCentredString(self.page_width/2, self.page_height/2, "SOLUTIONS")
        canvas_obj.showPage()

        solutions_per_page = 9
        rows, cols = 3, 3
        solution_width = (self.page_width - 2 * self.page_margin) / cols
        solution_height = (self.page_height - 3 * self.page_margin) / rows
        solution_size = min(solution_width, solution_height) * 0.8

        puzzle_files = sorted([f for f in os.listdir(puzzle_dir) 
                             if f.endswith('.svg') and not f.endswith('S.svg')],
                            key=lambda x: int(re.search(r'(\d+)', x).group()))

        difficulty_groups = {
            'E': {'files': [], 'name': 'Easy Mode'},
            'M': {'files': [], 'name': 'Medium Mode'},
            'A': {'files': [], 'name': 'Advanced Mode'},
            'G': {'files': [], 'name': 'Grandmaster Mode'}
        }

        for puzzle_file in puzzle_files:
            difficulty = puzzle_file[puzzle_file.find('.')+2]
            if difficulty in difficulty_groups:
                difficulty_groups[difficulty]['files'].append(puzzle_file)

        self._render_solution_pages(canvas_obj, difficulty_groups, 
                                  puzzle_dir, solutions_per_page, 
                                  solution_size, rows, cols)

    def _render_solution_pages(self, canvas_obj, difficulty_groups, puzzle_dir,
                             solutions_per_page, solution_size, rows, cols):
        solution_width = (self.page_width - 2 * self.page_margin) / cols
        solution_height = (self.page_height - 3 * self.page_margin) / rows

        for difficulty, group in difficulty_groups.items():
            if not group['files']:
                continue

            for i in range(0, len(group['files']), solutions_per_page):
                if self.background_images.get('solutions'):
                    canvas_obj.drawImage(self.background_images['solutions'], 
                                       0, 0, self.page_width, self.page_height)

                canvas_obj.setFont("Helvetica-Bold", 24)
                canvas_obj.drawCentredString(self.page_width/2, 
                                           self.page_height - self.page_margin, 
                                           group['name'])

                for j, puzzle_file in enumerate(group['files'][i:i + solutions_per_page]):
                    solution_file = puzzle_file.replace('.svg', 'S.svg')
                    solution_path = os.path.join(puzzle_dir, solution_file)

                    if os.path.exists(solution_path):
                        self._render_single_solution(canvas_obj, solution_path, 
                                                  j, rows, cols, solution_size,
                                                  solution_width, solution_height,
                                                  puzzle_file)

                canvas_obj.setFont("Helvetica", 12)
                page_num = (i // solutions_per_page) + 1
                total_pages = (len(group['files']) + solutions_per_page - 1) // solutions_per_page
                canvas_obj.drawCentredString(self.page_width/2, self.page_margin,
                                           f"{group['name']} - Page {page_num} of {total_pages}")

                canvas_obj.showPage()

    def _render_single_solution(self, canvas_obj, solution_path, position, 
                              rows, cols, solution_size, solution_width, 
                              solution_height, puzzle_file):
        drawing = svg2rlg(solution_path)
        if drawing:
            row = position // cols
            col = position % cols

            scale = min(solution_size / drawing.width,
                       solution_size / drawing.height)
            drawing.scale(scale, scale)

            cell_center_x = self.page_margin + col * solution_width + solution_width/2
            cell_center_y = self.page_height - (2*self.page_margin + 
                                              row * solution_height + solution_height/2)

            x_pos = cell_center_x - (drawing.width * scale) / 2
            y_pos = cell_center_y - (drawing.height * scale) / 2

            renderPDF.draw(drawing, canvas_obj, x_pos, y_pos)

            puzzle_id = re.search(r'[EMAG]\d+', puzzle_file).group()
            canvas_obj.setFont("Helvetica", 10)
            canvas_obj.drawCentredString(cell_center_x, y_pos - 20, f"Solution - {puzzle_id}")

    def _render_rules_section(self, canvas_obj):
        y_position = self.page_height - 180
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.drawString(self.page_margin, y_position, "Basic Sudoku Rules:")

        rules = [
            "• Fill in the 9×9 grid with numbers 1-9",
            "• Each row must contain all numbers 1-9",
            "• Each column must contain all numbers 1-9",
            "• Each 3×3 box must contain all numbers 1-9"
        ]

        canvas_obj.setFont("Helvetica", 12)
        for rule in rules:
            y_position -= 20
            canvas_obj.drawString(self.page_margin + 10, y_position, rule)

    def _render_gameplay_section(self, canvas_obj):
        gameplay_sections = [
            {"title": "How The Linked System Works:", "y_offset": -20,
            "font": ("Helvetica-Bold", 16)},
            {"title": "Step 1: Solve the First Puzzle", "y_offset": -30,
            "font": ("Helvetica-Bold", 14),
            "text": (
            "Start with Puzzle E1 - a standard Sudoku puzzle with no special rules. "
            "Solve it completely using regular Sudoku rules.")},
            {"title": "Step 2: Use the Link Table", "y_offset": -15,
            "font": ("Helvetica-Bold", 14),
            "text": (
            "Below each puzzle, you'll find a link table. It shows which numbers you need "
            "to carry forward to the next puzzle. For example:"),
            "draw_table": True},
            {"title": "Step 3: Fill in Starting Numbers", "y_offset": -15,
            "font": ("Helvetica-Bold", 14),
            "text": (
            "Look at your solution for the previous puzzle. Find the numbers in the positions "
            "specified by the link table. These numbers become your starting points in the "
            "next puzzle, replacing the letters (a, b, c, etc.).")}
        ]

        y_position = self.page_height - 280
        text_width = self.page_width - 2 * self.page_margin
        for section in gameplay_sections:
            y_position += section["y_offset"]
            canvas_obj.setFont(*section["font"])
            canvas_obj.drawString(self.page_margin, y_position, section["title"])
            if "text" in section:
                y_position -= 20
                wrapped_text = self._wrap_text(section["text"], "Helvetica", 12, text_width)
                canvas_obj.setFont("Helvetica", 12)
                for line in wrapped_text:
                    canvas_obj.drawString(self.page_margin + 10, y_position, line)
                    y_position -= 15
            if "draw_table" in section:
                y_position = self._draw_link_table(canvas_obj, y_position - 20)

    def _draw_link_table(self, canvas_obj, y_position):
        table_data = [
            ["Letter", "Row", "Column", "Value"],
            ["a", "2", "4", "__"],
            ["b", "5", "7", "__"],
            ["c", "8", "1", "__"]
        ]

        col_widths = [60, 60, 60, 60]
        row_height = 20
        x_start = self.page_margin + 50

        # Draw table
        canvas_obj.setFont("Helvetica-Bold", 10)
        for col, header in enumerate(table_data[0]):
            canvas_obj.drawString(x_start + sum(col_widths[:col]), y_position, header)

        canvas_obj.setFont("Helvetica", 10)
        for row in range(1, len(table_data)):
            y_position -= row_height
            for col, value in enumerate(table_data[row]):
                canvas_obj.drawString(
                    x_start + sum(col_widths[:col]), y_position, value)
                
        return y_position - 25

    def _render_difficulty_section(self, canvas_obj):
        y_position = self.page_height - 655
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.drawString(self.page_margin, y_position, "Difficulty Levels:")

        difficulty_levels = [
            "E: Easy Mode - Easy puzzles with more number hints and less placeholders (a, b, c, etc.)",
            "M: Medium Mode - Balanced puzzles with less number hints and more placeholders",
            "A: Advanced Mode - Complex patterns with fewer number hints and more placeholders",
            "G: Grandmaster Mode - Expert-level challenges with minimal number hints and many placeholders"
        ]

        canvas_obj.setFont("Helvetica", 12)
        for level in difficulty_levels:
            y_position -= 20
            canvas_obj.drawString(self.page_margin + 10, y_position, level)

        # Add page number
        canvas_obj.setFont("Helvetica", 12)
        canvas_obj.drawCentredString(self.page_width/2, self.page_margin, "Instructions")

    def _render_instruction_sections(self, canvas_obj):
        sections = {
            'title': {
                'text': "How to Play Linked Sudoku",
                'font': ("Helvetica-Bold", 28),
                'position': (self.page_width/2, self.page_height - 80)
            },
            'intro': {
                'text': "Welcome to Linked Sudoku! This unique puzzle book connects each puzzle to the next, "
                       "creating an engaging chain of challenges. Each solution becomes a key to unlock the next puzzle.",
                'font': ("Helvetica", 12),
                'position': (self.page_margin, self.page_height - 120)
            }
        }
        
        for type, section in sections.items():
            canvas_obj.setFont(*section['font'])
            if type == 'title':
                canvas_obj.drawCentredString(*section['position'], section['text'])
            else:
                text_obj = canvas_obj.beginText(*section['position'])
                for line in self._wrap_text(section['text'], *section['font'], 
                                          self.page_width - 2 * self.page_margin):
                    text_obj.textLine(line)
                canvas_obj.drawText(text_obj)

        self._render_rules_section(canvas_obj)
        self._render_gameplay_section(canvas_obj)
        self._render_difficulty_section(canvas_obj)

    def render_cover_page(self, canvas_obj):
        background = self.background_images.get('cover', self.background_images.get('instructions'))
        if background and os.path.exists(background):
            canvas_obj.drawImage(background, 0, 0, self.page_width, self.page_height)

        if self.include_cover_text:
            title = self.output_filename.replace(".pdf", "").replace("_", " ")
            canvas_obj.setFont("Helvetica-Bold", 36)
            canvas_obj.drawCentredString(self.page_width/2, self.page_height - 200, title)
            
            canvas_obj.setFont("Helvetica", 18)
            canvas_obj.drawCentredString(self.page_width/2, self.page_height - 250, 
                                       "Each puzzle unlocks the next challenge")

        canvas_obj.showPage()

    def render_instructions_page(self, canvas_obj):
        if self.background_images.get('instructions'):
            canvas_obj.drawImage(self.background_images['instructions'], 0, 0, 
                               self.page_width, self.page_height)

        self._render_instruction_sections(canvas_obj)
        canvas_obj.showPage()

    def _wrap_text(self, text, font_name, font_size, max_width):
        words = text.split()
        lines, current_line = [], []

        for word in words:
            current_line.append(word)
            if pdfmetrics.stringWidth(' '.join(current_line), font_name, font_size) > max_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def render_index_page(self, canvas_obj, puzzle_dir):
        puzzle_files = sorted([f for f in os.listdir(puzzle_dir) 
                             if f.endswith('.svg') and not f.endswith('S.svg')],
                            key=lambda x: int(re.search(r'(\d+)', x).group()))

        mode_data = {
            'E': {'name': 'Easy Mode', 'puzzles': []},
            'M': {'name': 'Medium Mode', 'puzzles': []},
            'A': {'name': 'Advanced Mode', 'puzzles': []},
            'G': {'name': 'Grandmaster Mode', 'puzzles': []}
        }

        for puzzle in puzzle_files:
            mode = puzzle[puzzle.find('.')+2]
            if mode in mode_data:
                mode_data[mode]['puzzles'].append(re.search(r'[EMAG]\d+', puzzle).group())

        self._render_index_content(canvas_obj, mode_data)
        canvas_obj.showPage()

    def create_book(self, puzzle_dir):
        canvas_obj = canvas.Canvas(self.output_filename, pagesize=A4)
        
        self.render_cover_page(canvas_obj)
        self.render_index_page(canvas_obj, puzzle_dir)
        self.render_instructions_page(canvas_obj)

        puzzle_files = sorted([f for f in os.listdir(puzzle_dir) 
                             if f.endswith('.svg') and not f.endswith('S.svg')],
                            key=lambda x: int(re.search(r'(\d+)', x).group()))

        current_mode = None
        for puzzle_file in puzzle_files:
            puzzle_path = os.path.join(puzzle_dir, puzzle_file)
            puzzle_number = int(re.search(r'(\d+)', puzzle_file).group())
            mode = puzzle_file[puzzle_file.find('.')+2]

            if mode != current_mode:
                self._render_mode_transition(canvas_obj, mode)
                current_mode = mode

            self._render_puzzle_page(canvas_obj, puzzle_path, puzzle_number)

        self._render_solutions_section(canvas_obj, puzzle_dir)
        canvas_obj.save()


def create_sudoku_book(puzzle_dir, output_filename="Sudoku_Book.pdf", 
                      background_images=None, include_cover_text=False):
    output_filename = output_filename.strip() if output_filename.endswith(".pdf") \
                     else f"{output_filename.strip()}.pdf"
    creator = SudokuBookCreator(output_filename, include_cover_text, background_images)
    creator.create_book(puzzle_dir)