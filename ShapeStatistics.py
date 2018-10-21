import numpy as np

import vtk
from vtk.util.numpy_support import vtk_to_numpy

import csv

class ShapeStatisticsLogic:
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

		if ID =='B':
			self.B_path=file_path
			self.B_reader=reader

	#function that return the polydata assocciated to shape identified by ID
	def getPolydata(self,ID):
		if ID =='A':
			return self.A_reader.GetOutput()

		if ID =='B':
			return self.B_reader.GetOutput()

	#return True if both file A and file B have been set
	#and if the computation is ready to be launched
	#return False otherwise
	def IsReady(self):
		ready=False
		if self.A_path and self.B_path:
			ready=True
		return ready
	
	#compute distances between A and B using the closest point method
	#the vtk object vtkDistancePolyDataFilter is used to compute the distances
	#inverse=False : A->B ,inverse=True : B->A
	#return a numpy array 
	def ClosestPoint(self,signed=True,inverse=False):
		distancefilter=vtk.vtkDistancePolyDataFilter()

		if inverse:
			distancefilter.SetInputData(1,self.A_reader.GetOutput())
			distancefilter.SetInputData(0,self.B_reader.GetOutput())
		else:
			distancefilter.SetInputData(0,self.A_reader.GetOutput())
			distancefilter.SetInputData(1,self.B_reader.GetOutput())

		distancefilter.SetSignedDistance(signed)
		distancefilter.Update()

		datavtkfloat=distancefilter.GetOutput().GetPointData().GetScalars()
		dist = vtk_to_numpy(datavtkfloat)

		return dist
	
	#compute distances between A and B assuming that the two shapes have corresponding points
	#the vtk object vtkSelectEnclosedPoints is used to give a sign for each distance
	#inverse=False : A->B ,inverse=True : B->A
	#return a numpy array 
	def CorrespondenceDistance(self,signed=False,inverse=False,tolerance=0.0000001):

		A = self.A_reader.GetOutput()
		A = A.GetPoints()
		A = A.GetData()
		A = vtk_to_numpy(A)

		B = self.B_reader.GetOutput()
		B = B.GetPoints()
		B = B.GetData()
		B = vtk_to_numpy(B)

		dist = A-B
		dist = np.linalg.norm(dist,axis=1)

		if not signed:
			return dist

		else:
			enclosed_points=vtk.vtkSelectEnclosedPoints()
			if inverse:
			    enclosed_points.SetInputData(self.B_reader.GetOutput())
			    enclosed_points.SetSurfaceData(self.A_reader.GetOutput())
			else:
			    enclosed_points.SetInputData(self.A_reader.GetOutput())
			    enclosed_points.SetSurfaceData(self.B_reader.GetOutput())

			enclosed_points.SetTolerance(tolerance)
			enclosed_points.Update()

			for i in range(len(dist)):
				if enclosed_points.IsInside(i):
					dist[i]=-dist[i]
		    
			

		return dist
	
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
	def Histogram(self,signed=True,bins=256,correspondence=False,mode=2):
		if self.A_path and self.B_path:
			if correspondence :
				if signed == False:
					dist = self.CorrespondenceDistance(signed=signed)
					hist , edge = np.histogram(dist,bins=bins)
					distances=[dist]

				else:
					if mode == 'A->B':
						dist = self.CorrespondenceDistance(signed=signed,inverse=False)
						hist,edge=np.histogram(dist,bins=bins)
						distances=[dist]

					if mode == 'B->A':
						dist = self.CorrespondenceDistance(signed=signed,inverse=True)
						hist,edge=np.histogram(dist,bins=bins)
						distances=[dist]

					if mode == 'A->B & B->A':
						distab = self.CorrespondenceDistance(signed=signed,inverse=False)
						distba = self.CorrespondenceDistance(signed=signed,inverse=True)

						maxi=np.max([np.max(distab),np.max(distba)])
						mini=np.min([np.min(distab),np.min(distba)])

						histab,edge=np.histogram(distab,bins=bins,range=(mini,maxi))
						histba,edge=np.histogram(distba,bins=bins,range=(mini,maxi))

						hist = (histab + histba)
						distances=[distab,distba]
					
			else:
				if mode == 'A->B':
					distab = self.ClosestPoint(signed=signed,inverse=False)
					hist,edge=np.histogram(distab,bins=bins)
					distances=[distab]


				if mode == 'B->A':
					distba = self.ClosestPoint(signed=signed,inverse=True)
					hist,edge=np.histogram(distba,bins=bins)
					distances=[distba]

				if mode == 'A->B & B->A':
					distab = self.ClosestPoint(signed=signed,inverse=False)
					distba = self.ClosestPoint(signed=signed,inverse=True)

					maxi=np.max([np.max(distab),np.max(distba)])
					mini=np.min([np.min(distab),np.min(distba)])

					histab,edge=np.histogram(distab,bins=bins,range=(mini,maxi))
					histba,edge=np.histogram(distba,bins=bins,range=(mini,maxi))

					hist = histba + histab

					distances=[distab,distba]


			self.hist=hist
			self.edge=edge
			self.edgemean = self.EdgeMean()
			return hist, edge, distances

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
		minimum = np.min(self.edge)
		maximum = np.max(self.edge)
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
	def ComputeValues(self,signed=True,bins=256,correspondence=False,mode=2):
		hist,edge,distances=self.Histogram(signed=signed,bins=bins,correspondence=correspondence,mode=mode)

		minimum, maximum = self.MinAndMax()

		Hausdorf = self.Hausdorf(minimum,maximum)

		mean,sigma =self.MeanAndSigma()

		MSD = self.MSD()
		MAD = self.MAD()

		median = self.Median()

		IQR,IQR_Q1,IQR_Q3=self.IQR()

		stats_dict=dict()
		stats_dict['distances']=distances
		stats_dict['corresponding_points_exist']=correspondence
		stats_dict['mode']=mode
		stats_dict['signed_distances']=signed
		stats_dict['number_of_bins']=bins
		stats_dict['histogram']=hist
		stats_dict['edge']=edge
		stats_dict['edge_mean']=self.edgemean
		stats_dict['minimum']=minimum
		stats_dict['maximum']=maximum
		stats_dict['hausdorf']=Hausdorf
		stats_dict['mean']=mean
		stats_dict['sigma']=sigma
		stats_dict['MSD']=MSD
		stats_dict['MAD']=MAD
		stats_dict['median']=median
		stats_dict['IQR_Q1']=IQR_Q1
		stats_dict['IQR_Q3']=IQR_Q3
		stats_dict['IQR']=IQR

		return stats_dict

	#Save in a CSV file (file_path), all the dictionaries of the list dict_list
	#each dictionary should come from the ComputeValues function.
	def SaveStatsAsCSV(self,file_path,dict_list):
		for stats in dict_list:
			del stats['histogram']
			del stats['edge']
			del stats['edge_mean']

		with open(file_path,'w',newline='') as csvfile:
			fieldnames = dict_list[0].keys()
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

			writer.writeheader()
			for stats in dict_list:
				writer.writerow(stats)

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

