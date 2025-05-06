import re
from enum import Enum, auto

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    STRING = auto()
    OPERATOR = auto()
    PUNCTUATION = auto()
    COMMENT = auto()
    EOF = auto()

class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f"{self.type.name}: {self.value}"

# Define token patterns for RPAL
TOKEN_SPECIFICATION = [
    ("COMMENT",     r"//.*"),
    ("STRING",      r"'(?:[^'\\]|\\.)*'"),  # Single-quoted string
    ("INTEGER",     r"\d+"),
    ("IDENTIFIER",  r"[a-zA-Z][a-zA-Z0-9_]*"),
    ("OPERATOR",    r"(\*\*|->|=>|>=|<=|==|!=|[+\-*/=><@&|~!%^])"),
    ("PUNCTUATION", r"[(),.;]"),
    ("NEWLINE",     r"\n"),
    ("SKIP",        r"[ \t]+"),
    ("MISMATCH",    r"."),  # Any other character
]

# Keywords in RPAL grammar
KEYWORDS = {
    'let', 'in', 'fn', 'where', 'aug', 'or', 'not',
    'gr', 'ge', 'ls', 'le', 'eq', 'ne', 'true', 'false',
    'nil', 'dummy', 'within', 'and', 'rec'
}

def tokenize(code):
    tokens = []
    tok_regex = '|'.join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION)
    get_token = re.compile(tok_regex).match
    line = 1
    pos = 0
    mo = get_token(code)
    while mo:
        kind = mo.lastgroup
        value = mo.group()
        if kind == "NEWLINE":
            line += 1
        elif kind == "SKIP" or kind == "COMMENT":
            pass
        elif kind == "IDENTIFIER" and value in KEYWORDS:
            tokens.append(Token(TokenType.KEYWORD, value))
        elif kind == "IDENTIFIER":
            tokens.append(Token(TokenType.IDENTIFIER, value))
        elif kind == "INTEGER":
            tokens.append(Token(TokenType.INTEGER, value))
        elif kind == "STRING":
            tokens.append(Token(TokenType.STRING, value))
        elif kind == "OPERATOR":
            tokens.append(Token(TokenType.OPERATOR, value))
        elif kind == "PUNCTUATION":
            tokens.append(Token(TokenType.PUNCTUATION, value))
        elif kind == "MISMATCH":
            raise RuntimeError(f"Unexpected character {value!r} on line {line}")
        pos = mo.end()
        mo = get_token(code, pos)
    tokens.append(Token(TokenType.EOF, 'EOF'))
    return tokens



if __name__ == "__main__":
    code = """
    let x = 5 in
    fn f => f 3
    // this is a comment
    'string literal'
    """

    token_list = tokenize(code)
    for token in token_list:
        print(token)
