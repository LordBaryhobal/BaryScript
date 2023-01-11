#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs_const import *

reserved_words = [
    "if", "else", "for", "while", "break", "continue",
    "function", "class"
]

operators = [
    "+", "-", "*", "/", "%", "=",
]

unary_op = [
    "!"
]

class Tokenizer:
    def __init__(self, interpreter):
        self.interpreter = interpreter

    def tokenize(self, text):
        self.interpreter.log("Start tokenization", DebugLevel.DEBUG)

        content = self.interpreter.content
        self.tree = TokenBlock(0, 0, content)

        index = 0
        line = 0
        col = 0
        skip = 0

        while True:
            char = content[index]
            
            #if len(self.tree.tokens) == 0:
            #    self.tree.content += char

            if not skip and char not in ["\n", "\t", " "]:
                """
                    End of tokens
                """
                closeToken = False
                # If in a string
                if isinstance(self.tree, TokenString):
                    # Escaped character
                    if char == "\\":
                        self.interpreter.log(
                            f"  Escaped character ({line}:{col})", DebugLevel.DEBUG)
                        skip = 2

                    # End of string ( between " or ' )
                    elif (char == '"' == self.tree.content[0]) or (char == "'" == self.tree.content[0]):
                        self.interpreter.log(
                            f"  End of string ({line}:{col})", DebugLevel.DEBUG)
                        
                        self.tree.content = content[self.tree.index+1:index]
                        closeToken = True
                
                elif char not in [";", ","]:
                    if isinstance(self.tree, TokenList):
                        # End of list ( between [ and ] )
                        if char == "]":
                            self.interpreter.log(
                                f"  End of list ({line}:{col})", DebugLevel.DEBUG)
                            closeToken = True
                    
                    elif isinstance(self.tree, TokenParenthesis):
                        # End of parenthesis ( between ( and ) )
                        if char == ")":
                            self.interpreter.log(
                                f"  End of parenthesis ({line}:{col})", DebugLevel.DEBUG)
                            closeToken = True
                            
                            self.tree.content = content[self.tree.index:index]

                    elif isinstance(self.tree, TokenBlock):
                        # End of block ( between { and } )
                        if char == "}":
                            self.interpreter.log(
                                f"  End of block ({line}:{col})", DebugLevel.DEBUG)
                            closeToken = True

                if not closeToken:
                    # End of expression
                    if char == ";":
                        self.interpreter.log(
                            f"  End of expression ({line}:{col})", DebugLevel.DEBUG)
                        closeToken = True
                        
                        self.tree.content = content[self.tree.index:index]
                    
                    elif char == ")":
                        self.interpreter.log(
                            f"  End of parenthesis (probably in expr) ({line}:{col})", DebugLevel.DEBUG)
                        closeToken = True
                        
                        self.tree.content = content[self.tree.index:index]
                        self.tree = self.tree.moveUp()
                        self.tree.content = content[self.tree.index:index+1]
                    
                    # End of element
                    elif char == "," and isinstance(self.tree, (TokenParenthesis, TokenList)):
                        self.interpreter.log(
                            f"  End of element ({line}:{col})", DebugLevel.DEBUG)
                        closeToken = True
                        
                        self.tree.content = content[self.tree.index:index]
                        self.tree = self.tree.moveUp()
                        self.tree.content = content[self.tree.index:index]

                if closeToken:
                    #self.tree.content = content[self.tree.index:index+1]
                    self.tree = self.tree.moveUp()

                """
                    Beginning of tokens
                """
                if not isinstance(self.tree, TokenString) and not closeToken:
                    token = -1

                    if char == '"' or char == "'":
                        self.interpreter.log(
                            f"  Start of string ({line}:{col})", DebugLevel.DEBUG)
                        token = TokenString

                    elif char == "[":
                        self.interpreter.log(
                            f"  Start of list ({line}:{col})", DebugLevel.DEBUG)
                        token = TokenList

                    elif char == "(":
                        self.interpreter.log(
                            f"  Start of parenthesis ({line}:{col})", DebugLevel.DEBUG)
                        token = TokenParenthesis

                    elif char == "{":
                        self.interpreter.log(
                            f"  Start of block ({line}:{col})", DebugLevel.DEBUG)
                        token = TokenBlock

                    elif char in operators:
                        self.interpreter.log(
                            f"  Operator ({line}:{col})", DebugLevel.DEBUG)
                        
                        self.tree.content = content[self.tree.index:index]
                        
                        op = TokenOperator(index, line, col, char, self.tree.moveUp())
                        op.operands.append(self.tree)
                        
                        self.tree = self.tree.moveUp()
                        
                        self.tree.tokens[-1] = op
                        token = -2

                    elif isinstance(self.tree, (TokenBlock, TokenParenthesis)):
                        self.interpreter.log(
                            f"  Start of expression ({line}:{col})", DebugLevel.DEBUG)
                        token = TokenExpression
                    
                    if token != -1:
                        self.tree.content = content[self.tree.index:index]
                    
                        if token != -2:
                            token = token(index, line, col, char, self.tree)
                            self.tree.tokens.append(token)

                            self.tree = token
                            self.tree.content += char

            if self.tree is None:  # means a certain token doesn't have a parent but was closed
                extract = content[index-5:index+5]
                raise SyntaxError(
                    f"Invalid syntax at line {line} (col {col}): {extract}")
            
            if skip:
                skip -= 1

            # Move forward
            col += 1
            if char == "\n":
                line += 1
                col = 0

            index += 1

            # Reached end of file
            if index >= len(content):
                break

        self.tree = self.tree.moveTop()
        self.tree.content = content
        self.interpreter.log("End tokenization", DebugLevel.DEBUG)

        #self.tree.display()


class Token:
    name = "Token"

    def __init__(self, index, line, col, content="", parent=None):
        self.index = index
        self.line = line
        self.col = col
        self.content = content
        self.tokens = []
        self.parent = parent

    def moveUp(self):
        return self.parent

    def moveTop(self):
        if not self.parent is None:
            return self.parent.moveTop()

        return self

    def display(self, indent=0):
        c = self.content.replace('\n', '\\n')
        print(" "*indent + self.name + f" -> '{c}'")

        for token in self.tokens:
            token.display(indent+1)


class TokenBlock(Token):
    name = "Block"
    #def __init__(self, index, line, col, content):
    #    super().__init__(self, index, line, col, content)


class TokenString(Token):
    name = "String"
    #def __init__(self, index, line, col, content):
    #    super().__init__(self, index, line, col, content)


class TokenFunction(Token):
    name = "Function"
    #def __init__(self, index, line, col, content):
    #    super().__init__(self, index, line, col, content)


class TokenList(Token):
    name = "List"
    #def __init__(self, index, line, col, content):
    #    super().__init__(self, index, line, col, content)


class TokenParenthesis(Token):
    name = "Parenthesis"
    #def __init__(self, index, line, col, content):
    #    super().__init__(self, index, line, col, content)


class TokenExpression(Token):
    name = "Expression"
    #def __init__(self, index, line, col, content):
    #    super().__init__(self, index, line, col, content)


class TokenOperator(Token):
    name = "Operator"
    
    def __init__(self, index, line, col, content, parent):
        super().__init__(index, line, col, content, parent)
        
        if content in unary_op:
            self.argc = 1
        
        else:
            self.argc = 2
        
        self.operands = []