from core.exceptions import (
    DatabaseExistsException, DatabaseNotFoundException, 
    TableExistsException, TableNotFoundException
)
from core.query import AXQL

import readline, os, atexit
from config import HISTORY_FILE

from prompt_toolkit import prompt
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer

from cli.styles import HIGHLIGHT_STYLE

def load_history():
    if os.path.exists(HISTORY_FILE):
        readline.read_history_file(HISTORY_FILE)

def save_history():
    readline.write_history_file(HISTORY_FILE)


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
                
                if axql.current_db.cli_table:
                    prefix += f">{axql.current_db.cli_table}"
                    command_prefix = "axql.current_db.tables[axql.current_db.cli_table]"
            
            if command != "exit":
                command = prompt(f"{prefix} #~> ", lexer=PygmentsLexer(PythonLexer), style=HIGHLIGHT_STYLE).strip()
            
            match command.lower():
                # alter table things
                case "cancel": # decline new table structure
                    if axql.current_db.cli_table:
                        axql.current_db.cancel_alter()
                    else:
                        print("No table selected !!")

                case "accept": # accept new table structure
                    if axql.current_db.cli_table:
                        axql.current_db.accept_alter()
                    else:
                        print("No table selected !!")

                case "qt": # quit the current table
                    if axql.current_db.cli_table:
                        print(f"Quit table {axql.current_db.cli_table} !")
                        axql.current_db.quit_table()
                    else:
                        print("No table selected !!")

                # CLI things
                case "exit":
                    if axql.current_db:
                        print(f"\nQuit database {axql.current_db.dbname} !!")
                        axql.quit_current_db()

                    else:
                        print("\nGoodbye :)")
                        break
                    
                    command = ""

                case "clear":
                    clear_screen()

                case "":
                    pass

                case _:
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
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("set editing-mode vi")
    atexit.register(save_history)
    load_history()
    launch_shell()
    