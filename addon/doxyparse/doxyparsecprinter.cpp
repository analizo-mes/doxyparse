#include "doxyparsecprinter.h"

DoxyparseCPrinter::DoxyparseCPrinter() {}

DoxyparseCPrinter::~DoxyparseCPrinter() {}

void DoxyparseCPrinter::printReferenceTo(MemberDef *md)
{
  printf("      uses ");
  if (md->getClassDef() != NULL)
  {
    printType(md);
    printf("%s::", md->getClassDef()->name().data());
    printSignature(md);
    printf("defined in %s\n", md->getClassDef()->getFileDef()->getOutputFileBase().data());
  }
}

void DoxyparseCPrinter::printClass(ClassDef *cd)
{
  MemberList* ml = cd->getMemberList(MemberListType_variableMembers);
  if (ml)
  {
    MemberListIterator mli(*ml);
    MemberDef* md;
    for (mli.toFirst();(md=mli.current());++mli)
    {
      printf("   variable %s::%s in line %d\n", cd->name().data(), md->name().data(), md->getDefLine());
      printProtection(md);
    }
  }
}
