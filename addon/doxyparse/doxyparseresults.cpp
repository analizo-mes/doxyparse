#include "doxyparseresults.h"

DoxyparseResults::DoxyparseResults() {}

DoxyparseResults::~DoxyparseResults() {}


void DoxyparseResults::informResults()
{
  // iterate over the input files
  FileNameListIterator fnli(*Doxygen::inputNameList);
  FileName *fn;

  DoxyparsePrinter* printer;
  DoxyparseLanguageChecker languageChecker;
  if (languageChecker.isCCode(fnli))
  {
    printer = new DoxyparseCPrinter();
  }
  else
  {
    printer = new DoxyparseStandardPrinter();
  }

  // for each file
  for (fnli.toFirst();(fn=fnli.current());++fnli)
  {
    FileNameIterator fni(*fn);
    FileDef *fd;
    for (;(fd=fni.current());++fni)
    {
      printer->printFile(fd);

      ClassSDict *classes = fd->getClassSDict();
      if (classes)
      {
        ClassSDict::Iterator cli(*classes);
        ClassDef *cd;
        for (cli.toFirst();(cd = cli.current());++cli)
        {
          printer->printClass(cd);
        }
      }
    }
  }
  // TODO print external symbols referenced
}
