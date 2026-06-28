import csv
from datetime import datetime
import requests
import io
from io import StringIO
import json
import os

from Backend.routes.lesson import delete_true_lesson
#from models import lesson

#from Backend.routes import lesson
#from Backend.routes.lesson import create_lesson, delete_lesson

    
URL="http://localhost:8080/api/v2/get/232817/"


from icalendar import Calendar

def parse_calendar_file(file_content: bytes):
    """
    Parse vCalendar file content and return parsed data.
    """
    
    from models import lesson
    from routes.lesson import create_lesson, delete_lesson

    try:
        response = Calendar.from_ical(file_content)

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
            prof = from_text_to_dict(desc.split(' '))
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
        csv_content = str()

        csv_content += ','.join([''] + profDup) + '\n'
        csv_content += ','.join([''] + teamsDisplay) + '\n'
        for row in matieres:
            cur_matiere = row
            line = []
            for week in weeks:
                for professeur in professeurs:
                    for team in teams:
                        last= 0
                        is_inserted = False 
                        for cour in cours: 
                            if cour[0] == cur_matiere and cour[1] == team and cour[2] == week and cour[3] == professeur:
                                is_inserted = True
                                last += cour[4]
                        if is_inserted:
                            line.append(str(last))
                        else:
                            line.append('')
                csv_content += ','.join([row + ' ' + week] + line) + '\n'
        
        # Parse CSV string into list of dictionaries
        parsed_data = parse_csv_string(csv_content)

        delete_lesson()
        for lessons in realLessons:
            new_lesson = lesson(
                code_ens=lessons[0],
                semaine=lessons[1],
                type_ens=lessons[2],
                code_res_sae=lessons[3],
                heures=lessons[4],
                is_valid=False,
                is_lesson=False
            )
            create_lesson(new_lesson)

        return parsed_data
    except Exception as e:
        print(f"Error parsing calendar file: {e}")
        import traceback
        traceback.print_exc()
        return -1


def from_text_to_dict(desc: list):
    """
    Extract professor names from event description.
    """
    Interest_data=desc[1:3]
    for i in range(len(Interest_data)):
        if 'Prof' in Interest_data[i]:
            return Interest_data[i][5:]


def parse_csv_string(csv_string: str):
    """
    Parse CSV string and return list of dictionaries.
    """
    lines = csv_string.strip().split('\n')
    if len(lines) < 3:
        return []
    
    # First row: professor names
    professors = lines[0].split(',')[1:]  # Skip empty first column
    # Second row: course types (AMPHI, TD, TP, COURS)
    course_types = lines[1].split(',')[1:]  # Skip empty first column
    
    # Create column headers by combining professor and course type
    headers = []
    for i, prof in enumerate(professors):
        if i < len(course_types):
            headers.append(f"{prof} - {course_types[i]}")
    
    # Parse data rows
    data = []
    for line in lines[2:]:
        if not line.strip():
            continue
        
        parts = line.split(',')
        matiere = parts[0]
        values = parts[1:]
        
        row_dict = {"matière": matiere}
        for i, header in enumerate(headers):
            if i < len(values):
                row_dict[header] = values[i] if values[i].strip() else ""
        
        data.append(row_dict)
    
    return data


