import json


def json2graph(inpath, outpath):
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
    for atom in range(nr_of_atoms):
        outfile.write(str(compound["aid"][atom]) + ";" + str(compound["element"][atom]) + "\n")
    outfile.write("\n")
    for bond in range(nr_of_bonds):
        outfile.write(str(bonds["aid1"][bond]) + ";" + str(bonds["aid2"][bond]) + ";" + str(bonds["order"][bond]) + "\n")
    outfile.close()
