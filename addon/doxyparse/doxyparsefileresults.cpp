#include "doxyparsefileresults.h"
#include <yaml-cpp/yaml.h>

void DoxyparseFileResults::lookup_symbol(Definition *def){
  if (def->definitionType() == Definition::TypeMember) {
    MemberDef *member_def = (MemberDef *)def;
    std::string type = member_def->memberTypeName().data();
    std::string signature = this->function_signature(member_def);
    this->print_definition(type, signature, member_def->getDefLine(), def);
  }
}

void DoxyparseFileResults::print_reference_to(std::string type,
                                            std::string signature,
                                            std::string defined_in) {
  *this->yaml << YAML::Key << YAML::DoubleQuoted << signature << YAML::Value;
  *this->yaml << YAML::BeginMap;
  this->add_value(TYPE, type); //Print type
  this->add_value(DEFINED_IN, defined_in); //Print line definition
  *this->yaml << YAML::EndMap;
}

void DoxyparseFileResults::print_definition(std::string type,
                                            std::string signature, int line,
                                            Definition *def){
  MemberDef *member_def = (MemberDef *)def;
  *this->yaml << YAML::Key << YAML::DoubleQuoted << signature << YAML::Value;
  *this->yaml << YAML::BeginMap;
  this->add_value(TYPE, type); //Print type
  this->add_value(LINE, line); //Print number line
  if (member_def->protection() == Public) {
    this->add_value(PROTECTION, PUBLIC);
  }
  if (member_def->isFunction()) {
    this->function_information(member_def);
  }
  *this->yaml << YAML::EndMap;
}

bool DoxyparseFileResults::ignore_static_external_call(MemberDef *context, MemberDef *member_def){
  return member_def->isStatic() &&
         member_def->getFileDef() &&
         !(member_def->getFileDef()->getOutputFileBase() == context->getFileDef()->getOutputFileBase());
}

void DoxyparseFileResults::function_information(MemberDef* member_def){
  int size = member_def->getEndBodyLine() - member_def->getStartBodyLine() + 1;
  this->add_value(LINES_OF_CODE, size); //Print number of lines
  ArgumentList *argList = member_def->argumentList();
  this->add_value(PARAMETERS, argList->count()); //Print number of arguments
  this->add_value(CONDITIONAL_PATHS, member_def->numberOfFlowKeyWords()); //Print number of conditional paths
  MemberSDict *def_dict = member_def->getReferencesMembers();
  if (def_dict) {
    MemberSDict::Iterator member_dict_iterator(*def_dict);
    MemberDef *member_def;
    this->add_value(USES); //Print uses
    *this->yaml << YAML::BeginSeq;
    for (member_dict_iterator.toFirst(); (member_def=member_dict_iterator.current()); ++member_dict_iterator) {
      if (member_def->definitionType() == Definition::TypeMember && !this->ignore_static_external_call(member_def, member_def)) {
        *this->yaml << YAML::BeginMap;
        this->reference_to(member_def);
        *this->yaml << YAML::EndMap;
      }
    }
    *this->yaml << YAML::EndSeq;
  }
}

void DoxyparseFileResults::list_members(MemberList *member_list){
  if (member_list) {
    MemberListIterator member_list_iterator(*member_list);
    MemberDef *member_def;
    for (member_list_iterator.toFirst(); (member_def=member_list_iterator.current()); ++member_list_iterator) {
      *this->yaml << YAML::BeginMap;
      this->lookup_symbol((Definition*) member_def);
      *this->yaml << YAML::EndMap;
    }
  }
}

void DoxyparseFileResults::add_value(std::string key, std::string value){
  this->add_key_yaml(key);
  *this->yaml << YAML::Value << value;
}

void DoxyparseFileResults::add_value(std::string key, int value){
  this->add_value(key, std::to_string(value));
}

void DoxyparseFileResults::add_value(std::string key){
  this->add_key_yaml(key);
  *this->yaml << YAML::Value;
}

void DoxyparseFileResults::add_value(std::string key, enum YAML::EMITTER_MANIP value){
  *this->yaml << value;
  this->add_value(key);
}

void DoxyparseFileResults::add_key_yaml(std::string key){
  *this->yaml << YAML::Key << key;
}

std::string DoxyparseFileResults::function_signature(MemberDef* member_def) {
  std::string signature = member_def->name().data();
  if(member_def->isFunction()){
    ArgumentList *argList = member_def->argumentList();
    ArgumentListIterator iterator(*argList);
    signature += "(";
    Argument * argument = iterator.toFirst();
    if(argument != NULL) {
      signature += argument->type.data();
      for(++iterator; (argument = iterator.current()) ;++iterator){
        signature += std::string(",") + argument->type.data();
      }
    }
    signature += ")";
  }
  return signature;
}
