from . import tokenizer as t


class ASTNode:
    pass


class ASTLiteralString(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "\"%s\"" % self.value

    def topy(self):
        return self.value

    def format(self, indent=0):
        return "%s\"%s\"" % ("\t" * indent, self.value.replace("\"", "\"\""))


class ASTLiteralLong(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "%f" % self.value

    def topy(self):
        return self.value

    def format(self, indent=0):
        return "%s%d" % ("\t" * indent, self.value)


class ASTLiteralFloat(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "%f" % self.value

    def topy(self):
        return self.value

    def format(self, indent=0):
        return "%s%f" % ("\t" * indent, self.value)


class ASTArray(ASTNode):
    def __init__(self, members, extends=False):
        self.members = members
        self.extends = extends

    def __repr__(self):
        return "{...}"

    def topy(self):
        out = []

        for item in self.members:
            out.append(item.topy())

        return out

    def format(self, indent=0):
        padding = "\t" * indent

        if len(self.members) == 0:
            return "%s\{\}\n" % padding

        value = "%s{\n" % ("\t" * indent)
        items = []
        for item in self.members:
            items.append(item.format(indent + 1))

        value += ",\n".join(items) + "\n"
        value += "%s}\n" % ("\t" * indent)

        return value


class ASTProperty(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "%s = %s" % (self.name, repr(self.value))

    def format(self, indent=0):
        value = ""
        padding = "\t" * indent
        if type(self.value) is ASTArray:
            if len(self.value.members) == 0:
                return "%s%s[] = \{\};\n" % (padding, self.name)

            value = "%s%s[] = {\n" % (padding, self.name)
            items = []
            for item in self.value.members:
                items.append(item.format(indent + 1))

            value += ",\n".join(items) + "\n"
            value += "%s};\n" % padding
        else:
            value = "%s%s = %s;\n" % (padding, self.name, self.value.format())

        return value


class ASTClass(ASTNode):
    def __init__(self, name, parent=None, main=None, isref=False):
        self.name = name
        self.parent = parent
        self.properties = []
        self.classes = []
        self.main = main
        self.isref = isref

    def __repr__(self):
        if self.isref:
            return "class %s;" % self.name
        elif self.parent is None:
            return "class %s" % self.name

        return "class %s: %s" % (self.name, self.parent.name)

    def get_class(self, steps):
        if len(steps) == 0:
            return self

        step = steps.pop(0)
        for item in self.classes:
            if item.name == step:
                if len(steps) == 0:
                    return item

                return item.get_class(steps)

        if self.parent is None:
            return None

        steps.insert(0, step)
        return self.parent.get_class(steps)

    def get_prop(self, propname, default=None):
        for item in self.properties:
            if item.name == propname:
                return item.value

        if self.parent is None:
            return default

        return self.parent.get_prop(propname, default)

    def format(self, indent=0):
        padding = "\t" * indent
        value = ""

        if self.isref:
            return "%sclass %s;\n" % (padding, self.name)

        if self.parent is not None:
            value += "%sclass %s: %s {" % (padding,
                                           self.name, self.parent.name)
        else:
            value += "%sclass %s {" % (padding, self.name)

        if len(self.properties) == 0 and len(self.classes) == 0:
            value += "};"
            return value
        else:
            value += "\n"

        for prop in self.properties:
            value += prop.format(indent + 1)

        for cls in self.classes:
            value += cls.format(indent + 1)

        value += "%s};\n" % padding
        return value


class AST:
    def __init__(self, root):
        self.root = root

    def __repr__(self):
        return "AST"

    def get_class(self, path):
        steps = path.replace(" ", "").split("/")
        step = steps.pop(0)
        if step != self.root.name:
            return None
        elif len(steps) == 0:
            return self.root

        return self.root.get_class(steps)

    def get_prop(self, path, default=None):
        steps = path.replace(" ", "").split("/")
        step = steps.pop(0)

        if len(steps) == 0 or step != self.root.name:
            return default

        propname = steps.pop()
        leaf = self.root.get_class(steps)
        if leaf is None:
            return default

        return leaf.get_prop(propname, default)

    def format(self):
        value = ""
        for prop in self.root.properties:
            value += prop.format()

        for cls in self.root.classes:
            value += cls.format()

        return value


class Parser:
    def __init__(self, tokens):
        self.ptr = 0
        self.tokens = tokens

    @classmethod
    def from_lexxer(cls, lex):
        return cls(lex.all())

    def read_token(self, count=1):
        if self.ptr == len(self.tokens):
            return []

        if count == 1:
            result = self.tokens[self.ptr]
            self.ptr += 1
            return result

        tokens = self.tokens[self.ptr:self.ptr+count]
        self.ptr += len(tokens)
        return tokens

    def peek_token(self, count=1):
        if self.ptr == len(self.tokens):
            return []

        if count == 1:
            return self.tokens[self.ptr]

        tokens = self.tokens[self.ptr:self.ptr+count]
        return tokens

    def seek_token(self, offset, ref):
        token_count = len(self.tokens)
        if ref == 2:
            offset += token_count - 1
        elif ref == 1:
            offset += self.ptr

        if not (0 <= offset < token_count):
            raise ValueError("Offset out of range")

        self.ptr = offset

    @staticmethod
    def compare_tokens(got, expected):
        for t, exp in zip(got, expected):
            if exp is not None and type(t) is not exp:
                return False

        return True

    def parse_identifier(self):
        value = ""
        nexttoken = self.peek_token()
        while nexttoken and type(nexttoken) in (t.TIdentifier, t.TLiteralLong):
            value += str(nexttoken.value)
            self.read_token()
            nexttoken = self.peek_token()

        if value == "":
            return None

        return t.TIdentifier(value)

    def recover_literal(self):
        values = []
        nexttoken = self.peek_token()
        while nexttoken and type(nexttoken) in (t.TIdentifier, t.TLiteralLong, t.TLiteralFloat, t.TLiteralString):
            values.append(nexttoken)
            self.read_token()
            nexttoken = self.peek_token()

        return t.TLiteralString(" ".join([("\"\"%s\"\"" % t.value) if type(t) is t.TLiteralString else str(t.value) for t in values]))

    def parse_literal(self):
        items = []
        while self.peek_token() and type(self.peek_token()) not in (t.TComma, t.TSemicolon, t.TBraceClose):
            items.append(self.read_token())

        count = len(items)

        if count == 0:
            return ASTLiteralString("")

        if count == 1:
            itemtype = type(items[0])
            if itemtype is t.TLiteralString:
                return ASTLiteralString(items[0].value)
            elif itemtype is t.TLiteralLong:
                return ASTLiteralLong(items[0].value)
            elif itemtype is t.TLiteralFloat:
                return ASTLiteralFloat(items[0].value)

            return ASTLiteralString(str(items[0]))

        if count == 2 and type(items[0]) in (t.TPlus, t.TMinus):
            if type(items[1]) is t.TLiteralLong:
                return ASTLiteralLong(items[1].value * (-1 if type(items[0]) is t.TMinus else 1))
            elif type(items[1]) is t.TLiteralFloat:
                return ASTLiteralFloat(items[1].value * (-1 if type(items[0]) is t.TMinus else 1))

        return ASTLiteralString(" ".join([("\"%s\"" % t) if type(t) is t.TLiteralString else str(t) for t in items]))

    def parse_array(self):
        if type(self.read_token()) is not t.TBraceOpen:
            raise Exception("Unexpected token at array start")

        nexttoken = self.peek_token()
        if nexttoken and type(nexttoken) is t.TBraceClose:
            self.read_token()
            return ASTArray([])

        members = []
        while nexttoken and type(nexttoken) is not t.TBraceClose:
            if type(nexttoken) is t.TBraceOpen:
                members.append(self.parse_array())

            elif type(nexttoken) is t.TComma:
                self.read_token()
            else:
                nexttype = type(nexttoken)
                new = None
                if nexttype is t.TLiteralString:
                    new = ASTLiteralString(nexttoken.value)
                elif nexttype is t.TLiteralLong:
                    new = ASTLiteralLong(nexttoken.value)
                else:
                    new = ASTLiteralFloat(nexttoken.value)

                members.append(new)
                self.read_token()

            nexttoken = self.peek_token()

        self.read_token()

        return ASTArray(members)

    def parse_property(self):
        name = self.parse_identifier()
        if not name:
            raise Exception("Could not parse property name")

        value = None
        if type(self.peek_token()) is t.TEquals:
            self.read_token()
            value = self.parse_literal()
            end = self.read_token()
            if not end or type(end) is not t.TSemicolon:
                raise Exception("Expected semicolon after property assignment")

        elif self.compare_tokens(self.peek_token(2), [t.TBracketOpen, t.TBracketClose]):
            self.read_token(2)
            operator = self.read_token()
            if not operator or type(operator) not in (t.TEquals, t.TPlusEquals):
                raise Exception("Unexpected array assignment operator")

            value = self.parse_array()
            if type(operator) is t.TPlusEquals:
                value.extends = True

            end = self.read_token()
            if not end or type(end) is not t.TSemicolon:
                raise Exception("Expected semicolon after property assignment")

        return ASTProperty(name.value, value)

    def resolve_parent(self, main, parentname):
        for item in main.classes:
            if item.name == parentname:
                return item

        if main.parent is None:
            return None

        return self.resolve_parent(main.parent, parentname)

    def parse_class_header(self, main=None):
        self.read_token()  # skip class keyword
        name = self.parse_identifier()
        if not name:
            raise Exception("Could not parse class name")

        delimiter = self.read_token()
        delimitertype = type(delimiter)
        if delimitertype not in (t.TColon, t.TSemicolon, t.TBraceOpen):
            raise Exception("Unexpected token after class name")

        if delimitertype is t.TSemicolon:
            return ASTClass(name.value, None, main, isref=True)
        elif delimitertype is t.TBraceOpen:
            return ASTClass(name.value, None, main)

        parentname = self.parse_identifier()
        if not parentname:
            raise Exception("Could not parse class parent name")

        parent = self.resolve_parent(main, parentname.value)
        if not parent:
            raise Exception("Could not resolve class parent")

        end = self.read_token()
        if not end or type(end) is not t.TBraceOpen:
            raise Exception("Unexpected token")

        return ASTClass(name.value, parent, main)

    def parse_class(self, main=None):
        new = self.parse_class_header(main)
        if new.isref:
            return new

        clses = set()
        props = set()
        newclass = None
        newprop = None

        peeked = self.peek_token()
        peekedtype = None
        while peeked and type(peeked) is not t.TBraceClose:
            peekedtype = type(peeked)
            if peekedtype is t.TDel:
                raise Exception("Class deletion syntax is not supported")
            elif peekedtype is t.TEnum:
                raise Exception("Enum syntax is not supported")
            elif peekedtype is t.TClass:
                newclass = self.parse_class(new)
                if newclass.name in clses:
                    raise Exception("Duplicate class definition")
                clses.add(newclass.name)
                new.classes.append(newclass)
            else:
                newprop = self.parse_property()
                if newprop.name not in props:
                    props.add(newprop.name)
                    new.properties.append(newprop)

            peeked = self.peek_token()

        if not self.compare_tokens(self.read_token(2), [t.TBraceClose, t.TSemicolon]):
            raise Exception("Unexpected class ending")

        return new

    def parse(self):
        root = self.parse_class()
        return AST(root)
