

#include <vtkVersion.h>
#include <vtkSmartPointer.h>

#include <vtkPolyDataReader.h>
#include <vtkTriangleFilter.h>
#include <vtkPolyDataWriter.h>
#include "LinearSubdivisionCLP.h"
#include "vtkLinearSubdivisionFilter2.h"

int main(int argc, char *argv[])
{
  PARSE_ARGS;

  vtkSmartPointer<vtkPolyDataReader> reader =
    vtkSmartPointer<vtkPolyDataReader>::New();

  vtkSmartPointer<vtkTriangleFilter> triangles =
    vtkSmartPointer<vtkTriangleFilter>::New();

  vtkSmartPointer<vtkLinearSubdivisionFilter2> subdivisionFilter = 
    vtkSmartPointer<vtkLinearSubdivisionFilter2>::New();

  vtkSmartPointer<vtkPolyDataWriter> writer = 
    vtkSmartPointer<vtkPolyDataWriter>::New();

  //read the file
  reader->SetFileName(input.c_str());
  reader->Update();

  // Subdivision filters only work on triangles
  triangles->SetInputConnection(reader->GetOutputPort());
  triangles->Update();

  //Subdivide mesh
  subdivisionFilter->SetNumberOfSubdivisions(subdivisions);
  subdivisionFilter->SetInputData(triangles->GetOutput());
  subdivisionFilter->Update();

  //Save subdivide mesh
  writer->SetFileName(output.c_str());
  writer->SetInputData(subdivisionFilter->GetOutput());
  writer->Write();

  return EXIT_SUCCESS;
}
