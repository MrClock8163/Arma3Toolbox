# Reader function to import data from rapified files.
# Format specifications: https://community.bistudio.com/wiki/raP_File_Format_-_Elite


from enum import Enum

from . import binary_handler as binary
from ..utilities import errors


# Internal data structure to store the read data.
class Cfg():
    class EntryType(Enum):
        CLASS = 0
        SCALAR = 1
        ARRAY = 2
        EXTERN = 3
        DELETE = 4
        FLAGGED = 5

    class EntrySubType(Enum):
        NONE = 0
        STRING = 1
        FLOAT = 2
        LONG = 3
        ARRAY = 4
        VARIABLE = 5

    class EnumItem():
        def __init__(self):
            self.name = ""
            self.value = 0
        
        def __str__(self):
            return "%s = %s" % (self.name, self.value)

    class ClassBody():    
        def __init__(self):
            self.inherits = ""
            self.entry_count = 0
            self.entries = []
        
        def __str__(self):
            return "Inherits: %s" % (self.inherits if self.inherits != "" else "nothing")
        
        def find(self, name):
            for item in self.entries:
                if item.name.lower() == name.lower():
                    return item

    class Entry():
        def __init__(self):
            self.type = Cfg.EntryType.CLASS
            self.subtype = Cfg.EntrySubType.NONE
            self.name = ""
            self.value = ""

    class Class():
        def __init__(self):
            self.type = Cfg.EntryType.CLASS
            self.subtype = Cfg.EntrySubType.NONE
            self.name = ""
            self.value = ""
            self.body_offset = 0
            self.body = Cfg.ClassBody()
        
        def __str__(self):
            if self.body:
                return "class %s {%d}" % (self.name, self.body.entry_count)
            return "class %s {...}" % self.name

    class Scalar():
        def __init__(self):
            self.type = Cfg.EntryType.SCALAR
            self.subtype = Cfg.EntrySubType.NONE
            self.name = ""
            self.value = ""

    class String():
        def __init__(self):
            self.type = Cfg.EntryType.SCALAR
            self.subtype = Cfg.EntrySubType.STRING
            self.name = ""
            self.value = ""
        
        def __str__(self):
            if self.name != "":
                return "%s = \"%s\";" % (self.name, self.value)
            return "\"%s\"" % self.value

    class Float():
        def __init__(self):
            self.type = Cfg.EntryType.SCALAR
            self.subtype = Cfg.EntrySubType.FLOAT
            self.name = ""
            self.value = 0.0
        
        def __str__(self):
            if self.name != "":
                return "%s = %f;" % (self.name, self.value)
            return "%f" % self.value

    class Long():
        def __init__(self):
            self.type = Cfg.EntryType.SCALAR
            self.subtype = Cfg.EntrySubType.LONG
            self.name = ""
            self.value = 0
        
        def __str__(self):
            if self.name != "":
                return "%s = %d;" % (self.name, self.value)
            return "%d" % self.value

    class Variable():
        def __init__(self):
            self.type = Cfg.EntryType.SCALAR
            self.subtype = Cfg.EntrySubType.VARIABLE
            self.name = ""
            self.value = ""
        
        def __str__(self):
            if self.name != "":
                return "%s = ""%s"";" % (self.name, self.value)
            return "\"%s\"" % self.value

    class ArrayBody():
        def __init__(self):
            self.type = Cfg.EntryType.ARRAY
            self.subtype = Cfg.EntrySubType.NONE
            self.name = ""
            self.value = ""
            self.element_count = 0
            self.elements = []

    class Array():
        def __init__(self):
            self.type = Cfg.EntryType.ARRAY
            self.subtype = Cfg.EntrySubType.NONE
            self.name = ""
            self.value = ""
            self.body = Cfg.ArrayBody()
            self.flag = None
        
        def __str__(self):
            if self.body:
                return "%s[] = {%d};" % (self.name, self.body.element_count)
            return "%s[] = {...};" % self.name

    class External():
        def __init__(self):
            self.type = Cfg.EntryType.EXTERN
            self.subtype = Cfg.EntrySubType.NONE
            self.name = ""
            self.value = ""
        
        def __str__(self):
            return "class %s;" % self.name

    class Delete():
        def __init__(self):
            self.type = Cfg.EntryType.DELETE
            self.subtype = Cfg.EntrySubType.NONE
            self.name = ""
            self.value = ""
        
        def __str__(self):
            return "delete %s;" % self.name

    class Root():
        def __init__(self):
            self.enum_offset = 0
            self.body = Cfg.ClassBody()
            self.enums = []


class CFGReader():
    @classmethod
    def read_entry_class_body(cls, file, body_offset):
        output = Cfg.ClassBody()
        current_pos = file.tell()
        file.seek(body_offset, 0)
        
        output.inherits = binary.read_asciiz(file)
        output.entry_count = binary.read_compressed_uint(file)
        output.entries = cls.read_entries(file, output.entry_count)
        
        file.seek(current_pos, 0)
        
        return output
    
    @classmethod
    def read_entry_class(cls, file):
        output = Cfg.Class()
        
        output.name = binary.read_asciiz(file)
        output.body_offset = binary.read_ulong(file)
        output.body = cls.read_entry_class_body(file, output.body_offset)
        
        return output
    
    @classmethod
    def read_entry_value(cls, file, sign):
        output = Cfg.Scalar()
        
        if sign == 0:
            output = Cfg.String()
            output.value = binary.read_asciiz(file)
        
        elif sign == 1:
            output = Cfg.Float()
            output.value = binary.read_float(file)
        
        elif sign == 2:
            output = Cfg.Long()
            output.value = binary.read_long(file)
        
        elif sign == 3:
            output = cls.read_entry_array_body(file)
            
        elif sign == 4:
            output = Cfg.Variable()
            output.value = binary.read_asciiz(file)
            
        return output
            
    
    @classmethod
    def read_entry_scalar(cls, file):
        entry_sign = binary.read_byte(file)
        entry_name = binary.read_asciiz(file)
        
        output = cls.read_entry_value(file, entry_sign)
        output.name = entry_name
        
        return output
    
    @classmethod
    def read_entry_array_body(cls, file):
        output = Cfg.ArrayBody()
        output.element_count = binary.read_compressed_uint(file)
        
        for i in range(output.element_count):
            output.elements.append(cls.read_entry_value(file, binary.read_byte(file)))
        
        return output
        
    @classmethod
    def read_entry_array(cls, file):
        output = Cfg.Array()
        output.name = binary.read_asciiz(file)
        output.body = cls.read_entry_array_body(file)
        
        return output
    
    @classmethod
    def read_entry_array_flagged(cls, file):
        output = Cfg.Array()
        output.flag = binary.read_long(file)
        output.name = binary.read_asciiz(file)
        output.body = cls.read_entry_array_body(file)
        
        return output
    
    @classmethod
    def read_entry_class_external(cls, file):
        output = Cfg.External()
        output.name = binary.read_asciiz(file)
        
        return output
    
    @classmethod
    def read_entry_class_delete(cls, file):
        output = Cfg.Delete()
        output.name = binary.read_asciiz(file)
        
        return output
    
    @classmethod
    def read_entry(cls, file):
        output = Cfg.Entry()
        entry_sign = binary.read_byte(file)
        
        if entry_sign == 0:
            output = cls.read_entry_class(file)
            
        elif entry_sign == 1:
            output = cls.read_entry_scalar(file)
            
        elif entry_sign == 2:
            output = cls.read_entry_array(file)
            
        elif entry_sign == 3:
            output = cls.read_entry_class_external(file)
            
        elif entry_sign == 4:
            output = cls.read_entry_class_delete(file)
            
        elif entry_sign == 5:
            output = cls.read_entry_array_flagged(file)
        
        return output
    
    @classmethod
    def read_entries(cls, file, entry_count):
        output = []
        
        for i in range(entry_count):
            output.append(cls.read_entry(file))
        
        return output
    
    @classmethod
    def derapify(cls, filepath):
        output = Cfg.Root()
        
        with open(filepath, "rb") as file:
            try:
                # Do header validation
                file.read(4)
                
                padding1 = binary.read_ulong(file)
                padding2 = binary.read_ulong(file)
                
                if not (padding1 == 0 and padding2 == 8):
                    padding1 = binary.read_ulong(file)
                    padding2 = binary.read_ulong(file)
                       
                    if not (padding1 == 0 and padding2 == 8):
                        file.read(4)
                        padding1 = binary.read_ulong(file)
                        padding2 = binary.read_ulong(file)
                        
                        if not (padding1 == 0 and padding2 == 8):
                            raise errors.RAPError("Invalid file header padding")
                
                output.enum_offset = binary.read_ulong(file)
                
                # Body
                output_body = Cfg.ClassBody()
                output_body.inherits = binary.read_asciiz(file)
                output_body.entry_count = binary.read_compressed_uint(file)
                output_body.entries = cls.read_entries(file, output_body.entry_count)
                
                output.body = output_body
                
                # Enums
                file.seek(output.enum_offset)
                enum_count = binary.read_ulong(file)
                for i in range(enum_count):
                    new_item = Cfg.EnumItem()
                    new_item.name = binary.read_asciiz(file)
                    new_item.value = binary.read_ulong(file)
                    output.enums.append(new_item)
                    
                if file.peek():
                    raise errors.RAPError("Invalid EOF")
                
            except:
                output = None
                
        return output