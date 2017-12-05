#ifndef DOXYPARSERESULTSTRUCTURED_H
#define DOXYPARSERESULTSTRUCTURED_H

#include "doxygen.h"
#include "arguments.h"
#include "classlist.h"
#include "filedef.h"
#include "filename.h"
#include "doxyparsefileresults.h"
#include <string>
#include <yaml-cpp/yaml.h>

class DoxyparseResultStructured : public DoxyparseFileResults
{
  public:
    DoxyparseResultStructured(){};
    ~DoxyparseResultStructured(){};

  protected:
    void reference_to(MemberDef* member_def) override;

  private:
    const std::string VARIABLE = "variable";
    void list_struct_definition(ClassDef* struct_def);
    void load_file_members_into_yaml(MemberList *member_list, FileDef *file_def, ClassSDict *structies);
};

#endif
