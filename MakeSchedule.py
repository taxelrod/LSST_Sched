"""
Input a milestone table, and a CSC table.
Link the milestone CSC requirementsto the CSC table to 
calculate an order for CSC development, and resources
as a function of time.
"""

from enum import Enum
from collections import OrderedDict
import datetime as dt
import pandas  as pd
import numpy as np
import plotly
import plotly.figure_factory as ff

class DevelState(Enum):
    NotStarted = 0
    Skeleton = 1
    Algorithm = 2
    Verified = 3

class Milestone:
    def readIn(self,fileName):
        self.df = pd.read_csv(fileName, sep = ',', dtype = str)
        self.df['Completion Date(dt)']=dt.date(2030,1,1)
        for i in range(len(self.df)):
            row = self.df.iloc[i]
            try:
                dateString = row['Completion Date'].strip()
            except:
                print('Warning on missing date for: ', row['P6 Task'])
            try:
                d = dt.datetime.strptime(dateString, '%d-%b-%y')
                self.df.loc[i,'Completion Date(dt)'] = d.date()
                # NOTE: the above awkwardness is required to avoid pandas chained indexing issue
            except:
                print('Warning on date format for: ', row['P6 Task'], row['Completion Date'])
        

class CSC:
    def __init__(self, name, percentComplete=0, costSkeleton=0, costAlgorithm=0, costVerified=0):
        self.name = name
        self.cost = np.zeros(4)
        self.date = np.zeros(4, dtype=dt.date)

        self.complete = percentComplete
        
        self.cost[DevelState.NotStarted.value] = 0
        self.date[DevelState.NotStarted.value] = dt.date(2021,1,1)
        self.cost[DevelState.Skeleton.value] = costSkeleton
        self.date[DevelState.Skeleton.value] = dt.date(2021,1,1)
        self.cost[DevelState.Algorithm.value] = costAlgorithm
        self.date[DevelState.Algorithm.value] = dt.date(2021,1,1)
        self.cost[DevelState.Verified.value] = costVerified
        self.date[DevelState.Verified.value] = dt.date(2021,1,1)
        

class CSCdict:
    
    def __init__(self):
        self.dict = {}
        
    def readIn(self,fileName):
        self.df = pd.read_csv(fileName, sep=',')

        for i in range(len(self.df)):
            row = self.df.iloc[i]

            cscName = row['CSC Name']
            
            if np.isnan(row['percentComplete']):
                percentComplete = 0
            else:
                percentComplete = row['percentComplete']

            if np.isnan(row['costSkeleton']):
                costSkeleton = 0
            else:
                costSkeleton = row['costSkeleton']
            if np.isnan(row['costAlgorithm']):
                costAlgorithm = 0
            else:
                costAlgorithm = row['costAlgorithm']
            if np.isnan(row['costVerified']):
                costVerified = 0
            else:
                costVerified = row['costVerified']
            # dates = 4:6

            self.dict[cscName] = CSC(cscName, percentComplete, costSkeleton, costAlgorithm, costVerified)

    def makeDF(self):
        nrows = len(self.dict)
        names = np.zeros((nrows), dtype=object)
        complete = np.zeros((nrows), dtype=object)
        color = np.zeros((nrows), dtype=object)
        dateSkeleton = np.zeros((nrows), dtype=dt.date)
        dateAlgorithm = np.zeros((nrows), dtype=dt.date)
        dateVerified = np.zeros((nrows), dtype=dt.date)
        i = 0
        for k in iter(self.dict):
            csc = self.dict[k]
            names[i] = k
            complete[i] = csc.complete
            if complete[i] >= 70:
                color[i] = 'green'
            elif complete[i] >= 30:
                color[i] = 'yellow'
            else:
                color[i] = 'red'
            dateSkeleton[i] = csc.date[DevelState.Skeleton.value]
            dateAlgorithm[i] = csc.date[DevelState.Algorithm.value]
            dateVerified[i] = csc.date[DevelState.Verified.value]
            i += 1
        d = OrderedDict()
        d['CSCname'] = names
        d['color'] = color
        d['dateSkeleton'] = dateSkeleton
        d['dateAlgorithm'] =  dateAlgorithm
        d['dateVerified'] = dateVerified
        self.df = pd.DataFrame(d)

        return self.df

    def makeGanttOrig(self, cutStart=None, cutEnd=None):
        self.ganttDf = self.df.sort_values('dateSkeleton').rename(index=str,columns={"CSCname":"Task", "dateSkeleton":"Start", "dateVerified":"Finish"})

        colors = {'red': 'rgb(220, 0, 0)',
          'yellow': (1, 0.9, 0.16),
          'green': 'rgb(0, 255, 100)'}

        fig = ff.create_gantt(self.ganttDf,index_col='color',height=1200,width=1800,colors=colors,showgrid_x=True, showgrid_y=True)
        plotly.offline.plot(fig, filename='CSC_gantt.html')
        
    def makeGantt(self, cutStart=None, cutEnd=None):

        self.ganttDF = pd.DataFrame(columns=['Task', 'Start', 'Finish', 'color'])

        dayGap = 5
        
        for i in range(len(self.df)):
            row = self.df.iloc[i]
            self.ganttDF = self.ganttDF.append({'Task':row['CSCname'], 'Start':row['dateSkeleton'], 'Finish':row['dateAlgorithm'], 'color':row['color']},ignore_index=True)
            self.ganttDF = self.ganttDF.append({'Task':row['CSCname'], 'Start':row['dateAlgorithm']+dt.timedelta(dayGap), 'Finish':max(row['dateVerified'],row['dateAlgorithm']+dt.timedelta(2*dayGap)) , 'color':row['color']},ignore_index=True)
            
        self.ganttDF = self.ganttDF.sort_values('Task')

        colors = {'red': 'rgb(220, 0, 0)',
          'yellow': (1, 0.9, 0.16),
          'green': 'rgb(0, 255, 100)'}

        fig = ff.create_gantt(self.ganttDF,index_col='color',title='CSC Capabilities Needed to Meet AIV Requirements',height=1200,width=1800,colors=colors,showgrid_x=True, showgrid_y=True, group_tasks=True)
        plotly.offline.plot(fig, filename='CSC_gantt.html')
        
    def print(self):
        for k in iter(self.dict):
            csc = self.dict[k]
            print(k, end='\t\t')
            for i in range(len(csc.date)):
                print(csc.date[i], end='\t')
            print('')

"""
Iterate over milestones:
For each CSC needed by the milestone:
"""

def calcCSCReq(milestones,CSCdict):

    for i in range(len(milestones.df)):
        row = milestones.df.iloc[i]
        try:
            np.isnan(row['CSC List'])
        except TypeError:
            CSClist = row['CSC List'].split(',')
            for cscSpec in CSClist:
                cscSplit = cscSpec.split(':')
                if len(cscSplit) >= 2:
                    cscName = cscSplit[0]
                    cscState = DevelState(int(cscSplit[1]))
                else:
                    cscName = cscSplit[0]
                    cscState = DevelState.Verified

                if cscName in CSCdict.dict:
                    csc = CSCdict.dict[cscName]
                    cscDate = csc.date[cscState.value] # this is a datetime.date
                    msDate = row['Completion Date(dt)'] # this is a datetime.date
                    if msDate < cscDate:
                        csc.date[cscState.value] = msDate
                    for i in np.arange(len(csc.date)-2, -1, -1):
                        csc.date[i] = min(csc.date[i], csc.date[i+1])
                    
                else:
                    print('KeyError for %s' % cscName)
                
        

