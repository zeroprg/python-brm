from theano import tensor as T
import theano, time, numpy

from RuleEvaluator import RuleEvaluator

# Tests
rows,cols = 20,1

m1 = numpy.random.randint(3,size=(rows,cols)) # [[1,1]] 
m2 = numpy.random.randint(3,size=(rows,cols)) # [[1],[-1]]
m3 = numpy.random.randint(3,size=(rows,cols)) #[[1],[-1]]
m4 = numpy.random.randint(3,size=(rows,cols))
m5 = numpy.random.randint(3,size=(rows,cols))

print ('a: ' ) 
print (m3) 
print ('b: ')
print (m5)

#x = T.dvector('x')
#y = x.sum()
#x = numpy.random.randint(5,size=(rows,cols))  

rule0 = RuleEvaluator('a','>','b',['a','b'],rows,cols)
print ('a>b: ' ) 
print ( rule0.evaluate(m3,m5) )

rule1 = RuleEvaluator('a','>','0',['a'],rows,cols)
print ('a>0: ' ) 
print ( rule1.evaluate(m3) )


#re = RuleEvaluator('a','>',['a'],rows,cols)
totalRule = RuleEvaluator('((a).sum() / (b).sum()) - 1','>','0',['a','b'],rows,cols)
one_arg_rule1 = RuleEvaluator('a','>','0',['a'],rows,cols)

one_arg_rule2 = RuleEvaluator('a-1','>','a',['a'],rows,cols)

#c =  re.evaluate(m3)

print ('a: ' ) 
print (m3) 
print ('b: ')
print (m5)



print ('a>0: ' ) 
print ( one_arg_rule1.evaluate(m3) )

print( 'a-1>0: ')
print ( one_arg_rule2.evaluate(m3) )

print( '((a).sum() / (b).sum()) - 1 > 0:')
c =  totalRule.evaluate(m3,m5)
print (c)


print( '{((a).sum() / (b).sum()) - 1 > 0} and {a-b > 0} :')
c =  totalRule.evaluate(m3,m5) * rule0.evaluate(m3,m5)*1
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
c =  (totalRule.evaluate(*set1) * rule0.evaluate(*set2) + rule0.evaluate(*set2))/2





 


# loop over all available rules:
 
 
print (c)





