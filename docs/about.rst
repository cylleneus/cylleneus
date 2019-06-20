=====
About
=====

Towards a semantic and syntactic search engine for electronic corpora of Greek and Latin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

William Michael Short
`````````````````````
The University of Exeter, Department of Classics & Ancient History

Existing applications for browsing and searching electronic corpora of Greek and Latin fall into
two broad categories. The first comprises basic textual search tools using ‘regular expression’
pattern matching. These tools allow users to perform word-form and ‘wildcard’ searches,
including lexical co-occurrence queries. For example, a user can search for the Latin word
*lacrimas* near words containing the stem *-fund-* to discover where authors write about
‘shedding tears’, whether with the verb *profundo*, *effundo*, or simply *fundo*. The second category
comprises tools that can query texts tagged with various sorts of metadata, including
information about metre, genre and time period, the parts of speech of words, intertextual
references, or parallel translations. Both types have made corpus search indispensable for
studying Greek and Latin, which are morphologically complex languages with relatively free
word order. However, while improving the efficiency, precision, and scope of corpus-based
research, they have left a window for new applications that redefine the sorts of questions users
are able to ask of ancient texts.
The search engine software we are designing will enable its users to explore Greek and Latin
texts in new ways by opening these texts to queries based – for the first time – on their semantic
as well as syntactic properties. Using our tool, users will be able to search Latin (and, at a later
stage of the project, Greek) texts by inputting meanings in English (or another language)
without concern for how these meanings are captured lexically in the target corpus. This means
that in the above example the user could replace the wildcard *-fund-* with the meaning ‘shed’
or ‘pour’, and the search engine would return instances with *profundo*, *effundo*, and *fundo*, but
also passages where the semantically similar verbs *mitto* and *mano* appear, which otherwise
will be missed. Likewise, by replacing the fixed word-form *lacrimas* with the meaning ‘tears’ or
‘crying’, our engine would automatically include additional instances where this notion is
represented by *fletus*, *ploratus*, or *delacrimatio*. In principle, searches could be conducted across
both corpora simultaneously, without the user needing to constrain her query to specific words
in Greek or Latin.
Meaning-based search improves upon pattern matching by abstracting away from the
lexicon. It enables entirely novel kinds of queries, as well. Consider that the Latin word locus,
literally, ‘a place’, can be used metaphorically in the sense of ‘an idea’. The same metaphor can
be detected in many other expressions where different kinds of mental operations (‘planning’,
‘agreeing’, ‘conceiving’) are conveyed figuratively by verbs of spatial motion (‘entering’,
‘coming to’, ‘approaching’). With existing tools, identifying such patterns of metaphorical
structure requires painstakingly searching the corpus for forms of words that signify spatial
motion, then culling these results for only those occurrences where the sense must be
figurative. By contrast, a tool that permits searching by word sense (i.e., ‘an idea’) and by
semantic field (‘mental phenomena’) would make identifying linguistic details like this
effortless. Even for users with limited knowledge of the ancient languages, this functionality can
provide insight into how concepts were understood in historical societies.
The kinds of queries enabled by our semantic search engine can also inform literary
interpretation. Take Vergil’s famous line, *mihi frigidus horror / membra quatit*, ‘Cold fear shakes
my limbs’ (*Aen*. 3.29‒30). A simple collocation search suggests this expression is a product of
Vergil’s poetic imagination: the pairing *frigidus horror* occurs only twice elsewhere in Latin
literature, once in a passage of Lucretius that probably served as a model for the Vergilian
phrase, and again in a verse of Ovid that was in turn likely influenced by it. Apparent fodder for
intertextual studies of Latin epic poetry, or for tracing out relationships of imitation and allusion
between Latin authors. Yet a search for words denoting ‘fear’ in conjunction with words
signifying ‘cold’ or ‘shivering’ reveals that representations of fear in these terms are in fact
quite regular across different authors, genres, and time periods. In other words, what appears
to be an instance of creative literary expression may instead be a manifestation of Latin
speakers’ entirely regular conceptualisation of fear. Whereas traditional methods of corpus
search tend to obscure this kind of fact, our software could help distinguish what is creative
about texts from what is conventional, and thus highlight where authors are actually engaged
in novel meaning-making.
Along with meanings, users will also be able to specify bare morphological and syntactic
features as part of search parameters, enabling complex queries like ‘any adjective in the
semantic field of “racial, ethnic, and national groups” when it precedes its noun in the dative
case’. We believe this ability to search texts for grammatical configurations independent of any
particular lexical instantiation could have a significant impact on the study of ancient languages,
which abound in structurally intricate – and very often seemingly functionally equivalent –
syntactic constructions. In particular, it could propel the growing field of cognitive classical
linguistics, which treats constructions as having meanings in and of themselves, distinct from the
meanings of the words of which they are composed, as well as classical linguistics more
generally, where focus has recently shifted to the interface of semantics and morpho-syntactic
structure. The search engine could also aid teachers and their students by facilitating
exemplification of syntactical rules based on the actual usage of ancient authors.
We have identified two main and largely separate challenges to implementing semantic and
syntactic search. The first will be to implement meaning-based queries. Today’s electronic
databanks of Latin texts – including those parsed corpora which include morpho-syntactic
annotations – contain basically no semantic information. Our solution will be to integrate the
data of the Latin WordNet, a lexical knowledge-base for this language created as part of the
Fondazione Bruno Kessler’s MultiWordNet Project, into existing treebanks. In a WordNet, words
or phrases are assigned to one or more ‘synsets’, corresponding to the different senses they
possess. A synset thus represents a grouping of semantically related expressions, or, from a
different angle, an atomized meaning-component in the language. The words of languages
within the MultiWordNet are keyed to over 100,000 distinct synsets from English and can be
assigned language-specific synsets glossed in English. As the Latin WordNet presently contains
only a portion of the Latin vocabulary, however, a crucial step in our effort will be to expand it
by about 30,000 lemmas, adding morphological information as well as coding a dense network
of lexical and semantic relations into the database. In a future stage, the WordNet will be
rearchitected to distinguish metonymic and metaphorical from literal senses of words, as well
as to be aware of large-scale mappings that structure figurative usage supralexically.
Basing our engine’s semantic model on the MultiWordNet offers key advantages. By preprocessing
and tagging texts within our corpora with each lemma’s synsets, searching for
meanings becomes highly efficient. As the Latin WordNet will include information about lexical
and semantic relations, users will also be able to conduct searches based on, for instance,
antonymy or etymological derivation (‘the word mitto not in the sense “pour”’, ‘any word
derived from the verb *fari*’). Furthermore, because word senses are defined according to a
common pool of synsets, theoretically users will be able to enter queries in any language for
which a WordNet is available. Users can also specify semantic fields as search parameters,
enabling queries over sets of terms grouped by conceptual domain (e.g., ‘economy’, ‘military’,
‘agriculture’). Finally, the inclusion of multiple synset assignments within the annotation
structure, together with a mechanism of moderated crowd-sourced ‘up-voting’ whereby users
can indicate informed judgments about senses in context, will help avoid predetermining the
meaning of ancient texts, and builds into the engine itself an awareness that literary texts are
generally open to having various interpretations.
The second challenge is to determine the correct syntactic structure of texts and to devise
an annotation schema at an appropriate level of linguistic description. Our engine, built on the
open-source ANNIS platform, will aggregate curated and verified morpho-syntactic data in the
form of treebanks, drawing primarily on the database of rich text annotations in the Greek and
Latin Dependency Treebank created by the Perseus Project at Tufts University, with additions
from the Index Thomisticus and the PROIEL project providing coverage of different authors,
genres, and time periods. The treebanks in these repositories have undergone manual review
and correction of the tagged syntactic information to ensure a high degree of accuracy.
However, because they encode linguistic information in different ways and with differing
degrees of granularity, our task will be to devise a high-level model that can integrate treebanks
based on potentially very different grammars, along with the semantic data of the WordNet.
