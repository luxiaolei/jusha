
import pandas as pd
import numpy as np
import jushacore
import os
import copy
from sklearn.preprocessing import normalize,StandardScaler
from utilityFuncs import statistical_tests, genJetColormap

cutoffs = {'first_gap': jushacore.cutoff.first_gap(gap=.1),
           'biggest_gap': jushacore.cutoff.biggest_gap,
           'variable_exp_gap':jushacore.cutoff.variable_exp_gap(exponent=.1, maxcluster=20),
           'variable_exp_gap2': jushacore.cutoff.variable_exp_gap2(exponent=.1, maxcluster=20)}

"""
20151220_TL
call jushacore engine in the server to execute the cluster process according to the user parameter setting
interval
overlap
*potentially, the ability to select different filter lenses should also be made available once activated
*as well as whether to perform a scale graph algorithm following the main loop
"""
def runJusha(selfvars, filename, intervals=8, overlap=50.0):
    #type check inputParams, string for default,
    #float for user inputed
    if type(selfvars.parameters['interval']) == int:
        intervals = selfvars.parameters['interval']
        overlap = selfvars.parameters['overlap']

    in_file = [f for f in os.listdir('uploads/')]
    assert len(in_file) > 0
    in_file = 'uploads/' + filename
    #data = np.loadtxt(str(in_file), delimiter=',', dtype=np.float)
    #  20151220_TL pass on the selected features to be run in Model
    CF = selfvars.checkedFeatures

    data = selfvars.df.ix[:, CF].astype(np.float64)

    data.to_csv('uploads/' + 'RAN'+ filename, index=False)
    print 'jusha is runing with calculating %s'%CF
    #dataNormed = data.ix[:, ]
    for col in selfvars.checkedFeaturesNorm:
        if col not in CF:
            continue
        else:
            print '%s is normalized!'%col
            Scaler = StandardScaler()
            data[col] = Scaler.fit_transform(data[col].values[:, np.newaxis]).ravel()
    print data.describe()
    data = data.values

    Filter = np.array(selfvars.parameters['filter'])
    cover = jushacore.cover.cube_cover_primitive(intervals, overlap)
    cluster = jushacore.single_linkage()
    metricpar = {'metric': selfvars.parameters['metric']}

    if selfvars.parameters['cutoff'] != 'scale_graph':
        cutoff = cutoffs[selfvars.parameters['cutoff']]

    mapper_output = jushacore.jushacore(data, Filter,
        cover=cover,
        cluster=cluster,
        point_labels= None,
        cutoff=None,
        metricpar=metricpar)
    #cutoff = jushacore.cutoff.first_gap(gap=0.1)
    if selfvars.parameters['cutoff'] != 'scale_graph':
        mapper_output.cutoff(cutoff, Filter, cover=cover, simple=False)
    else:
        jushacore.scale_graph(mapper_output, Filter,
                            weighting=selfvars.parameters['weighting'],
                            exponent=selfvars.parameters['exponent'],
                            maxcluster=None, expand_intervals=False)

    """
	20151220_TL
	dump the cluster outcome to a json file for d3 template and html to pick up and display in the front ends
	this includes the following tuples:
	vertices/nodes
	edges
	statistics associated to each vertex/node: number of nodes, ks-test p value, t-test p value	-- to deactivate by default, only switch on when need!!!
	"""
    def to_d3js_graph(mapper_output):
        """
        Convert the 1-skeleton of a L{mapper_output} to a dictionary
        designed for exporting to a json package for use with the d3.js
        force-layout graph visualisation system.
        """
        G = {}
        G['vertices'] = [{'index': i, 'level': n.level, 'members':
                          list(n.points), 'attribute': n.attribute}
                         for (i,n) in enumerate(mapper_output.nodes)]
        G['edges'] = [{'source': e[0], 'target': e[1], 'wt':
                       mapper_output.simplices[1][e]} for e in
                      mapper_output.simplices[1].keys()]
        distinctAttr = [i['attribute'] for i in G['vertices']]
        distinctAttr = list(set(distinctAttr))
        distinctAttr.sort()
        G['distinctAttr'] = distinctAttr
        G['colormap'] = genJetColormap(len(distinctAttr))

        #generate two maps for index key-value pairs
        G['indexNameMap']= {}
        G['nameIndexMap']= {}

        for k,v in enumerate(selfvars.df.index):
            G['indexNameMap'][k] = v
            G['nameIndexMap'][v] = k

        return G
    return to_d3js_graph(mapper_output)
