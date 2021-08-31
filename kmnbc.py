# Keyword Matching with NBC (KMNBC)
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

import math
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

from nltk.classify import NaiveBayesClassifier

# Define a word feature

def word_feats(words):
    return dict([(word, True) for word in words])

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

# Build the priority map from the training input file

def build_training(filename):

    bn = os.path.basename(filename)
    tf = filename + '/' + bn + '_training.json'

    train_set = []

    with open(tf, "r") as f2:
        bugs = ijson.items(f2, 'item')
        for bug in bugs:
            d = bug[mapfile.map['description']]
            p = bug[mapfile.map['priority']]
            wp = priority.weight_from_priority(p)
            if d and p and wp > 0:
                tks = text_to_tokens(d)
                train_set = train_set + [(word_feats(tks), p)]

    return NaiveBayesClassifier.train(train_set) 

# Verify the computed priority against the verification
# input file

def verify(filename, classifier):

    bn = os.path.basename(filename)
    tf = filename + '/' + bn + '_verify.json'

    with open(tf, "r") as f2:
        bugs = ijson.items(f2, 'item')
        success0 = 0
        success1 = 1
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
    print ('Syntax: kmnbc.py <name>')
    exit()

mapfile.load_map(sys.argv[1])
classifier = build_training(sys.argv[1])
verify(sys.argv[1], classifier)
