from datetime import date

from icalendar import Calendar
import csv
from io import StringIO
import json
import os
import copy

import pandas as pd

from routes.lesson import create_lesson, delete_lesson, get_false_lesson, get_lesson



def lesson_from_spreadsheets(contentSchedulerPlanned: bytes, contentSchedulerPlaced: bytes):
    from models import lesson
    from routes.lesson import create_lesson, delete_true_lesson
    

    lessonsPlanned =preprocessed_data_to_csv(contentSchedulerPlanned, "scheduler_planned.csv")
    lessonsPlaced = get_false_lesson()

    # Add line here to register every lesson 
    lessonsPlanned=[list(s) for s in lessonsPlanned]

    lessonsPlaced=[[lesson.code_ens,lesson.type_ens.split("_")[0],lesson.semaine,lesson.code_res_sae,-lesson.heures,lesson.type_ens] for lesson in lessonsPlaced]
    
    differences = comparaison(lessonsPlanned,lessonsPlaced)

    delete_true_lesson()

    # Single comparison: planned vs placed
    # Positive difference = unplaced (planned but not placed)
    # Negative difference = overplaced (placed but not planned)
    
    lessonsNotPlaced= [lesson for lesson in differences if lesson[4] > 0]

    for lessons in lessonsPlaced + lessonsNotPlaced:
        print(f"{lessons=}")

        is_valid=not (lessons in differences)

        if(not is_valid):
            differences.remove(lessons)

        group = lessons[1] if len(lessons)==6 else lessons[-2]
        
        new_lesson = lesson(
            code_ens=lessons[0],
            type_ens=group,
            code_res_sae=lessons[3],
            semaine=lessons[2],
            heures=lessons[4],
            is_valid=is_valid,
            is_lesson=True
        )
        create_lesson(new_lesson)
        

def comparaison(lessonsA, lessonsB):
    """
    Compare two lists of lessons.
    Returns lessons from A with non-zero difference (after subtracting matching B lessons).
    Also includes lessons from B that have no match in A (as negative values).
    """
    # Convert tuples to lists so they can be modified

    lessonsAInstance=copy.deepcopy(lessonsA)
    lessonsBInstance=copy.deepcopy(lessonsB)
    # Track which B lessons have been matched

    for lessonA in lessonsAInstance:
        for i, lessonB in enumerate(lessonsBInstance):
            if(lessonA[0]==lessonB[0] and lessonA[1]==lessonB[1] and lessonA[2]==lessonB[2] and lessonA[3]==lessonB[3]):
                # Match found: subtract placed hours from planned hours
                temp=lessonA[4]
                lessonA[4] += lessonB[4]
                lessonB[4] += temp
                lessonsBInstance = [lesson for lesson in lessonsBInstance if lesson[4] != 0.0]
                lessonsAInstance = [lesson for lesson in lessonsAInstance if lesson[4] != 0.0]
                break

    result= lessonsAInstance + lessonsBInstance

    result = [lesson for lesson in result if lesson[4] != 0.0]

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

    lessonPlanned = []

    for _, row in processed_data.iterrows():
        type_ens = row['type_ens'].strip()
        if type_ens == 'C':
            type_ens = 'COURS'
        lessonPlanned.append((row['code_ens'].strip(), type_ens.strip(), row['semaine'].strip(), row['code_res_sae'].strip(), float(row['volume'])))
    # (prof, type_ens, année-semaine, matière, heures) 
    return lessonPlanned


def preprocessed_scheduler_placed(processed_data: pd.DataFrame):

    dateAndSubject = processed_data['matière'].map(lambda x: x.strip()).tolist()
    listSubject= [dateAndSubject[i].split(' ')[0] for i in range(len(dateAndSubject))]
    listDate= [dateAndSubject[i].split(' ')[1] for i in range(len(dateAndSubject))]


    lessonPlaced = []
    for column in processed_data:
        if column == 'matière':
            continue
        lesson = processed_data[processed_data[column] != ''].index.tolist()
        hours = processed_data[processed_data[column] != ''][column].tolist() 
        for i in range(len(hours)):
            teacher = column.split(' - ')[0].strip()
            type_ens = column.split(' - ')[1].strip()
            lessonPlaced.append((teacher.strip(), type_ens.strip(), listDate[lesson[i]], listSubject[lesson[i]], float(hours[i])))
            # (prof, type_ens, année-semaine, matière, heures) 
    return lessonPlaced

