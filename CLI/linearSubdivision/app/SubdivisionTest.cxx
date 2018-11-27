#include <vtkVersion.h>
#include <vtkSmartPointer.h>
#include <vtkCellData.h>
#include <vtkCellArray.h>
#include <vtkDoubleArray.h>
#include <vtkPoints.h>
#include <vtkTriangle.h>
#include <vtkPolyData.h>
#include <vtkPointData.h>
#include <vtkPlatonicSolidSource.h>
#include <vtkSphereSource.h>
#include <vtkPolyDataReader.h>
#include <vtkTriangleFilter.h>
#include <vtkPolyDataMapper.h>
#include <vtkActor.h>
#include <vtkRenderWindow.h>
#include <vtkRenderer.h>
#include <vtkRenderWindowInteractor.h>

#include <string>

#include <vtkButterflySubdivisionFilter.h>
#include <vtkLoopSubdivisionFilter.h>
#include <vtkLinearSubdivisionFilter.h>

#include "vtkLinearSubdivisionFilter2.h"

int main(int argc, char *argv[])
{
  vtkSmartPointer<vtkPolyData> originalMesh;

  if(argc > 1) //If a file name is specified, open and use the file.
  {
    vtkSmartPointer<vtkPolyDataReader> reader =
      vtkSmartPointer<vtkPolyDataReader>::New();
    reader->SetFileName(argv[1]);
    reader->Update();

    // Subdivision filters only work on triangles
    vtkSmartPointer<vtkTriangleFilter> triangles =
      vtkSmartPointer<vtkTriangleFilter>::New();
    triangles->SetInputConnection(reader->GetOutputPort());
    triangles->Update();
    originalMesh = triangles->GetOutput();
  }
  else //If a file name is not specified, create a sphere
  {
    
    // vtkSmartPointer<vtkPlatonicSolidSource> sphereSource =
    //   vtkSmartPointer<vtkPlatonicSolidSource>::New();
    //   sphereSource->SetSolidTypeToIcosahedron();
    // sphereSource->Update();
    vtkSmartPointer<vtkSphereSource> sphereSource =
      vtkSmartPointer<vtkSphereSource>::New();
    sphereSource->Update();    
    originalMesh = sphereSource->GetOutput();
  }

  std::cout << "Before subdivision" << std::endl;
  std::cout << "    There are " << originalMesh->GetNumberOfPoints()
            << " points." << std::endl;
  std::cout << "    There are " << originalMesh->GetNumberOfPolys()
            << " triangles." << std::endl;

  double numberOfViewports = 3.;

  vtkSmartPointer<vtkRenderWindow> renderWindow =
    vtkSmartPointer<vtkRenderWindow>::New();
  renderWindow->SetSize(200* numberOfViewports,200); //(width, height)

  vtkSmartPointer<vtkRenderWindowInteractor> renderWindowInteractor =
      vtkSmartPointer<vtkRenderWindowInteractor>::New();

  renderWindowInteractor->SetRenderWindow(renderWindow);


  int numberOfSubdivisions = 3;
  for(unsigned i = 0; i < numberOfViewports; i++)
  {
    // Note: Here we create a superclass pointer (vtkPolyDataAlgorithm) so that we can easily instantiate different
    // types of subdivision filters. Typically you would not want to do this, but rather create the pointer to be the type
    // filter you will actually use, e.g.
    // vtkSmartPointer<vtkLinearSubdivisionFilter>  subdivisionFilter = vtkSmartPointer<vtkLinearSubdivisionFilter>::New();
    vtkSmartPointer<vtkPolyDataAlgorithm> subdivisionFilter;
    switch(i)
    {
      case 0:
        subdivisionFilter = vtkSmartPointer<vtkLinearSubdivisionFilter2>::New();
        dynamic_cast<vtkLinearSubdivisionFilter2 *> (subdivisionFilter.GetPointer())->SetNumberOfSubdivisions(numberOfSubdivisions + 1);
        break;
      case 1:
        subdivisionFilter =  vtkSmartPointer<vtkLoopSubdivisionFilter>::New();
        dynamic_cast<vtkLoopSubdivisionFilter *> (subdivisionFilter.GetPointer())->SetNumberOfSubdivisions(numberOfSubdivisions);
        break;
      case 2:
        subdivisionFilter = vtkSmartPointer<vtkLinearSubdivisionFilter>::New();
        dynamic_cast<vtkLinearSubdivisionFilter *> (subdivisionFilter.GetPointer())->SetNumberOfSubdivisions(numberOfSubdivisions);
        break;
      default:
        break;
    }
#if VTK_MAJOR_VERSION <= 5
    subdivisionFilter->SetInputConnection(originalMesh->GetProducerPort());
#else
    subdivisionFilter->SetInputData(originalMesh);
#endif
    subdivisionFilter->Update();

    vtkSmartPointer<vtkRenderer> renderer =
      vtkSmartPointer<vtkRenderer>::New();

    renderWindow->AddRenderer(renderer);
    renderer->SetViewport(static_cast<double>(i)/numberOfViewports,0,static_cast<double>(i+1)/numberOfViewports,1);

    //Create a mapper and actor
    vtkSmartPointer<vtkPolyDataMapper> mapper =
        vtkSmartPointer<vtkPolyDataMapper>::New();
    mapper->SetInputConnection(subdivisionFilter->GetOutputPort());
    vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
    actor->SetMapper(mapper);
    renderer->AddActor(actor);
    renderer->ResetCamera();
    renderer->SetBackground(.1,.25,.8);

    renderWindow->Render();
    renderWindow->SetWindowName("Multiple ViewPorts");

  }

  renderWindowInteractor->Start();

  return EXIT_SUCCESS;
}
