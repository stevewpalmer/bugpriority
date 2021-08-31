# Split a JSON file into separate training
# and verification files.

import ijson
import sys
import os
import json
import decimal

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): return float(obj)

def split(filename):

    # Output files are in the same folder as the original

    tf = os.path.splitext(filename)[0] + '_training.json'
    vf = os.path.splitext(filename)[0] + '_verify.json'

    w = 0
    with open(filename, "r") as f1:
        with open(tf, "w") as f2:
            with open(vf, "w") as f3:

                f2.write('[')
                f3.write('[')

                bugs = ijson.items(f1, 'item')
                f2_sep = ''
                f3_sep = ''
                for bug in bugs:
                    if w == 0:
                        f2.write(f2_sep + json.dumps(bug, cls = Encoder))
                        f2_sep = ','
                        w = 1
                    else:
                        f3.write(f3_sep + json.dumps(bug, cls = Encoder))
                        f3_sep = ','
                        w = 0

                f2.write(']')
                f3.write(']')

# Main program starts here

if len(sys.argv) < 2:
    print ('Syntax: split.py <json_file>')
    exit()

split(sys.argv[1])
