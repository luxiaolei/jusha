"""
This py contains all the View -> Controller and Controller -> View modules to be executed in the front end j
"""

#!encoding=utf-8
from flask import redirect, request, render_template, url_for, session, g, jsonify
from flask_wtf import Form
from wtforms import RadioField
from app import app
from werkzeug import secure_filename
import os
import copy
import json
import jushacore
import numpy as np
import os.path as op
import pandas as pd
from jushawrapper import runJusha
from utilityFuncs import binGen, recolor_mapperoutput, statistical_tests
from jushaFilter import svmFilter

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

"""
This class is used for passing variables between functions
20151220_TL
Equivalent to the model in the MVC web app framework, where key user business data are stored and queried from
"""
class selfgloablvars:
    def __init__(self):
        self.jushaoutput = 1
        self.features = 1
        self.df = 1
        self.selected_feature = 1
        self.checkedFeatures = 1
        self.checkedFeaturesNorm = 1
        self.barchart = 'Not Signed'
        self.parameters = {}
        self.graphStates = {'svgimg0': {'parameters': [], 'vertices': [], 'nodes': []}}

selfvars = selfgloablvars()

filterFuncs = {'eccentricity': jushacore.filters.eccentricity ,
              'Gauss_density': jushacore.filters.Gauss_density,
              'kNN_distance': jushacore.filters.kNN_distance,
              'distance_to_measure': jushacore.filters.distance_to_measure,
              'graph_Laplacian': jushacore.filters.graph_Laplacian,
              'dm_eigenvector' : jushacore.filters.dm_eigenvector,
              'zero_filter': jushacore.filters.zero_filter,
              'svm': svmFilter}

"""
20151220_TL
Utilities: input format control
"""
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


"""
20151220_TL
View -> Controller
"""

"""
20151220_TL
temp store selected features column data in a url for immediate use, to be updated any time when the new request arrives
http://flask.pocoo.org/docs/0.10/api/#returning-json
"""
@app.route('/features')
def send_features():
    """
    Generates new columns for sklearn clustering labels, and its correspongind silhouette_score
    User Selected Features used for genrating labels
    Then, update selfvars.df, selfvars.features
    """
    from sklearn.cluster import KMeans,AffinityPropagation,MeanShift,SpectralClustering,DBSCAN,\
                                AgglomerativeClustering, Birch
    from sklearn.metrics import silhouette_score

    data = selfvars.df.ix[:, selfvars.checkedFeatures].values
    name = ['KMeans', 'AfPropagatn', 'MeanShift', 'SpectralCluster', 'DBSCAN', 'AgCluster', 'Brich']
    #print 'selfvars.checkedFeatures is %s'%selfvars.checkedFeatures
    #for those clustering emthod require n_clusters, set it tobe the number fo features
    default_num_clusters = 5# len(selfvars.checkedFeatures)
    clusteringObjs = [KMeans(n_clusters=default_num_clusters, init='k-means++', n_init=10, max_iter=300, tol=0.0001, precompute_distances='auto', verbose=0, random_state=None, copy_x=True, n_jobs=1),
                      AffinityPropagation(damping=0.5, max_iter=200, convergence_iter=15, copy=True, preference=None, affinity='euclidean', verbose=False),
                      MeanShift(bandwidth=None, seeds=None, bin_seeding=False, min_bin_freq=1, cluster_all=True, n_jobs=1),
                      SpectralClustering(n_clusters=default_num_clusters, eigen_solver=None, random_state=None, n_init=10, gamma=1.0, affinity='rbf', n_neighbors=10, eigen_tol=0.0, assign_labels='kmeans', degree=3, coef0=1, kernel_params=None),
                      DBSCAN(eps=0.5, min_samples=5, metric='euclidean', algorithm='auto', leaf_size=30, p=None, random_state=None),
                      AgglomerativeClustering(n_clusters=default_num_clusters, affinity='euclidean',connectivity=None, n_components=None, compute_full_tree='auto', linkage='ward'),
                      Birch(threshold=0.5, branching_factor=50, n_clusters=default_num_clusters, compute_labels=True, copy=True)]
    #lables = [estimator.fit(data).labels_ for estimator in clusteringObjs]
    for k, col_name in enumerate(name):
        if col_name in ['KMeans']:#, 'MeanShift', 'SpectralCluster']:
            try:
                label = clusteringObjs[k].fit(data).labels_
                score = '%.2f'%silhouette_score(data, label)
                col_name = ('[{0}]{1}').format(score, col_name)
                selfvars.df[col_name] = label
            except Exception,e:
                print e
        else:
            continue

    selfvars.features = list(selfvars.df.columns)
    FwithFilters = ['[F]'+k for k in filterFuncs.keys()] + selfvars.features
    return jsonify(features=list(FwithFilters))

"""
20151220_TL
Request the bins and feature selection parameters - ticks, and call the send_bins to execute the job
"""
@app.route('/bins')
def send_bins():
    """
    send the bins and ticks data to client
    """
    #update the selfvars.feature_his and generate the
    #primary barChart
    if '[F]' in selfvars.selected_feature:
        data = selfvars.df.ix[:, selfvars.checkedFeatures].values
        key = str(selfvars.selected_feature).strip('[F]')

        array = pd.Series(filterFuncs[key](data, metricpar={"metric":selfvars.parameters['metric']}))
    else:
        array = selfvars.df[selfvars.selected_feature]
    selfvars.parameters['filter'] = list(array)
    selfvars.barchart = binGen(array,selfvars.binsNumber)
    return json.dumps(selfvars.barchart[0])


"""
20151220_TL
from View passed down the re-colour request and this Flask module execute the job for the selected feature
"""
@app.route('/feature_ajax', methods=['POST','GET'])
def feature_ajax():
    """
    recieve selected feature from client, then
    *call recolor function
    *set selfvars.ma
    """
    selected_f = request.json['selected']
    selfvars.binsNumber = int(request.json['binsNumber'])
    selfvars.selected_feature = selected_f
    return json.dumps({'ans':'1'})

"""
20151220_TL
parameter specification passed down from View to fire up jushacore for the main cluster loop
"""
@app.route('/paramsAjax', methods=['POST'])
def paramsAjax():
    """
    *recieve params from clients
    *when user click inspect
    """
    #if request.method == 'POST'
    try:
        #set input params to selfvars
        selfvars.parameters['interval'] = int(request.json['interval'])
        selfvars.parameters['overlap'] = float(request.json['overlap'])
        selfvars.checkedFeatures = request.json['checkedFeatures']
        selfvars.checkedFeaturesNorm = request.json['checkedFeaturesNorm']
        selfvars.parameters['metric'] = request.json['metric']
        selfvars.parameters['cutoff'] = request.json['cutoff']
        selfvars.parameters['weighting'] = request.json['weighting']
        selfvars.parameters['exponent'] = float(request.json['exponent'])
        #Reconstruct the dataframe based on selected index
        #!!WHen multipul calls, the features and df are shrinking!! should solve the problem
        #through redesign a poper user workflow!
        index = request.json['index']

        if index != 'None':
            assert index in selfvars.features
            selfvars.features.remove(index)
            selfvars.df.index = selfvars.df.ix[:, index]

            del selfvars.df[index]

        selfvars.jushaoutput = 1
        return json.dumps({'ans': str(type(selfvars.parameters['interval']))})
    except Exception,e:
        return json.dumps({'ans':str(e)})

@app.route('/explainAjax',  methods= ['POST', 'GET'])
def explainAjax():
    SelectionA = request.json['selectionA']
    SelectionB = request.json['selectionB']
    test = statistical_tests(selfvars, SelectionA, SelectionB)
    return json.dumps(test)#{'ans':str('yeyeye')})

@app.route('/graphstateAjax',  methods= ['POST', 'GET'])
def graphStateSaver():
    """
    when user click saveimg button, save nodes co-ordinates and parameters
    """
    coordinates = request.json['xy']
    assert type(coordinates)==list
    stateId = request.json['stateId']
    #construct the state dictionary
    savedOutput = selfvars.jushaoutput.copy()
    for key, xy in enumerate(coordinates):
        assert type(xy)==list
        xy = [float(i) for i in xy]
        savedOutput['vertices'][key]['x'] = xy[0]
        savedOutput['vertices'][key]['y'] = xy[1]
    savedOutput['parameters'] = selfvars.parameters.copy()
    #savedOutput['parameters']['filter'] = list(savedOutput['parameters']['filter'])
    savedOutput['selected_feature'] = selfvars.selected_feature
    selfvars.graphStates[stateId] = savedOutput
    return json.dumps({'ans':stateId})

@app.route('/Restore', methods= ['POST', 'GET'])
def graphstateRestoreAjax():
    """
    when user click the minisvg, do the restoring
    """
    stateId = request.json['stateId']
    return json.dumps({'ans':stateId})

@app.route('/restoreJson/<svgimgid>')
def restorejson(svgimgid):
    return json.dumps(selfvars.graphStates[svgimgid])

"""
20151220_TL
once the "upload" request occurs, go to the local folder and fetch the dataset csv/txt file and dump it on the "/uploadFile" url for further use
furthermore, store in the temp object df for jushacore to read as input of the cluster process
"""
@app.route('/uploadFile', methods= ['POST'])
def uploadFile():
    try:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            message = 'Successfully Uploaded!'
            session['filename'] = filename
            #retrive the column names and pass to /
            #pop index col
            FirstRowisIndex= False
            if FirstRowisIndex:
                df = pd.read_csv('uploads/'+filename, index_col=0)
            else:
                df = pd.read_csv('uploads/'+filename)
            df.columns = [str(i).replace(' ','_') for i in df.columns]
            #store the col into selfvars obj
            selfvars.features = list(df.columns.values)
            df.replace([np.inf, -np.inf], np.nan)
            selfvars.df = df.dropna()
            selfvars.df1 = df.dropna()

            #initialize jushaoutput
            selfvars.jushaoutput = 1
        return jsonify(features=list(selfvars.features))#json.dumps({'result': 'Successfully Uploaded!'})
    except Exception,e:
        return json.dumps(str(e))
    return json.dumps({'ans': 'failed!'})

"""
20151220_TL
fire up the html to the front end via the Jinja2 framework, no fuss
http://flask.pocoo.org/docs/0.10/quickstart/
"""
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

"""
20151220_TL
fire up the html to the front end via the Jinja2 framework, no fuss
http://flask.pocoo.org/docs/0.10/quickstart/
"""
@app.route('/mapperjson')
def mapper_cluster():
    """
    Generates jushaoutput
    """
    #check if the current params setting has been processed
    for dic in selfvars.graphStates.values():
        try:
            if selfvars.parameters == dic['parameters']:
                #print ('Restoring the old graph with settings: {0}').format(dic['parameters'])
                selfvars.jushaoutput = dic
                return json.dumps(selfvars.jushaoutput)
        except Exception,e:
            print e
            continue
    #for first time run the current params settings, save the result
    selfvars.jushaoutput = runJusha(selfvars, session['filename'])
    #tempkey = np.random.randint(1000)
    #selfvars.graphStates[tempkey] = copy.deepcopy(selfvars.jushaoutput)
    #selfvars.graphStates[tempkey]['parameters'] = selfvars.parameters
    return json.dumps(selfvars.jushaoutput)

"""
20151220_TL
save the jushacore output in another url to be re-coloured and for further reference?
"""
@app.route('/mapperJsonSaved')
def mapperRecolored():
    """
    This is for search utility to look up data in nodes
    """
    return json.dumps(selfvars.jushaoutput)


"""
20151220_TL
take the copy from '/mapperJsonSaved' and perform the re-colouring exercise in correspondence to the feature selected
refresh the content in this url (the same url)
"""
@app.route('/newjson')
def newjson():
    """
    This is for recoloring based on selected feature
    """
    a = copy.deepcopy(selfvars.jushaoutput)
    mappernew = recolor_mapperoutput(selfvars, a)
    return json.dumps(mappernew)
