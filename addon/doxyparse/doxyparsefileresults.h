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
    DoxyparseFileResults();
   ~DoxyparseFileResults();

    virtual void listSymbols() = 0;
}

