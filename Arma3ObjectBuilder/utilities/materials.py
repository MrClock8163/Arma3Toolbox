import os
import re

def process_template(template, root, folder, basename, check_file_exist):
    data = ""

    with open(template) as file:
        data = file.read()

        RE_STAGE = re.compile(r"(?:<)(?P<stage>.*)(?:>)")
        
        replace = []
        for match in RE_STAGE.finditer(data):
            suffix, default = match.group("stage").split('|')

            path = os.path.join(folder, "%s%s.paa" % (basename, ("_" + suffix) if suffix else ""))
            if os.path.isfile(path) or not check_file_exist:
                if path.lower().startswith(root.lower()):
                    path = os.path.relpath(path, root)
            else:
                path = default
            
            replace.append("\"%s\"" % path)
        
        replace = iter(replace)
        def repl(match):
            return next(replace)

        data = RE_STAGE.sub(repl, data)
    
    with open(os.path.join(folder, basename + ".rvmat"), "w") as file:
        file.write(data)
