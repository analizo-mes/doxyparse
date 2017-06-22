#ifndef DOXYPARSECPRINTER_H
#define DOXYPARSECPRINTER_H

#include "doxygen.h"
#include "arguments.h"
#include "classlist.h"
#include "filedef.h"
#include "filename.h"
#include "doxyparseprinter.h"
#include <string>

class DoxyparseCPrinter : public DoxyparsePrinter
{
  public:
    DoxyparseCPrinter();
   ~DoxyparseCPrinter();

    void printClass(ClassDef *cd);

  protected:
    void printReferenceTo(MemberDef *md);
};

#endif
