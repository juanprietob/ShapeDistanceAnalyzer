from __future__ import print_function
import numpy as np

import vtk
from vtk.util.numpy_support import vtk_to_numpy
#import sys
#sys.path.append('Resources/LinearSubdivisionFilter')
import LinearSubdivisionFilter

import csv
import json

class StatisticsLogic:
	def __init__(self):
		self.A_path=None

		self.B_path=None


	#load a .vtk file
	#the ID parameter define if the file is loaded as the A shape or the B shape
	#create a polydata reader in self.A_reader or self.B_reader
	def Set(self,ID,file_path):
		reader=vtk.vtkPolyDataReader()
		reader.SetFileName(file_path)
		reader.Update()

		if ID =='A':
			self.A_path=file_path
			self.A_reader=reader
			self.A_polydata=self.A_reader.GetOutput()

		if ID =='B':
			self.B_path=file_path
			self.B_reader=reader
			self.B_polydata=self.B_reader.GetOutput()

	#function that return the polydata assocciated to shape identified by ID
	def getPolydata(self,ID):
		if ID =='A':
			return self.A_polydata

		if ID =='B':
			return self.B_polydata

	#return True if both file A and file B have been set
	#and if the computation is ready to be launched
	#return False otherwise
	def IsReady(self):
		ready=False
		if self.A_path and self.B_path:
			ready=True
		return ready

	#return True if the 2 shapes have the same number of point
	def IsCorrespondencePossible(self):
		try:
			nbr_points_A=self.A_reader.GetOutput().GetPoints().GetNumberOfPoints()
			nbr_points_B=self.B_reader.GetOutput().GetPoints().GetNumberOfPoints()

			if nbr_points_A == nbr_points_B:
				return True
			else:
				return False
		except:
			return False

	def linearSample(self,sampling_level):
		if sampling_level==1:
			self.A_polydata = self.A_reader.GetOutput()
			self.B_polydata = self.B_reader.GetOutput()

		else:
			print('')
			print('Sampling polydata ...',end=' ')
			self.A_sampler=LinearSubdivisionFilter.LinearSubdivisionFilter()
			self.A_sampler.SetInputData(self.A_reader.GetOutput())
			self.A_sampler.SetNumberOfSubdivisions(sampling_level)
			self.A_sampler.Update()
			self.A_polydata = self.A_sampler.GetOutput()

			self.B_sampler=LinearSubdivisionFilter.LinearSubdivisionFilter()
			self.B_sampler.SetInputData(self.B_reader.GetOutput())
			self.B_sampler.SetNumberOfSubdivisions(sampling_level)
			self.B_sampler.Update()
			self.B_polydata = self.B_sampler.GetOutput()
			print('Done')

	
	#compute distances between A and B using the closest point method
	#the vtk object vtkDistancePolyDataFilter is used to compute the distances
	#inverse=False : A->B ,inverse=True : B->A
	#return a numpy array 
	def ClosestPoint(self,signed=True,inverse=False):
		distancefilter=vtk.vtkDistancePolyDataFilter()

		if inverse:
			distancefilter.SetInputData(1,self.getPolydata('A'))
			distancefilter.SetInputData(0,self.getPolydata('B'))
		else:
			distancefilter.SetInputData(0,self.getPolydata('A'))
			distancefilter.SetInputData(1,self.getPolydata('B'))

		distancefilter.SetSignedDistance(signed)
		distancefilter.Update()

		datavtkfloat=distancefilter.GetOutput().GetPointData().GetScalars()
		dist = vtk_to_numpy(datavtkfloat)

		return dist.tolist()
	
	#compute distances between A and B assuming that the two shapes have corresponding points
	#the vtk object vtkSelectEnclosedPoints is used to give a sign for each distance
	#inverse=False : A->B ,inverse=True : B->A
	#return a numpy array 
	def CorrespondenceDistance(self,signed=False,inverse=False,tolerance=0.000000001):

		A = self.getPolydata('A')
		A = A.GetPoints()
		A = A.GetData()
		A = vtk_to_numpy(A)

		B = self.getPolydata('B')
		B = B.GetPoints()
		B = B.GetData()
		B = vtk_to_numpy(B)

		dist = A-B
		dist = np.linalg.norm(dist,axis=1)


		if not signed:
			return dist.tolist()

		else:
			enclosed_points=vtk.vtkSelectEnclosedPoints()
			if inverse:
			    enclosed_points.SetInputData(self.getPolydata('B'))
			    enclosed_points.SetSurfaceData(self.getPolydata('A'))
			else:
			    enclosed_points.SetInputData(self.getPolydata('A'))
			    enclosed_points.SetSurfaceData(self.getPolydata('B'))

			enclosed_points.SetTolerance(tolerance)
			enclosed_points.Update()

			for i in range(len(dist)):
				if enclosed_points.IsInside(i):
					dist[i]=-dist[i]
		    
			

		return dist.tolist()
	
	#compute the histogram between A and B according to the given parameters
	#mode=0: A->B, mode=1: B->A, mode=2: A->B and B->A
	#set 3 attributes:
	#  -self.hist, the histogram array (bins elements)
	#  -self.edge, the edge array associated (bins+1 elements)
	#  -self.edgemean, an array that contains the mean value of each bin (bins elements)
	#return 2 numpy array:
	#  -the histogram array (bins elements)
	#  -the edge array associated (bins+1 elements)
	#  -a list containing the distances array used (contains only 1 array in mode 0 and 1 and 2 arrays in mode 2)
	def Histogram(self,signed=True,bins=256,correspondence=False):
		if self.A_path and self.B_path:
			hist_dict=dict()
			distances=dict()
			if correspondence :
				if signed == False:
					dist = self.CorrespondenceDistance(signed=signed)
					hist , edge = np.histogram(dist,bins=bins)
					hist_dict['A<->B'] = hist
					distances['A<->B'] = [dist] 


				else:
					distab = self.CorrespondenceDistance(signed=signed,inverse=False)
					distba = self.CorrespondenceDistance(signed=signed,inverse=True)

					maxi=np.max([np.max(distab),np.max(distba)])
					mini=np.min([np.min(distab),np.min(distba)])

					histab,edge=np.histogram(distab,bins=bins,range=(mini,maxi))
					histba,edge=np.histogram(distba,bins=bins,range=(mini,maxi))

					hist_dict['A->B'] = histab 
					hist_dict['B->A'] = histba
					hist_dict['A->B & B->A'] = histab +histba
					distances['A->B'] = [distab] 
					distances['B->A'] = [distba]
					distances['A->B & B->A'] = [distab,distba]

					
			else:
				distab = self.ClosestPoint(signed=signed,inverse=False)
				distba = self.ClosestPoint(signed=signed,inverse=True)

				maxi=np.max([np.max(distab),np.max(distba)])
				mini=np.min([np.min(distab),np.min(distba)])

				histab,edge=np.histogram(distab,bins=bins,range=(mini,maxi))
				histba,edge=np.histogram(distba,bins=bins,range=(mini,maxi))

				hist_dict['A->B'] = histab 
				hist_dict['B->A'] = histba
				hist_dict['A->B & B->A'] = histab +histba
				distances['A->B'] = [distab] 
				distances['B->A'] = [distba]
				distances['A->B & B->A'] = [distab,distba]

			return hist_dict, edge, distances

	#compute the mean of each bin dscribed by self.edge
	#return 1 numpy array
	def EdgeMean(self):
		mean=list()

		for i in range(len(self.edge)-1):
			section=self.edge[i:i+1]
			mean.append(np.mean(section))
		return np.array(mean) 

	#compute the median of the histogram described by self.hist and self.edgemean
	def Median(self):
		cumsum = np.cumsum(self.hist)
		#number of samples
		N=cumsum[-1]

		halfN = N/2.0
		if N%2 != 0:
			for i in range(len(cumsum)):
				if cumsum[i]>halfN:
					median=self.edgemean[i]
					return median
		else:
			for i in range(len(cumsum)):
				if cumsum[i]==halfN:
					median = np.mean(self.edgemean[i:i+1])
					return median
				if cumsum[i]>halfN:
					median=self.edgemean[i]
					return median

	#compute the minimum and the maximum of the histogram using self.edge
	def MinAndMax(self):
		for i in range(len(self.hist)):
			if self.hist[i]!=0:
				minimum=self.edge[i]
				break

		fliped=np.flip(self.hist,axis=0)
		for i in range(len(fliped)):
			if fliped[i]!=0:
				maximum=np.flip(self.edge,axis=0)[i]
				break
		return minimum, maximum

	#return the absolute maximum between minimum and maximum
	def Hausdorf(self,minimum,maximum):
		Hausdorf = np.max([np.abs(minimum),np.abs(maximum)])
		return Hausdorf

	#compute the mean and the standart deviation of the histogram described by self.hist and self.edgemean
	def MeanAndSigma(self):
		mean = np.average(self.edgemean,weights=self.hist)
		variance = np.average((self.edgemean-mean)**2, weights=self.hist)
		sigma =np.sqrt(variance)
		return mean,sigma

	#compute the mean squared distance using self.hist and self.edgemean
	def MSD(self):
		MSD = np.average(self.edgemean**2,weights=self.hist)
		return MSD

	#compute the mean absolute distance using self.hist and self.edgemean
	def MAD(self):
		MAD = np.average(np.abs(self.edgemean),weights=self.hist)
		return MAD

	#compute perentiles value 	
	#percentile should be between 0 and 1.0
	def Percentile(self, percentile):

		sumhist = np.cumsum(self.hist)

		N= sumhist[-1]

		for i in range(len(self.hist)):
			if sumhist[i]>= N*percentile:

				percentile= self.edgemean[i]
				break

		return percentile

	#compute the IQR
	#return IQR,IQR_Q1,IQR_Q3
	def IQR(self):
		IQR_Q1 = self.Percentile(0.25)
		IQR_Q3 = self.Percentile(0.75)

		IQR = IQR_Q3-IQR_Q1

		return IQR,IQR_Q1,IQR_Q3

	#compute the histogram and the statistic values associated
	#mode=0: A->B, mode=1: B->A, mode=2: A->B and B->A
	#return a dictionnary containing all the values
	def ComputeValues(self,signed=True,bins=256,correspondence=False):

		self.A_polydata = self.A_reader.GetOutput()
		self.B_polydata = self.B_reader.GetOutput()

		hist_dict,edge,distances=self.Histogram(signed=signed,bins=bins,correspondence=correspondence)

		stats_dict=dict()
		for mode in hist_dict.keys():
			self.hist=hist_dict[mode]
			self.edge=edge
			self.edgemean = self.EdgeMean()

			minimum, maximum = self.MinAndMax()

			Hausdorf = self.Hausdorf(minimum,maximum)

			mean,sigma =self.MeanAndSigma()

			MSD = self.MSD()
			MAD = self.MAD()

			median = self.Median()

			IQR,IQR_Q1,IQR_Q3=self.IQR()

			stats_values=dict()
			stats_values['distances']=distances[mode]
			stats_values['corresponding_points_exist']=correspondence
			stats_values['mode']=mode
			stats_values['signed_distances']=signed
			stats_values['number_of_bins']=bins
			stats_values['histogram']=self.hist.tolist()
			stats_values['edge']=self.edge.tolist()
			stats_values['edge_mean']=self.edgemean.tolist()
			stats_values['minimum']=minimum
			stats_values['maximum']=maximum
			stats_values['hausdorf']=Hausdorf
			stats_values['mean']=mean
			stats_values['sigma']=sigma
			stats_values['msd']=MSD
			stats_values['mad']=MAD
			stats_values['median']=median
			stats_values['iqr_q1']=IQR_Q1
			stats_values['iqr_q3']=IQR_Q3
			stats_values['iqr']=IQR

			
			stats_dict[mode]=stats_values


		return stats_dict

	#Save in a CSV file (file_path), all the dictionaries of the list dict_list
	#each dictionary should come from the ComputeValues function.
	def SaveStatsAsCSV(self,file_path,dict_list):
		for stats in dict_list:
			#del stats['histogram']
			#del stats['edge']
			#del stats['edge_mean']
			pass

		with open(file_path,'w') as csvfile:
			fieldnames = dict_list[0].keys()
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')

			writer.writeheader()
			for stats in dict_list:
				writer.writerow(stats)

	#Save in a JSON file (file_path), all the dictionaries of the list dict_list
	#each dictionary should come from the ComputeValues function.
	def SaveStatsAsJSON(self,file_path,dict_list):
		for stats in dict_list:
			#del stats['histogram']
			#del stats['edge']
			#del stats['edge_mean']
			pass

		with open(file_path,'w') as jsonfile:
			json.dump(dict_list,jsonfile,indent=4)

	#test stats functions with a normal law
	def test(self,mu=0,sig=1,bins=1000):
		rand = np.random.normal(mu,sig,10000)

		self.hist, self.edge = np.histogram(rand,bins=bins)
		self.edgemean = self.EdgeMean()

		minimum, maximum = self.MinAndMax()
		Hausdorf = self.Hausdorf(minimum,maximum)

		mean,sigma =self.MeanAndSigma()
		MSD = self.MSD()
		MAD = self.MAD()

		median = self.Median()

		IQR,IQR_Q1,IQR_Q3=self.IQR()

		print("############################Testing##############################")
		print('Normal distribution: mu =',mu,'sigma =',sig)

		print('Number of bins:\t\t',bins)

		print('Minimum:\t\t',minimum)
		print('Maximum:\t\t',maximum)
		print('Hausdorf:\t\t',Hausdorf)

		print('mean:\t\t\t', mean)
		print('sigma:\t\t\t',sigma)
		print('MSD:\t\t\t',MSD)
		print('MAD:\t\t\t',MAD)

		print('Median:\t\t\t',median)

		print('IQR:\t\t',IQR)
		print('IQR_Q1:\t\t',IQR_Q1)
		print('IQR_Q3:\t\t',IQR_Q3)

