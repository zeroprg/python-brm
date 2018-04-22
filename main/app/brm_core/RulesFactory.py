import theano
import theano.tensor as T
import xlrd
import re
import numpy as np
from theano.tensor import _shared
from numpy import array
import time
import json
from RuleEvaluator import RuleEvaluator




# Class itself
#================================================================================================

class RulesFactory(object):
    """A RulesFactory evaluate symbolic rule . RuleEvaluator have the
    following properties:

    Attributes:
        python_code_rule: A string of the Python code representing formula.
        operand: A simple operand '<', '>'. '-'.
        args: list of symbolic variables (string), init. inside by Theano library
        
    """


    # Global variables and rules defined as  functions 
#================================================================================================
    #set true if parameters already loaded
    is_params_loaded = False

    _funct_dict = {'check_first_2_characters_of': 'vfind', "Sum_of": 'sum'  }
    _constant_dict = {'Y': 1, 'N': 0}
    _boolean_operations_dict = {'STCC,Position':'NOT'} #' np.logical_and, np.logical_or, np.logical_xor 



    def conv_rule1(val):
        match = re.search(r'(?<=sum\()\w+', val)
        if( not match ): raise Exception( 'function Sum_of must have at least 1 argument. Error in: ' + str )
        while match : 
            arg = match.group(0)
            val = val.replace('sum(' + arg + ')', '(' + arg + ').sum()')
            match = re.search(r'(?<=sum\()\w+', val)
        return val

# find any occurance of elements from search_list in string in position 0
    def find(string): 
        ret = False
        for arg in ('48', '49'):
           if( string.find(arg) == 0 ): 
               ret = True
               break
        return ret

# define function to find as global variable
    vfind = np.vectorize(find)

# test vfind 
#print(vfind(['48werw','46sffsdf', '45sffsdf', '49gdf', '48sds']))

# special dictionary which converts written  functions to python notations
    conv_rule_dict = {'Sum_of':  conv_rule1}

    def vector_to_matrix(v):
        ret = []
        for r in v: ret.append([r]) 
        return ret


    def __init__(self,  file_locRules , rows, cols):
        """Return a Customer object whose name is *name* and starting
        balance is *balance*."""
        self.show_log = False
        self.rows = rows
        self.cols = cols
        self.eval_rules_dict = {}
        self.rules_immediate_eval_dict = {}
        #self.rules_mtrx = self.loadMatrixFromExcellAsRules(file_locRules)
        self.rules_mtrx =  self.loadFromExcellAsRules_groupedByRows(file_locRules)
        if( self.show_log ):
            print('Matrix of rules:')
            print('##########################################################################################################################')
            print(self.rules_mtrx)

        #self.EvaluateAllRulesByColumns()
        self.EvaluateAllRulesByRows()
        if( self.show_log ):
            print('Dictionary of evaluated rules:')
            print('##########################################################################################################################')
            print(self.eval_rules_dict)


        # define all parameters:
        #STCC       = param_mtrx [0][0:rows]
        #Position_  = vector_to_matrix(np.arange(rows))
        #Weight_    = vector_to_matrix(param_mtrx [1][0:rows])
        #Length_    = vector_to_matrix(param_mtrx [2][0:rows])
        #CushionDB_ = vector_to_matrix(param_mtrx [3][0:rows])
        #Hazard_    = vector_to_matrix(param_mtrx [4][0:rows])
    def loadParametersFromJSON(json_str):        
        data = json.loads(json_str)
        for key in data[0]:
            key_ = key
            if(not (key in ['STCC'])): key_ = key +'_'
            (globals()[key_]) = []
            temp = []
            for i in range(len(data)):
                val = data[i][key]
                if(not( key in ['STCC'])):
                    if(not( type(val) is float or type(val) is int ) ): val = RulesFactory.conertToInt(val)
                temp.append(val)
            if(not( key in ['STCC'])):
                (globals()[key_]) =  RulesFactory.vector_to_matrix(temp)
            else:
                (globals()[key_]) = temp
        RulesFactory.is_params_loaded = True
        return len(data)

    def conertToInt(s):
        ret = 0
        # get from  dict fro mmost common constants
        if(s in RulesFactory._constant_dict):
           ret = RulesFactory._constant_dict[s]
        # generate hash code
        else:
           ret = abs(hash(s)) % (10 ** 8)
        return ret
        
    
    # Replace constants by encoded integer use constant dictionary
    def constantReplacer(val):
        match = re.search(r'\'(.*)\'', val)
        if( not match ): raise Exception( 'Constants mus be in one quotes like this \'Y\' or \'N\'. Error in:  ' + val )
        const =  match.group(1)
        hashcode = str(conertToInt(const))
        ret = val.replace('\'' + const + '\'' , hashcode )
        return ret
    
    # Start point for translation rule from string to Python code
    def do_rule_translation(self,rule, val):
         ret = val.replace( rule, RulesFactory._funct_dict[rule] )
         if( rule in RulesFactory.conv_rule_dict ):
           ret = RulesFactory.conv_rule_dict[rule](ret)
         return ret
    
    def findWholeWord(w):
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
        
    
    def find_operand(self,rule,operands):
        ret = ''
        for x in operands:
            if ( x in rule ): 
                ret = x
                break
        return ret
    
    #Populate tuples of args for rule
    def populate_rule_args(self,rule,all_params):
        args = []
        for arg in all_params:
            if( rule.find(arg) >=0 ): args.append(arg)
        if( not args ): raise Exception( 'Rule: "' +  rule+ '"  must have at least one argument. To fix it define argument in first row of spreadsheet ')
        return args
    
    # This is static method used as helper to download parameters from spreadsheet for BRM evaluator. 
    # WARNING: Parameters must be initiated before any rules evaluations : (self.EvaluateAllRules())
    def loadMatrixFromExcellAsConstants(file_loc):
        wkb=xlrd.open_workbook(file_loc)
        sheet=wkb.sheet_by_index(0)
        _matrix=[]
        for col in range (sheet.ncols):
                _row = []
                for row in range (sheet.nrows):
                     val = sheet.cell_value(row,col)
                     if( col > 0): #exception case: read first column as it is without hash conversion 
                        if(not( type(val) is float or type(val) is int ) ): val = RulesFactory.conertToInt(val)
                     _row.append(val)
                _matrix.append(_row)
        return _matrix
    
    def loadMatrixFromExcellAsRules(self, file_loc):
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
                         for rule in RulesFactory._funct_dict: 
                             if (  val.find(rule) >= 0 ):
                                 val = self.do_rule_translation( rule, val ) # this word is rule function translate it
                            
                         if( val.find('\'') >=0 ): val = constantReplacer(val)
                         _row.append(val)
                _matrix.append(_row)
        return _matrix

    def loadFromExcellAsRules_groupedByRows(self, file_loc):
        wkb=xlrd.open_workbook(file_loc)
        sheet=wkb.sheet_by_index(0)
        parameters_row = 0
        _matrix=[]
        self.rule_names = []
        rule_key = 'None'
        for row in range (sheet.nrows):
                _row = []
                #Exclude first column and last column with ErrorMessage
                for col in range (sheet.ncols):
                     val = sheet.cell_value(row,col)
                     if( col == 0 and row == 0 ): continue
                     if( not val or  val.strip() == '' ): # Empty cell
                         _row.append('None') 
                         continue
                     if( col == 0 ): 
                         rule_key = val	
                         self.rule_names.append(val)
                         continue
                     if(row == parameters_row): # read first row and consider it as header of parameters
                         if( val == 'ErrorMessage'): 
                             self.error_message_col = col
                             self.error_message = {}
                             continue
                         params = val.split(',')
                         _row.append(params)
                     else:
                         if( col == self.error_message_col ):
                             self.error_message[rule_key] = val 
                             continue
                         for rule in RulesFactory._funct_dict: 
                             if (  val.find(rule) >= 0 ):
                                 val = self.do_rule_translation( rule, val ) # this word is rule function translate it
                            
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



    def EvaluateAllRulesByColumns(self):
        # Evaluate ( convert the rules from strings to real functions)
        start_time = time.time()
        for j in range(len(self.rules_mtrx[0])):
            _rules = []
            for i in range(1,len(self.rules_mtrx)):
                all_params = self.rules_mtrx[0][j]
                rule = self.rules_mtrx[i][j]
                if( not rule or rule == 'None' ): continue
                operand = self.find_operand(rule,['<','>','>=','<=','=']) # move to translate rule
                if( not operand ):
                    # add no parameters rules to immediate evaluation rule's dictionary by key where key is point to spreadsheet column
                    self.rules_immediate_eval_dict[','.join(all_params)] = rule
                else: 
                    params = self.populate_rule_args(rule,all_params)
                    # add Rule function , rule's paramters pair to tupil
                    if( len(params) == 1 ) :
                        rule_params =  (globals()[params[0]+'_'])
                    else:
                        rule_params = eval('_,'.join(params) + '_')
                    pair = rule.split(operand)
                    rule_left = pair[0]
                    rule_right= pair[1]
                    _rules.append( (RuleEvaluator(rule_left,operand,rule_right,params,self.rows,self.cols), rule_params) )
            if( len(_rules)>0 ):
               self.eval_rules_dict[','.join(all_params)] = _rules
        print("Evaluation time: --- %s seconds ---" % (time.time() - start_time))

    def EvaluateAllRulesByRows(self):
        # Evaluate ( convert the rules from strings to real functions)
        start_time = time.time()

        for i in range(1,len(self.rules_mtrx)):
            _rules = []
            for j in range(len(self.rules_mtrx[0])):
                all_params = self.rules_mtrx[0][j]
                rule = self.rules_mtrx[i][j]
                if( not rule or rule == 'None'): continue
                operand = self.find_operand(rule,['<','>','>=','<=','=']) # move to translate rule
                if( not operand and rule):
                    # add no parameters rules to immediate evaluation rule's dictionary by key where key is point to spreadsheet column
                    self.rules_immediate_eval_dict[self.rule_names[i-1]] = rule
                else: 
                    params = self.populate_rule_args(rule,all_params)
                    # add Rule function , rule's paramters pair to tupil
                    if( len(params) == 1 ) :
                        rule_params =  (globals()[params[0]+'_'])
                    else:
                        rule_params = eval('_,'.join(params) + '_')
                    pair = rule.split(operand)
                    rule_left = pair[0]
                    rule_right= pair[1]

                    _rules.append( (RuleEvaluator(rule_left,operand,rule_right,params,self.rows,self.cols), rule_params) )
            if( len(_rules)>0 ):
               self.eval_rules_dict[self.rule_names[i-1]] = _rules
        print("Evaluation time: --- %s seconds ---" % (time.time() - start_time))

    def log_error_message(self, key, ret):
        if not self.show_log : return ''
        postions = ''
        msg = ''
        i = 0
        if ret.any() ==  0 : 
            msg = key  + ': ' + self.error_message[key] + ' in positions: ' + postions
        print(msg)
        return msg

    def evaluate_none_arg_rules(self,key):
        rule_failed = 0
        ret = []
        _r = eval(type(self).__name__ + '.'+self.rules_immediate_eval_dict[key])
          # convert result to array of arrays
        for r in _r: 
             # do error log printing
             if( r == 0 ): rule_failed += 1
             ret.append([r])
        if(rule_failed > 0 ): print('Rule: ' + self.rules_immediate_eval_dict[key] + ' was failed ' + str(rule_failed) + ' time(s)') 
        return ret

     # Basic method to call all rules once
    def fireBRM(self):       
        start_time = time.time()
        self.errors_msg = ''
        # loop over the all rules in evuluated rules dictionary
        ret = 0.
        normalizer = 0
        for key,rules in  self.eval_rules_dict.items():
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
                _ret = _ret * rule_ret
            if( key in self.rules_immediate_eval_dict ) :  
                _ret = _ret * self.evaluate_none_arg_rules(key)
            if( key in RulesFactory._boolean_operations_dict ): 
                #call numpy boolean functions for whole column _ret = np.logical_not(_ret)
                if(RulesFactory._boolean_operations_dict[key] == 'NOT' ):
                    _ret = np.logical_not(_ret)
                elif(RulesFactory._boolean_operations_dict[key] == 'XOR' ):
                    _ret = np.logical_not(_ret,_ret)
            normalizer += 1
            self.errors_msg += self.log_error_message(key, _ret) + '\n'          
            ret  +=  _ret*1 
        ret = ret/normalizer * 100
        print("Execution time: --- %s seconds ---" % (time.time() - start_time))
        return ret

    def collect_rule_statistic(self,ret):
        i,j,l, failed_count,completed_count  = 0,0,0,0,0
        positions_f =  []
        positions_ok = []
        for res in ret:
           if( res[0] == 0 ): 
               failed_count += 1 
               positions_f.append(j)
           else:
              completed_count += 1 
              positions_ok.append(j)
           j += 1 

        str_f = ' '.join([str(x)+',' for x in positions_f]) 
        str_ok = ''.join([str(x)+' with ' + str(int(ret[x][0])) + '% of success,'  for x in positions_ok]) 
        html =   "<html><p> <red> " +  self.errors_msg + ' </red> </p> '
        print( self.errors_msg )
        msg =  "Total: " + str(failed_count)  + " car with all rules failed in positions: " + str_f 
        print( msg )
        html +=  "<html><p><b>  " + msg + " </b></p>"
        msg =  "Total: " + str(completed_count)  + " car with rules satisfied in positions: " + str_ok 
        print( msg )
        html += "<p><b> " + msg + " </b></p></html>"
        print(html)
        return html

"""   Use this block for testing this class """
if(__name__ == "__main__"):
    rows,cols = 2,1
    file_locParams="matrixOfParams.xlsx"
    #file_locRules="BRMRulesInColumns.xlsx"
    file_locRules="BRMRulesInRows.xlsx"

    #Test with JSON array
    RulesFactory.loadParametersFromJSON('[{"STCC": "48ttrtt", "Position":1,"Length":34,"Weight":65, "CushionDB":"Y"}, {"STCC": "49422h", "Position":2,"Length":30,"Weight":60, "CushionDB":"Y"}]')

    #Test with Excell Spread Sheet define all parameters:
#    param_mtrx = RulesFactory.loadMatrixFromExcellAsConstants(file_locParams)
#    STCC      = param_mtrx [0][0:rows]
#    Position_  = RulesFactory.vector_to_matrix(np.arange(rows))
#    Weight_    = RulesFactory.vector_to_matrix(param_mtrx [1][0:rows])
#    Length_    = RulesFactory.vector_to_matrix(param_mtrx [2][0:rows])
#    CushionDB_ = RulesFactory.vector_to_matrix(param_mtrx [3][0:rows])
   # Hazard_ =    RulesFactory.vector_to_matrix(param_mtrx [4][0:rows])


    rf = RulesFactory(file_locRules,rows,cols)
    print('########################################## BRM result ########################################################')   
    ret = rf.fireBRM()
    i,j,l, failed_count,completed_count  = 0,0,0,0,0
    positions_f =  []
    positions_ok = []
    for res in ret:
       if( res[0] == 0 ): 
           failed_count += 1 
           positions_f.append(j)
       else:
          completed_count += 1 
          positions_ok.append(j)
       j += 1 

    str_f = ''.join([str(x)+',' for x in positions_f]) 
    str_ok = ''.join([str(x)+' with ' + str(int(ret[x][0])) + '% of success,'  for x in positions_ok]) 
    print(" Total: " + str(failed_count)  + " car with all rules failed in positions: " + str_f)
    print(" Total: " + str(completed_count) + " cars with some rules completed in positions: " + str_ok )

    print(ret)



# Example usage in FaaS , rules are only evaluated 
# invoke method called from index.py

def invoke(args):
  # print("################### Welcome to BRM engine ###################### ")
    rows,cols = 50,1
    file_locParams="matrixOfParams.xlsx"
    file_locRules="BRMRulesInRows.xlsx"

#Test with Excell Spread Sheet define all parameters: 
    param_mtrx = RulesFactory.loadMatrixFromExcellAsConstants(file_locParams)
    (globals()['STCC'])  = param_mtrx [0][0:rows]
    (globals()['Position_'])  = RulesFactory.vector_to_matrix(np.arange(rows))
    (globals()['Weight_'])    = RulesFactory.vector_to_matrix(param_mtrx [1][0:rows])
    (globals()['Length_'])    = RulesFactory.vector_to_matrix(param_mtrx [2][0:rows])
    (globals()['CushionDB_']) = RulesFactory.vector_to_matrix(param_mtrx [3][0:rows])
    (globals()['Hazard_'])    = RulesFactory.vector_to_matrix(param_mtrx [4][0:rows])
    rf = RulesFactory(file_locRules,rows,cols)
  #  rf.show_log = False
  # Test with JSON array this is is test only
     #RulesFactory.loadParametersFromJSON(args)
# body examle : '[{"STCC": 1, "Position":1,"Length":34,"Weight":65, "CushionDB":"Y", "Hazard":"Y"}, {"STCC": 1, "Position":2,"Length":30,"Weight":60, "CushionDB":"Y", "Hazard":"N"}]'
     # STCC - is exceptional case
    ret = rf.fireBRM()
    return ret

