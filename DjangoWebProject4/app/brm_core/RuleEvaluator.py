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

    def __init__(self, python_code_rule, operand, args,rows,cols):
        """Return a Customer object whose name is *name* and starting
        balance is *balance*."""
        self.rule = python_code_rule
        self.show_log = True
      # just case 
        constant = args[len(args)-1] # constant is last arg
        self.operands = {'>' : 'T.gt(self.param,0)',
                        '<' : 'T.lt(self.param,0)',
                        '<=': 'T.le(self.param,0)',
                        '>=': 'T.ge(self.param,0)',
                        '=' : 'T.eq(self.param,0)'
                    }
 
        self.operand = self.operands[operand]
        self.operand_symb = operand
        self.args = args
        self.args_str = (','.join(args))
        #print(self.args_str)
        for p in self.args:
            globals()[p] = T.dmatrix(p)
        #evaluate list of parameters    
        self._list = eval('[' + self.args_str + ']')
        #print(a)
        
        self.param = T.dmatrix('param')
        self.ones = numpy.ones((rows,cols))
        self.zeros = numpy.zeros((rows,cols))
        self.f_switch = theano.function(self._list, self.__rule(self._list),
                            mode=theano.Mode(linker='vm'))


        
 
        
        
            
    """This very generic rule evaluated during construction class
    ."""
    def __rule(self,p1,*therest):
        print(self.rule)
        if( self.rule.find('sum(') >=0 ): 
            self.param =  eval(self.rule + self.operand_symb + '0')
        else:
            self.param = eval(self.rule) 
            self.param = T.switch(eval(self.operand),  self.ones, self.zeros,)
            
        return self.param
    
        
        

    def evaluate(self,p1,*therest):
        """Return the function which available to apply arguments and run
        ."""
        ret = self.f_switch(p1,*therest) 
        if( self.show_log and ret.shape != () ):
            rule_failed = 0
            for r in ret:
                if( 0. in r ) : rule_failed += 1
                    # rule failed
            if ( rule_failed > 0 ): print( 'Rule: "' + self.rule + ' '+self.operand_symb + ' 0" was failed ' + str(rule_failed) + ' time(s)')
        return ret




# Tests
rows,cols = 20,1

m1 = numpy.random.randint(3,size=(rows,cols)) # [[1,1]] 
m2 = numpy.random.randint(3,size=(rows,cols)) # [[1],[-1]]
m3 = numpy.random.randint(3,size=(rows,cols)) #[[1],[-1]]
m4 = numpy.random.randint(3,size=(rows,cols))
m5 = numpy.random.randint(3,size=(rows,cols))

#x = T.dvector('x')
#y = x.sum()
#x = numpy.random.randint(5,size=(rows,cols))  



#re = RuleEvaluator('a','>',['a'],rows,cols)
totalRule = RuleEvaluator('((a).sum() / (b).sum()) - 1','>',['a','b'],rows,cols)
rule = RuleEvaluator('(a -b)','>',['a','b'],rows,cols)
one_arg_rule = RuleEvaluator('a','>',['a'],rows,cols)
one_arg_rule2 = RuleEvaluator('a-1','>','a',rows,cols)
#c =  re.evaluate(m3)

print ('a: ' ) 
print (m3) 
print ('b: ')
print (m5)

print ('a>0: ' ) 
print ( one_arg_rule.evaluate(m3) )

print( 'a-1>0: ')
print ( one_arg_rule2.evaluate(m3) )

print( '((a).sum() / (b).sum()) - 1 > 0:')
c =  totalRule.evaluate(m3,m5)
print (c)


print( '{((a).sum() / (b).sum()) - 1 > 0} and {a-b > 0} :')
c =  totalRule.evaluate(m3,m5)*rule.evaluate(m3,m5)*1
print (c)
 

set1 = (m3,m5)
set2 = (m1,m2)

# Create mapping between vaiables and real data
param_dict = {'a' : m1, 'b': m2}
set1 = (m3,m5)
set2 =  (param_dict['a'], param_dict['b'])
#print(a, b)
# Applying multiple rules 
print( '{((a).sum() / (b).sum()) - 1 > 0} and {a-b > 0}  +  { (a -b) > 0 }:')
c =  (totalRule.evaluate(*set1) * rule.evaluate(*set2) + rule.evaluate(*set2))/2





 


# loop over all available rules:
 
 
print (c)


