import codecs
from copy import copy
from itertools import chain

from cylleneus.corpus import Corpus
from cylleneus.engine.analysis.filters import CachedLemmaFilter, CachedSynsetFilter
from cylleneus.engine.analysis.tokenizers import CachedLASLATokenizer
from cylleneus.search import Searcher


# Adapted from NLTK
def pad_sequence(
    sequence,
    n,
    pad_left=False,
    pad_right=False,
    left_pad_symbol=None,
    right_pad_symbol=None,
):
    """
    Returns a padded sequence of items before ngram extraction.

        >>> list(pad_sequence([1,2,3,4,5], 2, pad_left=True, pad_right=True, left_pad_symbol='<s>', right_pad_symbol='</s>'))
        ['<s>', 1, 2, 3, 4, 5, '</s>']
        >>> list(pad_sequence([1,2,3,4,5], 2, pad_left=True, left_pad_symbol='<s>'))
        ['<s>', 1, 2, 3, 4, 5]
        >>> list(pad_sequence([1,2,3,4,5], 2, pad_right=True, right_pad_symbol='</s>'))
        [1, 2, 3, 4, 5, '</s>']

    :param sequence: the source data to be padded
    :type sequence: sequence or iter
    :param n: the degree of the ngrams
    :type n: int
    :param pad_left: whether the ngrams should be left-padded
    :type pad_left: bool
    :param pad_right: whether the ngrams should be right-padded
    :type pad_right: bool
    :param left_pad_symbol: the symbol to use for left padding (default is None)
    :type left_pad_symbol: any
    :param right_pad_symbol: the symbol to use for right padding (default is None)
    :type right_pad_symbol: any
    :rtype: sequence or iter
    """
    sequence = iter(sequence)
    if pad_left:
        sequence = chain((left_pad_symbol,) * (n - 1), sequence)
    if pad_right:
        sequence = chain(sequence, (right_pad_symbol,) * (n - 1))
    return sequence

def ngrams(
    sequence,
    n,
    pad_left=False,
    pad_right=False,
    left_pad_symbol=None,
    right_pad_symbol=None,
):
    """
    Return the ngrams generated from a sequence of items, as an iterator.
    For example:

        >>> list(ngrams([1,2,3,4,5], 3))
        [(1, 2, 3), (2, 3, 4), (3, 4, 5)]

    Wrap with list for a list version of this function.  Set pad_left
    or pad_right to true in order to get additional ngrams:

        >>> list(ngrams([1,2,3,4,5], 2, pad_right=True))
        [(1, 2), (2, 3), (3, 4), (4, 5), (5, None)]
        >>> list(ngrams([1,2,3,4,5], 2, pad_right=True, right_pad_symbol='</s>'))
        [(1, 2), (2, 3), (3, 4), (4, 5), (5, '</s>')]
        >>> list(ngrams([1,2,3,4,5], 2, pad_left=True, left_pad_symbol='<s>'))
        [('<s>', 1), (1, 2), (2, 3), (3, 4), (4, 5)]
        >>> list(ngrams([1,2,3,4,5], 2, pad_left=True, pad_right=True, left_pad_symbol='<s>', right_pad_symbol='</s>'))
        [('<s>', 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, '</s>')]

    :param sequence: the source data to be converted into ngrams
    :type sequence: sequence or iter
    :param n: the degree of the ngrams
    :type n: int
    :param pad_left: whether the ngrams should be left-padded
    :type pad_left: bool
    :param pad_right: whether the ngrams should be right-padded
    :type pad_right: bool
    :param left_pad_symbol: the symbol to use for left padding (default is None)
    :type left_pad_symbol: any
    :param right_pad_symbol: the symbol to use for right padding (default is None)
    :type right_pad_symbol: any
    :rtype: sequence or iter
    """
    sequence = pad_sequence(
        sequence, n, pad_left, pad_right, left_pad_symbol, right_pad_symbol
    )

    history = []
    while n > 1:
        # PEP 479, prevent RuntimeError from being raised when StopIteration bubbles out of generator
        try:
            next_item = next(sequence)
        except StopIteration:
            # no more data, terminate the generator
            return
        history.append(copy(next_item))
        n -= 1
    for item in sequence:
        history.append(copy(item))
        yield tuple(history)
        del history[0]


def find_quotations(tokens, n=4, slop=1, synsets=False):
    """
    Finds lexically or semantically similar phrases in the reference corpus
    for phrases of length n in a tokenized source text.

    :param tokens: Generator of token objects for target text
    :param n: Length of gram (1-gram, bigram, trigram...) used in matching phrases
    :param slop: Permissible distance between tokens in the matching phrase
    :param synsets: Convert tokens to synsets before matching for semantic matching
    :return: List of Search objects representing matched phrases in
    """
    results = []

    # Load the reference corpus
    corpus = Corpus('lasla')
    count = corpus.index.doc_count_all()
    print(f"searching corpus '{corpus}' ({count} indexed)...")
    searcher = Searcher(corpus)

    lemmatizer = CachedLemmaFilter()
    if not synsets:
        before, after = '<', '>'
    else:
        synsetizer = CachedSynsetFilter()
        before, after = '[', ']'

    # Generate and process n-grams
    for ngram in ngrams(tokens, n):
        queries = []

        # Lemmatize, and optionally synsetize, every word in the ngram
        for gram in ngram:
            subqueries = set()
            if not synsets:
                for lemma in lemmatizer([copy(gram),], mode='index'):
                    subqueries.add(lemma.text.split('=')[0])
            else:
                for synset in synsetizer(lemmatizer([copy(gram),], mode='index'), mode='index'):
                    if synset.text:
                        subqueries.add(synset.text)

            # Construct subquery
            if len(subqueries) == 0:
                queries.append(f"{gram.text}")
            elif len(subqueries) == 1:
                queries.append(f"{before}{list(subqueries)[0]}{after}")
            else:
                queries.append(f'''({' OR '.join([f"{before}{subquery}{after}" for subquery in subqueries])})''')

        # Join all subqueries into a single complex adjacency or proximity query
        if slop:
            query = f'''"{' '.join(queries)}"{f'~{slop}' if slop else ''}'''
        else:
            query = f'''{' '.join(queries)}'''

        # Execute the query against the given corpus
        search = searcher.search(query)

        # Display the query if any matches
        if search.count != (0, 0):  # matches, docs
            results.append(search.highlights)
    return results


if __name__ == "__main__":
    print("""
    ================================ CYLLENEUS SEMANTIC SEARCH ENGINE v0.0.1 ================================
    (c) 2019 William Michael Short
    """)

    # Load target text and process, if necessary
    with codecs.open('corpus/text/lasla/Catullus_Catullus_Catul.BPN', 'r', 'utf8') as fp:
        doc = fp.readlines()

    meta = 'poem-verse'

    # Tokenize the target text
    tokenizer = CachedLASLATokenizer()
    tokens = tokenizer({ "text": doc, "meta": meta }, mode='index')  # generator
    results = find_quotations(tokens, n=5)
    print(results)
