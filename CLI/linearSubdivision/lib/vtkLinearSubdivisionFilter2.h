
/*=========================================================================
  Program:   Visualization Toolkit
  Module:    vtkLinearSubdivisionFilter2.h
  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.
     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.
=========================================================================*/
/**
 * @class   vtkLinearSubdivisionFilter2
 * @brief   generate a subdivision surface using the Linear Scheme
 *
 * vtkLinearSubdivisionFilter2 is a filter that generates output by
 * subdividing its input polydata. Each subdivision iteration create 4
 * new triangles for each triangle in the polydata.
 *
 * @par Thanks:
 * This work was supported by PHS Research Grant No. 1 P41 RR13218-01
 * from the National Center for Research Resources.
 *
 * @sa
 * vtkInterpolatingSubdivisionFilter vtkButterflySubdivisionFilter
*/

#ifndef vtkLinearSubdivisionFilter2_h
#define vtkLinearSubdivisionFilter2_h

#include "vtkFiltersModelingModule.h" // For export macro
#include "vtkInterpolatingSubdivisionFilter.h"
#include "vtkInformation.h"
#include "vtkInformationVector.h"
#include <map>

class vtkIntArray;
class vtkPointData;
class vtkPoints;
class vtkPolyData;

class vtkCellArray;
class vtkCellData;
class vtkIdList;



class VTKFILTERSMODELING_EXPORT vtkLinearSubdivisionFilter2 : public vtkInterpolatingSubdivisionFilter
{
public:
  //@{
  /**
   * Construct object with NumberOfSubdivisions set to 1.
   */
  static vtkLinearSubdivisionFilter2 *New();
  vtkTypeMacro(vtkLinearSubdivisionFilter2,vtkInterpolatingSubdivisionFilter);
  //@}

protected:
  vtkLinearSubdivisionFilter2 () {}
  ~vtkLinearSubdivisionFilter2 () override {}

  int RequestData(vtkInformation *, 
                  vtkInformationVector **, 
                  vtkInformationVector *) override;

  
  void GenerateSubdivisionCells (vtkPolyData *inputDS, 
                                 vtkIntArray *edgeData, 
                                 vtkCellArray *outputPolys, 
                                 vtkCellData *outputCD) ;


  int GenerateSubdivisionPoints (vtkPolyData *inputDS,
                                 vtkIntArray *edgeData,
                                 vtkPoints *outputPts,
                                 vtkPointData *outputPD) override;

  int vtkSubdivisionFilterRequestData(vtkInformation *,
                                      vtkInformationVector **, 
                                      vtkInformationVector *);

private:
  vtkLinearSubdivisionFilter2(const vtkLinearSubdivisionFilter2&) = delete;
  void operator=(const vtkLinearSubdivisionFilter2&) = delete;
};

#endif


// VTK-HeaderTest-Exclude: vtkLinearSubdivisionFilter2.h