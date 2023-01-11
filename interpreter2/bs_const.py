#!/usr/bin/env python
# -*- coding: utf-8 -*-

VERSION = (0, 0, 1, "A")
INDENT_SIZE = 4

class DebugLevel:
    NONE = 0
    NORMAL = 1
    WARNINGS = 2
    ERRORS = 4
    DEBUG = 8
    
    DEFAULT = 7 # ERRORS + WARNINGS + NORMAL
    VERBOSE = 15 # DEBUG + ERRORS + WARNINGS + NORMAL

class TokenType:
    OTHER = 0
    BREAK = 1
    CLOSE_BRA = 2
    CLOSE_CUR = 3
    CLOSE_PAR = 4
    COMMENT = 5
    CONTINUE = 6
    ELIF = 7
    ELSE = 8
    EOL = 9
    FOR = 10
    FUNC = 11
    GENERIC = 12
    IF = 13
    NAME = 14
    NUMBER = 15
    OPEN_BRA = 16
    OPEN_CUR = 17
    OPEN_PAR = 18
    OPERATOR = 19
    RETURN = 20
    STRING = 21
    WHILE = 22
    WHITESPACE = 23
    
    names = [
        "Other",
        "Break",
        "Close bracket",
        "Close curly",
        "Close parenthesis",
        "Comment",
        "Continue",
        "Elif",
        "Else",
        "EOL",
        "For",
        "Func",
        "Generic",
        "If",
        "Name",
        "Number",
        "Open bracket",
        "Open curly",
        "Open parenthesis",
        "Operator",
        "Return",
        "String",
        "While",
        "Whitespace"
    ]

ANSI_CLEAR = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_FAINT = "\033[2m"
ANSI_ITALIC = "\033[3m"
ANSI_UNDERLINE = "\033[4m"

ANSI_BLACK = "\033[30m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_BLUE = "\033[34m"
ANSI_MAGENTA = "\033[35m"
ANSI_CYAN = "\033[36m"
ANSI_WHITE = "\033[37m"

ANSI_BLACK_BG = "\033[40m"
ANSI_RED_BG = "\033[41m"
ANSI_GREEN_BG = "\033[42m"
ANSI_YELLOW_BG = "\033[43m"
ANSI_BLUE_BG = "\033[44m"
ANSI_MAGENTA_BG = "\033[45m"
ANSI_CYAN_BG = "\033[46m"
ANSI_WHITE_BG = "\033[47m"

ANSI_BRIGHT_BLACK = "\033[90m"
ANSI_BRIGHT_RED = "\033[91m"
ANSI_BRIGHT_GREEN = "\033[92m"
ANSI_BRIGHT_YELLOW = "\033[93m"
ANSI_BRIGHT_BLUE = "\033[94m"
ANSI_BRIGHT_MAGENTA = "\033[95m"
ANSI_BRIGHT_CYAN = "\033[96m"
ANSI_BRIGHT_WHITE = "\033[97m"

ANSI_BRIGHT_BLACK_BG = "\033[100m"
ANSI_BRIGHT_RED_BG = "\033[101m"
ANSI_BRIGHT_GREEN_BG = "\033[102m"
ANSI_BRIGHT_YELLOW_BG = "\033[103m"
ANSI_BRIGHT_BLUE_BG = "\033[104m"
ANSI_BRIGHT_MAGENTA_BG = "\033[105m"
ANSI_BRIGHT_CYAN_BG = "\033[106m"
ANSI_BRIGHT_WHITE_BG = "\033[107m"