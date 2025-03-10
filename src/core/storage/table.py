import struct
from core.config import ROOT_DIR
from core.exceptions import TableAttributeExistsException, TableAttributeNotFoundException
from core.entities.table import TableAttribute

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
    def select(self, where=("*")):
        matched = False
        if "*" in where:
            matched = True

        with open(self.filepath, "rb") as tablefile:
            while True:
                record = {}
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

                print(record)