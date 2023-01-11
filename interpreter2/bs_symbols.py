#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs_const import *
from bs_tokens import *
import json, re

i = 0

class Symbolizer:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.tokens = self.interpreter.tokens
        self.tokenCount = len(self.tokens)
        
        self.index = 0
        
        self.tree = SymbolBlock(context=GlobalContext())
    
    def findNext(self, typeOrTypes):
        if not isinstance(typeOrTypes, (list, tuple)):
            typeOrTypes = [typeOrTypes]
        
        for i in range(self.index+1, self.tokenCount):
            if self.tokens[i].type in typeOrTypes:
                return (i, self.tokens[i])
        
        return (-1, None)
    
    def getNext(self, ignoreWhitespace=True):
        for i in range(self.index+1, self.tokenCount):
            token = self.tokens[i]
            
            if (not ignoreWhitespace) or (token.type != TokenType.WHITESPACE):
                return (i, token)
        
        return (-1, None)
    
    def getPrev(self, ignoreWhitespace=True):
        for i in range(self.index-1, -1, -1):
            token = self.tokens[i]
            
            if (not ignoreWhitespace) or (token.type != TokenType.WHITESPACE):
                return (i, token)
        
        return (-1, None)
    
    def symbolize(self):
        self.interpreter.log("Start symbolization", DebugLevel.DEBUG)
        
        self._symbolize()
        self.tree = self.tree.getTop()
        
        self.interpreter.log("End symbolization", DebugLevel.DEBUG)
    
    def _symbolize(self, start=0, end=None):
        if end is None:
            end = self.tokenCount
        
        self.index = start
        
        while self.index < end:
            self.loop()
            self.index += 1
    
    def loop(self):
        token = self.tokens[self.index]
        nextDIndex, nextDToken = self.getNext(False)
        nextIndex, nextToken = self.getNext()
        
        #print(f"Token -> {token}") ### TO REMOVE
        #print(f"Next -> {nextToken}") ### TO REMOVE
        #print(f"Next direct -> {nextDToken}") ### TO REMOVE
        
        if token.type == TokenType.FUNC:
            #Function definition
            if nextToken and nextToken.type == TokenType.NAME:
                symbol = SymbolFunction(nextToken.content)
                
                self.tree.addChild(symbol)
                
                #Get opening parenthesis
                beginParamsI, _ = self.findNext(TokenType.OPEN_PAR)
                
                if beginParamsI == -1:
                    raise SyntaxError("Missing function parameters")
                
                self.index = beginParamsI+1
                
                #Get closing parenthesis
                closingPar = _.closing
                endParamsI = self.tokens.index(closingPar)
                
                #Get parameters
                for i in range(self.index,endParamsI):
                    param = self.tokens[i]
                    
                    if param.type == TokenType.NAME:
                        symbol.params.append(param.content)
                
                self.index = endParamsI+1
                self.tree = symbol
                
                #Get opening curly brace
                beginBodyI, _ = self.findNext(TokenType.OPEN_CUR)
                
                if beginBodyI == -1:
                    raise SyntaxError("Missing function body")
                
                self.index = beginBodyI+1
                
                #Get closing curly brace
                closingCur = _.closing
                endBodyI = self.tokens.index(closingCur)
                
                #Body
                self._symbolize(self.index, endBodyI)
                
                self.tree = self.tree.getUp()
            
            else:
                raise SyntaxError("Function defined without a name")
        
        elif token.type == TokenType.NAME:
            #Function call
            if nextDToken and nextDToken.type == TokenType.OPEN_PAR:
                symbol = SymbolFunctionCall(token.content)
                self.tree.addChild(symbol)
                self.tree = symbol
                
                endArgsI = self.tokens.index(nextDToken.closing)
                
                #Args
                self._symbolize(self.index+2, endArgsI)
                
                self.tree = self.tree.getUp()
            
            else:
                symbol = SymbolVariable(token.content)
                self.tree.addChild(symbol)
        
        elif token.type == TokenType.STRING:
            self.tree.addChild(SymbolString(token.content))
        
        elif token.type == TokenType.NUMBER:
            value = token.content
            try:
                value = int(value)
                symbol = SymbolInt(value)
            
            except:
                value = float(value)
                symbol = SymbolFloat(value)
            
            self.tree.addChild(symbol)
        
        elif token.type == TokenType.OPERATOR:
            op = token.content
            symbol = SymbolOperator(op)
            self.tree.addChild(symbol)
            
            prevIndex, prevToken = self.getPrev()
            
            if symbol.needPrev and prevIndex == -1:
                raise SyntaxError("Missing operand before operator")
            
            if symbol.needNext and nextIndex == -1:
                raise SyntaxError("Missing operand after operator")
            
            if True: #op == "=": # TO REMOVE
                symbol.op1 = self.tree.children[-2]
                
                self.tree = symbol
                endLineI, _ = self.findNext([TokenType.EOL, TokenType.CLOSE_PAR, TokenType.CLOSE_BRA])
                
                if endLineI == -1:
                    raise SyntaxError("EOL not found")
                
                self._symbolize(self.index+1, endLineI)
            
                self.tree = self.tree.getUp()
            
            if not symbol.op1 is None:
                self.tree.children.pop(-2) ###HERE
        
        elif token.type == TokenType.RETURN:
            symbol = SymbolReturn()
            self.tree.addChild(symbol)
            
            self.tree = symbol
            endLineI, _ = self.findNext(TokenType.EOL)
            
            if endLineI == -1:
                raise SyntaxError("EOL not found")
            
            self._symbolize(self.index+1, endLineI)
        
            self.tree = self.tree.getUp()
        
        elif token.type in [TokenType.IF, TokenType.ELIF, TokenType.ELSE]:
            if token.type == TokenType.ELSE or (nextToken and nextToken.type == TokenType.OPEN_PAR):
                symbol = SymbolConditional(token.content)
                self.tree.addChild(symbol)
                
                if token.type != TokenType.ELSE:
                    self.tree = symbol
                    
                    #Get start of condition
                    startCondI, _ = self.findNext(TokenType.OPEN_PAR)
                    
                    if startCondI == -1:
                        raise SyntaxError(f"{token.content} condition not found at {token.pos}")
                    
                    self.index = startCondI+1
                    
                    endCondI = self.tokens.index(_.closing)
                    
                    #Condition
                    self._symbolize(self.index, endCondI)
                
                else:
                    self.index += 1
                
                self.tree = symbol.body
                
                #Get start of body
                startBodyI, _ = self.findNext(TokenType.OPEN_CUR)
                
                if startBodyI == -1:
                    raise SyntaxError(f"{token.content} body not found at {token.pos}")
                
                self.index = startBodyI+1
                
                #Get end of body
                endBodyI = self.tokens.index(_.closing)
                
                #Body
                self._symbolize(self.index, endBodyI)
                
                self.tree = symbol.getUp()
                
                #Parent if
                if token.type in [TokenType.ELIF, TokenType.ELSE]:
                    prevSymbol = None
                    
                    if len(self.tree.children) > 1:
                        prevSymbol = self.tree.children[-2]
                    
                    if prevSymbol is None or not isinstance(prevSymbol, SymbolConditional):
                        raise SyntaxError(f"{token.content} is not preceed by an if statement ({token.pos})")
                    
                    if prevSymbol.op in ["if", "elif"]:
                        symbol.parentIf = prevSymbol
                    
                    elif prevSymbol.op == "else":
                        self.interpreter.log(f"Double else statement at {token.pos}, will never be called", DebugLevel.WARNINGS)
            
            else:
                raise SyntaxError(f"Missing condition after {token.content}")

class Node:
    def __init__(self):
        self.parent = None
        self.children = []
    
    def addChild(self, node):
        self.children.append(node)
        node.parent = self
    
    def getUp(self):
        return self.parent
    
    def getTop(self):
        if self.parent is None:
            return self
        
        return self.parent.getTop()


class Symbol(Node):
    name = "Symbol"

    def __init__(self, value):
        super().__init__()
        self.value = value

    def eval(self, context, *args, **kwargs):
        #print(f"Evaluating {self}") ### TO REMOVE
        return self.value
    
    def display(self, indent=0):
        print(" "*indent*INDENT_SIZE + str(self))
        
        for child in self.children:
            child.display(indent+1)
    
    def __eq__(self, other):
        return id(self) == id(other)
    
    def __repr__(self):
        return f"/{self.name} ({self.value})/"


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

    def __init__(self, id_):
        Node.__init__(self)
        
        self.id = id_
        self.params = []
    
    def eval(self, context, *args, **kwargs):
        context.define(self.id, self)
    
    def call(self, context, *args, **kwargs):
        #print(f"Evaluating function {self.id}") ### TO REMOVE
        
        context = context.copy()
        for i in range(len(self.params)):
            if i < len(args):
                context.define(self.params[i], args[i].eval(context, *args, **kwargs))

            else:
                raise TypeError("Not enough arguments")
        
        """
        for k, v in self.params[1].items():
            if k in kwargs.keys():
                v = kwargs[k]

            context.define(k, v)
        """
        
        self.value = None
        for symbol in self.children:
            symbol.eval(context)
            
            if isinstance(symbol, SymbolReturn):
                break

        return self.value
    
    def __repr__(self):
        return f"/{self.name} ({self.id}) {self.params}/"


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


class SymbolInt(SymbolNumeric):
    name = "Int"
    func = int


class SymbolFloat(SymbolNumeric):
    name = "Float"
    func = float


class SymbolBlock(Symbol):
    name = "Block"
    
    def __init__(self, context=None):
        Node.__init__(self)

    def eval(self, context, *args, **kwargs):
        self.value = None

        for symbol in self.children:
            symbol.eval(context)

        return self.value
    
    def __repr__(self):
        return f"/{self.name}/"

class SymbolReturn(Symbol):
    name = "Return"
    
    def __init__(self):
        Node.__init__(self)

    def eval(self, context, *args, **kwargs):
        self.value = None

        if len(self.children) != 0:
            self.value = self.children[0].eval(context)
        
        self.parent.value = self.value
        return self.value
    
    def __repr__(self):
        return f"/{self.name}/"


class SymbolFunctionCall(Symbol):
    name = "Function call"

    def __init__(self, function):
        Node.__init__(self)
        self.function = function

    def eval(self, context, *args, **kwargs):
        function = context.lookup(self.function)
        
        #print(f"Calling function {self.function} with args {self.children}") ### TO REMOVE
        
        return function.call(context.copy(), *self.children, *kwargs)
    
    def __repr__(self):
        return f"/{self.name} ({self.function})/"

class SymbolOperator(Symbol):
    name = "Operator"
    
    def __init__(self, op, operands=None):
        Node.__init__(self)
        self.op = op
        
        self.op1 = None
        
        self.needPrev = False
        self.needNext = False
        if op in ["=", "+", "-", "*", "/"]:
            self.needPrev = True
            self.needNext = True
    
    def eval(self, context, *args, **kwargs):
        #print()
        #print("Op:",self.op) ### TO REMOVE
        #self.display()
        #print()
        
        #context = self.parent.context
        #parent = context.lookup("@@PARENT")
        #familyIndex = parent.symbols.index(self)
        
        #prev, next_ = None, None
        
        """
        if familyIndex > 0:
            prev = parent.symbols[familyIndex-1]
        
        if familyIndex < len(parent.symbols)-1:
            next_ = parent.symbols[familyIndex+1]
        """
        """
        if len(self.operands) > 0:
            prev = self.operands[0]
            
            if len(self.operands) > 1:
                next_ = self.operands[1]
        """
        
        #print(prev,prev.value, next_,next_.value) ### TO REMOVE
        
        value = None
        val1, val2 = self.op1.eval(context, *args, **kwargs), self.children[0].eval(context, *args, **kwargs)
        #print(self.op1, val1, type(val1), self.children[0], val2, type(val2))
        
        if self.op in ["<", ">", "<=", ">=", "!=","=="]:
            value = eval(f"{val1} {self.op} {val2}")
        
        else:
            if self.op == "=":
                if isinstance(self.op1, SymbolVariable):
                    #context.define(prev.value, next_.eval(context, *args, **kwargs))
                    context.define(self.op1.value, val2)
            
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
                    if isinstance(self.op1, SymbolVariable):
                        context.define(self.op1.value, value)
        
        return value
    
    def __repr__(self):
        return f"/{self.name} ({self.op}) -> {self.op1}/"

class SymbolConditional(Symbol):
    name = "Conditional"
    
    def __init__(self, op):
        Node.__init__(self)
        
        self.op = op
        self.body = SymbolBlock()
        self.body.parent = self
        
        self.parentIf = None
    
    def eval(self, context, *args, **kwargs):
        if self.op in ["elif", "else"]:
            if self.parentIf is None or self.parentIf.value:
                #If no parent if statement or executed a block, don't execute this one
                #print(f"{self.op} -> already executed") ### TO REMOVE
                self.value = True
                return
        
        self.value = True
        
        if self.op in ["if", "elif"]:
            self.value = self.children[0].eval(context)
        
        if self.value:
            #print(f"{self.op} -> test passed") ### TO REMOVE
            self.body.eval(context)
    
    def __repr__(self):
        return f"/{self.name} ({self.op})/"

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
        result = "Context ("+str(id(self))+") {"
        for k, v in self.symbols.items():
            result += f"\n    {k} -> {v}"
        
        result += "\n}"
        #return json.dumps(self.symbols, indent=2)
        return result

from bs_builtin import *