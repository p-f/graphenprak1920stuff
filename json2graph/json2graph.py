import argparse
import json


def json2graph(inpath, outpath, remove_atoms=[], author=None):
    vertices, edges = read_graph(inpath)
    vertices, edges = induced_subgraph(
        filter(lambda x: x[1] not in remove_atoms, vertices), edges)
    write_graph(vertices, edges, outpath, author)


def get_neighbors_of(vertices, edges, vertex):
    """
    Get the neighbors of a vertex in the form of
    (neighbor_vertex, edge_label)

    :param vertices: The vertex set of the graph.
    :param edges: The edge set of the graph.
    :param vertex: The vertex to get neighbors of.
    :return: The neighbors of the vertex and the corresponding edge label.
    """

    vid = vertex[0]
    edges_min = list(map(lambda x: (x[0], x[1]), edges))
    neighbors = filter(lambda x: ((x[0], vid) in edges_min or
                                  (vid, x[0] in edges_min)), vertices)
    res = []
    for neighbor in neighbors:
        n_id = neighbor[0]
        for connecting in [e for e in edges if
                           (e[0] == vid and e[1] == n_id) or
                           (e[0] == n_id and e[1] == vid)]:
            res += [(neighbor, connecting[2])]
    return res


def induced_subgraph(vertices, edges):
    """
    Returns an induced subgraph from a set of vertices and edges. This will
    effectively remove dangling edges.

    :param vertices: The vertex set.
    :param edges: The edge set.
    :return: The induced subgraph.
    """
    new_vertices = vertices if isinstance(vertices, list) else list(vertices)
    vertex_ids = sorted(map(lambda x: x[0], new_vertices))
    result_edges = list(filter(
        lambda x: (x[0] in vertex_ids and x[1] in vertex_ids), edges))
    return new_vertices, result_edges


def read_graph(inpath):
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
    return vertices, edges


def write_graph(nodes, edges, outpath, author=None):
    """
    Writes a graph in the format used by read_graph (as lists of tuples)
    as the custom .graph format used by the other tools in the Praktikum.

    :param nodes: The list of vertex-tuples.
    :param edges: The list of edge-tuples.
    :param outpath: The path of the output .graph file.
    :param author: The value of the author field in the output file (optional).
    :return: nothing.
    """
    outfile = open(outpath, "w")
    if author:
        outfile.write("AUTHOR: " + author + "\n")
    outfile.write("#nodes;" + str(len(nodes)) + "\n")
    outfile.write("#edges;" + str(len(edges)) + "\n")
    outfile.write("Nodes labelled;True\n")
    outfile.write("Edges labelled;True\n")
    outfile.write("Directed graph;False\n")
    outfile.write("\n")
    for vertex in nodes:
        outfile.write(";".join(vertex) + "\n")
    outfile.write("\n")
    for edge in edges:
        outfile.write(";".join(edge) + "\n")
    outfile.close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--filter-atom", help="Filtered atom types (comma "
                                                "separated)", default="")
    ap.add_argument("-i", "--input", help="Input file", required=True)
    ap.add_argument("-o", "--output", help="Output file", required=True)
    ap.add_argument("-a", "--author", help="Author", default="Egal.",
                    required=False)
    ap.add_argument("-A", "--no-author", help="Do not write the author.",
                    action="store_true")
    args = ap.parse_args()
    new_author = args.author
    if args.no_author:
        new_author = None
    json2graph(args.input, args.output, args.filter_atom.split(","), new_author)
