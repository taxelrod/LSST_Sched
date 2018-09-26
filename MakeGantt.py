#!/usr/bin/env python

import pandas as pd
import MakeSchedule as ms
from importlib import reload

miles=ms.Milestone()
miles.readIn('MasterTasks.csv')
cscd=ms.CSCdict()
cscd.readIn('../Arch/CSClist.txt')
ms.calcCSCReq(miles, cscd)
cscd.makeDF()
cscd.makeGantt()
