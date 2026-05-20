# kalk/ast_nodes.py

class Context:
    def __init__(self, input_provider=None, parent=None):
        self.mem = {}
        self.funcs = {} if parent is None else parent.funcs
        self.output = [] if parent is None else parent.output
        self.input_provider = input_provider if parent is None else parent.input_provider
        self.parent = parent
        self.return_value = None
        self.returning = False

    def get_var(self, name):
        if name in self.mem:
            return self.mem[name]
        if self.parent:
            return self.parent.get_var(name)
        return 0

    def set_var(self, name, val):
        self.mem[name] = val

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
        return ctx.get_var(self.name)

class ArrayLiteral(Expr):
    def __init__(self, elements):
        self.elements = elements
    def eval(self, ctx):
        return [e.eval(ctx) for e in self.elements]

class ArrayAccess(Expr):
    def __init__(self, name, index_expr):
        self.name = name
        self.index_expr = index_expr
    def eval(self, ctx):
        arr = ctx.get_var(self.name)
        if not isinstance(arr, list): arr = []
        idx = int(self.index_expr.eval(ctx))
        return arr[idx]

class FunctionCallExpr(Expr):
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def eval(self, ctx):
        func = ctx.funcs.get(self.name)
        if not func:
            raise Exception(f"Funcția {self.name} nu este definită")
        
        new_ctx = Context(parent=ctx)
        for i, param in enumerate(func.params):
            if i < len(self.args):
                new_ctx.set_var(param, self.args[i].eval(ctx))
        
        for instr in func.body:
            instr.exec(new_ctx)
            if new_ctx.returning:
                break
        
        return new_ctx.return_value

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
            "/": a / b,
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
        ctx.set_var(self.var, ctx.input_provider(self.var))

class DeclInstr(Instr):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr
    def exec(self, ctx):
        ctx.set_var(self.var, self.expr.eval(ctx))

class AssignInstr(Instr):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr
    def exec(self, ctx):
        ctx.set_var(self.var, self.expr.eval(ctx))

class ArrayAssignInstr(Instr):
    def __init__(self, var, index_expr, expr):
        self.var = var
        self.index_expr = index_expr
        self.expr = expr
    def exec(self, ctx):
        arr = ctx.get_var(self.var)
        if not isinstance(arr, list): arr = []
        idx = int(self.index_expr.eval(ctx))
        arr[idx] = self.expr.eval(ctx)

class FunctionDefInstr(Instr):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
    def exec(self, ctx):
        ctx.funcs[self.name] = self

class ReturnInstr(Instr):
    def __init__(self, expr):
        self.expr = expr
    def exec(self, ctx):
        ctx.return_value = self.expr.eval(ctx)
        ctx.returning = True

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
            if ctx.returning: break

class WhileInstr(Instr):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body
    def exec(self, ctx):
        while self.cond.eval(ctx):
            for instr in self.body:
                instr.exec(ctx)
                if ctx.returning: break
            if ctx.returning: break
