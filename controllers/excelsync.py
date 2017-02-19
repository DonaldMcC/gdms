#! /usr/bin/env python

#from Tkinter import Tk
from time import sleep
#from tkMessageBox import showwarning
import datetime
#warn = lambda app: showwarning(app, 'Exit?')
import win32com.client as win32


def excel():
    app = 'Excel'
    xl = win32.gencache.EnsureDispatch('%s.Application' % app)

    excel = win32.gencache.EnsureDispatch('Excel.Application')
    # wb = excel.Workbooks.Add()
    wb = excel.Workbooks.Open(r'c:\web2py\applications\gdms\private\ProjectMappingTest1.xlsx')
    ws = wb.Worksheets("Sheet2")

    xl.Visible = True
    sleep(1)

    # so lets change to get one record at a time - however maybe transferring the whole list
    # is better and then we just slice the big list into rows
    myplan = ws.Range("Plan")

    # So we will have a list of tuples which will allow rows to map to corresponding value
    # in a dictionary when we retrieve corresponding values from row to write back then
    # for writing back we just write in the order
    SourceColumns = [('w2pid', 'id'), ('Level', 'None'), ('Number', 'None'), ('Classification', 'None'),
                     ('Start', 'Startdate'), ('EndDate', 'Enddate'), ('Description', 'questiontext'),
                     ('Owner', 'Responsible'), ('Status', 'Execstatus'), ('Actstart', 'None'), ('Actend', 'None'),
                     ('Dependency', 'None'), ('Notes', 'Notes')]

    SourceColumns = [('w2pid', 'id'), ('Level', 'None'), ('Number', 'None'), ('Classification', 'None'),
                     ('Start', 'startdate'), ('EndDate', 'enddate'), ('Description', 'questiontext'),
                     ('Owner', 'responsible'), ('Status', 'None'), ('Actstart', 'None'), ('Actend', 'None'),
                     ('Dependency', 'None'), ('Notes', 'notes')]

    rowlength = len(SourceColumns)
    numrows = len(myplan) / rowlength
    print rowlength

    myrows = []
    myrow = []
    for i, x in enumerate(myplan):
        myrow.append(x.Value)
        if (i + 1) % rowlength == 0:
            myrows.append(myrow)
            myrow = []

    for x in myrows:
        rowdict = dict()
        for i, y in enumerate(x):
            if SourceColumns[i][1] != 'None':
                rowdict[SourceColumns[i][1]] = y
        rowdict['qtype'] = 'action'
        rowdict['status'] = 'Agreed'
        rowdict['startdate'] = datetime.datetime.fromtimestamp (int(rowdict['startdate']))
        rowdict['enddate'] = datetime.datetime.fromtimestamp(int(rowdict['enddate']))

        if rowdict['id'] is None:
            db.question.insert(**rowdict)


    # Alternately, specify the full path to the workbook
    # wb = excel.Workbooks.Open(r'C:\myfiles\excel\workbook2.xlsx')
    #excel.Visible = True

    # warn(app)
    wb.Save()
    excel.Application.Quit()
    return locals()

