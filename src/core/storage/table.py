import struct
from config import ROOT_DIR
from core.exceptions import TableAttributeExistsException, TableAttributeNotFoundException
from core.entities.table import TableAttribute
import re

def verify(value, conditions:list, all=False):
    for condition in conditions:
        v_type = type(condition)
        if v_type != str: # match if equal
            to_ev = f'{value}=={condition}'
            ev = eval(to_ev)
        elif type(value)==str: # value and condition are both str (this should be regex)
            to_ev = f'"{value}"=="{condition}"'
            ev = eval(to_ev)

        else: # condition is str and value is not
            # example value = 8 and condition = "<4"
            ev = eval(f'{value}{condition}')
            
        if ev==True and all==False:
            return True
        
        if ev==False and all==True:
            return False

    return True
    


"""
Handing tables
"""
class Table:
    def __init__(self, dbname:str, tablename:str, attributes=[]):
        self.tablename = tablename
        self.attributes:dict[str, TableAttribute] = {}
        self.dbname = dbname
        self.file = None
        self.filepath = f"{ROOT_DIR}/{self.dbname}/{self.tablename}.tbl"

    # CLI things
    def describe(self):
        """
        Prints a nicely formatted description of the table's schema.
        """
        RESET = "\033[0m"
        BOLD = "\033[1m"
        CYAN = "\033[36m"
        YELLOW = "\033[33m"
        MAGENTA = "\033[35m"
        GREEN = "\033[32m"

        # Helper function to strip ANSI escape sequences.
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        def strip_ansi(text):
            return ansi_escape.sub('', text)

        # Define the header labels
        headers = ["Column", "Type", "Min Size", "Max Size", "Default", "Constraint"]
        headers = [f"{BOLD}{YELLOW}{header}{RESET}" for header in headers]
        # Build rows from each attribute
        rows = []
        for attr_name, attr in self.attributes.items():
            rows.append([
                f"{GREEN}{attr_name}{RESET}",
                attr.dtype,
                str(attr.min_size),
                str(attr.max_size),
                str(attr.default) if attr.default is not None else "",
                str(attr.constraint) if attr.constraint is not None else ""
            ])
        
        # Compute column widths based on header and row values
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(strip_ansi(header))
            for row in rows:
                cell_len = len(strip_ansi(row[i]))
                if cell_len > max_width:
                    max_width = cell_len
            col_widths.append(max_width)
        
        # Build border lines using Unicode box-drawing characters
        top_line = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        sep_line = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        bottom_line = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
        
        # Print a header for the table description
        print(f"\nTable: {self.tablename}\n")
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
            row_cells = []
            for i, cell in enumerate(row):
                visible = strip_ansi(cell)
                pad = col_widths[i] - len(visible)
                row_cells.append(cell + " " * pad)
            row_line = "│ " + " │ ".join(row_cells) + " │"
            print(row_line)
            
        print(bottom_line)
    
    def create(self, attributes):
        self.file = open(self.filepath, "a") # create the table file if it does not exist
        self.setup(attributes)

    def setup(self, attributes:list):
        for attr in attributes:
            attr_name, *props = attr
            self.attributes[attr_name] = TableAttribute(*attr)

        self.file = open(self.filepath, "r") # read the file

    def add_attributes(self, *attributes):
        for attr in attributes:
            attr_name, *props = attr

            if attr_name in self.attributes.keys():
                raise TableAttributeExistsException("Attribute exists !!")
            
            self.attributes[attr_name] = TableAttribute(*attr)

    def remove_attribute(self, attr_name:str):
        if attr_name not in self.attributes.keys():
            raise TableAttributeNotFoundException(f"No attribute {attr_name} !!")
        
        self.attributes.pop(attr_name)
    
    def modify_attribute(self, attr_name:str, new_attr:tuple):
        if attr_name not in self.attributes.keys():
            raise TableAttributeNotFoundException(f"No attribute {attr_name} !!")
        
        new_name, *props = new_attr
        # same attribute
        if new_name == attr_name:
            self.attributes[attr_name] = TableAttribute(*new_attr)
        # different name (replace the attribute)
        else:
            self.remove_attribute(attr_name)
            self.add_attributes(new_attr)

    def description(self):
        return {
            name:attr.properties()
            for name,attr in self.attributes.items()
        }
    
    
    # Record handling
    def insert_values(self, **kwargs):
        """
        Writing record following the structure of the table in order
        """
        record_bytes = b""
        for attr in self.attributes:
            if attr not in kwargs:
                default_value = self.attributes[attr].default
                if default_value is not None:
                    kwargs[attr] = default_value
                else:
                    raise Exception(f"Missing attribute {attr} !!")
                
            if attr not in self.attributes:
                raise Exception(f"Table {self.tablename} has no attribute {attr} !!")

            dtype = self.attributes[attr].dtype
            value = kwargs[attr]
            match dtype:
                case "int":
                    packed = struct.pack("<B I", 1, value)  # Type 1 = int

                case "float":
                    packed = struct.pack("<B f", 2, value)  # Type 2 = float

                case "str":
                    value = value.encode("utf-8")
                    packed = struct.pack(f"<B I {len(value)}s ", 3, len(value), value)  # Type 3 = str

                case _:
                    pass

            record_bytes += packed
        
        with open(self.filepath, "ab") as tablefile:
            tablefile.write(record_bytes)

    # Reading records
    def select(self, **where):
        records = []
        with open(self.filepath, "rb") as tablefile:
            while True:
                record = {}
                match_conditions = True
                for attr in self.attributes:
                    dtype_code_bytes = tablefile.read(1)
                    
                    if not dtype_code_bytes: # end of file
                        return
                
                    dtype_code = struct.unpack("<B", dtype_code_bytes)[0]
                    match dtype_code:
                        case 1: # int
                            data = tablefile.read(4) # int size is 4
                            value = struct.unpack("<I", data)[0]

                        case 2: # float
                            data = tablefile.read(4) # float size is 4
                            value = struct.unpack("<f", data)[0]

                        case 3: # str
                            strlen_bytes = tablefile.read(4)
                            strlen = struct.unpack("<I", strlen_bytes)[0]

                            data = tablefile.read(strlen)
                            value = struct.unpack(f"<{strlen}s", data)[0].decode("utf-8")

                        case _:
                            pass
                    
                    record[attr] = value
                    
                    # Handling the where clause
                    if attr in where:
                        conditions = where[attr]
                        condition_type = type(conditions).__name__
                        
                        # print(f"Condition type on {attr}:", condition_type)
                        condition_verified = True
                        match condition_type:
                            case "tuple": # AND
                                condition_verified = verify(value, list(conditions), all=True)

                            case "list": # OR
                                condition_verified = verify(value, conditions, all=False)

                            case "str": # maybe regular expression
                                condition_verified = re.match(pattern=conditions, string=value)

                            case _: # numerical value (for now) check if equal
                                condition_verified = (value==conditions)

                        if not condition_verified: # some conditions not verified
                            match_conditions = False
                    

                if match_conditions:
                    print(record)
                    records.append(record)

        return records