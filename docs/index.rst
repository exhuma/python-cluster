Welcome to python-cluster's documentation!
==========================================

Implementation of cluster algorithms in pure Python.

.. warning::

    This is currently a bug in HierarchicalClustering which causes incorrect
    output. This is currently being worked on. In the meantime
    ``HierarchicalClustering`` should be regarded as *broken*!

Example
-------

::

    from cluster import KMeansClustering
    data = [
        (8, 2),
        (7, 3),
        (2, 6),
        (3, 5),
        (3, 6),
        (1, 5),
        (8, 1),
        (3, 4),
        (8, 3),
        (9, 2),
        (2, 5),
        (9, 3)
    ]
    cl = KMeansClustering(data)
    c.getclusters(2)

The above code would give the following result::

    [
        [(8, 2), (8, 1), (8, 3), (7, 3), (9, 2), (9, 3)],
        [(3, 5), (1, 5), (3, 4), (2, 6), (2, 5), (3, 6)]
    ]

API
---

.. toctree::
   :maxdepth: 1

   apidoc/cluster
   apidoc/cluster.matrix
   apidoc/cluster.method.base
   apidoc/cluster.method.hierarchical
   apidoc/cluster.method.kmeans
   apidoc/cluster.util

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

