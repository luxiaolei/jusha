#!encoding=utf-8
import pandas as pd
import numpy as np
from scipy import stats
from matplotlib.cm import jet
from matplotlib.colors import rgb2hex


"""
20151220_TL
this module contains pure View-Controller interaction, nothing involves the Model within, however,
worth keeping a note for Model logging the actions, as registered user later may want to come back to the same state he last time left
to be called in the "newjson" module
"""
def recolor_mapperoutput(selfvars,mapperjson):
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
    vertices = selfvars.mapperoutput['vertices']
    SeA = SelectionA#convertSelections(SelectionA)
    SeB = SelectionB#convertSelections(SelectionB)
    testsRes = []
    ranks = []
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
