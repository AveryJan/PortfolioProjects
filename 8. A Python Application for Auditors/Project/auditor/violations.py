"""
Module to check violations for a flight lesson.

This module processes the primary violations, which are violations of weather restrictions. 
Weather restrictions express the minimum conditions that a pilot is allowed to fly in.  
So, if a pilot has a ceiling minimum of 2000 feet and there is cloud cover at 1500 feet, 
the pilot should not fly.To determine weather minimums, it is necessary to integrate three 
different files: daycycle.json (for sunrise and sunset), weather.json (for hourly weather 
observations at the airport), and minimums.csv (for the school's minimums set by agreement 
with the insurance agency). 

The functions in this module only check weather conditions at the time of 
takeoff and not the entire time the flight is in the air.  This is standard procedure 
for the insurance company. The school is only liable if they let a pilot take off in 
the wrong conditions. If the pilot stays up in adverse conditions, responsibility shifts 
to the pilot.

Author: Avery Jan
Date: 6-26-2023
"""

import utils
import pilots
import os.path


# WEATHER FUNCTIONS
def bad_visibility(visibility,minimum):
    """
    Returns True if the visibility measurement violates the minimum, False otherwise.
    
    A valid visibility measurement is EITHER the string 'unavailable', or a dictionary 
    with (up to) four values: 'minimum', 'maximum',  'prevailing', and 'units'. Only 
    'prevailing' and 'units' are required; the other two are optional. The units may be 
    'FT' (feet) or 'SM' for (statute) miles and the other three fields are all floats.
    
    If the visibility measurement is a dictionary, this function compares ths visibility
    'minimum' (if it exists) against the parameter minimum. Otherwise, it compares the 
    'prevailing' visibility against the parameter minimum. This function returns True 
    if parameter minimum is more than the measurement. If the visibility measurement is 
    'unavailable', then this function returns True (indicating bad record keeping).
    
    Example: Suppose this is a visibility measurement.
        
        {
            "prevailing": 21120.0,
            "minimum": 1400.0,
            "maximum": 21120.0,
            "units": "FT"
        }
    
    Given the above measurement ('minimum' in the measurement is 1400.0 FT, or 0.26 SM), 
    this function returns True if the parameter minimum is 1 SM and False if it is 0.25 SM.
    
    Parameter visibility: The visibility information
    Precondition: visibility is a valid visibility measurement, as described above.
    (e.g. either a dictionary or the string 'unavailable')
    
    Parameter minimum: The minimum allowed visibility (in statute miles)
    Precondition: minimum is a float or int
    """
                       
    if visibility=='unavailable':
        return True
    elif 'minimum' in visibility.keys():
        measurement = visibility['minimum']
    elif 'minimum' not in visibility.keys(): 
        measurement = visibility['prevailing'] 
    if visibility['units']=='FT':
        measurement = measurement/5280      

    return minimum > measurement
             

def bad_winds(winds,maxwind,maxcross):
    """
    Returns True if the wind measurement violates the maximums, False otherwise.
    
    A valid wind measurement is EITHER the string 'calm', the string 'unavailable', OR 
    a dictionary with (up to) four values: 'speed', 'crosswind', 'gusts', and 'units'. 
    Only 'speed' and 'units' are required if it is a dictionary; the other two values 
    are optional. The units are either 'KT' (knots) or 'MPS' (meters per second) and 
    the other three fields are all floats.
    
    This function compares 'speed' or 'gusts' against the parameter maxwind 
    (whichever is worse) and 'crosswind' against the parameter maxcross. If either 
    measurement is greater than the allowed maximum, this function returns True.
    
    If the winds are 'calm', then this function always returns False. If the winds are
    'unavailable', then this function returns True (indicating bad record keeping).
    
    For conversion information, 1 MPS (meter per second) is about 1.94384 'KT' (knots).
    
    Example: Suppose this is a wind measurement.
        
        {
            "speed": 12.0,
            "crosswind": 10.0,
            "gusts": 18.0,
            "units": "KT"
        }
    
    Given the above measurement, this function returns True if maxwind is 15 or maxcross is 5.
    If both maxwind is 20 and maxcross is 10, it returns False. 
    
    Parameter winds: The wind speed information
    Precondition: winds is a valid wind measurement, as described above.
    (e.g. either a dictionary, the string 'calm', or the string 'unavailable')
    
    Parameter maxwind: The maximum allowable wind speed (in knots)
    Precondition: maxwind is a float or int
    
    Parameter maxcross: The maximum allowable crosswind speed (in knots)
    Precondition: maxcross is a float or int
    """
                       
    if winds == 'calm':
        return False
    elif winds == 'unavailable':
        return True
    elif 'gusts' in winds.keys():
        if winds['gusts'] > winds['speed']:
            w_measurement = winds['gusts']
        elif winds['gusts'] <= winds['speed']:
            w_measurement = winds['speed']
    elif 'gusts' not in winds.keys():
        w_measurement = winds['speed']

    cw_measurement = winds['crosswind']

    if winds['units'] == 'MPS':
        w_measurement = w_measurement * 1.94384
        cw_measurement = cw_measurement * 1.94384

    return (w_measurement > maxwind) or (cw_measurement > maxcross)


def bad_ceiling(ceiling,minimum):
    """
    Returns True if the ceiling measurement violates the minimum, False otherwise.
    
    A valid ceiling measurement is EITHER the string 'clear', the string 'unavailable', 
    OR a list of cloud layer measurements. A cloud layer measurement is a dictionary 
    with three required keys: 'type', 'height', and 'units'. Type is one of 'a few', 
    'scattered', 'broken', 'overcast', or 'indefinite ceiling'. The value of 'units' 
    must be 'FT' and the 'units' is for the float associated with 'height'.
    
    If the ceiling is 'clear', then this function always returns False. If the ceiling 
    is 'unavailable', then this function returns True (indicating bad record keeping).
    Otherwise, it compares the minimum allowed ceiling against the lowest cloud layer 
    that is either 'broken', 'overcast', or 'indefinite ceiling'.
    
    Example: Suppose this is a ceiling measurement.
        
        [
            {
                "cover": "clouds",
                "type": "scattered",
                "height": 700.0,
                "units": "FT"
            },
            {
                "type": "overcast",
                "height": 1200.0,
                "units": "FT"
            }
        ]
    
    Given the above measurement, this function returns True if minimum is 2000,
    but False if it is 1000.
    
    Parameter ceiling: The ceiling information
    Precondition: ceiling is a valid ceiling measurement, as described above.
    (e.g. either a dictionary, the string 'clear', or the string 'unavailable')
        
    Parameter minimum: The minimum allowed ceiling (in feet)
    Precondition: minimum is a float or int
    """

    if ceiling == 'clear':
        return False
    elif ceiling == 'unavailable':
        return True
    
    measurement = []   # accumulator
    
    for x in range(len(ceiling)):
        if ceiling[x]['type']=='broken' or ceiling[x]['type']=='overcast' or ceiling[x]['type']=='indefinite ceiling'
            measurement.append(ceiling[x]['height'])
    
    if len(measurement) > 0:
        return min(measurement) < minimum    
    elif len(measurement) == 0:
        return False


def get_weather_report(takeoff,weather):
    """
    Returns the most recent weather report at or before take-off.
    
    The weather is a dictionary whose keys are ISO formatted timestamps and whose values 
    are weather reports.  For example, here is an example of a (small portion of) a
    weather dictionary:
        
        {
            "2017-04-21T08:00:00-04:00": {
                "visibility": {
                "prevailing": 10.0,
                "units": "SM"
            },
            "wind": {
                "speed": 13.0,
                "crosswind": 2.0,
                "units": "KT"
            },
            "temperature": {
                "value": 13.9,
                "units": "C"
            },
            "sky": [
                {
                    "cover": "clouds",
                    "type": "broken",
                    "height": 700.0,
                    "units": "FT"
                }
            ],
            "code": "201704211056Z"
        },
        "2017-04-21T07:00:00-04:00": {
            "visibility": {
                "prevailing": 10.0,
                "units": "SM"
            },
            "wind": {
                "speed": 13.0,
                "crosswind": 2.0,
                "units": "KT"
            },
            "temperature": {
                "value": 13.9,
                "units": "C"
            },
            "sky": [
                {
                    "type": "overcast",
                    "height": 700.0,
                    "units": "FT"
                }
            ],
            "code": "201704210956Z"
        }
        ...
    },
    
    If there is a report whose timestamp matches the ISO representation of takeoff, 
    this function uses that report.  Otherwise it searches the dictionary for the most
    recent report before (but not equal to) takeoff.  If there is no such report, it
    returns None.
    
    Example: If takeoff was as 8 am on April 21, 2017 (Eastern), this function returns 
    the value for key '2017-04-21T08:00:00-04:00'.  If there is no additional report at
    9 am, a 9 am takeoff would use this value as well.
    
    Parameter takeoff: The takeoff time
    Precondition: takeoff is a datetime object
    
    Paramater weather: The weather report dictionary 
    Precondition: weather is a dictionary formatted as described above
    """
    # Note: Looping through the dictionary is VERY slow because it is so large
    # Should convert the takeoff time to an ISO string and search for that first.
    # Only loop through the dictionary as a back-up if that fails.
    
    # Search for time in dictionary
    # As fall back, find the closest time before takeoff
    
    import datetime

    isostring = takeoff.isoformat()
    
    # Find exact match
    if isostring in weather:
        return weather[isostring]
       
    # Did not find exact match => Apply Seth approach
    w_list = list(weather)
    last_key = w_list[len(w_list)-1]
    result = utils.str_to_time(last_key, tzsource=None)
 
    for k in weather.keys():  
        key = utils.str_to_time(k,tzsource=None)    #create a datetime object of k
        if key < takeoff: 
            if key > result:
                result = utils.str_to_time(k,tzsource=None)

    timestamp = result.isoformat()     # get the key from result datetime objet in isoformat
    return weather[timestamp]   


def get_weather_violation(weather,minimums):
    """
    Returns a string representing the type of weather violation (empty string if flight is ok)
    
    The weather reading is a dictionary with the keys: 'visibility', 'wind', and 'sky'.
    These correspond to a visibility, wind, and ceiling measurement, respectively. It
    may have other keys as well, but these can be ignored. For example, this is a possible 
    weather value:
        
        {
            "visibility": {
                "prevailing": 21120.0,
                "minimum": 1400.0,
                "maximum": 21120.0,
                "units": "FT"
            },
            "wind": {
                "speed": 12.0,
                "crosswind": 3.0,
                "gusts": 18.0,
                "units": "KT"
            },
            "temperature": {
                "value": -15.6,
                "units": "C"
            },
            "sky": [
                {
                    "cover": "clouds",
                    "type": "broken",
                    "height": 2100.0,
                    "units": "FT"
                }
            ],
            "weather": [
                "light snow"
            ]
        }
    
    The minimums is a list of the four minimums ceiling, visibility, and max windspeed,
    and max crosswind speed in that order.  Ceiling is in feet, visibility is in statute
    miles, max wind and cross wind speed are both in knots. For example, 
    [3000.0,10.0,20.0,8.0] is a potential minimums list.
    
    This function uses bad_visibility, bad_winds, and bad_ceiling as helpers. It returns
    'Visibility' if the only problem is bad visibility, 'Winds' if the only problem is 
    wind, and 'Ceiling' if the only problem is the ceiling.  If there are multiple
    problems, it returns 'Weather', It returns 'Unknown' if no weather reading is 
    available (e.g. weather is None).  Finally, it returns '' (the empty string) if 
    the weather is fine and there are no violations.
    
    Parameter weather: The weather measure
    Precondition: weather is dictionary containing a visibility, wind, and ceiling measurement,
    or None if no weather reading is available.
    
    Parameter minimums: The safety minimums for ceiling, visibility, wind, and crosswind
    Precondition: minimums is a list of four floats
    """
                        
    
    if weather == None:
        result = 'Unknown'
        return result

    c = bad_ceiling(weather['sky'],minimums[0])
    v = bad_visibility(weather['visibility'], minimums[1])
    w = bad_winds(weather['wind'], minimums[2], minimums[3])

    if c == False and v == False and w == False:
        result = ''
    elif c == True and v == False and w == False:
        result = 'Ceiling'
    elif c == False and v == True and w == False:
        result = 'Visibility'
    elif c == False and v == False and w == True:
        result = 'Winds'
    elif c == False and v == True and w == True:
        result = 'Weather'       
    elif c == True and v == True and w == False:
        result = 'Weather' 
    elif c == True and v == False and w == True:
        result = 'Weather' 
    elif c == True and v == True and w == True:
        result = 'Weather' 
    
    return result


# FILES TO AUDIT
# Sunrise and sunset
DAYCYCLE = 'daycycle.json'
# Hourly weather observations
WEATHER  = 'weather.json'
# The list of insurance-mandated minimums
MINIMUMS = 'minimums.csv'
# The list of all registered students in the flight school
STUDENTS = 'students.csv'
# The list of all take-offs (and landings)
LESSONS  = 'lessons.csv'


def list_weather_violations(directory):
    """
    Returns the (annotated) list of flight reservations that violate weather minimums.
    
    This function reads the data files in the given directory (the data files are all
    identified by the constants defined above in this module).  It loops through the
    list of flight lessons (in lessons.csv), identifying those takeoffs for which
    get_weather_violation() is not the empty string.
    
    This function returns a list that contains a copy of each violating lesson, together 
    with the violation appended to the lesson.
    
    Example: Suppose that the lessons
        
        S00687  548QR  I061  2017-01-08T14:00:00-05:00  2017-01-08T16:00:00-05:00  VFR  Pattern
        S00758  548QR  I072  2017-01-08T09:00:00-05:00  2017-01-08T11:00:00-05:00  VFR  Pattern
        S00971  426JQ  I072  2017-01-12T13:00:00-05:00  2017-01-12T15:00:00-05:00  VFR  Pattern
    
    violate for reasons of 'Winds', 'Visibility', and 'Ceiling', respectively (and are the
    only violations).  Then this function will return the 2d list
        
        [[S00687, 548QR, I061, 2017-01-08T14:00:00-05:00, 2017-01-08T16:00:00-05:00, VFR, Pattern, Winds],
         [S00758, 548QR, I072, 2017-01-08T09:00:00-05:00, 2017-01-08T11:00:00-05:00, VFR, Pattern, Visibility],
         [S00971, 426JQ, I072, 2017-01-12T13:00:00-05:00, 2017-01-12T15:00:00-05:00, VFR, Pattern, Ceiling]]
    
    REMEMBER: VFR flights are subject to minimums with VMC in the row while IFR flights 
    are subject to minimums with IMC in the row.  The examples above are all VFR flights.
    If we changed the second lesson to
    
        S00758, 548QR, I072, 2017-01-08T09:00:00-05:00, 2017-01-08T11:00:00-05:00, IFR, Pattern
    
    then it is possible it is no longer a visibility violation because it is subject to
    a different set of minimums.
    
    Parameter directory: The directory of files to audit
    Precondition: directory is the name of a directory containing the files 'daycycle.json',
    'weather.json', 'minimums.csv', 'students.csv', and 'lessons.csv'
    """
    # Load in all of the files
    
    # For each of the lessons
        # Get the takeoff time
        # Get the pilot credentials
        # Get the pilot minimums
        # Get the weather conditions
        # Check for a violation and add to result if so
    
    # Load in all of the files    
    daycycle = utils.read_json(os.path.join(directory,DAYCYCLE))  # A dictionary
    weather = utils.read_json(os.path.join(directory, WEATHER))  # A dictionary
    minimums = utils.read_csv(os.path.join(directory, MINIMUMS))  # A 2-D list with header
    students = utils.read_csv(os.path.join(directory, STUDENTS))  # A 2-D list with header
    lessons = utils.read_csv(os.path.join(directory, LESSONS))   # A 2-D list with header

    result = []                # will be a 2-D list if theres is any weather violation

    # For each of the lessons
    for row in range(1, len(lessons)):
        # Get the takeoff time
        timezone = daycycle['timezone']
        takeoff = utils.str_to_time(lessons[row][3], tzsource = timezone )    # takeoff as a datetime object
        # Get the pilot credentials
        id = lessons[row][0]                            # get pilot id from lessons table
        student = utils.get_for_id(id,students)         # get pilot credentials from students table         
        # Get the pilot minimum
        cert = pilots.get_certification(takeoff, student)
        area = lessons[row][6]
        if len(lessons[row][2]) == 0:
            instructed = False
        elif len(lessons[row][2])>0:
            instructed = True
        if lessons[row][5] == 'VFR':
            vfr = True
        elif lessons[row][5] == 'IFR':
            vfr = False       
        daytime = utils.daytime(takeoff, daycycle)
        p_minimums = pilots.get_minimums(cert, area, instructed, vfr, daytime, minimums)
        # Get the weather conditions
        report = get_weather_report(takeoff, weather)
        if report!=None and len(p_minimums)>0: 
            violation = get_weather_violation(report,p_minimums)
        # Check for a violation and add to result if so
            if len(violation) > 0:
                lessons[row].append(violation)
                result.append(lessons[row])
        
    return result
    

