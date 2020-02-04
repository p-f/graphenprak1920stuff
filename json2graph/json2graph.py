import argparse
import json


def json2graph(inpath, outpath, remove_atoms=[]):
    file = open(inpath, "r")
    outfile = open(outpath, "w")
    parsed = json.load(file)
    file.close()
    compound = parsed["PC_Compounds"][0]["atoms"]
    bonds = parsed["PC_Compounds"][0]["bonds"]
    outfile.write("AUTHOR: Egal.\n")
    nr_of_atoms = len(compound["aid"])
    outfile.write("#nodes;" + str(nr_of_atoms) + "\n")
    nr_of_bonds = len(bonds["aid1"])
    outfile.write("#edges;" + str(nr_of_bonds) + "\n")
    outfile.write("Nodes labelled;True\n")
    outfile.write("Edges labelled;True\n")
    outfile.write("Directed graph;False\n")
    outfile.write("\n")
    removed_atom_ids = []
    for atom in range(nr_of_atoms):
        atom_type = str(compound["element"][atom])
        atom_id = str(compound["aid"][atom])
        if atom_type in remove_atoms:
            removed_atom_ids += [atom_id]
            continue
        outfile.write(atom_id + ";" + atom_type + "\n")
    outfile.write("\n")
    for bond in range(nr_of_bonds):
        source_id = str(bonds["aid1"][bond])
        target_id = str(bonds["aid2"][bond])
        if source_id in removed_atom_ids or target_id in removed_atom_ids:
            continue
        outfile.write(source_id + ";" + target_id + ";" +
                      str(bonds["order"][bond]) + "\n")
    outfile.close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--filter-atom", help="Filtered atom types (comma "
                                             "reparated)")
    ap.add_argument("-i", "--input", help="Input file", required=True)
    ap.add_argument("-o", "--output", help="Output file", required=True)
    args = ap.parse_args()
    json2graph(args.input, args.output, args.filter_atom.split(","))
