import json, os
from core.config import ROOT_DIR
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