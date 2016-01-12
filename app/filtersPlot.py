from mapper import filters
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from sklearn.cluster import KMeans,AffinityPropagation,MeanShift,SpectralClustering,DBSCAN

__all__ = ['eccentricity', 'Gauss_density', 'kNN_distance',
           'distance_to_measure', 'graph_Laplacian', 'dm_eigenvector',
           'zero_filter']

metric = ["euclidean", "minkowski", "cityblock", "seuclidean",
            "sqeuclidean", "cosine", "correlation"]

filterFuncs = {'eccentricity': filters.eccentricity ,
          'Gauss_density': filters.Gauss_density,
          'kNN_distance': filters.kNN_distance,
          'distance_to_measure': filters.distance_to_measure,
          'graph_Laplacian': filters.graph_Laplacian,
          'dm_eigenvector' : filters.dm_eigenvector,
          'zero_filter': filters.zero_filter}



fileUrl ='wineQuality.csv'#'irisFlower.csv'#input_boston_wPrice.csv'#'irisFlower.csv'#'circle.csv'

data = pd.read_csv(fileUrl).values



metricpar = {'metric': metric[0]}

ecc = filterFuncs['eccentricity'](data, metricpar= metricpar)
gaus = filterFuncs['Gauss_density'](data, sigma= 1.0, metricpar= metricpar)
knn = filterFuncs['kNN_distance'](data, k=2, metricpar= metricpar)
d2m = filterFuncs['distance_to_measure'](data, k=2, metricpar= metricpar)
pca = filterFuncs['dm_eigenvector'](data, metricpar= metricpar)

y = [1]*len(ecc)
bins = 150

f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, sharex=False, sharey=False)
#ax1.scatter(ecc, y, s= 8, marker='|')
ax1.hist(ecc, bins)
ax1.set_title('eccentricity_%s'%fileUrl)

#ax2.scatter(gaus, y,s= 8, marker='|')
ax2.hist(gaus, bins)
ax2.set_title('Gauss_density')

#ax3.scatter(knn, y,s= 8, marker='|')
ax3.hist(knn, bins)
ax3.set_title('kNN_distance')

#ax4.scatter(pca, y,s= 8, marker='|')
ax4.hist(pca, bins)
ax4.set_title('PCA')

f.subplots_adjust(wspace=0.05, left= .02, right=.98, bottom= .04, top=.97)

#plt.show()


from mapper.cover import cube_cover_primitive

intervals, overlap = 10, 25

cover = cube_cover_primitive(intervals=intervals, overlap=overlap)




