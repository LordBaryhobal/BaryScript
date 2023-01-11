#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs_const import *
import re

reserved_words = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elif": TokenType.ELIF,
    "for": TokenType.FOR,
    "while": TokenType.WHILE,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "return": TokenType.RETURN,
    "func": TokenType.FUNC
    #"class": TokenType.CLASS
}

operators = [
    "+", "-", "*", "/", "%", "=",
    "<", ">", "!"
]

class Stream:
    def __init__(self, content):
        self.content = content
        self.length = len(content)
        self.pos = 0
    
    def canRead(self):
        return self.pos < self.length
    
    def read(self, count=1, offset=0, stay=False):
        result = ""
        
        if stay:
            start = self.pos
        
        self.move(offset)
        
        if self.pos < 0:
            return result
        
        for i in range(count):
            if not self.canRead():
                break
            
            result += self.content[self.pos]
            
            self.pos += 1
        
        if stay:
            self.goto(start)
        
        return result
    
    def goto(self, p):
        self.pos = p
    
    def move(self, d):
        self.pos += d

class Tokenizer:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.content = Stream(self.interpreter.content)
        
        self.tokens = []
        
        self.current = None
        
        self.line = 0
        self.col = 0
    
    def dbg(self, msg):
        self.interpreter.log(msg, DebugLevel.DEBUG)
    
    def close(self):
        if not self.current is None:
            start, end = self.current.index, self.content.pos-1
            
            if self.current.type == TokenType.STRING:
                start += 1
            
            self.current.content = self.content.content[start:end]
            self.current = None
    
    def add(self, type_):
        self.close()
        token = Token(self.content.pos-1, self.line, self.col, self.char, type_)
        self.tokens.append(token)
    
    def new(self, type_):
        self.close()
        self.current = Token(self.content.pos-1, self.line, self.col, self.char, type_)
        self.tokens.append(self.current)
    
    def newIfNot(self, type_):
        if (self.current is None) or (self.current.type != type_):
            self.new(type_)
    
    def findPrevOpen(self, type_):
        for i in range(len(self.tokens)-1,-1,-1):
            token = self.tokens[i]
            
            if token.type == type_:
                if not hasattr(token, "closing"):
                    return token
        
        return None

    def tokenize(self):
        self.dbg("Start tokenization")

        while self.content.canRead():
            #print(self.content.pos) ### To Remove
            self.char = self.content.read()
            
            inComment = (False if self.current is None else (self.current.type == TokenType.COMMENT))
            inStr = (False if self.current is None else (self.current.type == TokenType.STRING))
            
            if not inComment:
                if inStr:
                    if self.char == '"' or self.char == "'":
                        if self.current and self.current.type == TokenType.STRING and self.current.content[0] == self.char:
                            #self.dbg("End of string") ### To Remove
                            self.close()
                
                
                else:
                    if self.char == "/" and self.content.read(2, -1, True) in ["//", "/*"]:
                        #self.dbg("Start of comment") ### To Remove
                        
                        self.new(TokenType.COMMENT)
                        self.current.content = self.content.read(2, -1, True)
                    
                    elif self.char == ";":
                        #self.dbg("Semi-colon") ### To Remove
                        self.add(TokenType.EOL)
                    
                    elif re.match(r"\s", self.char):
                        #self.dbg("Whitespace") ### To Remove
                        self.newIfNot(TokenType.WHITESPACE)
                    
                    elif self.char == "(":
                        #self.dbg("Opening parenthesis") ### To Remove
                        self.add(TokenType.OPEN_PAR)
                    elif self.char == ")":
                        #self.dbg("Closing parenthesis") ### To Remove
                        prev = self.findPrevOpen(TokenType.OPEN_PAR)
                        
                        if prev is None:
                            raise SyntaxError(f"Opening parenthesis not found ({token.pos})")
                        
                        self.add(TokenType.CLOSE_PAR)
                        token = self.tokens[-1]
                        
                        prev.closing = token
                        token.opening = prev
                    
                    elif self.char == "[":
                        #self.dbg("Opening bracket") ### To Remove
                        self.add(TokenType.OPEN_BRA)
                    elif self.char == "]":
                        #self.dbg("Closing bracket") ### To Remove
                        prev = self.findPrevOpen(TokenType.OPEN_BRA)
                        
                        if prev is None:
                            raise SyntaxError(f"Opening bracket not found ({token.pos})")
                        
                        self.add(TokenType.CLOSE_BRA)
                        token = self.tokens[-1]
                        prev.closing = token
                        token.opening = prev
                    
                    elif self.char == "{":
                        #self.dbg("Opening curly brace") ### To Remove
                        self.add(TokenType.OPEN_CUR)
                    elif self.char == "}":
                        #self.dbg("Closing curly brace") ### To Remove
                        prev = self.findPrevOpen(TokenType.OPEN_CUR)
                        
                        if prev is None:
                            raise SyntaxError(f"Opening curly brace not found ({token.pos})")
                        
                        self.add(TokenType.CLOSE_CUR)
                        token = self.tokens[-1]
                        prev.closing = token
                        token.opening = prev
                    
                    elif self.char == '"' or self.char == "'":
                        #self.dbg("Start of string") ### To Remove
                        self.new(TokenType.STRING)
                    
                    elif (self.current is None or self.current.type != TokenType.NAME) and (re.match(r"\d", self.char)):
                        #self.dbg("Number") ### To Remove
                        self.newIfNot(TokenType.NUMBER)
                    
                    elif (not self.current is None and self.current.type == TokenType.NUMBER) and self.char == ".":
                        #self.dbg("Number (.)") ### To Remove
                        self.newIfNot(TokenType.NUMBER)
                    
                    elif self.char == "-" and re.match(r"\d", self.content.read(stay=True)):
                        #self.dbg("Number (-)") ### To Remove
                        self.newIfNot(TokenType.NUMBER)
                    
                    elif self.char in operators:
                        #self.dbg("Operator") ### To Remove
                        self.newIfNot(TokenType.OPERATOR)
                    
                    elif self.char == ",":
                        self.close()
                    
                    else:
                        isReserved = False
                        for k in reserved_words.keys():
                            if self.content.read(len(k), -1, True) == k:
                                isReserved = True
                                self.new(reserved_words[k])
                                self.content.move(len(k))
                                self.close()
                                self.content.move(-1)
                                break
                        
                        if not isReserved:
                            #self.dbg("Name") ### To Remove
                            self.newIfNot(TokenType.NAME)
                
            
            else:
                if self.current.content.startswith("//"):
                    if self.char == "\n":
                        #self.dbg("End of comment") ### To Remove
                        self.close()
                
                elif self.current.content.startswith("/*"):
                    if self.content.read(2, -2, True) == "*/":
                        #self.dbg("End of mutliline comment") ### To Remove
                        self.close()
        
        #Post-tokenization checks
        for token in self.tokens:
            #Check if all parentheses/brackets/curly braces are closed
            if token.type in [TokenType.OPEN_PAR,TokenType.OPEN_BRA,TokenType.OPEN_CUR]:
                if not hasattr(token, "closing"):
                    type_ = {
                        TokenType.OPEN_PAR: "parenthesis",
                        TokenType.OPEN_BRA: "bracket",
                        TokenType.OPEN_CUR: "curly brace"
                    }[token.type]
                    raise SyntaxError(f"{type_.capitalize()} not closed at {token.pos}")
        
        
        self.dbg("End tokenization")


class Token:
    name = "Token"

    def __init__(self, index, line, col, content, type_=TokenType.OTHER):
        self.index = index
        self.line = line
        self.col = col
        
        self.content = content
        self.type = type_
    
    def __repr__(self):
        name = TokenType.names[self.type]
        c = self.content.replace('\n', '\\n')
        
        return f"<{name} -> '{c}'>"
    
    """
        TODO:
        change to return line and column
    """
    @property
    def pos(self):
        return self.index