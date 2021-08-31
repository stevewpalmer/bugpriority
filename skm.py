# Specific Keyword Matching (SKM)
#
# Folder pointed by <name> must contain at least these files:
#
#   <name>_verify.json
#   <name>_keywords.json
#
# It may also contain a map file for mapping metadata names in
# the above two files to names we expect.
#
#   <name>_map.json

import json
import math
import os.path
import sys
import priority
import mapfile
import ijson
import nltk

from nltk.classify import NaiveBayesClassifier

# Define a word feature

def word_feats(words):
    return dict([(word, True) for word in words])

# Load a keywords file

def load_keywords(filename):
    bn = os.path.basename(filename)
    kwf = filename + '/' + bn + '_keywords.json'

    with open(kwf) as f1:
        fmap = json.load(f1)
        train_set = []
        for k in fmap['keywords']:
            p = k['priority']
            ws = k['words']
            train_set = train_set + [(word_feats(ws), p)]

        return NaiveBayesClassifier.train(train_set) 

# Verify the computed priority against the verification
# input file

def verify(filename, classifier):

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
                words = nltk.word_tokenize(d)
                classResult = classifier.classify(word_feats(words))
                cp = priority.weight_from_priority(classResult)

                result = abs(cp - wp)
                if result < 1:
                    success0 += 1
                if result < 2:
                    success1 += 1

                count = count + 1

        if count == 0:
            print (bn + ' : Failed to match any bugs')
        else:
            success0p = int((100/count) * success0)
            success1p = int((100/count) * success1)
            print (bn, ':', str(count), 'records :', success0p, '% success (exact),', success1p, '% success (+/-1)')

# Main program starts here

if len(sys.argv) < 2:
    print ('Syntax: skm.py <name>')
    exit()

# Folder pointed by <name> must contain at least these files:
#
#   <name>_training.json
#   <name>_verify.json
#   <name>_keywords.json
#
# It may also contain a map file for mapping metadata names in
# the above two files to names we expect.
#
#   <name>_map.json

mapfile.load_map(sys.argv[1])
classifier = load_keywords(sys.argv[1])
verify(sys.argv[1], classifier)
