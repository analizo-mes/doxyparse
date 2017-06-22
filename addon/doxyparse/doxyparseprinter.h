#ifndef DOXYPARSEPRINTER_H
#define DOXYPARSEPRINTER_H

#include "doxygen.h"
#include "arguments.h"
#include "classlist.h"
#include "filedef.h"
#include "filename.h"
#include <string>

class DoxyparsePrinter
{
  public:
    DoxyparsePrinter();
   ~DoxyparsePrinter();

    void printFile(FileDef *fd);
    virtual void printClass(ClassDef *cd) {}

  protected:
    void printMembers(MemberList *ml);
    void printDefinition(MemberDef *md);
    void printType(MemberDef *md);
    void printSignature(MemberDef *md);
    void printArgumentList(MemberDef *md);
    void printDefinitionLine(MemberDef *md);
    void printProtection(MemberDef *md);
    void printFunctionInformation(MemberDef *md);
    void printNumberOfLines(MemberDef *md);
    void printNumberOfArguments(MemberDef *md);
    void printNumberOfConditionalPaths(MemberDef *md);
    void printReferencesMembers(MemberDef *md);
    bool ignoreStaticExternalCall(MemberDef *context, MemberDef *md);
    virtual void printReferenceTo(MemberDef *md) {}
};

#endif
