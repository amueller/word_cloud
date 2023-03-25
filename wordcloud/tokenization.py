from __future__ import division
from itertools import tee
from operator import itemgetter
from collections import defaultdict
from math import log


def l(k, n, x):  # noqa: E741, E743
    # dunning's likelihood ratio with notation from
    # http://nlp.stanford.edu/fsnlp/promo/colloc.pdf p162
    return log(max(x, 1e-10)) * k + log(max(1 - x, 1e-10)) * (n - k)


def score(count_bigram, count1, count2, n_words):
    """Collocation score"""
    if n_words <= count1 or n_words <= count2:
        # only one words appears in the whole document
        return 0
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


def unigrams_and_bigrams(words, stopwords, normalize_plurals=True, collocation_threshold=30):
    # We must create the bigrams before removing the stopword tokens from the words, or else we get bigrams like
    # "thank much" from "thank you very much".
    # We don't allow any of the words in the bigram to be stopwords
    bigrams = list(p for p in pairwise(words) if not any(w.lower() in stopwords for w in p))
    unigrams = list(w for w in words if w.lower() not in stopwords)
    n_words = len(unigrams)
    counts_unigrams, standard_form = process_tokens(
        unigrams, normalize_plurals=normalize_plurals)
    counts_bigrams, standard_form_bigrams = process_tokens(
        [" ".join(bigram) for bigram in bigrams],
        normalize_plurals=normalize_plurals)
    # create a copy of counts_unigram so the score computation is not changed
    orig_counts = counts_unigrams.copy()

    # Include bigrams that are also collocations
    for bigram_string, count in counts_bigrams.items():
        bigram = tuple(bigram_string.split(" "))
        word1 = standard_form[bigram[0].lower()]
        word2 = standard_form[bigram[1].lower()]

        collocation_score = score(count, orig_counts[word1], orig_counts[word2], n_words)
        if collocation_score > collocation_threshold:
            # bigram is a collocation
            # discount words in unigrams dict. hack because one word might
            # appear in multiple collocations at the same time
            # (leading to negative counts)
            counts_unigrams[word1] -= counts_bigrams[bigram_string]
            counts_unigrams[word2] -= counts_bigrams[bigram_string]
            counts_unigrams[bigram_string] = counts_bigrams[bigram_string]
    for word, count in list(counts_unigrams.items()):
        if count <= 0:
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
