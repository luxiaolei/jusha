from flask import redirect, request, render_template, url_for, session, g
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
import json

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])


class selfgloablvars:
    def __init__(self):
        self.features = 1
        self.df = 1
        self.selected_feature = 1
        self.mappernew = 1

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


@app.route('/', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        try:
        #file uploading
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


                col = df.columns.values

                #store the col into selfvars obj
                selfvars.features = col
                selfvars.df = df

                return render_template('index.html', \
                message = message,  columns= col, submitflag= True)
            else:
                message = 'Failed upload! File type is not supported!'
                return render_template('index.html', message = message)
        except Exception:
            try:
                #feature selection
                selected_f = request.form['option']
                selfvars.selected_feature = selected_f

                data = selfvars.df[selected_f]
                minvalue = data.min()
                maxvalue = data.max()

                with open('mapperoutput.json', 'rb') as f:
                    mapperoutput = json.load(f)

                recolor_mapperoutput(mapperoutput)

                return render_template('index.html', columns= selfvars.features,\
                        submitflag=True, featureflag= True, selected_f= selfvars.selected_feature,\
                        minvalue= minvalue,\
                        maxvalue = maxvalue)
            except Exception:
                try:

                    inputrange = request.form['range']
                    inputrange = [float(i) for i in inputrange.split(',')]


                    df = selfvars.df
                    sf = selfvars.selected_feature
                    rangeindex = df.ix[(df[sf] >= inputrange[0]) & (df[sf] <= inputrange[-1])].index.values
                    """
                    with open('mapperoutput.json', 'rb') as f:
                        mapperoutput = json.load(f)

                    recolor_mapperoutput(mapperoutput)
                    """


                    return render_template('index.html', columns= selfvars.features,\
                            submitflag=True, featureflag= True, selected_f= selfvars.selected_feature,\
                            inputrange = inputrange, rangeindex = rangeindex)
                    #feture range selection
                    pass
                except Exception, e:
                    return render_template('index.html', error = str(e))
                    pass
    else: return render_template('index.html')


@app.route('/mapperjson')
def mapper_cluster():
    #in_file_dir = '/Users/xl-macbook/documents/project/flask/mapper_web/upload'
    in_file = [f for f in os.listdir('uploads/')]
    assert len(in_file) > 0

    in_file = 'uploads/' + session['filename']

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
    cover = mapper.cover.cube_cover_primitive(intervals=8, overlap=50.0)
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

    if selfvars.mappernew == 1:
        #first time initiate the graph
        G = to_d3js_graph(mapper_output)
        with open('mapperoutput.json', 'wb') as f:
            json.dump(G, f)
    else:
        G = selfvars.mappernew
    return json.dumps(G)
