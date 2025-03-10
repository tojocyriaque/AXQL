import os,shutil
import genericpath as path
from core.config import ROOT_DIR
from core.exceptions import DatabaseExistsException, DatabaseNotFoundException
from core.storage.database import DataBase


class AXQL:
    def __init__(self, dbname:str=None):
        self.current_db: DataBase = DataBase(dbname) if dbname != None else None

    def create_database(self, dbname:str):
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