import csv
from datetime import datetime
import requests
import io
from io import StringIO
import json
import os

from routes.lesson import deleteTrueLesson
    
URL="http://localhost:8080/api/v2/get/232817/"


from icalendar import Calendar

def parseCalendarFile(fileContent: bytes):
    """
    Parse vCalendar file content and return parsed data.
    """
    
    from models import lesson
    from routes.lesson import createLesson, deleteLesson

    try:
        response = Calendar.from_ical(fileContent)

        #Variable for backend comparaison 
        realLessons = list()

        # Variable for the csv
        professeurs = set()
        matieres = set()
        cours = list()
        weeks= set()

        for event in response.walk('VEVENT'):
            summary = event.get('SUMMARY')
            
            # Get start and end times
            dtstart = event.get('DTSTART')
            dtend = event.get('DTEND')
            
            startDate = dtstart.dt
            endDate = dtend.dt
            last = int((endDate - startDate).total_seconds())/3600
            
            text = str(summary)
            desc = event.get('DESCRIPTION')
            prof = fromTextToDict(desc.split(' '))
            parts = text.split(' / ') #(DESCRIPTION.profs, SUMMARY[0], SUMMARY[1], last)
            
            week = startDate.isocalendar().week
            week = str(startDate.year) + '-' + str(week)

            if parts[1] != 'Autonomie':
                if '/' in prof:
                    everyTeacher =prof.split('/')
                    for teacher in everyTeacher:
                        professeurs.add(teacher.strip())
                        cours.append((parts[0], parts[1], week, teacher.strip(), last))
                else:
                    professeurs.add(prof)
                    cours.append((parts[0], parts[1], week, prof, last))
            else:
                professeurs.add('Autonomie')
                cours.append((parts[0], parts[1], week, 'Autonomie', last))
            matieres.add(parts[0])
            weeks.add(week)

            whichGroup= parts[1] if (parts[1][0] == 'C' or parts[1][0] == 'A') else parts[1] + '_'+ parts[2].split('_')[1]         
            realLessons.append([prof, week, whichGroup, parts[0], last])

        professeur = list(professeurs)
        profDup = list()
        teamsDisplay = list()

        for professeur in professeurs:
            profDup.append(professeur)
            profDup.append(professeur)
            profDup.append(professeur)
            profDup.append(professeur)
            profDup.append(professeur)

            teamsDisplay.append('AMPHI')
            teamsDisplay.append('TD')
            teamsDisplay.append('TP')
            teamsDisplay.append('DS')
            teamsDisplay.append('Autonomie')

        teams = teamsDisplay[0:5]
        teams.insert(teams.index('AMPHI'), 'COURS')
        teams.remove('AMPHI')
        csvContent = str()

        csvContent += ','.join([''] + profDup) + '\n'
        csvContent += ','.join([''] + teamsDisplay) + '\n'
        for row in matieres:
            curMatiere = row
            line = []
            for week in weeks:
                for professeur in professeurs:
                    for team in teams:
                        last= 0
                        isInserted = False 
                        for cour in cours: 
                            if cour[0] == curMatiere and cour[1] == team and cour[2] == week and cour[3] == professeur:
                                isInserted = True
                                last += cour[4]
                        if isInserted:
                            line.append(str(last))
                        else:
                            line.append('')
                csvContent += ','.join([row + ' ' + week] + line) + '\n'
        
        # Parse CSV string into list of dictionaries
        parsedData = parseCsvString(csvContent)

        deleteTrueLesson()
        for lessons in realLessons:
            newLesson = lesson(
                codeEns=lessons[0],
                week=lessons[1],
                typeEns=lessons[2],
                codeResSae=lessons[3],
                hour=lessons[4],
                isValid=False,
                isLesson=False
            )
            createLesson(newLesson)

        return parsedData
    except Exception as e:
        print(f"Error parsing calendar file: {e}")
        import traceback
        traceback.print_exc()
        return -1


def fromTextToDict(desc: list):
    """
    Extract professor names from event description.
    """
    InterestData=desc[1:3]
    for i in range(len(InterestData)):
        if 'Prof' in InterestData[i]:
            return InterestData[i][5:]


def parseCsvString(csvString: str):
    """
    Parse CSV string and return list of dictionaries.
    """
    lines = csvString.strip().split('\n')
    if len(lines) < 3:
        return []
    
    # First row: professor names
    professors = lines[0].split(',')[1:]  # Skip empty first column
    # Second row: course types (AMPHI, TD, TP, COURS)
    courseTypes = lines[1].split(',')[1:]  # Skip empty first column
    
    # Create column headers by combining professor and course type
    headers = []
    for i, prof in enumerate(professors):
        if i < len(courseTypes):
            headers.append(f"{prof} - {courseTypes[i]}")
    
    # Parse data rows
    data = []
    for line in lines[2:]:
        if not line.strip():
            continue
        
        parts = line.split(',')
        matiere = parts[0]
        values = parts[1:]
        
        rowDict = {"matière": matiere}
        for i, header in enumerate(headers):
            if i < len(values):
                rowDict[header] = values[i] if values[i].strip() else ""
        
        data.append(rowDict)
    
    return data


