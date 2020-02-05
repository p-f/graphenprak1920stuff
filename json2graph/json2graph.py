import argparse
import json


def json2graph(inpath, outpath, remove_atoms=[]):
    file = open(inpath, "r")
    parsed = json.load(file)
    file.close()
    compound = parsed["PC_Compounds"][0]["atoms"]
    bonds = parsed["PC_Compounds"][0]["bonds"]
    nr_of_atoms = len(compound["aid"])
    nr_of_bonds = len(bonds["aid1"])
    removed_atom_ids = []
    vertices = []
    edges = []
    for atom in range(nr_of_atoms):
        atom_type = str(compound["element"][atom])
        atom_id = str(compound["aid"][atom])
        if atom_type in remove_atoms:
            removed_atom_ids += [atom_id]
            continue
        vertices += [(atom_id, atom_type)]
    for bond in range(nr_of_bonds):
        source_id = str(bonds["aid1"][bond])
        target_id = str(bonds["aid2"][bond])
        if source_id in removed_atom_ids or target_id in removed_atom_ids:
            continue
        edges += [(source_id, target_id, str(bonds["order"][bond]))]
    outfile = open(outpath, "w")
    outfile.write("AUTHOR: Egal.\n")
    outfile.write("#nodes;" + str(len(vertices)) + "\n")
    outfile.write("#edges;" + str(len(edges)) + "\n")
    outfile.write("Nodes labelled;True\n")
    outfile.write("Edges labelled;True\n")
    outfile.write("Directed graph;False\n")
    outfile.write("\n")
    for vertex in vertices:
        outfile.write(";".join(vertices) + "\n")
    outfile.write("\n")
    for edge in edges:
        outfile.write(";".join(edges) + "\n")
    outfile.close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--filter-atom", help="Filtered atom types (comma "
                                                "separated)", default="")
    ap.add_argument("-i", "--input", help="Input file", required=True)
    ap.add_argument("-o", "--output", help="Output file", required=True)
    args = ap.parse_args()
    json2graph(args.input, args.output, args.filter_atom.split(","))
