import unittest
import json2graph as j2g


class MyTestCase(unittest.TestCase):
    def test_get_neighbors_of(self):
        """
        Test case for the get_neighbors_of method.

        :return: Nothing.
        """
        center = ("center", "a")
        in1 = ("in", "b")
        out1 = ("out1", "c")
        out2 = ("out2", "d")
        vertices = [
            center, in1, out1, out2,
            ("other", "e")
        ]
        edges = [
            ("in", "center", "cin"),
            ("center", "out1", "cout1"),
            ("center", "out2", "cout2"),
            ("out1", "other", "etc")
        ]
        expected = [
            (in1, "cin"),
            (out1, "cout1"),
            (out2, "cout2")
        ]
        neighbors = j2g.Graph(vertices, edges).get_neighbors_of(center)
        self.assertListEqual(expected, neighbors)


    def test_induced_subgraph(self):
        """
        Test case for the induced_subgraph method.

        :return: Nothing.
        """
        vertices = [
            ("1", "a"),
            ("2", "b")
        ]
        edges = [
            ("1", "2", "a"),
            ("1", "3", "b"),
            ("4", "2", "c"),
            ("3", "4", "d")
        ]
        expected_edges = [
            ("1", "2", "a")
        ]
        subgraph = j2g.Graph(vertices, edges).induced_subgraph()
        self.assertListEqual(vertices, subgraph.vertices)
        self.assertListEqual(expected_edges, subgraph.edges)

    def test_compress_ch3(self):
        """
        Test case for the compress_ch3 method.

        :return: Nothing.
        """
        vertices = [
            ("c_1", "6"),
            ("c_1_h1", "1"),
            ("c_1_h2", "1"),
            ("c_1_h3", "1"),
            ("c_2", "6"),
            ("c_2_h1", "1"),
            ("c_2_h2", "1"),
            ("etc", "7")
        ]
        edges = [
            ("c_1_h1", "c_1", ""),
            ("c_1", "c_1_h2", ""),
            ("c_1", "c_1_h3", ""),
            ("c_1", "c_2", ""),
            ("c_2_h1", "c_2", ""),
            ("c_2", "c_2_h2", ""),
            ("c_2", "etc", "")
        ]
        expected_vertices = [
            ("c_1", "CH3"),
            ("c_2", "6"),
            ("c_2_h1", "1"),
            ("c_2_h2", "1"),
            ("etc", "7")
        ]
        expected_edges = [
            ("c_1", "c_2", ""),
            ("c_2_h1", "c_2", ""),
            ("c_2", "c_2_h2", ""),
            ("c_2", "etc", "")
        ]
        res = j2g.Graph(vertices, edges).compress_ch3()
        self.assertListEqual(expected_vertices, res.vertices)
        self.assertListEqual(expected_edges, res.edges)


if __name__ == '__main__':
    unittest.main()
