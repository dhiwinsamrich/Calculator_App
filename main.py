from sqlite3 import PARSE_DECLTYPES
from tkinter import *
import tkinter.font as font
from functools import partial
import ctypes
import json
import re
import pyperclip as pc

# so the functions can be used from the math module can be used in the lineedit.
from math import *

ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Tkinter Setup
root = Tk()
root.geometry("550x270")
root.title("Calculator")

# Setting icon for the Application
photo = PhotoImage(file = "icon.png")
root.iconphoto(False, photo)

# Loading Font from font name
myFont = font.Font(family='Ubuntu', size=18)
bigFont = font.Font(family='Ubuntu', size=25)
smallFont = font.Font(family='Ubuntu', size=10)

# Formula Templates
formulas = [
    ['Pythagoras->c', '(({a}**2)+({b}**2))**0.5 ? a=5 & b=5'],
    ['Pythagoras->c**2', '({a}**2)+({b}**2) ? a=5 & b=5'],
    ['pq->(x1, x2)', '-({p}/2) + sqrt(({p}/2)**2 - ({q})), -({p}/2) - sqrt(({p}/2)**2 - ({q})) ? p=-1 & q=-12'],
    ['abc->(x1, x2)', 'quadratic_formula({a}, {b}, {c}) ? a=1 & b=5 & c=6'],
    ['Incline->y', '{m}{x} + {q} ? m=4 & x=5 & q=6'],
]

# All the history equations are in this list.
history = []

# Where the history file is located.
historyFilePath = 'history.json'

print("Reading history from: ",historyFilePath )

# Creating History file if it does not exist.
try:
    with open(historyFilePath, 'x') as fp:
        pass
    print("Created file at:", historyFilePath)
except:
    print('File already exists')

currentOutPut = ''

# converting RGB values to HEX
def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

# Colors
colors = {
    'bg1': rgb_to_hex((50, 50, 50)),
    'textColor': rgb_to_hex((230, 230, 230)),
}

buttonColor = (60, 60, 60)
embuttonColor = (60, 60, 70)
historyPanelBackground = (255, 255, 255)
lineeditColor = rgb_to_hex((240, 240, 240))
fontColorNormal = rgb_to_hex((60, 60, 60))

root.configure(background=colors['bg1'])

# Add something to the current calculation
def addSymbol(event=None, symbol=None):

    if symbol == '<':
        entryVariable.set(entryVariable.get()[:-1])
    elif symbol == '↑':
        if entryVariable.get() == '':
            return
        saveCurrentInputToHistory()
        entryVariable.set(currentOutPut)
    elif symbol == 'C':
        saveCurrentInputToHistory()
        entryVariable.set('')
    else:
        entryVariable.set(entryVariable.get()+symbol)

def varChange(*args):
    global currentOutPut

    evaluationString = entryVariable.get().replace(' ', '').split('?')[0]

    print('Before insertion: ',evaluationString)

    if len(entryVariable.get().split('?')) == 2:

        parameters = entryVariable.get().replace(' ', '').split('?')[1]

        for param in parameters.split('&'):
            where, what = param.split('=')
            evaluationString = re.sub('{'+where+'}', what, evaluationString)

    if entryVariable.get() == '':
        resultLabel.config(text='Empty Input')
        return

    try:
        print('After insertion: ', evaluationString)
        resultLabel.config(text=str(eval(evaluationString)))
        currentOutPut = str(eval(evaluationString))

    except:
        resultLabel.config(text='Invalid Input')


def saveCurrentInputToHistory(event=None):
    if entryVariable.get() in history:
        return

    history.append(entryVariable.get())

    with open(historyFilePath, 'w') as file:
        file.write(json.dumps(history))

    updateListBox()

def updateListBox(event=None):
    global history

    historyList.delete(0, END)

    try:
        with open(historyFilePath, 'r') as file:
            history = json.loads(file.read())
    except json.decoder.JSONDecodeError:
        print('File does not contain JSON')

    index = 0
    for item in history:
        index+=1
        historyList.insert(index, item)
"""         index+=1
        historyList.insert(index, '') """

def setEntryFromHistory(event=None):
    historyItem = historyList.get(historyList.curselection()[0])
    entryVariable.set(historyItem)

def addFormula(formula=''):
    saveCurrentInputToHistory()
    entryVariable.set(formula)

def quadratic_formula(a, b, c):

    disc = b**2 - 4 * a * c

    x1 = (-b - sqrt(disc)) / (2 * a)
    x2 = (-b + sqrt(disc)) / (2 * a)

    return(x1, x2)

def KeyEvent(event=None):
    print(event)
    if event.keysym == 'BackSpace':
        entryVariable.set(entryVariable.get()[:-1])
    elif event.keysym == 'Return':
        addSymbol(symbol = '↑')
    else:
        entryVariable.set(entryVariable.get()+event.char)

def copyFrom(event=None, fromwhere=None):

    print('Copy: ', fromwhere)

    if fromwhere == 'input':
        pc.copy(entryVariable.get())
    elif fromwhere == 'output':
        pc.copy(currentOutPut)

def insertTo(event=None):
    entryVariable.set(pc.paste())

# Work with Frames to split the window in two parts: the calculator and the History Panel.

# Calculation Panel
calcSide = Frame(root, bg=colors['bg1'])
calcSide.pack(side=LEFT, fill=BOTH, expand=1)

# Entry Variable for the calculations
entryVariable = StringVar(root, '')
entryVariable.trace('w', varChange)

Entry(calcSide, textvariable=entryVariable, font=bigFont, borderwidth=0, relief=FLAT, disabledbackground=colors['bg1'], background=colors['bg1'],  fg=colors['textColor'], state='disable').pack(fill=X, ipady=40, padx=40)
resultLabel = Label(calcSide, text='Result', font=bigFont, borderwidth=0,anchor="e", bg=colors['bg1'], fg=colors['textColor'])
resultLabel.pack(fill=X, ipady=40, padx=40)

row = Frame(calcSide, bg=colors['bg1'])
row.pack(fill=X, side=TOP, ipady=0)
Button(row, text='Copy Input', relief='flat', font=smallFont, command=partial(copyFrom, fromwhere='input'), bg=colors['bg1'], fg=colors['textColor']).pack(side=RIGHT)
Button(row, text='Copy Output', relief='flat', font=smallFont, command=partial(copyFrom, fromwhere='output'), bg=colors['bg1'], fg=colors['textColor']).pack(side=RIGHT)
Button(row, text='Insert Clipboard', relief='flat', font=smallFont, command=insertTo, bg=colors['bg1'], fg=colors['textColor']).pack(side=RIGHT)

# History Panel
historySide = Frame(root, bg=colors['bg1'])
historySide.pack(side=LEFT, fill=BOTH, expand=1)

historyTopBar = Frame(historySide, bg=colors['bg1'])
historyTopBar.pack(fill=X)
Label(historyTopBar, text='History', fg=colors['textColor'], bg=colors['bg1'], font=smallFont).pack(side=LEFT)
Button(historyTopBar, text='Save Current Input', bg=rgb_to_hex(buttonColor), borderwidth=0, command=saveCurrentInputToHistory, fg=colors['textColor'], font=smallFont).pack(side=RIGHT)

historyList = Listbox(historySide, borderwidth=0, font=smallFont, fg=colors['textColor'], highlightthickness=0, bg=colors['bg1'])
historyList.pack(fill=BOTH, expand=True, padx=30, pady=30)
historyList.bind("<Double-Button-1>", setEntryFromHistory)

pressableKeys = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '<BackSpace>', '{', '}', '<Return>'
]

letters = '1234567890.?&=+*/-()%'
pressableKeys += list(letters)

print(pressableKeys)

for key in pressableKeys:
    root.bind(key, KeyEvent)

root.bind('<Key>', KeyEvent)

# Insert stuff into the history
updateListBox()

# Button Symbols (and their position)
symbols = [
    ['1', '2', '3', '+', '(', '{'],
    ['4', '5', '6', '-', ')', '}'],
    ['7', '8', '9', '/', 'C', 'sqrt('],
    ['0', '.', '<', '*', '↑', '**2'],
]

symbols = [
    ['1', '4', '7', '.'],
    ['2', '5', '8', '0'],
    ['3', '6', '9', '<'],
    ['+', '-', '/', '*'],
    ['(', ')', 'C', '↑'],
    ['{', '}', 'sqrt(', '**2'],
]



for rowList in symbols:

    # Make a row
    row = Frame(calcSide)
    row.pack(fill=BOTH, expand=True, side=LEFT)
    for symbol in rowList:

        if symbol in list('1234567890'):
            thisColor = rgb_to_hex(embuttonColor)

        else:
            thisColor = rgb_to_hex(buttonColor)

        # Making and packing the Button
        Button(
            row,
            text=symbol,
            command=partial(addSymbol, symbol=symbol),
            font=myFont,
            bg=thisColor,
            fg=colors['textColor'],
            borderwidth=0,
            highlightthickness=5
            ).pack(
                side=TOP,
                fill=BOTH,
                expand=1,
            )

"""         # Change button color each iteration for gradient.
        buttonColor = (buttonColor[0] - 2, buttonColor[1] - 2, buttonColor[1] - 2) """





menubar = Menu(root, bg=colors['bg1'],)


filemenu = Menu(menubar, tearoff=0)

# Add all Formulas to the dropdown menu.
for formula in formulas:
    filemenu.add_command(label=formula[0], command=partial(addFormula, formula[1]), font=smallFont)

filemenu.add_separator()

# Quit command
filemenu.add_command(label="Exit", command=root.quit, font=smallFont)

menubar.add_cascade(menu=filemenu, label='Formulas', font=smallFont)

root.config(menu=menubar)



menubar.add_command(label='Help', font=smallFont)



# Call the var change once so it is evaluated withhout actual change.
varChange('foo')

root.mainloop()