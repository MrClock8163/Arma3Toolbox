class CFG_Error(Exception):
    def __str__(self):
        return "CFG - %s" % super().__str__()


class CFGNode:
    pass


class CFGLiteralString(CFGNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "\"%s\"" % self.value

    def topy(self):
        return self.value

    def format(self, indent=0):
        return "%s\"%s\"" % ("\t" * indent, self.value.replace("\"", "\"\""))


class CFGLiteralLong(CFGNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "%f" % self.value

    def topy(self):
        return self.value

    def format(self, indent=0):
        return "%s%d" % ("\t" * indent, self.value)


class CFGLiteralFloat(CFGNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "%f" % self.value

    def topy(self):
        return self.value

    def format(self, indent=0):
        return "%s%f" % ("\t" * indent, self.value)


class CFGArray(CFGNode):
    def __init__(self, members, extends=False):
        self.members = members
        self.extends = extends

    def __repr__(self):
        return "{ len = %d }" % len(self.members)

    def topy(self):
        out = []

        for item in self.members:
            out.append(item.topy())

        return out

    def format(self, indent=0):
        padding = "\t" * indent

        if len(self.members) == 0:
            return "%s{}\n" % padding

        value = "%s{\n" % ("\t" * indent)
        items = []
        for item in self.members:
            items.append(item.format(indent + 1))

        value += ",\n".join(items) + "\n"
        value += "%s}\n" % ("\t" * indent)

        return value


class CFGProperty(CFGNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    @classmethod
    def type_from_py(cls, value):
        valuetype = type(value)
        if valuetype not in (str, int, float, list):
            raise ValueError("Could not create value (%s) from type (%s)" % (value, valuetype))

        if valuetype is str:
            return CFGLiteralString(value)
        elif valuetype is int:
            return CFGLiteralLong(value)
        elif valuetype is float:
            return CFGLiteralFloat(value)

        members = []
        for item in value:
            members.append(cls.type_from_py(item))

        return CFGArray(members)

    @classmethod
    def from_py(cls, name, value):
        if type(name) is not str or len(name) < 1:
            raise ValueError("Cannot create property (%s) without valid name (%s)" % (value, name))

        return cls(name, cls.type_from_py(value))

    def __repr__(self):
        return "%s = %s" % (self.name, repr(self.value))

    def format(self, indent=0):
        value = ""
        padding = "\t" * indent
        if type(self.value) is CFGArray:
            if len(self.value.members) == 0:
                return "%s%s[] = {};\n" % (padding, self.name)

            value = "%s%s[] = {\n" % (padding, self.name)
            items = []
            for item in self.value.members:
                items.append(item.format(indent + 1))

            value += ",\n".join(items) + "\n"
            value += "%s};\n" % padding
        else:
            value = "%s%s = %s;\n" % (padding, self.name, self.value.format())

        return value


class CFGClass(CFGNode):
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

    @classmethod
    def resolve_parent(cls, main, parentname):
        if not main:
            return None

        for item in main.classes:
            if item.name.lower() == parentname.lower():
                return item

        if main.parent is None:
            return None

        return cls.resolve_parent(main.parent, parentname)

    def get_class(self, steps):
        if len(steps) == 0:
            return self

        step = steps.pop(0).lower()
        for item in self.classes:
            if item.name.lower() == step:
                if len(steps) == 0:
                    return item

                return item.get_class(steps)

        if self.parent is None:
            return None

        steps.insert(0, step)
        return self.parent.get_class(steps)

    def get_prop(self, propname, default=None):
        for item in self.properties:
            if item.name.lower() == propname.lower():
                return item.value

        if self.parent is None:
            return default

        return self.parent.get_prop(propname, default)

    def get_path(self):
        steps = [self.name]
        main = self.main
        while main is not None:
            steps.insert(0, main.name)

            main = main.main

        return "/".join(steps)

    def format(self, indent=0):
        padding = "\t" * indent
        value = ""

        if self.isref:
            return "%sclass %s;\n" % (padding, self.name)

        if self.parent is not None:
            value += "%sclass %s: %s {" % (padding, self.name, self.parent.name)
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

    def as_dict(self):
        propdict = {}
        classdict = {}
        data = {
            "properties": propdict,
            "classes": classdict,
            "isref": self.isref,
            "parent": self.parent.name if self.parent else None
        }

        for prop in self.properties:
            propdict[prop.name] = prop.value.topy()

        for cls in self.classes:
            classdict[cls.name] = cls.as_dict()

        return data

    @classmethod
    def from_dict(cls, name, main, data):
        parent = None
        parentname = data.get("parent")
        if parentname is not None:
            parent = cls.resolve_parent(main, parentname)
            if not parent:
                raise CFG_Error("Could not resolve parent (%s) of (%s) in (%s)" % (parentname, name, main.get_path()))

        out = cls(name, parent, main, data.get("isref", False))

        for name, value in data.get("properties", {}).items():
            out.properties.append(CFGProperty.from_py(name, value))

        for name, item in data.get("classes", {}).items():
            out.classes.append(CFGClass.from_dict(name, out, item))

        return out


class CFG:
    def __init__(self, root):
        self.root = root

    def __repr__(self):
        return "CFG: %s" % self.root.name

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

    def as_dict(self):
        return {self.root.name: self.root.as_dict()}

    @classmethod
    def from_dict(cls, data):
        if len(data) != 1:
            raise ValueError("Root node must be a single key: %s" % list(data.keys()))

        name = list(data.keys())[0]
        root = CFGClass.from_dict(name, None, data[name])

        return cls(root)
