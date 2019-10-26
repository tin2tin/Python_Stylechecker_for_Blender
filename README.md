# Python Stylechecker(pep8) for Blender
[Pycodestyle](https://github.com/PyCQA/pycodestyle) integrated into Blender Text Editor

### pycodestyle must be installed first:

Locate your Blender's Python binary path.
Let's call it <BPYTHON> (in my case 2.80/python/bin/python.exe at the Blender installation).

Run the following to enable pip operations in bpython:
```
<BPYTHON> -m pip install --upgrade pip
```
  
Now install the pycodestyle package by simply call pip from bpython:
```
<BPYTHON> -m pip install pycodestyle
```
  
You just have to install a package once and uninstalling works the same way:
```
<BPYTHON> -m pip uninstall pycodestyle
```
  
### Then download and install codestyle.py in Blender: 
https://raw.githubusercontent.com/tin2tin/Python_Stylechecker_for_Blender/master/codestyle.py
