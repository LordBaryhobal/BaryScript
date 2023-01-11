#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs_symbols import *

class SymbolBuiltin(SymbolFunction):
    name = "Symbol builtin"

    def __init__(self, func):
        self.func = func

    def call(self, context, *args, **kwargs):
        return self.func(context, *args, **kwargs)
    
    def __repr__(self):
        return self.func.__name__

class GlobalContext(Context):
    def __init__(self):
        self.symbols = {
            "print": func_print,
            "dbg_ctxt": func_dbg_ctxt
        }

def print_(ctxt, *args, **kwargs):
    #print("Print <")
    print(*[arg.eval(ctxt) for arg in args])
    #print(">")

def dbg_ctxt(ctxt, *args, **kwargs):
    print(ctxt)

func_print = SymbolBuiltin(print_)
func_dbg_ctxt = SymbolBuiltin(dbg_ctxt)