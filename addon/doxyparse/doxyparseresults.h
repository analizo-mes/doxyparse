#ifndef DOXYPARSERESULTS_H
#define DOXYPARSERESULTS_H

#include "doxygen.h"
#include "arguments.h"
#include "classlist.h"
#include "filedef.h"
#include "filename.h"
#include "doxyparselanguagechecker.h"
#include "doxyparseprinter.h"
#include "doxyparsecprinter.h"
#include "doxyparsestandardprinter.h"
#include <string>

class DoxyparseResults
{
  public:
    DoxyparseResults();
   ~DoxyparseResults();

    void informResults();
};
#endif
