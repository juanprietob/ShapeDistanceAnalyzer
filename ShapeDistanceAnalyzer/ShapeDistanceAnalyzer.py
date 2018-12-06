from __future__ import print_function

import os, sys
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

import csv
import json
import numpy as np
import ShapeStatistics

#Debug line, permit to modify ShapeStatistics
#without relaunching Slicer
reload(ShapeStatistics)



########################################################################################
#                                   MODULE CLASS                                       #
########################################################################################

#Uses ScriptedLoadableModule base class, available at:
#https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
class ShapeDistanceAnalyzer(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        parent.title = "ShapeDistanceAnalyzer"
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

class ShapeDistanceAnalyzerWidget(ScriptedLoadableModuleWidget):

    #------------------------------------------------------#    
    #         Setup and configuration Functions            #
    #------------------------------------------------------#

    #Variable initialisation and widgets confguration
    def setup(self):

        ScriptedLoadableModuleWidget.setup(self)        

        # Global Variables
        self.logic = ShapeDistanceAnalyzerLogic(self)

        self.current_file_A = None
        self.current_file_B = None

        self.result_labels = [[]]

        #Load the interface from .ui file
        self.moduleName = 'ShapeDistanceAnalyzer'
        scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.moduleName)
        self.widget = slicer.util.loadUI(path)
        self.layout.addWidget(self.widget)

        #get, configure and connect widgets and add the colorscale widget
        self.getWidgets()

        self.defaultConfigWidget()
        self.connectWidget()

        #mrmlScene observers
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, self.onCloseScene)
        
        if not os.path.exists(slicer.app.temporaryPath):            
            os.path.mkdirs(slicer.app.temporaryPath)

    #get all needed widget from the .ui file that describe the module interface
    def getWidgets(self):
        #Shape Selection
        self.pathLineEdit_fileA=self.logic.get('pathLineEdit_fileA')
        self.pathLineEdit_fileB=self.logic.get('pathLineEdit_fileB')

        #Parameters
        self.spinBox_bins=self.logic.get('spinBox_bins')
        self.comboBox_distanceType=self.logic.get('comboBox_distanceType')
        self.comboBox_correspondence=self.logic.get('comboBox_correspondence')
        self.spinBox_sampling=self.logic.get('spinBox_sampling')

        #Translation
        self.horizontalSlider_translation=self.logic.get('horizontalSlider_translation')

        #Colors
        self.doubleSpinBox_minimum=self.logic.get('doubleSpinBox_minimum')
        self.doubleSpinBox_maximum=self.logic.get('doubleSpinBox_maximum')
        self.ctkRangeSlider_color=self.logic.get('ctkRangeSlider_color')
        self.label_colorMin=self.logic.get('label_colorMin')
        self.label_colorMax=self.logic.get('label_colorMax')

        #Results
        self.gridLayout_results=self.logic.get('gridLayout_results')
        self.comboBox_mode=self.logic.get('comboBox_mode')

        #Buttons
        self.pushButton_compute=self.logic.get('pushButton_compute')
        self.pushButton_save=self.logic.get('pushButton_save')

    #initialize all the widgets configurations at their default state
    def defaultConfigWidget(self):
        #Shape Selection
        self.pathLineEdit_fileA.setCurrentPath(' ')
        self.pathLineEdit_fileB.setCurrentPath(' ')

        #Parameters
        self.spinBox_bins.setMinimum(5)
        self.spinBox_bins.setMaximum(9999999)
        self.spinBox_bins.setValue(256)

        self.comboBox_distanceType.clear()
        self.comboBox_distanceType.addItem('Signed Distance')
        self.comboBox_distanceType.addItem('Unsigned Distance')

        self.comboBox_correspondence.clear()
        self.comboBox_correspondence.addItem('Yes')
        self.comboBox_correspondence.addItem('No')

        self.spinBox_sampling.setMinimum(0)
        self.spinBox_sampling.setMaximum(50)
        self.spinBox_sampling.setValue(0)

        #Translation
        self.horizontalSlider_translation.setMinimum(0)
        self.horizontalSlider_translation.setMaximum(400)
        self.horizontalSlider_translation.setValue(200)
        self.horizontalSlider_translation.setDisabled(True)

        #Colors
        self.doubleSpinBox_minimum.setDisabled(True)

        self.doubleSpinBox_maximum.setDisabled(True)

        self.ctkRangeSlider_color.setMinimumValue(0)
        self.ctkRangeSlider_color.setMaximumValue(99)
        self.ctkRangeSlider_color.setValues(0,99)
        self.ctkRangeSlider_color.setDisabled(True)
        self.label_colorMax.setStyleSheet("QLabel{background-color:rgb(255,26,26);}")
        self.label_colorMin.setStyleSheet("QLabel{background-color:rgb(26,26,255);}")

        #Results
        self.comboBox_mode.clear()
        self.comboBox_mode.setDisabled(True)

        #Buttons
        self.pushButton_compute.setDisabled(True)

        self.pushButton_save.setDisabled(True)

    #connect widgets signal to their corresponding slot 
    def connectWidget(self):
        #Shape Selection
        self.pathLineEdit_fileA.connect('currentPathChanged(const QString)', self.onLoadFileA)
        self.pathLineEdit_fileB.connect('currentPathChanged(const QString)', self.onLoadFileB)

        #Parameters
 
        #Translation
        self.horizontalSlider_translation.connect('valueChanged(int)',self.onTranslation)

        #Colors
        self.doubleSpinBox_minimum.connect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)
        self.doubleSpinBox_maximum.connect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)
        self.ctkRangeSlider_color.connect('valuesChanged(int,int)',self.onSliderScalarRangeChanged)

        #Results
        self.comboBox_mode.connect('currentIndexChanged(const QString)',self.onModeChanged)

        #Buttons
        self.pushButton_compute.connect('clicked()', self.onCompute)
        self.pushButton_save.connect('clicked()', self.onSave)

    #disconnect widgets signal 
    def disconnectWidget(self):
        #Shape Selection
        self.pathLineEdit_fileA.disconnect('currentPathChanged(const QString)', self.onLoadFileA)
        self.pathLineEdit_fileB.disconnect('currentPathChanged(const QString)', self.onLoadFileB)

        #Parameters
 
        #Translation
        self.horizontalSlider_translation.disconnect('valueChanged(int)',self.onTranslation)

        #Colors
        self.doubleSpinBox_minimum.disconnect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)
        self.doubleSpinBox_maximum.disconnect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)
        self.ctkRangeSlider_color.disconnect('valuesChanged(int,int)',self.onSliderScalarRangeChanged)

        #Results
        self.comboBox_mode.disconnect('currentIndexChanged(const QString)',self.onModeChanged)

        #Buttons
        self.pushButton_compute.disconnect('clicked()', self.onCompute)
        self.pushButton_save.disconnect('clicked()', self.onSave)

    #Activate the interface when two files are loaded
    def activateInterface(self):
        if self.logic.IsCorrespondencePossible(self.pathLineEdit_fileA.currentPath,self.pathLineEdit_fileB.currentPath):
            index=self.comboBox_correspondence.findText('Yes')
            self.comboBox_correspondence.setCurrentIndex(index)
            self.comboBox_correspondence.setEnabled(True)
        else:
            index=self.comboBox_correspondence.findText('No')
            self.comboBox_correspondence.setCurrentIndex(index)
            self.comboBox_correspondence.setDisabled(True)

        self.x_range=self.logic.getXRange()
        self.onTranslation(200)
        self.horizontalSlider_translation.setValue(200)
        self.horizontalSlider_translation.setEnabled(True)

        self.pushButton_compute.setEnabled(True)

        self.deleteResultsLabels()
        self.comboBox_mode.disconnect('currentIndexChanged(const QString)',self.onModeChanged)
        self.comboBox_mode.setCurrentIndex(-1)
        self.comboBox_mode.setDisabled(True)
        self.pushButton_save.setDisabled(True)
        self.doubleSpinBox_minimum.setDisabled(True)
        self.doubleSpinBox_maximum.setDisabled(True)

        self.ctkRangeSlider_color.disconnect('valuesChanged(int,int)',self.onSliderScalarRangeChanged)
        self.ctkRangeSlider_color.setValues(0,99)
        self.ctkRangeSlider_color.setDisabled(True)
        self.ctkRangeSlider_color.connect('valuesChanged(int,int)',self.onSliderScalarRangeChanged)

    #------------------------------------------------------#    
    #                   Events Functions                   #
    #------------------------------------------------------#

    # function called each time that the scene is closed (if Diagnostic Index has been initialized)
    def onCloseScene(self, obj, event):
        print('close scene')
        self.disconnectWidget()
        self.defaultConfigWidget()
        self.connectWidget()
        self.logic.generateLUT()

    #Action to do when file A is setted
    def onLoadFileA(self,fileA_path):
        if self.logic.checkExtension(fileA_path,'.vtk'):
            print('Loading file A ...',end=' ')
            self.current_file_A=fileA_path
            self.logic.stats.Set('A',fileA_path)
            self.logic.show('A',self.current_file_A,color=(1,0,0))
            self.AddDisplayNodeChangedObserver('Shape A')
            print('Done!')

            if self.logic.stats.IsReady():
                self.activateInterface()
                self.logic.disableAllScalarViews()
                self.deleteResultsLabels()


        elif self.current_file_A:
            self.pathLineEdit_fileA.setCurrentPath(self.current_file_A)
        else:
            self.pathLineEdit_fileA.setCurrentPath(' ')

    #Action to do when file B is setted
    def onLoadFileB(self,fileB_path):
        if self.logic.checkExtension(fileB_path,'.vtk'):
            print('Loading file B ...',end=' ')
            self.current_file_B=fileB_path
            self.logic.stats.Set('B',fileB_path)
            self.logic.show('B',self.current_file_B,color=(0,0,1))
            self.AddDisplayNodeChangedObserver('Shape B')

            print('Done!')

            if self.logic.stats.IsReady():
                self.activateInterface()
                self.logic.disableAllScalarViews()


        elif self.current_file_B:
            self.pathLineEdit_fileB.setCurrentPath(self.current_file_B)
        else:
            self.pathLineEdit_fileB.setCurrentPath(' ')

    #Action to do when compute button is pushed
    def onCompute(self):
        print('Computing ...')
        sampling_level=self.spinBox_sampling.value

        #sampling
        if sampling_level>0:
            fileA=self.pathLineEdit_fileA.currentPath
            fileB=self.pathLineEdit_fileB.currentPath

            self.logic.samplePolydatas(fileA,fileB,sampling_level)

            self.checkThreadTimer=qt.QTimer()
            self.checkThreadTimer.connect('timeout()', self.onCheckSampling)
            self.checkThreadTimer.start(100)

            self.pushButton_compute.setText('Sampling ...')
            self.pushButton_compute.setDisable(True)
            #self.pushButton_compute.Disable(True)
            return

        #Getting parameters
        nb_bins=self.spinBox_bins.value

        signed=False
        if self.comboBox_distanceType.currentText == 'Signed Distance':
            signed=True

        correspondence=False
        if self.comboBox_correspondence.currentText == 'Yes':
            correspondence=True


        self.logic.fileA_out=self.pathLineEdit_fileA.currentPath
        self.logic.fileB_out=self.pathLineEdit_fileB.currentPath

        #self.logic.stats.Set('A',fileA_path)
        #self.logic.stats.Set('B',fileB_path)

        #computing
        self.pushButton_compute.setText("Computing ...")
        self.pushButton_compute.setDisable(True)
        self.logic.computeStats(nb_bins,signed,correspondence)

        self.checkThreadTimer=qt.QTimer()
        self.checkThreadTimer.connect('timeout()', self.onCheckCompute)
        self.checkThreadTimer.start(100)
        return

    #Action to do when the mode change
    def onModeChanged(self,mode):
        self.deleteResultsLabels()

        #show statistics labels
        self.result_labels=self.logic.formatStats(mode)
        for i in range(len(self.result_labels)):
            label = self.result_labels[i]
            self.gridLayout_results.addWidget(label[0],i+1,1)
            self.gridLayout_results.addWidget(label[1],i+1,2)

        #configure color parameters
        mini,maxi=self.logic.getMinAndMax(mode)

        self.doubleSpinBox_minimum.disconnect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)
        self.doubleSpinBox_minimum.setMaximum(maxi)
        self.doubleSpinBox_minimum.setMinimum(mini)
        self.doubleSpinBox_minimum.setValue(mini)
        self.doubleSpinBox_minimum.setEnabled(True)
        self.doubleSpinBox_minimum.connect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)

        self.doubleSpinBox_maximum.disconnect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)
        self.doubleSpinBox_maximum.setMaximum(maxi)
        self.doubleSpinBox_maximum.setMinimum(mini)
        self.doubleSpinBox_maximum.setValue(maxi)
        self.doubleSpinBox_maximum.setEnabled(True)
        self.doubleSpinBox_maximum.connect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)
        
        self.ctkRangeSlider_color.disconnect('valuesChanged(int,int)',self.onSliderScalarRangeChanged)
        self.ctkRangeSlider_color.setValues(0,99)
        self.ctkRangeSlider_color.setEnabled(True)
        self.ctkRangeSlider_color.connect('valuesChanged(int,int)',self.onSliderScalarRangeChanged)

        self.logic.setScalarRange(mini,maxi)

        self.logic.setDistance(mode)

    def onSpinBoxScalarRangeChanged(self):
        mode=self.comboBox_mode.currentText
        mini,maxi=self.logic.getMinAndMax(mode)

        current_mini=self.doubleSpinBox_minimum.value
        current_maxi=self.doubleSpinBox_maximum.value

        self.doubleSpinBox_minimum.setMaximum(current_maxi)
        self.doubleSpinBox_maximum.setMinimum(current_mini)

        reduced=current_mini-mini
        ratio=reduced/(maxi-mini)
        slider_min=int(ratio*100)

        reduced=current_maxi-mini
        ratio=reduced/(maxi-mini)
        slider_max=int(ratio*100)


        self.ctkRangeSlider_color.disconnect('valuesChanged(int,int)',self.onSliderScalarRangeChanged)
        self.ctkRangeSlider_color.setValues(slider_min,slider_max)
        self.ctkRangeSlider_color.connect('valuesChanged(int,int)',self.onSliderScalarRangeChanged)


        self.logic.setScalarRange(current_mini,current_maxi)

    def onSliderScalarRangeChanged(self):
        mode=self.comboBox_mode.currentText
        mini,maxi=self.logic.getMinAndMax(mode)

        slider_min=self.ctkRangeSlider_color.minimumValue
        slider_max=self.ctkRangeSlider_color.maximumValue

        ratio=slider_min/99.0
        reduced=ratio*(maxi-mini)
        current_min=reduced+mini

        ratio=slider_max/99.0
        reduced=ratio*(maxi-mini)
        current_max=reduced+mini

        self.doubleSpinBox_minimum.disconnect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)
        self.doubleSpinBox_maximum.disconnect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)

        self.doubleSpinBox_minimum.setMaximum(current_max)
        self.doubleSpinBox_minimum.setValue(current_min)

        self.doubleSpinBox_maximum.setMinimum(current_min)
        self.doubleSpinBox_maximum.setValue(current_max)

        self.doubleSpinBox_minimum.connect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)
        self.doubleSpinBox_maximum.connect('valueChanged(double)',self.onSpinBoxScalarRangeChanged)

        self.logic.setScalarRange(current_min,current_max)

    #Action to do when the translation slider have been moved
    def onTranslation(self,value):
        x_translation=self.x_range*value/400.0
        self.logic.updateTransform('A',x_translation)
        self.logic.updateTransform('B',x_translation)

    #Action to do when save button is pushed
    def onSave(self):
        dlg = ctk.ctkFileDialog()
        CSVpath = dlg.getSaveFileName(None, "Export CSV file for Classification groups", os.path.join(qt.QDir.homePath(), "Desktop"), "CSV File (*.csv)")

        if CSVpath == '' or CSVpath==' ':
            return

        if self.logic.checkExtension(CSVpath,'.csv'):
            print('saving ...',end=' ')
            self.logic.saveResults(CSVpath)
            slicer.util.delayDisplay("Exploration saved")
            print('Done!')

    def onCheckSampling(self):
        stateA=self.logic.samplingA.GetStatusString()
        stateB=self.logic.samplingB.GetStatusString()
        if stateA=='Running'or stateA=='Scheduled' or stateB=='Running'or stateB=='Scheduled':
            print('Sampling File A:',stateA)
            print('Sampling File B:',stateB)
        else:
            print('Sampling done!')
            self.checkThreadTimer.stop()
            self.checkThreadTimer.disconnect('timeout()', self.onCheckSampling)

            #Getting parameters
            nb_bins=self.spinBox_bins.value

            signed=False
            if self.comboBox_distanceType.currentText == 'Signed Distance':
                signed=True

            correspondence=False
            if self.comboBox_correspondence.currentText == 'Yes':
                correspondence=True


            fileA_path=self.logic.fileA_out
            fileB_path=self.logic.fileB_out

            self.logic.stats.Set('A',fileA_path)
            self.logic.stats.Set('B',fileB_path)

            #computing
            self.pushButton_compute.setText("Computing ...")
            self.logic.computeStats(nb_bins,signed,correspondence)

            self.checkThreadTimer=qt.QTimer()
            self.checkThreadTimer.connect('timeout()', self.onCheckCompute)
            self.checkThreadTimer.start(100)
            return

    def onCheckCompute(self):
        state=self.logic.cli_stats.GetStatusString()
        
        if state=='Running'or state=='Scheduled' :
            print('Computing:',state)
        else:

            print('Computing:',state)
            self.checkThreadTimer.stop()
            self.checkThreadTimer.disconnect('timeout()', self.onCheckCompute)

            results_file=self.logic.cli_param["outputStatisticsJSON"]
            #print(results_file)
            with open(results_file,'r') as json_data:
                results = json.load(json_data)


            # with open(results_file, 'rb') as csvfile:
            #     reader=csv.DictReader(csvfile)
            #     self.logic.stats_dict=dict()
            self.logic.stats_dict=dict()
            for res in results:
                for key,value in res.items():
                    if type(value)==type(list()):
                        res[key]=np.array(value)
                self.logic.stats_dict[res['mode']]=res

            #Config interface
            self.pushButton_compute.setText("Compute")
            self.pushButton_compute.setEnable(True)
            self.pushButton_save.setEnabled(True)

            self.comboBox_mode.disconnect('currentIndexChanged(const QString)',self.onModeChanged)
            self.comboBox_mode.clear()
            modes=self.logic.stats_dict.keys()
            mode=modes[0]
            for i in modes:
                self.comboBox_mode.addItem(i)
            if len(modes)==1:
                self.comboBox_mode.setDisabled(True)
            else:
                self.comboBox_mode.setEnabled(True)
            self.comboBox_mode.connect('currentIndexChanged(const QString)',self.onModeChanged)

            #show results
            self.logic.show('A',self.logic.fileA_out,color=(1,0,0))
            self.logic.show('B',self.logic.fileB_out,color=(0,0,1))
            self.AddDisplayNodeChangedObserver('Shape A')
            self.AddDisplayNodeChangedObserver('Shape B')
            self.onTranslation(self.horizontalSlider_translation.value)
            self.onModeChanged(mode)

            #show plot
            self.logic.generate2DVisualisationNodes(mode)
            print('Done!')

    def onDisplayNodeModified(self,obj,event):
        colorNode = obj.GetDisplayNode().GetColorNode()
        if colorNode is not None:
            lookuptable=colorNode.GetLookupTable()
            IdRange=lookuptable.GetTableRange()

            minColor=[0,0,0,0]
            colorNode.GetColor(int(IdRange[1]),minColor)

            maxColor=[0,0,0,0]
            colorNode.GetColor(int(IdRange[0]),maxColor)

            self.label_colorMax.setStyleSheet("QLabel{background-color:rgb("+str(int(minColor[0]*255))+","+str(int(minColor[1]*255))+","+str(int(minColor[2]*255))+");}")
            self.label_colorMin.setStyleSheet("QLabel{background-color:rgb("+str(int(maxColor[0]*255))+","+str(int(maxColor[1]*255))+","+str(int(maxColor[2]*255))+");}")

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

    def AddDisplayNodeChangedObserver(self,name):
        shapenode=slicer.mrmlScene.GetFirstNodeByName(name)
        #Observer
        r=shapenode.AddObserver(shapenode.DisplayModifiedEvent, self.onDisplayNodeModified)

    

########################################################################################
#                                   LOGIC CLASS                                        #
########################################################################################

class ShapeDistanceAnalyzerLogic(ScriptedLoadableModuleLogic):
    def __init__(self, interface):
        self.interface = interface

        self.stats=ShapeStatistics.StatisticsLogic()

        self.generateLUT()

        self.stats_dict=dict()

        self.shapeA_name='Shape A'
        self.shapeB_name='Shape B'


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

        shapestats = slicer.modules.shapestatistics

        fileA_path=self.fileA_out
        fileB_path=self.fileB_out

        self.cli_param = {}
        self.cli_param["inputShapeA"] = fileA_path
        self.cli_param["inputShapeB"] = fileB_path
        self.cli_param["NumberOfBins"] = nb_bins
        self.cli_param["Signed"]=signed
        self.cli_param["Correspondence"]=correspondence

        self.cli_param["outputStatisticsJSON"]= os.path.join(slicer.app.temporaryPath, 'SDA_statistics_result.json')
        self.cli_stats=slicer.cli.run(shapestats, None, self.cli_param, wait_for_completion=False)

        

        
    #function to generate results Qlabels
    #return an array of array containing the Qlabels to show in function of the desired mode.
    #Mode can be 'A<->B' or A->B' or 'B->A' or 'A->B & B->A'
    #QLabel_array=[[QLabel_key1,QLabel_value1],
    #                         ...
    #              [QLabel_keyN,QLabel_valueN]]
    def formatStats(self,mode):
        value_order=['number_of_bins','signed_distances','corresponding_points_exist','minimum',\
        'maximum','hausdorf','mean','sigma','msd','mad','median','iqr','iqr_q1','iqr_q3']

        label_dict=dict()
        label_dict['number_of_bins']='Number of bins'
        label_dict['signed_distances']='Signed distance'
        label_dict['corresponding_points_exist']='Corresponding points exist:'
        label_dict['minimum']='Minimum'
        label_dict['maximum']='Maximum'
        label_dict['hausdorf']='Hausdorf'
        label_dict['mean']='Mean'
        label_dict['sigma']='Sigma'
        label_dict['msd']='MSD'
        label_dict['mad']='MAD'
        label_dict['median']='Median'
        label_dict['iqr']='IQR'
        label_dict['iqr_q1']='IQR_Q1'
        label_dict['iqr_q3']='IQR_Q3'

        results=self.stats_dict[mode]

        QLabel_array=list()
        for key in value_order:
            value=results[key]
            label=label_dict[key]
            
            if isinstance(value,bool):
                if value==True:
                    value = 'Yes'
                else:
                    value = 'No'
            elif isinstance(value,int):
                pass
            else:
                value=round(value,4)

            QLabel_array.append([qt.QLabel(label+':'),qt.QLabel(value)])

        return QLabel_array
    
    #return the minimum distamce and the maximum distance for the selected mode
    def getMinAndMax(self,mode):
        mini = self.stats_dict[mode]['minimum']
        maxi = self.stats_dict[mode]['maximum']

        return mini,maxi
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
        self.deleteNodeByName("Histograms Table")
        self.deleteNodeByName("Histogram A->B")
        self.deleteNodeByName("Histogram B->A")
        self.deleteNodeByName("Histogram A->B & B->A")
        self.deleteNodeByName("Histogram A<->B")
        self.deleteNodeByName("Histograms plot chart")

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

    #function to show in slicer mrml scene the shape identified by ID
    #the color parameter define the color of the shape
    #shape is translated in the x axis by posX
    def show(self,ID,file,color=(1,1,1),posX=0):
        reader=vtk.vtkPolyDataReader()
        reader.SetFileName(file)
        reader.Update()
        polydata=reader.GetOutput()

        if ID == 'A':
            name=self.shapeA_name
            self.polydata_A=polydata
        if ID == 'B':
            name=self.shapeB_name
            self.polydata_B=polydata

        self.delete3DVisualisationNodes(name)
        
        self.autoOrientNormals(polydata)
        self.generate3DVisualisationNode(polydata,name,color=color,initial_pos_x=posX)
        self.setModelNodeLUT(name)

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
        self.deleteNodeByName(name)
        self.deleteNodeByName("Display "+name)
        self.deleteNodeByName("Translation "+name)

    #function to delete every Slicer node related to 3D Shapes
    #that could have been created by this module
    def deleteAll3DVisualisationNodes(self):
        self.delete3DVisualisationNodes(self.shapeA_name)
        self.delete3DVisualisationNodes(self.shapeB_name)

        self.deleteNodeByName('ShapeDistanceAnalyzer Distance Color Table')

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
    def updateTransform(self,shape,value):
        #translation shape A
        if shape == 'A':
            transform_node = slicer.mrmlScene.GetFirstNodeByName("Translation "+self.shapeA_name)
            if transform_node is not None:
                transform=vtk.vtkTransform()
                transform.Translate(value,0,0)
                transform_node.SetAndObserveTransformToParent(transform)

        #translation shape B
        if shape == 'B':
            transform_node = slicer.mrmlScene.GetFirstNodeByName("Translation "+self.shapeB_name)
            if transform_node is not None:
                transform=vtk.vtkTransform()
                transform.Translate(-value,0,0)
                transform_node.SetAndObserveTransformToParent(transform)

    #use the polydata boundaries to compute the X axis range
    def getXRange(self):
        polydata = self.polydata_A
        boundsA=polydata.GetBounds()
        rangeA=boundsA[1]-boundsA[2]

        polydata = self.polydata_B
        boundsB=polydata.GetBounds()
        rangeB=boundsB[1]-boundsB[2]

        return max(rangeA,rangeB)


    #------------------------------------------------------#    
    #            Color visualization Functions             #
    #------------------------------------------------------#

    #generate a color table node going from blue to green to red.
    #It will be used as look up table to visualise distances on shapes
    def generateLUT(self):
        self.deleteNodeByName('ShapeDistanceAnalyzer Distance Color Table')
        colorlow = (0.1,0.1, 1 )
        colormid = (1, 1 ,1)
        colorhigh= ( 1 ,0.1,0.1)

        #should be an odd number
        total_number_of_colors=512

        colorTableNode = slicer.vtkMRMLColorTableNode()
        colorTableNode.SetName('ShapeDistanceAnalyzer Color Table')
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

        colorTableNode.SetName('ShapeDistanceAnalyzer Distance Color Table')
        slicer.mrmlScene.AddNode(colorTableNode)

    #Show the distances on the corresponding(s) polydata in function of the mode
    #if mode == 'A<->B' the color is only shown on the shape A
    def setDistance(self,mode):
        if mode == 'A->B':
            #set polydata scalars
            self.setPolyDataDistanceScalars('A',mode,index=0)
            #enable/disable scalar visibility
            self.enableScalarView(self.shapeA_name)
            self.disableScalarView(self.shapeB_name)

        if mode == 'B->A':
            #set polydata scalars
            self.setPolyDataDistanceScalars('B',mode,index=0)
            #enable/disable scalar visibility
            self.enableScalarView(self.shapeB_name)
            self.disableScalarView(self.shapeA_name)

        if mode == 'A<->B':
            #set polydata scalars
            self.setPolyDataDistanceScalars('A',mode,index=0)
            self.setPolyDataDistanceScalars('B',mode,index=0)
            #enable/disable scalar visibility
            self.enableScalarView(self.shapeA_name)
            self.enableScalarView(self.shapeB_name)

        if mode == 'A->B & B->A':
            #set polydata scalars
            self.setPolyDataDistanceScalars('A',mode,index=0)
            self.setPolyDataDistanceScalars('B',mode,index=1)
            #enable scalar view
            self.enableScalarView(self.shapeA_name)
            self.enableScalarView(self.shapeB_name)

    #set the LUT of the model node named name and
    #set scalar range to min distance/max distance 
    def setModelNodeLUT(self,name):
        shapenode=slicer.mrmlScene.GetFirstNodeByName(name)
        colornode = slicer.mrmlScene.GetFirstNodeByName('ShapeDistanceAnalyzer Distance Color Table')
        if (shapenode is not None) and (colornode is not None):

            shapenode.GetDisplayNode().SetAndObserveColorNodeID(colornode.GetID())
            shapenode.Modified()

    def setScalarRange(self,mini,maxi):
        node = slicer.mrmlScene.GetFirstNodeByName(self.shapeA_name)
        node.GetDisplayNode().SetScalarRange(mini,maxi)

        node = slicer.mrmlScene.GetFirstNodeByName(self.shapeB_name)
        node.GetDisplayNode().SetScalarRange(mini,maxi)

    #take a numpy array distance, convert it in a vtkfloat array 
    #and set the scalars of polydata with this array 
    def setPolyDataDistanceScalars(self,shape,mode,index=0):
        distance = self.stats_dict[mode]['distances'][index]
        distance=self.generateVTKFloatArrayFromNumpy(distance)
        distance.SetName("Distance")

        if shape =='A':
            polydata = self.polydata_A
        else:
            polydata = self.polydata_B

        
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
        if shape_node is not None:
            shape_node.GetDisplayNode().SetScalarVisibility(0)

    #disable scalar view on shape A and B
    def disableAllScalarViews(self):
        self.disableScalarView(self.shapeA_name)
        self.disableScalarView(self.shapeB_name)


    #------------------------------------------------------#    
    #           LinearSubdivision cli Functions            #
    #------------------------------------------------------#

    def samplePolydatas(self,fileA,fileB,sampling_level):
        sampler = slicer.modules.linearsubdivision

        directory ,filename = os.path.split(fileA)
        name ,ext =os.path.splitext(filename)
        self.fileA_out=slicer.app.temporaryPath + '/' + name +'out'+ext

        self.eval_paramA = {}
        self.eval_paramA["input"] = fileA
        self.eval_paramA["output"] = self.fileA_out
        self.eval_paramA["subdivisions"] = sampling_level
        self.samplingA=slicer.cli.run(sampler, None, self.eval_paramA, wait_for_completion=False)

        directory ,filename = os.path.split(fileB)
        name ,ext =os.path.splitext(filename)
        self.fileB_out=slicer.app.temporaryPath + '/' + name +'out'+ext

        self.eval_paramB = {}
        self.eval_paramB["input"] = fileB
        self.eval_paramB["output"] = self.fileB_out
        self.eval_paramB["subdivisions"] = sampling_level
        self.samplingB=slicer.cli.run(sampler, None, self.eval_paramB, wait_for_completion=False)


    #------------------------------------------------------#    
    #                  Utility Functions                   #
    #------------------------------------------------------#

    def saveResults(self,CSVpath):
        listofdict=list()

        for mode,dict in self.stats_dict.items():
            listofdict.append(dict)

        self.stats.SaveStatsAsCSV(CSVpath,listofdict)

    #Function to get a widget in the .ui file that describe the module interface
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

    #function that convert a 1 dimensional numpy array into a VTKFloat array
    def generateVTKFloatArrayFromNumpy(self,np_array):
        size = np_array.size

        vtk_float = vtk.vtkFloatArray()
        vtk_float.SetNumberOfComponents(1)
        for i in range(size):
            
            vtk_float.InsertNextTuple([np_array[i]])
        return vtk_float

    #delete, if it exist, a node identified by his name
    def deleteNodeByName(self,name):
        node = slicer.mrmlScene.GetFirstNodeByName(name)
        if node is not None:
            slicer.mrmlScene.RemoveNode(node)

    def IsCorrespondencePossible(self,pathA,pathB):
        readerA=vtk.vtkPolyDataReader()
        readerA.SetFileName(pathA)
        readerA.Update()
        nb_points_A=readerA.GetOutput().GetPoints().GetNumberOfPoints()

        readerB=vtk.vtkPolyDataReader()
        readerB.SetFileName(pathB)
        readerB.Update()
        nb_points_B=readerB.GetOutput().GetPoints().GetNumberOfPoints()

        return nb_points_A==nb_points_B
            

########################################################################################
#                                   TEST CLASS                                         #
########################################################################################

class ShapeDistanceAnalyzerTest(ScriptedLoadableModuleTest):
    pass