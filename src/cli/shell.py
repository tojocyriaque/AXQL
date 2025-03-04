from core.exceptions import DatabaseNotFoundException
from core.query import AXQL

def launch_shell():
    axql = AXQL()
    while True:
        try:
            command_prefix = "axql" if axql.current_db==None else "axql.current_db"
            prefix = "axql" if axql.current_db==None else axql.current_db.dbname
            command = input(f"{prefix}> ")

            if command == "exit":
                print("\n\nGood bye :)")
                break

            eval(f"{command_prefix}.{command}")

        except DatabaseNotFoundException:
            print(f"\nError: database not found!!")

        except AttributeError:
            print(f"\nError: invalid function!!")

        except KeyboardInterrupt:
            print("\nError: shell interrupted!!")
            break

if __name__ == "__main__":
    launch_shell()