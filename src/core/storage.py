import json, os
from core.config import ROOT_DIR

class DataBase:
    def __init__(self, dbname:str):
        self.dirpath:str
        self.dbname = dbname
        self.dbpath = f"{ROOT_DIR}/{dbname}"
        self.table_stoarage: TableStorage

    def create_table(self, tablename:str, attributes=[]):
        # handling the table file
        open(f"{self.dbpath}/{tablename}.tabl", "ab")

        # handling the metadata file
        with open(f"{self.dbpath}/metadata.json", "r") as metadata_file:
            metadata = {}
            try:
                metadata = json.load(metadata_file)
                metadata[tablename] = {}
            except:
                metadata = {tablename:{}}

        for attr_name, attr_type, max_size in attributes:
            metadata[tablename][attr_name] = {"type": attr_type, "max_size": max_size}
        
        with open(f"{self.dbpath}/metadata.json", "w") as metadata_file:
            json.dump(metadata, fp=metadata_file)

    def drop_table(self, tablename=""):
        pass

    def alter_table(self, tablename="", new_attributes=[]):
        pass

class TableStorage:
    def __init__(self, tablename:str=None, filepath:str=None):
        self.filepath = filepath
        self.tablename = tablename

    def write_record(self):
        pass
      
    def read_record(self):
        pass

    def delete_record(self):
        pass