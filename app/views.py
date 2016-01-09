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
from scipy import stats
from matplotlib.cm import jet
from matplotlib.colors import rgb2hex
from sklearn.preprocessing import normalize,StandardScaler
from jushaFilter import svmFilter, selfdefined

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

"""
This class is used for passing variables between functions
20151220_TL
Equivalent to the model in the MVC web app framework, where key user business data are stored and queried from
"""
class selfgloablvars:
    def __init__(self):
        self.mapperoutput = 1
        self.features = 1
        self.df = 1
        self.selected_feature = 1
        self.checkedFeatures = 1
        self.checkedFeaturesNorm = 1
        self.feature_his = 1
        self.filter = 1
        self.metric = {}
        self.cutoff = 1
        self.inputInterval = 'Not Signed'
        self.inputOverlap = 'Not Signed'
        self.binsNumber = 20
        self.binTicks = 'Not Signed'
        self.binClicked = 'Not Signed'


selfvars = selfgloablvars()

filterFuncs = {'eccentricity': jushacore.filters.eccentricity ,
              'Gauss_density': jushacore.filters.Gauss_density,
              'kNN_distance': jushacore.filters.kNN_distance,
              'distance_to_measure': jushacore.filters.distance_to_measure,
              'graph_Laplacian': jushacore.filters.graph_Laplacian,
              'dm_eigenvector' : jushacore.filters.dm_eigenvector,
              'zero_filter': jushacore.filters.zero_filter,
              'selfdefined': selfdefined,
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
    print 'selfvars.checkedFeatures is %s'%selfvars.checkedFeatures
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
        if key == 'selfdefined':
            array = selfvars.df.ix[:, -1]
        else:
            array = pd.Series(filterFuncs[key](data, metricpar={}))
    else:
        array = selfvars.df[selfvars.selected_feature]
    selfvars.feature_his, selfvars.binTicks = binGen(array,selfvars.binsNumber)
    return json.dumps(selfvars.feature_his)

"""
20151220_TL
For the secondary bar charts? redundant then.
"""
@app.route("/binClickedAjax",  methods=['POST','GET'])
def binClicked():
    """
    recieve clicked bin index from client
    assign the index to selvar.binclicked
    to perform the sub barchart generation
    """
    binClicked = request.json['binClicked']
    selfvars.binClicked = int(binClicked)
    return json.dumps({'ans':1})


"""
20151220_TL
going to get redundant; code-structurally shouldn't be in this part of the code anyways
"""
@app.route('/binsSecondary')
def binsSecondary():
    """
    send the secondary bar chart data to clients
    """

    clickeRange = selfvars.binTicks[selfvars.binClicked]
    array = selfvars.df[selfvars.selected_feature]
    if selfvars.binClicked == 9:
        #the last bar
        array = array.ix[(array >= clickeRange[0])]
    else:
        array = array.ix[(array >= clickeRange[0]) & (array < clickeRange[1])]
    return json.dumps(binGen(array)[0])


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
    *call jushacore function to statisticT new Json
    """
    #if request.method == 'POST'
    try:
        #set input params to selfvars
        selfvars.inputInterval = int(request.json['interval'])
        selfvars.inputOverlap = float(request.json['overlap'])
        selfvars.checkedFeatures = request.json['checkedFeatures']
        selfvars.checkedFeaturesNorm = request.json['checkedFeaturesNorm']
        selfvars.filter = request.json['filter']
        selfvars.metric['metric'] = request.json['metric']
        selfvars.cutoff = request.json['cutoff']

        #Reconstruct the dataframe based on selected index
        #!!WHen multipul calls, the features and df are shrinking!! should solve the problem
        #through redesign a poper user workflow!
        index = request.json['index']
        print index
        if index != 'None':
            assert index in selfvars.features
            selfvars.features.remove(index)
            selfvars.df.index = selfvars.df.ix[:, index]
            print index
            del selfvars.df[index]

        selfvars.mapperoutput = 1
        return json.dumps({'ans': str(type(selfvars.inputInterval))})
    except Exception,e:
        return json.dumps({'ans':str(e)})

@app.route('/explainAjax',  methods= ['POST', 'GET'])
def explainAjax():
    SelectionA = request.json['selectionA']
    SelectionB = request.json['selectionB']
    test = statistical_tests(SelectionA, SelectionB)
    return json.dumps(test)#{'ans':str('yeyeye')})



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

            #initialize mapperoutput
            selfvars.mapperoutput = 1
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
    Generates mapperoutput
    """
    selfvars.mapperoutput = runMapper()
    return json.dumps(selfvars.mapperoutput)

"""
20151220_TL
save the jushacore output in another url to be re-coloured and for further reference?
"""
@app.route('/mapperJsonSaved')
def mapperRecolored():
    """
    This is for search utility to look up data in nodes
    """
    print 'i m called!'

    return json.dumps(selfvars.mapperoutput)

"""
20151220_TL
Division between View -> Controller and Controller -> View direction of the interactions
"""

"""
20151220_TL
View -> Controller
"""


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
    a = copy.deepcopy(selfvars.mapperoutput)
    mappernew = recolor_mapperoutput(a)
    return json.dumps(mappernew)


"""
20151220_TL
this module contains pure View-Controller interaction, nothing involves the Model within, however,
worth keeping a note for Model logging the actions, as registered user later may want to come back to the same state he last time left
to be called in the "newjson" module
"""
def recolor_mapperoutput(mapperjson):
    """
    set selfvars.mappernew to an altered mapper_ouput in json format
    the attartribut of vertices become the avg values of elements in the vertices
    """
    target = mapperjson
    for key, each_dic in enumerate(target['vertices']):
        elements_index = each_dic['members'] #list
        coresspoding_rows = selfvars.df.ix[elements_index, selfvars.selected_feature]
        average_value = np.average(coresspoding_rows)
        target['vertices'][key]['attribute'] = average_value

    #generate colormap both for domain and range
    distinctAttr = [i['attribute'] for i in target['vertices']]
    distinctAttr = list(set(distinctAttr))
    distinctAttr.sort()
    target['distinctAttr'] = distinctAttr
    target['colormap'] = genJetColormap(len(distinctAttr))
    return target

"""
20151220_TL
call jushacore engine in the server to execute the cluster process according to the user parameter setting
interval
overlap
*potentially, the ability to select different filter lenses should also be made available once activated
*as well as whether to perform a scale graph algorithm following the main loop
"""
def runMapper(intervals=8, overlap=50.0):
    #type check inputParams, string for default,
    #float for user inputed
    if type(selfvars.inputInterval) == int:
        intervals = selfvars.inputInterval
        overlap = selfvars.inputOverlap

    in_file = [f for f in os.listdir('uploads/')]
    assert len(in_file) > 0
    in_file = 'uploads/' + session['filename']
    #data = np.loadtxt(str(in_file), delimiter=',', dtype=np.float)
    #  20151220_TL pass on the selected features to be run in Model
    CF = selfvars.checkedFeatures

    data = selfvars.df.ix[:, CF].astype(np.float64)

    data.to_csv('uploads/' + 'RAN'+session['filename'], index=False)
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

    '''
        Step 1: Declare filters and cutoff selection dictionary

    '''
        #return data[:,-1]

    filterFuncs = {'eccentricity': jushacore.filters.eccentricity ,
                  'Gauss_density': jushacore.filters.Gauss_density,
                  'kNN_distance': jushacore.filters.kNN_distance,
                  'distance_to_measure': jushacore.filters.distance_to_measure,
                  'graph_Laplacian': jushacore.filters.graph_Laplacian,
                  'dm_eigenvector' : jushacore.filters.dm_eigenvector,
                  'zero_filter': jushacore.filters.zero_filter,
                  'selfdefined': selfdefined,
                  'svm': svmFilter}
    cutoffs = {'first_gap': jushacore.cutoff.first_gap(gap=.1),
               'biggest_gap': jushacore.cutoff.biggest_gap,
               'variable_exp_gap':jushacore.cutoff.variable_exp_gap(exponent=.1, maxcluster=20),
               'variable_exp_gap2': jushacore.cutoff.variable_exp_gap2(exponent=.1, maxcluster=20)}

    Filter = filterFuncs[str(selfvars.filter)]
    cover = jushacore.cover.cube_cover_primitive(intervals, overlap)
    cluster = jushacore.single_linkage()
    metricpar = selfvars.metric
    cutoff = cutoffs[selfvars.cutoff]

    '''
        Step 2: Metric
    '''
    intrinsic_metric = False
    is_vector_data = data.ndim != 1
    '''
        Step 3: Filter function
       ['eccentricity', 'Gauss_density', 'kNN_distance',
           'distance_to_measure', 'graph_Laplacian', 'dm_eigenvector',
           'zero_filter']
    '''




    if is_vector_data:
        #metricpar = selfvars.metric  #{'metric': 'euclidean'}
        if str(selfvars.filter) == 'selfdefined':
            #f = Filter(selfvars.df, metricpar=metricpar, index= -1)
            f = selfvars.df.ix[:, -1].values
        else:

            f = Filter(data, metricpar=metricpar)
    else:
        f = jushacore.filters.Gauss_density(data,
            sigma=1.0)
    # Filter transformation

    '''
        Step 4: jushacore parameters
    '''

    if not is_vector_data:
        metricpar = {}
    mapper_output = jushacore.jushacore(data, f,
        cover=cover,
        cluster=cluster,
        point_labels= None,
        cutoff=None,
        metricpar=metricpar)
    #cutoff = jushacore.cutoff.first_gap(gap=0.1)
    mapper_output.cutoff(cutoff, f, cover=cover, simple=False)

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

        #G['statisticT'] = statistical_tests(G['vertices'])


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




        """
        G['subnodes'] = [i['members'] for i in G['vertices']]
        #add subnodes connection,point subnodes to the main one
        org_length = len(G['vertices'])
        new_vertices = []
        for key, dic in enumerate(G['vertices']):
			for elem in dic['members']:
                subnodes = {}
                subnodes['index'] = elem
                subnodes['members'] = [1]
                #attribute of the subnodes is the same to the main node
                subnodes['attribute'] = dic['attribute']
                new_vertices.append(subnodes)
                G['edges'].append({'source':org_length, \
                    'target':dic['index']})
                org_length +=1
        G['vertices'] += new_vertices
        """
        return G
    return to_d3js_graph(mapper_output)


def binGen(array, binsNumber=10):
    """
    input an array
    return a list of dicts for drawing barchart
    """
    array_his = np.histogram(array,binsNumber)
    array_his = [list(i) for i in array_his]

    def getDatainBins(ticks):
        """
        ticks: [(lowerbound, upperbound),..]
        return a list of lists which contains data index for
        each bins
        """
        binData = []
        for k, bounds in enumerate(ticks):
            lower, upper= bounds
            if k == len(ticks)-1:
                #last bar, should inclue the last number
                dataIndex = array.ix[(array >= float(lower))& (array <= float(upper))].index.values
            else:
                dataIndex = array.ix[(array >= float(lower)) & (array < float(upper))].index.values
            binData.append(list(dataIndex))
        return binData

    bins = array_his[0]
    ticksOrigin = array_his[1]
    ticksOrigin = zip(ticksOrigin[:-1], ticksOrigin[1:])

    binData = getDatainBins(ticksOrigin)
    ticks = ['%.2f'%i for i in array_his[1]]
    ticks = zip(ticks[:-1], ticks[1:])


    assert type(binsNumber)==int
    jetcolor = genJetColormap(binsNumber)
    feature_his = []
    for k, v in enumerate(zip(bins, ticks)):
        dic = {'bins':v[0], 'ticks':v[1], 'binData':binData[k], 'color':jetcolor[k]}
        feature_his.append(dic)

    return (feature_his, ticksOrigin)


def statistical_tests(SelectionA, SelectionB, top=3):
    """
    Selection: input list of vertices indexes
    Return a list of ranked features, and p-value for t-unpaied test
    and ks-2samples test
    """
    #dataIndexesList = [i['members'] for i in vertices]

    """
    def convertSelections(Set):
        ans = [vertices[i]['members'] for i in Set]
        #make it flat
        ans = [item for sublist in ans for item in sublist]
        #make the items distinctive
        ans = list(set(ans))
        return ans
    """
    vertices = selfvars.mapperoutput['vertices']
    SeA = SelectionA#convertSelections(SelectionA)
    SeB = SelectionB#convertSelections(SelectionB)

    testsRes = []
    ranks = []
    """
    for pts in dataIndexesList:
        rankCols = []
        ansDic = {}
        if len(pts) < 10:

            testsRes.append(len(pts))
            rankCols.append([])
            continue
        else:
    """
    rankCols = []
    ansDic = {}
    df = copy.deepcopy(selfvars.df)
    for col in selfvars.features:
        targetSerie = df[col]
        dataA = targetSerie.ix[targetSerie.index.isin(SeA)].values
        dataB = targetSerie.ix[targetSerie.index.isin(SeB)].values
        #notinNodeArray = targetSerie.ix[~targetSerie.index.isin(pts)].values
        P4ttest = stats.ttest_ind(dataA, dataB)[-1]
        P4kstest = stats.ks_2samp(dataA, dataB)[-1]
        ansDic[col] = [round(i, 3) for i in [P4ttest, P4kstest]]
        rankCols.append( min(P4kstest, P4ttest))

    sortByminPindex = np.argsort(rankCols)
    sortByCol = [selfvars.features[i] for i in sortByminPindex]
    ans = [{'colname': col, 'p4t': ansDic[col][0], 'p4ks':ansDic[col][1]}
            for k, col in enumerate(sortByCol) if k < top]

    #print sortByCol
    return ans


"""
20151220_TL
generate Jet Colour scheme for node colouring
To be called in "recolor_mapperoutput"
"""
def genJetColormap(n):
    """
    give the length of the list contains only distict attribute value
    return an HX color map range which has the same length
    """
    interval = 256. / n
    indexes = [interval*(i) for i in range(n)]
    indexes[-1] = 255
    return [str(rgb2hex(jet(int(j)))) for j in indexes]


    #return [str(rgb2hex(jet(float(i)/n)[:-1])) for i in range(n)]
