from icalendar import Calendar
import csv
from io import StringIO
import json
import os
import copy

from Backend.processed_data.sessionName import session_name
import pandas as pd



def compare_schedulers_from_spreadsheets(contentSchedulerPlanned: bytes, contentSchedulerPlaced: bytes):
    from Backend.models import compare_scheduler
    from Backend.routes.compare_scheduler import create_compare_scheduler, delete_compare_scheduler
    
    sessionsPlanned =preprocessed_data_to_csv(contentSchedulerPlanned, "scheduler_planned.csv")
    sessionsPlaced =preprocessed_data_to_csv(contentSchedulerPlaced, "scheduler_placed.csv")

    # Add line here to register every sesssion 
    sessionsPlanned=[list(s) for s in sessionsPlanned]
    sessionsPlaced=[list(s) for s in sessionsPlaced]

    sessionsPlaced=[[session[0],session[1],session[2],-session[3]] for session in sessionsPlaced]

    delete_compare_scheduler()

    for session in sessionsPlaced+sessionsPlanned:
        new_compare_scheduler = compare_scheduler(
            code_ens=session[0],
            type_ens=session[1],
            code_res_sae=session[2],
            heures=session[3],
            real_session=True
        )
        create_compare_scheduler(new_compare_scheduler)


    # Single comparison: planned vs placed
    # Positive difference = unplaced (planned but not placed)
    # Negative difference = overplaced (placed but not planned)
    differences = comparaison(sessionsPlanned,sessionsPlaced)
    
    for session in differences:
        new_compare_scheduler = compare_scheduler(
            code_ens=session[0],
            type_ens=session[1],
            code_res_sae=session[2],
            heures=session[3],
            real_session=False
        )
        create_compare_scheduler(new_compare_scheduler)


def comparaison(sessionsA, sessionsB):
    """
    Compare two lists of sessions.
    Returns sessions from A with non-zero difference (after subtracting matching B sessions).
    Also includes sessions from B that have no match in A (as negative values).
    """
    # Convert tuples to lists so they can be modified

    sessionsAInstance=copy.deepcopy(sessionsA)
    # Track which B sessions have been matched

    for sessionA in sessionsAInstance:
        for i, sessionB in enumerate(sessionsB):
            if(sessionA[0]==sessionB[0] and sessionA[1]==sessionB[1] and sessionA[2]==sessionB[2]):
                # Match found: subtract placed hours from planned hours
                sessionA[3] += sessionB[3]
                break

    for sessionB in sessionsB:
        for i, sessionA in enumerate(sessionsA):
            if(sessionA[0]==sessionB[0] and sessionA[1]==sessionB[1] and sessionA[2]==sessionB[2]):

                sessionB[3] += sessionA[3]
                break

    result= sessionsAInstance + sessionsB
    
    result = [session for session in result if session[3] != 0.0]
    
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
        sessionPlanned.append((row['code_ens'].strip(), type_ens.strip(), session_name[row['code_res_sae'].strip()], float(row['volume'])))
    # (prof, type_ens, matière, heures) 
    return sessionPlanned

def preprocessed_scheduler_placed(processed_data: pd.DataFrame):
    
    dictMatiere = processed_data['matière'].map(lambda x: x.strip()).tolist()

    sessionPlaced = []
    for column in processed_data:
        if column == 'matière':
            continue
        session = processed_data[processed_data[column] != ''].index.tolist()
        hours = processed_data[processed_data[column] != ''][column].tolist() 
        for i in range(len(hours)):
            teacher = column.split(' - ')[0].strip()
            type_ens = column.split(' - ')[1].strip()
            sessionPlaced.append((teacher.strip(), type_ens.strip(), dictMatiere[session[i]], float(hours[i])))
            # (prof, type_ens, matière, heures) 

    return sessionPlaced

