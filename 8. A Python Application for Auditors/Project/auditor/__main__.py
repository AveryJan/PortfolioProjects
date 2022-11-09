"""
The script code for the application.

This file calls the execute() function in module app.py, passing it the contents of sys.argv EXCEPT for the application name
(Note: so only the command line arguments AFTER 'python auditor' when running this application in codio shell).

Author: Avery Jan
Date:   6-27-2022
"""
import sys, app
app.execute(sys.argv[1:])
