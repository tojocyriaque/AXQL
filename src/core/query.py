import os
import genericpath as path
from core.config import ROOT_DIR
from core.exceptions import DatabaseExistsException, DatabaseNotFoundException
from core.storage import DataBase

class AXQL:
    def __init__(self, dbname:str=None):
        self.current_db: DataBase = DataBase(dbname) if dbname != None else None

    def create_database(self, dbname:str):
        dbpath = f"{ROOT_DIR}/{dbname}"

        if path.exists(dbpath):
            raise DatabaseExistsException(f"Database {dbname} already exists")

        else:
            os.mkdir(f"{ROOT_DIR}/{dbname}")
            open(f"{dbpath}/metadata.json", "a")
            
    def use_database(self, dbname:str):
        if path.exists(f"{ROOT_DIR}/{dbname}"):
            self.current_db = DataBase(dbname)
        else:
            raise DatabaseNotFoundException(f"Database {dbname} does not exists")


    def drop_database(self, dbname:str):
        # Drop the files
        dbpath = f"{ROOT_DIR}/{dbname}"

        if path.exists(dbpath):
            os.remove(dbpath)
        else:
            raise DatabaseNotFoundException(f"Database {dbname} does not exists")