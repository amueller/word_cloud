from __future__ import division
from itertools import tee
from operator import itemgetter
from collections import defaultdict
from math import log


def l(k, n, x):
    # dunning's likelihood ratio with notation from
    # http://nlp.stanford.edu/fsnlp/promo/colloc.pdf
    return log(max(x, 1e-10)) * k + log(max(1 - x, 1e-10)) * (n - k)


def score(count_bigram, count1, count2, n_words):
    """Collocation score"""
    N = n_words
    c12 = count_bigram
    c1 = count1
    c2 = count2
    p = c2 / N
    p1 = c12 / c1
    p2 = (c2 - c12) / (N - c1)
    score = (l(c12, c1, p) + l(c2 - c12, N - c1, p)
             - l(c12, c1, p1) - l(c2 - c12, N - c1, p2))
    return -2 * score


def pairwise(iterable):
    # from itertool recipies
    # is -> (s0,s1), (s1,s2), (s2, s3), ...
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def unigrams_and_bigrams(words, normalize_plurals=True):
    n_words = len(words)
    # make tuples of two words following each other
    bigrams = list(pairwise(words))
    counts_unigrams = defaultdict(int)
    counts_bigrams = defaultdict(int)
    counts_unigrams, standard_form = process_tokens(
        words, normalize_plurals=normalize_plurals)
    counts_bigrams, standard_form_bigrams = process_tokens(
        [" ".join(bigram) for bigram in bigrams],
        normalize_plurals=normalize_plurals)
    # create a copy of counts_unigram so the score computation is not changed
    counts = counts_unigrams.copy()

    # decount words inside bigrams
    for bigram_string, count in counts_bigrams.items():
        bigram = tuple(bigram_string.split(" "))
        # collocation detection (30 is arbitrary):
        word1 = standard_form[bigram[0].lower()]
        word2 = standard_form[bigram[1].lower()]

        if score(count, counts[word1], counts[word2], n_words) > 30:
            # bigram is a collocation
            # discount words in unigrams dict. hack because one word might
            # appear in multiple collocations at the same time
            # (leading to negative counts)
            counts_unigrams[word1] -= counts_bigrams[bigram_string]
            counts_unigrams[word2] -= counts_bigrams[bigram_string]
            counts_unigrams[bigram_string] = counts_bigrams[bigram_string]
    words = list(counts_unigrams.keys())
    for word in words:
        # remove empty / negative counts
        if counts_unigrams[word] <= 0:
            del counts_unigrams[word]
    return counts_unigrams


def process_tokens(words, normalize_plurals=True):
    """Normalize cases and remove plurals.

    Each word is represented by the most common case.
    If a word appears with an "s" on the end and without an "s" on the end,
    the version with "s" is assumed to be a plural and merged with the
    version without "s" (except if the word ends with "ss").

    Parameters
    ----------
    words : iterable of strings
        Words to count.

    normalize_plurals : bool, default=True
        Whether to try and detect plurals and remove trailing "s".

    Returns
    -------
    counts : dict from string to int
        Counts for each unique word, with cases represented by the most common
        case, and plurals removed.

    standard_forms : dict from string to string
        For each lower-case word the standard capitalization.
    """
    # words can be either a list of unigrams or bigrams
    # d is a dict of dicts.
    # Keys of d are word.lower(). Values are dicts
    # counting frequency of each capitalization
    d = defaultdict(dict)
    for word in words:
        word_lower = word.lower()
        # get dict of cases for word_lower
        case_dict = d[word_lower]
        # increase this case
        case_dict[word] = case_dict.get(word, 0) + 1
    if normalize_plurals:
        # merge plurals into the singular count (simple cases only)
        merged_plurals = {}
        for key in list(d.keys()):
            if key.endswith('s') and not key.endswith("ss"):
                key_singular = key[:-1]
                if key_singular in d:
                    dict_plural = d[key]
                    dict_singular = d[key_singular]
                    for word, count in dict_plural.items():
                        singular = word[:-1]
                        dict_singular[singular] = (
                            dict_singular.get(singular, 0) + count)
                    merged_plurals[key] = key_singular
                    del d[key]
    fused_cases = {}
    standard_cases = {}
    item1 = itemgetter(1)
    for word_lower, case_dict in d.items():
        # Get the most popular case.
        first = max(case_dict.items(), key=item1)[0]
        fused_cases[first] = sum(case_dict.values())
        standard_cases[word_lower] = first
    if normalize_plurals:
        # add plurals to fused cases:
        for plural, singular in merged_plurals.items():
            standard_cases[plural] = standard_cases[singular.lower()]
    return fused_cases, standard_cases
