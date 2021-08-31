# Keyword Map file parsing

import json
import os

# JSON field name map

map = {}

# Load a map file

def load_map(filename):
	bn = os.path.basename(filename)
	mapf = filename + '/' + bn + '_map.json'

	map['id'] = 'issue_id'
	map['description'] = 'description'
	map['priority'] = 'priority'

	if os.path.isfile(mapf):
		with open(mapf) as f1:
			fmap = json.load(f1)
		map.update(fmap)
