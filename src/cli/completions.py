from prompt_toolkit.completion import WordCompleter

commands = [
    "use_database", "drop_database", "create_database"
    "select_table", "create_table", "describe",
    "exit", "qt", "accept", "cancel",
    "add_attributes", "remove_attribute", "update_attribute"
]
axql_completer = WordCompleter(commands, ignore_case=True)