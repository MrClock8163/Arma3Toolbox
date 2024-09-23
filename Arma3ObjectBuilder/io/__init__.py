import os
from datetime import datetime

from . import binary_handler
from . import compression
from . import data_asc
from . import data_p3d
from . import data_rap
from . import data_rtm
from . import data_tbcsv
from . import export_asc
from . import export_mcfg
from . import export_p3d
from . import export_rtm
from . import export_tbcsv
from . import import_armature
from . import import_asc
from . import import_mcfg
from . import import_p3d
from . import import_rtm
from . import import_tbcsv


class ExportFileHandler():
    def __init__(self, filepath, mode, backup, preserve_faulty):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.filepath = filepath
        self.temppath = "%s.%s.temp" % (filepath, timestamp)
        self.mode = mode
        self.file = None
        self.backup_old = backup
        self.preserve_faulty = preserve_faulty

    def __enter__(self):
        file = open(self.temppath, self.mode)
        self.file = file

        return file

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()

        if exc_type is None:
            if os.path.isfile(self.filepath) and self.backup_old:
                self.force_rename(self.filepath, self.filepath + ".bak")

            self.force_rename(self.temppath, self.filepath)
        
        elif not self.preserve_faulty:
            os.remove(self.temppath)
    
    @staticmethod
    def force_rename(old, new):
        if os.path.isfile(new):
            os.remove(new)
        
        os.rename(old, new)


def reload():
    import importlib

    importlib.reload(binary_handler)
    importlib.reload(compression)
    importlib.reload(data_asc)
    importlib.reload(data_p3d)
    importlib.reload(data_rap)
    importlib.reload(data_rtm)
    importlib.reload(data_tbcsv)
    importlib.reload(export_asc)
    importlib.reload(export_mcfg)
    importlib.reload(export_p3d)
    importlib.reload(export_rtm)
    importlib.reload(export_tbcsv)
    importlib.reload(import_armature)
    importlib.reload(import_asc)
    importlib.reload(import_mcfg)
    importlib.reload(import_p3d)
    importlib.reload(import_rtm)
    importlib.reload(import_tbcsv)
