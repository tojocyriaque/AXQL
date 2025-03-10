import os,shutil
import genericpath as path
from config import ROOT_DIR
from core.exceptions import DatabaseExistsException, DatabaseNotFoundException
from core.storage.database import DataBase

class AXQL:
    def __init__(self, dbname:str=None):
        self.current_db: DataBase = DataBase(dbname) if dbname != None else None

    def show_databases(self):
        # ANSI escape codes for colors and styles
        RESET = "\033[0m"
        BOLD = "\033[1m"
        CYAN = "\033[36m"
        YELLOW = "\033[33m"
        MAGENTA = "\033[35m"
        GREEN = "\033[32m"
        
        # Helper function to strip ANSI escape sequences.
        import re
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        def strip_ansi(text):
            return ansi_escape.sub('', text)
        

        headers = ["Database", "Owner"]
        headers = [f"{YELLOW}{BOLD}{header}{RESET}" for header in headers]
        
        rows = []
        for db_name in os.listdir(ROOT_DIR):
            db = DataBase(db_name)
            rows.append([f"{GREEN}{db_name}{RESET}",
                         db.owner])

        col_widths = []
        for i, header in enumerate(headers):
            max_width = max(
                len(strip_ansi(header)), 
                *map(
                    lambda row:len(strip_ansi(row[i])), 
                    rows))
            col_widths.append(max_width)
        
        # Build border lines using Unicode box-drawing characters
        top_line = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        sep_line = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        bottom_line = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
        
        # Build the header row with proper padding
        header_cells = []
        for i, cell in enumerate(headers):
            visible = strip_ansi(cell)
            pad = col_widths[i] - len(visible)
            header_cells.append(cell + " " * pad)
        header_row = "│ " + " │ ".join(header_cells) + " │"
        
        # Print the overview table
        print(top_line)
        print(header_row)
        print(sep_line)
        
        for row in rows:
            row_cells = []
            for i, cell in enumerate(row):
                visible = strip_ansi(cell)
                pad = col_widths[i] - len(visible)
                row_cells.append(cell + " " * pad)
            row_line = "│ " + " │ ".join(row_cells) + " │"
            print(row_line)
        
        print(bottom_line)
        
    def create_database(self, dbname:str, owner:str="axql_admin"):
        dbpath = f"{ROOT_DIR}/{dbname}"

        if path.exists(dbpath):
            raise DatabaseExistsException(f"Database {dbname} already exists")

        else:
            os.mkdir(dbpath)
            open(f"{dbpath}/metadata.json", "a")
            
    def use_database(self, dbname:str):
        dbpath = f"{ROOT_DIR}/{dbname}"
        if path.exists(dbpath):
            self.current_db = DataBase(dbname)
        else:
            raise DatabaseNotFoundException(f"Database {dbname} does not exists")

    def quit_current_db(self):
        self.current_db = None

    def drop_database(self, dbname:str):
        # Drop the files
        dbpath = f"{ROOT_DIR}/{dbname}"

        if path.exists(dbpath):
            shutil.rmtree(dbpath)
        else:
            raise DatabaseNotFoundException(f"Database {dbname} does not exists")