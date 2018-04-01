from theano import tensor as T
import theano, time, numpy

rows, cols = 2,2

param,constant = T.dmatrices('param','constant')

p1,p2,p3,p4 = T.dmatrices('p1','p2','p3','p4')
x,y,z,w,u = T.dmatrices('x','y', 'z', 'w','u')

ones = numpy.ones((rows,cols))
zeros = numpy.zeros((rows,cols))


# Second Group of rules - Decision Tree rules , apply to all nodes
def rule(p1,*therest):
    param = eval('p1 + p2 + p3 + p4')    
    param = T.switch(eval('T.eq(param,constant)'), ones,zeros)
    return param

#param = eval('p1+p2/p3')

list = [p1,p2,p3,p4, constant]
f_switch = theano.function(list, eval('rule(p1,p2,p3,p4, constant)'),
                            mode=theano.Mode(linker='vm'))

m1 = numpy.random.rand(rows,cols)
m2 = numpy.random.rand(rows,cols)
m3 = numpy.random.rand(rows,cols)
m4 = numpy.random.rand(rows,cols)
m5 = numpy.random.rand(rows,cols)

print(f_switch(m1, m2, m3, m4, m5))
