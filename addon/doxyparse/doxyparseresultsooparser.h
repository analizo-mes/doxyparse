#ifndef DOXYPARSERESULTOOPARSER_H
#define DOXYPARSERESULTOOPARSER_H

#include "doxyparsefileresults.h"

class DoxyparseResultsOOParser : public DoxyparseFileResults
{
  public:
    const std::string ABSTRACT_CLASS = "abstract class";
    const std::string INHERITS = "inherits";

  private:
    void class_information(ClassDef* cd);
    void list_all_members(ClassDef* cd);
    void reference_to(MemberDef* member_def);
    void load_file_members_into_yaml(MemberList *member_list, FileDef *file_def, ClassSDict *classes);
};

#endif
