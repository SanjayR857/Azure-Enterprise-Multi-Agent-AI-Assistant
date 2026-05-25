import tiktoken

try:
    encoder = tiktoken.get_encoding("cl100k_base")
except Exception:
    encoder = None


def count_tokens(text: str) -> int:
    """
    Calculate the number of tokens in the given text using the tiktoken cl100k_base encoding.
    Falls back to character length if the encoder is not available.
    """
    if not text:
        return 0
    if encoder:
        return len(encoder.encode(text))
    return len(text)
