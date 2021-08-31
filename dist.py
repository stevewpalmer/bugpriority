# Keyword Distribution
#
# The folder may contain a map file for mapping metadata names
# if needed:
#
#   <name>_map.json

import os
import os.path
import sys
import ijson
import nltk
import mapfile
import priority
from nltk.corpus import stopwords

# Stop-word corpus

stop_words = set(stopwords.words('english'))

# Tokenise the description, remove stop-words and words shorter than
# 3 characters or longer than 15. Then tag each word and filter to
# a specific set of tags.

def text_to_tokens(d):

    tk = nltk.word_tokenize(d)
    tk = [x for x in tk if x not in stop_words]
    tk = [x.lower() for x in tk if (len(x) > 2 and len(x) <= 15)]

    tagged = nltk.pos_tag(tk)

    # NLTK tags that we care about
    tags = ['NN', 'JJ', 'VBG', 'VBD', 'NNP', 'NNS', 'NNPS']

    return [x for (x,y) in tagged if y in tags]

def map_keyword(filename, keyword):

    bn = os.path.basename(filename)
    tf = filename + '/' + bn + '_verify.json'

    with open(tf, "r") as f2:
        bugs = ijson.items(f2, 'item')
        for bug in bugs:
            d = bug[mapfile.map['description']]
            p = bug[mapfile.map['priority']]
            wp = priority.weight_from_priority(p)
            if d and p and wp > 0:
                tks = text_to_tokens(d)

                for tk in tks:

                    if tk == keyword:
                        print (keyword, ",", wp)


# Main program starts here

if len(sys.argv) < 3:
    print ('Syntax: dist.py <name> <keyword>')
    exit()

mapfile.load_map(sys.argv[1])
map_keyword(sys.argv[1], sys.argv[2])
