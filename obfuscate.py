#!/usr/bin/python3

"""
    By Théophile Bastian, 2016
    Obfuscates a code by applying some trollful strategies :)
"""

import ast
import astunparse
import random
import sys

def replaceIdents(source, env):
    with open(source,'r') as handle:
        code = handle.read()
    codeAst = ast.parse(code, source)
    
    def freshName(env):
        NAME_LENGTH = 16
        CHARS = '0O'
        out = 'O'
        for i in range(NAME_LENGTH):
            out += random.choice(CHARS)
        
        if out in env:
            return freshName(env)
        return out

    class RewriteIdents(ast.NodeTransformer):
        def __init__(self, _env):
            self.env = _env
            ast.NodeTransformer.__init__(self)

        def changeName(self, name):
            if name in self.norepl:
                nId = name
            elif name in self.env:
                nId = self.env[name]
            else:
                nId = freshName(self.env)
                self.env[name] = nId
            return nId

        def visit_FunctionDef(self,node):
            node.name = self.changeName(node.name)
            nArgs = []
            for arg in node.args.args:
                arg.arg = self.changeName(arg.arg)
                nArgs.append(arg)
            node.args.args = nArgs
            self.generic_visit(node)
            return node

        def visit_Import(self, node):
            for al in node.names:
                if(al.asname):
                    self.norepl.append(al.asname)
                else:
                    self.norepl.append(al.name)
            return node
        def visit_Name(self, node):
            nId = self.changeName(node.id)
            return ast.fix_missing_locations(ast.Name(id=nId, ctx=ast.Load()))

        def getEnv(self):
            return self.env
        env = {}
        norepl = []

    rewriter = RewriteIdents(env)
    nCode = rewriter.visit(codeAst)
    nEnv = rewriter.getEnv()
    return nCode, nEnv

def main():
    env = {}
    for builtin in (dir(__builtins__) + ['__builtins__']):
        env[builtin] = builtin
    for f in sys.argv[1:]:
        nCode,env = replaceIdents(f, env)
        print(astunparse.unparse(nCode))

if __name__ == '__main__':
    main()
    sys.exit(0)

