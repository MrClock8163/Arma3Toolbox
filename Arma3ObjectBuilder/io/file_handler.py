import os
from datetime import datetime


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
