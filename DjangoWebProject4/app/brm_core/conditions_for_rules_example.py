from theano import tensor as T
from theano.ifelse import ifelse
import theano, time, numpy

a,b = T.scalars('a', 'b')
x,y = T.matrices('x', 'y')

#I would think of it as just another operator that acts on three symbolic variables, if the first is true, return the second, else return the third.
#But for many operators (like - and +) theano has overloaded them for symbolic variables, so probably you don't feel the difference.
#For example, if a and b are numbers, then c=a+b creates a variable c with the value of a+b. If a and b are symbolic variables, then c=a+b creates another symbolic variable c, that will apply (element-wise) addition to a and b when the corresponded function gets called/evaluated.
#Here's an introduction on theano operators and graphs. http://deeplearning.net/software/theano/extending/graphstructures.html

z_switch = T.switch(T.lt(a, b), T.mean(x), T.mean(y))
z_lazy = ifelse(T.lt(a, b), T.mean(x), T.mean(y))

f_switch = theano.function([a, b, x, y], z_switch,
                           mode=theano.Mode(linker='vm'))
f_lazyifelse = theano.function([a, b, x, y], z_lazy,
                               mode=theano.Mode(linker='vm'))

val1 = 0.
val2 = 1.
big_mat1 = numpy.ones((10000, 1000))
big_mat2 = numpy.ones((10000, 1000))

n_times = 10

tic = time.clock()
for i in range(n_times):
    f_switch(val1, val2, big_mat1, big_mat2)
print('time spent evaluating both values %f sec' % (time.clock() - tic))

tic = time.clock()
for i in range(n_times):
    f_lazyifelse(val1, val2, big_mat1, big_mat2)
print('time spent evaluating one value %f sec' % (time.clock() - tic))