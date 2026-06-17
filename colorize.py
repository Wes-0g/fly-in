def colorize(text: str, color: str | None) -> str:
    """Apply ANSI color codes to text for terminal output.

    Args:
        text: The text to colorize.
        color: The color name or hex code. If None, returns text unchanged.

    Returns:
        The colorized text with ANSI escape codes,
         or original text if color is None.
    """

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
    }

    if color and color in colors:
        return f"{colors[color]}{text}\033[0m"
    elif color:
        code = hash(color) % 256
        return f"\033[38;5;{code}m{text}\033[0m"
    else:
        return text
