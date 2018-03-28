import re
import theano, numpy
import theano.tensor as T
import xlrd

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
def words(str):
    delimiters = [' ','and','or','>', '<', 'not equal', '!=', '='] # .., ',' , '.' , '?' , ...
    return re.split('|'.join(delimiters), str)
def words_d(str, delimeter):
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

print(matchWord( words("How tuff and interesting to code this translator ! !") , "tuff") )

print( words(" Total((CushionDB<30)and(CushionDB>34))"))
print( words_d(" Total((CushionDB<30)and(CushionDB>34) and Length <10000 )", "and"))
print( matchWord ( words("How tuff and interesting to code this translator ! !") ,"<" ) )

# Simple algorithm to generate virtual operand

_words =  words_d(" Total((CushionDB<30)and(CushionDB>34) and Length <10000 )", "and")
print(_words)
# 1. Apply close/open parenthes rule and boolean operators 'or' && 'and'


string = ' fhgfg uyt kuyt uytkuytgyu Total ( CushionDB < 30 and CushionDB > 34 ) and ( Length <100 ) '


_words =  words_d(string, "and")


def applyDelimeters( str):
     pat = re.compile("([^,\(]*)\((.*?)\)")
    

     lst = [tuple(nws(item) for item in t) for t in pat.findall(str)]
     return lst

# normalize white space.  Replaces all runs of white space by a single space.
def nws(s):
     return " ".join(w for w in s.split())


# Default lamdas
less = lambda param, constant:  T.switch(T.lt(param,constant),  x, y)
greater = lambda param, constant:  T.switch(T.gt(param,constant),  x, y)
total = lambda x: T.dot(x,numpy.ones((len(x))))


functs = []
var_dict = {"var1" : 1 , "var2" : 2 ,"var3" : 3  }
f_dict1 = { ">" : greater, "<" : less  }
f_dict2 = { "Sum of" : total }

w, h = 10, 2;
args = [[0 for x in range(w)] for y in range(h)]


_and = applyDelimeters( string )

print( _and )

# print(lst) 
# 2. apply hiest prioriy operand ('and') to formed blocks 

def applyDictionary(dictionary, words): 
    applied = false

    for key, value in dictionary.iteritems():
      for index, word in enumerate(words):
        if ( word == key ) : 
            functs.append ()
            # check for functions argument . If function has two argument check for previouse arra element and nex element of array
            arg1 = words[index - 1]
            arg2 = words[index + 1]
            args[0][0]= arg1
            args[0][1]= arg1
            applied = true
    return applied


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

def _getOperandStr(str):
    # splist string to words
    # if operatorDictionary[word] follow positionByParam[i] then form oprand
    # then apply operand to parameter by evaluation
    operand = fireDictionaryFuncts(operator, wordsBeforeOperand, wordsAfterOperand)
    return operand

