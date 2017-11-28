#ifndef "DOXYPARSERESULTOOPARSER_H"
#define "DOXYPARSERESULTOOPARSER_H"

#include "doxyparsefileresult.h"

class DoxyparseResultsOOParser : public DoxyparseFileResult {
  public:
    const std::string ABSTRACT_CLASS = "abstract class";
    const std::string INHERITS = "inherits";

  private:
    void class_information(ClassDef* cd);
    void list_all_members(ClassDef* cd);
}

#endif;
