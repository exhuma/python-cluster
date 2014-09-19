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

from functools import partial
import logging

from cluster.cluster import Cluster
from cluster.method.base import BaseClusterMethod
from cluster.linkage import single, complete, average, uclus


logger = logging.getLogger(__name__)


class HierarchicalClustering(BaseClusterMethod):
    """
    Implementation of the hierarchical clustering method as explained in a
    tutorial_ by *matteucc*.

    Object prerequisites:

    * Items must be sortable (See `issue #11`_)
    * Items must be hashable.

    .. _issue #11: https://github.com/exhuma/python-cluster/issues/11
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

    :param data: The collection of items to be clustered.
    :param distance_function: A function which takes two elements of ``data``
        and returns a distance between both elements.
    :param linkage: The method used to determine the distance between two
        clusters. See :py:meth:`~.HierarchicalClustering.set_linkage_method` for
        possible values.
    :param num_processes: If you want to use multiprocessing to split up the
        work and run ``genmatrix()`` in parallel, specify num_processes > 1 and
        this number of workers will be spun up, the work split up amongst them
        evenly.
    :param progress_callback: A function to be called on each iteration to
        publish the progress. The function is called with two integer arguments
        which represent the total number of elements in the cluster, and the
        remaining elements to be clustered.
    """

    def __init__(self, data, distance_function, linkage=None, num_processes=1,
                 progress_callback=None):
        if not linkage:
            linkage = single
        logger.info("Initializing HierarchicalClustering object with linkage "
                    "method %s", linkage)
        BaseClusterMethod.__init__(self, sorted(data), distance_function)
        self.set_linkage_method(linkage)
        self.num_processes = num_processes
        self.progress_callback = progress_callback
        self.__cluster_created = False

    def publish_progress(self, total, current):
        """
        If a progress function was supplied, this will call that function with
        the total number of elements, and the remaining number of elements.

        :param total: The total number of elements.
        :param remaining: The remaining number of elements.
        """
        if self.progress_callback:
            self.progress_callback(total, current)

    def set_linkage_method(self, method):
        """
        Sets the method to determine the distance between two clusters.

        :param method: The method to use. It can be one of ``'single'``,
            ``'complete'``, ``'average'`` or ``'uclus'``, or a callable. The
            callable should take two collections as parameters and return a
            distance value between both collections.
        """
        if method == 'single':
            self.linkage = min
        elif method == 'complete':
            self.linkage = max
        elif method == 'average':
            self.linkage = mean
        elif method == 'uclus':
            self.linkage = median
        elif hasattr(method, '__call__'):
            self.linkage = method
        else:
            raise ValueError('distance method must be one of single, '
                             'complete, average of uclus')

    def __similarity(self, simfunc, a, b):
        return self.linkage([simfunc(x, y) for x in a for y in b])

    def __reconstruct(self, cluster_indices):
        if not cluster_indices:
            return []
        return [[self._input[i] for i in _] for _ in cluster_indices]

    def run(self, threshold):
        indices = [[_] for _ in range(len(self._input))]
        lookbehind = None
        minimum = 0
        while len(indices) > 1:
            minimum = None
            min_pair = None
            permutations = ((a, b)
                            for i, a in enumerate(indices)
                            for b in indices[:i])
            for x, y in permutations:
                sim = self.__similarity(
                    self.distance,
                    [self._input[_] for _ in x],
                    [self._input[_] for _ in y])
                if minimum is None or sim < minimum:
                    minimum = sim
                    min_pair = (x, y)
                if minimum == 0:
                    break
            if minimum > threshold:
                # we've come too far. Undo the last operation
                if lookbehind:
                    indices.pop()
                    indices.extend(lookbehind)
                return indices, minimum
            lookbehind = min_pair
            indices.append(min_pair[0] + min_pair[1])
            indices.remove(min_pair[0])
            indices.remove(min_pair[1])
        return indices, minimum

    def cluster(self):
        pass

    def getlevel(self, threshold):
        cluster, level = self.run(threshold)
        return self.__reconstruct(cluster)
