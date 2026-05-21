import csv
from datetime import datetime
import requests
import io
from io import StringIO
import json
import os

URL="http://localhost:8080/api/v2/get/232817/"


from icalendar import Calendar

def parse_calendar_file(file_content: bytes):
    """
    Parse vCalendar file content and return parsed data.
    """
    try:
        response = Calendar.from_ical(file_content)

        professeurs = set()
        matieres = set()
        cours = list()

        for event in response.walk('VEVENT'):
            summary = event.get('SUMMARY')
            
            # Get start and end times
            dtstart = event.get('DTSTART')
            dtend = event.get('DTEND')
            
            startDate = dtstart.dt
            endDate = dtend.dt
            last = int((endDate - startDate).total_seconds())/3600
            
            text = str(summary)
            parts = text.split(' - ') 
            if parts[1] != 'Autonomie':
                professeurs.add(parts[3])
                cours.append((parts[0], parts[1], parts[3], last))
            else:
                professeurs.add('Autonomie')
                cours.append((parts[0], parts[1], 'Autonomie', last))
            matieres.add(parts[0])

        professeur = list(professeurs)
        profDup = list()
        teamsDisplay = list()
        for professeur in professeurs:
            profDup.append(professeur)
            profDup.append(professeur)
            profDup.append(professeur)

            teamsDisplay.append('AMPHI')
            teamsDisplay.append('TD')
            teamsDisplay.append('TP')
            
        teams = list(set(teamsDisplay))
        if 'AMPHI' in teams:
            teams.remove('AMPHI')
        teams.append('COURS')
        teams.sort()
        
        csv_content = str()

        csv_content += ','.join([''] + profDup) + '\n'
        csv_content += ','.join([''] + teamsDisplay) + '\n'
        for row in matieres:
            cur_matiere = row
            line = []
            for professeur in professeurs:
                for team in teams:
                    last= 0
                    is_inserted = False 
                    for cour in cours: 
                        if cour[0] == cur_matiere and cour[1] == team and cour[2] == professeur:
                            is_inserted = True
                            last += cour[3]
                    if is_inserted:
                        line.append(str(last))
                    else:
                        line.append('')
            csv_content += ','.join([row] + line) + '\n'
        
        # Parse CSV string into list of dictionaries
        parsed_data = parse_csv_string(csv_content)
        return parsed_data
    except Exception as e:
        print(f"Error parsing calendar file: {e}")
        import traceback
        traceback.print_exc()
        return -1

def extract_calendar_data():
    response = requests.get(URL)
    if response.status_code != 200:
        print("Error fetching calendar data")
        return -1

    response = Calendar.from_ical(response.content)

    professeurs = set()
    matieres = set()
    cours = list()

    for event in response.walk('VEVENT'):
        summary = event.get('SUMMARY')
            
        # Get start and end times
        dtstart = event.get('DTSTART')
        dtend = event.get('DTEND')

        startDate = dtstart.dt
        endDate = dtend.dt
        last = int((endDate - startDate).total_seconds())/3600
            
        text = str(summary)
        parts = text.split(' - ') 
        if parts[1] != 'Autonomie':
            professeurs.add(parts[3])
            cours.append((parts[0], parts[1], parts[3], last))
        else:
            professeurs.add('Autonomie')
            cours.append((parts[0], parts[1], 'Autonomie', last))
        matieres.add(parts[0])

    professeur = list(professeurs)
    profDup= list()
    teamsDisplay=  list()
    for professeur in professeurs:
        profDup.append(professeur)
        profDup.append(professeur)
        profDup.append(professeur)

        teamsDisplay.append('AMPHI')
        teamsDisplay.append('TD')
        teamsDisplay.append('TP')
        
    teams= list(set(teamsDisplay))
    teams.remove('AMPHI')
    teams.append('COURS')
    teams.sort()
    
    csv_content = str()

    csv_content += ','.join([''] + profDup) + '\n'
    csv_content += ','.join([''] + teamsDisplay) + '\n'
    for row in matieres:
        cur_matiere = row
        line = []
        for professeur in professeurs:
            for team in teams:
                for cour in cours: 
                    is_inserted = False
                    if cour[0] == cur_matiere and cour[1] == team and cour[2] == professeur:
                        is_inserted = True
                        break
                if is_inserted:
                    line.append('X')
                else:
                    line.append('')
        csv_content += ','.join([row] + line) + '\n'
    
    # Parse CSV string into list of dictionaries
    parsed_data = parse_csv_string(csv_content)
    
    # Write parsed data to CSV file
    write_parsed_data_to_csv(parsed_data)
    
    return parsed_data


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

