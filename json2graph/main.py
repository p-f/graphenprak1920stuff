import sys

from json2graph.json2graph import json2graph

if __name__ == '__main__':
    if (len(sys.argv) < 3):
        print("Usage: JSONIN GRAPHOUTOUT")
    else:
        json2graph(sys.argv[1], sys.argv[2])
