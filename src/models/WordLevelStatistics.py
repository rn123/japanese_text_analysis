# -*- coding: utf-8 -*-

import re
from scipy import stats


class WordLevelStatistics():
    # Copyright 2014 Shubhanshu Mishra. All rights reserved.
    #
    # This library is free software; you can redistribute it and/or
    # modify it under the same terms as Python itself.
    def __init__(self, word_pos=None, corpus_file=None, percentile_C=95):
        '''This package is a port of the perl module Algorithm::WordLevelStatistics by
        Francesco Nidito which can be found at:
        http://search.cpan.org/~nids/Algorithm-WordLevelStatistics-0.03/

        The code is an implementation of the spatial statistics described in
        the following paper:
        @article{carpena2009level,
          title={Level statistics of words: Finding keywords in literary texts and symbolic sequences},
          author={Carpena, P and Bernaola-Galv{\'a}n, P and Hackenberg, M and Coronado, AV and Oliver, JL},
          journal={Physical Review E},
          volume={79},
          number={3},
          pages={035102},
          year={2009},
          publisher={APS}
        }

        Author: Shubhanshu Mishra
        Published: December 29, 2014
        License: GPL3
        '''
        if percentile_C is not None:
            self.percentile_C = percentile_C

        if word_pos is not None:
            self.word_pos = word_pos
        elif corpus_file is not None:
            self.word_pos = dict()
            self.pos_counter = 0
            if isinstance(corpus_file, list):
                for c in corpus_file:
                    self.gen_word_pos(c)
            else:
                self.gen_word_pos(corpus_file)

    def gen_word_pos(self, corpus_file):
        # with open(corpus_file, encoding='utf-8') as fp:
        text = corpus_file.read()  # .lower()
        tokens = re.findall('\w+', text)
        self.tokens = tokens
        for t in tokens:
            if t not in self.word_pos:
                self.word_pos[t] = []
            self.word_pos[t].append(self.pos_counter)
            self.pos_counter += 1

    def compute_spectra(self):
        if self.word_pos is None or len(self.word_pos.keys()) < 1:
            return None
        # Count total words in the text.
        self.tot_words = sum([len(self.word_pos[k]) for k in self.word_pos.keys()])

        # Compute level statistics of all terms
        self.level_stat = []
        for k in self.word_pos.keys():
            ls = self.compute_spectrum(k)
            self.level_stat.append(ls)

        # Sort level_stat frequency, use index in this list for vocab.
        self.level_stat = sorted(self.level_stat,
                                 key=lambda x: x['count'],
                                 reverse=True)

        # Add index to keep track of vocab, higher freq <-> higer index.
        for n, vocab_entry in enumerate(self.level_stat):
            vocab_entry['vocab_index'] = n

        self.threshold = stats.scoreatpercentile(    ## TODO: Compute this directly, dont import extra lib.
            [t['C'] for t in self.level_stat], self.percentile_C)
        self.level_stat_thresholded = [t for t in self.level_stat if t['C'] > self.threshold]

        # Significant terms
        self.significant_terms = [t['word'] for t in self.level_stat_thresholded]

    def compute_spectrum(self, word):
        positions = self.word_pos[word]
        n = len(positions)
        ls = {'word': word, 'count': n, 'C': 0, 'sigma_nor': 0}
        if n > 3:
            # position -> distance from preceding element in text
            tmp = [positions[i+1] - positions[i] for i in range(n-1)]
            # len(tmp) = n-1
            avg = sum(tmp)*1.0/(n-1)
            sigma = sum([(k-avg)**2 for k in tmp])*1.0/(n-1)
            sigma = (sigma**(0.5))/avg

            p = n*1.0/self.tot_words
            ls['sigma_nor'] = sigma/((1.0-p)**.5)

            ls['C'] = (ls['sigma_nor'] - (2.0*n-1.0)/(2.0*n+2.0))\
                       * ((n**0.5) * (1.0+2.8*n**-0.865))
        return ls
