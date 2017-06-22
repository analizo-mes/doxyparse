#ifndef DOXYPARSESTANDARDPRINTER_H
#define DOXYPARSESTANDARDPRINTER_H

#include "doxygen.h"
#include "arguments.h"
#include "classlist.h"
#include "filedef.h"
#include "filename.h"
#include "doxyparseprinter.h"
#include <string>

class DoxyparseStandardPrinter : public DoxyparsePrinter
{
  public:
    DoxyparseStandardPrinter();
   ~DoxyparseStandardPrinter();

    void printClass(ClassDef *cd);

  protected:
    void printReferenceTo(MemberDef *md);
    void printWhereItWasDefined(MemberDef *md);
    void printInheritance(ClassDef *cd);
    void printAllMembers(ClassDef *cd);
};

#endif
