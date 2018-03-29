import re
import theano, numpy
import theano.tensor as T
import xlrd
from collections import defaultdict


# Default lamdas
less = lambda param, constant:  T.switch(T.lt(param,constant),  x, y)
greater = lambda param, constant:  T.switch(T.gt(param,constant),  x, y)
total = lambda x: T.dot(x,numpy.ones((len(x))))
def substring(str,arg1):
        return str [0:arg1-1]


# Stack  of functions which will apply sequentially
functs =[]

args = d = dict() 
var_dict = {"var1" : 1 , "var2" : 2 ,"var3" : 3  }
f_dictPriority2 = { ">" : greater, "<" : less  }
f_dictPriority3 = { "Total of" : total }
f_dictPriority1 = { 'extract first % characters':substring }
operandsWith2Args = [">", "<" , ">=", "<=", "!="]
#w, h = 10, 2;
#args = [[0 for x in range(w)] for y in range(h)]




class RuleTranslator(object):
    """A customer of ABC Bank with a checking account. Customers have the
    following properties:

    Attributes:
        name: A string representing the customer's name.
        balance: A float tracking the current balance of the customer's account.
    """

    def __init__(self):
        """Return a Customer object whose name is *name* and starting
        balance is *balance*."""
        self.rule = name
                           
        self.dictionary = f_dictPriority1

    def translate(self, rule):
        """Return the function which available to apply arguments and run
        ."""
        _and = applyDelimeters( rule )
        if amount > self.balance:
            raise RuntimeError('Amount greater than available balance.')
 
        return self.function


# Spit words like this:
#for lines in content[0].split():
#    for split0 in lines.split(' '):
#        for split1 in split0.split(','):
#            for split2 in split1.split('.'):
#                for split3 in split2.split('?'):
#                    for split4 in split3.split('!'):
#                        for word in split4.split(':'): 
#                            if word != "":
#                                print(word)
def splitWords(str):
    delimiters = [' ','and','or','>', '<', 'not equal', '!=', '='] # .., ',' , '.' , '?' , ...
    return re.split('|'.join(delimiters), str)


def applyDelimeter(str, delimeter):
     return re.split(delimeter,str)



# Match words with dictionaries 
def matchWord(words, word):
   for index, next_word in enumerate(words):
       if next_word == word : 
           return index
   return -1

# apply delimeters one by one: 
 #delimiters = [ ' ','and']
 #delimiters = [' ','>', '<', 'and', '']

#print(matchWord( words("How tuff and interesting to code this translator ! !") , "tuff") )

#print( words(" Total((CushionDB<30)and(CushionDB>34))"))
#print( words_d(" Total((CushionDB<30)and(CushionDB>34) and Length <10000 )", "and"))
#print( matchWord ( words("How tuff and interesting to code this translator ! !") ,"<" ) )

# Simple algorithm to generate virtual operand
# 1. Apply close/open parenthes rule and boolean operators 'or' && 'and'



def applyDelimeters( str):
     pat = re.compile("([^,\(]*)\((.*?)\)")
    

     lst = [tuple(nws(item) for item in t) for t in pat.findall(str)]
     return lst

# normalize white space.  Replaces all runs of white space by a single space.
def nws(s):
     return " ".join(w for w in s.split())



# print(lst)  isinstance(words, (tulip,))
# 2. apply hiest prioriy operand ('and') to formed blocks 

def applyDictionary(dictionary, words): 
    applied = False
    i = -1
    for word, next_word in words:
         i += 1
         if ( word in dictionary ) : 
            functs.append (dictionary[word] )
            # check for functions argument . If function has two argument check for previouse arra element and nex element of array
            arg = next_word
            _args = []
            if( word in operandsWith2Args ): 
               if( i > 0 ): raise Exception( word + 'must have 2 arguments, but has only one:' + next_word)
                # read previouse word as first argument
                # _args = applyDelimeter( next_word , operand )
               prev_word = words[i-1]
               _args.append(prev_word)
               _args.append(word)
               args[word] = __arg    
            else:
                 _args.append(arg)
                 args[word] = _args

            applied = True
            # in furture release will be recursion here if functions may call another functions
            # but here will be checked only argument which may have simple openads like >, < , = , >, =, <=

    return applied

def findFirstOpenParenthesesBlock(dict, str):
    start=str.find('{') 
    block =  re.search(r'{(.*)}', str).group(1)
    if( not block ): raise Exception( word + ' must have block of rules started with { and finished with }' )
    start=block.find('{')
    if( start > 0 ):
        # as soon first block found check if this block may be some function argument
        # check if string before this block match any functions from the dictionaty

        # check from left side from parentes '{ '
        block_prefix = str[0:start]
        for funct_word in dict:
            if( block_prefix.find(funct_word)>-1 ):
                if(str.find(funct_word + '{' ) > -1 ): # create a first function
                        functs.append[funct_word]
                        _block =  findFirstOpenParenthesesBlock(dict, block_prefix)
                        if(_block == block_prefix): break # stop left side recursion
            else:
                # check from right side from parentes '{ '
                for funct_word in dict:
                    if( block.find(funct_word)>-1 ):
                        if(str.find(funct_word + '{' ) > -1 ): # create a second function
                                functs.append[funct_word]
                                _block =  findFirstOpenParenthesesBlock(dict, block)
                                if(_block == block):  break # stop left side recursion
                               

    return block




def applyDictionaries( words):
        applyDictionary(f_dict1, words)
        applyDictionary(f_dict2, words)
        return


def Translator(str, row, col):
    headers = {}
    if(row == 0 ) : # read 1 row, header  of names of parameters  
       paramNameByPosition[row]  = str 
       positionByParam[str] = row
   #Form rule based on parameters
    headerOfParams[row] == operator 
    headers[str] # eval(str)
    return



#===========================================================================================#


str = "Calculate { Total of{ (CushionDB<30) and (CushionDB>34) or (Length <10000 )} < 56 } for car in range"
print(str)
str = findFirstOpenParenthesesBlock (f_dictPriority3, str)
_words =  applyDelimeter(str, "and")
first_word_delemiterd =  applyDelimeters(_words[0])
#Check word by word is match with dictionaries' function

print(first_word_delemiterd )
print(functs)

print(applyDictionary(  f_dictPriority3 , first_word_delemiterd ))


