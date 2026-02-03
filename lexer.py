# kalk/lexer.py

KEYWORDS = {
    "CITESTE", "DECLAR", "VALOARE",
    "DACA", "ATUNCI", "ALTFEL",
    "CATTIMP", "EXECUTA", "SFARSIT",
    "SCRIE", "SI", "SAU"
}

OPERATORS = {"<-", "+", "-", "*", "/", "%", "==", "!=", "<=", ">=", "<", ">"}

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"{self.type}({self.value})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def peek(self):
        return self.text[self.pos] if self.pos < len(self.text) else None

    def advance(self):
        self.pos += 1

    def next_token(self):
        while self.peek() and self.peek().isspace():
            self.advance()

        if self.peek() is None:
            return Token("EOF", "")

        if self.peek().isdigit():
            num = ""
            while self.peek() and self.peek().isdigit():
                num += self.peek()
                self.advance()
            return Token("NUMBER", int(num))

        if self.peek().isalpha():
            ident = ""
            while self.peek() and self.peek().isalnum():
                ident += self.peek()
                self.advance()
            if ident.upper() in KEYWORDS:
                return Token("KEYWORD", ident.upper())
            return Token("IDENT", ident)

        for op in sorted(OPERATORS, key=len, reverse=True):
            if self.text[self.pos:self.pos+len(op)] == op:
                self.pos += len(op)
                return Token("OP", op)

        raise Exception(f"Caracter necunoscut: {self.peek()}")
