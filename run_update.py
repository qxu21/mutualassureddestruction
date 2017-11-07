#!flask/bin/python
import sys
from update import minor_update, major_update
if sys.argv[1] == "minor":
    minor_update()
elif sys.argv[1] == "major":
    major_update()
