from prompt_toolkit.styles import Style

# Define custom styles
HIGHLIGHT_STYLE = Style.from_dict({
    "pygments.keyword": "bold ansiblue",
    "pygments.string": "ansigreen",
    "pygments.number": "ansiyellow",
    "pygments.name": "ansicyan",
})