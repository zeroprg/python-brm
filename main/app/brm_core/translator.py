import re
import theano, numpy
import theano.tensor as T
import xlrd
from collections import defaultdict


# Default lamdas
less = lambda param, constant:  T.switch(T.lt(param,constant),  x, y)
greater = lambda param, constant:  T.switch(T.gt(param,constant),  x, y)
boolean_and = lambda param, constant:  T.switch(x*y,  x, y)
boolean_or = lambda param, constant:  T.switch(x+y,  x, y)

total = lambda x: T.dot(x,numpy.ones((len(x))))
def substring(str,arg1):
        return str [0:arg1-1]


# Stack  of functions which will apply sequentially
functs = list()

args = dict() 
var_dict = {"var1" : 1 , "var2" : 2 ,"var3" : 3  }
f_dictPriority2 = { ">" : greater, "<" : less  }
f_dictPriority3 = { "Total of" : total }
f_dictPriority1 = { 'extract first % characters':substring }
f_dictPriority0 = { 'and': boolean_and, 'or' : boolean_or }

dictionary = {**f_dictPriority0, **f_dictPriority1,**f_dictPriority2, **f_dictPriority3}
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

#Parentheses pairing ({}[]()<>) issue
def evalParentheses(str):
  stack = []
  pushChars, popChars = "({", "})"
  # prerequisits
  
  i = 0
  for c in str :
    if c in pushChars :
      stack.append(c)
    elif c in popChars :

      if not len(stack) :
        return False
      else :
        stackTop = stack.pop()
        balancingBracket = pushChars[popChars.index(c)]
        if stackTop != balancingBracket :
          return False
    else :
      i +=1  
  return (not len(stack) ) or len(str) == i 

print( evalParentheses('345345'))


def find_args(str, funct_name):
    words = applyDelimeter(str, funct_name )
    new_words = []
    _new_words =''
    #_if length more then 2 concatunate arrays in place where parenthes are broken 
    if(len(words) > 2 ):
            i,j = 0,0
            for word in words:
                i += 1
                if ( evalParentheses(word) ) : 
                    j = i
                else : 
                    _new_words +=  word
            if( j > 0 ) :  
                   new_words.append(_new_words)     
                   new_words.append(words[j-1]) 
            words = new_words
    else:
    # Check if every element of of word has open an closed parenthes correct
        for word in words:
            if (not evalParentheses(word) ) : return []
    return words



def findFirstOpenParenthesesBlock(dictionary, str):
    start=str.find('{')
    if( start < 0 ): return str
    block =  re.search(r'{(.*)}', str).group(1)
    if( not block ): raise Exception( word + ' must have block of rules started with { and finished with }' )
    start=block.find('{')
    if( start > 0 ):
        # as soon first block found check if this block may be some function argument
        # check if string before this block match any functions from the dictionaty

        # check from left side from parentes '{ '
        block_prefix = str[0:start]
        for funct_word,value in dictionary.items():
            if( block_prefix.find(funct_word)>-1 ):
                new_blocks_pair = find_args(block_prefix, funct_word)
                if( new_blocks_pair  ): # create a first function
                        functs.append(value) 
                        block =  findFirstOpenParenthesesBlock(dictionary, new_blocks_pair[0])
                        break # stop left side recursion

            else:
                # check from right side from parentes '{ '
                for funct_word,value in dictionary.items():
                    if( block.find(funct_word)>-1 ):
                        new_blocks_pair = find_args(block, funct_word)
                        if( new_blocks_pair ): # create a second function
                                functs.append(value)
                                if( len(new_blocks_pair)>1 ):
                                    block =  findFirstOpenParenthesesBlock(dictionary, new_blocks_pair[0] )
                                    block =  findFirstOpenParenthesesBlock(dictionary, new_blocks_pair[1] )
                                else:
                                      block =  findFirstOpenParenthesesBlock(dictionary, new_blocks_pair[0] )
                                break # stop left side recursion
                               

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
print( find_args('Total of{ (CushionDB<30) and (CushionDB>34) or (Length <10000 )} < 56 ', '<'))
_words =  applyDelimeter('Total of{ (CushionDB<30) and (CushionDB>34) or (Length <10000 )} < 56 ', '<')
str = findFirstOpenParenthesesBlock (dictionary, str)
_words =  applyDelimeter(str, "and")
first_word_delemiterd =  applyDelimeters(_words[0])
#Check word by word is match with dictionaries' function

print(first_word_delemiterd )
print(functs)

print(applyDictionary(  dictionary , first_word_delemiterd ))


