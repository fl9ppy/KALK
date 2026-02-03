# kalk/engine.py

from .ast_nodes import Context

class Engine:
    def run(self, program, ctx):
        for instr in program:
            instr.exec(ctx)

