from core.exceptions import (
    DatabaseExistsException, DatabaseNotFoundException, 
    TableExistsException, TableNotFoundException
)
from core.query import AXQL

import readline, os, atexit
from config import HISTORY_FILE

from prompt_toolkit import HTML, prompt
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from pygments.lexers.python import PythonLexer

from cli.styles import HIGHLIGHT_STYLE
from cli.completions import axql_completer

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
                    prefix += f"><ansiblue>{axql.current_db.cli_table}</ansiblue>"
                    command_prefix = "axql.current_db.tables[axql.current_db.cli_table]"
            
            if command != "exit":
                command = prompt(
                                HTML(f"<ansibold><ansimagenta>{prefix}</ansimagenta> <ansiblue>#~></ansiblue></ansibold> "),
                                 enable_history_search=True,
                                 enable_system_prompt=True,
                                 lexer=PygmentsLexer(PythonLexer),
                                 history=FileHistory(HISTORY_FILE),
                                 completer=axql_completer,
                                 style=HIGHLIGHT_STYLE).strip()
                
                readline.add_history(command)
            
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

                case "describe":
                    if axql.current_db != None:
                        eval(f"{command_prefix}.describe()")
                    
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
    load_history()
    launch_shell()
    