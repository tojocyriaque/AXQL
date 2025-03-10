import json, os
from config import ROOT_DIR
from core.exceptions import TableExistsException, TableNotFoundException
from core.storage.table import Table


"""
Handling databases
"""
class DataBase:
    def __init__(self, dbname:str):
        self.dbname = dbname
        self.dbpath = f"{ROOT_DIR}/{dbname}"

        self.metadata_path = f'{self.dbpath}/metadata.json'

        self.tables:dict[str: Table] = {}
        
        self.metadata:dict[str, dict[str, dict]] = {}
        self.metadata_file = None

        # using table
        self.cli_table = None

        self.load_metadata()
        self.load_tables()

    ## Metadata handling 
    def load_metadata(self):
        try:
            self.metadata_file = open(self.metadata_path, "r")
            self.metadata = json.load(self.metadata_file)
            
        except FileNotFoundError:
            raise Exception(f"Metadata file not found for database {self.dbname} !!")
        
        except PermissionError:
            raise Exception(f"Bad permission for metadata.json !!")
        
        except json.decoder.JSONDecodeError:
            pass
            # raise Exception(f"Bad json format for the metadata!!")
        
    # load tables from the metadata
    def load_tables(self):
        for table_name, attributes in self.metadata.items():
            attr_list =  [ (attr_name, *attribute.values())
                           for attr_name, attribute in attributes.items()]
            
            self.tables[table_name] = Table(self.dbname, table_name, attr_list)
            self.tables[table_name].setup(attr_list)

    # adding new table to the metadata
    def add_table_metadata(self, tablename:str):
        self.metadata[tablename] = self.tables[tablename].description()

    # remove table to the metadata
    def remove_table_metadata(self, tablename:str):
        self.metadata.pop(tablename)

    # update table structure in the metadata
    def update_table_metadata(self, tablename:str):
        self.metadata[tablename] = self.tables[tablename].description()

    def update_metadata_file(self):
        try:
            with open(self.metadata_path, "w") as mf:
                json.dump(self.metadata, mf)
        except:
            raise Exception("Failed to update metadata!!")


    # Tables handling
    def create_table(self, tablename:str, *attributes):
        if tablename in self.metadata:
            raise TableExistsException(f"Table {tablename} exists !!")

        self.tables[tablename] = Table(self.dbname, tablename, attributes)
        self.tables[tablename].create(attributes) # create the table
        
        self.add_table_metadata(tablename)
        self.update_metadata_file() # updating the metadata.json file

    def drop_table(self, tablename:str):
        table_filepath = f"{self.dbpath}/{tablename}.tbl"
        try:
            # remove the table name in the db table_keys
            self.tables.pop(tablename)

            self.remove_table_metadata(tablename)
            self.update_metadata_file()
            os.remove(table_filepath)

        except KeyError:
            # table does not exists
            raise TableNotFoundException(f"Table {tablename} does not exist!!")

    def select_table(self, tablename:str):
        if tablename not in self.tables.keys():
            raise TableNotFoundException(f"Table {tablename} does not exists !!")
        
        self.cli_table = tablename

    def quit_table(self):
        self.cli_table = None

    def cancel_alter(self):
        print(f"\nCancel alteration of table {self.cli_table} !")
        self.alter_table = None

    def accept_alter(self):
        self.update_table_metadata(self.cli_table)
        self.update_metadata_file()
        print(f"\nAltered table {self.cli_table} !")


    def describe(self):
        """
        Prints a colorful description of the database,
        listing each table and a summary of its columns,
        with proper padding despite ANSI escape codes.
        """
        import re
        # Helper function to strip ANSI escape sequences.
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        def strip_ansi(text):
            return ansi_escape.sub('', text)

        # ANSI escape codes for colors and styles
        RESET = "\033[0m"
        BOLD = "\033[1m"
        CYAN = "\033[36m"
        YELLOW = "\033[33m"
        MAGENTA = "\033[35m"
        GREEN = "\033[32m"
        
        # Build the header for the database
        header_text = f" Database: {self.dbname} "
        header = f"{BOLD}{CYAN}{header_text}{RESET}"
        visible_header = strip_ansi(header)
        border = "─" * len(visible_header)
        print(f"┌{border}┐")
        print(f"│{header}│")
        print(f"└{border}┘\n")
        
        # If no tables exist, notify the user.
        if not self.tables:
            print(f"{MAGENTA}No tables found in this database.{RESET}")
            return

        # Define headers for the overview table
        overview_headers = [f"{BOLD}{YELLOW}Table{RESET}", 
                            f"{BOLD}{YELLOW}Columns{RESET}", 
                            f"{BOLD}{YELLOW}Description{RESET}"]
        rows = []

        # Create a row for each table
        for table_name, table in self.tables.items():
            # List columns as a comma-separated string
            columns = ", ".join(table.attributes.keys())
            # Create a description: for each column, show "column:type"
            description = ", ".join(f"{col}:{table.attributes[col].dtype}" for col in table.attributes)
            rows.append([f"{GREEN}{table_name}{RESET}", columns, description])
        
        # Compute column widths based on visible lengths (ignoring ANSI codes)
        col_widths = []
        for i in range(len(overview_headers)):
            max_width = len(strip_ansi(overview_headers[i]))
            for row in rows:
                cell_len = len(strip_ansi(row[i]))
                if cell_len > max_width:
                    max_width = cell_len
            col_widths.append(max_width)
        
        # Build border lines using Unicode box-drawing characters
        top_line = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        sep_line = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        bottom_line = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
        
        # Build the header row with proper padding
        header_cells = []
        for i, cell in enumerate(overview_headers):
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
