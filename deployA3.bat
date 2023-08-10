xcopy /y /e "Arma3ObjectBuilder" "%appdata%\Blender Foundation\Blender\2.90\scripts\addons\Arma3ObjectBuilder"
xcopy /y /e "Arma3ObjectBuilder" "%appdata%\Blender Foundation\Blender\3.6\scripts\addons\Arma3ObjectBuilder"
del /s/q "%appdata%\Blender Foundation\Blender\2.90\scripts\addons\Arma3ObjectBuilder\__pycache__"
del /s/q "%appdata%\Blender Foundation\Blender\3.6\scripts\addons\Arma3ObjectBuilder\__pycache__"