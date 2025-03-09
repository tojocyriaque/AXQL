from prompt_toolkit import prompt
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer
from prompt_toolkit.styles import Style

# Define custom styles
style = Style.from_dict({
    "pygments.keyword": "bold ansiblue",
    "pygments.string": "ansigreen",
    "pygments.number": "ansiyellow",
    "pygments.name": "ansicyan",
})

def main():
    while True:
        try:
            # Prompt with syntax highlighting
            command = prompt(">>> ", lexer=PygmentsLexer(PythonLexer), style=style)
            if command.strip().lower() in ["exit", "quit"]:
                break
            exec(command)  # Execute the Python command
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
