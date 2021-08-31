# Priority to weight mapping

p_map = {
	"critical" : 5,
	"blocker" : 5,
	"highest" : 5,
	"p1" : 5,
	"high" : 4,
	"major" : 4,
	"p2" : 4,
	"medium" : 3,
	"p3" : 3,
	"low" : 2,
	"minor" : 2,
	"p4" : 2,
	"lowest" : 1,
	"trivial" : 1,
	"p5" : 1
}

# Convert a priority name to an weight. Returns
# 0 if the priority name is unknown

def weight_from_priority(p):
	return p_map[p.lower()] if p and p.lower() in p_map else 0