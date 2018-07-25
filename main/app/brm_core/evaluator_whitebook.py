import theano
import theano.tensor as T
import xlrd
import re
import numpy as np
from theano.tensor import _shared
from numpy import array
import time
from RuleEvaluator import RuleEvaluator


file_locParams="C:\\Users\\ark0006\\Documents\\matrixOfParams.xlsx"
file_locRules="C:\\Users\\ark0006\\Documents\\BRMRules.xlsx"


_funct_dict = {'check_first_2_characters_of': 'vfind', "start_with":'vstart_with',  "Sum_of": 'sum'  }
_constant_dict = {'Y': 1, 'N': 0}
#def boolean_f(x):
#    return np.logical_and(x)
_boolean_operations_dict = {'STCC,Position':'NOT'} #' np.logical_and, np.logical_or, np.logical_xor 



def conv_rule1(val):
    match = re.search(r'(?<=sum\()\w+', val)
    if( not match ): raise Exception( 'function Sum_of must have at least 1 argument. Error in: ' + str )
    while match : 
        print(match)
        arg = match.group(0)
        val = val.replace('sum(' + arg + ')', '(' + arg + ').sum()')
        match = re.search(r'(?<=sum\()\w+', val)
    return val

# find any occurance of elements from search_list in string in position 0
def find(string): 
    ret = False
    # defind arg1 for function find as global variable
    arg1 = ('48', '49') 
    for arg in arg1:
       if( string.find(arg) == 0 ): 
           ret = True
           break
    return ret

def starts_with(string, arg):
    return (string.startswith(arg))

vfind = np.vectorize(find)
vstarts_with = np.vectorize(starts_with)
                           

# test vfind 
print(vfind(['48werw','46sffsdf', '45sffsdf', '49gdf', '48sds']))
# test vstart_with
print(vstarts_with(['48werw','46sffsdf', '45sffsdf', '49gdf', '48sds'],'48')) 


# special dictionary which say how convert written  functions to python notations
conv_rule_dict = {'Sum_of':  conv_rule1}

def conertToInt(s):
    ret = 0
    # get from  dict fro mmost common constants
    if(s in _constant_dict):
       ret = _constant_dict[s]
    # generate hash code
    else:
       ret = abs(hash(s)) % (10 ** 8)
    return ret




# Replace constant by integer's hash codes in string
def constantReplacer(val):
    match = re.search(r'\'(.*)\'', val)
    if( not match ): raise Exception( 'Constants mus be in one quotes like this \'Y\' or \'N\'. Error in:  ' + val )
    const =  match.group(1)
    hashcode = str(conertToInt(const))
    ret = val.replace('\'' + const + '\'' , hashcode )
    return ret


def do_rule_translation(rule, val):
     ret = val.replace( rule, _funct_dict[rule] )
     if( rule in conv_rule_dict ):
       ret = conv_rule_dict[rule](ret)
     return ret

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def find_operand(rule,operands):
    ret = ''
    for x in operands:
        if ( x in rule ): 
            ret = x
            break
    return ret

    
    # none operand default assumtion:  if no operand found consider this rule exceptional and use evaluate it as it is
    #  after compare this function with 0 
    return ret
#Populate all possible tupil of args for rule
def populate_rule_args(rule,all_params):
    args = []
    for arg in all_params:
        if( rule.find(arg) >=0 ): args.append(arg)
    if( not args ): raise Exception( 'Rule: "' +  rule+ '"  must have at least one argument. To fix it define argument in first row of spreadsheet ')
    return args


def loadMatrixFromExcellAsConstants(file_loc):
    wkb=xlrd.open_workbook(file_loc)
    sheet=wkb.sheet_by_index(0)
    _matrix=[]
    for col in range (sheet.ncols):
            _row = []
            for row in range (sheet.nrows):
                 val = sheet.cell_value(row,col)
                 if( col > 0): #exception case: read first column as it is without hash conversion 
                    if(not( type(val) is float or type(val) is int ) ): val = conertToInt(val)
                 _row.append(val)
            _matrix.append(_row)
    return _matrix

def loadMatrixFromExcellAsRules(file_loc):
    wkb=xlrd.open_workbook(file_loc)
    sheet=wkb.sheet_by_index(0)
    parameters_row = 0
    _matrix=[]
    for row in range (sheet.nrows):
    
            _row = []
            for col in range (sheet.ncols):
                 val = sheet.cell_value(row,col)
              
                 if( not val ): # Empty cell
                        _row.append('None') 
                        continue
                 if( row == parameters_row): # read first row and consider it as header of parameters
                    params = val.split(',')
                    _row.append(params)
                 else:
                     for rule in _funct_dict: 
                         if (  val.find(rule) >= 0 ):
                             val = do_rule_translation( rule, val ) # this word is rule function translate it
                        
                     if( val.find('\'') >=0 ): val = constantReplacer(val)
                     _row.append(val)
            _matrix.append(_row)
    return _matrix

# Algorithm of  rules conversion
# check if the rule has any constants (embedded in '') if yes convert constant to integer hashcode
# check if the rule has function  which required some preprocessing
# for example check_first_2_characters_of(...) . If it has fire rule preprocessor to convert it to vfind(...)
# This rule requiered translation and  data preparation before firing it 
# both sides left and right must be numeric


# create matrix of rules
rules_mtrx = loadMatrixFromExcellAsRules(file_locRules)
print('Matrix of rules:')
print('##########################################################################################################################')
print(rules_mtrx)
# create matrix of constants
#const_mtrx = loadMatrixFromExcellAsConstants(file_locConstants)
# create matrix of parameters
param_mtrx = loadMatrixFromExcellAsConstants(file_locParams)
rows,cols = 50,1

print('Matrix of parameters:')
print('##########################################################################################################################')
print(param_mtrx)
eval_rules_dict = {}
rules_immediate_eval_dict = {}

def vector_to_matrix(v):
    ret = []
    for r in v: ret.append([r]) 
    return ret


# define all parameters:
STCC      = param_mtrx [0][0:rows]
Position_  = np.random.randint(50,size=(rows,cols))
Weight_    = vector_to_matrix(param_mtrx [1][0:rows])
Length_    = vector_to_matrix(param_mtrx [2][0:rows])
CushionDB_ = vector_to_matrix(param_mtrx [3][0:rows])
Hazard_ =    vector_to_matrix(param_mtrx [4][0:rows])

# Evaluate ( convert the rules from strings to real functions)

start_time = time.time()
for j in range(len(rules_mtrx[0])):
    _rules = []
    for i in range(1,len(rules_mtrx)):
        all_params = rules_mtrx[0][j]
        rule = rules_mtrx[i][j]
        if( not rule or rule == 'None' ): continue
        operand = find_operand(rule,['<','>','>=','<=','=']) # move to translate rule
        if( not operand ):
            # add no parameters rules to immediate evaluation rule's dictionary by key where key is point to spreadsheet column
            rules_immediate_eval_dict[','.join(all_params)] =  rule
        else: 
            params = populate_rule_args(rule,all_params)
            # add Rule function , rule's paramters pair to tupil
            if( len(params) == 1 ) :
                rule_params = (globals()[params[0]+'_'])
            else:
                rule_params = eval('_,'.join(params) + '_')
            
            pair = rule.split(operand)
            rule_left = pair[0]
            rule_right= pair[1]
            _rules.append( (RuleEvaluator(rule_left,operand,rule_right,params,rows,cols), rule_params) )

    if( len(_rules)>0 ):
       eval_rules_dict[','.join(all_params)] = _rules
print("Evaluation time: --- %s seconds ---" % (time.time() - start_time))
print('Dictionary of evaluated rules, where is the key is parameters used in rules:')
print('##########################################################################################################################')
print(eval_rules_dict)
print('Dictionary of not evaluated rules (rules without parameters):')
print('##########################################################################################################################')
print(rules_immediate_eval_dict)

ones = np.ones((rows,cols), dtype=int)
STCC =  param_mtrx [0][0:rows]


print('STCC: '  )
print( len(STCC[0]))
print(STCC)
print('Position:')
print(Position_)

print('check_first_2_characters_of(STCC)')
_r = eval(rules_immediate_eval_dict['STCC,Position'])
stcc = []
for r in _r: stcc.append([r])
print(stcc)


position_rule = (eval_rules_dict['STCC,Position'][0][0])
position_rule_param = (eval_rules_dict['STCC,Position'][0][1])
print (" eval_rules_dict['STCC,Position'][0][1]: "  )
print(position_rule_param)
#position_rule.show_log = False
position_result = position_rule.evaluate(position_rule_param)
print('Position < 5')
print( position_result )

result =  position_result * stcc 
print('BRM result:')
print('##########################################################################################################################')
print(result)

# formalise previouse hardcoded code to dynamic rule evaluation



def evaluate_none_arg_rules(key):
    rule_failed = 0
    ret = []
    _r = eval(rules_immediate_eval_dict[key])
      # convert result to array of arrays
    for r in _r: 
         # do error log printing
         if( r == 0 ): rule_failed += 1
         ret.append([r])
    if(rule_failed > 0 ): print('Rule: ' + rules_immediate_eval_dict[key] + ' was failed ' + str(rule_failed) + ' time(s)') 
    return ret





start_time = time.time()
# loop over the all rules in evuluated rules dictionary
ret = 0.
normalizer = 0
for key,rules in  eval_rules_dict.items():
    _ret = 1
    for rule_tupil in rules:
        #get value from rule tupil
        rule = rule_tupil[0]
        rule_params = rule_tupil[1]
        # all arguments are global and must end with '_' because there is symbolic arg with the same name
        if( not isinstance(rule_params, (tuple)) ): # if not list
                rule_ret = rule.evaluate(rule_params)
        else:
                rule_ret = rule.evaluate(*rule_params)
        

        #_param_list = '_,'.join(rule_param) + '_'
        #param_list = eval('(' + _param_list + ')') # create tupil

        _ret = _ret * rule_ret
    if( key in rules_immediate_eval_dict ) :  
        _ret = _ret * evaluate_none_arg_rules(key)
    if( key in _boolean_operations_dict ): 
        #call numpy boolean functions for whole column _ret = np.logical_not(_ret)
        if(_boolean_operations_dict[key] == 'NOT' ):
           _ret = np.logical_not(_ret)
        elif(_boolean_operations_dict[key] == 'XOR' ):
            _ret = np.logical_not(_ret,_ret)
    normalizer += 1
    ret  +=  _ret*1 
ret = ret/normalizer
print("Execution time: --- %s seconds ---" % (time.time() - start_time))
print('BRM result:')
print('##########################################################################################################################')
print(ret)

