Fixing my old Clustering Library
================================

The following example steps through the process of using the hierarchical
clustering algorithm. This example is also used in unit-tests of a library I
wrote a while back. Back then, I did not quite grasp the ideas behind the
algorithm. Which surprises me as the algorithm is quite straigh-forward.
Nevertheless, due to my lack of understaning, the tests I wrote that time were
incorrect. Which led to an error in the algorithm output.

When getting back to the code, I saw other issues, and will address those as
well, but for this article, I will prepare a simple test scenario, which will
server as basis for the new tests, and new code.

We will start of with a sample of non primitive data types. In this case points
on a two-dimensional plane. As distance function we will use the euclidian
distance. And, for the first step through, we will use single linkage between
clusters. The same scenario will be played through with complete- and
uclus-linkage later on. As overall method, we will use a bottom-up approach.

We will start with the following data:

:image hcluster-single-a.png:

So we have the following points::

    a (1, 1)
    b (9, 1)
    c (2, 2)
    d (3, 2)
    e (9, 2)
    f (3, 4)


.. note::

    To keep the matrix table more readable, individual points are written in
    lower-case, while clusters are written in upper-case!


This results in the following initial distance matrix. We will mark the
diagonal with an ``x`` as we're not interested in comparing a point with
itself.  Equally, we are only interested in the absolute distance. So we only
need the values for pairs on ons side of the diagonal.


 ===== ===== ====== ====== ====== ====== ======
         a     b      c      d      e      f
   a     x    8.00   1.41   2.24   8.06   3.61
   b           x     7.07   6.08   1.00   6.71
   c                  x     1.00   7.00   2.24
   d                         x     6.00   2.00
   e                                x     6.32
   f                                       x
 ===== ===== ====== ====== ====== ====== ======


 With this matrix, we see that the first candidates are ``[b, e]`` and ``[c,
 d]``. We'll pick ``[b, e]`` as firt cluster (``A``)::

    a (1, 1)
    A (9, 1), (9, 2) level=1.00
    c (2, 2)
    d (3, 2)
    f (3, 4)

 ===== ===== ====== ====== ====== ======
         a     A      c      d      f
   a     x    8.00   1.41   2.24   3.61
   A           x     7.00   6.00   6.32
   c                  x     1.00   2.24
   d                         x     2.00
   f                                x
 ===== ===== ====== ====== ====== ======


Single Linkage
--------------

The next candidate is ``[c, d]`` as ``B``::

    a (1, 1)
    A (9, 1), (9, 2) level=1.00
    B (2, 2), (3, 2) level=1.00
    f (3, 4)

 ===== ===== ====== ====== ======
         a     A      B      f
   a     x    8.00   1.41   3.61
   A           x     6.00   6.32
   B                  x     2.00
   f                         x
 ===== ===== ====== ====== ======

Then ``[f, B]`` as ``C``::

    a (1, 1)
    A (9, 1), (9, 2) level=1.00
    C (3, 4), ((2, 2), (3, 2) level=1.00) level=2.00

 ===== ===== ====== ======
         a     A      C
   a     x    8.00   1.41
   A           x     6.00
   C                  x
 ===== ===== ====== ======


Then ``[a, C]`` as ``D``::

    A (9, 1), (9, 2) level=1.00
    D (1, 1), ((3, 4), ((2, 2), (3, 2) level=1.00) level=2.00) level=1.41

 ===== ====== ======
         A      D
   A     x     6.00
   D            x
 ===== ====== ======

Which gives us the final cluster ``E`` with a level of ``6.00``.

The end-result is the following dendogram::

                       E
                       |
           +-----------+-----------+
           |                       |
           |                       D
           |                       |
           |                 +-----+-----+
           |                 |           |
           |                 C           |
           |                 |           |
           |            +----+----+      |
           |            |         |      |
           A            B         |      |
           |            |         |      |
        +--+--+      +--+--+      |      |
        |     |      |     |      |      |
        e     b      c     d      f      a



Complete Linkage
----------------

Initial distance matrix for reference:

 ===== ===== ====== ====== ====== ====== ======
         a     b      c      d      e      f
   a     x    8.00   1.41   2.24   8.06   3.61
   b           x     7.07   6.08   1.00   6.71
   c                  x     1.00   7.00   2.24
   d                         x     6.00   2.00
   e                                x     6.32
   f                                       x
 ===== ===== ====== ====== ====== ====== ======

First iteration is identical, but distance matrix has different values. The
subsequent steps will be displayed without aditional explanation, the idea is
the same as above, simply using a different linkage function.

 ===== ===== ====== ====== ====== ======
         a     A      c      d      f
   a     x    8.06   1.41   2.24   3.61
   A           x     7.07   6.08   6.71
   c                  x     1.00   2.24
   d                         x     2.00
   f                                x
 ===== ===== ====== ====== ====== ======


 ===== ===== ====== ====== ======
         a     A      B      f
   a     x    8.06   2.24   3.61
   A           x     7.07   6.71
   B                  x     2.24
   f                         x
 ===== ===== ====== ====== ======

.. note::
    We now have to make a choice. I have not yet decided on how to handle this
    situation to have a detereministic behaviour. My current train of thought
    is using python ``sets`` as data-structure which is unordered. So the
    algorithm could return either one here. I'll turn to a matematician to get
    some better information.

    For a demonstration, we'll pick ``[Ba]`` as to have a different result from
    sinle linkage...

This will give us:

 ===== ===== ====== ======
         C     A      f
   C     x    8.06   3.61
   A           x     6.71
   f                  x
 ===== ===== ====== ======

And finally

 ===== ===== ======
         D     A
   D     x    8.06
   A           x
 ===== ===== ======
