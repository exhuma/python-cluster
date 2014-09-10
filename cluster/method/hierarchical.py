#
# This is part of "python-cluster". A library to group similar items together.
# Copyright (C) 2006    Michel Albert
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
# for more details.
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

import logging

from cluster.cluster import Cluster
from cluster.matrix import Matrix
from cluster.method.base import BaseClusterMethod
from cluster.util import median, mean


logger = logging.getLogger(__name__)


class HierarchicalClustering(BaseClusterMethod):
    """
    Implementation of the hierarchical clustering method as explained in a
    tutorial_ by *matteucc*.

    .. _tutorial: http://www.elet.polimi.it/upload/matteucc/Clustering/tutorial_html/hierarchical.html

    Example:

        >>> from cluster import HierarchicalClustering
        >>> # or: from cluster import *
        >>> cl = HierarchicalClustering([123,334,345,242,234,1,3],
                lambda x,y: float(abs(x-y)))
        >>> cl.getlevel(90)
        [[345, 334], [234, 242], [123], [3, 1]]

    Note that all of the returned clusters are more than 90 (``getlevel(90)``)
    apart.

    See :py:class:`~cluster.method.base.BaseClusterMethod` for more details.

    :param linkage: The method used to determine the distance between two
        clusters. See :py:meth:`~.HierarchicalClustering.set_linkage_method` for
        the available methods.
    :param num_processes: If you want to use multiprocessing to split up the
        work and run ``genmatrix()`` in parallel, specify num_processes > 1 and
        this number of workers will be spun up, the work split up amongst them
        evenly.
    """

    def __init__(self, data, distance_function, linkage=None, num_processes=1):
        if not linkage:
            linkage = 'single'
        logger.info("Initializing HierarchicalClustering object with linkage "
                    "method %s", linkage)
        BaseClusterMethod.__init__(self, sorted(data), distance_function)
        self.set_linkage_method(linkage)
        self.num_processes = num_processes
        self.__cluster_created = False

    def set_linkage_method(self, method):
        """
        Sets the method to determine the distance between two clusters.

        :param method: The name of the method to use. It must be one of
            ``'single'``, ``'complete'``, ``'average'`` or ``'uclus'``.
        """
        if method == 'single':
            self.linkage = self.single_linkage_distance
        elif method == 'complete':
            self.linkage = self.complete_linkage_distance
        elif method == 'average':
            self.linkage = self.average_linkage_distance
        elif method == 'uclus':
            self.linkage = self.uclus_distance
        else:
            raise ValueError('distance method must be one of single, '
                             'complete, average of uclus')

    def uclus_distance(self, x, y):
        """
        The method to determine the distance between one cluster an another
        item/cluster. The distance equals to the *average* (median) distance
        from any member of one cluster to any member of the other cluster.

        :param x: first cluster/item.
        :param y: second cluster/item.
        """
        # create a flat list of all the items in <x>
        if not isinstance(x, Cluster):
            x = [x]
        else:
            x = x.fullyflatten()

        # create a flat list of all the items in <y>
        if not isinstance(y, Cluster):
            y = [y]
        else:
            y = y.fullyflatten()

        distances = []
        for k in x:
            for l in y:
                distances.append(self.distance(k, l))
        return median(distances)

    def average_linkage_distance(self, x, y):
        """
        The method to determine the distance between one cluster an another
        item/cluster. The distance equals to the *average* (mean) distance
        from any member of one cluster to any member of the other cluster.

        :param x: first cluster/item.
        :param y: second cluster/item.
        """
        # create a flat list of all the items in <x>
        if not isinstance(x, Cluster):
            x = [x]
        else:
            x = x.fullyflatten()

        # create a flat list of all the items in <y>
        if not isinstance(y, Cluster):
            y = [y]
        else:
            y = y.fullyflatten()

        distances = []
        for k in x:
            for l in y:
                distances.append(self.distance(k, l))
        return mean(distances)

    def complete_linkage_distance(self, x, y):
        """
        The method to determine the distance between one cluster an another
        item/cluster. The distance equals to the *longest* distance from any
        member of one cluster to any member of the other cluster.

        :param x: first cluster/item.
        :param y: second cluster/item.
        """

        # create a flat list of all the items in <x>
        if not isinstance(x, Cluster):
            x = [x]
        else:
            x = x.fullyflatten()

        # create a flat list of all the items in <y>
        if not isinstance(y, Cluster):
            y = [y]
        else:
            y = y.fullyflatten()

        # retrieve the minimum distance (single-linkage)
        maxdist = self.distance(x[0], y[0])
        for k in x:
            for l in y:
                maxdist = max(maxdist, self.distance(k, l))

        return maxdist

    def single_linkage_distance(self, x, y):
        """
        The method to determine the distance between one cluster an another
        item/cluster. The distance equals to the *shortest* distance from any
        member of one cluster to any member of the other cluster.

        :param x: first cluster/item.
        :param y: second cluster/item.
        """

        # create a flat list of all the items in <x>
        if not isinstance(x, Cluster):
            x = [x]
        else:
            x = x.fullyflatten()

        # create a flat list of all the items in <y>
        if not isinstance(y, Cluster):
            y = [y]
        else:
            y = y.fullyflatten()

        # retrieve the minimum distance (single-linkage)
        mindist = self.distance(x[0], y[0])
        for k in x:
            for l in y:
                mindist = min(mindist, self.distance(k, l))

        return mindist

    def cluster(self, matrix=None, level=None, sequence=None):
        """
        Perform hierarchical clustering.

        :param matrix: The 2D list that is currently under processing. The
            matrix contains the distances of each item with each other
        :param level: The current level of clustering
        :param sequence: The sequence number of the clustering
        """
        logger.info("Performing cluster()")

        if matrix is None:
            # create level 0, first iteration (sequence)
            level = 0
            sequence = 0
            matrix = []

        # if the matrix only has two rows left, we are done
        while len(matrix) > 2 or matrix == []:

            item_item_matrix = Matrix(self._data,
                                      self.linkage,
                                      True,
                                      0)
            item_item_matrix.genmatrix(self.num_processes)
            matrix = item_item_matrix.matrix

            smallestpair = None
            mindistance = None
            rowindex = 0  # keep track of where we are in the matrix
            # find the minimum distance
            for row in matrix:
                cellindex = 0  # keep track of where we are in the matrix
                for cell in row:
                    # if we are not on the diagonal (which is always 0)
                    # and if this cell represents a new minimum...
                    cell_lt_mdist = cell < mindistance if mindistance else False
                    if ((rowindex != cellindex) and
                            (cell_lt_mdist or smallestpair is None)):
                        smallestpair = (rowindex, cellindex)
                        mindistance = cell
                    cellindex += 1
                rowindex += 1

            sequence += 1
            level = matrix[smallestpair[1]][smallestpair[0]]
            cluster = Cluster(level, self._data[smallestpair[0]],
                              self._data[smallestpair[1]])

            # maintain the data, by combining the the two most similar items
            # in the list we use the min and max functions to ensure the
            # integrity of the data.  imagine: if we first remove the item
            # with the smaller index, all the rest of the items shift down by
            # one. So the next index will be wrong. We could simply adjust the
            # value of the second "remove" call, but we don't know the order
            # in which they come. The max and min approach clarifies that
            self._data.remove(self._data[max(smallestpair[0],
                                             smallestpair[1])])  # remove item 1
            self._data.remove(self._data[min(smallestpair[0],
                                             smallestpair[1])])  # remove item 2
            self._data.append(cluster)  # append item 1 and 2 combined

        # all the data is in one single cluster. We return that and stop
        self.__cluster_created = True
        logger.info("Call to cluster() is complete")
        return

    def getlevel(self, threshold):
        """
        Returns all clusters with a maximum distance of *threshold* in between
        each other

        :param threshold: the maximum distance between clusters.

        See :py:meth:`~cluster.cluster.Cluster.getlevel`
        """

        # if it's not worth clustering, just return the data
        if len(self._input) <= 1:
            return self._input

        # initialize the cluster if not yet done
        if not self.__cluster_created:
            self.cluster()

        return self._data[0].getlevel(threshold)
