from core.exceptions import DatabaseExistsException, DatabaseNotFoundException, TableExistsException, TableNotFoundException
from core.query import AXQL


def launch_shell():
    axql = AXQL()
    command = ""
    while True:
        try:
            command_prefix = "axql"
            prefix = "axql"
            if axql.current_db != None:
                command_prefix = "axql.current_db"
                prefix = axql.current_db.dbname

                if axql.current_db.alteration_table != None:
                    alteration_table_text = "axql.current_db.alteration_table"
                    command_prefix = f"axql.current_db.tables[{alteration_table_text}]"
                    prefix = f"{prefix}>{axql.current_db.alteration_table}"

            if command != "exit":
                command = input(f"{prefix} -> ")
    
            if command == "exit":
                command = ""
                if axql.current_db==None:
                    print("\n\nGood bye :)")
                    break

                elif axql.current_db.alteration_table!=None:
                    axql.current_db.end_alter()

                else:
                    print(f"\nQuit database {axql.current_db.dbname} !!")
                    axql.current_db=None

            else:
                eval(f"{command_prefix}.{command}")

        # except SyntaxError:
        #     print(f"\nError: Syntax error")

        except TypeError:
            print(f"\nError: Type error !!")
        
        except ValueError:
            print(f"\nError: Values error !!")

        except PermissionError:
            print(f"\nError: Permission denied")

        except DatabaseNotFoundException:
            print(f"\nError: database not found!!")
        
        except DatabaseExistsException:
            print(f"\nError: database already exists!!")

        except TableNotFoundException:
            print(f"\nError: table does not exists!!")
        
        except TableExistsException:
            print(f"\nError: table already exists!!")

        # except AttributeError:
        #     print(f"\nError: invalid function!!")


        # Exit with Ctrl + D
        except EOFError:
            command ="exit"

        # Interrupt with Ctrl + C
        except KeyboardInterrupt:
            print("\nError: shell interrupted!!")
            break

if __name__ == "__main__":
    launch_shell()