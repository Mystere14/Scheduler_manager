from datetime import date

from icalendar import Calendar
import csv
from io import StringIO
import json
import os
import copy

import pandas as pd

from routes.lesson import  getFalseLesson, getLesson



def lessonFromSpreadsheets(contentSchedulerPlanned: bytes, contentSchedulerPlaced: bytes):
    from models import lesson
    from routes.lesson import createLesson, deleteTrueLesson
    

    lessonsPlanned =preprocessedDataToCsv(contentSchedulerPlanned, "schedulerPlanned.csv")
    lessonsPlaced = getFalseLesson()

    # Add line here to register every lesson 
    lessonsPlanned=[list(s) for s in lessonsPlanned]

    lessonsPlaced=[[lesson.codeEns,lesson.typeEns.split("_")[0],lesson.week,lesson.codeResSae,-lesson.hour,lesson.typeEns] for lesson in lessonsPlaced]
    
    differences = comparaison(lessonsPlanned,lessonsPlaced)

    deleteTrueLesson()

    # Single comparison: planned vs placed
    # Positive difference = unplaced (planned but not placed)
    # Negative difference = overplaced (placed but not planned)
    
    lessonsNotPlaced= [lesson for lesson in differences if lesson[4] > 0]

    for lessons in lessonsPlaced + lessonsNotPlaced:

        isValid=not (lessons in differences)

        if(not isValid):
            differences.remove(lessons)

        group = ""

        if(len(lessons)==6):
            group = lessons[-1]
        else:
            group= lessons[1]
        
        newLesson = lesson(
            codeEns=lessons[0],
            typeEns=group,
            codeResSae=lessons[3],
            week=lessons[2],
            hour=lessons[4],
            isValid=isValid,
            isLesson=True
        )
        createLesson(newLesson)

        print(newLesson)
        

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


def preprocessedDataToCsv(contentFile: bytes, fileName: str):
    data = json.loads(contentFile.decode('utf-8'))

    processedData = pd.DataFrame(data['data'])
    
    everySession = pd.DataFrame()

    if fileName == "schedulerPlanned.csv":
        everySession = preprocessedSchedulerPlanned(processedData)

    if fileName == "schedulerPlaced.csv":
        everySession = preprocessedSchedulerPlaced(processedData)

    return everySession


def preprocessedSchedulerPlanned(processedData: pd.DataFrame):

    lessonPlanned = []

    for _, row in processedData.iterrows():
        typeEns = row['typeEns'].strip()
        if typeEns == 'C':
            typeEns = 'COURS'
        lessonPlanned.append((row['codeEns'].strip(), typeEns.strip(), row['week'].strip(), row['codeResSae'].strip(), float(row['volume'])))
    return lessonPlanned


def preprocessedSchedulerPlaced(processedData: pd.DataFrame):

    dateAndSubject = processedData['matière'].map(lambda x: x.strip()).tolist()
    listSubject= [dateAndSubject[i].split(' ')[0] for i in range(len(dateAndSubject))]
    listDate= [dateAndSubject[i].split(' ')[1] for i in range(len(dateAndSubject))]


    lessonPlaced = []
    for column in processedData:
        if column == 'matière':
            continue
        lesson = processedData[processedData[column] != ''].index.tolist()
        hours = processedData[processedData[column] != ''][column].tolist() 
        for i in range(len(hours)):
            teacher = column.split(' - ')[0].strip()
            typeEns = column.split(' - ')[1].strip()
            lessonPlaced.append((teacher.strip(), typeEns.strip(), listDate[lesson[i]], listSubject[lesson[i]], float(hours[i])))
    return lessonPlaced

