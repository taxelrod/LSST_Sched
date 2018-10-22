"""
Parse the HTML file for each CSC that defines its Commands
"""

import os
import re
from html.parser import HTMLParser

class TsHTMLParser(HTMLParser):

    def __init__(self, callback, *callbackArgs):
        HTMLParser.__init__(self)
        self.callback = callback
        self.callbackArgs = callbackArgs
        self.collecting = False
        self.collected = ''
    
    def handle_starttag(self, tag, attrs):
        if tag=='tr':
            self.collecting = True

    def handle_endtag(self, tag):
        if tag=='tr':
            self.collecting = False
            self.callback(self.collected, self.callbackArgs)
            self.collected = ''

    def handle_data(self, data):
        if self.collecting:
            self.collected += data


def UnpackCmd(cmdString, *args):
    cmdDict = args[0][0]  # I don't know why this second level of indexing is required
    cmdArgs = list();
    cmdPieces = cmdString.split(',')
    for (i,piece) in enumerate(cmdPieces):
        piece = piece.replace('\'','')
        piece = piece.replace('\\n','')
        piece = piece.replace('\\','')
        piece = piece.strip()
        if i==0:
            cmdName = piece
        else:
            if len(piece) > 0:
                cmdArgs.append(piece)
    cmdDict[cmdName] = cmdArgs

def AssessCSC(cscDir):
    f = open(cscDir, 'r')
    htmlData=str(f.readlines())
    f.close()

    cmdDict = {}
    parser = TsHTMLParser(UnpackCmd, cmdDict)
    parser.feed(htmlData)

    try:
        cmdDict.pop('Command AliasParameter') # remove useless header line
    except KeyError:
        pass
    
    minArgs = 999
    maxArgs = 0
    
    for c in cmdDict:
        cmdArgs = cmdDict[c]
        lenArgs = len(cmdArgs)
        minArgs = min(minArgs, lenArgs)
        maxArgs = max(maxArgs, lenArgs)
        
    print(cscDir, len(cmdDict), minArgs, maxArgs)

def AssessCSCset(rootDir):

    cmdRe = re.compile('.*Commands.html')
    
    for p in os.walk(rootDir):
        pfiles = p[2]
        if len(pfiles) > 0:
            for pf in pfiles:
                if cmdRe.match(pf):
                    AssessCSC(os.path.join(p[0],pf))

    
