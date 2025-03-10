""""
This file contains every functions that can be usefull
for the code even if this is not directly an important part
"""
 
# Listing values in table with headers
# and colorfull things
def table_view(headers:list[str], rows:list[str], higlight_first_col=False):
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    GREEN = "\033[32m"
    
    import re
    # Helper function to strip ANSI escape sequences.
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    def strip_ansi(text):
        return ansi_escape.sub('', text)

    headers = [f'{YELLOW}{BOLD}{header}{RESET}' for header in headers]
    
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(strip_ansi(header))
        for row in rows:
            cell = f"{row[i]}"
            cell_len = len(strip_ansi(cell))
            max_width = max(cell_len, max_width)   
             
        col_widths.append(max_width)
    
    # Build border lines using Unicode box-drawing characters
    top_line = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    sep_line = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    bottom_line = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
    
    print(top_line)
    # Print header row
    header_cells = []
    for i, cell in enumerate(headers):
        visible = strip_ansi(cell)
        pad = col_widths[i] - len(visible)
        header_cells.append(cell + " " * pad)
    header_row = "│ " + " │ ".join(header_cells) + " │"
    print(header_row)
    print(sep_line)
    
    # Print each row
    for row in rows:
        if higlight_first_col:
            row[0] = f"{BOLD}{GREEN}{row[0]}{RESET}"
            
        row_cells = []
        for i, c in enumerate(row):
            cell = f"{c}"
            visible = strip_ansi(cell)
            pad = col_widths[i] - len(visible)
            row_cells.append(cell + " " * pad)
        row_line = "│ " + " │ ".join(row_cells) + " │"
        print(row_line)
        
    print(bottom_line)