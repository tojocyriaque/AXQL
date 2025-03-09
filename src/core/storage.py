from collections import defaultdict
import json, os
from core.config import ROOT_DIR
from core.exceptions import TableAttributeExistsException, TableAttributeNotFoundException, TableExistsException, TableNotFoundException
from core.entities.table import TableAttribute

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

        # for alter table
        self.alteration_table = None
        self.alter_action = None

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
            
            self.tables[table_name] = Table(self, table_name, attr_list)
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

        self.tables[tablename] = Table(self, tablename, attributes)
        self.tables[tablename].create(attributes) # create the table
        
        self.add_table_metadata(tablename)
        self.update_metadata_file() # updating the metadata.json file

    def drop_table(self, tablename:str):
        table_filepath = f"{self.dbpath}/{tablename}.tabl"
        try:
            # remove the table name in the db table_keys
            self.tables.pop(tablename)

            self.remove_table_metadata(tablename)
            self.update_metadata_file()
            os.remove(table_filepath)

        except KeyError:
            # table does not exists
            raise TableNotFoundException(f"Table {tablename} does not exist!!")

    def alter_table(self, tablename:str):
        if tablename not in self.tables.keys():
            raise TableNotFoundException(f"Table {tablename} does not exists !!")

        self.alteration_table = tablename
    
    def end_alter(self):
        self.update_table_metadata(self.alteration_table)
        self.update_metadata_file()
        print(f"\nAltered table {self.alteration_table} !")
        self.alteration_table = None

"""
Handing tables
"""
class Table:
    def __init__(self, database:DataBase, tablename:str, attributes=[]):
        self.tablename = tablename
        self.attributes:dict[str, TableAttribute] = {}
        self.db = database
        self.file = None
        self.filepath = f"{ROOT_DIR}/{self.db.dbname}/{self.tablename}.tbl"

    def create(self, attributes):
        self.file = open(self.filepath, "a") # create the table file if it does not exist
        self.setup(attributes)

    def setup(self, attributes:list):
        for attr in attributes:
            attr_name, *props = attr
            self.attributes[attr_name] = TableAttribute(*attr)

        self.file = open(self.filepath, "r") # read the file

    def add_attributes(self, *attributes):
        self.db.alter_action
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