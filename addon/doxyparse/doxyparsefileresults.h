#ifndef DOXYPARSEFILERESULTS_H
#define DOXYPARSEFILERESULTS_H

#include "doxygen.h"
#include "arguments.h"
#include "classlist.h"
#include "filedef.h"
#include "filename.h"
#include <string>
#include <yaml-cpp/yaml.h>

class DoxyparseFileResults
{
  public:
    DoxyparseFileResults(){};
   ~DoxyparseFileResults(){};

    void list_symbols(FileName* file_name){};
  protected:
    virtual void reference_to(MemberDef* member_def) = 0;

	protected:
    const std::string TYPE = "type";
	  const std::string INFORMATIONS = "informations";
    const std::string DEFINES = "defines";
    const std::string LINE = "line";
    const std::string PROTECTION = "protection";
    const std::string PUBLIC = "public";
    const std::string LINES_OF_CODE = "lines_of_code";
    const std::string PARAMETERS = "parameters";
    const std::string USES = "uses";
    const std::string DEFINED_IN = "defined_in";
    const std::string CONDITIONAL_PATHS = "conditional_paths";

    YAML::Emitter *yaml;


    void print_reference_to(std::string type, std::string signature,
                          std::string defined_in);
    void lookup_symbol(Definition *def);
    void print_definition(std::string type, std::string signature,
                         int line, Definition *def);
    bool ignore_static_external_call(MemberDef *context, MemberDef *member_def);
    void function_information(MemberDef* member_def);
    void list_members(MemberList *member_list);
		void add_value(std::string key, std::string value);
    void add_value(std::string key, int value);
    void add_value(std::string key);
    void add_value(std::string key, enum YAML::EMITTER_MANIP value);
    void add_key_yaml(std::string key);
    std::string function_signature(MemberDef* member_def);
};

#endif
