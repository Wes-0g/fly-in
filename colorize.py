def colorize(text: str, color: str | None) -> str:
    """Apply ANSI color codes to text for terminal output.

    Args:
        text: The text to colorize.
        color: The color name. If None, returns text unchanged.

    Returns:
        The colorized text with ANSI escape codes,
         or original text if color is None.
    """

    rainbow_color: list[str] = [
        "\033[31m",
        "\033[91m",
        "\033[93m",
        "\033[32m",
        "\033[34m",
        "\033[35m",
        "\033[95m"
    ]

    colors: dict[str, str] = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[93m",
        "blue": "\033[34m",
        "magenta": "\033[95m",
        "cyan": "\033[36m",
        "gray": "\033[90m",
        "orange": "\033[91m",
        "lime": "\033[92m",
        "brown": "\033[33m",
        "purple": "\033[35m",
        "gold": "\033[93m",
        "maroon": "\033[38;5;88m",
        "darkred": "\033[38;5;52m",
        "violet": "\033[38;5;135m",
        "crimson": "\033[38;5;160m"
    }

    if color and color in colors:
        return f"{colors[color]}{text}\033[0m"

    elif color == "rainbow":
        return "".join(f"{rainbow_color[i % 7]}{ch}"
                       for i, ch in enumerate(text))
    else:
        return text
