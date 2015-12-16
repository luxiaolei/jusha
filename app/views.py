#!encoding=utf-8
from flask import redirect, request, render_template, url_for, session, g, jsonify
from flask_wtf import Form
from wtforms import RadioField
from app import app
from werkzeug import secure_filename
import os
import json
import mapper
import numpy as np
import os.path as op
import pandas as pd
from scipy import stats

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])


class selfgloablvars:
    """
    This class is used for passing variables between functions
    """
    def __init__(self):
        self.features = 1
        self.df = 1
        self.selected_feature = 1
        self.mappernew = 1
        self.feature_his = 1
        self.inputInterval = 'Not Signed'
        self.inputOverlap = 'Not Signed'

selfvars = selfgloablvars()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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

        #reset the arrtribute
        target['vertices'][key]['attribute'] = average_value
    selfvars.mappernew =  target


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

@app.route('/feature_ajax', methods=['POST','GET'])
def feature_ajax():
    """
    recieve selected feature from client, then
    *call recolor function
    *set selfvars.ma
    """
    selected_f = request.json['selected']
    selfvars.selected_feature = selected_f
    #update the mapperjson based on the selected f
    with open('mapperoutput.json', 'rb') as f:
        mapperoutput = json.load(f)
    recolor_mapperoutput(mapperoutput)

    #update the selfvars.feature_his
    array = selfvars.df[selected_f]
    array_his = np.histogram(array)
    array_his = [list(i) for i in array_his]

    def getDatainBins(ticks):
        print ticks
        """
        ticks: [(lowerbound, upperbound),..]
        return a list of lists which contains data index for
        each bins
        """
        binData = []
        df, col = selfvars.df, selfvars.selected_feature
        for k, bounds in enumerate(ticks):
            lower, upper= bounds
            if k == len(ticks)-1:
                #last bar, should inclue the last number
                dataIndex = df.ix[(df[col] >= float(lower))& (df[col] <= float(upper))].index.values
            else:
                dataIndex = df.ix[(df[col] >= float(lower)) & (df[col] < float(upper))].index.values
            binData.append(list(dataIndex))
        return binData

    bins = array_his[0]
    ticksOrigin = array_his[1]
    ticksOrigin = zip(ticksOrigin[:-1], ticksOrigin[1:])
    binData = getDatainBins(ticksOrigin)

    ticks = ['%.2f'%i for i in array_his[1]]
    ticks = zip(ticks[:-1], ticks[1:])


    selfvars.feature_his = []
    for k, v in enumerate(zip(bins, ticks)):
        dic = {'bins':v[0], 'ticks':v[1], 'binData':binData[k]}
        selfvars.feature_his.append(dic)

    return json.dumps({'ans':'1'})

    #return render_template(url_for('newjson'), json.dumps(newmapperJson['vertices'])


@app.route('/paramsAjax', methods=['POST'])
def paramsAjax():
    """
    *recieve params from clients
    *call mapper function to generate new Json
    """
    #if request.method == 'POST'
    try:
        #set input params to selfvars
        selfvars.inputInterval = int(request.json['interval'])
        selfvars.inputOverlap = float(request.json['overlap'])
        return json.dumps({'ans': str(type(selfvars.inputInterval))})
    except Exception,e:
        return json.dumps({'ans':str(e)})


@app.route('/newjson')
def newjson():
    """
    mappernew was been set in feature ajax process
    """
    return json.dumps(selfvars.mappernew)


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
            selfvars.features = df.columns.values
            selfvars.df = df
        return json.dumps({'result': 'Successfully Uploaded!'})
    except Exception,e:
        return json.dumps(str(e))
    return json.dumps({'ans': 'failed!'})

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/mapperjson')
def mapper_cluster(intervals=8, overlap=50.0):
    #type check inputParams, string for default,
    #float for user inputed
    if type(selfvars.inputInterval) == int:
        intervals = selfvars.inputInterval
        overlap = selfvars.inputOverlap
        print intervals
        print overlap

    print type(intervals),type(overlap)
    print ">>"*30
    print selfvars.inputInterval
    print selfvars.inputOverlap
    in_file = [f for f in os.listdir('uploads/')]
    assert len(in_file) > 0
    in_file = 'uploads/' + session['filename']
    print "*"*10
    print 'File %s is loaded!'%session['filename']
    #data = np.loadtxt(str(in_file), delimiter=',', dtype=np.float)
    data = selfvars.df.values

    '''
        Step 2: Metric
    '''
    intrinsic_metric = False
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
    # Filter transformation

    '''
        Step 4: Mapper parameters
    '''
    cover = mapper.cover.cube_cover_primitive(intervals, overlap)
    cluster = mapper.single_linkage()
    if not is_vector_data:
        metricpar = {}
    mapper_output = mapper.mapper(data, f,
        cover=cover,
        cluster=cluster,
        point_labels= None,
        cutoff=None,
        metricpar=metricpar)
    cutoff = mapper.cutoff.first_gap(gap=0.1)
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

        G['statisticT'] = statistical_tests(G['vertices'])

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




    G = to_d3js_graph(mapper_output)
    #for i in G.keys(): print i

    with open('mapperoutput.json', 'wb') as f:
        json.dump(G, f)
    return json.dumps(G)

def statistical_tests(vertices):
    """
    Input is the vertices list, in which element contain members
    Return a list of ranked features, and p-value for t-unpaied test
    and ks-2samples test
    """

    dataIndexesList = [i['members'] for i in vertices]
    testsRes = []
    for pts in dataIndexesList:
        ansDic = {}
        if len(pts) < 10:
            print 'too small!!!!: %s' %len(pts)
            testsRes.append(len(pts))
            continue
        else:
            for col in selfvars.features:
                targetSerie = selfvars.df[col]
                inNodeArray = targetSerie.ix[targetSerie.index.isin(pts)].values
                notinNodeArray = targetSerie.ix[~targetSerie.index.isin(pts)].values
                P4ttest = stats.ttest_ind(inNodeArray, notinNodeArray)[-1]
                P4kstest = stats.ks_2samp(inNodeArray, notinNodeArray)[-1]
                ansDic[col] = [P4ttest, P4kstest, len(pts)]

            testsRes.append(ansDic)
    #print testsRes
    #print 'there r %s doable nodes'%len(testsRes)
    #print 'there r %s nodes '%len(dataIndexesList)
    return testsRes
