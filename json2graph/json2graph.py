import argparse
import json

from enum import Enum


class Graph:
    """
    A graph storing lists of labeled vertices and edges
    """

    def __init__(self):
        """
        Create a new empty graph
        """
        self.vertices = []
        self.edges = []

    def __init__(self, vertices, edges):
        """
        Create a new graph from lists of vertices and edges.

        :param vertices: A list of vertices.
        :param edges: A list of edges.
        """
        self.vertices = vertices
        self.edges = edges

    def have_neighbors_multibonds(self, vertex):
        """
        Calculate whether any neighbor of a vertex has multibonds 
        and return True in this case.
        
        :param vertex: The vertex to get neighbors of and search mfor multibonds
        :return: True if any neighbor has at least 1 multibond, False otherwise.
        """
        neighbors = list(self.get_neighbors_of(vertex))
        for neighbor in neighbors:
            nneighbors = list(self.get_neighbors_of(neighbor[0]))
            for nneighbor in nneighbors:
                if nneighbor[1] != "1":
                    return True
        return False

    def get_neighbors_of(self, vertex):
        """
        Get the neighbors of a vertex in the form of
        (neighbor_vertex, edge_label)

        :param vertex: The vertex to get neighbors of.
        :return: The neighbors of the vertex and the corresponding edge label.
        """
        vid = vertex[0]
        edges_min = list(map(lambda x: (x[0], x[1]), self.edges))
        neighbors = filter(lambda x: ((x[0], vid) in edges_min or
                                      (vid, x[0] in edges_min)), self.vertices)
        res = []
        for neighbor in neighbors:
            n_id = neighbor[0]
            for connecting in [e for e in self.edges if
                               (e[0] == vid and e[1] == n_id) or
                               (e[0] == n_id and e[1] == vid)]:
                res += [(neighbor, connecting[2])]
        return res

    def filter_vertices(self, vertex_filter):
        """
        Apply a filter to the list of vertices.

        :param vertex_filter: The vertex filter.
        :return: The subgraph.
        """
        self.vertices = list(filter(vertex_filter, self.vertices))
        return self.induced_subgraph()

    def induced_subgraph(self):
        """
        Returns an induced subgraph from a set of vertices and edges. This will
        effectively remove dangling edges.

        :param vertices: The vertex set.
        :param edges: The edge set.
        :return: The induced subgraph.
        """
        vertex_ids = sorted(map(lambda x: x[0], self.vertices))
        result_edges = list(filter(
            lambda x: (x[0] in vertex_ids and x[1] in vertex_ids), self.edges))
        self.edges = result_edges
        return self

    def write(self, outpath, author=None):
        """
        Writes the graph in the format used by read_graph (as lists of tuples)
        as the custom .graph format used by the other tools in the Praktikum.

        :param outpath: The path of the output .graph file.
        :param author: The value of the author field in the output file
        (optional).
        """
        vertex_count = str(len(self.vertices))
        edges_count = str(len(self.edges))
        print("Writing ", outpath, " with ", vertex_count, " vertices and ",
              edges_count, " edges.")
        outfile = open(outpath, "w")
        if author:
            outfile.write("AUTHOR: " + author + "\n")
        outfile.write("#nodes;" + vertex_count + "\n")
        outfile.write("#edges;" + edges_count + "\n")
        outfile.write("Nodes labelled;True\n")
        outfile.write("Edges labelled;True\n")
        outfile.write("Directed graph;False\n")
        outfile.write("\n")
        for vertex in self.vertices:
            outfile.write(";".join(vertex) + "\n")
        outfile.write("\n")
        for edge in self.edges:
            outfile.write(";".join(edge) + "\n")
        outfile.close()

    @classmethod
    def read_graph(cls, in_path: str, in_format="auto"):
        """
        Read a graph in either json or .graph format.

        :param in_path: The input path.
        :param in_format: The input format (or auto).
        :return: A new graph read from the file
        """
        if (in_format == "auto" and in_path.endswith("json"))\
                or in_format == "json":
            return Graph.read_graph_json(in_path)
        elif (in_format == "auto" and in_path.endswith("graph")) \
                or in_format == "graph":
            return Graph.read_graph_graph(in_path)
        else:
            raise Exception("Unknown format " + in_format + " or format not "
                                                            "detected.")

    @classmethod
    def read_graph_graph(cls, in_path):
        """
        Read a graph from a .graph file.

        :param in_path: The input path.
        :return: The parsed graph.
        """
        infile = open(in_path, "r")
        vertices = []
        edges = []
        author = None
        vertex_count = None
        edge_count = None
        line: str = infile.readline()
        state = 1
        while line:
            line = line.rstrip()
            if state == 1:
                # Header
                if line.startswith("//"):
                    pass
                elif line.startswith("AUTHOR:"):
                    author = line[7:]
                elif line.startswith("#nodes;"):
                    vertex_count = line.split(";")[1]
                elif line.startswith("#edges;"):
                    edge_count = line.split(";")[1]
                elif line.startswith("Nodes labelled;"):
                    if not bool(line.split(";")[1]):
                        raise Exception("Unlabelled nodes are not supported")
                elif line.startswith("Edges labelled;"):
                    if not bool(line.split()):
                        raise Exception("Unlabelled edges are not supported")
                elif line.startswith("Directed graph"):
                    pass
                elif line == "":
                    state = 2
                else:
                    raise Exception("Unrecognized line: " + line)
            if state == 2:
                # Validify header
                assert vertex_count, "Vertex count not set"
                assert edge_count, "Edge count not set"
                state = 3
            elif state == 3:
                # Vertices
                if line == "":
                    state = 4
                else:
                    data = line.split(";")
                    if len(data) != 2:
                        raise Exception("Failed to parse vertex: " + line)
                    vertices += [(data[0], data[1])]
            elif state == 4:
                # Edges
                data = line.split(";")
                if len(data) != 3:
                    raise Exception("Failed to parse edge: " + line)
                else:
                    edges += [(data[0], data[1], data[2])]
            line = infile.readline()
        infile.close()
        return Graph(vertices, edges)

    @classmethod
    def read_graph_json(cls, inpath):
        """
        Read a graph from a file in JSON format. This lists of vertices and edges
        as tuples. Vertices are encoded as tuples of (id, label) and edges as
        tuples of (source_id, target_id, label).

        :param inpath: The JSON file input path.
        :return: A graph as tuple of vertex- and edge-list.
        """
        file = open(inpath, "r")
        parsed = json.load(file)
        file.close()
        compound = parsed["PC_Compounds"][0]["atoms"]
        bonds = parsed["PC_Compounds"][0]["bonds"]
        nr_of_atoms = len(compound["aid"])
        nr_of_bonds = len(bonds["aid1"])
        vertices = []
        edges = []
        for atom in range(nr_of_atoms):
            atom_type = str(compound["element"][atom])
            atom_id = str(compound["aid"][atom])
            vertices += [(atom_id, atom_type)]
        for bond in range(nr_of_bonds):
            source_id = str(bonds["aid1"][bond])
            target_id = str(bonds["aid2"][bond])
            edges += [(source_id, target_id, str(bonds["order"][bond]))]
        return Graph(vertices, edges)


def json2graph(inpath: str, outpath: str, informat: str,
               remove_atoms=[], author=None):
    graph = Graph.read_graph(inpath, informat)
    graph.filter_vertices(lambda x: x[1] not in remove_atoms or (x[1] in remove_atoms and graph.have_neighbors_multibonds(x))) \
        .write(outpath, author)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--filter-atom", help="Filtered atom types (comma "
                                                "separated)", default="")
    ap.add_argument("-i", "--input", help="Input file", required=True)
    ap.add_argument("-o", "--output", help="Output file", required=True)
    ap.add_argument("-l", "--format", help="Input format (json, graph, auto)",
                    default="auto")
    ap.add_argument("-a", "--author", help="Author", default="Egal.",
                    required=False)
    ap.add_argument("-A", "--no-author", help="Do not write the author.",
                    action="store_true")
    args = ap.parse_args()
    new_author = args.author
    if args.no_author:
        new_author = None
    filter_atoms = args.filter_atom.split(",")
    json2graph(args.input, args.output, args.format, filter_atoms, new_author)
