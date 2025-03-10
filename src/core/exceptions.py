"""
Database errors
"""
class DatabaseNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class DatabaseExistsException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
    
"""
Table errors
"""
class TableNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class TableExistsException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


"""
Table attributes errors
"""
class TableAttributeNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class TableAttributeExistsException(Exception):
    def __init__(self, *args):
        super().__init__(*args)