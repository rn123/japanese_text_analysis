# -*- coding: utf-8 -*-

import numpy as np
from scipy import stats
from collections import Counter, defaultdict

import hdbscan

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s %(message)s', '%b-%d-%Y %H:%M:%S')
logger.handlers[0].setFormatter(formatter)


def hdbscan_parameter_search(
                                X,
                                min_cluster_size_min=4,
                                min_cluster_size_max=10,
                                min_samples_min=4,
                                min_samples_max=10,
                                target_label_min=5,
                                target_label_max=260,
                                cluster_selection_method='leaf'
                            ):
    # Brute force over combinations.
    sizes = range(min_cluster_size_min, min_cluster_size_max)
    ranges = range(min_samples_min, min_samples_max)
    all_combinations = ((c, s) for c in sizes for s in ranges)

    logging.info('Searching for clusters with: %d <= label_max <= %d',
                 target_label_min, target_label_max)
    cluster_params = []
    label_values = []
    cluster_bincounts = []

    # Calculate results of hdbscan for every combination, save results.
    for min_cluster_size, min_samples in all_combinations:
        labels, *rest = hdbscan.hdbscan(
                            X,
                            approx_min_span_tree=False,
                            cluster_selection_method=cluster_selection_method,
                            min_cluster_size=min_cluster_size,
                            min_samples=min_samples
                        )
        true_labels = [label for label in labels if label != -1]
        try:
            label_max = np.max(true_labels)
        except Exception as ex:
            logging.error('(%s) labels %s', ex, set(labels))
            continue

        if label_max >= target_label_min and label_max <= target_label_max:
            label_values.append(label_max)
            cluster_params.append((min_cluster_size, min_samples))
            cluster_bincounts.append(np.bincount(true_labels))

    label_values = list(reversed(label_values))
    cluster_params = list(reversed(cluster_params))
    cluster_bincounts = list(reversed(cluster_bincounts))

    # Select a solution of the clustering problem that has the most clusters.
    if len(label_values) > 0:
        i = np.argmax(label_values)
        min_cluster_size_opt, min_samples_opt = cluster_params[i]
        label_max = label_values[i]

    # Print out all the solutions with the max number of clusters.
    for i, label in enumerate(label_values):
        if label == label_max:
            logging.info('%d %d %d %s' % (
                *cluster_params[i],
                label,
                cluster_bincounts[i]
            ))

    logging.info('label_max = %d, min_cluster_size = %d, min_samples = %d',
                 label_max, min_cluster_size_opt, min_samples_opt)

    return min_cluster_size_opt, min_samples_opt


def enumerate_exemplars(clusterer, X):
    points = []
    ex_no = []
    for n, ex in enumerate(clusterer.exemplars_):
        ex_points = []
        for point in ex:
            points.append(point)
            ex_points.append(point)
            ex_no.append(n)

    exemplars = ['']*len(X)
    for n, v in enumerate(X):
        for p in points:
            if np.allclose(v, p):
                exemplars[n] = '*'

    return exemplars


def topic_order_index(topic_list):
    '''
    The input is a list of integers (topics) that has many repeats but has been
    sorted in a meaningful way (e.g by some word importance score). Three
    topics might look, for example, like [1, 1, 2, 1, 3, 2, 2, 3] and this
    routine produces an index to keep track of the topic
    order => [1, 2, 1, 3, 1, 2, 3, 2].
    '''
    position_counter = Counter()
    per_topic_index = []
    for t in topic_list:
        position_counter[t] += 1
        per_topic_index.append(position_counter[t])
    return per_topic_index


def filter_enrich_significant_terms(df, percentile_C,
                                    cluster_selection_method):
    # Find topic clusters for the data after applying threshhold
    # corresponding to desired percentile.
    threshold = stats.scoreatpercentile(df['C'], percentile_C)
    significant_terms_filtered = df[df['C'] > threshold].copy()

    X = list(significant_terms_filtered['vector'])
    min_cluster_size_opt, min_samples_opt = hdbscan_parameter_search(
        X, cluster_selection_method=cluster_selection_method)

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size_opt,
        min_samples=min_samples_opt,
        approx_min_span_tree=False,
        cluster_selection_method=cluster_selection_method)
    labels = clusterer.fit_predict(X)
    significant_terms_filtered['topic'] = labels

    exemplars = enumerate_exemplars(clusterer, X)
    significant_terms_filtered['exemplar'] = exemplars
    significant_terms_filtered['word*'] = (
        significant_terms_filtered['word'] +
        significant_terms_filtered['exemplar'])

    topic_list = list(significant_terms_filtered['topic'])
    significant_terms_filtered['pos'] = topic_order_index(topic_list)

    return significant_terms_filtered


def message_topics(topic_model=None, sentences=None,
                   sentences_ids=None, significant_terms=None):
    ''' Cacluate the distribution of term weights in each sentence.
        Expects a data frame that at least includes columns for word,
        weight, and topic number. Expects lists of sentences and their
        corresponding ids. The significant terms are used to further
        restrict the terms.
    '''
    K = topic_model['topic'].max()
    message_topics = {}

    # Simple maps for convenicence.
    wt = list(zip(list(topic_model['word']), list(topic_model['topic'])))
    word_to_topic = {}
    for w, t in wt:
        word_to_topic[w] = t

    def map_word_to_topic(w):
        try:
            t = word_to_topic[w]
        except Exception as ex:
            t = ''
        return (w, t)

    ww = list(zip(list(topic_model['word']), list(topic_model['weight'])))
    word_to_weight = {}
    for w, t in ww:
        word_to_weight[w] = t

    def map_word_to_weight(w):
        try:
            wt = word_to_weight[w]
        except Exception as ex:
            wt = 0.0
        return (w, wt)

    def terms_to_topics(terms=None):
        topic_vector = defaultdict(list)
        word_topic_list = list(map(map_word_to_topic, terms))
        for k, v in word_topic_list:
            topic_vector[v].append(k)
        return [len(topic_vector[n]) for n in range(1, K+1)]

    def terms_to_weights(terms=None, topic_no=1, doc_id=None):
        weight_vector = {}
        for w in significant_words:
            if w in word_to_weight:
                for t in range(0, K+1):
                    if w in word_to_topic:
                        if word_to_topic[w] == t:
                            if t in weight_vector:
                                # print(t,weight_vector)
                                if len(terms) > 0:
                                    weight_vector[t] += word_to_weight[w]/len(terms)
                                else:
                                    weight_vector[t] += word_to_weight[w]
                            else:
                                if len(terms) > 0:
                                    weight_vector[t] = word_to_weight[w]/len(terms)
                                else:
                                    weight_vector[t] = word_to_weight[w]

        weight_vector['doc_id'] = doc_id
        return weight_vector

    for doc_id, message_txt in list(zip(sentences_ids, sentences)):
        words = message_txt.split()
        significant_words = [w for w in words if w in significant_terms]
        message_topics[doc_id] = terms_to_weights(terms=significant_words,
                                                  doc_id=doc_id)
        # message_topics[doc_id] = terms_to_topics(terms=significant_words)

    return message_topics


def enrich_significant_terms(significant_terms, vec, vec_2d, cluster_method):
    # Find topic clusters for the data
    min_cluster_size_opt, min_samples_opt = hdbscan_parameter_search(
                          vec,
                          cluster_selection_method=cluster_method)

    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size_opt,
                                min_samples=min_samples_opt,
                                approx_min_span_tree=False,
                                cluster_selection_method=cluster_method)
    labels = clusterer.fit_predict(np.array(vec))
    significant_terms['topic'] = labels

    exemplars = enumerate_exemplars(clusterer, np.array(vec))
    significant_terms['exemplar'] = exemplars
    significant_terms['word*'] = (significant_terms['word'] +
                                  significant_terms['exemplar'])

    topic_list = list(significant_terms['topic'])
    significant_terms['pos'] = topic_order_index(topic_list)

    significant_terms['x2D'] = [v[0] for v in vec_2d]
    significant_terms['y2D'] = [v[1] for v in vec_2d]

    return significant_terms


def topic_exemplars(df):
    grouped = df.groupby('topic')
    hovers = []
    exemplar_scores = []
    for topic, group in grouped:
        if topic > -1:
            h = 'topic ' + str(topic) + ': '
            exemplars = list(group[group['exemplar'] == '*']['word'])
            score = group[group['exemplar'] == '*']['sigma_nor'].sum()
            exemplar_scores.append(score)
            hovers.append(h + ' | '.join(exemplars))
    return exemplar_scores, hovers


def display_topics(df, n_rows=10, n_cols=12):
    """Pretty-print table of themes and some corpus statistics."""

    exemplar_scores, hovers = topic_exemplars(df)
    top_columns = sorted(range(len(exemplar_scores)),
                         key=lambda i: exemplar_scores[i],
                         reverse=True)[:n_cols]

    topics = df.pivot(index='pos', columns='topic', values='word*') # .replace([None], [''], regex=True)

    topics_display = topics[top_columns].head(n_rows)

    return topics_display, top_columns
