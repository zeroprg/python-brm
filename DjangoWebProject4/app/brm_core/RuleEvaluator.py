from theano import tensor as T
import theano, time, numpy




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
        # define all symbolic arguments
        for p in args:
            globals()[p] = T.dmatrix(p)

        arg_set = eval('[' + ','.join(args) + ']')

        if( rule_left.find('sum(' )>=0 or rule_right.find('sum(')>=0 ):
            self.f_switch = theano.function(arg_set, self.__rule(arg_set), mode=theano.Mode(linker='vm'))
        else:
            operands =      {'>' : 'T.gt(' + rule_left +','+ rule_right+')',
                             '<' : 'T.lt(' + rule_left +','+ rule_right+')',
                             '<=': 'T.le(' + rule_left +','+ rule_right+')',
                             '>=': 'T.ge(' + rule_left +','+ rule_right+')',
                             '=' : 'T.eq(' + rule_left +','+ rule_right+')',
                            }
            t_compare = eval( operands[operand] )
            self.ones = numpy.ones((rows,cols))
            self.zeros = numpy.zeros((rows,cols))
            z_switch = T.switch(t_compare, self.ones, self.zeros)
            self.f_switch = theano.function(arg_set, z_switch, mode=theano.Mode(linker='vm'))

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
        ret = self.f_switch(p1,*therest) 
        if( self.show_log and ret.shape != () ):
            rule_failed = 0
            for r in ret:
                if( 0. in r ) : rule_failed += 1
                    # rule failed
            if ( rule_failed > 0 ): print( 'Rule: "' + self.rule + '" was failed ' + str(rule_failed) + ' time(s)')
        return ret
