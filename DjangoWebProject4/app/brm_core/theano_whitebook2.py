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
        
       # just case 
        constant = args[len(args)-1] # constant is last arg
        self.operands = {'<' : 'T.gt(self.param,'+ constant +')',
                         '>' : 'T.lt(self.param,'+ constant +')',
                         '=' : 'T.eq(self.param,'+ constant +')'
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
        if( self.rule.find('sum(') ): 
            self.param =  eval(self.rule + self.operand_symb + '0')
        else:
            self.param = eval(self.rule)
            self.param = T.switch(eval(self.operand), self.zeros, self.ones)
            
        return self.param
    
        
        

    def evaluate(self,p1,*therest):
        """Return the function which available to apply arguments and run
        ."""
        ret = self.f_switch(p1,*therest) 
        return ret




# Tests
rows,cols = 2,2

m1 = numpy.random.randint(3,size=(rows,cols))
m2 = numpy.random.randint(3,size=(rows,cols))
m3 = numpy.random.randint(3,size=(rows,cols))
m4 = numpy.random.randint(3,size=(rows,cols))
m5 = numpy.random.randint(3,size=(rows,cols))

x = T.dvector('x')
y = x.sum()
x = numpy.random.randint(5,size=(rows,cols))  


#re = RuleEvaluator('a-b','>',['a','b'],rows,cols)
#re = RuleEvaluator('a','>',['a'],rows,cols)
re1 = RuleEvaluator('((a).sum() / (b).sum()) - 1','>',['a','b'],rows,cols)
re2 = RuleEvaluator('(a -b)','>',['a','b'],rows,cols)

#c =  re.evaluate(m3)

print ('a: ' ) 
print (m3) 
print ('b: ')
print (m5)
#print( 'a-b>0: ')
print( '((a).sum() / (b).sum()) - 1 > 0 :')
c =  re1.evaluate(m3,m5)*re2.evaluate(m3,m5)/2

print (c)
c =  re1.evaluate(m3,m5)*re2.evaluate(m3,m5)
print (c)
 

