import theano, numpy
import theano.tensor as T
import xlrd

file_locParams="C:\\Users\\ark0006\\Documents\\matrixOfParams.xlsx"
file_locConstants="C:\\Users\\ark0006\\Documents\\matrixOfConstants.xlsx"

def loadMatrixFromExcell(file_loc):
    wkb=xlrd.open_workbook(file_loc)
    sheet=wkb.sheet_by_index(0)

    _matrix=[]
    for row in range (sheet.nrows):
        _row = []
        for col in range (sheet.ncols):
            _row.append(sheet.cell_value(row,col))
        _matrix.append(_row)
    return _matrix


param,constant = T.dmatrices('param','constant')
x,y = T.dmatrices('x','y')


big_mat1 = loadMatrixFromExcell(file_locParams)
big_mat2 = loadMatrixFromExcell(file_locConstants)

#a,b = T.scalars('a', 'b')
#p,c = T.scalars('p','c')

#First group of rules :
# Greater, less , greater or equal 
ruleGT = T.switch(T.gt(param,constant),  x, y)
ruleEQ = T.switch(T.eq(param,constant),  x, y)

# Second Group of rules - Decision Tree rules , apply to all nodes
def ruleDecesionTree1(param, constant):
    return T.switch(T.eq(param,constant), x, y)
# Third group of rules position based rules apply based on different arrangment of nodes

#Scalar's rules 
#ruleGT_s = T.switch(T.gt(p,c),  a, b)
#ruleEQ_s = T.switch(T.eq(p,c) ,  a, b)

ruleAgregator = (ruleGT + ruleGT)/2 # apply 2 rules together for all matrix elements and normilize it after
ruleAgregator_s = ruleEQ + ruleGT  # apply 2 rules together for specifix elements in matrix 

# Apply rules sequentially
f_switch = theano.function([param, constant, x, y], ruleAgregator,
                           mode=theano.Mode(linker='vm'))
# Decision Trees rules switch appy all Decisions Tree rules together
f_switch_DT = theano.function([param, constant, x, y], ruleDecesionTree1(param,constant) + ruleDecesionTree1(param,constant),
                           mode=theano.Mode(linker='vm'))

#f_switch_s = theano.function([p, c, a, b], ruleAgregator_s,
#                           mode=theano.Mode(linker='vm'))

#print(a)






#M = T.stacklists([[ruleGT1(a,b), b], [c, d]])  # apply rule for position 1 depends from position b
#f = theano.function([a, b], M) 
                         
#print(f_switch_s(3,2,1,0))

#print(f(1, 2.0))


rows,cols = len(big_mat1),len(big_mat1[0])
ones = numpy.ones((rows,cols))
zeros = numpy.zeros((rows,cols))
 



print(f_switch(big_mat2, big_mat1 ,ones, zeros ))

print(f_switch_DT(big_mat2, big_mat1 ,ones, zeros ))

#a,b = T.scalars('a', 'b')
#param,constant = te.vectors('param', 'constant')

#z =  a + b

#z_lazy = ifelse(te.lt(a, b), te.mean(param), te.mean(constant))
#f_lazyifelse = theano.function([a, b, param, constant], z_lazy, mode=theano.Mode(linker='vm'))
#print (z)

#M = te.stacklists([[z, z], [b, a]])

#f = theano.function([a, b], M)

#print(f(3, 5))

# [[ 1.  2.]
#  [ 2.  1.]]