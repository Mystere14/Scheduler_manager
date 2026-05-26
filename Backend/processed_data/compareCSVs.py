from icalendar import Calendar
import csv
from io import StringIO
import json
import os

from Backend.processed_data.sessionName import session_name
import pandas as pd



def compare_schedulers_from_spreadsheets(contentSchedulerPlanned: bytes, contentSchedulerPlaced: bytes):
    from Backend.models import compare_scheduler
    from Backend.routes.compare_scheduler import create_compare_scheduler, delete_compare_scheduler
    
    sessionsPlanned =preprocessed_data_to_csv(contentSchedulerPlanned, "scheduler_planned.csv")
    sessionsPlaced =preprocessed_data_to_csv(contentSchedulerPlaced, "scheduler_placed.csv")
    
    print("sessionsPlanned:", sessionsPlanned)
    print("sessionsPlaced:", sessionsPlaced)

    # Single comparison: planned vs placed
    # Positive difference = unplaced (planned but not placed)
    # Negative difference = overplaced (placed but not planned)
    differences = comparaison([list(s) for s in sessionsPlanned], [list(s) for s in sessionsPlaced])

    print("differences:", differences)

    delete_compare_scheduler()
    
    for session in differences:
        new_compare_scheduler = compare_scheduler(
            code_ens=session[0],
            type_ens=session[1],
            code_res_sae=session[2],
            heures=session[3]
        )
        create_compare_scheduler(new_compare_scheduler)


def comparaison(sessionsA, sessionsB):
    """
    Compare two lists of sessions.
    Returns sessions from A with non-zero difference (after subtracting matching B sessions).
    Also includes sessions from B that have no match in A (as negative values).
    """
    # Convert tuples to lists so they can be modified
    sessionsA = [list(session) for session in sessionsA]
    sessionsB = [list(session) for session in sessionsB]
    
    # Track which B sessions have been matched
    matched_indices = set()
    
    for sessionA in sessionsA:
        for i, sessionB in enumerate(sessionsB):
            if(sessionA[0]==sessionB[0] and sessionA[1]==sessionB[1] and sessionA[2]==sessionB[2]):
                # Match found: subtract placed hours from planned hours
                sessionA[3] -= sessionB[3]
                matched_indices.add(i)
                break
    
    # Keep only A sessions with non-zero difference
    result = [session for session in sessionsA if session[3] != 0]
    
    # Add B sessions that have no match in A (as negative values - overplaced)
    for i, sessionB in enumerate(sessionsB):
        if i not in matched_indices:
            # No match found in A - this is overplaced
            result.append([sessionB[0], sessionB[1], sessionB[2], -sessionB[3]])
    
    return result


def preprocessed_data_to_csv(content_file: bytes, file_name: str):
    data = json.loads(content_file.decode('utf-8'))

    processed_data = pd.DataFrame(data['data'])
    
    everySession = pd.DataFrame()

    if file_name == "scheduler_planned.csv":
        everySession = preprocessed_scheduler_planned(processed_data)

    if file_name == "scheduler_placed.csv":
        everySession = preprocessed_scheduler_placed(processed_data)

    # Aggregate sessions with same (code_ens, type_ens, code_res_sae)
    everySession = aggregate_sessions(everySession)

    return everySession

def aggregate_sessions(sessions):
    """
    Combine sessions with same (code_ens, type_ens, code_res_sae) by summing hours.
    """
    aggregated = {}
    for session in sessions:
        key = (session[0], session[1], session[2])
        if key in aggregated:
            aggregated[key] += session[3]
        else:
            aggregated[key] = session[3]
    
    return [(*key, value) for key, value in aggregated.items()]

def preprocessed_scheduler_planned(processed_data: pd.DataFrame):
    sessionPlanned = []

    for _, row in processed_data.iterrows():
        type_ens = row['type_ens'].strip()
        if type_ens == 'C':
            type_ens = 'AMPHI'
        sessionPlanned.append((row['code_ens'].strip(), type_ens.strip(), session_name[row['code_res_sae']], float(row['volume'])))
    # (prof, type_ens, matière, heures) 
    return sessionPlanned

def preprocessed_scheduler_placed(processed_data: pd.DataFrame):
    
    sessionPlaced = []
    for column in processed_data:
        if column == 'matière':
            continue
        session = processed_data[processed_data[column] != ''].index.tolist()
        hours = processed_data[processed_data[column] != ''][column].tolist()
        matiere= processed_data['matière'][session[0]]
        for i in range(len(session)):
            teacher = column.split(' - ')[0].strip()
            type_ens = column.split(' - ')[1].strip()
            sessionPlaced.append((teacher.strip(), type_ens.strip(), matiere, float(hours[i])))
            # (prof, type_ens, matière, heures) 

    return sessionPlaced