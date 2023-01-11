#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from bs_core import Interpreter
from bs_help import *

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print_help()
    
    else:
        interpreter = Interpreter()
        
        for arg in sys.argv:
            if arg.startswith("--"):
                arg, value = arg.split("=")
                arg = arg[2:]
                
                interpreter.setArg(arg, value)
            
            elif arg.startswith("-"):
                interpreter.setFlag(arg[1:])
            
            else:
                interpreter.setFile(arg)
        
        interpreter.run()