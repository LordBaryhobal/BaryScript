#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs_const import *
from bs_tokens import *
import json, re

i = 0

class Symbolizer:
    def __init__(self, interpreter):
        self.interpreter = interpreter

    def symbolize(self, tokenTree):
        self.interpreter.log("Start symbolization", DebugLevel.DEBUG)

        globalCtxt = GlobalContext()

        self.program = self.tokenToSymbol(tokenTree, globalCtxt)

    def tokenToSymbol(self, token, ctxt):
        global i
        I = i
        i += 1
        
        if not isinstance(token, TokenString):
            token.content = token.content.strip()
        
        if isinstance(token, TokenBlock):
            self.interpreter.log("  Block symbol", DebugLevel.DEBUG)
            
            symbol = SymbolBlock(context=ctxt.copy())
            symbol.context.define("@@PARENT", symbol)

            for t in token.tokens:
                symbol.symbols.append(self.tokenToSymbol(t, symbol.context))

        elif isinstance(token, TokenString):
            self.interpreter.log("  String symbol", DebugLevel.DEBUG)
            
            symbol = SymbolString(token.content)

        elif isinstance(token, TokenExpression):
            self.interpreter.log("  Expression symbol", DebugLevel.DEBUG)
            
            if len(token.tokens) == 1 and isinstance(token.tokens[0], TokenParenthesis):
                self.interpreter.log("    Function call symbol", DebugLevel.DEBUG)
                
                name = token.content.split("(")[0]
                args = token.tokens[0].tokens
                
                func = ctxt.lookup(name)
                
                if func:
                    args = [
                        self.tokenToSymbol(arg, ctxt)
                        for arg in args
                    ]
                    
                    symbol = SymbolFunctionCall(func, args)
                
                else:
                    raise ReferenceError(f"Function {name} is not defined")
            
            elif re.match(r"\d", token.content):
                symbol = SymbolNumeric(token.content)
            
            elif len(token.tokens) == 0:
                symbol = SymbolVariable(token.content)
            
            else:
                symbol = SymbolBlock(context=ctxt.copy())
                symbol.context.define("@@PARENT", symbol)

                for t in token.tokens:
                    symbol.symbols.append(self.tokenToSymbol(t, symbol.context))
        
        elif isinstance(token, TokenFunction):
            if len(token.tokens) == 2 and isinstance(token.tokens[0], TokenParenthesis) and isinstance(token.tokens[1], TokenExpression):
                self.interpreter.log("    Function definition symbol", DebugLevel.DEBUG)
                
                name = token.content.split("(")[0]
                params = token.tokens[0].content.split(",")
                body = self.tokenToSymbol(token.tokens[1], ctxt.copy())

                symbol = SymbolFunction(name, params, body)
                body.context.define("@@PARENT", symbol)

                ctxt.define(name, symbol)
            
            else:
                self.interpreter.log("  Invalid function call", DebugLevel.ERRORS)

        elif isinstance(token, TokenOperator):
            self.interpreter.log("  Operator symbol", DebugLevel.DEBUG)
            
            op = token.content
            
            """
            parent = ctxt.lookup("@@PARENT")
            if len(parent.symbols) > 1:
                if isinstance(parent.symbols[-1], SymbolOperator):
                    if len(parent.symbols[-1].operands) < 2:
                        prev = parent.symbols.pop(-1)
                        op = prev.op + op
            """
            
            operands = [
                self.tokenToSymbol(operand, ctxt)
                for operand in token.operands
            ]
            symbol = SymbolOperator(op, operands)
        
        else:
            symbol = SymbolValue(token.content)
        
        parent = ctxt.lookup("@@PARENT", True)
        print("--1--")
        print(I)
        print(symbol)
        if token.content == "c":
            print("##################################")
        print("A")
        if parent and len(parent.symbols) > 0:
            print("B")
            prev = parent.symbols[-1]
            print("prev:",prev)
            if isinstance(prev, SymbolOperator):
                print("C")
                print(token.line, prev.op, prev.operands)
                
                if len(prev.operands) < 2:
                    print("D")
                    parent.symbols.pop(-1)
                    prev.operands.append(symbol)
                    
                    symbol = prev
        print("--2---")
        
        return symbol


class Symbol(str):
    name = "Symbol"
    
    def __new__(cls, *args, **kwargs):
        obj = str.__new__(cls, f"<{cls.name}>")
        return obj

    def __init__(self, value):
        self.value = value

    def eval(self, context, *args, **kwargs):
        #print(f"Evaluating {self}") ### TO REMOVE
        return self.value
    
    def display(self, indent=0):
        print(" "*indent + str(self))
        
        for child in self.getDisplayChildren():
            child.display(indent+1)
    
    def getDisplayChildren(self):
        return []
    
    def __eq__(self, other):
        return id(self) == id(other)


class SymbolVariable(Symbol):
    name = "Variable"
    
    def eval(self, context, *args, **kwargs):
        val = context.lookup(self.value, True)
        
        """
        if val is None:
            raise NameError(f"{self.value} is undefined")
        """
        
        return val


class SymbolFunction(Symbol):
    name = "Function"

    def __init__(self, id_, params, body):
        self.id = id_
        self.params = params
        self.body = body

    def eval(self, context, *args, **kwargs):
        #print(f"Evaluating function {self.id}") ### TO REMOVE
        
        context = context.copy()
        for i in range(len(self.params[0])):
            if i < len(args):
                context.define(self.params[0][i], args[i])

            else:
                raise TypeError("Not enough arguments")

        for k, v in self.params[1].items():
            if k in kwargs.keys():
                v = kwargs[k]

            context.define(k, v)

        return self.body.eval(context, *args, funcBody=True, **kwargs)
    
    
    def getDisplayChildren(self):
        return self.params+[self.body]


class SymbolValue(Symbol):
    name = "Value"
    func = lambda self, v: v
    
    def eval(self, context, *args, **kwargs):
        #print(f"Evaluating {self}") ### TO REMOVE
        return self.func(self.value)


class SymbolString(SymbolValue):
    name = "String"
    func = str
    
    def __init__(self, value):
        value = value.replace("\\n", "\n")
        value = value.replace("\\t", "\t")
        value = value.replace('\\"', '"')
        value = value.replace("\\'", "'")
        super().__init__(value)


class SymbolNumeric(SymbolValue):
    name = "Numeric"
    func = int
    
    def __init__(self, value, full=True):
        #print(f"Init numeric {value} ({full})") ### TO REMOVE
        
        super().__init__(value)
        
        if full:
            try:
                f = float(value)
                i = int(value)
                
                if i != f or "." in value:
                    self = SymbolFloat(f, False)
                
                else:
                    self = SymbolInt(i, False)
            
            except:
                print(f"{value}: NaN")
        
        #print(self.__dict__,full) ### TO REMOVE


class SymbolInt(SymbolNumeric):
    name = "Int"
    func = int


class SymbolFloat(SymbolNumeric):
    name = "Float"
    func = float


class SymbolBlock(Symbol):
    name = "Block"
    
    def __init__(self, symbols=None, context=None):
        if symbols is None:
            symbols = []

        self.symbols = symbols

        if context is None:
            context = Context()

        self.context = context

    def eval(self, *args, funcBody=False, **kwargs):
        #print(f"Evaluating block") ### TO REMOVE
        self.value = None

        for symbol in self.symbols:
            val = symbol.eval(self.context)
            
            if funcBody:
                self.value = val

        return self.value
    
    def getDisplayChildren(self):
        return self.symbols

class SymbolFunctionCall(Symbol):
    name = "Function call"

    def __init__(self, function, params):
        self.function = function
        self.params = params

    def eval(self, context, *args, **kwargs):
        return self.function.eval(context, *self.params, *kwargs)
    
    def getDisplayChildren(self):
        return self.params

class SymbolOperator(Symbol):
    name = "Operator"
    
    def __init__(self, op, operands=None):
        self.op = op
        
        if operands is None:
            operands = []
        
        self.operands = operands
    
    def eval(self, context, *args, **kwargs):
        #print()
        #print("Op:",self.op) ### TO REMOVE
        #self.display()
        #print()
        
        parent = context.lookup("@@PARENT")
        #familyIndex = parent.symbols.index(self)
        
        prev, next_ = None, None
        
        """
        if familyIndex > 0:
            prev = parent.symbols[familyIndex-1]
        
        if familyIndex < len(parent.symbols)-1:
            next_ = parent.symbols[familyIndex+1]
        """
        if len(self.operands) > 0:
            prev = self.operands[0]
            
            if len(self.operands) > 1:
                next_ = self.operands[1]
        
        #print(prev,prev.value, next_,next_.value) ### TO REMOVE
        
        value = None
        val1, val2 = prev.eval(context, *args, **kwargs), next_.eval(context, *args, **kwargs)
        #print(prev, val1, next_, val2)
        
        if self.op == "=":
            if isinstance(next_, SymbolVariable):
                #context.define(prev.value, next_.eval(context, *args, **kwargs))
                context.define(next_.value, val1)
        
        elif self.op[0] == "+":
            value = val1 + val2
        
        elif self.op[0] == "-":
            value = val1 - val2
        
        elif self.op[0] == "*":
            value = val1 * val2
        
        elif self.op[0] == "/":
            value = val1 / val2
        
        if len(self.op) > 1:
            if self.op[1] == "=":
                if isinstance(prev, SymbolVariable):
                    context.define(prev.value, value)
        
        return value
    
    def display(self, indent=0):
        print(" "*indent + f"OPERATOR : {self.op} -> {self.operands}")
        
        for child in self.getDisplayChildren():
            child.display(indent+1)

class Context:
    def __init__(self):
        self.symbols = {}

    def lookup(self, name, soft=False):
        #print(f"Looking up {name}") ### TO REMOVE
        
        if name not in self.symbols.keys():
            if soft:
                return None
            
            raise NameError(f"{name} is not defined")

        return self.symbols[name]

    def define(self, name, symbol):
        #print(f"Defining {name}") ### TO REMOVE
        self.symbols[name] = symbol

    def copy(self):
        ctxt = Context()
        ctxt.symbols = self.symbols.copy()

        return ctxt
    
    def __repr__(self):
        return json.dumps(self.symbols, indent=2)

from bs_builtin import *