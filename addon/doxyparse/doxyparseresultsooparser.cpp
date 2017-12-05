#include "doxyparseresultsooparser.h"
#include <yaml-cpp/yaml.h>

void DoxyparseResultsOOParser::load_file_members_into_yaml(MemberList *member_list, FileDef *file_def, ClassSDict *classes) {
  if (member_list) {
    this->add_value(file_def->getOutputFileBase().data());
    this->add_value(DEFINES, YAML::BeginMap);
    *this->yaml << YAML::BeginSeq;
    this->list_members(member_list);

    if (classes) {
      *this->yaml << YAML::BeginMap;
      ClassSDict::Iterator classes_element_iterator(*classes);
      ClassDef *classes_def;
      for (classes_element_iterator.toFirst(); (classes_def = classes_element_iterator.current()); ++classes_element_iterator) {
        this->class_information(classes_def);
      }
      *this->yaml << YAML::EndMap;
    }
    *this->yaml << YAML::EndSeq;
    *this->yaml << YAML::EndMap;
  }
}

void DoxyparseResultsOOParser::class_information(ClassDef* class_def) {
  this->add_value(class_def->name().data());
  BaseClassList* baseClasses = class_def->baseClasses();
  *this->yaml << YAML::BeginMap;
  if (baseClasses) {
    BaseClassListIterator base_list_iterator(*baseClasses);
    BaseClassDef* base_class_def;
    for (base_list_iterator.toFirst(); (base_class_def = base_list_iterator.current()); ++base_list_iterator) {
      this->add_value(INHERITS, base_class_def->classDef->name().data());
    }
  }
  if(class_def->isAbstract()) {
    this->add_value(INFORMATIONS, ABSTRACT_CLASS);
  }
  this->add_value(DEFINES);
  this->list_all_members(class_def);
  *this->yaml << YAML::EndMap;
}

void DoxyparseResultsOOParser::list_all_members(ClassDef* class_def) {
  *this->yaml << YAML::BeginSeq;
  // methods
  this->list_members(class_def->getMemberList(MemberListType_functionMembers));
  // constructors
  this->list_members(class_def->getMemberList(MemberListType_constructors));
  // attributes
  this->list_members(class_def->getMemberList(MemberListType_variableMembers));
  *this->yaml << YAML::EndSeq;
}
