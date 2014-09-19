#
# This is part of "python-cluster". A library to group similar items together.
# Copyright (C) 2006    Michel Albert
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

"""
Tests for hierarchical clustering.

.. note::

    Even though the results are lists, the order of items in the resulting
    clusters is non-deterministic. This should be taken into consideration when
    writing "expected" values!
"""

from difflib import SequenceMatcher
from sys import hexversion
import unittest

from cluster import HierarchicalClustering


class Py23TestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(Py23TestCase, self).__init__(*args, **kwargs)
        if hexversion < 0x030000f0:
            self.assertCItemsEqual = self.assertItemsEqual
        else:
            self.assertCItemsEqual = self.assertCountEqual


class HClusterSmallListTestCase(Py23TestCase):
    """
    Test for Bug #1516204
    """

    def testClusterLen1(self):
        """
        Testing if hierarchical clustering a set of length 1 returns a set of
        length 1
        """
        cl = HierarchicalClustering([876], lambda x, y: abs(x - y))
        self.assertEqual([[876]], cl.getlevel(40))

    def testClusterLen0(self):
        """
        Testing if hierarchical clustering an empty list returns an empty list
        """
        cl = HierarchicalClustering([], lambda x, y: abs(x - y))
        self.assertEqual([], cl.getlevel(40))


class HClusterIntegerTestCase(Py23TestCase):

    def setUp(self):
        self.__data = [791, 956, 676, 124, 564, 84, 24, 365, 594, 940, 398,
                       971, 131, 365, 542, 336, 518, 835, 134, 391]

    def testSingleLinkage(self):
        "Basic Hierarchical Clustering test with integers"
        cl = HierarchicalClustering(self.__data, lambda x, y: abs(x - y))
        result = cl.getlevel(40)

        # sort the values to make the tests less prone to algorithm changes
        result = sorted([sorted(_) for _ in result])
        expected = sorted([
            [791],
            [676],
            [84],
            [24],
            [835],
            sorted([134, 131, 124]),
            sorted([971, 956, 940]),
            sorted([391, 398, 365, 365, 336]),
            sorted([542, 564, 518, 594])
        ])
        self.assertEqual(expected, result)

    def testCompleteLinkage(self):
        "Basic Hierarchical Clustering test with integers"
        cl = HierarchicalClustering(self.__data,
                                    lambda x, y: abs(x - y),
                                    linkage='complete')
        result = cl.getlevel(40)

        # sort the values to make the tests less prone to algorithm changes
        result = sorted([sorted(_) for _ in result])

        expected = sorted([
            [791],
            [676],
            [84],
            [24],
            [594],
            [940],
            [518],
            [835],
            sorted([391, 398]),
            sorted([134, 131, 124]),
            sorted([971, 956]),
            sorted([542, 564]),
            sorted([365, 365, 336])
        ])
        self.assertEqual(result, expected)

    def testUCLUS(self):
        "Basic Hierarchical Clustering test with integers"
        cl = HierarchicalClustering(self.__data,
                                    lambda x, y: abs(x - y),
                                    linkage='uclus')
        expected = sorted([
            [791],
            [676],
            [84],
            [24],
            [594],
            [518],
            [835],
            sorted([134, 131, 124]),
            sorted([542, 564]),
            sorted([971, 956, 940]),
            sorted([365, 365, 336, 391, 398])
        ])
        result = sorted([sorted(_) for _ in cl.getlevel(40)])
        self.assertEqual(result, expected)

    def testAverageLinkage(self):
        cl = HierarchicalClustering(self.__data,
                                    lambda x, y: abs(x - y),
                                    linkage='average')
        expected = sorted([
            [791],
            [676],
            [84],
            [24],
            [594],
            [835],
            sorted([391, 398]),
            sorted([134, 131, 124]),
            sorted([971, 956, 940]),
            sorted([365, 365, 336]),
            sorted([542, 564, 518])
        ])
        result = sorted([sorted(_) for _ in cl.getlevel(40)])
        self.assertEqual(result, expected)

    def testUnmodifiedData(self):
        cl = HierarchicalClustering(self.__data, lambda x, y: abs(x - y))
        new_data = []
        [new_data.extend(_) for _ in cl.getlevel(40)]
        self.assertEqual(sorted(new_data), sorted(self.__data))

    def testMultiprocessing(self):
        cl = HierarchicalClustering(self.__data, lambda x, y: abs(x - y),
                                    num_processes=4)
        new_data = []
        [new_data.extend(_) for _ in cl.getlevel(40)]
        self.assertEqual(sorted(new_data), sorted(self.__data))


class HClusterStringTestCase(Py23TestCase):

    def sim(self, x, y):
        sm = SequenceMatcher(lambda x: x in ". -", x, y)
        return 1 - sm.ratio()

    def setUp(self):
        self.__data = ("Lorem ipsum dolor sit amet consectetuer adipiscing "
                       "elit Ut elit Phasellus consequat ultricies mi Sed "
                       "congue leo at neque Nullam").split()

    def testDataTypes(self):
        "Test for bug #?"
        cl = HierarchicalClustering(self.__data, self.sim)
        for item in cl.getlevel(0.5):
            self.assertEqual(
                type(item), type([]),
                "Every item should be a list!")

    def testCluster(self):
        """
        Using the threshold value 0.5 with single distance puts us into a
        situation where the algorithm might stop too soon as there are a few
        consecutive steps towards a cluster with a level higher than 0.5!

        This test ensures that it runs as far as required.
        """
        # XXX self.skipTest('These values lead to non-deterministic results. '
        # XXX               'This makes it untestable!')
        cl = HierarchicalClustering(self.__data, self.sim, linkage="single")

        result = sorted([sorted(_) for _ in cl.getlevel(0.5)])
        expected = sorted([
            ['Lorem'],
            ['ipsum'],
            ['adipiscing'],
            ['Phasellus'],
            ['ultricies'],
            ['mi'],
            ['Sed'],
            ['Nullam'],
            sorted(['elit', 'elit', 'sit']),
            sorted(['consequat', 'consectetuer', 'neque', 'congue']),
            sorted(['leo', 'dolor']),
            sorted(['at', 'amet', 'Ut']),
        ])
        self.assertEqual(result, expected)

    def testUnmodifiedData(self):
        cl = HierarchicalClustering(self.__data, self.sim)
        new_data = []
        [new_data.extend(_) for _ in cl.getlevel(0.5)]
        self.assertEqual(sorted(new_data), sorted(self.__data))


if __name__ == '__main__':
    suite = unittest.TestSuite((
        unittest.makeSuite(HClusterIntegerTestCase),
        unittest.makeSuite(HClusterSmallListTestCase),
        unittest.makeSuite(HClusterStringTestCase),
    ))

    unittest.TextTestRunner(verbosity=2).run(suite)
