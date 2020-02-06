import unittest
import json2graph as j2g


class MyTestCase(unittest.TestCase):
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
        new_vertices, new_edges = j2g.induced_subgraph(vertices, edges)
        self.assertListEqual(vertices, new_vertices)
        self.assertListEqual(expected_edges, new_edges)


if __name__ == '__main__':
    unittest.main()
