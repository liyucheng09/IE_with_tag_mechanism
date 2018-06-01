#!/usr/bin/env python
# -*-coding:utf-8-*-

import sys
from dltk import trie


class Dictionary():
    def __init__(self):
        self.trie = trie.Trie()
        self.weights = {}
        self.sizes = 0

    def delete_dict(self):
        self.trie = trie.Trie()
        self.weights = {}
        self.sizes = 0

    def add_dict(self, path):
        words = []

        with open(path) as f:
            for i, line in enumerate(f):
                line = line.strip("\n").strip()
                if not line:
                    continue
                line = line.split()
                word = line[0].strip()
                if sys.version_info[0] == 3:                
                    self.trie.add_keyword(word)
                else:
                    self.trie.add_keyword(word.decode('utf-8'))
                if len(line) == 1:
                    weight = 1.0
                else:
                    weight = float(line[1])
                weight = float(weight)
                # compromise to python 2
                
                if sys.version_info[0] == 3:
                    self.weights[word] = weight
                    words.append(word)
                else:
                    self.weights[word.decode('utf-8')] = weight
                    words.append(word.decode('utf-8'))
                
        self.sizes += len(self.weights)

    def parse_words(self, text):
        matchs = self.trie.parse_text(text)
        return matchs

    def get_weight(self, word):
        return self.weights.get(word, 0.1)
