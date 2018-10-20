from __future__ import print_function

import slicer
from slicer.ScriptedLoadableModule import *

import vtk, qt, ctk

import os

import ShapeStatistics

#Debug line, permit to modify ShapeStatistics
#without relaunching Slicer
reload(ShapeStatistics)



########################################################################################
#                                   MODULE CLASS                                       #
########################################################################################

#Uses ScriptedLoadableModule base class, available at:
#https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
class ShapeStats(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        parent.title = "ShapeStats"
        parent.categories = ["Statistics"]
        parent.dependencies = []
        parent.contributors = ["Lopez Mateo (University of North Carolina)"]
        parent.helpText = """
            ...
            """
        parent.acknowledgementText = """
            ...
            """



########################################################################################
#                                   WIDGET CLASS                                       #
########################################################################################

class ShapeStatsWidget(ScriptedLoadableModuleWidget):
    #Variable initialisation and widgets confguration
    def setup(self):

        ScriptedLoadableModuleWidget.setup(self)        

        # Global Variables
        self.logic = ShapeStatsLogic(self)

        self.current_file_A = None
        self.current_file_B = None

        self.result_labels = [[]]


        #############################################
        # ---- Loading interface from .ui file ---- #
        #############################################

        self.moduleName = 'ShapeStats'
        scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.moduleName)
        self.widget = slicer.util.loadUI(path)
        self.layout.addWidget(self.widget)

        #############################
        # ---- Widget recovery ---- #
        #############################

        #Shape Selection
        self.pathLineEdit_fileA=self.logic.get('pathLineEdit_fileA')
        self.pathLineEdit_fileB=self.logic.get('pathLineEdit_fileB')

        #Parameters
        self.spinBox_bins=self.logic.get('spinBox_bins')
        self.comboBox_distanceType=self.logic.get('comboBox_distanceType')
        self.comboBox_correspondence=self.logic.get('comboBox_correspondence')

        #Translation
        self.horizontalSlider_translation=self.logic.get('horizontalSlider_translation')

        #Colors
        self.doubleSpinBox_minimum=self.logic.get('doubleSpinBox_minimum')
        self.doubleSpinBox_maximum=self.logic.get('doubleSpinBox_maximum')
        self.horizontalSlider_color=self.logic.get('horizontalSlider_color')

        #Results
        self.gridLayout_results=self.logic.get('gridLayout_results')
        self.comboBox_mode=self.logic.get('comboBox_mode')

        #Buttons
        self.pushButton_compute=self.logic.get('pushButton_compute')
        self.pushButton_save=self.logic.get('pushButton_save')

        #################################################
        # ---- Widget configuration and connection ---- #
        #################################################

        self.initializeWidgetConfiguration()

    #initialize all the widgets configurations at their default state
    def initializeWidgetConfiguration(self):
        #Shape Selection
        self.pathLineEdit_fileA.setCurrentPath(' ')
        self.pathLineEdit_fileA.connect('currentPathChanged(const QString)', self.onLoadFileA)

        self.pathLineEdit_fileB.setCurrentPath(' ')
        self.pathLineEdit_fileB.connect('currentPathChanged(const QString)', self.onLoadFileB)

        #Parameters
        self.spinBox_bins.setMinimum(5)
        self.spinBox_bins.setMaximum(9999999)
        self.spinBox_bins.setValue(256)

        self.comboBox_distanceType.addItem('Signed Distance')
        self.comboBox_distanceType.addItem('Unsigned Distance')

        self.comboBox_correspondence.addItem('Yes')
        self.comboBox_correspondence.addItem('No')

        #Translation
        self.horizontalSlider_translation.setMinimum(0)
        self.horizontalSlider_translation.setMaximum(500)
        self.horizontalSlider_translation.setValue(0)
        self.horizontalSlider_translation.setDisabled(True)
        self.horizontalSlider_translation.connect('valueChanged(int)',self.onTranslation)

        #Colors
        self.doubleSpinBox_minimum.setDisabled(True)

        self.doubleSpinBox_maximum.setDisabled(True)

        self.horizontalSlider_color.setMinimum(-1000)
        self.horizontalSlider_color.setMaximum(1000)
        self.horizontalSlider_color.setValue(0)
        self.horizontalSlider_color.setDisabled(True)

        #Results
        self.comboBox_mode.clear()
        self.comboBox_mode.setDisabled(True)
        self.comboBox_mode.connect('currentIndexChanged(const QString)',self.onModeChanged)

        #Buttons
        self.pushButton_compute.connect('clicked()', self.onCompute)
        self.pushButton_compute.setDisabled(True)

        self.pushButton_save.connect('clicked()', self.onSave)
        self.pushButton_save.setDisabled(True)

    # function called each time that the user "enter" in Diagnostic Index interface
    def enter(self):
        #TODO
        pass

    # function called each time that the user "exit" in Diagnostic Index interface
    def exit(self):
        #TODO
        pass

    
    #------------------------------------------------------#    
    #                   Events Functions                   #
    #------------------------------------------------------#

    # function called each time that the scene is closed (if Diagnostic Index has been initialized)
    def onCloseScene(self, obj, event):
        print('close scene')
        #self.logic.deleteAll3DVisualisationNodes()
        #self.logic.delete2DVisualisationNodes()
        self.initializeWidgetConfiguration()

    #Action to do when file A is setted
    def onLoadFileA(self,fileA_path):
        print('debut')
        if self.logic.checkExtension(fileA_path,'.vtk'):
            print('Loading file A ...',end=' ')
            self.current_file_A=fileA_path
            self.logic.stats.SetA(fileA_path)
            pos_x=self.horizontalSlider_translation.value
            self.logic.showA(posX=pos_x)
            print('Done!')

            if self.logic.stats.IsReady():
                self.horizontalSlider_translation.setEnabled(True)
                self.pushButton_compute.setEnabled(True)

        elif self.current_file_A:
            self.pathLineEdit_fileA.setCurrentPath(self.current_file_A)
        else:
            self.pathLineEdit_fileA.setCurrentPath(' ')

    #Action to do when file B is setted
    def onLoadFileB(self,fileB_path):
        if self.logic.checkExtension(fileB_path,'.vtk'):
            print('Loading file B ...',end=' ')
            self.current_file_B=fileB_path
            self.logic.stats.SetB(fileB_path)
            pos_x=self.horizontalSlider_translation.value
            self.logic.showB(posX=-pos_x)
            print('Done!')

            if self.logic.stats.IsReady():
                self.horizontalSlider_translation.setEnabled(True)
                self.pushButton_compute.setEnabled(True)

        elif self.current_file_B:
            self.pathLineEdit_fileB.setCurrentPath(self.current_file_B)
        else:
            self.pathLineEdit_fileB.setCurrentPath(' ')

    #Action to do when compute button is pushed
    def onCompute(self):
        print('Computing ...',end=' ')

        #Getting parameters
        nb_bins=self.spinBox_bins.value

        signed=False
        if self.comboBox_distanceType.currentText == 'Signed Distance':
            signed=True

        correspondence=False
        if self.comboBox_correspondence.currentText == 'Yes':
            correspondence=True

        #computing
        self.logic.computeStats(nb_bins,signed,correspondence)
        
        #Show Results
        self.comboBox_mode.disconnect('currentIndexChanged(const QString)',self.onModeChanged)
        if signed == False and correspondence == True:
            self.comboBox_mode.clear()
            self.comboBox_mode.addItem('A<->B')
            self.comboBox_mode.setDisabled(True)
            mode='A<->B'
        else:
            self.comboBox_mode.clear()
            self.comboBox_mode.addItem('A->B')
            self.comboBox_mode.addItem('B->A')
            self.comboBox_mode.addItem('A->B & B->A')
            self.comboBox_mode.setEnabled(True)
            mode='A->B'
        self.comboBox_mode.connect('currentIndexChanged(const QString)',self.onModeChanged)

        #show results
        self.onModeChanged(mode)

        #show plot
        self.logic.generate2DVisualisationNodes(mode)


        print('Done!')

    #Action to do when the mode change
    def onModeChanged(self,mode):
        self.deleteResultsLabels()

        self.result_labels=self.logic.formatStats(mode)

        for i in range(len(self.result_labels)):
            label = self.result_labels[i]
            self.gridLayout_results.addWidget(label[0],i+1,1)
            self.gridLayout_results.addWidget(label[1],i+1,2)

        self.logic.showDistance(mode)

    #Action to do when the translation slider have been moved
    def onTranslation(self,value):
        self.logic.updateTransform('A',value)
        self.logic.updateTransform('B',value)

    #Action to do when save button is pushed
    def onSave(self):
        print('Saving ...',end=' ')

        print('Done!')


    #------------------------------------------------------#    
    #                  Utility Functions                   #
    #------------------------------------------------------#

    #delete all the labels shown in the result section
    #at the end of execution, self.result_labels = [[]]
    def deleteResultsLabels(self):
        for i in range(len(self.result_labels)):
            try:
                self.result_labels[i][0].deleteLater()
                self.result_labels[i][1].deleteLater()
            except:
                pass
        self.result_labels=[[]]


########################################################################################
#                                   LOGIC CLASS                                        #
########################################################################################

class ShapeStatsLogic(ScriptedLoadableModuleLogic):
    def __init__(self, interface):
        self.interface = interface

        self.stats=ShapeStatistics.ShapeStatisticsLogic()

        self.generateLUT()

        self.stats_dict=dict()

        self.shapeA_name='Shape A'
        self.shapeB_name='Shape B'

    #------------------------------------------------------#    
    #                   Common Functions                   #
    #------------------------------------------------------#

    #Function to recovery a widget in the .ui file
    def get(self, objectName):
        
        return slicer.util.findChild(self.interface.widget, objectName)

    #Check if the file given has the right extension
    def checkExtension(self, filename, extension):
        if os.path.splitext(os.path.basename(filename))[1] == extension : 
            return True
        elif os.path.basename(filename) == "" or os.path.basename(filename) == " " :
            return False
        slicer.util.errorDisplay("Wrong file extension, a '" + extension + "' file is needed!")
        return False


    #------------------------------------------------------#    
    #                 Statistics Functions                 #
    #------------------------------------------------------#

    #function to compute the histogram with the given parameters:
    #nb_bins: number of bins to compute the historgram
    #signed: True or False, specify if signed distance should be computed or not.
    #        If not, absolute distances are computed
    #correspondence: True or False, specify if a point to point correspondence should be used to compute the distances.
    #        If not, closest point distances are computed 
    #results:
    #initialise self.stats_dict, it contains the results for each mode (A->B / B->A / A->B & B->A) 
    # if correspondence = True and signed = False, only one mode is computed (A<->B)
    def computeStats(self,nb_bins,signed,correspondence):
        self.stats_dict=dict()

        if signed == False and correspondence == True:
            mode = 'A<->B'
            stats_result=self.stats.ComputeValues(signed=signed,bins=nb_bins,correspondence=correspondence,mode=mode)
            self.stats_dict[mode]=stats_result

        else:
            mode='A->B'
            stats_result=self.stats.ComputeValues(signed=signed,bins=nb_bins,correspondence=correspondence,mode=mode)
            self.stats_dict[mode]=stats_result

            mode='B->A'
            stats_result=self.stats.ComputeValues(signed=signed,bins=nb_bins,correspondence=correspondence,mode=mode)
            self.stats_dict[mode]=stats_result

            mode='A->B & B->A'
            stats_result=self.stats.ComputeValues(signed=signed,bins=nb_bins,correspondence=correspondence,mode=mode)
            self.stats_dict[mode]=stats_result

    #function to generate results Qlabels
    #return an array of array containing the Qlabels to show in function of the desired mode.
    #Mode can be 'A<->B' or A->B' or 'B->A' or 'A->B & B->A'
    #QLabel_array=[[QLabel_key1,QLabel_value1],
    #                         ...
    #              [QLabel_keyN,QLabel_valueN]]
    def formatStats(self,mode):
        value_order=['number_of_bins','signed_distances','corresponding_points_exist','minimum',\
        'maximum','hausdorf','mean','sigma','MSD','MAD','median','IQR','IQR_Q1','IQR_Q3']

        results=self.stats_dict[mode]

        QLabel_array=list()
        for key in value_order:
            QLabel_array.append([qt.QLabel(key+':'),qt.QLabel(results[key])])

        return QLabel_array
    

    #------------------------------------------------------#    
    #                    Plots Functions                   #
    #------------------------------------------------------#

    #function that create and show in Slicer all the nodes needed to display the histograms in a plot view
    #if mode = 'A<->B', one graph is generated
    #if mode != 'A<->B', 3 graph are generated
    def generate2DVisualisationNodes(self,mode):
        #clean previously created nodes
        self.delete2DVisualisationNodes()

        #generate PlotChartNodes to visualize the histograms
        if mode == 'A<->B':
            histogramPCN = self.generate1HistogramPlot()
        else:
            histogramPCN = self.generate3HistogramPlot()

        # Switch to a layout that contains a plot view to create a plot widget
        layoutManager = slicer.app.layoutManager()
        layoutWithPlot = slicer.modules.plots.logic().GetLayoutWithPlot(layoutManager.layout)
        layoutManager.setLayout(layoutWithPlot)

        # Select chart in plot view
        plotWidget = layoutManager.plotWidget(0)
        self.plotViewNode = plotWidget.mrmlPlotViewNode()

        self.plotViewNode.SetPlotChartNodeID(histogramPCN.GetID())

    #function to delete every Slicer node related to plots
    #that could have been created by this module
    def delete2DVisualisationNodes(self):
        node = slicer.mrmlScene.GetFirstNodeByName("Histograms Table")
        if node is not None:
            slicer.mrmlScene.RemoveNode(node)

        node = slicer.mrmlScene.GetFirstNodeByName("Histogram A->B")
        if node is not None:
            slicer.mrmlScene.RemoveNode(node)

        node = slicer.mrmlScene.GetFirstNodeByName("Histogram B->A")
        if node is not None:
            slicer.mrmlScene.RemoveNode(node)

        node = slicer.mrmlScene.GetFirstNodeByName("Histogram A->B & B->A")
        if node is not None:
            slicer.mrmlScene.RemoveNode(node)

        node = slicer.mrmlScene.GetFirstNodeByName("Histogram A<->B")
        if node is not None:
            slicer.mrmlScene.RemoveNode(node)

        node = slicer.mrmlScene.GetFirstNodeByName("Histograms plot chart")
        if node is not None:
            slicer.mrmlScene.RemoveNode(node)

    #function that create the plot chart node containing all the histograms to show:
    #   -A->B histogram
    #   -B->A histogram
    #   -A->B & B-.A histogram
    def generate3HistogramPlot(self):
        histogramTableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode","Histograms Table")
        table = histogramTableNode.GetTable()

        
        histAB, edgeAB=self.getHistogramAsVTKFloatArray('A->B')
        histBA, edgeBA=self.getHistogramAsVTKFloatArray('B->A')
        histABBA, edgeABBA=self.getHistogramAsVTKFloatArray('A->B & B->A')



        edgeAB.SetName("edgeAB")
        histAB.SetName("histAB")
        edgeBA.SetName("edgeBA")
        histBA.SetName("histBA")
        edgeABBA.SetName("edgeABBA")
        histABBA.SetName("histABBA")


        table.AddColumn(edgeAB)
        table.AddColumn(histAB)
        table.AddColumn(edgeBA)
        table.AddColumn(histBA)
        table.AddColumn(edgeABBA)
        table.AddColumn(histABBA)


        #histogram A->B plot serie
        ABPlotSeries = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "Histogram A->B")
        ABPlotSeries.SetAndObserveTableNodeID(histogramTableNode.GetID())
        ABPlotSeries.SetXColumnName("edgeAB")
        ABPlotSeries.SetYColumnName("histAB")
        ABPlotSeries.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatter)
        ABPlotSeries.SetUniqueColor()

        #histogram B->A plot serie
        BAPlotSeries = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "Histogram B->A")
        BAPlotSeries.SetAndObserveTableNodeID(histogramTableNode.GetID())
        BAPlotSeries.SetXColumnName("edgeBA")
        BAPlotSeries.SetYColumnName("histBA")
        BAPlotSeries.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatter)
        BAPlotSeries.SetUniqueColor()

        #histogram A->B plot serie
        ABBAPlotSeries = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "Histogram A->B & B->A")
        ABBAPlotSeries.SetAndObserveTableNodeID(histogramTableNode.GetID())
        ABBAPlotSeries.SetXColumnName("edgeABBA")
        ABBAPlotSeries.SetYColumnName("histABBA")
        ABBAPlotSeries.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatter)
        ABBAPlotSeries.SetUniqueColor()

        # Create variance plot chart node
        plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode","Histograms plot chart")
        plotChartNode.AddAndObservePlotSeriesNodeID(ABPlotSeries.GetID())
        plotChartNode.AddAndObservePlotSeriesNodeID(BAPlotSeries.GetID())
        plotChartNode.AddAndObservePlotSeriesNodeID(ABBAPlotSeries.GetID())
        plotChartNode.SetTitle('Histograms')
        plotChartNode.SetXAxisTitle('Distance')
        plotChartNode.SetYAxisTitle('Value') 

        return plotChartNode

    #function that create the plot chart node containing one histogram:
    #   -A<->B histogram
    def generate1HistogramPlot(self):
        histogramTableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode","Histograms Table")
        table = histogramTableNode.GetTable()

        hist, edge=self.getHistogramAsVTKFloatArray('A<->B')

        edge.SetName("edge")
        hist.SetName("hist")

        table.AddColumn(edge)
        table.AddColumn(hist)

        #histogram A->B plot serie
        PlotSeries = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "Histogram A<->B")
        PlotSeries.SetAndObserveTableNodeID(histogramTableNode.GetID())
        PlotSeries.SetXColumnName("edge")
        PlotSeries.SetYColumnName("hist")
        PlotSeries.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatter)
        PlotSeries.SetUniqueColor()

        # Create variance plot chart node
        plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode","Histograms plot chart")
        plotChartNode.AddAndObservePlotSeriesNodeID(PlotSeries.GetID())
        plotChartNode.SetTitle('Histograms')
        plotChartNode.SetXAxisTitle('Distance')
        plotChartNode.SetYAxisTitle('Value') 

        return plotChartNode

    #function that returns the histogram and the edge of the selected mode in a VTKFloat array
    def getHistogramAsVTKFloatArray(self,mode):
        hist=self.stats_dict[mode]['histogram']
        edge=self.stats_dict[mode]['edge_mean']

        vtkhist=self.generateVTKFloatArrayFromNumpy(hist)
        vtkedge=self.generateVTKFloatArrayFromNumpy(edge)

        return vtkhist, vtkedge


    #------------------------------------------------------#    
    #            Shapes visualization Functions            #
    #------------------------------------------------------#

    #function to show in slicer mrml scene the shape A
    #color is red
    #shape is translated in the x axis by posX
    def showA(self,posX=0):
        self.delete3DVisualisationNodes(self.shapeA_name)
        polydata = self.stats.getShapeAPolydata()
        self.autoOrientNormals(polydata)
        self.generate3DVisualisationNode(polydata,self.shapeA_name,color=(0.9,0.1,0.1),initial_pos_x=posX)

    #function to show in slicer mrml scene the shape B
    #color is blue
    #shape is translated in the x axis by posX
    def showB(self,posX=0):
        self.delete3DVisualisationNodes(self.shapeB_name)
        polydata = self.stats.getShapeBPolydata()
        self.autoOrientNormals(polydata)
        self.generate3DVisualisationNode(polydata,self.shapeB_name,color=(0.1,0.1,0.9),initial_pos_x=posX)

    #function that create a model node and his associated model display and transform node
    #The Nodes are also added to slicer's mrmlScene
    #Need a vtk polydata object, a color and a name to identify the nodes 
    #if translate is True, the object will be tranlated
    def generate3DVisualisationNode(self,polydata,name,color=(1,1,1),initial_pos_x=0):
        #create Model Node
        shape_node = slicer.vtkMRMLModelNode()
        shape_node.SetAndObservePolyData(polydata)
        shape_node.SetName(name)
        #create display node
        model_display = slicer.vtkMRMLModelDisplayNode()
        model_display.SetColor(color[0],color[1],color[2]) 
        model_display.AutoScalarRangeOff()
        model_display.SetScene(slicer.mrmlScene)
        model_display.SetName("Display "+name)

        #create transform node
        transform=vtk.vtkTransform()
        transform.Translate(initial_pos_x,0,0)
        transform_node=slicer.vtkMRMLTransformNode()
        transform_node.SetName("Translation "+name)
        transform_node.SetAndObserveTransformToParent(transform)

        #Add Nodes to Slicer
        slicer.mrmlScene.AddNode(transform_node)
        slicer.mrmlScene.AddNode(model_display)
        slicer.mrmlScene.AddNode(shape_node)

        #Link nodes
        shape_node.SetAndObserveTransformNodeID(transform_node.GetID())
        shape_node.SetAndObserveDisplayNodeID(model_display.GetID())

    #function to delete a model node and his associated model display node
    #using the name used during their creation
    def delete3DVisualisationNodes(self,name):
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if node is not None:
            slicer.mrmlScene.RemoveNode(node)
        node = slicer.mrmlScene.GetFirstNodeByName("Display "+name)
        if node is not None:
            slicer.mrmlScene.RemoveNode(node)
        node = slicer.mrmlScene.GetFirstNodeByName("Translation "+name)
        if node is not None:
            slicer.mrmlScene.RemoveNode(node)

    #function to delete every Slicer node related to 3D Shapes
    #that could have been created by this module
    def deleteAll3DVisualisationNodes(self):
        self.delete3DVisualisationNodes(self.shapeA_name)
        self.delete3DVisualisationNodes(self.shapeB_name)

        node = slicer.mrmlScene.GetFirstNodeByName('ShapeStats Distance Color Table')
        if node is not None:
            slicer.mrmlScene.RemoveNode(node)

    #function to compute automaticaly the normals of a polydata
    def autoOrientNormals(self, model):
        normals = vtk.vtkPolyDataNormals()
        normals.SetAutoOrientNormals(True)
        normals.SetFlipNormals(False)
        normals.SetSplitting(False)
        normals.ConsistencyOn()
        normals.SetInputData(model)
        normals.Update()
        normalspoint=normals.GetOutput().GetPointData().GetArray("Normals")
        model.GetPointData().SetNormals(normalspoint)

    #function to update the transform(translation on the x axis) Node of the shape B
    def updateTransform(self,shape,value):\
        #translation shape A
        if shape == 'A':
            transform_node = slicer.mrmlScene.GetFirstNodeByName("Translation "+self.shapeA_name)
            transform=vtk.vtkTransform()
            transform.Translate(value,0,0)
            transform_node.SetAndObserveTransformToParent(transform)

        #translation shape B
        if shape == 'B':
            transform_node = slicer.mrmlScene.GetFirstNodeByName("Translation "+self.shapeB_name)
            transform=vtk.vtkTransform()
            transform.Translate(-value,0,0)
            transform_node.SetAndObserveTransformToParent(transform)


    #------------------------------------------------------#    
    #            Color visualization Functions             #
    #------------------------------------------------------#

    #generate a color table node going from blue to green to red.
    #It will be used as look up table to visualise distances on shapes
    def generateLUT(self):
        colorlow = (0,0,1)
        colormid = (0,1,0)
        colorhigh= (1,0,0)

        #should be an odd number
        total_number_of_colors=256

        colorTableNode = slicer.vtkMRMLColorTableNode()
        colorTableNode.SetName('ShapeStats Color Table')
        colorTableNode.SetTypeToUser()
        colorTableNode.HideFromEditorsOff()
        colorTableNode.SaveWithSceneOff()
        colorTableNode.SetNumberOfColors(total_number_of_colors)
        colorTableNode.GetLookupTable().SetTableRange(0,total_number_of_colors-1)

        number_of_colors=total_number_of_colors/2

        #from colorlow to colormid
        for i in range(number_of_colors):
            alpha=float(i)/(number_of_colors-1)
            r=colorlow[0]*(1-alpha)+colormid[0]*alpha 
            g=colorlow[1]*(1-alpha)+colormid[1]*alpha 
            b=colorlow[2]*(1-alpha)+colormid[2]*alpha 

            colorTableNode.AddColor(str(i), r, g, b, 1)  

        #from colormid to colorhigh
        for i in range(number_of_colors):
            alpha=float(i)/(number_of_colors-1)
            r=colormid[0]*(1-alpha)+colorhigh[0]*alpha 
            g=colormid[1]*(1-alpha)+colorhigh[1]*alpha 
            b=colormid[2]*(1-alpha)+colorhigh[2]*alpha 

            colorTableNode.AddColor(str(number_of_colors+i), r, g, b, 1)  

        colorTableNode.SetName('ShapeStats Distance Color Table')
        slicer.mrmlScene.AddNode(colorTableNode)

    #Show the distances on the corresponding(s) polydata in function of the mode
    #if mode == 'A<->B' the color is only shown on the shape A
    def showDistance(self,mode):
        if mode == 'A->B':
            #set polydata scalars
            distance = self.stats_dict[mode]['distances'][0]
            polydata=self.stats.getShapeAPolydata()
            self.setPolyDataDistanceScalars(polydata,distance)

            #Set model node to use our LUT and set the range
            self.setModelNodeLUT(mode,self.shapeA_name)
            
            #enable/disable scalar visibility
            self.enableScalarView(self.shapeA_name)
            self.disableScalarView(self.shapeB_name)

        if mode == 'B->A':
            #set polydata scalars
            distance = self.stats_dict[mode]['distances'][0]
            polydata=self.stats.getShapeBPolydata()
            self.setPolyDataDistanceScalars(polydata,distance)

            #Set model node to use our LUT and set the range
            self.setModelNodeLUT(mode,self.shapeB_name)
            
            #enable/disable scalar visibility
            self.enableScalarView(self.shapeB_name)
            self.disableScalarView(self.shapeA_name)

        if mode == 'A<->B':
            #set polydata scalars
            distance = self.stats_dict[mode]['distances'][0]
            polydata=self.stats.getShapeAPolydata()
            self.setPolyDataDistanceScalars(polydata,distance)

            #Set model node to use our LUT and set the range
            self.setModelNodeLUT(mode,self.shapeA_name)
            
            #enable/disable scalar visibility
            self.enableScalarView(self.shapeA_name)
            self.disableScalarView(self.shapeB_name)

        if mode == 'A->B & B->A':
            #A->B
            #set polydata scalars
            distance = self.stats_dict[mode]['distances'][0]
            polydata=self.stats.getShapeAPolydata()
            self.setPolyDataDistanceScalars(polydata,distance)

            #Set model node to use our LUT and set the range
            self.setModelNodeLUT(mode,self.shapeA_name)

            #B->A
            #set polydata scalars
            distance = self.stats_dict[mode]['distances'][1]
            polydata=self.stats.getShapeBPolydata()
            self.setPolyDataDistanceScalars(polydata,distance)

            #Set model node to use our LUT and set the range
            self.setModelNodeLUT(mode,self.shapeB_name)

            #enable scalar view
            self.enableScalarView(self.shapeA_name)
            self.enableScalarView(self.shapeB_name)

    #set the LUT of the model node named name and
    #set scalar range to min distance/max distance 
    def setModelNodeLUT(self,mode,name):
        shapeBnode=slicer.mrmlScene.GetFirstNodeByName(name)
        colornode = slicer.mrmlScene.GetFirstNodeByName('ShapeStats Distance Color Table')
        if (shapeBnode is not None) and (colornode is not None):

            maxi=self.stats_dict[mode]['maximum']
            mini=self.stats_dict[mode]['minimum']

            node = slicer.mrmlScene.GetFirstNodeByName("Display "+name)
            node.SetScalarRange(mini,maxi)

            shapeBnode.GetDisplayNode().SetAndObserveColorNodeID(colornode.GetID())
            shapeBnode.Modified()

    #take a numpy array distance, convert it in a vtkfloat array 
    #and set the scalars of polydata with this array 
    def setPolyDataDistanceScalars(self,polydata,distance):
        distance=self.generateVTKFloatArrayFromNumpy(distance)
        distance.SetName("Distance")

        polydata.GetPointData().SetScalars(distance)
        polydata.GetPointData().Modified()

    #enable scalar view on the model node created with the name parameter
    def enableScalarView(self,name):
        shape_node=slicer.mrmlScene.GetFirstNodeByName(name)
        shape_node.GetDisplayNode().SetActiveScalarName('Distance')
        shape_node.GetDisplayNode().SetScalarVisibility(1)

    #disable scalar view on the model node created with the name parameter
    def disableScalarView(self,name):
        shape_node=slicer.mrmlScene.GetFirstNodeByName(name)
        shape_node.GetDisplayNode().SetScalarVisibility(0)

    #------------------------------------------------------#    
    #                  Utility Functions                   #
    #------------------------------------------------------#

    #function that convert a 1 dimensional numpy array into a VTKFloat array
    def generateVTKFloatArrayFromNumpy(self,np_array):
        size = np_array.size

        vtk_float = vtk.vtkFloatArray()
        vtk_float.SetNumberOfComponents(1)
        for i in range(size):
            vtk_float.InsertNextTuple([np_array[i]])
        return vtk_float


########################################################################################
#                                   TEST CLASS                                         #
########################################################################################

class ShapeStatsTest(ScriptedLoadableModuleTest):
    pass