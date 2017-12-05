#include "doxyparseresults.h"
#include "doxyparsefileresults.h"
#include "doxyparseresultsooparser.h"
#include "doxyparseresultstructured.h"
#include <yaml-cpp/yaml.h>

FileNameListIterator DoxyparseResults::get_files()
{
    FileNameListIterator file_name_list_iterator(*Doxygen::inputNameList);
    return file_name_list_iterator;
}

void DoxyparseResults::listSymbols()
{
  FileNameListIterator file_name_list_iterator = this->get_files();
  file_name_list_iterator.toFirst();

  for (FileName *file_name; (file_name=file_name_list_iterator.current()); ++file_name_list_iterator) {
    FileNameIterator file_name_iterator(*file_name);
    DoxyparseFileResults* file_result;
    if (this->detect_is_c_code(file_name)) {
      file_result = new DoxyparseResultStructured();
    } else {
      // file_result = new DoxyparseResultsOOParser();
    }
    file_result->list_symbols(file_name);
  }
  // TODO print external symbols referenced
}

/* Detects the programming language of the project. Actually, we only care
 * about whether it is a C project or not. */
bool DoxyparseResults::detect_is_c_code(FileName* file_name) {
  std::string filename = file_name->fileName();
  bool is_c_code = !(
    this->check_language(filename, ".cc") ||
    this->check_language(filename, ".cxx") ||
    this->check_language(filename, ".cpp") ||
    this->check_language(filename, ".java") ||
    this->check_language(filename, ".py") ||
    this->check_language(filename, ".pyw") ||
    this->check_language(filename, ".cs")
   );

   return is_c_code;
}

bool DoxyparseResults::check_language(std::string& filename, std::string extension) {
  if (filename.find(extension, filename.size() - extension.size()) != std::string::npos) {
    return true;
  } else {
    return false;
  }
}
