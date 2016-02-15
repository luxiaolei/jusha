# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 17:14:41 2016

@author: tieqiangli
"""
# prepare calling the r TDA API
from rpy2.robjects.packages import importr
utils = importr("utils")
utils.chooseCRANmirror(ind=1)
utils.install_packages('TDA')
TDA = importr('TDA')

import mapper
import pandas as pd
import numpy as np

def AutoScale(f = '/user/dataset.csv'):
    intervalStep = 1
    overlap = 70
    t = pd.read_csv(f)
    NumberOfDataPoints = t.shape[1]
    intervalUp = max(50,NumberOfDataPoints)
    intervalRange = (3,intervalUp,intervalStep)
#    overlapRange = (50,80,overlapStep)

    bottleneckDist_dim0 =[]
    bottleneckDist_dim1 =[]   
    
    result_0 = core_mapping(f,2,overlap)
    # call the R TDA API to compute the persistent diagrams with the first scale parameters set
    Diag0 = TDA.gridDiag(zip(result_0['x'],result_0['y']), filterFunctionChosenInCore)
    for i in intervalRange:
        result = core_mapping(t,i,overlap)
        # call the R TDA API to compute the persistent diagrams with the parameters set in the loop
        Diag = TDA.gridDiag(zip(result['x'],result['y']), filterFunctionChosenInCore)
        # call the R TDA API to compute bottleneck distance against the first scale parameters set            
        tmpDist_dim0 = TDA.bottleneck(Diag0[["diagram"]], Diag[["diagram"]], dimension = 0)
        tmpDist_dim1 = TDA.bottleneck(Diag0[["diagram"]], Diag[["diagram"]], dimension = 1)
        # record it in a list
        bottleneckDist_dim0.append(tmpDist_dim0)
        bottleneckDist_dim1.append(tmpDist_dim1)            

    # do statistics to identify the sub-range of the list of diagrams that capture the persistent shape
    
    # re-map back to the scales parameters that produce the corresponding diagrams as result
    return resultIntervalsRange

def core_mapping(in_file = '/Users/tieqiangli/mapperinput/CorrelationArray1d_0708.csv',
                   # out_path = '/Users/tieqiangli/mapperinput/output/', 
                   intervals = 15,
                   overlap = 50):
                        
    data = np.loadtxt(str(in_file), delimiter=',', dtype=np.float)
    
#    metricpar = {'metric': 'euclidean'}
#    
#    point_labels = np.array(['a','b','c','d'])
##    point_labels = np.array([600001,600002,600003,600004])
#    mask = [1,2,3,4]
    point_labels = None
    mask = None

#    data, point_labels = mapper.mask_data(data, mask, point_labels)
    
    '''
        Step 2: Metric
    '''
    intrinsic_metric = False
    if intrinsic_metric:
        is_vector_data = data.ndim != 1
        if is_vector_data:
            metric = Euclidean
            if metric != 'Euclidean':
                raise ValueError('Not implemented')
        data = mapper.metric.intrinsic_metric(data, k=1, eps=1.0)
    is_vector_data = data.ndim != 1
    '''
        Step 3: Filter function
    '''
    if is_vector_data:
        metricpar = {'metric': 'euclidean'}
        f = mapper.filters.Gauss_density(data,
            metricpar=metricpar,
            sigma=1.0)
    else:
        f = mapper.filters.Gauss_density(data,
            sigma=1.0)
    '''
        Step 4: Mapper parameters
    '''
    cover = mapper.cover.cube_cover_primitive(intervals=intervals, overlap=overlap)
    cluster = mapper.single_linkage()
    if not is_vector_data:
        metricpar = {}
    mapper_output = mapper.mapper(data, f,
        cover=cover,
        cluster=cluster,
        point_labels=point_labels,
        cutoff=None,
        metricpar=metricpar)
    mapper.scale_graph(mapper_output, f, cover=cover,
                       weighting='inverse', maxcluster=100, expand_intervals=False, exponent=10,
                       simple=False)
#    cutoff = mapper.cutoff.first_gap(gap=0.1)
#    mapper_output.cutoff(cutoff, f, cover=cover, simple=False)
    
    '''
        Step 5: Save results
    '''
    
    # store the x-y coordinate of the mapper_output simplicial complex 
    # as well as the scale parameters in a dictionary
    temp_out = mapper_output.draw_2D()
    Output = {}
    Output['tag'] = 'scaleParam_' + intervals + '_' + overlap
    # vertex_pos stores the x y coordinates however, not checked the right way of extracting it from mapper_output
    Output['x'] = temp_out.vertex_pos[:, 0]
    Output['y'] = temp_out.vertex_pos[:, 1]
    Output['intervals'] = intervals
    Output['overlap'] = overlap
    
    return Output
    
