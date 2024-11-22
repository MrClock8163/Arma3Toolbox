from importlib import reload


if "data" in locals():
    reload(data)
if "tokenizer" in locals():
    reload(tokenizer)
if "parser" in locals():
    reload(parser)


from . import data
from . import tokenizer
from . import parser


def tokenize(file):
    return tokenizer.CFGTokenizer(file).all()


def tokenize_file(path):
    with open(path, "rt") as file:
        return tokenize(file)


def wrap(tokens, wrapper):
    if wrapper == "":
        raise ValueError("Cannot add wrapper tokens with empty class name")

    wrapped = [tokenizer.TClass(), tokenizer.TIdentifier(wrapper), tokenizer.TBraceOpen()]
    wrapped.extend(tokens)
    wrapped.extend([tokenizer.TBraceClose(), tokenizer.TSemicolon()])
    return wrapped


def parse(tokens):
    return parser.CFGParser(tokens).parse()


def print_tokens(tokens):
    tokenizer.print_tokens(tokens)
