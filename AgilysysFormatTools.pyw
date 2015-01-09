#!/usr/bin/python

import os
import sys
import re
import codecs
import datetime
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from Things import MenuItemThings
from Things.SheetWrapper import FitSheetWrapper
from tkinter import filedialog
from tempfile import TemporaryFile
from xlwt import Workbook, easyxf
from xlrd import open_workbook

priceArrayMatch = re.compile(r'(?<=\{)[^(\{|\})].+?(?=\})')
IG_EXPORT = 1
SIMPLE_EXPORT = 3
UNKNOWN_EXPORT = 10
CSV_EXPORT = 2
itemList = []
itemMap = {}

def ezPrint(string):
    print(str(string))
    
def openFile(options=None):
    if options == None:
        options = {}
        options['defaultextension'] = '.txt' 
        options['filetypes'] = [('Text Files', '.txt'), ('CSV Files', '*.csv*'), ('All Files', '.*')]
        options['title'] = 'Open...'
    file_opt = options
    global file_path
    file_path = filedialog.askopenfilename(**file_opt)
    options = None
    if file_path == None or file_path == "":
        print("No file selected")
    openFileString.set(str(os.path.basename(file_path)))
    if determineExportType(file_path) == IG_EXPORT:
        conversionButtonText.set("Simplify")
    else:
        conversionButtonText.set("Generate IG Update")
        
    showButton()
    
def saveFile(options):
        
    file_opt = options
    global csv_file
    global save_file
    csv_file = str(file_path)[:-4] + ".csv"
    save_file = filedialog.asksaveasfilename(**file_opt)
    if save_file == None or save_file == "":
        print("No file selected")
        
def fixArray(match):
    match = str(match.group(0))
    return match.replace(",",";")
    
def preParse(file_name, output):
    with codecs.open(file_name, 'r', 'latin-1') as export:
        print('pre-parse initiated')
        index = 1
        for x in export:
            itemDetails = re.sub(priceArrayMatch, fixArray, x)
            item = itemDetails.split(",")
            i = MenuItemThings.MenuItem(
                                    item[1], item[2], item[3], item[4], item[5],
                                    item[6], item[7], item[8], item[9], item[10],
                                    item[11], item[12], item[13], item[14], item[15],
                                    item[16], item[18], item[19], item[20], item[21],
                                    item[22], item[23], item[24], item[25], item[26],
                                    item[28], item[29], item[30], item[31]
                                    )
#             print('Item:\n' + i.toString())
            itemList.append(i)
            itemMap[i.id] = i
            try:
                output.write(itemDetails)
            except UnicodeEncodeError:
                errorText = "\n\n!!!!!!!!!!!!!!!!!!!!!!!\nerror encoding string for print/output\n!!!!!!!!!!!!!!!!!!!!!!!!!\n\n"
                print(errorText)
                output.write("error processing item " + str(i.id) + "\n")
            index += 1
    print("completed")
    
def readFromExcel(file=None):
    if file == None:
        file = 'simple_export.xls'
    
    book = open_workbook(file)
    print('openning ' + str(file))
    sheet = book.sheet_by_index(0)
    
    print('name: ' + sheet.name)
    print('number of rows: ' + str(sheet.nrows))
    print('number of columns: ' + str(sheet.ncols))
    print(str(sheet.row(0)))
    
    
def enumeratePriceLevels():
    numberOfPriceLevels = 0
    for item in itemList:
        if len(item.separatePriceLevels()) > numberOfPriceLevels:
            numberOfPriceLevels = len(item.separatePriceLevels())
    return numberOfPriceLevels

def generateSimpleExport(items=itemList, altered=True, goExcel=False):
    print('Generating Simple Export')
    simpleOutput = codecs.open(save_file, 'w+', 'utf8')
    
    book = Workbook()
    heading = easyxf(
        'font: bold True;'
        'alignment: horizontal center;'
        )
    sheet = book.add_sheet('Sheet 1')
    sheet.panes_frozen = True
    sheet.remove_splits = True
    sheet.horz_split_pos = 1
    row1 = sheet.row(0)
    row1.write(0, 'ID', heading)
    row1.write(1, 'Name', heading)
    
    numberOfPriceLevels = enumeratePriceLevels()
    for x in range(numberOfPriceLevels):
        col = x + 2
        row1.write(col, 'Price Level ' + str(x + 1), heading)
        sheet.col(col).width = 4260
    
    for i,item in zip(range(1, len(items) + 1),items):
        if altered:
            if item.priceLevels != "{}":
                simpleOutput.write(str(item.id) + "," + str(item.name) + "," + str(item.priceLevels) + "\r\n")
        else:
            simpleOutput.write(str(item.id) + "," + str(item.name) + "," + str(item.priceLevels) + "\r\n")
        row = sheet.row(i)
        row.write(0, str(item.id))
        row.write(1, str(item.name))
        for p in range(1, (numberOfPriceLevels + 1)):
            if p in item.separatePriceLevels():
                price = item.separatePriceLevels()[p]
            else:
                price = ''
            row.write((p + 1), str(price))
    
    sheet.col(1).width = 12780
    book.save('simple_export.xls')
    
    if goExcel:
        print('Converting to Excel')
        convertToExcel(items, altered)
    else:
        print('Completed Simplify procedure without converting to Excel')
        
    messagebox.showinfo(title='Success', message='Simplified item export created successfully.')
        
def convertToExcel(items=itemList, altered=True):
    print('preparing to convert to Excel')
    book = Workbook()
    heading = easyxf(
        'font: bold True;'
        'alignment: horizontal center;'
        )
    sheet = book.add_sheet('Sheet 1')
    sheet.panes_frozen = True
    sheet.remove_splits = True
    sheet.horz_split_pos = 1
    row1 = sheet.row(0)
    row1.write(0, '0', heading)
    sheet.col(0).hidden = True
    row1.write(1, '"U"', heading)
    row1.write(2, 'ID', heading)
    row1.write(3, 'Name', heading)
    row1.write(4, 'Abbr1', heading)
    row1.write(5, 'Abbr2', heading)
    row1.write(6, 'Kitchen Printer Label', heading)
    row1.write(7, 'Price(s)', heading)
    row1.write(8, 'Product Class ID', heading)
    row1.write(9, 'Revenue Category ID', heading)
    row1.write(10, 'Tax Group ID', heading)
    row1.write(11, 'Security Level ID', heading)
    row1.write(12, 'Report Category ID', heading)
    row1.write(13, 'Use Weight Flagh', heading)
    row1.write(14, 'Weight Tare Amount', heading)
    row1.write(15, 'SKU Number', heading)
    row1.write(16, 'Bar Gun Code', heading)
    row1.write(17, 'Cost Amount', heading)
    row1.write(18, 'Reserved', heading)
    row1.write(19, 'Prompt for Price Flag', heading)
    row1.write(20, 'Print on Check Flag', heading)
    row1.write(21, 'Discountable Flag', heading)
    row1.write(22, 'Voidable Flag', heading)
    row1.write(23, 'Not Active Flag', heading)
    row1.write(24, 'Tax Included Flag', heading)
    row1.write(25, 'Menu Item Group ID', heading)
    row1.write(26, 'Customer Receipt Text', heading)
    row1.write(27, 'Allow Price Override Flag', heading)
    row1.write(28, 'Reserved', heading)
    row1.write(29, 'Choice Groups', heading)
    row1.write(30, 'Kitchen Printers (Logical)', heading)
    row1.write(31, 'Covers', heading)
    row1.write(32, 'Store ID', heading)
    for i in range(1, 32):
        sheet.row(1).set_cell_boolean(i, False)
    sheet.row(1).set_cell_boolean(2, True)
    
    print('headings written')
    
    for i,item in zip(range(2, len(items) + 2),items):
        row = sheet.row(i)
        row.write(2, str(item.id))
        row.write(3, str(item.name))
        row.write(4, str(item.abbr1))
        row.write(5, str(item.abbr2))
        row.write(6, str(item.printerLabel))
        row.write(7, str(item.priceLevels))
        row.write(8, str(item.classID))
        row.write(9, str(item.revCategoryID))
        row.write(10, str(item.taxGroup))
        row.write(11, str(item.securityLevel))
        row.write(12, str(item.reportCategory))
        row.write(13, str(item.useWeightFlag))
        row.write(14, str(item.weightTareAmount))
        row.write(15, str(item.sku))
        row.write(16, str(item.gunCode))
        row.write(17, str(item.costAmount))
        row.write(18, 'N/A')
        row.write(19, str(item.pricePrompt))
        row.write(20, str(item.checkPrintFlag))
        row.write(21, str(item.discountableFlag))
        row.write(22, str(item.voidableFlag))
        row.write(23, str(item.inactiveFlag))
        row.write(24, str(item.taxIncludeFlag))
        row.write(25, str(item.itemGroupID))
        row.write(26, str(item.receiptText))
        row.write(27, str(item.priceOverrideFlag))
        row.write(28, 'N/A')
        row.write(29, str(item.choiceGroups))
        row.write(30, str(item.kitchenPrinters))
        row.write(31, str(item.covers))
        row.write(32, str(item.storeID))
    
    book.save('complete_export.xls')
    print('excel workbook saved')

    messagebox.showinfo(title='Success', message='Excel export created successfully.')
        
def generateIGPriceUpdate(inputFile, updateFile):
    print('preparing to generate IG Price Update file')
    if inputFile[-3:] == 'xls' or inputFile[-4:] == 'xlsx':
        print('generating IG Update from xls')
        book = open_workbook(inputFile)
        sheet = book.sheet_by_index(0)
        if sheet.ncols > 3:
            if sheet.cell_value(1,1) == True or sheet.cell_value(1,1) == False:
                generateIGUpdate(book, updateFile)
                return
            print('Extra Price Levels found.')
            for row in range(1, sheet.nrows):
                prices = []
                for col in range(2, sheet.ncols):
                    if sheet.cell_value(row,col) != '':
                        priceLevel = str(col - 1) + ',' + str(sheet.cell_value(row,col))
                        prices.append(priceLevel)
                priceImport = '{' + ','.join(prices) + '}'
                line = '"U",' + str(sheet.cell_value(row, 0)) + ',,,,,' + str(priceImport) + ',,,,,,,,,,,,,,,,,\r\n'
                updateFile.write(line)
        else:
            print('Processing with a single price level')
            for row in range(1, sheet.nrows):
                line = '"U",' + str(sheet.cell_value(row, 0)) + ',,,,,' + str(cell_value(row,2)) + ',,,,,,,,,,,,,,,,,\r\n'
    else:
        print('generating IG Update from txt or csv')
        with codecs.open(file_path, 'r', 'utf8') as file:
            for x in file:
                details = x.split(",")
                details[2] = details[2].replace(";", ",").strip("\r\n")
                line = '"U",' + str(details[0]) + ',,,,,' + str(details[2]) + ',,,,,,,,,,,,,,,,,\r\n'
                updateFile.write(line)

    messagebox.showinfo(title='Success', message='IG Item Import created successfully.')

def generateIGUpdate(book, updateFile):
    print('preparing to generate IG Update file')
    sheet = book.sheet_by_index(0)
    includeColumns = set()
    
    for col in range(3, sheet.ncols):
        if sheet.cell_value(1, col) == True:
            includeColumns.add(col)
            
    for row in range(2, sheet.nrows):
        itemProperties = []
        if sheet.cell_value(row,1) != 'A' and sheet.cell_value(row,1) != 'U' and sheet.cell_value(row,1) != 'D':
            itemProperties.append('"U"')
        else:
            itemProperties.append('"' + str(sheet.cell_value(row,1)) + '"')
        itemProperties.append(str(sheet.cell_value(row,2)))
        previousIndex = 2
        for col in includeColumns:
            emptySpaces = col - previousIndex - 1
            for x in range(emptySpaces):
                itemProperties.append('')
            itemProperties.append(str(sheet.cell_value(row,col)))
            previousIndex = col
        if len(itemProperties) < 32:
            for x in range(32 - len(itemProperties)):
                itemProperties.append('')
        line = ",".join(itemProperties).replace(";",",")
        updateFile.write(line + "\r\n")

    messagebox.showinfo(title='Success', message='IG Item Import created successfully.')
    
def determineExportType(f):
    if f[-3:] == 'xls':
        print('Input file is xls, processing as SIMPLE_EXPORT')
        return SIMPLE_EXPORT
    else:
        file = codecs.open(f, 'r', 'utf8')
        if len(file.readline().split(",")) > 20:
            return IG_EXPORT
        else:
            return SIMPLE_EXPORT
        
def runConversion():

    export = file_path
        
    if conversionButtonText.get() == "Simplify":
        print('simplifying...')
        options = {}
        options['title'] = 'Save As'
        options['initialfile'] = str(file_path)[:-4] + "_simplified" + str(file_path)[-4:]
        saveFile(options)
        output = codecs.open(csv_file, 'w+', 'utf8')
        try:
            preParse(export, output)
        except UnicodeDecodeError:
            export = codecs.open(file_path, 'r', 'latin-1')
            preParse(export, output)
        generateSimpleExport(altered=truncate.get(), goExcel=includeExcel.get())
    else:
        options = {}
        options['title'] = 'Save As'
        options['initialfile'] = 'MI_IMP.txt'
        saveFile(options)
        output = codecs.open(save_file, 'w+', 'latin-1')
        generateIGPriceUpdate(export, output)

def hideButton():
    thatButton.grid_remove()
    
def showButton():
    thatButton.grid()

root = Tk()
root.option_add('*tearOff', FALSE)
root.title("Agilysy File Tools")

save_syserr = sys.stderr
fsock = open('error.log', 'a+')
sys.stderr = fsock

openFileString = StringVar()
conversionButtonText = StringVar()
truncate = StringVar()
includeExcel = StringVar()

menubar = Menu(root)
menu_file = Menu(menubar)
menu_options = Menu(menubar)
menubar.add_cascade(menu=menu_file, label='File')
menubar.add_cascade(menu=menu_options, label='Options')

menu_file.add_command(label='Open...', command=openFile)
menu_file.add_command(label='Close', command=root.quit)

menu_options.add_checkbutton(label='Condense Simplified Output', variable=truncate, onvalue=1, offvalue=0)
menu_options.add_checkbutton(label='Generate Complete Excel Export', variable=includeExcel, onvalue=1, offvalue=0)

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=1, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(1, weight=1)

ttk.Label(mainframe, text="Input File:").grid(column=1, row=1, sticky=(N, W, E))
openFile_entry = ttk.Entry(mainframe, width=40, textvariable=openFileString)
openFile_entry.grid(column=1, row=2, sticky=(W, E))

global thatButton
thatButton = ttk.Button(mainframe, textvariable=conversionButtonText, command=runConversion)
thatButton.grid(column=1, row=3)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

root.config(menu=menubar)
hideButton()
root.mainloop()