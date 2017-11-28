#include "doxyparseresultsooparser.h"
#include <yaml-cpp/yaml.h>

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
