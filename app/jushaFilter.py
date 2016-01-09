import numpy as np
from sklearn import svm
import pandas as pdb

def svmFilter(data,kernel='rbf', metricpar={}):
    if data.ndim == 1:
        pass

    else:
        clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
        clf.fit(data)
        dis2hyperplane = clf.decision_function(data).T[0]
    return dis2hyperplane


def selfdefined(data, metricpar):
    print selfvars.df.ix[:,-1].values.dtype
    return selfvars.df1.ix[:,-1].values
