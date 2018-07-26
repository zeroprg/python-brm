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

import logging
logger = logging.getLogger(__name__)

logger = logging.getLogger('log')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('job.log')
fh.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
console.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(console)


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

    _funct_dict = {'check_first_2_characters_of': 'vfind', "starts_with": "vstarts_with", "Sum_of": 'sum'  }
    _constant_dict = {'Y': 1, 'N': 0}
    _boolean_operations_dict = {} #' np.logical_and, np.logical_or, np.logical_xor 



    def conv_rule1(val):
        match = re.search(r'(?<=sum\()\w+', val)
        if( not match ): raise Exception( 'function Sum_of must have at least 1 argument. Error in: ' + str )
        while match : 
            arg = match.group(0)
            val = val.replace('sum(' + arg + ')', '(' + arg + ').sum()')
            match = re.search(r'(?<=sum\()\w+', val)
        return val
##############################################################################
#          This is example of hardcoded exceptional rule
##############################################################################
# find any occurance of elements start with (48,49) in begining of  string only for  position <5 and fail the rule if found :  return False
    def find(string, position): 
        ret = False
        if( position < 5):
            for arg in ('48', '49'):
               if( string.find(arg) == 0 ): 
                   ret = True
                   break
        else: ret = True 
        return ret

    def starts_with(string, arg):
        return (string.startswith(arg))

# define function to find as global variable
    vfind = np.vectorize(find)
    vstarts_with = np.vectorize(starts_with)
# test vfind 
#logger.info(vfind(['48werw','46sffsdf', '45sffsdf', '49gdf', '48sds'], [1,2,3,4,5]))


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
            logger.info('Matrix of rules:')
            logger.info('##########################################################################################################################')
            logger.info(self.rules_mtrx)

        #self.EvaluateAllRulesByColumns()
        self.EvaluateAllRulesByRows()
        if( self.show_log ):
            logger.info('Dictionary of evaluated rules:')
            logger.info('##########################################################################################################################')
            logger.info(self.eval_rules_dict)


  
        # This is static method used as helper to download parameters from spreadsheet for BRM evaluator. 
        # WARNING: Parameters must be initiated before any rules evaluations : (self.EvaluateAllRules())
        def load_params_from_excel(file_loc,except_params=('STCC','Position','AAR_CAR_TYPE','SCS')):
            wkb=xlrd.open_workbook(file_loc)
            sheet=wkb.sheet_by_index(0)
            header_row = 0
            header_name =''
            for col in range (sheet.ncols):
                    _row = []
                    for row in range (sheet.nrows):
                         val = sheet.cell_value(row,col)
                         if(row == header_row): 
                             header_name = val
                             (globals()[header_name]) = (globals()[header_name+'_']) = []
                         if(not(header in except_params)): #exception case: read first column as it is without hash conversion 
                            if(not( type(val) is float or type(val) is int ) ): val = RulesFactory.convertToInt(val)
                         (globals()[header_name]).append(val)
            return

   ########################################### Static methods and classes ########################################################

    # This is static method used as helper to download parameters from json file for BRM evaluator. 
    # WARNING: Parameters must be initiated before any rules evaluations : (self.EvaluateAllRules())
    def load_params_from_json(json_str, except_params=('STCC','Position','AAR_CAR_TYPE','SCS')):        
        data = json.loads(json_str)
        for key in data[0]:
            key_ = key
            if(not (key in except_params)): 
                key_ = key +'_'
            else:
                (globals()[key+'_']) = [] #Make params  like this 

            (globals()[key_]) = []
            temp = []
            for i in range(len(data)):
                val = data[i][key]
                if(not( key in except_params)):
                    if(not( type(val) is float or type(val) is int ) ): val = RulesFactory.convertToInt(val)
                temp.append(val)
            #if(not( key in except_params)):
            (globals()[key+'_']) =  RulesFactory.vector_to_matrix(temp)
            if(key in except_params):
                (globals()[key]) = temp
        RulesFactory.is_params_loaded = True
        return len(data)

    # This is static method used as helper to download parameters from csv file for BRM evaluator. 
    # WARNING: Parameters must be initiated before any rules evaluations : (self.EvaluateAllRules())
    def load_params_from_csv(file_loc,except_params=('STCC','Position','AAR_CAR_TYPE','SCS')): 
        ret = 0
        with open(file_loc) as f:
            reader = csv.DictReader(f)
            data = [r for r in reader]
            ret = loadParametersFromJSON(data, except_params)
        return ret


    def convertToInt(s):
        ret = 0
        # get from  dict fro mmost common constants
        if(s in RulesFactory._constant_dict):
           ret = RulesFactory._constant_dict[s]
        # generate hash code
        else:
           ret = abs(hash(s)) % (10 ** 8)
        return ret
        
    
    # Replace constants by encoded integer for all possible variations including constants in list like this : "['A','B']"
    def constantReplacer(val):
        match_bracket = re.search(r'\[(.*)\]', val)
        ret = val
        if match_bracket:
            const_com = match_bracket.group(1)
            const_arr = const_com.split(',')
            for item in const_arr:
                match_quote = re.search(r'\'(.*)\'', item)
                v = match_quote.group(1)
                hashcode = str(RulesFactory.convertToInt(v))
                ret = ret.replace( item , hashcode )
                
        else:
            match_quote = re.search(r'\'(.*)\'', val)
            if not match_quote: raise Exception( 'Constants must be in one quotes like this \'Y\' or \'N\'. Error in:  ' + val )
            const =  match_quote.group(1)        
            hashcode = str(RulesFactory.convertToInt(const))
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
            arg = arg.strip()
            if( rule.find(arg) >=0 ): args.append(arg)
        if( not args ): raise Exception( 'Rule: "' +  rule+ '"  must have at least one argument from the header of spread shhet.  To fix it define argument in first row of spreadsheet ')
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
                        if(not( type(val) is float or type(val) is int ) ): val = RulesFactory.convertToInt(val)
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
                            
                         if( val.find('\'') >=0 ): val = RulesFactory.constantReplacer(val)
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
                     if( not val or  val.strip() == '' or val == 'None' ): # Empty cell
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
                            
                         if( val.find('\'') >=0 ): val = RulesFactory.constantReplacer(val)
                         _row.append(val)
                _matrix.append(_row)
        return _matrix    
    # Algorithm of  rules conversion
    # check if the rule has any constants (embedded in '') if yes convert constant to integer hashcode
    # check if the rule has function  which required some preprocessing
    # for example check_first_2_characters_of(...) . If it has then fire rule preprocessor to convert it to vfind(...)
    # This rule requiered translation and  data preparation before firing it 
    # both sides left and right must be numeric

    def EvaluateAllRulesByRows(self):
        # Evaluate ( convert the rules from strings to real functions)
        start_time = time.time()

        for i in range(1,len(self.rules_mtrx)):
            _rules = []
            for j in range(len(self.rules_mtrx[0])):
                all_params = self.rules_mtrx[0][j]
                rule = self.rules_mtrx[i][j]
                if( not rule or rule == 'None'): continue
                operand = self.find_operand(rule,['>=','=>','<=','=<','=','<','>']) # move to translate rule
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
        logger.info("Evaluation time: --- %s seconds ---" % (time.time() - start_time))

    def log_error_message(self, key, ret):
        if (not self.show_log): return ''        
        msg=''
        logger.info(ret)        
        if( any(r[0] == 0 for r in ret)):
            msg = key  + ': ' + self.error_message[key] 
            self.errors_msg += msg + '<br><br>'
            logger.info(msg)
        return msg

    def evaluate_none_arg_rules(self,key):
        rule_failed = 0
        ret = []
        _r = eval(type(self).__name__ + '.'+self.rules_immediate_eval_dict[key])
          # convert result to array of arrays
        for r in _r: 
             # do error log logger.infoing
             if( r == 0 ): rule_failed += 1
             ret.append([r])
        if(self.show_log and rule_failed > 0 ): 
            logger.info('Rule: ' + self.rules_immediate_eval_dict[key] + ' was failed ' + str(rule_failed) + ' time(s)') 
        return ret

     # Basic method to call all rules once
    def fireBRM(self):       
        start_time = time.time()
        self.errors_msg = ''
        # loop over the all rules in evuluated rules dictionary
        ret = 0.
        normalizer = 0
        ones = np.ones((self.rows,1))
        for key,rules in  self.eval_rules_dict.items():            
            _ret = ones
            for rule_tupil in rules:
                #get value from rule tupil
                rule = rule_tupil[0]
                rule_params = rule_tupil[1]
                # all arguments are global and must end with '_' because there is symbolic arg with the same name
                if( not isinstance(rule_params, (tuple)) ): # if not list
                     # 1 argument rule (compare to 0)  
                   rule_ret = rule.evaluate(rule_params)
                else: # 2 arguments rule
                   rule_ret = rule.evaluate(*rule_params)
                _ret =  rule_ret *_ret
            if( key in self.rules_immediate_eval_dict ) :  
                _ret = _ret * self.evaluate_none_arg_rules(key)
            if( key in RulesFactory._boolean_operations_dict ): 
                #call numpy boolean functions for whole column _ret = np.logical_not(_ret)
                if(RulesFactory._boolean_operations_dict[key] == 'NOT' ):
                    _ret = np.logical_not(_ret)
                elif(RulesFactory._boolean_operations_dict[key] == 'XOR' ):
                    _ret = np.logical_not(_ret,_ret)
            normalizer += 1
            self.log_error_message(key, _ret)     
            ret  +=  _ret*1 
            
        ret = ret/normalizer * 100
        logger.info("Execution time: --- %s seconds ---" % (time.time() - start_time))
        return ret

    def collect_rule_statistic(self,ret):
        i,j,l, failed_count,completed_50_count,completed_75_count,completed_100_count,completed_ok_count  = 0,0,0,0,0,0,0,0
        positions_f =  []
        positions_50 = []
        positions_75 = []
        positions_100 = []
        positions_ok = []
        for res in ret:
           logger.info(res)
           if( res[0] == 0): 
               failed_count += 1 
               positions_f.append(j)
           elif(res[0] <50):
              completed_50_count += 1 
              positions_50.append(j)
           elif(res[0] <75):
              completed_75_count += 1 
              positions_75.append(j)
           elif(res[0] <100):
              completed_100_count += 1 
              positions_100.append(j)
           else:
              completed_ok_count += 1 
              positions_ok.append(j)


           j += 1 

        str_f =  ' '.join([str(x)+'/'+str(int(ret[x][0])) + '%, ' for x in positions_f]) 
        str_50 = ' '.join([str(x)+'/'+str(int(ret[x][0])) + '%, ' for x in positions_50]) 
        str_75 = ' '.join([str(x)+'/'+str(int(ret[x][0])) + '%, ' for x in positions_75]) 
        str_100 =' '.join([str(x)+'/'+str(int(ret[x][0])) + '%,  ' for x in positions_100]) 
        str_ok = ' '.join([str(x) + ', '  for x in positions_ok]) 

        html = '<html><h1> This  is BRM statistic: </h1>'
        logger.info( self.errors_msg )
        if( str_f ):
            msg =  "Total: " + str(failed_count)  + " car with all rules failed in positions: " + str_f 
            logger.info( msg )
            html +=  '<p><b> Total: <span style="color:red;"> ' + str(failed_count)  + '</span> car(s) with all rules failed in positions: <span style="color:red;">' + str_f  + '</span></b></p>'
        if( str_50 ):
            msg =  "Total: " + str(completed_50_count)  + " car failed in positions: " + str_50
            logger.info( msg )
            html +=  '<p><b> Total: <span style="color:orange;"> ' + str(completed_50_count)  + '</span> car(s) (position/rules completed rate): <span style="color:orange;">' + str_50  + '</span></b></p>'
        if( str_75 ):
            msg =  "Total: " + str(completed_75_count)  + " car failed in positions: " + str_75
            logger.info( msg )
            html +=  '<p><b> Total: <span style="color:orange;"> ' + str(completed_75_count)  + '</span> car(s) (position/rules completed rate): <span style="color:orange;">' + str_75  + '</span></b></p>'
        if( str_100 ):
            msg =  "Total: " + str(completed_100_count)  + " car failed in positions: " + str_100 
            logger.info( msg )
            html +=  '<p><b> Total: <span style="color:blue;"> ' + str(completed_100_count)  + '</span> car(s) (position/rules completed rate): <span style="color:blue;">' + str_100  + '</span></b></p>'
        if( str_ok ):
            msg =  "Total: " + str(completed_ok_count)  + " car with rules satisfied in positions: " + str_ok 
            logger.info( msg )
            html +=  '<p><b> Total: <span style="color:green;"> ' + str(completed_ok_count)  + '</span> car(s)  with all rules completed in positions: <span style="color:green;">' + str_ok  + ' has 100% success</span></b></p>'
        html += "</html>"
        #logger.info(html)
        return html

"""   Use this block for testing this class """
if(__name__ == "__main__"):
    rows,cols = 0,1
    #file_locParams="matrixOfParams.xlsx"
    #file_locRules="BRMRulesInColumns.xlsx"
    #file_locRules="BRMRulesInRows.xlsx"
    file_locRules="BRMRulesLatest.xlsx"
        #Test with JSON array
    rows = RulesFactory.load_params_from_json('''[
              {
                "STCC": "48ttrtt",
                "Position": 1,
                "Length": 34,
                "Weight": 65,
                "Hazardous":"N",
                "CushionDB": 0,
                "BEARINGS":"A",
                "STATION": 6300,
                "EMPTY_LOAD": 2,
                "CAR_SERIES": "MILW10000",
                "AAR_CAR_TYPE": "M310",
                "SCS":"112J34534"
              },
              {
                "STCC": "49422h",
                "Position": 2,
                "Length": 30,
                "Weight": 60,
                "Hazardous":"N",
                "CushionDB": 5,
                "BEARINGS":"B",
                "STATION": 6305,
                "EMPTY_LOAD": 2,
                "CAR_SERIES": "MILW123000",
                "AAR_CAR_TYPE": "M340",
                "SCS":"112J34534"
              },
              {
                "STCC": "422h",
                "Position": 2,
                "Length": 35,
                "Weight": 6,
                "Hazardous":"Y",
                "CushionDB": 35,
                "BEARINGS":"C",
                "STATION": 6304,
                "EMPTY_LOAD": 2,
                "CAR_SERIES": "MILW113000",
                "AAR_CAR_TYPE": "M340",
                "SCS":"112J34534"
              },
              {
                "STCC": "4422h",
                "Position": 2,
                "Length": 34,
                "Weight": 6,
                "Hazardous":"Y",
                "CushionDB": 36,
                "BEARINGS":"C",
                "STATION": 6104,
                "EMPTY_LOAD": 2,
                "CAR_SERIES": "MILW113000",
                "AAR_CAR_TYPE": "M340",
                "SCS":"112J34534"
              }  
            ]''')

    #Test with Excell Spread Sheet define all parameters:
#    param_mtrx = RulesFactory.loadMatrixFromExcellAsConstants(file_locParams)
#    STCC      = param_mtrx [0][0:rows]
#    Position_  = RulesFactory.vector_to_matrix(np.arange(rows))
#    Weight_    = RulesFactory.vector_to_matrix(param_mtrx [1][0:rows])
#    Length_    = RulesFactory.vector_to_matrix(param_mtrx [2][0:rows])
#    CushionDB_ = RulesFactory.vector_to_matrix(param_mtrx [3][0:rows])
   # Hazard_ =    RulesFactory.vector_to_matrix(param_mtrx [4][0:rows])


    rf = RulesFactory(file_locRules,rows,cols)
    rf.show_log = True
    logger.info('########################################## BRM result ########################################################')   
    ret = rf.fireBRM()
    rf.collect_rule_statistic(ret)

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
    logger.info(" Total: " + str(failed_count)  + " car with all rules failed in positions: " + str_f)
    logger.info(" Total: " + str(completed_count) + " cars with some rules completed in positions: " + str_ok )

    logger.info(ret)
