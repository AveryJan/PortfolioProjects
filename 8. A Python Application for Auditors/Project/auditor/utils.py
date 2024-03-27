"""
Module providing utility functions for this project.

These functions are general purpose utilities used by other modules in this project.

Author: Avery Jan
Date: 6-19-2023
"""
import csv
import json
import datetime
import pytz
from dateutil.parser import parse

def read_csv(filename):
    """
    Returns the contents read from the CSV file filename.
    
    This function reads the contents of the file filename and returns the contents as
    a 2-dimensional list. Each element of the list is a row, with the first row being
    the header. Cells in each row are all interpreted as strings; it is up to the 
    programmer to interpret this data, since CSV files contain no type information.
    
    Parameter filename: The file to read
    Precondition: filename is a string, referring to a file that exists, and that file 
    is a valid CSV file
    """
                      
    file = open(filename)
    wrapper = csv.reader(file)

    result = []  # accumulator

    for row in wrapper:
        result.append(row)
    
    file.close()
    
    return result


def write_csv(data,filename):
    """
    Writes the given data out as a CSV file filename.
    
    To be a proper CSV file, data must be a 2-dimensional list with the first row 
    containing only strings.  All other rows may be any Python value.  Dates are
    converted using ISO formatting. All other objects are converted to their string
    representation.
    
    Parameter data: The Python value to encode as a CSV file
    Precondition: data is a  2-dimensional list of strings
    
    Parameter filename: The file to read
    Precondition: filename is a string representing a path to a file with extension
    .csv or .CSV.  The file may or may not exist.
    """
                        
    file = open(filename, 'w')
    wrapper = csv.writer(file)

    for x in range(len(data)):
        wrapper.writerow(data[x])

    file.close()


def read_json(filename):
    """
    Returns the contents read from the JSON file filename.
    
    This function reads the contents of the file filename, and will use the json module
    to covert these contents in to a Python data value.  This value will either be a
    a dictionary or a list. 
    
    Parameter filename: The file to read
    Precondition: filename is a string, referring to a file that exists, and that file 
    is a valid JSON file
    """
                       
    file = open(filename)
    text = file.read()
    file.close()

    data = json.loads(text)

    return data


def str_to_time(timestamp,tzsource=None):
    """
    Returns the datetime object for the given timestamp (or None if timestamp is 
    invalid).
    
    This function uses the parse function in dateutil.parser to
    convert the timestamp to a datetime object.  If it is not a valid date (so
    the parser crashes), this function returns None.
    
    If the timestamp has a time zone, then it keeps that time zone even if
    the value for tzsource is not None.  Otherwise, if timestamp has no time zone 
    and tzsource is not None, then this function will use tzsource to assign 
    a time zone to the new datetime object.
    
    The value for tzsource can be None, a string, or a datetime object.  If it 
    is a string, it will be the name of a time zone, and this function localizes the 
    timestamp.  If it is another datetime, then the datetime object created from 
    timestamp should get the same time zone as tzsource.
    
    Parameter timestamp: The time stamp to convert
    Precondition: timestamp is a string
    
    Parameter tzsource: The time zone to use (OPTIONAL)
    Precondition: tzsource is either None, a string naming a valid time zone,
    or a datetime object.
    """
    
    try:
        d = parse(timestamp)
 
    except:
        return None

    if d.tzinfo!=None:
        return d
        
    if d.tzinfo==None:
        if tzsource == None:
            return d
        elif type(tzsource)==str:
            tz = pytz.timezone(tzsource)
            e = tz.localize(d)
            return e
        elif type(tzsource)==datetime.datetime:
            f = d.replace(tzinfo=tzsource.tzinfo)
            return f  


def daytime(time,daycycle):
    """
    Returns true if the time takes place during the day.
    
    A time is during the day if it is after sunrise but before sunset, as
    indicated by the daycycle dicitionary.
    
    A daycycle dictionary has keys for several years (as str).  The value for
    each year is also a dictionary, taking strings of the form 'mm-dd'.  The
    value for that key is a THIRD dictionary, with two keys "sunrise" and
    "sunset".  The value for each of those two keys is a string in 24-hour
    time format.
    
    For example, here is what part of a daycycle dictionary might look like:
    
        "2015": {
            "01-01": {
                "sunrise": "07:35",
                "sunset":  "16:44"
            },
            "01-02": {
                "sunrise": "07:36",
                "sunset":  "16:45"
            },
            ...
        }
    
    In addition, the daycycle dictionary has a key 'timezone' that expresses the
    timezone as a string. This function uses that timezone when constructing
    datetime objects from this set.  If the time parameter does not have a timezone,
    we assume that it is in the same timezone as the daycycle dictionary.
    
    Parameter time: The time to check
    Precondition: time is a datetime object
    
    Parameter daycycle: The daycycle dictionary
    Precondition: daycycle is a valid daycycle dictionary, as described above
    """
    year = time.strftime('%Y')

    if year not in daycycle.keys():
        return None
    
    if year in daycycle.keys():
        #get the timestamps to be used for creating sunrise and sunset datetime objects
        mm_dd = time.strftime('%m-%d')
        sr_time = daycycle[year][mm_dd]['sunrise']
        sr_tstamp = time.strftime('%Y-%m-%d') + 'T' + sr_time
        ss_time = daycycle[year][mm_dd]['sunset']
        ss_tstamp = time.strftime('%Y-%m-%d') + 'T' + ss_time
        tzsource = daycycle['timezone']
        #create sunrise and sunset datetime objects
        sunrise = str_to_time(sr_tstamp, tzsource)
        sunset = str_to_time(ss_tstamp, tzsource)

    # compare time with sunrise and sunset (if time.tzinfo !=None)
    if time.tzinfo != None:
        if time > sunrise and time < sunset:
            return True
        elif time <= sunrise or time >= sunset:
            return False

    # compare time with sunrise and sunset (if time.tzinfo ==None)
    if time.tzinfo == None: 
        new_time = time.replace(tzinfo=sunrise.tzinfo)
        if new_time > sunrise and new_time < sunset:
            return True
        elif new_time <= sunrise or new_time >= sunset:
            return False 



def get_for_id(id,table):
    """
    Returns (a copy of) a row of the table with the given id.
    
    Table is a two-dimensional list where the first element of each row is an identifier
    (string).  This function searches the table for the row with the matching identifier and
    returns a COPY of that row. If there is no match, this function returns None.
    
    Parameter id: The id of the student
    Precondition: id is a string
    
    Parameter table: The 2-dimensional list of data
    Precondition: table is a non-empty 2-dimensional list of strings
    """

    for x in range(1, len(table)):        
        if id == table[x][0]:
            return table[x]

