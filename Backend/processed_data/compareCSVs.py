from datetime import date

from icalendar import Calendar
import csv
from io import StringIO
import json
import os
import copy

from Backend.processed_data.sessionName import session_name
import pandas as pd



def sessions_from_spreadsheets(contentSchedulerPlanned: bytes, contentSchedulerPlaced: bytes):
    from Backend.models import session
    from Backend.routes.session import create_session, delete_session
    
    sessionsPlanned =preprocessed_data_to_csv(contentSchedulerPlanned, "scheduler_planned.csv")
    sessionsPlaced =preprocessed_data_to_csv(contentSchedulerPlaced, "scheduler_placed.csv")

    # Add line here to register every sesssion 
    sessionsPlanned=[list(s) for s in sessionsPlanned]
    sessionsPlaced=[list(s) for s in sessionsPlaced]

    sessionsPlaced=[[session[0],session[1],session[2],session[3],-session[4]] for session in sessionsPlaced]
    
    differences = comparaison(sessionsPlanned,sessionsPlaced)

    delete_session()

    # Single comparison: planned vs placed
    # Positive difference = unplaced (planned but not placed)
    # Negative difference = overplaced (placed but not planned)
    
    sessionsNotPlaced= [session for session in differences if session[4] > 0]

    for session in sessionsPlaced + sessionsNotPlaced:
        is_valid=not (session in differences)
        new_session = session(
            code_ens=session[0],
            type_ens=session[1],
            code_res_sae=session[3],
            semaine=session[2],
            heures=session[4],
            is_valid=is_valid
        )
        create_session(new_session)


def comparaison(sessionsA, sessionsB):
    """
    Compare two lists of sessions.
    Returns sessions from A with non-zero difference (after subtracting matching B sessions).
    Also includes sessions from B that have no match in A (as negative values).
    """
    # Convert tuples to lists so they can be modified

    sessionsAInstance=copy.deepcopy(sessionsA)
    sessionsBInstance=copy.deepcopy(sessionsB)
    # Track which B sessions have been matched

    for sessionA in sessionsAInstance:
        for i, sessionB in enumerate(sessionsB):
            if(sessionA[0]==sessionB[0] and sessionA[1]==sessionB[1] and sessionA[2]==sessionB[2] and sessionA[3]==sessionB[3]):
                # Match found: subtract placed hours from planned hours
                sessionA[4] += sessionB[4]
                break

    for sessionB in sessionsBInstance:
        for i, sessionA in enumerate(sessionsA):
            if(sessionA[0]==sessionB[0] and sessionA[1]==sessionB[1] and sessionA[2]==sessionB[2] and sessionA[3]==sessionB[3]):

                sessionB[4] += sessionA[4]
                break

    result= sessionsAInstance + sessionsBInstance
    
    result = [session for session in result if session[4] != 0.0]
    
    return result


def preprocessed_data_to_csv(content_file: bytes, file_name: str):
    data = json.loads(content_file.decode('utf-8'))

    processed_data = pd.DataFrame(data['data'])
    
    everySession = pd.DataFrame()

    if file_name == "scheduler_planned.csv":
        everySession = preprocessed_scheduler_planned(processed_data)

    if file_name == "scheduler_placed.csv":
        everySession = preprocessed_scheduler_placed(processed_data)

    return everySession


def preprocessed_scheduler_planned(processed_data: pd.DataFrame):
    sessionPlanned = []

    for _, row in processed_data.iterrows():
        type_ens = row['type_ens'].strip()
        if type_ens == 'C':
            type_ens = 'AMPHI'
        sessionPlanned.append((row['code_ens'].strip(), type_ens.strip(), row['semaine'].strip(), session_name[row['code_res_sae'].strip()], float(row['volume'])))
    # (prof, type_ens, année-semaine, matière, heures) 
    return sessionPlanned


def preprocessed_scheduler_placed(processed_data: pd.DataFrame):

    dateAndSubject = processed_data['matière'].map(lambda x: x.strip()).tolist()
    listSubject= [dateAndSubject[i].split(' ')[0] for i in range(len(dateAndSubject))]
    listDate= [dateAndSubject[i].split(' ')[1] for i in range(len(dateAndSubject))]


    sessionPlaced = []
    for column in processed_data:
        if column == 'matière':
            continue
        session = processed_data[processed_data[column] != ''].index.tolist()
        hours = processed_data[processed_data[column] != ''][column].tolist() 
        for i in range(len(hours)):
            teacher = column.split(' - ')[0].strip()
            type_ens = column.split(' - ')[1].strip()
            sessionPlaced.append((teacher.strip(), type_ens.strip(), listDate[session[i]], listSubject[session[i]], float(hours[i])))
            # (prof, type_ens, année-semaine, matière, heures) 
    return sessionPlaced

