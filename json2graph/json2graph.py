import argparse
import json
import os
import sys

from enum import Enum, unique

@unique
class Preprocessing(Enum):
    """
    An enum used to select preprocessing steps.
    """
    COMPRESS_CH3 = "COMPRESS_CH3"
    REMOVE_H = "REMOVE_H"

    @classmethod
    def get(cls, name: str):
        """
        Get a Preprocessing value from its name.

        :param name: The name.
        :return: The enum value
        """
        for p in Preprocessing:
            if name == p.value:
                return p
        raise Exception("Step not found: " + name)

    @classmethod
    def names(cls):
        """
        Get the names of all possible preprocessing steps.

        :return: The preprocessing step names.
        """
        return ", ".join([p.value for p in Preprocessing])

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

    def compress_ch3(self):
        """
        Find CH_3 subgraphs and replace them with a single vertex.

        :return: The graph with compressed CH_3 subgraphs.
        """
        to_remove = []
        new_vertices = []
        for vertex in self.vertices:
            if vertex[1] != "6":
                new_vertices += [vertex]
                continue
            neighbors = list(filter(lambda x: x[1] == "1",
                                    map(lambda x: x[0],
                                        self.get_neighbors_of(vertex))))
            if len(neighbors) == 3:
                to_remove += neighbors
                new_vertices += [(vertex[0], "CH3")]
            else:
                new_vertices += [vertex]
        return Graph(new_vertices, self.edges)\
            .filter_vertices(lambda x: x not in to_remove)

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

    def preprocess(self, step: Preprocessing):
        """
        Run a preprocessing step.

        :param step: The step.
        :return: The processed graph.
        """
        remove_atoms = ["1"]
        if step == Preprocessing.REMOVE_H:
            return self.filter_vertices(
                lambda x: x[1] not in remove_atoms or
                          (x[1] in remove_atoms and
                           self.have_neighbors_multibonds(x)))
        elif step == Preprocessing.COMPRESS_CH3:
            return self.compress_ch3()
        else:
            raise Exception("Unknown step: " + str(step))

    def preprocessing(self, step_names: list):
        """
        Run preprocessing steps.

        :param step_names: The steps (by name)
        :return: The graph after preprocessing.
        """
        g = self
        for step in step_names:
            g = g.preprocess(Preprocessing.get(step))
        return g

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


def json2graph(inpath: str, outpath: str, informat: str, author=None,
               preprocess = []):
    print("Converting ", inpath, "to", outpath)
    graph = Graph.read_graph(inpath, informat)
    graph.preprocessing(preprocess).write(outpath, author)


def print_banner():
    """
    Print the json2graph banner.

    :return: Nothing.
    """
    if "TERM" in os.environ and "color" in os.environ["TERM"]:
        print(r"""[38;5;93m    [38;5;99m   _[38;5;63m     [38;5;69m    [38;5;33m    [38;5;39m    _[38;5;38m__  [38;5;44m    [38;5;43m     [38;5;49m    [38;5;48m    [38;5;84m     [38;5;83m  __[38;5;119m
[38;5;93m   [38;5;99m   (_[38;5;63m)___[38;5;69m____[38;5;33m_  __[38;5;39m__ |[38;5;38m__ \[38;5;44m ____[38;5;43m ___[38;5;49m_____[38;5;48m__ _[38;5;84m____[38;5;83m  / /[38;5;119m
[38;5;93m   [38;5;99m  / [38;5;63m/ ___[38;5;69m/ __[38;5;33m \/ [38;5;39m__ \_[38;5;38m_/ /[38;5;44m/ __[38;5;43m `/ _[38;5;49m__/ [38;5;48m__ `[38;5;84m/ __ [38;5;83m\/ _[38;5;119m_ \
[38;5;93m   [38;5;99m / ([38;5;63m__  [38;5;69m) /_/[38;5;33m / /[38;5;39m / /[38;5;38m __//[38;5;44m /_/[38;5;43m / /[38;5;49m  / /[38;5;48m_/ /[38;5;84m /_/[38;5;83m / / [38;5;119m/ /
[38;5;93m _[38;5;99m_/ /[38;5;63m____/[38;5;69m\___[38;5;33m_/_/[38;5;39m /_/_[38;5;38m___/[38;5;44m\__, [38;5;43m/_/ [38;5;49m  \_[38;5;48m_,_/ [38;5;84m.___[38;5;83m/_/ [38;5;119m/_/
[38;5;93m/_[38;5;99m__/ [38;5;63m    [38;5;69m     [38;5;33m    [38;5;39m    [38;5;38m    /[38;5;44m____[38;5;43m/   [38;5;49m     [38;5;48m  /_[38;5;84m/   [38;5;83m     [38;5;119m

[0m""")
    else:
        print(r"""       _                 ___                          __
      (_)________  ____ |__ \ ____ __________ _____  / /_
     / / ___/ __ \/ __ \__/ // __ `/ ___/ __ `/ __ \/ __ \
    / (__  ) /_/ / / / / __// /_/ / /  / /_/ / /_/ / / / /
 __/ /____/\____/_/ /_/____/\__, /_/   \__,_/ .___/_/ /_/
/___/                      /____/          /_/""")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--force", help="Overwrite existing files.",
                    action="store_true")
    ap_out_selection = ap.add_mutually_exclusive_group(required=True)
    ap_out_selection.add_argument("-o", "--output", help="Output file")
    ap_out_selection.add_argument("-O", "--outpath", help="Output path")
    ap.add_argument("-l", "--format", help="Input format (json, graph, auto)",
                    default="auto")
    ap.add_argument("-a", "--author", help="Author", default="Egal.",
                    required=False)
    ap.add_argument("-A", "--no-author", help="Do not write the author.",
                    action="store_true")
    ap.add_argument("-P", "--preprocess", nargs="+", metavar="STEP",
                    help="Run a preprocessing step ("
                         + Preprocessing.names() + ")")
    ap.add_argument("input", metavar="INFILE", nargs="+", help="Input file(s)")
    print_banner()
    args = ap.parse_args()
    new_author = args.author
    if args.no_author:
        new_author = None
    filter_atoms = args.filter_atom.split(",")
    infiles = args.input
    if len(infiles) > 1 or args.outpath:
        if args.output:
            sys.stderr.write("Please use -O when converting multiple input "
                             "files\n")
            exit(1)
        assert args.outpath, "Output path not set. [-O]"
        outpath = args.outpath
        if not os.path.exists(outpath):
            sys.stderr.write("Warning: Output path does not exist\n")
            os.mkdir(outpath)
        for infile in infiles:
            next_outfile = os.path.join(outpath,
                                        os.path.basename(infile) + ".graph")
            if os.path.exists(next_outfile) and not args.force:
                sys.stderr.write("Error: File already exists: " + next_outfile
                                 + "\n")
                continue
            json2graph(infile, next_outfile, args.format,
                       new_author, args.preprocess)
    elif len(infiles) == 0:
        sys.stderr.write("Error: No input files.\n")
    elif len(infiles) == 1:
        assert args.output, "No output file given. [-o]"
        json2graph(infiles[0], args.output, args.format, new_author,
                   args.preprocess)
