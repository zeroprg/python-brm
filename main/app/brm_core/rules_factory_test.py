import theano
import theano.tensor as T
import xlrd
import re
import numpy as np
from theano.tensor import _shared
from numpy import array
import time
from RulesFactory import RulesFactory


rows,cols = 50,1
file_locParams="matrixOfParams.xlsx"
file_locRules="BRMRulesInColumns.xlsx"
#file_locRules="..\BRMRulesInRows.xlsx"

param_mtrx = RulesFactory.loadMatrixFromExcellAsConstants(file_locParams)
RulesFactory.setParameters(param_mtrx,rows)

rf = RulesFactory(file_locRules,rows,cols)
rf.show_log = False
ret = rf.fireBRM()
print('BRM result:')
print('##########################################################################################################################')
print(ret)
