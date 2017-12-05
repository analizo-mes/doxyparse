#ifndef DOXYPARSERESULTS_H
#define DOXYPARSERESULTS_H

#include "doxygen.h"
#include "arguments.h"
#include "classlist.h"
#include "filedef.h"
#include "filename.h"
#include <string>
#include <yaml-cpp/yaml.h>

class DoxyparseResults
{
  public:
    DoxyparseResults(){};
   ~DoxyparseResults(){};

    void listSymbols();

  private:
    const std::string VARIABLE = "variable";

    FileNameListIterator get_files();
    bool detect_is_c_code(FileName* file_name);
    bool check_language(std::string& filename, std::string extension);

};
#endif
