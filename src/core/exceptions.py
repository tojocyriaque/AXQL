class DatabaseNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class DatabaseExistsException(Exception):
    def __init__(self, *args):
        super().__init__(*args)