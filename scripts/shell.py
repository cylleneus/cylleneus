import codecs
import unicodedata
import re

from engine import index
from utils import spinner
from search import Searcher
from corpus import Corpus


def main():
    print("""
    ================================ CYLLENEUS SEMANTIC SEARCH ENGINE v0.0.1 ================================
    (c) 2019 William Michael Short
    """)
    s = spinner.Spinner('simpleDotsScrolling')

    s.start()
    c = None
    corpus_name = 'lasla'
    corpus = Corpus(corpus_name)
    count = corpus.index.doc_count_all()
    searcher = Searcher(corpus)
    s.stop()

    print("type 'help' for help, 'exit' to exit")
    print(f"using corpus '{corpus}' ({count} indexed)")
    search = None
    while c != 'exit':
        c = input(">>> ")
        if c != '' and c != 'exit':
            if c.split()[0] == 'corpus':
                new_corpus = c.split()[1]
                if new_corpus == '?':
                    for docnum, fields in corpus.index.reader().iter_docs():
                        print(f"{docnum}.", fields['author'].title(), fields['title'].title())
                else:
                    if index.exists_in(f"index/{new_corpus}"):
                        s_ = spinner.Spinner('simpleDotsScrolling')
                        s_.start()
                        corpus = Corpus(new_corpus)
                        count = corpus.index.doc_count_all()
                        searcher = Searcher(corpus)
                        s_.stop()
                        print(f"using corpus '{corpus}' ({count} indexed)")
            elif c.split()[0] == 'save':
                if search and search.results:
                    try:
                        filename = c.split()[1]
                    except IndexError:
                        filename = slugify(search.query, allow_unicode=False)
                    finally:
                        with codecs.open(f"{filename}", "w", "utf8") as fp:
                            for hlite in search.highlights:
                                fp.write(hlite)
                        print(f"saved '{filename}'")
            elif c.split()[0] == 'print':
                if search and search.results:
                    for hlite in search.highlights:
                        print(hlite.strip('\n'))
            elif c.split()[0] == 'list':
                for i, s in enumerate(searcher.history):
                    print(f"{i+1}.\t{s}")
            elif c.split()[0] == 'get':
                try:
                    i = int(c.split()[1])
                except IndexError:
                    pass
                except ValueError:
                    pass
                else:
                    if 0 < i <= len(searcher.searches):
                        search = searcher.searches[i-1]
            elif c.split()[0] == 'help':
                print("""
Possible query types:
    'virtutem'          literal form
    <virtus>            lemma
    [en?courage]        gloss ('en', 'it', 'es', 'fr')
    [n#05595229]        gloss (synset-based)
    {611}, {Anatomy}    domain (use DDCS codes or names)
    :ACC.SG.            morphology (Leipzig notation)
    </=virtus>          lexical relations (/=relates to, \=derives from, +c=composed of, -c=composes)
    [@=n#05595229]      semantic relations (!=antonym, @=hypernym, ~=hyponym, |=nearest, *=entails,
                                #m=member of, #p=substance of, #s=substance of, +r=has role,
                                %m=has member, %p=has part, %s=has substance, -r=is role, 
                                >=causes, ^=see also, $=verb group, <=participle, ==attribute)
    /ablative absolute/ syntactical constructions

Other commands:
    list                list search history
    get <#>             retrieve search by #
    save <filename>     save current search to disk
    print               print current search to screen
    corpus <name>       load corpus index
    """)
            else:
                s__ = spinner.Spinner('simpleDotsScrolling')
                s__.start()
                search = searcher.search(c)
                s__.stop()
                print(f"{search.time} secs, {search.count[0]} results")


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


if __name__=="__main__":
    main()
