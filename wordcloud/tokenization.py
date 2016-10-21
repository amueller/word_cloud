from itertools import tee
from operator import itemgetter
from collections import defaultdict
import re
from math import log


def l(k, n, x):
    # dunning's likelihood ratio with notation from
    # http://nlp.stanford.edu/fsnlp/promo/colloc.pdf
    return log(max(x, 1e-10)) * k + log(max(1 - x, 1e-10)) * (n - k)


def score(bigram, counts, n_words):
    """Collocation score"""
    N = n_words
    c12 = counts[bigram]
    c1 = counts[bigram[0]]
    c2 = counts[bigram[1]]
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


def unigrams_and_bigrams(text, stopwords, token_regex, flags):
    words = re.findall(r"\w[\w']+", text)
    # remove stopwords
    words = [word for word in words if word.lower() not in stopwords]
    # remove 's
    words = [word[:-2] if word.lower().endswith("'s") else word
             for word in words]
    n_words = len(words)
    # make tuples of two words following each other
    bigrams = list(pairwise(words))
    counts_unigrams = defaultdict(int)
    counts_bigrams = defaultdict(int)
    for word in words:
        counts_unigrams[word] += 1
    for bigram in bigrams:
        counts_bigrams[bigram] += 1

    counts_all = {}
    counts_all.update(counts_unigrams)
    counts_all.update(counts_bigrams)

    # decount words inside bigrams
    for bigram in counts_bigrams.keys():
        # collocation detection (30 is arbitrary):
        if score(bigram, counts_all, n_words) > 30:
            counts_unigrams[bigram[0]] -= counts_bigrams[bigram]
            counts_unigrams[bigram[1]] -= counts_bigrams[bigram]
        # add joined bigram into unigrams
        counts_unigrams[' '.join(bigram)] = counts_bigrams[bigram]
    return counts_unigrams


def unigram_counts(text, stopwords, regexp, flags):
    d = {}
    for word in re.findall(regexp, text, flags=flags):
        if word.isdigit():
            continue

        word_lower = word.lower()
        if word_lower in stopwords:
            continue

        # Look in lowercase dict.
        try:
            d2 = d[word_lower]
        except KeyError:
            d2 = {}
            d[word_lower] = d2

        # Look in any case dict.
        d2[word] = d2.get(word, 0) + 1


def remove_plurals(word_counts):
    # merge plurals into the singular count (simple cases only)
    for key in list(word_counts.keys()):
        if key.endswith('s'):
            key_singular = key[:-1]
            if key_singular in word_counts:
                dict_plural = word_counts[key]
                dict_singular = word_counts[key_singular]
                for word, count in dict_plural.items():
                    singular = word[:-1]
                    dict_singular[singular] = (dict_singular.get(singular, 0)
                                               + count)
                del word_counts[key]

    d3 = {}
    item1 = itemgetter(1)
    for d2 in word_counts.values():
        # Get the most popular case.
        first = max(d2.items(), key=item1)[0]
        d3[first] = sum(d2.values())
    return d3
