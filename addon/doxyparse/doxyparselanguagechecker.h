#ifndef DOXYPARSELANGUAGECHECKER_H
#define DOXYPARSELANGUAGECHECKER_H

#include "doxygen.h"
#include "filename.h"
#include <string>

class DoxyparseLanguageChecker
{
  public:
    DoxyparseLanguageChecker();
   ~DoxyparseLanguageChecker();

    bool isCCode(FileNameListIterator &fnli);
  private:
    bool checkLanguage(std::string &filename, std::string extension);
};

#endif
