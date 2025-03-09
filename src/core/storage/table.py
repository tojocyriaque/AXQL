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