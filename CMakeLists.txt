cmake_minimum_required(VERSION 2.8.9)

project(ShapeDistanceAnalyzer)


set(ShapeDistanceAnalyzer_VERSION_MAJOR 1)
set(ShapeDistanceAnalyzer_VERSION_MINOR 0)
set(ShapeDistanceAnalyzer_VERSION_PATCH 1)


option(ShapeDistanceAnalyzer_BUILD_SLICER_EXTENSION OFF)

if(ShapeDistanceAnalyzer_BUILD_SLICER_EXTENSION)
	#-----------------------------------------------------------------------------
	# Extension meta-information
	set(EXTENSION_HOMEPAGE "")
	set(EXTENSION_CATEGORY "Statistics")
	set(EXTENSION_CONTRIBUTORS "Mateo Lopez (University of North Carolina), Juan Carlos Prieto (University of North Carolina) ")
	set(EXTENSION_DESCRIPTION "ShapeDistanceAnalyzer allows the computation of statistics of 3D models, according to the distance between them. Linear subdivision  is possible to smooth the computed histogram.")
	set(EXTENSION_ICONURL "")
	set(EXTENSION_SCREENSHOTURLS "")
	set(EXTENSION_DEPENDS )

	#-----------------------------------------------------------------------------
	# Extension dependencies
	find_package(Slicer REQUIRED)
	include(${Slicer_USE_FILE})

	add_subdirectory(ShapeDistanceAnalyzer)
else()
	find_package(VTK REQUIRED)
	find_package(SlicerExecutionModel REQUIRED)
endif()

#-----------------------------------------------------------------------------
# Extension modules

#add_subdirectory(CLI/ComputeMeanShapes)
add_subdirectory(CLI/linearSubdivision)
## NEXT_MODULE


#-----------------------------------------------------------------------------
if(ShapeDistanceAnalyzer_BUILD_SLICER_EXTENSION)
	include(${Slicer_EXTENSION_CPACK})
endif()
