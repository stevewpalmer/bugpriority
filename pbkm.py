# Priority-Based Keyword Matching (PBKM)
#
# Folder pointed by <name> must contain at least these files:
#
#   <name>_training.json
#   <name>_verify.json
#
# It may also contain a map file for mapping metadata names in
# the above two files to names we expect.
#
#   <name>_map.json

import os
import re
import os.path
import sys
import ijson
import nltk
import mapfile
import priority
from collections import Counter

from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn

# Top 10 keywords

kp = ()

# Corpus

stop_words = set(stopwords.words('english'))

# Tokenise the description and filter out any word in the
# English language corpus.

def text_to_tokens(d):

    # Make all tokens lower-case, limit to 3..15 characters and 
    # filter out stop-words
    tk = nltk.word_tokenize(d)
    tk = [x.lower() for x in tk if (len(x) > 2 and len(x) <= 15)]
    tk = [x for x in tk if x not in stop_words]

    # Remove any words which have non-alphabetic characters
    tk = [x for x in tk if re.search('^[a-zA-Z]+$', x)]

    # Filter further to just nouns and specific verbs.
    tagged = nltk.pos_tag(tk)
    tags = ['NN', 'JJ', 'VBG', 'VBD', 'NNP', 'NNS', 'NNPS']
    tk = [x for (x,y) in tagged if y in tags]

    # Restrict results to those in the wordnet corpus
    return [x for x in tk if len(wn.synsets(x)) == 0]

# Build the priority map from the training input file

def build_training(filename):

    global kp

    bn = os.path.basename(filename)
    tf = filename + '/' + bn + '_training.json'

    k_map = Counter()

    with open(tf, "r") as f2:
        bugs = ijson.items(f2, 'item')
        for bug in bugs:

            d = bug[mapfile.map['description']]
            p = bug[mapfile.map['priority']]
            wp = priority.weight_from_priority(p)

            if d and wp > 0:

                tks = text_to_tokens(d)
                for tk in tks:
                    if (wp == 4):   # 4 = Major pri bugs
                        if tk in k_map:
                            k_map[tk] += 1
                        else:
                            k_map[tk] = 1

    # List of 10 most common words in major bugs
    kp = [x for (x,y) in k_map.most_common(10)]
   
    # Report
    print ('Most common words are ' + ",".join(kp))

# Verify the computed priority against the verification
# input file

def verify(filename):

    global kp

    bn = os.path.basename(filename)
    tf = filename + '/' + bn + '_verify.json'

    with open(tf, "r") as f2:
        bugs = ijson.items(f2, 'item')
        success0 = 0
        success1 = 0
        count = 0
        for bug in bugs:
            d = bug[mapfile.map['description']]
            p = bug[mapfile.map['priority']]
            wp = priority.weight_from_priority(p)
            if d and wp > 0:
                tks = text_to_tokens(d)
                cp = 0
                for tk in tks:
                    if tk in kp:
                        cp = 1

                if cp == 1 and wp == 4:
                    success0 = success0 + 1
                if cp == 1 and (wp >= 3 and wp <= 5):
                    success1 = success1 + 1

                count = count + 1

        if count == 0:
            print (bn + ' : Failed to match any bugs')
        else:
            success0p = int((100/count) * success0)
            success1p = int((100/count) * success1)
            print (bn, ':', str(count), 'records :', success0p, '% success (exact),', success1p, '% success (+/-1)')

# Main program starts here

if len(sys.argv) < 2:
    print ('Syntax: pbkm.py <name>')
    exit()

mapfile.load_map(sys.argv[1])
build_training(sys.argv[1])
verify(sys.argv[1])
