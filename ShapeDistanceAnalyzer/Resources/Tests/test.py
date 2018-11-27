from __future__ import print_function

import unittest
import sys
sys.path.append('../../')
sys.path.append('./')
import ShapeStatistics
import csv
import numpy as np
import math



class ShapeStatisticsTesting(unittest.TestCase):

	def test_Statistics_Functions(self):
		print('')
		valmet=ShapeStatistics.StatisticsLogic()

		mu,sig,bins=0,1,256
		
		print('Testing with normal law: mu =',mu,', sig =',sig,', bins =',bins,end=' ... ')
		sys.stdout.flush()

		rand = np.random.normal(mu,sig,10000)
		valmet.hist, valmet.edge = np.histogram(rand,bins=bins)
		valmet.edgemean = valmet.EdgeMean()

		minimum, maximum = valmet.MinAndMax()
		self.assertEqual(minimum,np.min(rand))
		self.assertEqual(maximum,np.max(rand))

		Hausdorf = valmet.Hausdorf(minimum,maximum)
		self.assertEqual(Hausdorf,np.max(np.abs(rand)))

		mean,sigma =valmet.MeanAndSigma()
		self.assertAlmostEqual(mean,mu,delta=0.2)
		self.assertAlmostEqual(sigma,sig,delta=0.2)

		IQR,IQR_Q1,IQR_Q3 = valmet.IQR()
		self.assertAlmostEqual(IQR_Q1,mu-0.6745*sig,delta=0.2)
		self.assertAlmostEqual(IQR_Q3,mu+0.6745*sig,delta=0.2)

		print('ok')

		mu,sig,bins=25,2,256
		
		print('Testing with normal law: mu =',mu,', sig =',sig,', bins =',bins,end=' ... ')
		sys.stdout.flush()

		rand = np.random.normal(mu,sig,10000)
		valmet.hist, valmet.edge = np.histogram(rand,bins=bins)
		valmet.edgemean = valmet.EdgeMean()

		minimum, maximum = valmet.MinAndMax()
		self.assertEqual(minimum,np.min(rand))
		self.assertEqual(maximum,np.max(rand))

		Hausdorf = valmet.Hausdorf(minimum,maximum)
		self.assertEqual(Hausdorf,np.max(np.abs(rand)))

		mean,sigma =valmet.MeanAndSigma()
		self.assertAlmostEqual(mean,mu,delta=0.2)
		self.assertAlmostEqual(sigma,sig,delta=0.2)

		IQR,IQR_Q1,IQR_Q3 = valmet.IQR()
		self.assertAlmostEqual(IQR_Q1,mu-0.6745*sig,delta=0.2)
		self.assertAlmostEqual(IQR_Q3,mu+0.6745*sig,delta=0.2)

		print('ok')

	def test_Pipeline(self):
		print('')
		fileA='./File_A.vtk'
		fileB='./File_B.vtk'
		goodResults='./TestValues.csv'

		valmet=ShapeStatistics.StatisticsLogic()
		valmet.Set('A',fileA)
		valmet.Set('B',fileB)

		with open(goodResults, newline='') as csvfile:
		    reader = csv.DictReader(csvfile)
		    for teststats in reader:
		    	correspondence=str2bool(teststats['corresponding_points_exist'])
		    	mode=teststats['mode']
		    	signed=str2bool(teststats['signed_distances'])
		    	bins=int(teststats['number_of_bins'])
		    	print('Testing with Correspondance =',correspondence,',Signed =',signed,',Mode =',mode,end=' ... ')
		    	sys.stdout.flush()
		    	stats=valmet.ComputeValues(bins=bins,signed=signed,correspondence=correspondence)
		    	stats=stats[mode]
		    	
		    	for key , value in teststats.items():
		    		self.assertAlmostEqual(value,str(stats[key]),delta=0.00001)
		    	print('ok')
		

def str2bool(v):
	
  return v.lower() in ("yes", "true", "t", "1")		



if __name__ == '__main__':
    unittest.main()