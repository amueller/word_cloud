cmake_minimum_required(VERSION 3.12.0)
project(hello LANGUAGES C)

find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)

set(module "query_integral_image")

add_cython_target(${module} ${module}.pyx C OUTPUT_VAR sources)
add_library(${module} MODULE ${sources})
python_extension_module(${module})

install(TARGETS ${module} LIBRARY DESTINATION wordcloud)