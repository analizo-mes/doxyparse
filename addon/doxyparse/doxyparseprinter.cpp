#include "doxyparseprinter.h"

DoxyparsePrinter::DoxyparsePrinter() {}

DoxyparsePrinter::~DoxyparsePrinter() {}

void DoxyparsePrinter::printFile(FileDef *fd)
{
  printf("file %s\n", fd->absFilePath().data());
  MemberList *ml = fd->getMemberList(MemberListType_allMembersList);
  if (ml && ml->count() > 0)
  {
    printf("module %s\n", fd->getOutputFileBase().data());
    printMembers(ml);
  }
}

void DoxyparsePrinter::printMembers(MemberList *ml)
{
  if (ml)
  {
    MemberListIterator mli(*ml);
    MemberDef *md;
    for (mli.toFirst();(md=mli.current());++mli)
    {
      if (md->definitionType() == Definition::TypeMember)
      {
        printDefinition(md);
        printProtection(md);
        if (md->isFunction())
        {
          printFunctionInformation(md);
        }
      }
    }
  }
}

void DoxyparsePrinter::printDefinition(MemberDef *md)
{
  printf("   ");
  printType(md);
  printSignature(md);
  printDefinitionLine(md);
}

void DoxyparsePrinter::printType(MemberDef *md)
{
  printf("%s ", md->memberTypeName().data());
}

void DoxyparsePrinter::printSignature(MemberDef* md)
{
  printf("%s", md->name().data());
  if (md->isFunction())
  {
    printArgumentList(md);
  }
  printf(" ");
}

void DoxyparsePrinter::printArgumentList(MemberDef *md)
{
  ArgumentList *argList = md->argumentList();
  ArgumentListIterator iterator(*argList);

  printf("(");
  Argument * argument = iterator.toFirst();
  if (argument != NULL)
  {
    printf("%s", argument->type.data());
    for (++iterator;(argument = iterator.current());++iterator)
    {
      printf(",%s", argument->type.data());
    }
  }
  printf(")");
}

void DoxyparsePrinter::printDefinitionLine(MemberDef *md)
{
  printf("in line %d\n", md->getDefLine());
}

void DoxyparsePrinter::printProtection(MemberDef *md)
{
  if (md->protection() == Public)
  {
    printf("      protection public\n");
  }
}

void DoxyparsePrinter::printFunctionInformation(MemberDef *md)
{
  printNumberOfLines(md);
  printNumberOfArguments(md);
  printNumberOfConditionalPaths(md);
  printReferencesMembers(md);
}

void DoxyparsePrinter::printNumberOfLines(MemberDef *md)
{
  int size = md->getEndBodyLine() - md->getStartBodyLine() + 1;
  printf("      %d lines of code\n", size);
}

void DoxyparsePrinter::printNumberOfArguments(MemberDef *md)
{
  ArgumentList *argList = md->argumentList();
  printf("      %d parameters\n", argList->count());
}

void DoxyparsePrinter::printNumberOfConditionalPaths(MemberDef *md)
{
  printf("      %d conditional paths\n", md->numberOfFlowKeyWords());
}

void DoxyparsePrinter::printReferencesMembers(MemberDef *md)
{
  MemberSDict *defDict = md->getReferencesMembers();
  if (defDict)
  {
    MemberSDict::Iterator msdi(*defDict);
    MemberDef *rmd;
    for (msdi.toFirst();(rmd=msdi.current());++msdi)
    {
      if (rmd->definitionType() == Definition::TypeMember
          && !ignoreStaticExternalCall(md, rmd))
      {
        printReferenceTo(rmd);
      }
    }
  }
}

bool DoxyparsePrinter::ignoreStaticExternalCall(MemberDef *context, MemberDef *md)
{
  if (md->isStatic())
  {
    if (md->getFileDef())
    {
      if (md->getFileDef()->getOutputFileBase() == context->getFileDef()->getOutputFileBase())
        // TODO ignore prefix of file
        return false;
      else
        return true;
    }
    else
    {
      return false;
    }
  }
  else
  {
    return false;
  }
}
