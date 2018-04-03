import theano
import theano.tensor as T
import xlrd
import re
import numpy as np

from RuleEvaluator import RuleEvaluator


file_locParams="C:\\Users\\ark0006\\Documents\\matrixOfParams.xlsx"
file_locConstants="C:\\Users\\ark0006\\Documents\\matrixOfConstants.xlsx"
file_locRules="C:\\Users\\ark0006\\Documents\\BRMRules.xlsx"


_funct_dict = {'check_first_2_characters_of': 'vfind', "Sum_of": 'sum'  }


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
    ret = 0
    for arg in arg1:
       if( string.find(arg) == 0 ): 
           ret = 1
           break
    return ret

# defind arg1 for function find as global variable
arg1 = ('48', '49') 
vfind = np.vectorize(find)

# test vfind 
print(vfind(['48werw','46sffsdf', '45sffsdf', '49gdf', '48sds']))



# special dictionary which say how convert written  functions to python notations
conv_rule_dict = {'Sum_of':  conv_rule1}

def conertToInt(s):
     return abs(hash(s)) % (10 ** 8)




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


def do_rule_leftshift(rule,operands):
    ret = (rule,)
    for x in operands:
        if ( x in rule ):
    # return tupil of rule and operand 
            ret = (rule.replace(x,'-') , x)
            break
    
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
rows,cols = 10,1

print('Matrix of parameters:')
print('##########################################################################################################################')
print(param_mtrx)
eval_rules_dict = {}
rules_immediate_eval_dict = {}

# Evaluate ( convert the rules from strings to real functions)

for j in range(len(rules_mtrx[0])):
    _rules = []
    for i in range(1,len(rules_mtrx)):
        all_params = rules_mtrx[0][j]
        rule = rules_mtrx[i][j]
        if( not rule or rule == 'None' ): continue
        rule_info = do_rule_leftshift(rule,['<','>','>=','<=','='])
        if( len(rule_info) == 1 ):
            # add no parameters rules to immediate evaluation rule's dictionary by key where key is point to spreadsheet column
            rules_immediate_eval_dict[','.join(all_params)] = rule_info[0]
        else: 
            params = populate_rule_args(rule,all_params)
            # add Rule function , rule's paramters pair to tupil
            _rules.append( (RuleEvaluator(rule_info[0],rule_info[1],params,rows,cols), params) )
    if( len(_rules)>0 ):
       eval_rules_dict[','.join(all_params)] = _rules

print('Dictionary of evaluated rules, where is the key is parameters used in rules:')
print('##########################################################################################################################')
print(eval_rules_dict)
print('Dictionary of not evaluated rules (rules without parameters):')
print('##########################################################################################################################')
print(rules_immediate_eval_dict)

STCC = param_mtrx[0]
Position =  np.random.randint(50,size=(rows,cols))
print('STCC: ' )
print( len(STCC))
print(STCC)
print('Position:')
print(Position)

result =  (eval_rules_dict['STCC,Position'][0][0]).evaluate(Position) * eval(rules_immediate_eval_dict['STCC,Position']) *
print('BRM result:')
print('##########################################################################################################################')
print(result)

