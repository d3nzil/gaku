"""Misc utils that didn't fit elsewhere."""

import regex


def is_kanji(char: str) -> bool:
    """Checks if provided character is kanji.

    Parameters
    ----------
    char: str
        Character to check

    Returns
    -------
    bool
        True if the character is Kanji

    Raises
    ------
    ValueError
        If there is no character, or more than one
    """

    if len(char) != 1:
        raise ValueError(
            f"The char must be exactly one character, got {len(char)}: {char}"
        )

    return regex.match(r"\p{Han}", char) is not None
