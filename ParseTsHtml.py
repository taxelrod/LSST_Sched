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
#    print('args: ', args)
    cmdDict = args[0][0]  # I don't know why this second level of indexing is required
    cmdArgs = list();
    cmdPieces = cmdString.split(',')
    for (i,piece) in enumerate(cmdPieces):
        piece = piece.replace('\'','')
        piece = piece.replace('\\n','')
        piece = piece.replace('\\','')
        piece = piece.strip()
#        print(piece)
        if i==0:
            cmdName = piece
        else:
            if len(piece) > 0:
                cmdArgs.append(piece)
#    print(type(cmdDict),cmdName, cmdArgs)
    cmdDict[cmdName] = cmdArgs
#    print(cmdPieces)

def AssessCSC(cscDir):
    f = open(cscDir, 'r')
    htmlData=str(f.readlines())
    f.close()

    cmdDict = {}
    parser = TsHTMLParser(UnpackCmd, cmdDict)
    parser.feed(htmlData)

    print(cscDir, len(cmdDict))

def AssessCSCset(rootDir):

    cmdRe = re.compile('.*Commands.html')
    
    for p in os.walk(rootDir):
        pfiles = p[2]
        if len(pfiles) > 0:
            for pf in pfiles:
                if cmdRe.match(pf):
                    AssessCSC(os.path.join(p[0],pf))

    
