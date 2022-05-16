def format_currency(value: float) -> str:
    """Parses the value to a currency like format
    Returns
    -------
    str
        the parsed value
    """
    return f"{value:,.2f}"