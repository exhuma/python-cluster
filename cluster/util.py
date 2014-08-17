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


logger = logging.getLogger(__name__)


class ClusteringError(Exception):
    pass


def flatten(L):
    """
    Flattens a list.
    Example:
    flatten([a,b,[c,d,[e,f]]]) = [a,b,c,d,e,f]
    """
    if not isinstance(L, list):
        return [L]

    if L == []:
        return L

    return flatten(L[0]) + flatten(L[1:])


def median(numbers):
    """
    Return the median of the list of numbers.
    see: http://mail.python.org/pipermail/python-list/2004-December/294990.html
    """

    # Sort the list and take the middle element.
    n = len(numbers)
    copy = sorted(numbers)
    if n & 1:  # There is an odd number of elements
        return copy[n // 2]
    else:
        return (copy[n // 2 - 1] + copy[n // 2]) / 2.0


def mean(numbers):
    """
    Returns the arithmetic mean of a numeric list.
    see: http://mail.python.org/pipermail/python-list/2004-December/294990.html
    """
    return float(sum(numbers)) / float(len(numbers))


def minkowski_distance(x, y, p=2):
    """
    Calculates the minkowski distance between two points.

    PARAMETERS
        x - the first point
        y - the second point
        p - the order of the minkowski algorithm.
            This is equal to the euclidian distance.  If the order is 1, it is
            equal to the manhatten distance.
            The higher the order, the closer it converges to the Chebyshev
            distance, which has p=infinity. Default = 2.
    """
    from math import pow
    assert len(y) == len(x)
    assert x >= 1
    sum = 0
    for i in range(len(x)):
        sum += abs(x[i] - y[i]) ** p
    return pow(sum, 1.0 / float(p))


def genmatrix(data, combinfunc, symmetric=False, diagonal=None):
    """
    Takes a list of data and generates a 2D-matrix using the supplied
    combination function to calculate the values.

    PARAMETERS
        data        - the list of items
        combinfunc  - the function that is used to calculate teh value in a
                      cell.  It has to cope with two arguments.
        symmetric   - Whether it will be a symmetric matrix along the diagonal.
                      For example, if the list contains integers, and the
                      combination function is abs(x-y), then the matrix will
                      be symmetric.
                      Default: False
        diagonal    - The value to be put into the diagonal. For some
                      functions, the diagonal will stay constant. An example
                      could be the function "x-y". Then each diagonal cell
                      will be "0".  If this value is set to None, then the
                      diagonal will be calculated.  Default: None
    """
    logger.info("Generating matrix for %s items - O(n^2)", len(data))
    matrix = []
    for row_index, item in enumerate(data):
        logger.debug("Generating row %s", row_index)
        row = []
        for col_index, item2 in enumerate(data):
            if diagonal is not None and col_index == row_index:
                # if this is a cell on the diagonal
                row.append(diagonal)
            elif symmetric and col_index < row_index:
                # if the matrix is symmetric and we are "in the lower left
                # triangle"
                row.append(matrix[col_index][row_index])
            else:
                # if this cell is not on the diagonal
                row.append(combinfunc(item, item2))
        matrix.append(row)
    logger.info("Matrix generated")
    return matrix


def printmatrix(data):
    """
    Prints out a 2-dimensional list of data cleanly.
    This is useful for debugging.

    PARAMETERS
        data  -  the 2D-list to display
    """
    # determine maximum length
    maxlen = 0
    colcount = len(data[0])
    for col in data:
        for cell in col:
            maxlen = max(len(str(cell)), maxlen)
    # print data
    format = " %%%is |" % maxlen
    format = "|" + format * colcount
    for row in data:
        print format % tuple(row)


def magnitude(a):
    "calculates the magnitude of a vecor"
    from math import sqrt
    sum = 0
    for coord in a:
        sum += coord ** 2
    return sqrt(sum)


def dotproduct(a, b):
    "Calculates the dotproduct between two vecors"
    assert(len(a) == len(b))
    out = 0
    for i in range(len(a)):
        out += a[i] * b[i]
    return out


def centroid(data, method=median):
    "returns the central vector of a list of vectors"
    out = []
    for i in range(len(data[0])):
        out.append(method([x[i] for x in data]))
    return tuple(out)
