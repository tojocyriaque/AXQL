from core.exceptions import (
    DatabaseExistsException, DatabaseNotFoundException, 
    TableExistsException, TableNotFoundException
)
from core.query import AXQL

def clear_screen():
    print("\033c", end="")

def launch_shell():
    axql = AXQL()
    command = ""
    
    while True:
        try:
            command_prefix = prefix = "axql"
            if axql.current_db:
                prefix = axql.current_db.dbname
                command_prefix = "axql.current_db"
                
                if axql.current_db.alteration_table:
                    prefix += f">\033[36m{axql.current_db.alteration_table}"
                    command_prefix = "axql.current_db.tables[axql.current_db.alteration_table]"
            
            if command != "exit":
                command = input(f"\033[33m{prefix} \033[31m#~> \033[0m").strip()
            
            if command.lower() == "exit":
                if axql.current_db:
                    if axql.current_db.alteration_table:
                        axql.current_db.end_alter()
                    else:
                        print(f"\nQuit database {axql.current_db.dbname} !!")
                        axql.quit_current_db()

                else:
                    print("\nGoodbye :)")
                    break
                
                command = ""

            elif command.lower() == "clear":
                clear_screen()
            
            elif command == "":
                pass

            else:
                try:
                    eval(f"{command_prefix}.{command}")
                except Exception as e:
                    print(f"\n\033[31mError: {e}")
        
        except (TypeError, ValueError, PermissionError) as e:
            print(f"\n\033[31mError: {type(e).__name__} - {e}")
        
        except (DatabaseNotFoundException, DatabaseExistsException, 
                TableNotFoundException, TableExistsException) as e:
            print(f"\n\033[31mError: {e}")
        
        except EOFError:
            command = "exit"
        
        except KeyboardInterrupt:
            print("\nError: shell interrupted!!")
            break

if __name__ == "__main__":
    launch_shell()
