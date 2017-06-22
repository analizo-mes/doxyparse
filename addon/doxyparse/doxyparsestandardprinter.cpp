#include "doxyparsestandardprinter.h"

DoxyparseStandardPrinter::DoxyparseStandardPrinter() {}

DoxyparseStandardPrinter::~DoxyparseStandardPrinter() {}

void DoxyparseStandardPrinter::printReferenceTo(MemberDef *md)
{
  printf("      uses ");
  printType(md);
  printSignature(md);
  printWhereItWasDefined(md);
}

void DoxyparseStandardPrinter::printWhereItWasDefined(MemberDef *md)
{
  if (md->getClassDef())
  {
    printf("defined in %s\n", md->getClassDef()->name().data());
  }
  else if (md->getFileDef())
  {
    printf("defined in %s\n", md->getFileDef()->getOutputFileBase().data());
  }
  else
  {
    printf("\n");
  }
}

void DoxyparseStandardPrinter::printClass(ClassDef *cd)
{
  printf("module %s\n", cd->name().data());
  printInheritance(cd);
  if (cd->isAbstract())
  {
    printf("   abstract class\n");
  }
  printAllMembers(cd);
}

void DoxyparseStandardPrinter::printInheritance(ClassDef *cd)
{
  BaseClassList* baseClasses = cd->baseClasses();
  if (baseClasses)
  {
    BaseClassListIterator bci(*baseClasses);
    BaseClassDef* bcd;
    for (bci.toFirst();(bcd = bci.current());++bci)
    {
      printf("   inherits from %s\n", bcd->classDef->name().data());
    }
  }
}

void DoxyparseStandardPrinter::printAllMembers(ClassDef *cd)
{
  // methods
  printMembers(cd->getMemberList(MemberListType_functionMembers));
  // constructors
  printMembers(cd->getMemberList(MemberListType_constructors));
  // attributes
  printMembers(cd->getMemberList(MemberListType_variableMembers));
}
