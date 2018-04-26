#!/usr/local/bin/pythonw

#At the moment 2.7 only

from urllib import *
from xml.dom import minidom
import webbrowser

try:
    from Tkinter import * # as tk
except ImportError:
    from tkinter import *

#try :
from os import system
#except ImportError :
#    pass

import ConfigParser
#import glob
################################################################################
mouseEvent="<Button-2>"
openArtTxt="Open Article"
feedsWinTitle="RSS News Feed"
oddTitleColor="#FFFFFF"
oddDescColor="#FFFFFF"
evenTitleColor="#B0FFB0"
evenDescColor="#D0FFD0"
mouseScale=1
titleFont="Times New Roman"
titleSize=18
titleFace="bold italic"
descFont="Times New Roman"
descSize=14
descFace="normal"
winGeoetry="1000x500"

parser = ConfigParser.RawConfigParser(allow_no_value=True)
parser.optionxform = str    # Keeps the case on the Keys
readFiles = parser.read('rssSettings.ini')
for name, value in parser.items('rssFeedSettings') :
        globals()[name] = value
############################# Create our Articles List ###########################
def getArticles(feedList):
    articles = dict()

    for key,urlStr in feedList :
        try:
            usock = urlopen(urlStr)
            xmldoc = minidom.parse(usock)
            for item in xmldoc.getElementsByTagName('item'):
                akey = item.getElementsByTagName('guid').item(0).firstChild.nodeValue
                try:
                    akey = akey[:akey.index("?")]
                except:
                    pass
                articles[akey] = item
        except:
            pass
    return articles
############################################################################
class NewsItem(Message):
    def __init__(self, parent, *args, **kwargs):
        self.theUrl = kwargs.pop('passedUrl','http://duckduckgo.com')
        Message.__init__(self, parent, *args, **kwargs)
        self.popup_menu = Menu(self, tearoff=0)
        self.popup_menu.add_command(label=openArtTxt, command=self.display_selected)
        self.popup_menu.add_command(label="Copy Link", command=self.copy_link)
        self.popup_menu.add_command(label="Read line", command=self.read_this)
        self.bind(mouseEvent, self.popup) # Button-2 on Aqua
        self.myParent = parent

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def display_selected(self):
        webbrowser.open_new(self.theUrl)

    def copy_link(self):
        top.clipboard_clear()
        top.clipboard_append(self.theUrl)

    def read_this(self):
        theText = 'say "{:s}"'.format(self.cget("text").encode("utf-7","ignore"))
        #print theText
        try:
            system(theText)
        except Exception as e:
            print (e)
            print ("Whoops")
            e = sys.exc_info()[0]
            write_to_page( "<p>Error: %s</p>" % e )
###############################################################################
class ScrollFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.canvas = Canvas(parent, borderwidth=0, background="#40FF40")
        self.frame = Frame(self.canvas, background="#D0E0FF")

        self.vsb = Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y",expand=False)

        self.hsb = Scrollbar(parent, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.hsb.set)
        self.hsb.pack(side="bottom", fill="x",expand=False)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.frame_id = self.canvas.create_window((0,0), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.artList = []

    def _on_mousewheel(self, event):
        #self.canvas.yview_scroll(-1*(event.delta/mouseScale), "units")
        self.canvas.yview_scroll(-1*(event.delta/abs(event.delta)), "units")

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        theW =  self.canvas.winfo_width() - 25
        for widget in self.artList:
            widget.config(width = (theW))

    def addEntry(self, n, t1, t2, u1):
        theColour = oddTitleColor
        blurbColour = oddDescColor
        if (n % 2 == 1) :
            theColour = evenTitleColor
            blurbColour = evenDescColor

        nws = NewsItem(self.frame, text=t1, bg=theColour,font=(titleFont,titleSize,titleFace),anchor=W,justify=LEFT,passedUrl=u1)
        nws.pack(side="top", anchor="w", fill="x", expand=True)
 #       nws.bind("<Configure>", lambda e: nws.configure(width=e.width-10))
        self.artList.append(nws)

        nws = NewsItem(self.frame, text=t2, bg=blurbColour,font=(descFont,descSize,descFace),anchor=W,justify=LEFT,passedUrl=u1)
        nws.pack(side=TOP, anchor=W, fill=X, expand=True)
 #       nws.bind("<Configure>", lambda e: nws.configure(width=e.width-10))
        self.artList.append(nws)
###############################################################################
top = Tk()
top.wm_title (feedsWinTitle)
top.geometry(winGeoetry)
wFrame = ScrollFrame(top,padx="5",pady="5")
###################################################################################
articles = getArticles(parser.items('feeds'))
artKeys = articles.keys()
theRow = 0
for key in artKeys:
    item = articles[key]
    desc = item.getElementsByTagName('description').item(0).lastChild.nodeValue
    try:
        desc = desc[:desc.index("<")]
    except:
        pass
    currUrl = item.getElementsByTagName('link').item(0).lastChild.nodeValue
    myTitle = item.getElementsByTagName('title').item(0).firstChild.nodeValue
    wFrame.addEntry(theRow, myTitle, desc,currUrl)

    theRow = theRow + 1
###################################################################################
top.mainloop()
