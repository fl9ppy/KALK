# kalk/parser.py

from .lexer import Token
from .ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def cur(self):
        return self.tokens[self.pos]

    def eat(self):
        self.pos += 1

    def expect(self, t, v=None):
        tok = self.cur()
        if tok.type != t or (v and tok.value != v):
            raise Exception(f"Eroare sintactica la {tok}")
        self.eat()
        return tok

    def parse_program(self):
        instr = []
        while self.cur().type != "EOF":
            instr.append(self.parse_statement())
        return instr

    def parse_statement(self):
        tok = self.cur()

        if tok.value == "CITESTE":
            self.eat()
            name = self.expect("IDENT").value
            return InputInstr(name)

        if tok.value == "DECLAR":
            self.eat()
            name = self.expect("IDENT").value
            self.expect("KEYWORD", "VALOARE")
            expr = self.parse_expr()
            return DeclInstr(name, expr)

        if tok.value == "SCRIE":
            self.eat()
            return OutputInstr(self.parse_expr())

        if tok.value == "DACA":
            self.eat()
            cond = self.parse_cond()
            self.expect("KEYWORD", "ATUNCI")
            then_body = self.parse_block()
            else_body = []
            if self.cur().value == "ALTFEL":
                self.eat()
                else_body = self.parse_block()
            self.expect("KEYWORD", "SFARSIT")
            return IfInstr(cond, then_body, else_body)

        if tok.value == "CATTIMP":
            self.eat()
            cond = self.parse_cond()
            self.expect("KEYWORD", "EXECUTA")
            body = self.parse_block()
            self.expect("KEYWORD", "SFARSIT")
            return WhileInstr(cond, body)

        if tok.type == "IDENT":
            name = tok.value
            self.eat()
            self.expect("OP", "<-")
            return AssignInstr(name, self.parse_expr())

        raise Exception(f"Instructiune necunoscuta: {tok}")

    def parse_block(self):
        body = []
        while self.cur().value not in {"SFARSIT", "ALTFEL"}:
            body.append(self.parse_statement())
        return body

    # -------- CONDITII --------
    def parse_cond(self):
        left = self.parse_and()
        while self.cur().value == "SAU":
            self.eat()
            right = self.parse_and()
            left = LogicalCond("SAU", left, right)
        return left

    def parse_and(self):
        left = self.parse_simple_cond()
        while self.cur().value == "SI":
            self.eat()
            right = self.parse_simple_cond()
            left = LogicalCond("SI", left, right)
        return left

    def parse_simple_cond(self):
        left = self.parse_expr()
        op = self.expect("OP").value
        right = self.parse_expr()
        return CompareCond(op, left, right)

    # -------- EXPRESII --------
    def parse_expr(self):
        left = self.parse_term()
        while self.cur().value in {"+", "-"}:
            op = self.cur().value
            self.eat()
            right = self.parse_term()
            left = BinExpr(op, left, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.cur().value in {"*", "/", "%"}:
            op = self.cur().value
            self.eat()
            right = self.parse_factor()
            left = BinExpr(op, left, right)
        return left

    def parse_factor(self):
        tok = self.cur()
        if tok.type == "NUMBER":
            self.eat()
            return Number(tok.value)
        if tok.type == "IDENT":
            self.eat()
            return Variable(tok.value)
        raise Exception("Factor invalid")
