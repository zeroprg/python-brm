from theano import tensor as T
import theano, time, numpy
import re



class RuleEvaluator(object):
    """A RuleEvalutor evaluate symbolic rule . RuleEvaluator have the
    following properties:

    Attributes:
        python_code_rule: A string of the Python code representing formula.
        operand: A simple operand '<', '>'. '-'.
        args: list of symbolic variables (string), init. inside by Theano library
        
    """


   # Return a RuleEvaluator object which is wrapper on top of  ifelse(T.lt(a, b), T.mean(x), T.mean(y)),  self.ones, self.zeros,) use to apply to
   # rules like "a  > b "  it is always compare with each other 
    def __init__(self, rule_left, operand, rule_right, args,rows,cols):
        self.show_log = True
        self.rule_left = rule_left
        self.rule_right = rule_right
        self.operand =operand
        self.rule = rule_left + operand + rule_right
        self.args_str = ','.join(args)
        self.f_switch = []
        # define all symbolic arguments
        operands_const= {'>' : 'T.gt(' + rule_left +', _const)',
                        '<' : 'T.lt(' + rule_left +', _const)',
                        '<=': 'T.le(' + rule_left +', _const)',
                        '=<': 'T.le(' + rule_left +', _const)',
                        '>=': 'T.ge(' + rule_left +', _const)',
                        '=>': 'T.ge(' + rule_left +', _const)',
                        '=' : 'T.eq(' + rule_left +', _const)',
                        }
        operands      = {'>' : 'T.gt(' + rule_left +','+ rule_right+')',
                        '<' : 'T.lt(' + rule_left +','+ rule_right+')',
                        '<=': 'T.le(' + rule_left +','+ rule_right+')',
                        '=<': 'T.le(' + rule_left +','+ rule_right+')',
                        '>=': 'T.ge(' + rule_left +','+ rule_right+')',
                        '=>': 'T.ge(' + rule_left +','+ rule_right+')',
                        '=' : 'T.eq(' + rule_left +','+ rule_right+')',
                        }

        for p in args:
            globals()[p] = T.dmatrix(p)

        arg_set = eval('[' + ','.join(args) + ']')
        total = ''
        if( rule_left.find('sum(' )>=0 or rule_right.find('sum(')>=0 ):
            self.f_switch.append(theano.function(arg_set, self.__rule(arg_set), mode=theano.Mode(linker='vm')))
        else:
            self.ones = numpy.ones((rows,cols))
            self.zeros = numpy.zeros((rows,cols))
            match_bracket = re.search(r'\[(.*)\]', rule_right)
            if match_bracket:
                r = match_bracket.group(1).split(',')
                for item in r:
                    if '.' in item:
                       _const = T.constant(float(item))    
                    else:
                       _const = T.constant(int(item))    
                    t_compare = eval( operands_const[operand] )
                    z_switch = T.switch(t_compare, self.ones, self.zeros)
                    self.f_switch.append(theano.function(arg_set, z_switch, mode=theano.Mode(linker='vm')))
            else:
                    t_compare = eval(operands[operand])
                    z_switch = T.switch(t_compare, self.ones, self.zeros)
                    self.f_switch.append(theano.function(arg_set, z_switch, mode=theano.Mode(linker='vm')))

    def __rule(self,p1,*therest):
        print(self.rule)
        if(self.rule_right == '0'):
           r_str = self.rule_left + self.operand + self.rule_right
        else:
           r_str = self.rule_left +'-' + self.rule_right  + self.operand + '0'
        param =  eval(r_str)
        return param

    def evaluate(self,p1,*therest):
        if(len(p1) == 0): 
            raise Exception('Parameter(s): "' + self.args_str + '" must be initiated by not empty arrays before rule: "' + self.rule +'" evaluation')
        ret = self.f_switch[0](p1,*therest)
        for i in range(1,len(self.f_switch)):
            ret += self.f_switch[i](p1,*therest)

        if( self.show_log and ret.shape != () ):
            rule_failed = 0
            for r in ret:
                if( 0. in r ) : rule_failed += 1
                    # rule failed
            if ( rule_failed > 0 ): print( 'Rule: "' + self.rule + '" was failed ' + str(rule_failed) + ' time(s)')
        return ret
