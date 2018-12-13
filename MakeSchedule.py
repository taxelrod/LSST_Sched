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
import matplotlib.pyplot as plt

debug = False

class DevelState(Enum):
    NotStarted = 0
    Skeleton = 1
    Algorithm = 2
    Verified = 3

class Milestone:
    def readIn(self,fileName):
        self.df = pd.read_csv(fileName, sep = ',', comment = '#', dtype = str)
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
        self.wbs = np.zeros(4, dtype=object)

        self.complete = percentComplete
        
        self.cost[DevelState.NotStarted.value] = 0
        self.date[DevelState.NotStarted.value] = dt.date(2021,1,1)
        self.cost[DevelState.Skeleton.value] = costSkeleton
        self.date[DevelState.Skeleton.value] = dt.date(2021,1,1)
        self.cost[DevelState.Algorithm.value] = costAlgorithm
        self.date[DevelState.Algorithm.value] = dt.date(2021,1,1)
        self.cost[DevelState.Verified.value] = costVerified
        self.date[DevelState.Verified.value] = dt.date(2021,1,1)
        
"""
Per FE:

7.5 story points / wk / developer including overhead

Small task:  2 weeks, 15 pts
Med       :  6 weeks, 45 pts
Large     :  3 months, 90 pts

Her guess at hexapod CSC:  Med

Derating factor DM productivity/TSS:  2?

"""
class CSCdict:

    defaultCostSkeleton = 7
    defaultCostAlgorithm = 45
    defaultCostVerified = 45

    def __init__(self):
        self.dict = {}
        
    def readIn(self,fileName):
        self.df = pd.read_csv(fileName, sep=',', comment='#')

        for i in range(len(self.df)):
            row = self.df.iloc[i]

            cscName = row['CSC Name']
            
            if np.isnan(row['percentComplete']):
                percentComplete = 0
            else:
                percentComplete = row['percentComplete']

            if np.isnan(row['costSkeleton']):
                costSkeleton = self.defaultCostSkeleton
            else:
                costSkeleton = row['costSkeleton']
            if np.isnan(row['costAlgorithm']):
                costAlgorithm = self.defaultCostAlgorithm
            else:
                costAlgorithm = row['costAlgorithm']
            if np.isnan(row['costVerified']):
                costVerified = self.defaultCostVerified
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
        wbsSkeleton = np.zeros((nrows), dtype=object)
        wbsAlgorithm = np.zeros((nrows), dtype=object)
        wbsVerified = np.zeros((nrows), dtype=object)
        costTot = np.zeros((nrows))
        percentComplete = np.zeros((nrows))

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
            wbsSkeleton[i] = csc.wbs[DevelState.Skeleton.value]
            wbsAlgorithm[i] = csc.wbs[DevelState.Algorithm.value]
            wbsVerified[i] = csc.wbs[DevelState.Verified.value]
            costTot[i] = csc.cost[DevelState.Skeleton.value] + csc.cost[DevelState.Algorithm.value] + csc.cost[DevelState.Verified.value]
            percentComplete[i] = csc.complete
            i += 1
        d = OrderedDict()
        d['CSCname'] = names
        d['color'] = color
        d['story points'] = costTot
        d['% complete'] = percentComplete
        d['dateSkeleton'] = dateSkeleton
        d['dateAlgorithm'] =  dateAlgorithm
        d['dateVerified'] = dateVerified
        d['wbsSkeleton'] = wbsSkeleton
        d['wbsAlgorithm'] =  wbsAlgorithm
        d['wbsVerified'] = wbsVerified
        self.df = pd.DataFrame(d)

        return self.df

    def writeCSV(self, fileName):
        f = open(fileName, 'w')
        colsToWrite=['CSCname', 'story points', '% complete', 'dateSkeleton', 'dateAlgorithm', 'dateVerified', 'wbsSkeleton', 'wbsAlgorithm', 'wbsVerified']
        f.write(self.df.sort_values('dateAlgorithm').to_csv(columns=colsToWrite))
        f.close()
        
    def makeCostProfile(self):

        nCostPoints = 3*len(self.dict)
        times = np.zeros((nCostPoints), dtype=object)
        costs = np.zeros((nCostPoints), dtype=object)
        
        i = 0
        for k in iter(self.dict):
            csc = self.dict[k]
            times[i] = csc.date[DevelState.Skeleton.value]
            times[i+1] = csc.date[DevelState.Algorithm.value]
            times[i+2] = csc.date[DevelState.Verified.value]
            costs[i] = csc.cost[DevelState.Skeleton.value]
            costs[i+1] = csc.cost[DevelState.Algorithm.value]
            costs[i+2] = csc.cost[DevelState.Verified.value]

            if csc.complete > 0:
                if debug:
                    print(csc.complete, costs[i], costs[i+1], costs[i+2], end=' ')
                fracCompl = csc.complete/100.0
                costTot = costs[i] + costs[i+1] + costs[i+2]
                costDone = fracCompl*costTot
                costSkel = costs[i]
                costAlg = costs[i+1]
                costVer = costs[i+2]
                costs[i] = max(0, costSkel-costDone) 
                costs[i+1] = max(0, costSkel+costAlg-costs[i]-costDone) 
                costs[i+2] = max(0, costSkel+costAlg+costVer-costs[i+1]-costDone)
                if debug:
                    print(fracCompl, costDone, costs[i], costs[i+1], costs[i+2], costTot-(costDone+costs[i]+costs[i+1]+costs[i+2]))
            
            i += 3

        ix = np.argsort(times)
        timesSorted = times[ix]
        costsSorted = costs[ix]

        costsCumulative = np.zeros_like(costsSorted)
        costsCumulative[0] = costsSorted[0]
        for i in range(1, len(costsCumulative)):
            costsCumulative[i] = costsCumulative[i-1] + costsSorted[i]

        return timesSorted, costsCumulative
        
        
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
                    msWBS = row['WBS Code']
                    if msDate < cscDate:
                        csc.date[cscState.value] = msDate
                        csc.wbs[cscState.value] = msWBS
                    for i in np.arange(len(csc.date)-2, -1, -1):
                        csc.date[i] = min(csc.date[i], csc.date[i+1])
                    
                else:
                    print('KeyError for %s' % cscName)
                
        

