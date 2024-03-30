"""
Module that validates the flight school's records.

This is the primary module that does all of the work. It loads the files, loops through
the lessons, and searches for any takeoffs that violate insurance requirements. For 
testing purposes all functions are defined in modules and only the script code is 
in the file __main__.py.

Author: Avery Jan
Date: 6-27-2023
"""

import utils
import tests
import os.path
import violations


def discover_violations(directory,output):
    """
    Searches the dataset directory for any flight lessons that violate regulations.
    
    This function will call list_weather_violations() to get the list of weather  
    violations. If the parameter output is not None, it will create the CSV file 
    with name output and write the 2-dimensional list of violations to this file. 
    This CSV file should have the following header:
    
        STUDENT,AIRPLANE,INSTRUCTOR,TAKEOFF,LANDING,FILED,AREA,REASON
    
    Regardless of whether output is None, this function will print out the number 
    of violations, as follows:
    
        '23 violations found.'
    
    If no violations are found, it will say
    
        'No violations found.'
    
    Parameter directory: The directory of files to audit
    Precondition: directory is the name of a directory containing the files 
    'daycycle.json', 'weather.json', 'minimums.csv', 'students.csv', and 
    'lessons.csv'.
    
    Parameter output: The CSV file to store the results
    Precondition: output is None or a string that is a valid file name
    """
                      
    # Get the list of weather violations.    
    data = violations.list_weather_violations(directory)

    # Add a header to the 2-D list.
    header = ['STUDENT','AIRPLANE','INSTRUCTOR','TAKEOFF','LANDING','FILED','AREA','REASON']
    data.insert(0,header)
        
    # If no violations are found, that is, data has the header only. 
    if len(data) == 1:              
        print('No violations found.')

    # If data has the header and one violation, write data into a csv file.
    elif len(data) == 2:
        if output != None:
            utils.write_csv(data,output)
        elif output == None:
            utils.write_csv(data,'output.csv')
        num_violations = len(data)-1
        print(str(num_violations)+' '+'violation found.')
        
    # If data has the header and multiple violations, write data into a csv file.
    elif len(data) > 2:
        if output != None:    
            utils.write_csv(data,output)
        elif output == None:
            utils.write_csv(data,'output.csv')
        num_violations = len(data)-1
        print(str(num_violations)+' '+'violations found.')              

    
def execute(args):
    """
    Executes the application or prints an error message if executed incorrectly.
    
    The arguments to the application (EXCLUDING the application name) are provided to
    the list args. This list should contain either 1 or 2 elements.  If there is one
    element, it should be the name of the data set folder or the value '--test'.  If
    there are two elements, the first should be the data set folder and the second
    should be the name of a CSV file (for output of the results).
    
    If the user calls this script incorrectly (with the wrong number of arguments), this
    function prints:
    
        Usage: python auditor dataset [output.csv]
    
    This function does not do much error checking beyond counting the number of arguments.
    
    Parameter args: The command line arguments for the application (minus the application name)
    Precondition: args is a list of strings.
    """
                       
    
    # Quit if user call the script with wrong number of arguments
    if len(args) > 2 or len(args) < 1:
        print('Usage: python auditor dataset [output.csv]')

    # args has one element
    elif len(args) == 1: 
        if args[0] == '--test':
            tests.test_all()
        else:
            try: 
                discover_violations(args[0], None)
            except:
                print('Usage: python auditor dataset [output.csv]')
                
    # args has two elements   
    elif len(args) == 2:
        if '--test' in args:
            print('Usage: python auditor dataset [output.csv]')
        else: 
            try:
                discover_violations(args[0],args[1])  
            except:
                print('Usage: python auditor dataset [output.csv]')


