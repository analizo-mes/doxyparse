"""Script to generate reports on translator classes from Doxygen sources.

  The main purpose of the script is to extract the information from sources
  related to internationalization (the translator classes). It uses the
  information to generate documentation (language.doc,
  translator_report.txt) from templates (language.tpl, maintainers.txt).
  
  Simply run the script without parameters to get the reports and
  documentation for all supported languages. If you want to generate the
  translator report only for some languages, pass their codes as arguments
  to the script. In that case, the language.doc will not be generated.
  Example:
      
    python translator.py en nl cz
  
  Originally, the script was written in Perl and was known as translator.pl.
  The last Perl version was dated 2002/05/21 (plus some later corrections)

  $Id$
  
                                         Petr Prikryl (prikrylp@skil.cz)
                               
  History:
  --------
  2002/05/21
   - This was the last Perl version. 
  2003/05/16
   - If the script is given list of languages, only the translator report
     is generated and only for those languages.
  2004/01/24
   - Total reimplementation just started: classes TrManager, and Transl.
  2004/02/05
   - First version that produces translator report. The documentation 
     in the language.doc is not generated yet.
  2004/02/10
   - First fully functional version that generates both the translator
     report and the documentation. It is a bit slower than the Perl version,
     but is much less tricky and much more flexible. It also solves some
     problems that were not solved by the Perl version. The translator report
     content should be more useful for developers.
  2004/02/11
   - Some tuning-up to provide more useful information.
  """                               

import os, re, sys, textwrap


def fill(s):
    """Returns string formated to the wrapped paragraph multiline string.
    
    Replaces whitespaces by one space and then uses he textwrap.fill()."""
    rexWS = re.compile(r'\s+')
    return textwrap.fill(rexWS.sub(' ', s))
    

class Transl:
    """One instance is build for each translator.
    
    The abbreviation of the source file--part after 'translator_'--is used as
    the identification of the object. The empty string is used for the
    abstract Translator class from translator.h. The other information is
    extracted from inside the source file."""
    
    def __init__(self, fname, manager):
        """Bind to the manager and initialize."""
        
        # Store the filename and the reference to the manager object.
        self.fname = fname
        self.manager = manager
        
        # The instance is responsible for loading the source file, so it checks
        # for its existence and quits if something goes wrong.
        if not os.path.isfile(fname):
            sys.stderr.write("\a\nFile '%s' not found!\n" % fname)
            sys.exit(1)
            
        # Initialize the other collected information.
        self.classId = None
        self.baseClassId = None
        self.readableStatus = None  # 'up-to-date', '1.2.3', '1.3', etc.
        self.status = None          # '', '1.2.03', '1.3.00', etc.
        self.lang = None            # like 'Brasilian'
        self.langReadable = None    # like 'Brasilian Portuguese'
        self.note = None            # like 'should be cleaned up'
        self.prototypeDic = {}      # uniPrototype -> prototype
        self.obsoleteMethods = None # list of prototypes to be removed
        self.missingMethods = None  # list of prototypes to be implemented
        self.implementedMethods = None  # list of implemented required methods
        self.adaptMinClass = None   # The newest adapter class that can be used
            
    def __tokenGenerator(self):
        """Generator that reads the file and yields tokens as 4-tuples.
        
        The tokens have the form (tokenId, tokenString, lineNo). The
        last returned token has the form ('eof', None, None). When trying
        to access next token afer that, the exception would be raised."""

        # Set the dictionary for recognizing tokenId for keywords, separators
        # and the similar categories. The key is the string to be recognized,
        # the value says its token identification.
        tokenDic = { 'class':     'class',
                     'const':     'const',
                     'public':    'public',
                     'protected': 'protected',
                     'private':   'private',
                     'static':    'static',
                     'virtual':   'virtual',
                     ':':         'colon',    
                     ';':         'semic',
                     ',':         'comma',
                     '[':         'lsqbra',   
                     ']':         'rsqbra',
                     '(':         'lpar',    
                     ')':         'rpar',
                     '{':         'lcurly',    
                     '}':         'rcurly',
                     '=':         'assign',
                     '*':         'star',
                     '&':         'amp',
                     '+':         'plus',
                     '-':         'minus',
                     '!':         'excl',
                     '?':         'qmark',
                     '<':         'lt',
                     '>':         'gt',
                     "'":         'quot',
                     '"':         'dquot',
                     '.':         'dot',
                     '%':         'perc',
                   }
        
        # Regular expression for recognizing identifiers.
        rexId = re.compile(r'^[a-zA-Z]\w*$')

        # Open the file for reading and extracting tokens until the eof.
        # Initialize the finite automaton.
        f = file(self.fname)
        lineNo = 0
        line = ''         # init -- see the pos initialization below
        linelen = 0       # init
        pos = 100         # init -- pos after the end of line
        status = 0     
        
        tokenId = None    # init
        tokenStr = ''     # init -- the characters will be appended.
        tokenLineNo = 0

        while status != 777:
            
            # Get the next character. Read next line first, if necessary.
            if pos < linelen:
                c = line[pos]
            else:
                lineNo += 1
                line = f.readline()
                linelen = len(line)
                pos = 0
                if line == '':   # eof
                    status = 777
                else:
                    c = line[pos]
                
            # Consume the character based on the status

            if status == 0:     # basic status
                
                # This is the initial status. If tokenId is set, yield the
                # token here and only here (except when eof is found).
                # Initialize the token variables after the yield.
                if tokenId:
                    # If it is an unknown item, it can still be recognized
                    # here. Keywords and separators are the example.
                    if tokenId == 'unknown': 
                        if tokenDic.has_key(tokenStr):
                            tokenId = tokenDic[tokenStr]
                        elif tokenStr.isdigit():
                            tokenId = 'num'
                        elif rexId.match(tokenStr):
                            tokenId = 'id'
                        else:
                            msg = '\aWarning: unknown token "' + tokenStr + '"'
                            msg += '\tfound on line %d' % tokenLineNo 
                            msg += 'in "' + self.fname + '".\n'
                            sys.stderr.write(msg)
                    
                    yield (tokenId, tokenStr, tokenLineNo)
                    tokenId = None
                    tokenStr = ''
                    tokenLineNo = 0 
                
                # Now process the character. When we just skip it (spaces),
                # stay in this status. All characters that will be part of
                # some token cause moving to the specific status. And only
                # when moving to the status == 0 (or the final state 777), 
                # the token is yielded. With respect to that the automaton
                # behaves as Moore's one (output bound to status). When 
                # collecting tokens, the automaton is the Mealy's one 
                # (actions bound to transitions).
                if c.isspace():
                    pass                 # just skip whitespace characters
                elif c == '/':           # Possibly comment starts here, but
                    tokenId = 'unknown'  # it could be only a slash in code.
                    tokenStr = c
                    tokenLineNo = lineNo
                    status = 1
                elif c == '#':
                    tokenId = 'preproc'  # preprocessor directive
                    tokenStr = c
                    tokenLineNo = lineNo
                    status = 5
                elif c == '"':           # string starts here
                    tokenId = 'string'
                    tokenStr = c
                    tokenLineNo = lineNo
                    status = 6
                elif c == "'":           # char literal starts here
                    tokenId = 'charlit'
                    tokenStr = c
                    tokenLineNo = lineNo
                    status = 8
                elif tokenDic.has_key(c):  # known one-char token 
                    tokenId = tokenDic[c]
                    tokenStr = c
                    tokenLineNo = lineNo
                    # stay in this state to yield token immediately
                else:
                    tokenId = 'unknown'  # totally unknown
                    tokenStr = c
                    tokenLineNo = lineNo
                    status = 333
                
                pos += 1                 # move position in any case
                    
            elif status == 1:            # possibly a comment
                if c == '/':             # ... definitely the C++ comment
                    tokenId = 'comment'
                    tokenStr += c
                    pos += 1            
                    status = 2
                elif c == '*':           # ... definitely the C comment
                    tokenId = 'comment'
                    tokenStr += c
                    pos += 1            
                    status = 3
                else:
                    status = 0           # unrecognized, don't move pos
                    
            elif status == 2:            # inside the C++ comment
                if c == '\n':            # the end of C++ comment
                    status = 0           # yield the token
                else:
                    tokenStr += c        # collect the C++ comment
                pos += 1
                
            elif status == 3:            # inside the C comment
                if c == '*':             # possibly the end of the C comment
                    tokenStr += c
                    status = 4
                else:
                    tokenStr += c        # collect the C comment
                pos += 1

            elif status == 4:            # possibly the end of the C comment
                if c == '/':             # definitely the end of the C comment
                    tokenStr += c
                    status = 0           # yield the token
                elif c == '*':           # more stars inside the comment
                    tokenStr += c
                else:
                    tokenStr += c        # this cannot be the end of comment
                    status = 3
                pos += 1

            elif status == 5:            # inside the preprocessor directive
                if c == '\n':            # the end of the preproc. command
                    status = 0           # yield the token
                else:
                    tokenStr += c        # collect the preproc
                pos += 1
                
            elif status == 6:            # inside the string
                if c == '\\':            # escaped char inside the string
                    tokenStr += c
                    status = 7
                elif c == '"':           # end of the string
                    tokenStr += c
                    status = 0
                else:
                    tokenStr += c        # collect the chars of the string
                pos += 1
                
            elif status == 7:            # escaped char inside the string
                tokenStr += c            # collect the char of the string
                status = 6
                pos += 1
                
            elif status == 8:            # inside the char literal
                tokenStr += c            # collect the char of the literal
                status = 9
                pos += 1
                
            elif status == 9:            # end of char literal expected
                if c == "'":             # ... and found
                    tokenStr += c
                    status = 0
                    pos += 1
                else:
                    tokenId = 'error'    # end of literal was expected
                    tokenStr += c
                    status = 0

            elif status == 333:          # start of the unknown token
                if c.isspace():
                    pos += 1
                    status = 0           # tokenId may be determined later
                elif tokenDic.has_key(c):  # separator, don't move pos
                    status = 0
                else:
                    tokenStr += c        # collect
                    pos += 1
                    
        # We should have finished in the final status. If some token 
        # have been extracted, yield it first.
        assert(status == 777)
        if tokenId:
            yield (tokenId, tokenStr, tokenLineNo)
            tokenId = None
            tokenStr = ''
            tokenLineNo = 0 

        # The file content is processed. Close the file. Then always yield 
        # the eof token.
        f.close()
        yield ('eof', None, None)
            
        
    def __collectClassInfo(self, tokenIterator):
        """Collect the information about the class and base class.
        
        The tokens including the opening left curly brace of the class are
        consumed."""
        
        status = 0  # initial state
        
        while status != 777:   # final state
            
            # Always assume that the previous tokens were processed. Get
            # the next one.
            tokenId, tokenStr, tokenLineNo = tokenIterator.next()

            # Process the token and never return back.
            if status == 0:    # waiting for the 'class' keyword.
                if tokenId == 'class':
                    status = 1
                    
            elif status == 1:  # expecting the class identification
                if tokenId == 'id':
                    self.classId = tokenStr
                    status = 2
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                
            elif status == 2:  # expecting the curly brace or base class info
                if tokenId == 'lcurly':
                    status = 777        # correctly finished
                elif tokenId == 'colon':
                    status = 3
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 3:  # expecting the 'public' in front of base class id
                if tokenId == 'public':
                    status = 4
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                
            elif status == 4:  # expecting the base class id
                if tokenId == 'id':
                    self.baseClassId = tokenStr
                    status = 5
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                
            elif status == 5:  # expecting the curly brace and quitting
                if tokenId == 'lcurly':
                    status = 777        # correctly finished
                elif tokenId == 'comment':
                    pass
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                
        # Extract the status of the TranslatorXxxx class. The readable form
        # will be used in reports the status form is a string that can be
        # compared lexically (unified length, padding with zeros, etc.).
        if self.baseClassId:
            lst = self.baseClassId.split('_')
            if lst[0] == 'Translator':
                self.readableStatus = 'up-to-date'
                self.status = ''
            elif lst[0] == 'TranslatorAdapter':
                self.status = lst[1] + '.' + lst[2]
                self.readableStatus = self.status
                if len(lst) > 3:        # add the last part of the number
                    self.status += '.' + ('%02d' % int(lst[3]))
                    self.readableStatus += '.' + lst[3]
                else:
                    self.status += '.00'
            elif lst[0] == 'TranslatorEnglish':
                # Obsolete or Based on English.
                if self.classId[-2:] == 'En':
                    self.readableStatus = 'English based'
                    self.status = 'En'
                else:
                    self.readableStatus = 'obsolete'
                    self.status = '0.0.00'
                    
            # Check whether status was set, or set 'strange'.
            if self.status == None: 
                self.status = 'strange'
            if not self.readableStatus: 
                self.readableStatus = 'strange'
                
            # Extract the name of the language and the readable form.
            self.lang = self.classId[10:]  # without 'Translator'
            if self.lang == 'Brazilian':
                self.langReadable = 'Brazilian Portuguese'
            elif self.lang == 'Chinesetraditional':
                self.langReadable = 'Chinese Traditional'
            else:
                self.langReadable = self.lang
                
                

    def __unexpectedToken(self, status, tokenId, tokenLineNo):
        """Reports unexpected token and quits with exit code 1."""
    
        import inspect
        calledFrom = inspect.stack()[1][3]
        msg = "\a\nUnexpected token '%s' on the line %d in '%s'.\n"
        msg = msg % (tokenId, tokenLineNo, self.fname)
        msg += 'status = %d in %s()\n' % (status, calledFrom)
        sys.stderr.write(msg)
        sys.exit(1)
        
                
    def collectPureVirtualPrototypes(self):
        """Returns dictionary 'unified prototype' -> 'full prototype'.

        The method is expected to be called only for the translator.h. It
        extracts only the pure virtual method and build the dictionary where
        key is the unified prototype without argument identifiers."""
        
        # Prepare empty dictionary that will be returned.
        resultDic = {}
        
        # Start the token generator which parses the class source file.
        tokenIterator = self.__tokenGenerator()

        # Collect the class and the base class identifiers.
        self.__collectClassInfo(tokenIterator)
        assert(self.classId == 'Translator')
        
        # Let's collect readable form of the public virtual pure method
        # prototypes in the readable form -- as defined in translator.h.
        # Let's collect also unified form of the same prototype that omits
        # everything that can be omitted, namely 'virtual' and argument
        # identifiers.
        prototype = ''    # readable prototype (with everything)
        uniPrototype = '' # unified prototype (without arg. identifiers)
        
        # Collect the pure virtual method prototypes. Stop on the closing
        # curly brace followed by the semicolon (end of class).
        status = 0
        curlyCnt = 0      # counter for the level of curly braces

        # Loop until the final state 777 is reached. The errors are processed
        # immediately. In this implementation, it always quits the application.
        while status != 777:     
            
            # Get the next token.
            tokenId, tokenStr, tokenLineNo = tokenIterator.next()
            
            if status == 0:      # waiting for 'public:'
                if tokenId == 'public':
                    status = 1
                
            elif status == 1:    # colon after the 'public'
                if tokenId == 'colon':
                    status = 2
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                
            elif status == 2:    # waiting for 'virtual'
                if tokenId == 'virtual':
                    prototype = tokenStr  # but not to unified prototype
                    status = 3
                elif tokenId == 'comment':
                    pass
                elif tokenId == 'rcurly':
                    status = 11         # expected end of class
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 3:    # return type of the method expected
                if tokenId == 'id':
                    prototype += ' ' + tokenStr
                    uniPrototype = tokenStr  # start collecting the unified prototype
                    status = 4
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 4:    # method identifier expected
                if tokenId == 'id':
                    prototype += ' ' + tokenStr
                    uniPrototype += ' ' + tokenStr
                    status = 5
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 5:    # left bracket of the argument list expected
                if tokenId == 'lpar':
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 6
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 6:    # collecting arguments of the method
                if tokenId == 'rpar':
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 7
                elif tokenId == 'const':
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 12
                elif tokenId == 'id':           # type identifier
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 13
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 7:    # assignment expected or left curly brace
                if tokenId == 'assign':
                    status = 8
                elif tokenId == 'lcurly':
                    curlyCnt = 1      # method body entered 
                    status = 10
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 8:    # zero expected
                if tokenId == 'num' and tokenStr == '0':
                    status = 9
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 9:    # after semicolon, produce the dic item
                if tokenId == 'semic':
                    assert(not resultDic.has_key(uniPrototype))
                    resultDic[uniPrototype] = prototype
                    status = 2
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 10:   # consuming the body of the method
                if tokenId == 'rcurly':
                    curlyCnt -= 1
                    if curlyCnt == 0:
                        status = 2     # body consumed
                elif tokenId == 'lcurly':
                    curlyCnt += 1
                        
            elif status == 11:   # probably the end of class
                if tokenId == 'semic':
                    status = 777
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 12:   # type id for argument expected
                if tokenId == 'id':
                    prototype += ' ' + tokenStr
                    uniPrototype += ' ' + tokenStr
                    status = 13
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 13:   # namespace qualification or * or & expected
                if tokenId == 'colon':        # was namespace id
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 14
                elif tokenId == 'star' or tokenId == 'amp':  # pointer or reference
                    prototype += ' ' + tokenStr
                    uniPrototype += ' ' + tokenStr
                    status = 16
                elif tokenId == 'id':         # argument identifier
                    prototype += ' ' + tokenStr
                    # don't put this into unified prototype
                    status = 17
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 14:   # second colon for namespace:: expected
                if tokenId == 'colon':        
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 15
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 15:   # type after namespace:: expected
                if tokenId == 'id':        
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 13
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 16:   # argument identifier expected
                if tokenId == 'id':        
                    prototype += ' ' + tokenStr
                    # don't put this into unified prototype
                    status = 17
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 17:   # comma or ')' after argument identifier expected
                if tokenId == 'comma':        
                    prototype += ', '
                    uniPrototype += ', '
                    status = 6
                elif tokenId == 'rpar':
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 7
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
 
        # Eat the rest of the source to cause closing the file.
        while tokenId != 'eof':
            tokenId, tokenStr, tokenLineNo = tokenIterator.next()
            
        # Return the resulting dictionary with 'uniPrototype -> prototype'.
        return resultDic
            
        
    def __collectPublicMethodPrototypes(self, tokenIterator):    
        """Collects prototypes of public methods and fills self.prototypeDic.
        
        The dictionary is filled by items: uniPrototype -> prototype. 
        The method is expected to be called only for TranslatorXxxx classes,
        i.e. for the classes that implement translation to some language.
        It assumes that the openning curly brace of the class was already
        consumed. The source is consumed until the end of the class. 
        The caller should consume the source until the eof to cause closing 
        the source file."""
        
        assert(self.classId != 'Translator')
        assert(self.baseClassId != None)

        # The following finite automaton slightly differs from the one
        # inside self.collectPureVirtualPrototypes(). It produces the
        # dictionary item just after consuming the body of the method
        # (transition from from state 10 to state 2). It also does not allow
        # definitions of public pure virtual methods, except for
        # TranslatorAdapterBase (states 8 and 9). Argument identifier inside
        # method argument lists can be omitted or commented.
        #
        # Let's collect readable form of all public method prototypes in 
        # the readable form -- as defined in the source file.
        # Let's collect also unified form of the same prototype that omits
        # everything that can be omitted, namely 'virtual' and argument
        # identifiers.
        prototype = ''    # readable prototype (with everything)
        uniPrototype = '' # unified prototype (without arg. identifiers)
        
        # Collect the method prototypes. Stop on the closing
        # curly brace followed by the semicolon (end of class).
        status = 0
        curlyCnt = 0      # counter for the level of curly braces

        # Loop until the final state 777 is reached. The errors are processed
        # immediately. In this implementation, it always quits the application.
        while status != 777:     
            
            # Get the next token.
            tokenId, tokenStr, tokenLineNo = tokenIterator.next()
            
            if status == 0:      # waiting for 'public:'
                if tokenId == 'public':
                    status = 1
                elif tokenId == 'eof':  # non-public things until the eof
                    status = 777
                
            elif status == 1:    # colon after the 'public'
                if tokenId == 'colon':
                    status = 2
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                
            elif status == 2:    # waiting for 'virtual' (can be omitted)
                if tokenId == 'virtual':
                    prototype = tokenStr  # but not to unified prototype
                    status = 3
                elif tokenId == 'id':     # 'virtual' was omitted
                    prototype = tokenStr
                    uniPrototype = tokenStr  # start collecting the unified prototype
                    status = 4
                elif tokenId == 'comment':
                    pass
                elif tokenId == 'protected' or tokenId == 'private':
                    status = 0
                elif tokenId == 'rcurly':
                    status = 11         # expected end of class
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 3:    # return type of the method expected
                if tokenId == 'id':
                    prototype += ' ' + tokenStr
                    uniPrototype = tokenStr  # start collecting the unified prototype
                    status = 4
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 4:    # method identifier expected
                if tokenId == 'id':
                    prototype += ' ' + tokenStr
                    uniPrototype += ' ' + tokenStr
                    status = 5
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 5:    # left bracket of the argument list expected
                if tokenId == 'lpar':
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 6
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 6:    # collecting arguments of the method
                if tokenId == 'rpar':
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 7
                elif tokenId == 'const':
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 12
                elif tokenId == 'id':           # type identifier
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 13
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 7:    # left curly brace expected 
                if tokenId == 'lcurly':
                    curlyCnt = 1      # method body entered 
                    status = 10
                elif tokenId == 'comment':
                    pass
                elif tokenId == 'assign': # allowed only for TranslatorAdapterBase
                    assert(self.classId == 'TranslatorAdapterBase')
                    status = 8
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 8:    # zero expected (TranslatorAdapterBase)
                assert(self.classId == 'TranslatorAdapterBase')
                if tokenId == 'num' and tokenStr == '0':
                    status = 9
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                    
            elif status == 9:    # after semicolon (TranslatorAdapterBase)
                assert(self.classId == 'TranslatorAdapterBase')
                if tokenId == 'semic':
                    status = 2
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)

            elif status == 10:   # consuming the body of the method, then dic item
                if tokenId == 'rcurly':
                    curlyCnt -= 1
                    if curlyCnt == 0:
                        # Insert new dictionary item.
                        assert(not self.prototypeDic.has_key(uniPrototype))
                        self.prototypeDic[uniPrototype] = prototype
                        status = 2     # body consumed
                elif tokenId == 'lcurly':
                    curlyCnt += 1
            elif status == 11:   # probably the end of class
                if tokenId == 'semic':
                    status = 777
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 12:   # type id for argument expected
                if tokenId == 'id':
                    prototype += ' ' + tokenStr
                    uniPrototype += ' ' + tokenStr
                    status = 13
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 13:   # :: or * or & or id or ) expected
                if tokenId == 'colon':        # was namespace id
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 14
                elif tokenId == 'star' or tokenId == 'amp':  # pointer or reference
                    prototype += ' ' + tokenStr
                    uniPrototype += ' ' + tokenStr
                    status = 16
                elif tokenId == 'id':         # argument identifier
                    prototype += ' ' + tokenStr
                    # don't put this into unified prototype
                    status = 17
                elif tokenId == 'comment':    # probably commented-out identifier
                    prototype += tokenStr
                elif tokenId == 'rpar':
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 7
                elif tokenId == 'comma':        
                    prototype += ', '
                    uniPrototype += ', '
                    status = 6
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 14:   # second colon for namespace:: expected
                if tokenId == 'colon':        
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 15
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 15:   # type after namespace:: expected
                if tokenId == 'id':        
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 13
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 16:   # argument identifier or ) expected
                if tokenId == 'id':        
                    prototype += ' ' + tokenStr
                    # don't put this into unified prototype
                    status = 17
                elif tokenId == 'rpar':
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 7
                elif tokenId == 'comment':
                    prototype += tokenStr
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
            elif status == 17:   # comma or ')' after argument identifier expected
                if tokenId == 'comma':        
                    prototype += ', '
                    uniPrototype += ', '
                    status = 6
                elif tokenId == 'rpar':
                    prototype += tokenStr
                    uniPrototype += tokenStr
                    status = 7
                else:
                    self.__unexpectedToken(status, tokenId, tokenLineNo)
                   
        

    def collectAdapterPrototypes(self):
        """Returns the dictionary of prototypes implemented by adapters.
        
        It is created to process the translator_adapter.h. The returned 
        dictionary has the form: unifiedPrototype -> (version, classId)
        thus by looking for the prototype, we get the information what is 
        the newest (least adapting) adapter that is sufficient for 
        implementing the method."""            

        # Start the token generator which parses the class source file.
        assert(os.path.split(self.fname)[1] == 'translator_adapter.h')
        tokenIterator = self.__tokenGenerator()

        # Get the references to the involved dictionaries.
        reqDic = self.manager.requiredMethodsDic

        # Create the empty dictionary that will be returned.
        adaptDic = {}
        
        
        # Loop through the source of the adapter file until no other adapter
        # class is found.
        while True:
            try:
                # Collect the class and the base class identifiers.
                self.__collectClassInfo(tokenIterator)

                # Extract the comparable version of the adapter class.
                # Note: The self.status as set by self.__collectClassInfo()
                # contains similar version, but is related to the base class,
                # not to the class itself.
                lst = self.classId.split('_')
                version = ''
                if lst[0] == 'TranslatorAdapter': # TranslatorAdapterBase otherwise
                    version = lst[1] + '.' + lst[2]
                    if len(lst) > 3:        # add the last part of the number
                        version += '.' + ('%02d' % int(lst[3]))
                    else:
                        version += '.00'
                
                # Collect the prototypes of implemented public methods.
                self.__collectPublicMethodPrototypes(tokenIterator)
        
                # For the required methods, update the dictionary of methods 
                # implemented by the adapter.
                for protoUni in self.prototypeDic:
                    if reqDic.has_key(protoUni):
                        # This required method will be marked as implemented
                        # by this adapter class. This implementation assumes 
                        # that newer adapters do not reimplement any required
                        # methods already implemented by older adapters.
                        assert(not adaptDic.has_key(protoUni))
                        adaptDic[protoUni] = (version, self.classId)

                # Clear the dictionary object and the information related
                # to the class as the next adapter class is to be processed.
                self.prototypeDic.clear()
                self.classId = None
                self.baseClassId = None
                
            except StopIteration:
                break

        # Return the result dictionary.
        return adaptDic    

        
    def processing(self):
        """Processing of the source file -- only for TranslatorXxxx classes."""            

        # Start the token generator which parses the class source file.
        tokenIterator = self.__tokenGenerator()

        # Collect the class and the base class identifiers.
        self.__collectClassInfo(tokenIterator)
        assert(self.classId != 'Translator')
        assert(self.classId[:17] != 'TranslatorAdapter')
        
        # Collect the prototypes of implemented public methods.
        self.__collectPublicMethodPrototypes(tokenIterator)
        
        # Eat the rest of the source to cause closing the file.
        while True:
            try:
                t = tokenIterator.next()
            except StopIteration:
                break

        # Shorthands for the used dictionaries.
        reqDic = self.manager.requiredMethodsDic
        adaptDic = self.manager.adaptMethodsDic
        myDic = self.prototypeDic
        
        # Build the list of obsolete methods.
        self.obsoleteMethods = []
        for p in myDic:
            if not reqDic.has_key(p):
                self.obsoleteMethods.append(p)
        
        # Build the list of missing methods and the list of implemented
        # required methods.
        self.missingMethods = []
        self.implementedMethods = []
        for p in reqDic:
            if myDic.has_key(p):
                self.implementedMethods.append(p)
            else:
                self.missingMethods.append(p)

        # Check whether adapter must be used or suggest the newest one.
        # Change the status and set the note accordingly.
        if self.baseClassId != 'Translator':
            if not self.missingMethods: 
                self.note = 'Change the base class to Translator.'
                self.status = ''
                self.readableStatus = 'up-to-date'
            elif self.baseClassId != 'TranslatorEnglish':
                # The translator uses some of the adapters.
                # Look at the missing methods and check what adapter 
                # implements them. Remember the one with the lowest version.
                adaptMinVersion = '9.9.99'
                adaptMinClass = 'TranslatorAdapter_9_9_99'
                for uniProto in self.missingMethods:
                    if adaptDic.has_key(uniProto):
                        version, cls = adaptDic[uniProto]
                        if version < adaptMinVersion:
                            adaptMinVersion = version
                            adaptMinClass = cls
                
                # Test against the current status -- preserve the self.status.
                # Possibly, the translator implements enough methods to 
                # use some newer adapter.
                status = self.status
                    
                # If the version of the used adapter is smaller than
                # the required, set the note and update the status as if
                # the newer adapter was used.
                if adaptMinVersion > status:
                    self.note = 'Change the base class to %s.' % adaptMinClass
                    self.status = adaptMinVersion
                    self.adaptMinClass = adaptMinClass
                    self.readableStatus = adaptMinVersion # simplified
        
        # If everything seems OK, but there are obsolete methods, set 
        # the note to clean-up source. This note will be used only when
        # the previous code did not set another note (priority).
        if not self.note and self.status == '' and self.obsoleteMethods:
            self.note = 'Remove the obsolete methods (never used).'
                
    def report(self, fout):
        """Returns the report part for the source as a multiline string.
        
        No output for up-to-date translators without problem."""
        
        # If there is nothing to report, return immediately.
        if self.status == '' and not self.note:
            return
            
        # Report the number of not implemented methods.
        fout.write('\n\n\n')
        fout.write(self.classId + '   (' + self.baseClassId + ')')
        if self.missingMethods:
            fout.write('  %d' % len(self.missingMethods))
            fout.write(' methods to implement')
        fout.write('\n' + '-' * len(self.classId))
        
        # Write the info about the implemented required methods.
        fout.write('\n\n  Implements %d' % len(self.implementedMethods))
        fout.write(' of the required methods.')
        
        # Report the missing method, but only when it is not English-based
        # translator.
        if self.missingMethods and self.status != 'En':
            fout.write('\n\n  Missing methods (should be implemented):\n')
            reqDic = self.manager.requiredMethodsDic
            for p in self.missingMethods:
                fout.write('\n    ' + reqDic[p])

        # Always report obsolete methods.
        if self.obsoleteMethods:
            fout.write('\n\n  Obsolete methods (should be removed, never used):\n')
            myDic = self.prototypeDic
            for p in self.obsoleteMethods:
                fout.write('\n    ' + myDic[p])

        # For English-based translator, report the implemented methods.
        if self.status == 'En' and self.implementedMethods:
            fout.write('\n\n  This English-based translator implements ')
            fout.write('the following methods:\n')
            reqDic = self.manager.requiredMethodsDic
            for p in self.implementedMethods:
                fout.write('\n    ' + reqDic[p])

                
    def getmtime(self):
        """Returns the last modification time of the source file."""
        assert(os.path.isfile(self.fname))
        return os.path.getmtime(self.fname)
        
                
class TrManager:
    """Collects basic info and builds subordinate Transl objects."""
    
    def __init__(self):                                
        """Determines paths, creates and initializes structures.
        
        The arguments of the script may explicitly say what languages should 
        be processed. Write the two letter identifications that are used
        for composing the source filenames, so...
            
            python translator.py cz
            
        this will process only translator_cz.h source.
        """
        
        # Determine the path to the script and the absolute path to the
        # Doxygen's root subdirectory.
        self.script = os.path.abspath(sys.argv[0]) 
        self.script_path, self.script_name = os.path.split(self.script) 
        self.script_path = os.path.abspath(self.script_path)
        self.doxy_path = os.path.abspath(os.path.join(self.script_path, '..'))    
        
        # Get the explicit arguments of the script.
        self.script_argLst = sys.argv[1:]
        
        # Build the path names based on the Doxygen's root knowledge.
        self.doc_path = os.path.join(self.doxy_path, 'doc')
        self.src_path = os.path.join(self.doxy_path, 'src')
        
        # Create the empty dictionary for Transl object identitied by the
        # class identifier of the translator. 
        self.__translDic = {}

        # Create the None dictionary of required methods. The key is the
        # unified prototype, the value is the full prototype. Set inside
        # the self.__build().
        self.requiredMethodsDic = None
        
        # Create the empty dictionary that says what method is implemented
        # by what adapter.
        self.adaptMethodsDic = {}
        
        # The last modification time will capture the modification of this
        # script, of the translator.h, of the translator_adapter.h (see the 
        # self.__build() for the last two) of all the translator_xx.h files
        # and of the template for generating the documentation. So, this
        # time can compared with modification time of the generated 
        # documentation to decide, whether the doc should be re-generated.
        self.lastModificationTime = os.path.getmtime(self.script)
        
        # Set the names of the translator report text file, of the template
        # for generating "Internationalization" document, for the generated
        # file itself, and for the maintainers list.
        self.translatorReportFileName = 'translator_report.txt'
        self.maintainersFileName = 'maintainers.txt'
        self.languageTplFileName = 'language.tpl'
        self.languageDocFileName = 'language.doc'
        
        # The information about the maintainers will be stored 
        # in the dictionary with the following name.
        self.__maintainersDic = None
        
        # Define the other used structures and variables for information.
        self.langLst = None                   # including English based
        self.supportedLangReadableStr = None  # coupled En-based as a note
        self.numLang = None                   # excluding coupled En-based
        self.doxVersion = None                # Doxygen version
        
        # Build objects where each one is responsible for one translator.
        self.__build()
        
        
    def __build(self):
        """Find the translator files and build the objects for translators."""
        
        # The translator.h must exist (the Transl object will check it),
        # create the object for it and let it build the dictionary of
        # required methods.
        tr = Transl(os.path.join(self.src_path, 'translator.h'), self)
        self.requiredMethodsDic = tr.collectPureVirtualPrototypes()
        tim = tr.getmtime()
        if tim > self.lastModificationTime:
            self.lastModificationTime = tim
        
        # The translator_adapter.h must exist (the Transl object will check it),
        # create the object for it and store the reference in the dictionary.
        tr = Transl(os.path.join(self.src_path, 'translator_adapter.h'), self)
        self.adaptMethodsDic = tr.collectAdapterPrototypes()
        tim = tr.getmtime()
        if tim > self.lastModificationTime:
            self.lastModificationTime = tim
            
        # Create the list of the filenames with language translator sources.
        # If the explicit arguments of the script were typed, process only
        # those files.
        if self.script_argLst:
            lst = ['translator_' + x + '.h' for x in self.script_argLst]
            for fname in lst:
                if not os.path.isfile(os.path.join(self.src_path, fname)):
                    sys.stderr.write("\a\nFile '%s' not found!\n" % fname)
                    sys.exit(1)
        else:                    
            lst = os.listdir(self.src_path)
            lst = filter(lambda x: x[:11] == 'translator_'
                                   and x[-2:] == '.h'
                                   and x != 'translator_adapter.h', lst)
    
        # Build the object for the translator_xx.h files, and process the 
        # content of the file. Then insert the object to the dictionary
        # accessed via classId.
        for fname in lst:
            fullname = os.path.join(self.src_path, fname)
            tr = Transl(fullname, self)
            tr.processing()
            assert(tr.classId != 'Translator')
            self.__translDic[tr.classId] = tr

        # Extract the global information of the processed info. 
        self.__extractProcessedInfo()
        
    
    def __extractProcessedInfo(self):
        """Build lists and strings of the processed info."""        

        # Build the auxiliary list with strings compound of the status,
        # readable form of the language, and classId.
        statLst = []
        for obj in self.__translDic.values():
            assert(obj.classId != 'Translator')
            s = obj.status + '|' + obj.langReadable + '|' + obj.classId
            statLst.append(s)
        
        # Sort the list and extract the object identifiers (classId's) for
        # the up-to-date translators and English-based translators.
        statLst.sort()
        self.upToDateIdLst = [x.split('|')[2] for x in statLst if x[0] == '|']
        self.EnBasedIdLst = [x.split('|')[2] for x in statLst if x[:2] == 'En']

        # Reverse the list and extract the TranslatorAdapter based translators.
        statLst.reverse()
        self.adaptIdLst = [x.split('|')[2] for x in statLst if x[0].isdigit()]

        # Build the list of tuples that contain (langReadable, obj). 
        # Sort it by readable name.
        self.langLst = []
        for obj in self.__translDic.values():
            self.langLst.append((obj.langReadable, obj))
        self.langLst.sort(lambda a, b: cmp(a[0], b[0]))
            
        # Create the list with readable language names. If the language has
        # also the English-based version, modify the item by appending
        # the note. Number of the supported languages is equal to the length
        # of the list.
        langReadableLst = []
        for name, obj in self.langLst:
            if obj.status == 'En': continue
            
            # Append the 'En' to the classId to possibly obtain the classId
            # of the English-based object. If the object exists, modify the
            # name for the readable list of supported languages.
            classIdEn = obj.classId + 'En'
            if self.__translDic.has_key(classIdEn):
                name += ' (+En)'
            
            # Append the result name of the language, possibly with note.
            langReadableLst.append(name)

        # Create the multiline string of readable language names, 
        # with punctuation, wrapped to paragraph.
        if len(langReadableLst) == 1:
            s = langReadableLst[0]
        elif len(langReadableLst) == 2:
            s = ' and '.join(langReadableLst) 
        else:    
            s = ', '.join(langReadableLst[:-1]) + ', and ' 
            s += langReadableLst[-1]
        
        self.supportedLangReadableStr = fill(s + '.') 

        # Find the number of the supported languages. The English based
        # languages are not counted if the non-English based also exists.
        self.numLang = len(self.langLst)
        for name, obj in self.langLst:
            if obj.status == 'En':
                classId = obj.classId[:-2]
                if self.__translDic.has_key(classId):
                    self.numLang -= 1    # the couple will be counted as one
        
        # Extract the version of Doxygen.
        f = file(os.path.join(self.doxy_path, 'VERSION'))
        self.doxVersion = f.readline().strip()
        f.close()
        
        # Update the last modification time.
        for tr in self.__translDic.values():
            tim = tr.getmtime()
            if tim > self.lastModificationTime:
                self.lastModificationTime = tim
                
        
        
    def generateTranslatorReport(self):
        """Generates the translator report."""

        output = os.path.join(self.doc_path, self.translatorReportFileName)
        
        # Open the textual report file for the output.
        f = file(output, 'w')

        # Output the information about the version.
        f.write('(' + self.doxVersion + ')\n\n')
        
        # Output the information about the number of the supported languages
        # and the list of the languages, or only the note about the explicitly
        # given languages to process.
        if self.script_argLst:
            f.write('The report was generated for the following, explicitly')
            f.write(' identified languages:\n\n')
            f.write(self.supportedLangReadableStr + '\n\n')
        else:
            f.write('Doxygen supports the following ')
            f.write(str(self.numLang))
            f.write(' languages (sorted alphabetically):\n\n')
            f.write(self.supportedLangReadableStr + '\n\n')
        
            # Write the summary about the status of language translators (how 
            # many translators) are up-to-date, etc.
            s = 'Of them, %d translators are up-to-date, ' % len(self.upToDateIdLst)
            s += '%d translators are based on some adapter class, ' % len(self.adaptIdLst)  
            s += 'and %d are English based.' % len(self.EnBasedIdLst)
            f.write(fill(s) + '\n\n')
        
        # Write the list of up-to-date translator classes.
        if self.upToDateIdLst:
            s = '''The following translator classes are up-to-date (sorted
                alphabetically). This means that they derive from the
                Translator class and they implement all %d of the required
                methods. Anyway, there still may be some details listed even 
                for them. Please, see the details for them:'''
            s = s % len(self.requiredMethodsDic)    
            f.write('-' * 70 + '\n')
            f.write(fill(s) + '\n\n')
            for x in self.upToDateIdLst:
                obj = self.__translDic[x]
                f.write('  ' + obj.classId)
                if obj.note:
                    f.write(' -- ' + obj.note)
                f.write('\n')

        # Write the list of the adapter based classes. The very obsolete
        # translators that derive from TranslatorEnglish are included.
        if self.adaptIdLst:
            s = '''The following translator classes need some maintenance 
                (the most obsolete at the end). The other info shows the
                estimation of Doxygen version when the class was last
                updated and number of methods that must be implemented to
                become up-to-date:'''
            f.write('\n' + '-' * 70 + '\n')
            f.write(fill(s) + '\n\n')
    
            # Find also whether some adapter classes may be removed.
            adaptMinVersion = '9.9.99'
            
            for x in self.adaptIdLst:
                obj = self.__translDic[x]
                f.write('  %-30s' % obj.classId)
                f.write('  %-6s' % obj.readableStatus)
                f.write('\t%2d methods to implement' % len(obj.missingMethods))
                if obj.note:
                    f.write('\n\tNote: ' + obj.note + '\n')
                f.write('\n')
                
                # Check the level of required adapter classes.
                if obj.status != '0.0.00' and obj.status < adaptMinVersion:
                    adaptMinVersion = obj.status
                
            # Set the note if some old translator adapters are not needed 
            # any more.
            for version, adaptClassId in self.adaptMethodsDic.values():
                if version < adaptMinVersion:
                    f.write('\nNote: The %s class ' % adaptClassId)
                    f.write('is not used and can be removed.\n')
                
        # Write the list of the English-based classes.
        if self.EnBasedIdLst:
            s = '''The following translator classes derive directly from the 
                TranslatorEnglish. The class identifier has the suffix 'En' 
                that says that this is intentional. Usually, there is also 
                a non-English based version of the translator for 
                the language:'''
            f.write('\n' + '-' * 70 + '\n')
            f.write(fill(s) + '\n\n')
    
            for x in self.EnBasedIdLst:
                obj = self.__translDic[x]
                f.write('  ' + obj.classId)
                f.write('\timplements %d methods' % len(obj.implementedMethods))
                if obj.note:
                    f.write(' -- ' + obj.note)
                f.write('\n')
            
        # Write the details for the translators.
        f.write('\n' + '=' * 70)
        f.write('\nDetails for translators (classes sorted alphabetically):\n')
        
        cls = self.__translDic.keys()
        cls.sort()
        
        for c in cls:
            obj = self.__translDic[c]
            assert(obj.classId != 'Translator') 
            obj.report(f)
                
        # Close the report file.        
        f.close()
        
            


    def __loadMaintainers(self):
        """Load and process the file with the maintainers.
        
        Fills the dictionary classId -> [(name, e-mail), ...]."""
        
        fname = os.path.join(self.script_path, self.maintainersFileName)

        # Include the maintainers file to the checked group of files with
        # respect to the modification time.
        tim = os.path.getmtime(fname)
        if tim > self.lastModificationTime:
            self.lastModificationTime = tim
        
        # Process the content of the maintainers file.
        f = file(fname)
        inside = False  # inside the record for the language
        lineReady = True
        classId = None
        maintainersLst = None
        self.__maintainersDic = {}
        while lineReady:
            line = f.readline()            # next line
            lineReady = line != ''         # when eof, then line == ''
                
            line = line.strip()            # eof should also behave as separator
            if line != '' and line[0] == '%':    # skip the comment line
                continue           
        
            if not inside:                 # if outside of the record
                if line != '':             # should be language identifier
                    classId = line
                    maintainersLst = []
                    inside = True
                # Otherwise skip empty line that do not act as separators.
                
            else:                          # if inside the record                       
                if line == '':             # separator found
                    inside = False
                else:
                    # If it is the first maintainer, create the empty list.
                    if not self.__maintainersDic.has_key(classId):
                        self.__maintainersDic[classId] = []
                    
                    # Split the information about the maintainer and append
                    # the tuple.
                    lst = line.split(':', 1)
                    assert(len(lst) == 2)
                    t = (lst[0].strip(), lst[1].strip())
                    self.__maintainersDic[classId].append(t)
        f.close()            
                    
    def generateLanguageDoc(self):
        """Checks the modtime of files and generates language.doc."""
        self.__loadMaintainers()
        
        # Check the last modification time of the template file. It is the
        # last file from the group that decide whether the documentation
        # should or should not be generated.
        fTplName = os.path.join(self.script_path, self.languageTplFileName)
        tim = os.path.getmtime(fTplName)
        if tim > self.lastModificationTime:
            self.lastModificationTime = tim

        # If the generated documentation exists and is newer than any of 
        # the source files from the group, do not generate it and quit 
        # quietly.
        fDocName = os.path.join(self.doc_path, self.languageDocFileName)
        if os.path.isfile(fDocName): 
            if os.path.getmtime(fDocName) > self.lastModificationTime:
                return
            
        # The document or does not exist or is older than some of the
        # sources. It must be generated again.
        #
        # Read the template of the documentation, and remove the first
        # attention lines.
        f = file(fTplName)
        line = f.readline()
        while line[0] != '/':
            line = f.readline()
        doctpl = line + f.read()    
        f.close()

        # Fill the tplDic by symbols that will be inserted into the 
        # document template.
        tplDic = {}
        
        s = 'Do not edit this file. It was generated by the %s script.' % self.script_name
        tplDic['editnote'] = s
        
        tplDic['doxVersion'] = self.doxVersion
        tplDic['supportedLangReadableStr'] = self.supportedLangReadableStr 
        tplDic['translatorReportFileName'] = self.translatorReportFileName

        ahref = '<a href="../doc/' + self.translatorReportFileName
        ahref += '"\n><code>doxygen/doc/'  + self.translatorReportFileName
        ahref += '</code></a>'
        tplDic['translatorReportLink'] = ahref
        tplDic['numLangStr'] = str(self.numLang)
        
        # Define templates for HTML table parts of the documentation.
        htmlTableTpl = '''\
            \\htmlonly
            <table align=center cellspacing=0 cellpadding=0 border=0>
            <tr bgcolor="#000000">
            <td>
              <table cellspacing=1 cellpadding=2 border=0>
              <tr bgcolor="#4040c0">
              <td ><b><font size=+1 color="#ffffff"> Language </font></b></td>
              <td ><b><font size=+1 color="#ffffff"> Maintainer </font></b></td>
              <td ><b><font size=+1 color="#ffffff"> Contact address </font>
                      <font size=-2 color="#ffffff">(remove the NOSPAM.)</font></b></td>
              <td ><b><font size=+1 color="#ffffff"> Status </font></b></td>
              </tr>
              <!-- table content begin -->
            %s
              <!-- table content end -->
              </table>
            </td>
            </tr>
            </table>
            \\endhtmlonly
            '''
        htmlTableTpl = textwrap.dedent(htmlTableTpl)    
        htmlTrTpl = '\n  <tr bgcolor="#ffffff">%s\n  </tr>'
        htmlTdTpl = '\n    <td>%s</td>'

        # Loop through transl objects in the order of sorted readable names
        # and add generate the content of the HTML table.
        trlst = []
        for name, obj in self.langLst:
            # Fill the table data elements for one row. The first element
            # contains the readable name of the language.
            lst = [ htmlTdTpl % obj.langReadable ]
            
            # The next two elements contain the list of maintainers 
            # and the list of their mangled e-mails. For English-based
            # translators that are coupled with the non-English based, 
            # insert the 'see' note.
            mm = None  # init
            ee = None  # init
            if obj.status == 'En':
                # Check whether there is the coupled non-English.
                classId = obj.classId[:-2]
                if self.__translDic.has_key(classId):
                    lang = self.__translDic[classId].langReadable
                    mm = 'see the %s language' % lang
                    ee = '&nbsp;'
            
            if not mm and self.__maintainersDic.has_key(obj.classId):
                lm = [ m[0] for m in self.__maintainersDic[obj.classId] ]  
                mm = '<br>'.join(lm)
                le = [ m[1] for m in self.__maintainersDic[obj.classId] ]
                ee = '<br>'.join(le)
            
            # Mangle the e-mail and replace the entity references.
            if ee:
                ee = ee.replace('@', '@NOSPAM.')
            if mm:
                mm = mm.replace('&ccaron;', '&#x010d;')
                mm = mm.replace('&rcaron;', '&#x0159;')
            
            # Append the maintainer and e-mail elements.
            lst.append(htmlTdTpl % mm)
            lst.append(htmlTdTpl % ee)
            
            # The last element contains the readable form of the status.
            lst.append(htmlTdTpl % obj.readableStatus)
            
            # Join the table data to one table row. 
            trlst.append(htmlTrTpl % (''.join(lst)))
             
        # Join the table rows and insert into the template.
        htmlTable = htmlTableTpl % (''.join(trlst))
        
        # Define templates for LaTeX table parts of the documentation.
        latexTableTpl = r'''
            \latexonly
            \begin{tabular}{|l|l|l|l|}
              \hline 
              {\bf Language} & {\bf Maintainer} & {\bf Contact address} & {\bf Status} \\
              \hline
            %s
              \hline
            \end{tabular}
            \endlatexonly
            '''
        latexTableTpl = textwrap.dedent(latexTableTpl)    
        latexLineTpl = '\n' + r'  %s & %s & {\tt\tiny %s} & %s \\'

        # Loop through transl objects in the order of sorted readable names
        # and add generate the content of the LaTeX table.
        trlst = []
        for name, obj in self.langLst:
            # For LaTeX, more maintainers for the same language are
            # placed on separate rows in the table.  The line separator
            # in the table is placed explicitly above the first
            # maintainer. Prepare the arguments for the LaTeX row template.
            maintainers = []
            if self.__maintainersDic.has_key(obj.classId):
                maintainers = self.__maintainersDic[obj.classId]

            lang = obj.langReadable
            maintainer = None  # init
            email = None       # init
            if obj.status == 'En':
                # Check whether there is the coupled non-English.
                classId = obj.classId[:-2]
                if self.__translDic.has_key(classId):
                    langNE = self.__translDic[classId].langReadable
                    maintainer = 'see the %s language' % langNE
                    email = '~'
            
            if not maintainer and self.__maintainersDic.has_key(obj.classId):
                lm = [ m[0] for m in self.__maintainersDic[obj.classId] ]  
                maintainer = maintainers[0][0]
                email = maintainers[0][1]

            status = obj.readableStatus

            # Use the template to produce the line of the table and insert
            # the hline plus the constructed line into the table content.
            trlst.append('\n  \\hline')
            trlst.append(latexLineTpl % (lang, maintainer, email, status))
                        
            # List the other maintainers for the language. Do not set
            # lang and status for them.
            lang = '~'
            status = '~'
            for m in maintainers[1:]:
                maintainer = m[0]
                email = m[1]
                trlst.append(latexLineTpl % (lang, maintainer, email, status))
            
        # Join the table lines and insert into the template.
        latexTable = latexTableTpl % (''.join(trlst))
            
        # Do the LaTeX replacements.
        latexTable = latexTable.replace('&aacute;', "\\'{a}")
        latexTable = latexTable.replace('&Aacute;', "\\'{A}")
        latexTable = latexTable.replace('&auml;',   '\\"{a}')
        latexTable = latexTable.replace('&ouml;',   '\\"{o}')
        latexTable = latexTable.replace('&oslash;', '\\o{}')
        latexTable = latexTable.replace('&ccaron;', '\\v{c}')
        latexTable = latexTable.replace('&rcaron;', '\\v{r}')
        latexTable = latexTable.replace('_',        '\\_')
        
        # Put the HTML and LaTeX parts together and define the dic item.
        tplDic['informationTable'] = htmlTable + '\n' + latexTable 

        # Insert the symbols into the document template and write it down.
        f = file(fDocName, 'w')
        f.write(doctpl % tplDic)
        f.close()
                    
if __name__ == '__main__':
    
    # Create the manager, build the transl objects, and parse the related
    # sources.
    trMan = TrManager()

    # Generate the language.doc.
    trMan.generateLanguageDoc()
    
    # Generate the translator report.
    trMan.generateTranslatorReport()
