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
from sklearn.preprocessing import normalize

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])


class selfgloablvars:
    """
    This class is used for passing variables between functions
    """
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
        self.binTicks = 'Not Signed'
        self.binClicked = 'Not Signed'


selfvars = selfgloablvars()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/features')
def send_features():
    """
    send feature info to clients
    """
    return jsonify(features=list(selfvars.features))

@app.route('/bins')
def send_bins():
    """
    send the bins and ticks data to client
    """
    return json.dumps(selfvars.feature_his)

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

@app.route('/feature_ajax', methods=['POST','GET'])
def feature_ajax():
    """
    recieve selected feature from client, then
    *call recolor function
    *set selfvars.ma
    """
    selected_f = request.json['selected']
    binsNumber = int(request.json['binsNumber'])

    selfvars.selected_feature = selected_f

    #update the selfvars.feature_his and generate the
    #primary barChart
    array = selfvars.df[selected_f]
    selfvars.feature_his, selfvars.binTicks = binGen(array,binsNumber)

    return json.dumps({'ans':'1'})

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
            #store the col into selfvars obj
            selfvars.features = list(df.columns.values)
            df.replace([np.inf, -np.inf], np.nan)
            selfvars.df = df.dropna()

            #initialize mapperoutput
            selfvars.mapperoutput = 1
        return jsonify(features=list(selfvars.features))#json.dumps({'result': 'Successfully Uploaded!'})
    except Exception,e:
        return json.dumps(str(e))
    return json.dumps({'ans': 'failed!'})

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/mapperjson')
def mapper_cluster():
    """
    Generates mapperoutput
    """
    selfvars.mapperoutput = runMapper()
    return json.dumps(selfvars.mapperoutput)

@app.route('/mapperJsonSaved')
def mapperRecolored():
    """
    This is for search utility to look up data in nodes
    """
    print 'i m called!'

    return json.dumps(selfvars.mapperoutput)

@app.route('/newjson')
def newjson():
    """
    This is for recoloring based on selected feature
    """
    a = copy.deepcopy(selfvars.mapperoutput)
    mappernew = recolor_mapperoutput(a)
    return json.dumps(mappernew)



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
    CF = selfvars.checkedFeatures
    data = selfvars.df.ix[:, CF]
    print CF
    #dataNormed = data.ix[:, ]
    for col in selfvars.checkedFeaturesNorm:
        if col not in CF:
            continue
        else:
            print '%s is normalized!'%col
            data[col] = normalize(data[col].values[:, np.newaxis],axis=0).ravel()
    #print data
    data = data.values

    '''
        Step 1: Declare filters and cutoff selection dictionary

    '''
    filterFuncs = {'eccentricity': jushacore.filters.eccentricity ,
                  'Gauss_density': jushacore.filters.Gauss_density,
                  'kNN_distance': jushacore.filters.kNN_distance,
                  'distance_to_measure': jushacore.filters.distance_to_measure,
                  'graph_Laplacian': jushacore.filters.graph_Laplacian,
                  'dm_eigenvector' : jushacore.filters.dm_eigenvector,
                  'zero_filter': jushacore.filters.zero_filter}
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

    def convertSelections(Set):
        ans = [vertices[i]['members'] for i in Set]
        #make it flat
        ans = [item for sublist in ans for item in sublist]
        #make the items distinctive
        ans = list(set(ans))
        return ans
    vertices = selfvars.mapperoutput['vertices']
    SeA = convertSelections(SelectionA)
    SeB = convertSelections(SelectionB)

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







            #testsRes.append(ansDic)
    #print testsRes
    #print 'there r %s doable nodes'%len(testsRes)
    #print 'there r %s nodes '%len(dataIndexesList)
    #return testsRes


def genJetColormap(n):
    """
    give the length of the list contains only distict attribute value
    return an HX color map range which has the same length
    """
    interval = 256 / n
    indexes = [interval*(i) for i in range(n)]
    indexes[-1] = 255
    return [str(rgb2hex(jet(j))) for j in indexes]


    #return [str(rgb2hex(jet(float(i)/n)[:-1])) for i in range(n)]
