#include "doxyparselanguagechecker.h"

DoxyparseLanguageChecker::DoxyparseLanguageChecker() {}

DoxyparseLanguageChecker::~DoxyparseLanguageChecker() {}

/* Detects the programming language of the project. Actually, we only care
 * about whether it is a C project or not. */
bool DoxyparseLanguageChecker::isCCode(FileNameListIterator &fnli)
{
  FileName* fn;
  bool isCCode = true;
  for(fnli.toFirst(); isCCode && (fn=fnli.current()); ++fnli)
  {
    std::string filename = fn->fileName();
    isCCode =
      !checkLanguage(filename, ".cc") &&
      !checkLanguage(filename, ".cxx") &&
      !checkLanguage(filename, ".cpp") &&
      !checkLanguage(filename, ".java") &&
      !checkLanguage(filename, ".py") &&
      !checkLanguage(filename, ".pyw");
  }
  return isCCode;
}

bool DoxyparseLanguageChecker::checkLanguage(std::string &filename,
  std::string extension)
{
  size_t findLength = filename.size() - extension.size();
  size_t findResult = filename.find(extension, findLength);
  return findResult != std::string::npos;
}
