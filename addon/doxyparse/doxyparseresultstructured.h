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

class DoxyparseResultStructured
{
  public:
    DoxyparseResultStructured();
   ~DoxyparseResultStructured();

  private:
    void list_struct_definition(ClassDef* struct_def);
}

