# coding=utf-8
import easygui as g
import sys

while 1:
    g.msgbox('Welcome to first GUI game!')

    msg = 'This is an information!'
    title = 'RaiykuGame'
    choices=[1,2,3,4]
    choices = g.choicebox(msg,title,choices)

    # note that we convert choice to string, in case
    # the user cancelled the choice, and we got None.
    # def msgbox(msg="(Your message goes here)", title="", ok_button="OK"):
    g.msgbox('What you Select is: '+str(choices),' Result.')

    msg = 'Do you want to restart it?'
    title = 'Please Select'

    if g.ccbox(msg,title):  # show a Continue/Cancel dialog
        pass # user chose Continue
    else:
        sys.exit(0) # user chose Cancel