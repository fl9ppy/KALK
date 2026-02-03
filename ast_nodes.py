# kalk/ast_nodes.py

class Context:
    def __init__(self, input_provider=None):
        self.mem = {}
        self.output = []
        self.input_provider = input_provider

# -------- EXPRESSII --------

class Expr:
    def eval(self, ctx):
        raise NotImplementedError

class Number(Expr):
    def __init__(self, value):
        self.value = value
    def eval(self, ctx):
        return self.value

class Variable(Expr):
    def __init__(self, name):
        self.name = name
    def eval(self, ctx):
        return ctx.mem.get(self.name, 0)

class BinExpr(Expr):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    def eval(self, ctx):
        a, b = self.left.eval(ctx), self.right.eval(ctx)
        return {
            "+": a + b,
            "-": a - b,
            "*": a * b,
            "/": a // b,
            "%": a % b
        }[self.op]

# -------- CONDITII --------

class Condition:
    def eval(self, ctx):
        raise NotImplementedError

class CompareCond(Condition):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    def eval(self, ctx):
        a, b = self.left.eval(ctx), self.right.eval(ctx)
        return {
            "==": a == b,
            "!=": a != b,
            "<": a < b,
            "<=": a <= b,
            ">": a > b,
            ">=": a >= b
        }[self.op]

class LogicalCond(Condition):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    def eval(self, ctx):
        if self.op == "SI":
            return self.left.eval(ctx) and self.right.eval(ctx)
        return self.left.eval(ctx) or self.right.eval(ctx)

# -------- INSTRUCTIUNI --------

class Instr:
    def exec(self, ctx):
        raise NotImplementedError

class InputInstr(Instr):
    def __init__(self, var):
        self.var = var

    def exec(self, ctx):
        if ctx.input_provider is None:
            raise Exception("Nu există provider de input")
        ctx.mem[self.var] = ctx.input_provider(self.var)

class DeclInstr(Instr):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr
    def exec(self, ctx):
        ctx.mem[self.var] = self.expr.eval(ctx)

class AssignInstr(Instr):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr
    def exec(self, ctx):
        ctx.mem[self.var] = self.expr.eval(ctx)

class OutputInstr(Instr):
    def __init__(self, expr):
        self.expr = expr
    def exec(self, ctx):
        ctx.output.append(str(self.expr.eval(ctx)))

class IfInstr(Instr):
    def __init__(self, cond, then_body, else_body):
        self.cond = cond
        self.then_body = then_body
        self.else_body = else_body
    def exec(self, ctx):
        body = self.then_body if self.cond.eval(ctx) else self.else_body
        for instr in body:
            instr.exec(ctx)

class WhileInstr(Instr):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body
    def exec(self, ctx):
        while self.cond.eval(ctx):
            for instr in self.body:
                instr.exec(ctx)
