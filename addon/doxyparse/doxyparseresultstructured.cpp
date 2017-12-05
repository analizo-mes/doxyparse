#include "doxyparseresultstructured.h"
#include <yaml-cpp/yaml.h>

void DoxyparseResultStructured::load_file_members_into_yaml(MemberList *member_list, FileDef *file_def, ClassSDict *structies) {
  if (member_list) {
    this->add_value(file_def->getOutputFileBase().data());
    this->add_value(DEFINES, YAML::BeginMap);
    *this->yaml << YAML::BeginSeq;
    this->list_members(member_list);

    if (structies) {
      *this->yaml << YAML::BeginMap;
      ClassSDict::Iterator struct_element_iterator(*structies);
      ClassDef *struct_def;
      for (struct_element_iterator.toFirst(); (struct_def = struct_element_iterator.current()); ++struct_element_iterator) {
        this->list_struct_definition(struct_def);
      }
      *this->yaml << YAML::EndMap;
    }
    *this->yaml << YAML::EndSeq;
    *this->yaml << YAML::EndMap;
  }
}

void DoxyparseResultStructured::list_struct_definition(ClassDef* struct_def) {
  MemberList* member_list = struct_def->getMemberList(MemberListType_variableMembers);
  if (member_list) {
    MemberListIterator member_list_iterator(*member_list);
    MemberDef* member_def;
    for (member_list_iterator.toFirst(); (member_def=member_list_iterator.current()); ++member_list_iterator) {
      this->print_definition(VARIABLE, struct_def->name().data() + std::string("::") + member_def->name().data(), member_def->getDefLine(), member_def);
    }
  }
}

void DoxyparseResultStructured::reference_to(MemberDef* member_def) {
  std::string type = member_def->memberTypeName().data();
  std::string defined_in = "";
  std::string signature = "";
  signature = member_def->getClassDef()->name().data() + std::string("::") + this->function_signature(member_def);
  defined_in = member_def->getClassDef()->getFileDef()->getOutputFileBase().data();
  this->print_reference_to(type, signature, defined_in);
}
