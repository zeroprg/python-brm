import theano, numpy
import theano.tensor as T
import xlrd
import re

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
def find(string,search_list): 
    return any( x in string for x in search_list) and string.find(x) == 0
 
vfind = np.vectorize(find)



# special dictionary which say how convert written  functions to python notations
conv_rule_dict = {'Sum_of':  conv_rule1}

def conertToInt(s):
     return abs(hash(s)) % (10 ** 8)




# Replace constant by integer's hash codes in string
def constantReplacer(val):
    match = re.search(r'\'(.*)\'', val)
    if( not match ): raise Exception( 'Constants mus be in one quotes like this \'Y\' or \'N\'. Error in:  ' + str )
    const =  match.group(1)
    hashcode = str(conertToInt(const))
    ret = val.replace('\'' + const + '\'' , hashcode )
    return ret


def do_rule_translation(rule, val):
     ret = val.replace( rule, _funct_dict[rule] )
     if( rule in conv_rule_dict ):
       ret = conv_rule_dict[rule](ret)
     return ret




def loadMatrixFromExcellAsConstants(file_loc):
    wkb=xlrd.open_workbook(file_loc)
    sheet=wkb.sheet_by_index(0)
    _matrix=[]
    for row in range (sheet.nrows):
            _row = []
            for col in range (sheet.ncols):
                 val = sheet.cell_value(row,col)
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
        if( row > parameters_row):
            _row = []
            for col in range (sheet.ncols):
                 val = sheet.cell_value(row,col)
                 if( not val ): continue
                 
                 for rule in _funct_dict: 
                     if (  val.find(rule) >= 0 ):
                         val = do_rule_translation( rule, val ) # this word is rule function translate it
                        
                 if( val.find('\'') >=0 ): val = constantReplacer(val)
                 _row.append(val)
            _matrix.append(_row)
    return _matrix

# Algorithm of  rules conversion
# check if the rule has any constants (embedded in '') if yes convert constant to integer
# check if the rule has function  which required some preprocessing
# for example check_first_2_characters_of  = 'Y' . 
# This rule requiered translation and  data preparation before firing it 
# both sides left and right must be numeric


# create matrix of rules
rules_mtrx = loadMatrixFromExcellAsRules(file_locRules)
print('Matrix of rules')
print(rules_mtrx)
# create matrix of constants
const_mtrx = loadMatrixFromExcellAsConstants(file_locConstants)
# create matrix of parameters
param_mtrx = loadMatrixFromExcellAsConstants(file_locParams)
