#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from bs_tokens import *
from bs_symbols import *
from bs_const import *


class Interpreter:
    def __init__(self):
        self.filePath = None
        self.context = {
            "log": DebugLevel.DEFAULT
        }

        self.flags = {

        }

    def log(self, msg, level):
        if level & self.context["log"]:
            if level == DebugLevel.DEBUG:
                msg = f"[{ANSI_BOLD}{ANSI_BRIGHT_CYAN}DEBUG{ANSI_CLEAR}] {msg}"

            elif level == DebugLevel.WARNINGS:
                msg = f"[{ANSI_BOLD}{ANSI_BRIGHT_YELLOW}WARNING{ANSI_CLEAR}] {msg}"

            elif level == DebugLevel.ERRORS:
                msg = f"[{ANSI_BOLD}{ANSI_BRIGHT_RED}ERROR{ANSI_CLEAR}] {msg}"

            print(msg)

    def setArg(self, arg, value):
        if arg in self.context.keys():
            if arg == "log":
                try:
                    value = int(value)
                    self.context[arg] = value

                except:
                    if hasattr(DebugLevel, value.upper()):
                        self.context[arg] = getattr(DebugLevel, value.upper())

                    else:
                        raise ValueError(arg, value)

        else:
            print(f"Unknown parameter '{arg}'")

    def setFlag(self, flag):
        if flag in self.flags.keys():
            self.flags[flag] = True

        else:
            print(f"Unknown flag '{flag}'")

    def setFile(self, filePath):
        if not os.path.exists(filePath):
            raise FileNotFoundError(filePath)

        self.filePath = filePath

    def run(self):
        if not self.filePath:
            raise ValueError("Missing file to run")

        if not os.path.exists(self.filePath):
            raise FileNotFoundError(self.filePath)

        self.log("Reading file", DebugLevel.DEBUG)

        with open(self.filePath, "r") as fileToRun:
            self.content = fileToRun.read()

        self.log(
            f"{ANSI_BRIGHT_GREEN}File read succesfully{ANSI_CLEAR}", DebugLevel.DEBUG)

        self.tokenizer = Tokenizer(self)
        self.tokenizer.tokenize()
        
        self.tokens = self.tokenizer.tokens

        print(self.tokens)

        self.log(
            f"{ANSI_BRIGHT_GREEN}Tokenized succesfully{ANSI_CLEAR}", DebugLevel.DEBUG)

        self.symbolizer = Symbolizer(self)
        self.symbolizer.symbolize()

        self.symbolizer.tree.display() ### TO REMOVE

        self.log(f"{ANSI_BRIGHT_GREEN}Symbolized succesfully{ANSI_CLEAR}", DebugLevel.DEBUG)

        program = self.symbolizer.tree

        self.log(f"{ANSI_BRIGHT_GREEN}Succseful anaylsis{ANSI_CLEAR}", DebugLevel.DEBUG)

        self.log(f"Starting execution\n", DebugLevel.DEBUG)

        ##import code
        ##code.interact(local=locals())
        
        try:
            program.eval(GlobalContext())
        except Exception as e:
            input(f"Exception -> {e}")

        self.log(f"\n{ANSI_BRIGHT_GREEN}Executed succesfully{ANSI_CLEAR}", DebugLevel.NORMAL)
        self.log(f"Return value: {program.value}", DebugLevel.NORMAL)
