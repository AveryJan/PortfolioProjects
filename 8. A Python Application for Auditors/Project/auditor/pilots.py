"""
Module determining pilot certifications, ratings, endorsements, and restrictions.

The restrictions placed on a pilot depend on their qualifications.  There are three
ways to think about a pilot.  

(1) Certifications.  These are what licenses a pilot has.  These are also used to classify
where the student is in the licensing process.  Is the student post solo (can fly without
instructor), but before license?  Is the student 50 hours past their license (a threshold 
that helps with insurance)?

(2) Ratings.  These are extra add-ons that a pilot can add to a license. For this project,
the only rating is Instrument Rating, which allows a pilot to fly through adverse weather
using only instruments.

(3) Endorsements. These are permission to fly certain types of planes solo.  Advanced 
allows a pilot to fly a plane with retractable landing gear. Multiengine allows a pilot
to fly a plane with more than one engine.

The file pilots.csv is a list of all pilots in the school, together with the dates that
they earned these certifications, ratings, and endorsements.  Specifically, this CSV file
has the following header:
    
    ID  LASTNAME  FIRSTNAME  JOINED  SOLO  LICENSE  50 HOURS  INSTRUMENT  ADVANCED  MULTIENGINE

The first three columns are strings, while all other columns are dates.

The functions in this class take a row from the pilot table and determine if a pilot has
a certain qualification at the time of takeoff. As this program is auditing the school 
over a course of a year, a student may not be instrument rated for one flight but might
be for another.

Author: Avery Jan
Date: 6-21-2023
"""
import utils

# CERTIFICATION CLASSIFICATIONS
# The certification of this pilot is unknown
PILOT_INVALID = -1
# A pilot that has joined the school, but has not soloed
PILOT_NOVICE  = 0
# A pilot that has soloed but does not have a license
PILOT_STUDENT = 1
# A pilot that has a license, but has under 50 hours post license
PILOT_CERTIFIED = 2
# A pilot that 50 hours post license
PILOT_50_HOURS  = 3


def get_certification(takeoff,student):
    """
    Returns the certification classification for this student at the time of takeoff.
    
    The certification is represented by an int, and must be the value PILOT_NOVICE, 
    PILOT_STUDENT, PILOT_CERTIFIED, PILOT_50_HOURS, or PILOT_INVALID. It is PILOT_50_HOURS 
    if the student has certified '50 Hours' before this flight takeoff.  It is 
    PILOT_CERTIFIED if the student has a private license before this takeoff and 
    PILOT_STUDENT if the student has soloed before this takeoff.  A pilot that has only
    just joined the school is PILOT_NOVICE.  If the flight takes place before the student
    has even joined the school, the certification is PILOT_INVALID.
    
    Recall that a student is a 10-element list of strings.  The first three elements are
    the student's identifier, last name, and first name.  The remaining elements are all
    timestamps indicating the following in order: time joining the school, time of first 
    solo, time of private license, time of 50 hours certification, time of instrument 
    rating, time of advanced endorsement, and time of multiengine endorsement.
    
    Parameter takeoff: The takeoff time of this flight
    Precondition: takeoff is a datetime object with a time zone.
    
    Parameter student: The student pilot
    Precondition: student is 10-element list of strings representing a pilot.
    """
                      
    result = ''
    timestamp = ''

    timestamp3 = student[3]
    d3 = utils.str_to_time(timestamp3, tzsource=takeoff)
    if takeoff < d3:
        return PILOT_INVALID

    for x in range(3, len(student)):
        timestamp = student[x]
        d = utils.str_to_time(timestamp, tzsource=takeoff)
        if d != None:               
            if takeoff >= d:
                result = student[x]

    if result == student[3]:
        return PILOT_NOVICE
    
    elif result == student[4]:
        return PILOT_STUDENT
    
    elif result == student[5]:
        return PILOT_CERTIFIED
       
    elif result in student[6:]:
        return PILOT_50_HOURS


def get_best_value(data, index, maximum=True):
    """
    Returns the 'best' value from a given column in a 2-dimensional nested list.
    
    This function is a helper function for get_minimums. 
    
    The data parameter is a 2-dimensional nested list of data. The index parameter
    indicates which "colummn" of data should be evaluated. Each item in that column
    is expected to be a number in string format.  Each item should be evaluated as a 
    float and the best value is selected as the return value for the function. The
    best value is determined by the maximum parameter and is either the highest or
    lowest float value of the column. The 2D list does not include a header row. 
    
    Parameter data: a 2-dimensional nested list of data
    Precondition: the column referenced by index should be numbers in string format
    
    Parameter index: position to examine in each row of data
    Precondition: index is a an integer
    
    Parameter maximum: indicates whether to return the highest value (True) or
    lowest value (False)
    Precondition: maximum is a boolean and defaults to True
    
    """
    # Find the best values for each column of the row
    if maximum == True:
        max = float(data[0][index])
        for row in range(len(data)):
            item = float(data[row][index]) 
            if item > max:
                max = item    
        return max
 
    elif maximum == False:
        min = float(data[0][index])
        for row in range(len(data)):
            item = float(data[row][index]) 
            if item < min:
                min = item        
        return min   
 

def get_minimums(cert, area, instructed, vfr, daytime, minimums):
    """
    Returns the most advantageous minimums for the given flight category.
    
    The minimums is the 2-dimensional list (table) of minimums, including the header.
    The header for this table is as follows:
        
        CATEGORY  CONDITIONS  AREA  TIME  CEILING  VISIBILITY  WIND  CROSSWIND
    
    The values in the first four columns are strings, while the values in the last
    four columns are numbers.  CEILING is a measurement in ft, while VISIBILITY is in
    miles.  Both WIND and CROSSWIND are speeds in knots.
    
    This function first searches the table for rows that match the function parameters. 
    It is possible for more than one row to be a match.  A row is a match if ALL four 
    of the first four columns match.
    
    The first column (CATEGORY) has values 'Student', 'Certified', '50 Hours', or 'Dual'.
    If the value is 'Student', it is a match if cert is PILOT_STUDENT or higher.  If the
    value is 'Certified', it is a match if cert is PILOT_CERTIFIED or higher. If it is 
    '50 Hours', it is only a match if cert is PILOT_50_HOURS. The value 'Dual' only
    matches if instructed is True and even if cert is PILOT_INVALID or PILOT_NOVICE.
    
    The second column (CONDITIONS) has values 'VMC' and 'IMC'. A flight filed as VFR 
    (visual flight rules) is subject to VMC (visual meteorological conditions) minimums.  
    Similarly, a fight filed as IFR is subject to IMC minimums.
    
    The third column (AREA) has values 'Pattern', 'Practice Area', 'Local', 
    'Cross Country', or 'Any'. Flights that are in the pattern or practice area match
    'Local' as well.  All flights match 'Any'.
    
    The fourth column (TIME) has values 'Day' or 'Night'. The value 'Day' is only 
    a match if daytime is True. If it is False, 'Night' is the only match.
    
    Once the function finds the all matching rows, it searches for the most advantageous
    values for CEILING, VISIBILITY, WIND, and CROSSWIND. Lower values of CEILING and
    VISIBILITY are better.  Higher values for WIND and CROSSWIND are better.  It then
    returns these four values as a list of four floats in the same order they appear
    in the table.
    
    Example: Suppose minimums is the table
        
        CATEGORY   CONDITIONS  AREA           TIME  CEILING  VISIBILITY  WIND  CROSSWIND
        Student    VMC         Pattern        Day   2000     5           20    8
        Student    VMC         Practice Area  Day   3000     10          20    8
        Certified  VMC         Local          Day   3000     5           20    20
        Certified  VMC         Practice Area  Night 3000     10          20    10
        50 Hours   VMC         Local          Day   3000     10          20    10
        Dual       VMC         Any            Day   2000     10          30    10
        Dual       IMC         Any            Day   500      0.75        30    20
    
    The call get_minimums(PILOT_CERTIFIED,'Practice Area',True,True,True,minimums) matches
    all of the following rows:
        
        Student    VMC         Practice Area  Day   3000     10          20    8
        Certified  VMC         Local          Day   3000     5           20    20
        Dual       VMC         Any            Day   2000     10          30    10
    
    The answer in this case is [2000,5,30,20]. 2000 and 5 are the least CEILING and 
    VISIBILITY values while 30 and 20 are the largest wind values.
    
    If there are no rows that match the parameters (e.g. a novice pilot with no 
    instructor), this function returns None.
    
    Parameter cert: The pilot certification
    Precondition: cert is an int and one of PILOT_NOVICE, PILOT_STUDENT, PILOT_CERTIFIED, 
    PILOT_50_HOURS, or PILOT_INVALID.
    
    Parameter area: The flight area for this flight plan
    Precondition: area is a string and one of 'Pattern', 'Practice Area' or 'Cross Country'
    
    Parameter instructed: Whether an instructor is present
    Precondition: instructed is a boolean
    
    Parameter vfr: Whether the pilot has filed this flight plan as an VFR flight
    Precondition: vfr is a boolean
    
    Parameter daytime: Whether this flight is during the day
    Precondition: daytime is boolean
    
    Parameter minimums: The table of allowed minimums
    Precondition: minimums is a 2d-list (table) as described above, including header.
    """
    # Find all rows that apply to this student.
    # Find the best values for each column of the row.
    # Use get_best_value to find best value in the list of matches.

    # Section I: Build the Matching Table with Each Row Being a Match for This Stucent.
    
    data = []

    for row in range(1, len(minimums)):
        # instructor == True, begins here
        #i,v,d = T,T,T 
        if instructed==True and vfr==True and daytime==True:    
            if minimums[row][1]=='VMC' and minimums[row][3]=='Day':
                if cert == -1 or cert == 0:
                    if minimums[row][0]=='Dual':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 1:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 2:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student' \
                    or minimums[row][0]=='Certified':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 3:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student' \
                    or minimums[row][0]=='Certified' or minimums[row][0]=='50 Hours':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
        #i,v,d = T,T,F 
        elif instructed==True and vfr==True and daytime==False:    
            if minimums[row][1]=='VMC' and minimums[row][3]=='Night':
                if cert == -1 or cert == 0:
                    if minimums[row][0]=='Dual':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 1:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 2:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student' \
                    or minimums[row][0]=='Certified':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 3:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student' \
                    or minimums[row][0]=='Certified' or minimums[row][0]=='50 Hours':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
        #i,v,d = T,F,T 
        elif instructed==True and vfr==False and daytime==True:    
            if minimums[row][1]=='IMC' and minimums[row][3]=='Day':
                if cert == -1 or cert == 0:
                    if minimums[row][0]=='Dual':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 1:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 2:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student' \
                    or minimums[row][0]=='Certified':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 3:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student' \
                    or minimums[row][0]=='Certified' or minimums[row][0]=='50 Hours':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row])
        #i,v,d = T,F,F 
        elif instructed==True and vfr==False and daytime==False:    
            if minimums[row][1]=='IMC' and minimums[row][3]=='Night':
                if cert == -1 or cert == 0:
                    if minimums[row][0]=='Dual':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 1:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 2:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student' \
                    or minimums[row][0]=='Certified':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 3:
                    if minimums[row][0]=='Dual' or minimums[row][0]=='Student' \
                    or minimums[row][0]=='Certified' or minimums[row][0]=='50 Hours':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                       
        # instructed == False, begins here 
        #i,v,d = F,F,F
        elif instructed==False and vfr==False and daytime==False:       
            if minimums[row][1]=='IMC' and minimums[row][3]=='Night':
                if cert == 1:
                    if minimums[row][0]=='Student':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 2:
                    if minimums[row][0]=='Student' or minimums[row][0]=='Certified':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 3:
                    if minimums[row][0]=='Student' or minimums[row][0]=='Certified' \
                    or minimums[row][0]=='50 Hours':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
        #i,v,d = F,F,T
        elif instructed==False and vfr==False and daytime==True:       
            if minimums[row][1]=='IMC' and minimums[row][3]=='Day':
                if cert == 1:
                    if minimums[row][0]=='Student':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 2:
                    if minimums[row][0]=='Student' or minimums[row][0]=='Certified':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 3:
                    if minimums[row][0]=='Student' or minimums[row][0]=='Certified' \
                    or minimums[row][0]=='50 Hours':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
        #i,v,d = F,T,T
        elif instructed==False and vfr==True and daytime==True:       
            if minimums[row][1]=='VMC' and minimums[row][3]=='Day':
                if cert == 1:
                    if minimums[row][0]=='Student':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 2:
                    if minimums[row][0]=='Student' or minimums[row][0]=='Certified':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 3:
                    if minimums[row][0]=='Student' or minimums[row][0]=='Certified' \
                    or minimums[row][0]=='50 Hours':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row])       
        #i,v,d = F,T,F
        elif instructed==False and vfr==True and daytime==False:       
            if minimums[row][1]=='VMC' and minimums[row][3]=='Night':
                if cert == 1:
                    if minimums[row][0]=='Student':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row])
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 2:
                    if minimums[row][0]=='Student' or minimums[row][0]=='Certified':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row]) 
                elif cert == 3:
                    if minimums[row][0]=='Student' or minimums[row][0]=='Certified' \
                    or minimums[row][0]=='50 Hours':
                        if area=='Pattern':
                            if minimums[row][2]=='Pattern' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':                           
                               data.append(minimums[row]) 
                        elif area=='Practice Area':
                            if minimums[row][2]=='Practice Area' or minimums[row][2]=='Local' \
                            or minimums[row][2]=='Any':
                                data.append(minimums[row])                
                        elif area=='Cross Country':
                            if minimums[row][2]=='Cross Country' or minimums[row][2]=='Any':                    
                                data.append(minimums[row])       
                                 

    # Section II: Build a 1-D list (best values for each of the last 4 columns in minimums)   
    
    bvlist = []

    if len(data)>0:
        ceiling = get_best_value(data, 4, maximum=False)
        bvlist.append(ceiling)
        visibility = get_best_value(data, 5, maximum=False)
        bvlist.append(visibility)
        wind = get_best_value(data, 6, maximum=True)
        bvlist.append(wind)
        crosswind = get_best_value(data, 7, maximum=True)
        bvlist.append(crosswind)

        return bvlist
