cmake_minimum_required(VERSION 3.12.0)
project(hello LANGUAGES C)

find_package(PythonExtensions REQUIRED)

set(module "query_integral_image")

add_library(${module} MODULE ${module}.c)
python_extension_module(${module})

install(TARGETS ${module} LIBRARY DESTINATION wordcloud)