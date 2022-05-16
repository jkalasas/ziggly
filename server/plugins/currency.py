def format_currency(value: float | int) -> str:
    """Parses the value to a currency like format
    Returns
    -------
    str
        the parsed value
    """
    return f"{value:,.2f}"