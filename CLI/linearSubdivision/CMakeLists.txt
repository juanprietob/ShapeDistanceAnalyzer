cmake_minimum_required(VERSION 2.8)
 
PROJECT(Subdivision)

set (CMAKE_CXX_STANDARD 11)

find_package(VTK REQUIRED)
include(${VTK_USE_FILE})

find_package(SlicerExecutionModel REQUIRED)
include(${SlicerExecutionModel_USE_FILE})

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/lib)
add_subdirectory(lib)
add_subdirectory(app)