import theano
import theano.tensor as T
import xlrd
import re
import numpy as np
from theano.tensor import _shared
from numpy import array
import time

from RulesFactory import RulesFactory

def vector_to_matrix(v):
    ret = []
    for r in v: ret.append([r]) 
    return ret

rows,cols = 50,1
file_locParams="C:\\Users\\ark0006\\Documents\\matrixOfParams.xlsx"
file_locRules="C:\\Users\\ark0006\\Documents\\BRMRules.xlsx"

param_mtrx = RulesFactory.loadMatrixFromExcellAsConstants(file_locParams)

# define all parameters:
STCC      = param_mtrx [0][0:rows]
Position_  = vector_to_matrix(np.arange(rows))
Weight_    = vector_to_matrix(param_mtrx [1][0:rows])
Length_    = vector_to_matrix(param_mtrx [2][0:rows])
CushionDB_ = vector_to_matrix(param_mtrx [3][0:rows])
Hazard_ =    vector_to_matrix(param_mtrx [4][0:rows])


rf = RulesFactory(file_locRules,rows,cols)
rf.show_log = False
ret = rf.fireBRM()
print('BRM result:')
print('##########################################################################################################################')
print(ret)
