#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs_symbols import *

class SymbolBuiltin(SymbolFunction):
    name = "Symbol builtin"

    def __init__(self, func):
        self.func = func

    def eval(self, context, *args, **kwargs):
        return self.func(context, *args, **kwargs)

class GlobalContext(Context):
    def __init__(self):
        self.symbols = {
            "print": func_print
        }

def print_(ctxt, *args, **kwargs):
    #print("Print <")
    print(*[arg.eval(ctxt) for arg in args])
    #print(">")

func_print = SymbolBuiltin(print_)