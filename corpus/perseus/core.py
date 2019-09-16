import codecs
import json
from pathlib import Path

import settings
from utils import nrange


def get(hit, meta, fragment):
    filename = Path(hit['filename']).name
    with codecs.open(
        settings.ROOT_DIR + f'/corpus/perseus/text/{filename}', 'r', 'utf8'
    ) as fp:
        doc = json.load(fp)

    divs = meta['meta'].split('-')

    # Reference and hlite values
    ref_start = ', '.join(
        [f"{item}: {meta['start'][item]}" for item in meta['start'] if item in divs]
    )
    ref_end = ', '.join(
        [f"{item}: {meta['end'][item]}" for item in meta['end'] if item in divs]
    )
    reference = '-'.join([ref_start, ref_end]) if ref_end != ref_start else ref_start

    # Collect text and context
    start = [
        int(v)
        for k, v in meta['start'].items()
        if k in divs
    ]
    end = [
        int(v)
        for k, v in meta['end'].items()
        if k in divs
    ]

    pre_start = start[:-1] + [(start[-1] - settings.LINES_OF_CONTEXT),]
    pre_end = start[:-1] + [(start[-1] - 1),]
    pre = []
    for ref in nrange(pre_start, pre_end):
        content = doc['text']
        for div in ref:
            try:
                content = content[str(div - 1)]
            except KeyError:
                content = None
                break
        if content:
            pre.append(f"<pre>{content}</pre>")

    match = []
    hlites = sorted(set([tuple(hlite) for hlite in meta['hlites']]))
    for ref in nrange(start, end):
        if 0 in ref: continue  # FIXME: nrange yields 0-numbered references
        content = doc['text']

        i = 0
        for div in ref:
            try:
                content = content[str(div - 1)]
            except KeyError:
                break
            else:
                i += 1
        # Skip incomplete refs (e.g., missing lines)
        if i < len(ref):
            continue

        refs = list(zip(divs, ref))
        start_refs = [(k, int(meta['start'][k])) for k in divs]

        if refs >= start_refs:
            content = [
                f"<em>{t}</em>"
                if tuple([str(r) for r in ref] + [str(i),]) in hlites
                else t
                for i, t in enumerate(content.split())
            ]
        else:
            content = [t for t in content.split()]
        match.append(f"<match>{' '.join(content)}</match>")

    post_start = end[:-1] + [(end[-1] + 1), ]
    post_end = end[:-1] + [(end[-1] + settings.LINES_OF_CONTEXT), ]
    post = []
    for ref in nrange(post_start, post_end):
        content = doc['text']
        for div in ref:
            try:
                content = content[str(div - 1)]
            except KeyError:
                content = None
                break
        if content:
            post.append(f"<post>{content}</post>")

    if 'poem' in divs or (len(divs) == 2 and divs[-1] in ['line', 'verse']):
        joiner = '\n\n'
    else:
        joiner = ' '
    parts = pre + match + post
    text = f'{joiner}'.join(parts)
    urn = hit.get('urn', None)

    return urn, reference, text


index = {0: {'author': 'Ammianus Marcellinus',
             'work': {'title': 'Rerum Gestarum',
                      'meta': 'book-chapter-section',
                      'urn': 'urn:cts:latinLit:stoa0023.stoa001.perseus-lat1-simple'}},
         1: {'author': 'Apuleius',
             'work': {'title': 'Apologia',
                      'meta': 'section',
                      'urn': 'urn:cts:latinLit:phi1212.phi001.perseus-lat1-simple'}},
         2: {'author': 'Apuleius',
             'work': {'title': 'Florida',
                      'meta': 'section',
                      'urn': 'urn:cts:latinLit:phi1212.phi003.perseus-lat1-simple'}},
         3: {'author': 'Apuleius',
             'work': {'title': 'Metamorphoses',
                      'meta': 'book-chapteer',
                      'urn': 'urn:cts:latinLit:phi1212.phi002.perseus-lat1-simple'}},
         4: {'author': 'Ausonius, Decimus Magnus',
             'work': {'title': 'Bissula',
                      'meta': 'poem-line',
                      'urn': 'urn:cts:latinLit:stoa0045.stoa001.perseus-lat2-simple'}},
         5: {'author': 'Ausonius, Decimus Magnus',
             'work': {'title': 'Caesares',
                      'meta': 'poem-line',
                      'urn': 'urn:cts:latinLit:stoa0045.stoa002.perseus-lat2-simple'}},
         6: {'author': 'Ausonius, Decimus Magnus',
             'work': {'title': 'Commemoratio Professorum Burdigalensium',
                      'meta': 'poem-line',
                      'urn': 'urn:cts:latinLit:stoa0045.stoa004.perseus-lat2-simple'}},
         7: {'author': 'Ausonius, Decimus Magnus',
             'work': {'title': 'De Herediolo',
                      'meta': 'line',
                      'urn': 'urn:cts:latinLit:stoa0045.stoa006.perseus-lat2-simple'}},
         8: {'author': 'Ausonius, Decimus Magnus',
             'work': {'title': 'Eclogarum Liber',
                      'meta': 'poem-line',
                      'urn': 'urn:cts:latinLit:stoa0045.stoa007.perseus-lat2-simple'}},
         9: {'author': 'Ausonius, Decimus Magnus',
             'work': {'title': 'Ephemeris',
                      'meta': 'poem-line',
                      'urn': 'urn:cts:latinLit:stoa0045.stoa008.perseus-lat2-simple'}},
         10: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Epicedion in Patrem',
                       'meta': 'line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa009.perseus-lat2-simple'}},
         11: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Epigrammaton Liber',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa010.perseus-lat2-simple'}},
         12: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Epistulae',
                       'meta': 'letter-line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa011.perseus-lat2-simple'}},
         13: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Epitaphia',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa012.perseus-lat2-simple'}},
         14: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Genethliacon ad Ausonium Nepotem',
                       'meta': 'line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa013.perseus-lat2-simple'}},
         15: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Gratiarum Actio',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa014.perseus-lat2-simple'}},
         16: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Griphus Ternarii Numeri',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa015.perseus-lat2-simple'}},
         17: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Liber Protrepticus ad Nepotem',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa016.perseus-lat2-simple'}},
         18: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Mosella',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa019.perseus-lat2-simple'}},
         19: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Oratio Versibus Rhopalicis',
                       'meta': 'line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa020.perseus-lat2-simple'}},
         20: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Ordo Urbium Nobilium',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa021.perseus-lat2-simple'}},
         21: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Parentalia',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa022.perseus-lat2-simple'}},
         22: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Praefatiunculae',
                       'meta': 'book-line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa025.perseus-lat2-simple'}},
         23: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Precationes',
                       'meta': 'book-line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa026.perseus-lat2-simple'}},
         24: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Technopaegnion',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa028.perseus-lat2-simple'}},
         25: {'author': 'Ausonius, Decimus Magnus',
              'work': {'title': 'Versus Paschales Prosodic',
                       'meta': 'line',
                       'urn': 'urn:cts:latinLit:stoa0045.stoa027.perseus-lat2-simple'}},
         26: {'author': 'Boethius D. 524',
              'work': {'title': 'De consolatione philosophiae',
                       'meta': 'book-section',
                       'urn': 'urn:cts:latinLit:stoa0058.stoa001.perseus-lat2-simple'}},
         27: {'author': 'Boethius D. 524',
              'work': {'title': 'De Fide Catholica',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:stoa0058.stoa006.perseus-lat1-simple'}},
         28: {'author': 'Boethius D. 524',
              'work': {'title': 'Liber De Persona et Duabus Naturis Contra Eutychen Et Nestorium',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:stoa0058.stoa023.perseus-lat1-simple'}},
         29: {'author': 'Boethius D. 524',
              'work': {'title': 'Quomodo Substantiae in Eo Quod Sint Bonae Sint Cum Non Sint Substanialia Bona',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:stoa0058.stoa003.perseus-lat1-simple'}},
         30: {'author': 'Boethius D. 524',
              'work': {'title': 'Quomodo Trinitas Unus Deus Ac Non Tres Dii (De Trinitate)',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:stoa0058.stoa025.perseus-lat1-simple'}},
         31: {'author': 'Boethius D. 524',
              'work': {
                  'title': 'Utrum Pater Et Filius Ac Spiritus Sanctus De Divinitate Substantialiter Praedicentur Liber',
                  'meta': 'section',
                  'urn': 'urn:cts:latinLit:stoa0058.stoa028.perseus-lat1-simple'}},
         32: {'author': 'Caesar, Julius',
              'work': {'title': 'Gallic War',
                       'meta': 'Book-Chapter-Section',
                       'urn': 'urn:cts:latinLit:phi0448.phi001.perseus-lat2-simple'}},
         33: {'author': 'Celsus, Aulus Cornelius',
              'work': {'title': 'De Medicina',
                       'meta': 'book-chapter',
                       'urn': 'urn:cts:latinLit:phi0836.phi002.perseus-lat5-simple'}},
         34: {'author': 'Cicero',
              'work': {'title': 'Academica',
                       'meta': 'book-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi045.perseus-lat1-simple'}},
         35: {'author': 'Cicero',
              'work': {'title': 'Orationes de Lege Agraria',
                       'meta': 'chapter-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi011.perseus-lat2-simple'}},
         36: {'author': 'Cicero',
              'work': {'title': 'Brutus',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi039.perseus-lat1-simple'}},
         37: {'author': 'Cicero',
              'work': {'title': 'De Amicitia',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi052.perseus-lat1-simple'}},
         38: {'author': 'Cicero',
              'work': {'title': 'De Divinatione',
                       'meta': 'book-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi053.perseus-lat1-simple'}},
         39: {'author': 'Cicero',
              'work': {'title': 'De Fato',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi054.perseus-lat1-simple'}},
         40: {'author': 'Cicero',
              'work': {'title': 'de Finibus Bonorum et Malorum',
                       'meta': 'book-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi048.perseus-lat1-simple'}},
         41: {'author': 'Cicero',
              'work': {'title': 'De Inventione',
                       'meta': 'chapter-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi036.perseus-lat1-simple'}},
         42: {'author': 'Cicero',
              'work': {'title': 'de Natura Deorum',
                       'meta': 'chapter-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi050.perseus-lat1-simple'}},
         43: {'author': 'Cicero',
              'work': {'title': 'De Officiis',
                       'meta': 'book-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi055.perseus-lat1-simple'}},
         44: {'author': 'Cicero',
              'work': {'title': 'De Optimo Genere Oratorum',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi041.perseus-lat1-simple'}},
         45: {'author': 'Cicero',
              'work': {'title': 'De Republica',
                       'meta': 'book-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi043.perseus-lat1-simple'}},
         46: {'author': 'Cicero',
              'work': {'title': 'De Senectute',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi051.perseus-lat1-simple'}},
         47: {'author': 'Cicero',
              'work': {'title': 'In Caecilium',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi004.perseus-lat2-simple'}},
         48: {'author': 'Cicero',
              'work': {'title': 'Pro Archia',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi016.perseus-lat2-simple'}},
         49: {'author': 'Cicero',
              'work': {'title': 'For Marcus Caelius',
                       'meta': 'unknown',
                       'urn': 'urn:cts:latinLit:phi0474.phi024.perseus-lat2-simple'}},
         50: {'author': 'Cicero',
              'work': {'title': 'Pro Fonteio',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi007.perseus-lat2-simple'}},
         51: {'author': 'Cicero',
              'work': {'title': 'Pro P. Quinctio',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi001.perseus-lat2-simple'}},
         52: {'author': 'Cicero',
              'work': {'title': 'Pro Roscio comoedo',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi003.perseus-lat2-simple'}},
         53: {'author': 'Cicero',
              'work': {'title': 'Pro S. Roscio Amerino',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi002.perseus-lat2-simple'}},
         54: {'author': 'Cicero',
              'work': {'title': 'Pro Sulla',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi015.perseus-lat2-simple'}},
         55: {'author': 'Cicero',
              'work': {'title': 'In Catilinam',
                       'meta': 'chapter-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi013.perseus-lat2-simple'}},
         56: {'author': 'Cicero',
              'work': {'title': 'Pro Cluentio',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi010.perseus-lat2-simple'}},
         57: {'author': 'Cicero',
              'work': {'title': 'Pro C. Rabiro perduellionis reo',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi012.perseus-lat2-simple'}},
         58: {'author': 'Cicero',
              'work': {'title': 'Pro Murena',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi014.perseus-lat2-simple'}},
         59: {'author': 'Cicero',
              'work': {'title': 'Pro Flacco',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi017.perseus-lat2-simple'}},
         60: {'author': 'Cicero',
              'work': {'title': 'Post reditum in senatu',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi019.perseus-lat2-simple'}},
         61: {'author': 'Cicero',
              'work': {'title': 'Letters to Atticus',
                       'meta': 'book-letter-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi057.perseus-lat1-simple'}},
         62: {'author': 'Cicero',
              'work': {'title': 'Letters to Brutus',
                       'meta': 'book-letter-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi059.perseus-lat1-simple'}},
         63: {'author': 'Cicero',
              'work': {'title': 'Letters to his brother Quintus',
                       'meta': 'book-letter-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi058.perseus-lat1-simple'}},
         64: {'author': 'Cicero',
              'work': {'title': 'Letters to his Friends',
                       'meta': 'book-letter-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi056.perseus-lat1-simple'}},
         65: {'author': 'Cicero',
              'work': {'title': 'Lucullus',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi046.perseus-lat1-simple'}},
         66: {'author': 'Cicero',
              'work': {'title': 'Pro A. Caecina',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi008.perseus-lat2-simple'}},
         67: {'author': 'Cicero',
              'work': {'title': 'Pro Tullio',
                       'meta': 'chapter',
                       'urn': 'urn:cts:latinLit:phi0474.phi006.perseus-lat2-simple'}},
         68: {'author': 'Cicero',
              'work': {'title': 'On Oratory',
                       'meta': 'chapter-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi037.perseus-lat1-simple'}},
         69: {'author': 'Cicero',
              'work': {'title': 'Pro lege manilia',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi009.perseus-lat2-simple'}},
         70: {'author': 'Cicero',
              'work': {'title': 'In Verrem',
                       'meta': 'actio-book-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi005.perseus-lat2-simple'}},
         71: {'author': 'Cicero',
              'work': {'title': 'Orator',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi040.perseus-lat1-simple'}},
         72: {'author': 'Cicero',
              'work': {'title': 'Paradoxa Stoicorum',
                       'meta': 'book-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi047.perseus-lat1-simple'}},
         73: {'author': 'Cicero',
              'work': {'title': 'Partitiones Oratoriae',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi038.perseus-lat1-simple'}},
         74: {'author': 'Cicero',
              'work': {'title': 'Timaeus',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi072.perseus-lat1-simple'}},
         75: {'author': 'Cicero',
              'work': {'title': 'Post reditum ad populum',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi018.perseus-lat2-simple'}},
         76: {'author': 'Cicero',
              'work': {'title': 'Topica',
                       'meta': 'section',
                       'urn': 'urn:cts:latinLit:phi0474.phi042.perseus-lat1-simple'}},
         77: {'author': 'Cicero',
              'work': {'title': 'Tusculanae Disputationes',
                       'meta': 'chapter-section',
                       'urn': 'urn:cts:latinLit:phi0474.phi049.perseus-lat1-simple'}},
         78: {'author': 'Claudianus, Claudius',
              'work': {'title': 'Carminum minorum corpusculum',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa001.perseus-lat2-simple'}},
         79: {'author': 'Claudianus, Claudius',
              'work': {'title': 'de bello Gildonico',
                       'meta': 'line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa002.perseus-lat2-simple'}},
         80: {'author': 'Claudianus, Claudius',
              'work': {'title': 'de Bello Gothico',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa003.perseus-lat2-simple'}},
         81: {'author': 'Claudianus, Claudius',
              'work': {'title': 'de consulatu Stilichonis',
                       'meta': 'book-line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa004.perseus-lat2-simple'}},
         82: {'author': 'Claudianus, Claudius',
              'work': {'title': 'de raptu Proserpinae',
                       'meta': 'book-poem-line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa005.perseus-lat2-simple'}},
         83: {'author': 'Claudianus, Claudius',
              'work': {'title': 'Epithalamium de nuptiis Honorii Augusti',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa006.perseus-lat2-simple'}},
         84: {'author': 'Claudianus, Claudius',
              'work': {'title': 'Fescinnina de nuptiis Honorii Augusti',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa007.perseus-lat2-simple'}},
         85: {'author': 'Claudianus, Claudius',
              'work': {'title': 'In Eutropium',
                       'meta': 'book-line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa008.perseus-lat2-simple'}},
         86: {'author': 'Claudianus, Claudius',
              'work': {'title': 'In Rufinum',
                       'meta': 'book-poem-line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa009.perseus-lat2-simple'}},
         87: {'author': 'Claudianus, Claudius',
              'work': {'title': 'Panegyricus de quarto consulatu Honorii Augusti',
                       'meta': 'line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa011.perseus-lat2-simple'}},
         88: {'author': 'Claudianus, Claudius',
              'work': {'title': 'Panegyricus de sexto consulatu Honorii Augusti',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa012.perseus-lat2-simple'}},
         89: {'author': 'Claudianus, Claudius',
              'work': {'title': 'Panegyricus de tertio consulatu Honorii Augusti',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa010.perseus-lat2-simple'}},
         90: {'author': 'Claudianus, Claudius',
              'work': {'title': 'Panegyricus dictus Manlio Theodoro consuli',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa013.perseus-lat2-simple'}},
         91: {'author': 'Claudianus, Claudius',
              'work': {'title': 'Panegyricus dictus Probino et Olybrio consulibus',
                       'meta': 'line',
                       'urn': 'urn:cts:latinLit:stoa0089.stoa014.perseus-lat2-simple'}},
         92: {'author': 'Columella, Lucius Junius Moderatus',
              'work': {'title': 'Res Rustica',
                       'meta': 'book-chapter-section',
                       'urn': 'urn:cts:latinLit:phi0845.phi002.perseus-lat3-simple'}},
         93: {'author': 'Curtius Rufus, Quintus',
              'work': {'title': 'Historiarum Alexandri Magni',
                       'meta': 'book-chapter-section',
                       'urn': 'urn:cts:latinLit:phi0860.phi001.perseus-lat2-simple'}},
         94: {'author': 'Florus, Lucius Annaeus',
              'work': {'title': 'Epitome Rerum Romanorum',
                       'meta': 'book-topic-chapter-section',
                       'urn': 'urn:cts:latinLit:phi1242.phi001.perseus-lat1-simple'}},
         95: {'author': 'Gellius, Aulus',
              'work': {'title': 'Noctes Atticae',
                       'meta': 'book-chapter-section',
                       'urn': 'urn:cts:latinLit:phi1254.phi001.perseus-lat1-simple'}},
         96: {'author': 'Horace',
              'work': {'title': 'Ars Poetica',
                       'meta': 'line',
                       'urn': 'urn:cts:latinLit:phi0893.phi006.perseus-lat2-simple'}},
         97: {'author': 'Horace',
              'work': {'title': 'Carmen Saeculare',
                       'meta': 'line',
                       'urn': 'urn:cts:latinLit:phi0893.phi002.perseus-lat2-simple'}},
         98: {'author': 'Horace',
              'work': {'title': 'Epistulae',
                       'meta': 'book-poem-line',
                       'urn': 'urn:cts:latinLit:phi0893.phi005.perseus-lat2-simple'}},
         99: {'author': 'Horace',
              'work': {'title': 'Epodi',
                       'meta': 'poem-line',
                       'urn': 'urn:cts:latinLit:phi0893.phi003.perseus-lat2-simple'}},
         100: {'author': 'Horace',
               'work': {'title': 'Odes',
                        'meta': 'book-poem-line',
                        'urn': 'urn:cts:latinLit:phi0893.phi001.perseus-lat2-simple'}},
         101: {'author': 'Horace',
               'work': {'title': 'Satires',
                        'meta': 'book-poem-line',
                        'urn': 'urn:cts:latinLit:phi0893.phi004.perseus-lat2-simple'}},
         102: {'author': 'Jerome Saint D. 419 Or 20',
               'work': {'title': 'Epistolae',
                        'meta': 'letter-section',
                        'urn': 'urn:cts:latinLit:stoa0162.stoa004.perseus-lat2-simple'}},
         103: {'author': 'Juvenal',
               'work': {'title': 'Satires',
                        'meta': 'book-poem-line',
                        'urn': 'urn:cts:latinLit:phi1276.phi001.perseus-lat2-simple'}},
         104: {'author': 'Lucan',
               'work': {'title': 'Civil War',
                        'meta': 'book-line',
                        'urn': 'urn:cts:latinLit:phi0917.phi001.perseus-lat2-simple'}},
         105: {'author': 'Lucretius',
               'work': {'title': 'De Rerum Natura',
                        'meta': 'book-line',
                        'urn': 'urn:cts:latinLit:phi0550.phi001.perseus-lat1-simple'}},
         106: {'author': 'Martial',
               'work': {'title': 'Epigrammata',
                        'meta': 'book-poem-line',
                        'urn': 'urn:cts:latinLit:phi1294.phi002.perseus-lat2-simple'}},
         107: {'author': 'Minucius Felix, Marcus',
               'work': {'title': 'Octavius',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0203.stoa001.perseus-lat2-simple'}},
         108: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Agesilaus',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo017.perseus-lat2-simple'}},
         109: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Alcibiades',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo007.perseus-lat2-simple'}},
         110: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Aristides',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo003.perseus-lat2-simple'}},
         111: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Atticus',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo025.perseus-lat2-simple'}},
         112: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Cato',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo024.perseus-lat2-simple'}},
         113: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Chabrias',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo012.perseus-lat2-simple'}},
         114: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Cimon',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo005.perseus-lat2-simple'}},
         115: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Conon',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo009.perseus-lat2-simple'}},
         116: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Datames',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo014.perseus-lat2-simple'}},
         117: {'author': 'Nepos, Cornelius',
               'work': {'title': 'De Regibus',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo021.perseus-lat2-simple'}},
         118: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Dion',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo010.perseus-lat2-simple'}},
         119: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Epaminondas',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo015.perseus-lat2-simple'}},
         120: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Eumenes',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo018.perseus-lat2-simple'}},
         121: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Hamilcar',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo022.perseus-lat2-simple'}},
         122: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Hannibal',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo023.perseus-lat2-simple'}},
         123: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Iphicrates',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo011.perseus-lat2-simple'}},
         124: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Lysander',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo006.perseus-lat2-simple'}},
         125: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Miltiades',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo001.perseus-lat2-simple'}},
         126: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Pausanias',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo004.perseus-lat2-simple'}},
         127: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Pelopidas',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo016.perseus-lat2-simple'}},
         128: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Phocion',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo019.perseus-lat2-simple'}},
         129: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Themistocles',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo002.perseus-lat2-simple'}},
         130: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Thrasybulus',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo008.perseus-lat2-simple'}},
         131: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Timoleon',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo020.perseus-lat2-simple'}},
         132: {'author': 'Nepos, Cornelius',
               'work': {'title': 'Timotheus',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi0588.abo013.perseus-lat2-simple'}},
         133: {'author': 'Ovid',
               'work': {'title': 'Amores',
                        'meta': 'book-poem-line',
                        'urn': 'urn:cts:latinLit:phi0959.phi001.perseus-lat2-simple'}},
         134: {'author': 'Ovid',
               'work': {'title': 'Medicamina faciei femineae',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0959.phi003.perseus-lat2-simple'}},
         135: {'author': 'Ovid',
               'work': {'title': 'Ars Amatoria',
                        'meta': 'book-line',
                        'urn': 'urn:cts:latinLit:phi0959.phi004.perseus-lat2-simple'}},
         136: {'author': 'Ovid',
               'work': {'title': 'Fasti',
                        'meta': 'book-line',
                        'urn': 'urn:cts:latinLit:phi0959.phi007.perseus-lat2-simple'}},
         137: {'author': 'Ovid',
               'work': {'title': 'Epistulae',
                        'meta': 'poem-line',
                        'urn': 'urn:cts:latinLit:phi0959.phi002.perseus-lat2-simple'}},
         138: {'author': 'Ovid',
               'work': {'title': 'Ibis',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0959.phi010.perseus-lat2-simple'}},
         139: {'author': 'Ovid',
               'work': {'title': 'Ex Ponto',
                        'meta': 'book-poem-line',
                        'urn': 'urn:cts:latinLit:phi0959.phi009.perseus-lat2-simple'}},
         140: {'author': 'Ovid',
               'work': {'title': 'Metamorphoses',
                        'meta': 'book-line',
                        'urn': 'urn:cts:latinLit:phi0959.phi006.perseus-lat2-simple'}},
         141: {'author': 'Ovid',
               'work': {'title': 'Remedia amoris',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0959.phi005.perseus-lat2-simple'}},
         142: {'author': 'Ovid',
               'work': {'title': 'Tristia',
                        'meta': 'book-poem-line',
                        'urn': 'urn:cts:latinLit:phi0959.phi008.perseus-lat2-simple'}},
         143: {'author': 'Paris, Julius',
               'work': {'title': 'Facta et Dicta Memorabilia',
                        'meta': 'book-chapter-section',
                        'urn': 'urn:cts:latinLit:phi1038.phi001.perseus-lat1-simple'}},
         144: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Asinaria',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi002.perseus-lat2-simple'}},
         145: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Aulularia',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi003.perseus-lat2-simple'}},
         146: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Bacchides',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi004.perseus-lat2-simple'}},
         147: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Captivi',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi005.perseus-lat2-simple'}},
         148: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Casina',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi006.perseus-lat2-simple'}},
         149: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Curculio',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi008.perseus-lat2-simple'}},
         150: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Epidicus',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi009.perseus-lat2-simple'}},
         151: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Menaechmi',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi010.perseus-lat2-simple'}},
         152: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Mercator',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi011.perseus-lat2-simple'}},
         153: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Miles Gloriosus',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi012.perseus-lat2-simple'}},
         154: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Mostellaria',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi013.perseus-lat2-simple'}},
         155: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Persa',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi014.perseus-lat2-simple'}},
         156: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Poenulus',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi015.perseus-lat2-simple'}},
         157: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Rudens',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi017.perseus-lat2-simple'}},
         158: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Stichus',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi018.perseus-lat2-simple'}},
         159: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Trinummus',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi019.perseus-lat2-simple'}},
         160: {'author': 'Plautus, Titus Maccius',
               'work': {'title': 'Truculentus',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0119.phi020.perseus-lat2-simple'}},
         161: {'author': 'Pliny, The Elder',
               'work': {'title': 'Naturalis Historia',
                        'meta': 'book-chapter',
                        'urn': 'urn:cts:latinLit:phi0978.phi001.perseus-lat2-simple'}},
         162: {'author': 'Pliny, The Younger',
               'work': {'title': 'Epistulae',
                        'meta': 'book-letter-section',
                        'urn': 'urn:cts:latinLit:phi1318.phi001.perseus-lat1-simple'}},
         163: {'author': 'Propertius, Sextus',
               'work': {'title': 'Elegies',
                        'meta': 'book-poem-line',
                        'urn': 'urn:cts:latinLit:phi0620.phi001.perseus-lat3-simple'}},
         164: {'author': 'Prudentius B. 348',
               'work': {'title': 'Apotheosis',
                        'meta': 'section-line',
                        'urn': 'urn:cts:latinLit:stoa0238.stoa005.perseus-lat2-simple'}},
         165: {'author': 'Prudentius B. 348',
               'work': {'title': 'Cathemerina',
                        'meta': 'poem-line',
                        'urn': 'urn:cts:latinLit:stoa0238.stoa004.perseus-lat2-simple'}},
         166: {'author': 'Prudentius B. 348',
               'work': {'title': 'Contra Orationem Symmachia',
                        'meta': 'book-section-line',
                        'urn': 'urn:cts:latinLit:stoa0238.stoa007.perseus-lat2-simple'}},
         167: {'author': 'Prudentius B. 348',
               'work': {'title': 'Dittochaeon',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:stoa0238.stoa008.perseus-lat2-simple'}},
         168: {'author': 'Prudentius B. 348',
               'work': {'title': 'Epilogus',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:stoa0238.stoa009.perseus-lat2-simple'}},
         169: {'author': 'Prudentius B. 348',
               'work': {'title': 'Hamartigenia',
                        'meta': 'section-line',
                        'urn': 'urn:cts:latinLit:stoa0238.stoa006.perseus-lat2-simple'}},
         170: {'author': 'Prudentius B. 348',
               'work': {'title': 'Liber Peristephanon',
                        'meta': 'poem-line',
                        'urn': 'urn:cts:latinLit:stoa0238.stoa001.perseus-lat2-simple'}},
         171: {'author': 'Prudentius B. 348',
               'work': {'title': 'Praefetio',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:stoa0238.stoa003.perseus-lat2-simple'}},
         172: {'author': 'Prudentius B. 348',
               'work': {'title': 'Psychomachia',
                        'meta': 'section-line',
                        'urn': 'urn:cts:latinLit:stoa0238.stoa002.perseus-lat2-simple'}},
         173: {'author': 'Quintus Tullius Cicero',
               'work': {'title': 'Commentariolum Petitionis',
                        'meta': 'section',
                        'urn': 'urn:cts:latinLit:phi0478.phi003.perseus-lat2-simple'}},
         174: {'author': 'Sallust',
               'work': {'title': 'Bellum Iugurthinum',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi0631.phi002.perseus-lat4-simple'}},
         175: {'author': 'Sallust',
               'work': {'title': 'Catilinae Coniuratio',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi0631.phi001.perseus-lat3-simple'}},
         176: {'author': 'Sallust',
               'work': {'title': 'Historiae',
                        'meta': 'book-section',
                        'urn': 'urn:cts:latinLit:phi0631.phi003.perseus-lat2-simple'}},
         177: {'author': 'Seneca, Lucius Annaeus, 55 B.C.-Ca. 39 A.D',
               'work': {'title': 'Controversiae',
                        'meta': 'book-chapter-section',
                        'urn': 'urn:cts:latinLit:phi1014.phi001.perseus-lat1-simple'}},
         178: {'author': 'Seneca, Lucius Annaeus, 55 B.C.-Ca. 39 A.D',
               'work': {'title': 'Excerpta Controversiae',
                        'meta': 'book-chapter',
                        'urn': 'urn:cts:latinLit:phi1014.phi002.perseus-lat1-simple'}},
         179: {'author': 'Seneca, Lucius Annaeus, 55 B.C.-Ca. 39 A.D',
               'work': {'title': 'Fragmenta',
                        'meta': 'fragment',
                        'urn': 'urn:cts:latinLit:phi1014.phi004.perseus-lat1-simple'}},
         180: {'author': 'Seneca, Lucius Annaeus, 55 B.C.-Ca. 39 A.D',
               'work': {'title': 'Suasoriae',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi1014.phi003.perseus-lat1-simple'}},
         181: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'Agamemnon',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi1017.phi007.perseus-lat2-simple'}},
         182: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'Apocolocyntosis',
                        'meta': 'section',
                        'urn': 'urn:cts:latinLit:phi1017.phi011.perseus-lat2-simple'}},
         183: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'De Clementia',
                        'meta': 'book-chapter-section',
                        'urn': 'urn:cts:latinLit:phi1017.phi014.perseus-lat2-simple'}},
         184: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'Hercules Furens',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi1017.phi001.perseus-lat2-simple'}},
         185: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'Hercules Oetaeus',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi1017.phi009.perseus-lat2-simple'}},
         186: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'Medea',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi1017.phi004.perseus-lat2-simple'}},
         187: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'Octavia',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi1017.phi010.perseus-lat2-simple'}},
         188: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'Oedipus',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi1017.phi006.perseus-lat2-simple'}},
         189: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'Phaedra',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi1017.phi005.perseus-lat2-simple'}},
         190: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'Phoenissae',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi1017.phi003.perseus-lat2-simple'}},
         191: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'Thyestes',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi1017.phi008.perseus-lat2-simple'}},
         192: {'author': 'Seneca, Lucius Annaeus (Plays)',
               'work': {'title': 'Troades Furens',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi1017.phi002.perseus-lat2-simple'}},
         193: {'author': 'Seneca, Lucius Annaeus',
               'work': {'title': 'de Brevitate Vitae',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0255.stoa004.perseus-lat2-simple'}},
         194: {'author': 'Seneca, Lucius Annaeus',
               'work': {'title': 'de consolatione ad Helviam',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0255.stoa006.perseus-lat2-simple'}},
         195: {'author': 'Seneca, Lucius Annaeus',
               'work': {'title': 'de consolatione ad Marciam',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0255.stoa007.perseus-lat2-simple'}},
         196: {'author': 'Seneca, Lucius Annaeus',
               'work': {'title': 'de consolatione ad Polybium',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0255.stoa008.perseus-lat2-simple'}},
         197: {'author': 'Seneca, Lucius Annaeus',
               'work': {'title': 'de Constantia',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0255.stoa009.perseus-lat2-simple'}},
         198: {'author': 'Seneca, Lucius Annaeus',
               'work': {'title': 'de Ira',
                        'meta': 'book-chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0255.stoa010.perseus-lat2-simple'}},
         199: {'author': 'Seneca, Lucius Annaeus',
               'work': {'title': 'de Otio Sapientis',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0255.stoa011.perseus-lat2-simple'}},
         200: {'author': 'Seneca, Lucius Annaeus',
               'work': {'title': 'de Providentia',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0255.stoa012.perseus-lat2-simple'}},
         201: {'author': 'Seneca, Lucius Annaeus',
               'work': {'title': 'de Tranquilitate Animi',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0255.stoa013.perseus-lat2-simple'}},
         202: {'author': 'Seneca, Lucius Annaeus',
               'work': {'title': 'de Vita Beata',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0255.stoa014.perseus-lat2-simple'}},
         203: {'author': 'Silius Italicus, Tiberius Catius',
               'work': {'title': 'Punica',
                        'meta': 'book-line',
                        'urn': 'urn:cts:latinLit:phi1345.phi001.perseus-lat2-simple'}},
         204: {'author': 'Statius, P. Papinius (Publius Papinius)',
               'work': {'title': 'Achilleis',
                        'meta': 'book-line',
                        'urn': 'urn:cts:latinLit:phi1020.phi003.perseus-lat2-simple'}},
         205: {'author': 'Statius, P. Papinius (Publius Papinius)',
               'work': {'title': 'Silvae',
                        'meta': 'book-poem-line',
                        'urn': 'urn:cts:latinLit:phi1020.phi002.perseus-lat2-simple'}},
         206: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Caligula',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi1348.abo014.perseus-lat2-simple'}},
         207: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Divus Augustus',
                        'meta': 'unknown',
                        'urn': 'urn:cts:latinLit:phi1348.abo012.perseus-lat2-simple'}},
         208: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Divus Claudius',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi1348.abo015.perseus-lat2-simple'}},
         209: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Divus Julius',
                        'meta': 'unknown',
                        'urn': 'urn:cts:latinLit:phi1348.abo011.perseus-lat2-simple'}},
         210: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Divus Titus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi1348.abo021.perseus-lat2-simple'}},
         211: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Divus Vespasianus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi1348.abo020.perseus-lat2-simple'}},
         212: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Domitianus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi1348.abo022.perseus-lat2-simple'}},
         213: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Galba',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi1348.abo017.perseus-lat2-simple'}},
         214: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Nero',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi1348.abo016.perseus-lat2-simple'}},
         215: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Otho',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi1348.abo018.perseus-lat2-simple'}},
         216: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Tiberius',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi1348.abo013.perseus-lat2-simple'}},
         217: {'author': 'Suetonius Ca. 69-Ca. 122',
               'work': {'title': 'Vitellius',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi1348.abo019.perseus-lat2-simple'}},
         218: {'author': 'Tacitus, Cornelius',
               'work': {'title': 'Agricola',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi1351.phi001.perseus-lat1-simple'}},
         219: {'author': 'Tacitus, Cornelius',
               'work': {'title': 'Germania',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:phi1351.phi002.perseus-lat1-simple'}},
         220: {'author': 'Terence',
               'work': {'title': 'Andria',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0134.phi001.perseus-lat2-simple'}},
         221: {'author': 'Terence',
               'work': {'title': 'Phormio',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0134.phi004.perseus-lat2-simple'}},
         222: {'author': 'Terence',
               'work': {'title': 'The Brothers',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0134.phi006.perseus-lat2-simple'}},
         223: {'author': 'Terence',
               'work': {'title': 'The Eunuch',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0134.phi003.perseus-lat2-simple'}},
         224: {'author': 'Terence',
               'work': {'title': 'The Mother-in-Law',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0134.phi005.perseus-lat2-simple'}},
         225: {'author': 'Terence',
               'work': {'title': 'The Self-Tormenter',
                        'meta': 'line',
                        'urn': 'urn:cts:latinLit:phi0134.phi002.perseus-lat2-simple'}},
         226: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'Ad Martyras',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa001.opp-lat1-simple'}},
         227: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'Ad Nationes Libri Duo',
                        'meta': 'book-chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa002.opp-lat1-simple'}},
         228: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'Ad Scapulam',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa003.opp-lat1-simple'}},
         229: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'Ad Uxorem',
                        'meta': 'book-chapter',
                        'urn': 'urn:cts:latinLit:stoa0276.stoa002.opp-lat1-simple'}},
         230: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'Adversus Hermogenem',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa004.opp-lat1-simple'}},
         231: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'Adversus Judaeos Liber',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa005.opp-lat1-simple'}},
         232: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'Adversus Marcionem',
                        'meta': 'book-chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa006.opp-lat1-simple'}},
         233: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'Adversus Praxean',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa007.opp-lat1-simple'}},
         234: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'Adversus Valentinianos',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa008.opp-lat1-simple'}},
         235: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'Apologeticum',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa009.perseus-lat2-simple'}},
         236: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Anima',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa010.opp-lat1-simple'}},
         237: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Baptismo',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa011.opp-lat1-simple'}},
         238: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Carne Christi',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa012.opp-lat1-simple'}},
         239: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Carnis Resurrectione',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa026.opp-lat1-simple'}},
         240: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Corona',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa013.opp-lat1-simple'}},
         241: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Cultu Feminarum',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa014.opp-lat1-simple'}},
         242: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Exhortatione Castitatis Liber',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa015.opp-lat1-simple'}},
         243: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Fuga in Persecutione',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa016.opp-lat1-simple'}},
         244: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De idolatria',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa017.opp-lat1-simple'}},
         245: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De ieiunio adversus psychicos',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa018.opp-lat1-simple'}},
         246: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Monogamia',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa019.opp-lat1-simple'}},
         247: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Oratione',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa020.opp-lat1-simple'}},
         248: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Paenitentia',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa021.opp-lat1-simple'}},
         249: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Pallio',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa022.opp-lat1-simple'}},
         250: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Patientia',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa023.opp-lat1-simple'}},
         251: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Praescriptionibus Hereticorum',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa024.opp-lat1-simple'}},
         252: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Pudicitia',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa025.opp-lat1-simple'}},
         253: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Spectaculis',
                        'meta': 'chapter-section',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa027.perseus-lat2-simple'}},
         254: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Testimionio Animae',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa028.opp-lat1-simple'}},
         255: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'De Virginibus Velandis',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa029.opp-lat1-simple'}},
         256: {'author': 'Tertullian Ca. 160-Ca. 230',
               'work': {'title': 'Scorpiace',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:stoa0275.stoa030.opp-lat1-simple'}},
         257: {'author': 'Tibullus',
               'work': {'title': 'Elegiae',
                        'meta': 'poem-line',
                        'urn': 'urn:cts:latinLit:phi0660.phi003.perseus-lat2-simple'}},
         258: {'author': 'Valerius Flaccus, Gaius',
               'work': {'title': 'Argonautica',
                        'meta': 'book-line',
                        'urn': 'urn:cts:latinLit:phi1035.phi001.perseus-lat2-simple'}},
         259: {'author': 'Virgil',
               'work': {'title': 'Aeneid',
                        'meta': 'Book-line',
                        'urn': 'urn:cts:latinLit:phi0690.phi003.perseus-lat2-simple'}},
         260: {'author': 'Virgil',
               'work': {'title': 'Eclogues',
                        'meta': 'poem-line',
                        'urn': 'urn:cts:latinLit:phi0690.phi001.perseus-lat2-simple'}},
         261: {'author': 'Virgil',
               'work': {'title': 'Georgics',
                        'meta': 'poem-line',
                        'urn': 'urn:cts:latinLit:phi0690.phi002.perseus-lat2-simple'}},
         262: {'author': 'Vitruvius Pollio',
               'work': {'title': 'On Architecture',
                        'meta': 'book-chapter-section',
                        'urn': 'urn:cts:latinLit:phi1056.phi001.perseus-lat1-simple'}},
         263: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Alexander Severus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi018.perseus-lat2-simple'}},
         264: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Antoninus Caracalla',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi013.perseus-lat2-simple'}},
         265: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Antoninus Geta',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi014.perseus-lat2-simple'}},
         266: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Antoninus Heliogobalus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi017.perseus-lat2-simple'}},
         267: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Antoninus Pius',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi003.perseus-lat2-simple'}},
         268: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Avidius Casius',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi006.perseus-lat2-simple'}},
         269: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Carus et Carinus et Numerianus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi030.perseus-lat2-simple'}},
         270: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Clodinus Albinus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi012.perseus-lat2-simple'}},
         271: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Commodus Antoninus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi007.perseus-lat2-simple'}},
         272: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'De Vita Hadriani',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi001.perseus-lat2-simple'}},
         273: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Diadumenus Antoninus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi016.perseus-lat2-simple'}},
         274: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Didius Julianus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi009.perseus-lat2-simple'}},
         275: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Divus Aurelianus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi026.perseus-lat2-simple'}},
         276: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Divus Claudius',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi025.perseus-lat2-simple'}},
         277: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Firmus Saturninus, Proculus et Bonosus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi029.perseus-lat2-simple'}},
         278: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Gallieni Duo',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi023.perseus-lat2-simple'}},
         279: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Goridani Tres',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi020.perseus-lat2-simple'}},
         280: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Helius',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi002.perseus-lat2-simple'}},
         281: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Marcus Antoninus Philosophus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi004.perseus-lat2-simple'}},
         282: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Maximini Duo',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi019.perseus-lat2-simple'}},
         283: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Maximus et Balbinus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi021.perseus-lat2-simple'}},
         284: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Opilius Macrinus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi015.perseus-lat2-simple'}},
         285: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Pertinax',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi008.perseus-lat2-simple'}},
         286: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Pescennius Niger',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi011.perseus-lat2-simple'}},
         287: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Probus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi028.perseus-lat2-simple'}},
         288: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Severus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi010.perseus-lat2-simple'}},
         289: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Tacitus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi027.perseus-lat2-simple'}},
         290: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Tyranni Triginta',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi024.perseus-lat2-simple'}},
         291: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Valeriani Duo',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi022.perseus-lat2-simple'}},
         292: {'author': 'Vopiscus, Flavius Fl. 3./4. Jh',
               'work': {'title': 'Verus',
                        'meta': 'chapter',
                        'urn': 'urn:cts:latinLit:phi2331.phi005.perseus-lat2-simple'}}}

reverse_index = {'Ammianus Marcellinus': [{'title': 'Rerum Gestarum',
               'meta': 'book-chapter-section',
               'urn': 'urn:cts:latinLit:stoa0023.stoa001.perseus-lat1-simple',
               'docnum': 0}],
             'Apuleius': [{'title': 'Apologia',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi1212.phi001.perseus-lat1-simple',
               'docnum': 1},
              {'title': 'Florida',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi1212.phi003.perseus-lat1-simple',
               'docnum': 2},
              {'title': 'Metamorphoses',
               'meta': 'book-chapteer',
               'urn': 'urn:cts:latinLit:phi1212.phi002.perseus-lat1-simple',
               'docnum': 3}],
             'Ausonius, Decimus Magnus': [{'title': 'Bissula',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa001.perseus-lat2-simple',
               'docnum': 4},
              {'title': 'Caesares',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa002.perseus-lat2-simple',
               'docnum': 5},
              {'title': 'Commemoratio Professorum Burdigalensium',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa004.perseus-lat2-simple',
               'docnum': 6},
              {'title': 'De Herediolo',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa006.perseus-lat2-simple',
               'docnum': 7},
              {'title': 'Eclogarum Liber',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa007.perseus-lat2-simple',
               'docnum': 8},
              {'title': 'Ephemeris',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa008.perseus-lat2-simple',
               'docnum': 9},
              {'title': 'Epicedion in Patrem',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa009.perseus-lat2-simple',
               'docnum': 10},
              {'title': 'Epigrammaton Liber',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa010.perseus-lat2-simple',
               'docnum': 11},
              {'title': 'Epistulae',
               'meta': 'letter-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa011.perseus-lat2-simple',
               'docnum': 12},
              {'title': 'Epitaphia',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa012.perseus-lat2-simple',
               'docnum': 13},
              {'title': 'Genethliacon ad Ausonium Nepotem',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa013.perseus-lat2-simple',
               'docnum': 14},
              {'title': 'Gratiarum Actio',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:stoa0045.stoa014.perseus-lat2-simple',
               'docnum': 15},
              {'title': 'Griphus Ternarii Numeri',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa015.perseus-lat2-simple',
               'docnum': 16},
              {'title': 'Liber Protrepticus ad Nepotem',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa016.perseus-lat2-simple',
               'docnum': 17},
              {'title': 'Mosella',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa019.perseus-lat2-simple',
               'docnum': 18},
              {'title': 'Oratio Versibus Rhopalicis',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa020.perseus-lat2-simple',
               'docnum': 19},
              {'title': 'Ordo Urbium Nobilium',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa021.perseus-lat2-simple',
               'docnum': 20},
              {'title': 'Parentalia',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa022.perseus-lat2-simple',
               'docnum': 21},
              {'title': 'Praefatiunculae',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa025.perseus-lat2-simple',
               'docnum': 22},
              {'title': 'Precationes',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa026.perseus-lat2-simple',
               'docnum': 23},
              {'title': 'Technopaegnion',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa028.perseus-lat2-simple',
               'docnum': 24},
              {'title': 'Versus Paschales Prosodic',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:stoa0045.stoa027.perseus-lat2-simple',
               'docnum': 25}],
             'Boethius D. 524': [{'title': 'De consolatione philosophiae',
               'meta': 'book-section',
               'urn': 'urn:cts:latinLit:stoa0058.stoa001.perseus-lat2-simple',
               'docnum': 26},
              {'title': 'De Fide Catholica',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:stoa0058.stoa006.perseus-lat1-simple',
               'docnum': 27},
              {'title': 'Liber De Persona et Duabus Naturis Contra Eutychen Et Nestorium',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:stoa0058.stoa023.perseus-lat1-simple',
               'docnum': 28},
              {'title': 'Quomodo Substantiae in Eo Quod Sint Bonae Sint Cum Non Sint Substanialia Bona',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:stoa0058.stoa003.perseus-lat1-simple',
               'docnum': 29},
              {'title': 'Quomodo Trinitas Unus Deus Ac Non Tres Dii (De Trinitate)',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:stoa0058.stoa025.perseus-lat1-simple',
               'docnum': 30},
              {'title': 'Utrum Pater Et Filius Ac Spiritus Sanctus De Divinitate Substantialiter Praedicentur Liber',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:stoa0058.stoa028.perseus-lat1-simple',
               'docnum': 31}],
             'Caesar, Julius': [{'title': 'Gallic War',
               'meta': 'Book-Chapter-Section',
               'urn': 'urn:cts:latinLit:phi0448.phi001.perseus-lat2-simple',
               'docnum': 32}],
             'Celsus, Aulus Cornelius': [{'title': 'De Medicina',
               'meta': 'book-chapter',
               'urn': 'urn:cts:latinLit:phi0836.phi002.perseus-lat5-simple',
               'docnum': 33}],
             'Cicero': [{'title': 'Academica',
               'meta': 'book-section',
               'urn': 'urn:cts:latinLit:phi0474.phi045.perseus-lat1-simple',
               'docnum': 34},
              {'title': 'Orationes de Lege Agraria',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0474.phi011.perseus-lat2-simple',
               'docnum': 35},
              {'title': 'Brutus',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi039.perseus-lat1-simple',
               'docnum': 36},
              {'title': 'De Amicitia',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi052.perseus-lat1-simple',
               'docnum': 37},
              {'title': 'De Divinatione',
               'meta': 'book-section',
               'urn': 'urn:cts:latinLit:phi0474.phi053.perseus-lat1-simple',
               'docnum': 38},
              {'title': 'De Fato',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi054.perseus-lat1-simple',
               'docnum': 39},
              {'title': 'de Finibus Bonorum et Malorum',
               'meta': 'book-section',
               'urn': 'urn:cts:latinLit:phi0474.phi048.perseus-lat1-simple',
               'docnum': 40},
              {'title': 'De Inventione',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0474.phi036.perseus-lat1-simple',
               'docnum': 41},
              {'title': 'de Natura Deorum',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0474.phi050.perseus-lat1-simple',
               'docnum': 42},
              {'title': 'De Officiis',
               'meta': 'book-section',
               'urn': 'urn:cts:latinLit:phi0474.phi055.perseus-lat1-simple',
               'docnum': 43},
              {'title': 'De Optimo Genere Oratorum',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi041.perseus-lat1-simple',
               'docnum': 44},
              {'title': 'De Republica',
               'meta': 'book-section',
               'urn': 'urn:cts:latinLit:phi0474.phi043.perseus-lat1-simple',
               'docnum': 45},
              {'title': 'De Senectute',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi051.perseus-lat1-simple',
               'docnum': 46},
              {'title': 'In Caecilium',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi004.perseus-lat2-simple',
               'docnum': 47},
              {'title': 'Pro Archia',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi016.perseus-lat2-simple',
               'docnum': 48},
              {'title': 'For Marcus Caelius',
               'meta': 'unknown',
               'urn': 'urn:cts:latinLit:phi0474.phi024.perseus-lat2-simple',
               'docnum': 49},
              {'title': 'Pro Fonteio',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi007.perseus-lat2-simple',
               'docnum': 50},
              {'title': 'Pro P. Quinctio',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi001.perseus-lat2-simple',
               'docnum': 51},
              {'title': 'Pro Roscio comoedo',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi003.perseus-lat2-simple',
               'docnum': 52},
              {'title': 'Pro S. Roscio Amerino',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi002.perseus-lat2-simple',
               'docnum': 53},
              {'title': 'Pro Sulla',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi015.perseus-lat2-simple',
               'docnum': 54},
              {'title': 'In Catilinam',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0474.phi013.perseus-lat2-simple',
               'docnum': 55},
              {'title': 'Pro Cluentio',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi010.perseus-lat2-simple',
               'docnum': 56},
              {'title': 'Pro C. Rabiro perduellionis reo',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi012.perseus-lat2-simple',
               'docnum': 57},
              {'title': 'Pro Murena',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi014.perseus-lat2-simple',
               'docnum': 58},
              {'title': 'Pro Flacco',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi017.perseus-lat2-simple',
               'docnum': 59},
              {'title': 'Post reditum in senatu',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi019.perseus-lat2-simple',
               'docnum': 60},
              {'title': 'Letters to Atticus',
               'meta': 'book-letter-section',
               'urn': 'urn:cts:latinLit:phi0474.phi057.perseus-lat1-simple',
               'docnum': 61},
              {'title': 'Letters to Brutus',
               'meta': 'book-letter-section',
               'urn': 'urn:cts:latinLit:phi0474.phi059.perseus-lat1-simple',
               'docnum': 62},
              {'title': 'Letters to his brother Quintus',
               'meta': 'book-letter-section',
               'urn': 'urn:cts:latinLit:phi0474.phi058.perseus-lat1-simple',
               'docnum': 63},
              {'title': 'Letters to his Friends',
               'meta': 'book-letter-section',
               'urn': 'urn:cts:latinLit:phi0474.phi056.perseus-lat1-simple',
               'docnum': 64},
              {'title': 'Lucullus',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi046.perseus-lat1-simple',
               'docnum': 65},
              {'title': 'Pro A. Caecina',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi008.perseus-lat2-simple',
               'docnum': 66},
              {'title': 'Pro Tullio',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi0474.phi006.perseus-lat2-simple',
               'docnum': 67},
              {'title': 'On Oratory',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0474.phi037.perseus-lat1-simple',
               'docnum': 68},
              {'title': 'Pro lege manilia',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi009.perseus-lat2-simple',
               'docnum': 69},
              {'title': 'In Verrem',
               'meta': 'actio-book-section',
               'urn': 'urn:cts:latinLit:phi0474.phi005.perseus-lat2-simple',
               'docnum': 70},
              {'title': 'Orator',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi040.perseus-lat1-simple',
               'docnum': 71},
              {'title': 'Paradoxa Stoicorum',
               'meta': 'book-section',
               'urn': 'urn:cts:latinLit:phi0474.phi047.perseus-lat1-simple',
               'docnum': 72},
              {'title': 'Partitiones Oratoriae',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi038.perseus-lat1-simple',
               'docnum': 73},
              {'title': 'Timaeus',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi072.perseus-lat1-simple',
               'docnum': 74},
              {'title': 'Post reditum ad populum',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi018.perseus-lat2-simple',
               'docnum': 75},
              {'title': 'Topica',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0474.phi042.perseus-lat1-simple',
               'docnum': 76},
              {'title': 'Tusculanae Disputationes',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0474.phi049.perseus-lat1-simple',
               'docnum': 77}],
             'Claudianus, Claudius': [{'title': 'Carminum minorum corpusculum',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa001.perseus-lat2-simple',
               'docnum': 78},
              {'title': 'de bello Gildonico',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa002.perseus-lat2-simple',
               'docnum': 79},
              {'title': 'de Bello Gothico',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa003.perseus-lat2-simple',
               'docnum': 80},
              {'title': 'de consulatu Stilichonis',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa004.perseus-lat2-simple',
               'docnum': 81},
              {'title': 'de raptu Proserpinae',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa005.perseus-lat2-simple',
               'docnum': 82},
              {'title': 'Epithalamium de nuptiis Honorii Augusti',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa006.perseus-lat2-simple',
               'docnum': 83},
              {'title': 'Fescinnina de nuptiis Honorii Augusti',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa007.perseus-lat2-simple',
               'docnum': 84},
              {'title': 'In Eutropium',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa008.perseus-lat2-simple',
               'docnum': 85},
              {'title': 'In Rufinum',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa009.perseus-lat2-simple',
               'docnum': 86},
              {'title': 'Panegyricus de quarto consulatu Honorii Augusti',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa011.perseus-lat2-simple',
               'docnum': 87},
              {'title': 'Panegyricus de sexto consulatu Honorii Augusti',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa012.perseus-lat2-simple',
               'docnum': 88},
              {'title': 'Panegyricus de tertio consulatu Honorii Augusti',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa010.perseus-lat2-simple',
               'docnum': 89},
              {'title': 'Panegyricus dictus Manlio Theodoro consuli',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa013.perseus-lat2-simple',
               'docnum': 90},
              {'title': 'Panegyricus dictus Probino et Olybrio consulibus',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:stoa0089.stoa014.perseus-lat2-simple',
               'docnum': 91}],
             'Columella, Lucius Junius Moderatus': [{'title': 'Res Rustica',
               'meta': 'book-chapter-section',
               'urn': 'urn:cts:latinLit:phi0845.phi002.perseus-lat3-simple',
               'docnum': 92}],
             'Curtius Rufus, Quintus': [{'title': 'Historiarum Alexandri Magni',
               'meta': 'book-chapter-section',
               'urn': 'urn:cts:latinLit:phi0860.phi001.perseus-lat2-simple',
               'docnum': 93}],
             'Florus, Lucius Annaeus': [{'title': 'Epitome Rerum Romanorum',
               'meta': 'book-topic-chapter-section',
               'urn': 'urn:cts:latinLit:phi1242.phi001.perseus-lat1-simple',
               'docnum': 94}],
             'Gellius, Aulus': [{'title': 'Noctes Atticae',
               'meta': 'book-chapter-section',
               'urn': 'urn:cts:latinLit:phi1254.phi001.perseus-lat1-simple',
               'docnum': 95}],
             'Horace': [{'title': 'Ars Poetica',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0893.phi006.perseus-lat2-simple',
               'docnum': 96},
              {'title': 'Carmen Saeculare',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0893.phi002.perseus-lat2-simple',
               'docnum': 97},
              {'title': 'Epistulae',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:phi0893.phi005.perseus-lat2-simple',
               'docnum': 98},
              {'title': 'Epodi',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:phi0893.phi003.perseus-lat2-simple',
               'docnum': 99},
              {'title': 'Odes',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:phi0893.phi001.perseus-lat2-simple',
               'docnum': 100},
              {'title': 'Satires',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:phi0893.phi004.perseus-lat2-simple',
               'docnum': 101}],
             'Jerome Saint D. 419 Or 20': [{'title': 'Epistolae',
               'meta': 'letter-section',
               'urn': 'urn:cts:latinLit:stoa0162.stoa004.perseus-lat2-simple',
               'docnum': 102}],
             'Juvenal': [{'title': 'Satires',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:phi1276.phi001.perseus-lat2-simple',
               'docnum': 103}],
             'Lucan': [{'title': 'Civil War',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:phi0917.phi001.perseus-lat2-simple',
               'docnum': 104}],
             'Lucretius': [{'title': 'De Rerum Natura',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:phi0550.phi001.perseus-lat1-simple',
               'docnum': 105}],
             'Martial': [{'title': 'Epigrammata',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:phi1294.phi002.perseus-lat2-simple',
               'docnum': 106}],
             'Minucius Felix, Marcus': [{'title': 'Octavius',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0203.stoa001.perseus-lat2-simple',
               'docnum': 107}],
             'Nepos, Cornelius': [{'title': 'Agesilaus',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo017.perseus-lat2-simple',
               'docnum': 108},
              {'title': 'Alcibiades',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo007.perseus-lat2-simple',
               'docnum': 109},
              {'title': 'Aristides',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo003.perseus-lat2-simple',
               'docnum': 110},
              {'title': 'Atticus',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo025.perseus-lat2-simple',
               'docnum': 111},
              {'title': 'Cato',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo024.perseus-lat2-simple',
               'docnum': 112},
              {'title': 'Chabrias',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo012.perseus-lat2-simple',
               'docnum': 113},
              {'title': 'Cimon',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo005.perseus-lat2-simple',
               'docnum': 114},
              {'title': 'Conon',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo009.perseus-lat2-simple',
               'docnum': 115},
              {'title': 'Datames',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo014.perseus-lat2-simple',
               'docnum': 116},
              {'title': 'De Regibus',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo021.perseus-lat2-simple',
               'docnum': 117},
              {'title': 'Dion',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo010.perseus-lat2-simple',
               'docnum': 118},
              {'title': 'Epaminondas',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo015.perseus-lat2-simple',
               'docnum': 119},
              {'title': 'Eumenes',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo018.perseus-lat2-simple',
               'docnum': 120},
              {'title': 'Hamilcar',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo022.perseus-lat2-simple',
               'docnum': 121},
              {'title': 'Hannibal',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo023.perseus-lat2-simple',
               'docnum': 122},
              {'title': 'Iphicrates',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo011.perseus-lat2-simple',
               'docnum': 123},
              {'title': 'Lysander',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo006.perseus-lat2-simple',
               'docnum': 124},
              {'title': 'Miltiades',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo001.perseus-lat2-simple',
               'docnum': 125},
              {'title': 'Pausanias',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo004.perseus-lat2-simple',
               'docnum': 126},
              {'title': 'Pelopidas',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo016.perseus-lat2-simple',
               'docnum': 127},
              {'title': 'Phocion',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo019.perseus-lat2-simple',
               'docnum': 128},
              {'title': 'Themistocles',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo002.perseus-lat2-simple',
               'docnum': 129},
              {'title': 'Thrasybulus',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo008.perseus-lat2-simple',
               'docnum': 130},
              {'title': 'Timoleon',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo020.perseus-lat2-simple',
               'docnum': 131},
              {'title': 'Timotheus',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi0588.abo013.perseus-lat2-simple',
               'docnum': 132}],
             'Ovid': [{'title': 'Amores',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:phi0959.phi001.perseus-lat2-simple',
               'docnum': 133},
              {'title': 'Medicamina faciei femineae',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0959.phi003.perseus-lat2-simple',
               'docnum': 134},
              {'title': 'Ars Amatoria',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:phi0959.phi004.perseus-lat2-simple',
               'docnum': 135},
              {'title': 'Fasti',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:phi0959.phi007.perseus-lat2-simple',
               'docnum': 136},
              {'title': 'Epistulae',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:phi0959.phi002.perseus-lat2-simple',
               'docnum': 137},
              {'title': 'Ibis',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0959.phi010.perseus-lat2-simple',
               'docnum': 138},
              {'title': 'Ex Ponto',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:phi0959.phi009.perseus-lat2-simple',
               'docnum': 139},
              {'title': 'Metamorphoses',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:phi0959.phi006.perseus-lat2-simple',
               'docnum': 140},
              {'title': 'Remedia amoris',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0959.phi005.perseus-lat2-simple',
               'docnum': 141},
              {'title': 'Tristia',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:phi0959.phi008.perseus-lat2-simple',
               'docnum': 142}],
             'Paris, Julius': [{'title': 'Facta et Dicta Memorabilia',
               'meta': 'book-chapter-section',
               'urn': 'urn:cts:latinLit:phi1038.phi001.perseus-lat1-simple',
               'docnum': 143}],
             'Plautus, Titus Maccius': [{'title': 'Asinaria',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi002.perseus-lat2-simple',
               'docnum': 144},
              {'title': 'Aulularia',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi003.perseus-lat2-simple',
               'docnum': 145},
              {'title': 'Bacchides',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi004.perseus-lat2-simple',
               'docnum': 146},
              {'title': 'Captivi',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi005.perseus-lat2-simple',
               'docnum': 147},
              {'title': 'Casina',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi006.perseus-lat2-simple',
               'docnum': 148},
              {'title': 'Curculio',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi008.perseus-lat2-simple',
               'docnum': 149},
              {'title': 'Epidicus',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi009.perseus-lat2-simple',
               'docnum': 150},
              {'title': 'Menaechmi',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi010.perseus-lat2-simple',
               'docnum': 151},
              {'title': 'Mercator',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi011.perseus-lat2-simple',
               'docnum': 152},
              {'title': 'Miles Gloriosus',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi012.perseus-lat2-simple',
               'docnum': 153},
              {'title': 'Mostellaria',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi013.perseus-lat2-simple',
               'docnum': 154},
              {'title': 'Persa',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi014.perseus-lat2-simple',
               'docnum': 155},
              {'title': 'Poenulus',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi015.perseus-lat2-simple',
               'docnum': 156},
              {'title': 'Rudens',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi017.perseus-lat2-simple',
               'docnum': 157},
              {'title': 'Stichus',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi018.perseus-lat2-simple',
               'docnum': 158},
              {'title': 'Trinummus',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi019.perseus-lat2-simple',
               'docnum': 159},
              {'title': 'Truculentus',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0119.phi020.perseus-lat2-simple',
               'docnum': 160}],
             'Pliny, The Elder': [{'title': 'Naturalis Historia',
               'meta': 'book-chapter',
               'urn': 'urn:cts:latinLit:phi0978.phi001.perseus-lat2-simple',
               'docnum': 161}],
             'Pliny, The Younger': [{'title': 'Epistulae',
               'meta': 'book-letter-section',
               'urn': 'urn:cts:latinLit:phi1318.phi001.perseus-lat1-simple',
               'docnum': 162}],
             'Propertius, Sextus': [{'title': 'Elegies',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:phi0620.phi001.perseus-lat3-simple',
               'docnum': 163}],
             'Prudentius B. 348': [{'title': 'Apotheosis',
               'meta': 'section-line',
               'urn': 'urn:cts:latinLit:stoa0238.stoa005.perseus-lat2-simple',
               'docnum': 164},
              {'title': 'Cathemerina',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0238.stoa004.perseus-lat2-simple',
               'docnum': 165},
              {'title': 'Contra Orationem Symmachia',
               'meta': 'book-section-line',
               'urn': 'urn:cts:latinLit:stoa0238.stoa007.perseus-lat2-simple',
               'docnum': 166},
              {'title': 'Dittochaeon',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:stoa0238.stoa008.perseus-lat2-simple',
               'docnum': 167},
              {'title': 'Epilogus',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:stoa0238.stoa009.perseus-lat2-simple',
               'docnum': 168},
              {'title': 'Hamartigenia',
               'meta': 'section-line',
               'urn': 'urn:cts:latinLit:stoa0238.stoa006.perseus-lat2-simple',
               'docnum': 169},
              {'title': 'Liber Peristephanon',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:stoa0238.stoa001.perseus-lat2-simple',
               'docnum': 170},
              {'title': 'Praefetio',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:stoa0238.stoa003.perseus-lat2-simple',
               'docnum': 171},
              {'title': 'Psychomachia',
               'meta': 'section-line',
               'urn': 'urn:cts:latinLit:stoa0238.stoa002.perseus-lat2-simple',
               'docnum': 172}],
             'Quintus Tullius Cicero': [{'title': 'Commentariolum Petitionis',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi0478.phi003.perseus-lat2-simple',
               'docnum': 173}],
             'Sallust': [{'title': 'Bellum Iugurthinum',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi0631.phi002.perseus-lat4-simple',
               'docnum': 174},
              {'title': 'Catilinae Coniuratio',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi0631.phi001.perseus-lat3-simple',
               'docnum': 175},
              {'title': 'Historiae',
               'meta': 'book-section',
               'urn': 'urn:cts:latinLit:phi0631.phi003.perseus-lat2-simple',
               'docnum': 176}],
             'Seneca, Lucius Annaeus, 55 B.C.-Ca. 39 A.D': [{'title': 'Controversiae',
               'meta': 'book-chapter-section',
               'urn': 'urn:cts:latinLit:phi1014.phi001.perseus-lat1-simple',
               'docnum': 177},
              {'title': 'Excerpta Controversiae',
               'meta': 'book-chapter',
               'urn': 'urn:cts:latinLit:phi1014.phi002.perseus-lat1-simple',
               'docnum': 178},
              {'title': 'Fragmenta',
               'meta': 'fragment',
               'urn': 'urn:cts:latinLit:phi1014.phi004.perseus-lat1-simple',
               'docnum': 179},
              {'title': 'Suasoriae',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi1014.phi003.perseus-lat1-simple',
               'docnum': 180}],
             'Seneca, Lucius Annaeus (Plays)': [{'title': 'Agamemnon',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi1017.phi007.perseus-lat2-simple',
               'docnum': 181},
              {'title': 'Apocolocyntosis',
               'meta': 'section',
               'urn': 'urn:cts:latinLit:phi1017.phi011.perseus-lat2-simple',
               'docnum': 182},
              {'title': 'De Clementia',
               'meta': 'book-chapter-section',
               'urn': 'urn:cts:latinLit:phi1017.phi014.perseus-lat2-simple',
               'docnum': 183},
              {'title': 'Hercules Furens',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi1017.phi001.perseus-lat2-simple',
               'docnum': 184},
              {'title': 'Hercules Oetaeus',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi1017.phi009.perseus-lat2-simple',
               'docnum': 185},
              {'title': 'Medea',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi1017.phi004.perseus-lat2-simple',
               'docnum': 186},
              {'title': 'Octavia',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi1017.phi010.perseus-lat2-simple',
               'docnum': 187},
              {'title': 'Oedipus',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi1017.phi006.perseus-lat2-simple',
               'docnum': 188},
              {'title': 'Phaedra',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi1017.phi005.perseus-lat2-simple',
               'docnum': 189},
              {'title': 'Phoenissae',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi1017.phi003.perseus-lat2-simple',
               'docnum': 190},
              {'title': 'Thyestes',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi1017.phi008.perseus-lat2-simple',
               'docnum': 191},
              {'title': 'Troades Furens',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi1017.phi002.perseus-lat2-simple',
               'docnum': 192}],
             'Seneca, Lucius Annaeus': [{'title': 'de Brevitate Vitae',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0255.stoa004.perseus-lat2-simple',
               'docnum': 193},
              {'title': 'de consolatione ad Helviam',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0255.stoa006.perseus-lat2-simple',
               'docnum': 194},
              {'title': 'de consolatione ad Marciam',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0255.stoa007.perseus-lat2-simple',
               'docnum': 195},
              {'title': 'de consolatione ad Polybium',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0255.stoa008.perseus-lat2-simple',
               'docnum': 196},
              {'title': 'de Constantia',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0255.stoa009.perseus-lat2-simple',
               'docnum': 197},
              {'title': 'de Ira',
               'meta': 'book-chapter-section',
               'urn': 'urn:cts:latinLit:stoa0255.stoa010.perseus-lat2-simple',
               'docnum': 198},
              {'title': 'de Otio Sapientis',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0255.stoa011.perseus-lat2-simple',
               'docnum': 199},
              {'title': 'de Providentia',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0255.stoa012.perseus-lat2-simple',
               'docnum': 200},
              {'title': 'de Tranquilitate Animi',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0255.stoa013.perseus-lat2-simple',
               'docnum': 201},
              {'title': 'de Vita Beata',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0255.stoa014.perseus-lat2-simple',
               'docnum': 202}],
             'Silius Italicus, Tiberius Catius': [{'title': 'Punica',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:phi1345.phi001.perseus-lat2-simple',
               'docnum': 203}],
             'Statius, P. Papinius (Publius Papinius)': [{'title': 'Achilleis',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:phi1020.phi003.perseus-lat2-simple',
               'docnum': 204},
              {'title': 'Silvae',
               'meta': 'book-poem-line',
               'urn': 'urn:cts:latinLit:phi1020.phi002.perseus-lat2-simple',
               'docnum': 205}],
             'Suetonius Ca. 69-Ca. 122': [{'title': 'Caligula',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi1348.abo014.perseus-lat2-simple',
               'docnum': 206},
              {'title': 'Divus Augustus',
               'meta': 'unknown',
               'urn': 'urn:cts:latinLit:phi1348.abo012.perseus-lat2-simple',
               'docnum': 207},
              {'title': 'Divus Claudius',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi1348.abo015.perseus-lat2-simple',
               'docnum': 208},
              {'title': 'Divus Julius',
               'meta': 'unknown',
               'urn': 'urn:cts:latinLit:phi1348.abo011.perseus-lat2-simple',
               'docnum': 209},
              {'title': 'Divus Titus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi1348.abo021.perseus-lat2-simple',
               'docnum': 210},
              {'title': 'Divus Vespasianus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi1348.abo020.perseus-lat2-simple',
               'docnum': 211},
              {'title': 'Domitianus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi1348.abo022.perseus-lat2-simple',
               'docnum': 212},
              {'title': 'Galba',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi1348.abo017.perseus-lat2-simple',
               'docnum': 213},
              {'title': 'Nero',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi1348.abo016.perseus-lat2-simple',
               'docnum': 214},
              {'title': 'Otho',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi1348.abo018.perseus-lat2-simple',
               'docnum': 215},
              {'title': 'Tiberius',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi1348.abo013.perseus-lat2-simple',
               'docnum': 216},
              {'title': 'Vitellius',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi1348.abo019.perseus-lat2-simple',
               'docnum': 217}],
             'Tacitus, Cornelius': [{'title': 'Agricola',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi1351.phi001.perseus-lat1-simple',
               'docnum': 218},
              {'title': 'Germania',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:phi1351.phi002.perseus-lat1-simple',
               'docnum': 219}],
             'Terence': [{'title': 'Andria',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0134.phi001.perseus-lat2-simple',
               'docnum': 220},
              {'title': 'Phormio',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0134.phi004.perseus-lat2-simple',
               'docnum': 221},
              {'title': 'The Brothers',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0134.phi006.perseus-lat2-simple',
               'docnum': 222},
              {'title': 'The Eunuch',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0134.phi003.perseus-lat2-simple',
               'docnum': 223},
              {'title': 'The Mother-in-Law',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0134.phi005.perseus-lat2-simple',
               'docnum': 224},
              {'title': 'The Self-Tormenter',
               'meta': 'line',
               'urn': 'urn:cts:latinLit:phi0134.phi002.perseus-lat2-simple',
               'docnum': 225}],
             'Tertullian Ca. 160-Ca. 230': [{'title': 'Ad Martyras',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa001.opp-lat1-simple',
               'docnum': 226},
              {'title': 'Ad Nationes Libri Duo',
               'meta': 'book-chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa002.opp-lat1-simple',
               'docnum': 227},
              {'title': 'Ad Scapulam',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa003.opp-lat1-simple',
               'docnum': 228},
              {'title': 'Ad Uxorem',
               'meta': 'book-chapter',
               'urn': 'urn:cts:latinLit:stoa0276.stoa002.opp-lat1-simple',
               'docnum': 229},
              {'title': 'Adversus Hermogenem',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa004.opp-lat1-simple',
               'docnum': 230},
              {'title': 'Adversus Judaeos Liber',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa005.opp-lat1-simple',
               'docnum': 231},
              {'title': 'Adversus Marcionem',
               'meta': 'book-chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa006.opp-lat1-simple',
               'docnum': 232},
              {'title': 'Adversus Praxean',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa007.opp-lat1-simple',
               'docnum': 233},
              {'title': 'Adversus Valentinianos',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa008.opp-lat1-simple',
               'docnum': 234},
              {'title': 'Apologeticum',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0275.stoa009.perseus-lat2-simple',
               'docnum': 235},
              {'title': 'De Anima',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa010.opp-lat1-simple',
               'docnum': 236},
              {'title': 'De Baptismo',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa011.opp-lat1-simple',
               'docnum': 237},
              {'title': 'De Carne Christi',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa012.opp-lat1-simple',
               'docnum': 238},
              {'title': 'De Carnis Resurrectione',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa026.opp-lat1-simple',
               'docnum': 239},
              {'title': 'De Corona',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa013.opp-lat1-simple',
               'docnum': 240},
              {'title': 'De Cultu Feminarum',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa014.opp-lat1-simple',
               'docnum': 241},
              {'title': 'De Exhortatione Castitatis Liber',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa015.opp-lat1-simple',
               'docnum': 242},
              {'title': 'De Fuga in Persecutione',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa016.opp-lat1-simple',
               'docnum': 243},
              {'title': 'De idolatria',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa017.opp-lat1-simple',
               'docnum': 244},
              {'title': 'De ieiunio adversus psychicos',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa018.opp-lat1-simple',
               'docnum': 245},
              {'title': 'De Monogamia',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa019.opp-lat1-simple',
               'docnum': 246},
              {'title': 'De Oratione',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa020.opp-lat1-simple',
               'docnum': 247},
              {'title': 'De Paenitentia',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa021.opp-lat1-simple',
               'docnum': 248},
              {'title': 'De Pallio',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa022.opp-lat1-simple',
               'docnum': 249},
              {'title': 'De Patientia',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa023.opp-lat1-simple',
               'docnum': 250},
              {'title': 'De Praescriptionibus Hereticorum',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa024.opp-lat1-simple',
               'docnum': 251},
              {'title': 'De Pudicitia',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa025.opp-lat1-simple',
               'docnum': 252},
              {'title': 'De Spectaculis',
               'meta': 'chapter-section',
               'urn': 'urn:cts:latinLit:stoa0275.stoa027.perseus-lat2-simple',
               'docnum': 253},
              {'title': 'De Testimionio Animae',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa028.opp-lat1-simple',
               'docnum': 254},
              {'title': 'De Virginibus Velandis',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa029.opp-lat1-simple',
               'docnum': 255},
              {'title': 'Scorpiace',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:stoa0275.stoa030.opp-lat1-simple',
               'docnum': 256}],
             'Tibullus': [{'title': 'Elegiae',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:phi0660.phi003.perseus-lat2-simple',
               'docnum': 257}],
             'Valerius Flaccus, Gaius': [{'title': 'Argonautica',
               'meta': 'book-line',
               'urn': 'urn:cts:latinLit:phi1035.phi001.perseus-lat2-simple',
               'docnum': 258}],
             'Virgil': [{'title': 'Aeneid',
               'meta': 'Book-line',
               'urn': 'urn:cts:latinLit:phi0690.phi003.perseus-lat2-simple',
               'docnum': 259},
              {'title': 'Eclogues',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:phi0690.phi001.perseus-lat2-simple',
               'docnum': 260},
              {'title': 'Georgics',
               'meta': 'poem-line',
               'urn': 'urn:cts:latinLit:phi0690.phi002.perseus-lat2-simple',
               'docnum': 261}],
             'Vitruvius Pollio': [{'title': 'On Architecture',
               'meta': 'book-chapter-section',
               'urn': 'urn:cts:latinLit:phi1056.phi001.perseus-lat1-simple',
               'docnum': 262}],
             'Vopiscus, Flavius Fl. 3./4. Jh': [{'title': 'Alexander Severus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi018.perseus-lat2-simple',
               'docnum': 263},
              {'title': 'Antoninus Caracalla',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi013.perseus-lat2-simple',
               'docnum': 264},
              {'title': 'Antoninus Geta',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi014.perseus-lat2-simple',
               'docnum': 265},
              {'title': 'Antoninus Heliogobalus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi017.perseus-lat2-simple',
               'docnum': 266},
              {'title': 'Antoninus Pius',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi003.perseus-lat2-simple',
               'docnum': 267},
              {'title': 'Avidius Casius',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi006.perseus-lat2-simple',
               'docnum': 268},
              {'title': 'Carus et Carinus et Numerianus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi030.perseus-lat2-simple',
               'docnum': 269},
              {'title': 'Clodinus Albinus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi012.perseus-lat2-simple',
               'docnum': 270},
              {'title': 'Commodus Antoninus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi007.perseus-lat2-simple',
               'docnum': 271},
              {'title': 'De Vita Hadriani',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi001.perseus-lat2-simple',
               'docnum': 272},
              {'title': 'Diadumenus Antoninus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi016.perseus-lat2-simple',
               'docnum': 273},
              {'title': 'Didius Julianus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi009.perseus-lat2-simple',
               'docnum': 274},
              {'title': 'Divus Aurelianus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi026.perseus-lat2-simple',
               'docnum': 275},
              {'title': 'Divus Claudius',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi025.perseus-lat2-simple',
               'docnum': 276},
              {'title': 'Firmus Saturninus, Proculus et Bonosus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi029.perseus-lat2-simple',
               'docnum': 277},
              {'title': 'Gallieni Duo',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi023.perseus-lat2-simple',
               'docnum': 278},
              {'title': 'Goridani Tres',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi020.perseus-lat2-simple',
               'docnum': 279},
              {'title': 'Helius',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi002.perseus-lat2-simple',
               'docnum': 280},
              {'title': 'Marcus Antoninus Philosophus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi004.perseus-lat2-simple',
               'docnum': 281},
              {'title': 'Maximini Duo',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi019.perseus-lat2-simple',
               'docnum': 282},
              {'title': 'Maximus et Balbinus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi021.perseus-lat2-simple',
               'docnum': 283},
              {'title': 'Opilius Macrinus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi015.perseus-lat2-simple',
               'docnum': 284},
              {'title': 'Pertinax',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi008.perseus-lat2-simple',
               'docnum': 285},
              {'title': 'Pescennius Niger',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi011.perseus-lat2-simple',
               'docnum': 286},
              {'title': 'Probus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi028.perseus-lat2-simple',
               'docnum': 287},
              {'title': 'Severus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi010.perseus-lat2-simple',
               'docnum': 288},
              {'title': 'Tacitus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi027.perseus-lat2-simple',
               'docnum': 289},
              {'title': 'Tyranni Triginta',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi024.perseus-lat2-simple',
               'docnum': 290},
              {'title': 'Valeriani Duo',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi022.perseus-lat2-simple',
               'docnum': 291},
              {'title': 'Verus',
               'meta': 'chapter',
               'urn': 'urn:cts:latinLit:phi2331.phi005.perseus-lat2-simple',
               'docnum': 292}]}

mapping = {
    "abactus1": {"lemma": "abactus", "uri": "45879", "pos": "a", "morpho": "aps---mn1-"}, "abactus2": {
        "lemma": "abactus", "uri": "a9982", "pos": "n", "morpho": "n-s---mn4-"
    }, "abdico1": {"lemma": "abdico", "uri": "a0034", "pos": "v", "morpho": "v1spia--1-"},
    "abdico2": {"lemma": "abdico", "uri": "a0035", "pos": "v", "morpho": "v1spia--3-"},
    "aborsus1": {"lemma": "aborsus", "uri": "51972", "pos": "a", "morpho": "aps---mn1-"},
    "aborsus2": {"lemma": "aborsus", "uri": "101412", "pos": "n", "morpho": "n-s---mn4-"},
    "abortio1": {"lemma": "abortio", "uri": "a0126", "pos": "n", "morpho": "n-s---fn3-"},
    "abortio2": {"lemma": "abortio", "uri": "a0127", "pos": "v", "morpho": "v1spia--4-"},
    "Absyrtus1": {"lemma": "Absyrtus", "uri": "58422", "pos": "n", "morpho": "n-s---mn2-"},
    "Absyrtus2": {"lemma": "Absyrtus", "uri": "58422", "pos": "n", "morpho": "n-s---mn2-"},
    "accendo1": {"lemma": "accendo", "uri": "a0246", "pos": "n", "morpho": "n-s---mn3-"},
    "accendo2": {"lemma": "accendo", "uri": "a0245", "pos": "v", "morpho": "v1spia--3-"},
    "accensus1": {"lemma": "accensus", "uri": "58407", "pos": "a", "morpho": "aps---mn1-"},
    "accensus2": {"lemma": "accensus", "uri": "a0277", "pos": "n", "morpho": "n-s---mn4-"},
    "acceptor1": {"lemma": "acceptor", "uri": "a0259", "pos": "n", "morpho": "n-s---mn3-"},
    "acceptor2": {"lemma": "acceptor", "uri": "a0259", "pos": "n", "morpho": "n-s---mn3-"},
    "accessus1": {"lemma": "accessus", "uri": "101502", "pos": "a", "morpho": "aps---mn1-"},
    "accessus2": {"lemma": "accessus", "uri": "a0239", "pos": "n", "morpho": "n-s---mn4-"},
    "accitus1": {"lemma": "accitus", "uri": "101513", "pos": "a", "morpho": "aps---mn1-"},
    "accitus2": {"lemma": "accitus", "uri": "a9989", "pos": "n", "morpho": "n-s---mn4-"},
    "acer1": {"lemma": "acer", "uri": "a0335", "pos": "n", "morpho": "n-s---nn3-"},
    "acer2": {"lemma": "acer", "uri": "a0336", "pos": "a", "morpho": "aps---mn3i"},
    "Achaeus1": {"lemma": "Achaeus", "uri": "101202", "pos": "n", "morpho": "n-s---mn2-"},
    "Achaeus2": {"lemma": "Achaeus", "uri": "58435", "pos": "a", "morpho": "aps---mn1-"},
    "Achates1": {"lemma": "Achates", "uri": "19250", "pos": "n", "morpho": "n-s---mn3-"},
    "Achates2": {"lemma": "Achates", "uri": "19250", "pos": "n", "morpho": "n-s---mn3-"},
    "Acis1": {"lemma": "Acis", "uri": "58448", "pos": "n", "morpho": "n-s---fn3-"},
    "Acis2": {"lemma": "Acis", "uri": "58448", "pos": "n", "morpho": "n-s---fn3-"},
    "Acragas1": {"lemma": "Acragas", "uri": "58453", "pos": "n", "morpho": "n-s---mn3-"},
    "Acragas2": {"lemma": "Acragas", "uri": "58453", "pos": "n", "morpho": "n-s---mn3-"},
    "acritas1": {"lemma": "acritas", "uri": "a0419", "pos": "n", "morpho": "n-s---fn3-"},
    "Acritas2": {"lemma": "Acritas", "uri": "19263", "pos": "n", "morpho": "n-s---mn1g"},
    "acta1": {"lemma": "acta", "uri": "a0436", "pos": "n", "morpho": "n-s---fn1-"},
    "acta2": {"lemma": "acta", "uri": "101596", "pos": "n", "morpho": "n-p---nn2-"},
    "acte1": {"lemma": "acte", "uri": "a0439", "pos": "n", "morpho": "n-s---fn1g"},
    "Acte2": {"lemma": "Acte", "uri": "58461", "pos": "n", "morpho": "n-s---fn1g"},
    "Actius1": {"lemma": "Actius", "uri": "58463", "pos": "n", "morpho": "n-s---mn2-"},
    "Actius2": {"lemma": "Actius", "uri": "58463", "pos": "n", "morpho": "n-s---mn2-"},
    "actor1": {"lemma": "actor", "uri": "a0448", "pos": "n", "morpho": "n-s---mn3-"},
    "actorius1": {"lemma": "actorius", "uri": "a0449", "pos": "a", "morpho": "aps---mn1-"},
    "Actorius2": {"lemma": "Actorius", "uri": "58464", "pos": "n", "morpho": "n-s---mn2-"},
    "actuarius1": {"lemma": "actuarius", "uri": "a0453", "pos": "a", "morpho": "aps---mn1-"},
    "actuarius2": {"lemma": "actuarius", "uri": "a0453", "pos": "n", "morpho": "n-s---mn2-"},
    "actus1": {"lemma": "actus", "uri": "a9991", "pos": "n", "morpho": "n-s---mn4-"},
    "actus2": {"lemma": "actus", "uri": "a9991", "pos": "n", "morpho": "n-s---mn4-"},
    "acus1": {"lemma": "acus", "uri": "a0468", "pos": "n", "morpho": "n-s---fn4-"},
    "acus2": {"lemma": "acus", "uri": "a0468", "pos": "n", "morpho": "n-s---nn3-"},
    "acus3": {"lemma": "acus", "uri": "a0468", "pos": "n", "morpho": "n-s---mn2-"},
    "adactus1": {"lemma": "adactus", "uri": "101622", "pos": "a", "morpho": "aps---mn1-"},
    "adactus2": {"lemma": "adactus", "uri": "a9993", "pos": "n", "morpho": "n-s---mn4-"},
    "adauctus1": {"lemma": "adauctus", "uri": "101646", "pos": "a", "morpho": "aps---mn1-"},
    "adauctus2": {"lemma": "adauctus", "uri": "a0477", "pos": "n", "morpho": "n-s---mn4-"},
    "adeo1": {"lemma": "adeo", "uri": "a0553", "pos": "v", "morpho": "v1spia--2-"},
    "adeo2": {"lemma": "adeo", "uri": "a0552", "pos": "r", "morpho": "rp--------"},
    "adeptus1": {"lemma": "adeptus", "uri": "101666", "pos": "a", "morpho": "aps---mn1-"},
    "adeptus2": {"lemma": "adeptus", "uri": "a0638", "pos": "n", "morpho": "n-s---mn4-"},
    "aditus1": {"lemma": "aditus", "uri": "a9997", "pos": "n", "morpho": "n-s---mn4-"},
    "aditus2": {"lemma": "aditus", "uri": "a9997", "pos": "n", "morpho": "n-s---mn4-"},
    "adjectus1": {"lemma": "adiectus", "uri": "101730", "pos": "a", "morpho": "aps---mn1-"},
    "adjectus2": {"lemma": "adiectus", "uri": "a9996", "pos": "n", "morpho": "n-s---mn4-"},
    "adjuro1": {"lemma": "adiuro", "uri": "a0628", "pos": "v", "morpho": "v1spia--1-"},
    "adjuro2": {"lemma": "adiuro", "uri": "a0628", "pos": "v", "morpho": "v1spia--1-"},
    "adjutor1": {"lemma": "adiutor", "uri": "a0631", "pos": "n", "morpho": "n-s---mn3-"},
    "adjutor2": {"lemma": "adiutor", "uri": "a0631", "pos": "n", "morpho": "n-s---mn3-"},
    "adjutus1": {"lemma": "adiutus", "uri": "101758", "pos": "a", "morpho": "aps---mn1-"},
    "adjutus2": {"lemma": "adiutus", "uri": "a0675", "pos": "n", "morpho": "n-s---mn4-"},
    "admissus1": {"lemma": "admissus", "uri": "101798", "pos": "a", "morpho": "aps---mn1-"},
    "admissus2": {"lemma": "admissus", "uri": "a9998", "pos": "n", "morpho": "n-s---mn4-"},
    "admixtus1": {"lemma": "admixtus", "uri": "101802", "pos": "a", "morpho": "aps---mn1-"},
    "admixtus2": {"lemma": "admixtus", "uri": "a9999", "pos": "n", "morpho": "n-s---mn4-"},
    "admonitus1": {"lemma": "admonitus", "uri": "101807", "pos": "a", "morpho": "aps---mn1-"},
    "admonitus2": {"lemma": "admonitus", "uri": "a0711", "pos": "n", "morpho": "n-s---mn4-"},
    "admorsus1": {"lemma": "admorsus", "uri": "101808", "pos": "a", "morpho": "aps---mn1-"},
    "admorsus2": {"lemma": "admorsus", "uri": "a8880", "pos": "n", "morpho": "n-s---mn4-"},
    "adoleo1": {"lemma": "adoleo", "uri": "a1875", "pos": "v", "morpho": "v1spia--2-"},
    "adoleo2": {"lemma": "adoleo", "uri": "a1875", "pos": "v", "morpho": "v1spia--2-"},
    "adoreus1": {"lemma": "adoreus", "uri": "a2263", "pos": "a", "morpho": "aps---mn1-"},
    "Adoreus2": {"lemma": "Adoreus", "uri": "58472", "pos": "n", "morpho": "n-s---mn2-"},
    "adulter1": {"lemma": "adulter", "uri": "a0812", "pos": "n", "morpho": "n-s---mn2r"},
    "adulter2": {"lemma": "adulter", "uri": "a0812", "pos": "a", "morpho": "aps---mn1r"},
    "advectus1": {"lemma": "aduectus", "uri": "101897", "pos": "a", "morpho": "aps---mn1-"},
    "advectus2": {"lemma": "aduectus", "uri": "a8885", "pos": "n", "morpho": "n-s---mn4-"},
    "adversus1": {"lemma": "aduersus", "uri": "19548", "pos": "a", "morpho": "aps---mn1-"},
    "adversus2": {"lemma": "aduersus", "uri": "a2240", "pos": "n", "morpho": "n-s---mn2-"},
    "adversus3": {"lemma": "aduersus", "uri": "a0795", "pos": "r", "morpho": "rp--------"},
    "advocatus1": {"lemma": "aduocatus", "uri": "101922", "pos": "a", "morpho": "aps---mn1-"},
    "advocatus2": {"lemma": "aduocatus", "uri": "a0794", "pos": "n", "morpho": "n-s---mn2-"},
    "Aegeus1": {"lemma": "Aegeus", "uri": "58485", "pos": "n", "morpho": "n-s---mn2-"},
    "Aegeus2": {"lemma": "Aegeus", "uri": "58485", "pos": "n", "morpho": "n-s---mn2-"},
    "Aegyptus1": {"lemma": "Aegyptus", "uri": "19574", "pos": "n", "morpho": "n-s---fn2-"},
    "Aegyptus2": {"lemma": "Aegyptus", "uri": "19574", "pos": "n", "morpho": "n-s---fn2-"},
    "Aenea1": {"lemma": "Aenea", "uri": "58500", "pos": "n", "morpho": "n-s---fn1-"},
    "Aenea2": {"lemma": "Aenea", "uri": "58500", "pos": "n", "morpho": "n-s---fn1-"},
    "aenus3": {"lemma": "aenus", "uri": "32574", "pos": "a", "morpho": "aps---mn1-"},
    "Aeolis1": {"lemma": "Aeolis", "uri": "58507", "pos": "n", "morpho": "n-s---fn3-"},
    "Aeolis2": {"lemma": "Aeolis", "uri": "58507", "pos": "n", "morpho": "n-s---fn3-"},
    "aereus1": {"lemma": "aereus", "uri": "a0974", "pos": "a", "morpho": "aps---mn1-"},
    "aereus2": {"lemma": "aereus", "uri": "a0974", "pos": "a", "morpho": "aps---mn1-"},
    "aero1": {"lemma": "aero", "uri": "a0985", "pos": "v", "morpho": "v1spia--1-"},
    "aero2": {"lemma": "aero", "uri": "a0986", "pos": "n", "morpho": "n-s---mn3-"},
    "Aesis1": {"lemma": "Aesis", "uri": "58520", "pos": "n", "morpho": "n-s---fn3-"},
    "Aesis2": {"lemma": "Aesis", "uri": "58520", "pos": "n", "morpho": "n-s---fn3-"},
    "aeterno1": {"lemma": "aeterno", "uri": "19627", "pos": "r", "morpho": "rp--------"},
    "aeterno2": {"lemma": "aeterno", "uri": "a1042", "pos": "v", "morpho": "v1spia--1-"},
    "aethra1": {"lemma": "aethra", "uri": "a1049", "pos": "n", "morpho": "n-s---fn1-"},
    "Aethra2": {"lemma": "Aethra", "uri": "58527", "pos": "n", "morpho": "n-s---fn1-"},
    "affatus1": {"lemma": "affatus", "uri": "a8888", "pos": "n", "morpho": "n-s---mn4-"},
    "affatus2": {"lemma": "affatus", "uri": "a8888", "pos": "n", "morpho": "n-s---mn4-"},
    "affectus1": {"lemma": "affectus", "uri": "37417", "pos": "a", "morpho": "aps---mn1-"},
    "affectus2": {"lemma": "affectus", "uri": "a1055", "pos": "n", "morpho": "n-s---mn4-"},
    "afflatus1": {"lemma": "afflatus", "uri": "a8889", "pos": "n", "morpho": "n-s---mn4-"},
    "afflatus2": {"lemma": "afflatus", "uri": "a8889", "pos": "n", "morpho": "n-s---mn4-"},
    "afflictus1": {"lemma": "afflictus", "uri": "36969", "pos": "a", "morpho": "aps---mn1-"},
    "afflictus2": {"lemma": "afflictus", "uri": "a8891", "pos": "n", "morpho": "n-s---mn4-"},
    "aggero1": {"lemma": "aggero", "uri": "a1150", "pos": "v", "morpho": "v1spia--1-"},
    "aggero2": {"lemma": "aggero", "uri": "a1149", "pos": "v", "morpho": "v1spia--3-"},
    "aggestus1": {"lemma": "aggestus", "uri": "a8893", "pos": "n", "morpho": "n-s---mn4-"},
    "aggestus2": {"lemma": "aggestus", "uri": "97563", "pos": "n", "morpho": "n-s---mn2-"},
    "aggressus1": {"lemma": "aggressus", "uri": "a1202", "pos": "n", "morpho": "n-s---mn4-"},
    "aggressus2": {"lemma": "aggressus", "uri": "a1202", "pos": "n", "morpho": "n-s---mn4-"},
    "agna1": {"lemma": "agna", "uri": "a1207", "pos": "n", "morpho": "n-s---fn1-"},
    "agna2": {"lemma": "agna", "uri": "a1207", "pos": "n", "morpho": "n-s---fn1-"},
    "agricola1": {"lemma": "agricola", "uri": "a1233", "pos": "n", "morpho": "n-s---mn1-"},
    "agrius1": {"lemma": "agrius", "uri": "a1242", "pos": "a", "morpho": "aps---mn1-"},
    "Agrius2": {"lemma": "Agrius", "uri": "58551", "pos": "n", "morpho": "n-s---mn2-"},
    "alazon1": {"lemma": "alazon", "uri": "101215", "pos": "n", "morpho": "n-s---mn3-"},
    "Alazon2": {"lemma": "Alazon", "uri": "58561", "pos": "n", "morpho": "n-s---nn3-"},
    "alba1": {"lemma": "alba", "uri": "a1311", "pos": "n", "morpho": "n-s---fn1-"},
    "Alba2": {"lemma": "Alba", "uri": "58562", "pos": "n", "morpho": "n-s---fn1-"},
    "Alba3": {"lemma": "Alba", "uri": "58562", "pos": "n", "morpho": "n-s---fn1-"},
    "Alba4": {"lemma": "Alba", "uri": "58562", "pos": "n", "morpho": "n-s---fn1-"},
    "albinus1": {"lemma": "albinus", "uri": "a1296", "pos": "n", "morpho": "n-s---mn2-"},
    "Albinus2": {"lemma": "Albinus", "uri": "58567", "pos": "n", "morpho": "n-s---mn2-"},
    "alburnus1": {"lemma": "alburnus", "uri": "a1310", "pos": "n", "morpho": "n-s---mn2-"},
    "Alcis1": {"lemma": "Alcis", "uri": "58578", "pos": "n", "morpho": "n-s---fn3-"},
    "Alcis2": {"lemma": "Alcis", "uri": "58578", "pos": "n", "morpho": "n-s---fn3-"},
    "Alcmaeo1": {"lemma": "Alcmaeo", "uri": "58581", "pos": "n", "morpho": "n-s---mn3-"},
    "Alcmaeo2": {"lemma": "Alcmaeo", "uri": "58581", "pos": "n", "morpho": "n-s---mn3-"},
    "algidus1": {"lemma": "algidus", "uri": "a1340", "pos": "a", "morpho": "aps---mn1-"},
    "Algidus2": {"lemma": "Algidus", "uri": "58590", "pos": "n", "morpho": "n-s---mn2-"},
    "alis1": {"lemma": "alis", "uri": "97578", "pos": "n", "morpho": "n-s---fn3-"},
    "Alis2": {"lemma": "Alis", "uri": "58592", "pos": "n", "morpho": "n-s---fn3-"},
    "alitus1": {"lemma": "alitus", "uri": "a8935", "pos": "n", "morpho": "n-s---mn4-"},
    "alitus2": {"lemma": "alitus", "uri": "a8935", "pos": "n", "morpho": "n-s---mn4-"},
    "Alius1": {"lemma": "Alius", "uri": "58593", "pos": "a", "morpho": "aps---mn1-"},
    "alius2": {"lemma": "alius", "uri": "a1506", "pos": "a", "morpho": "aps---mn1p"},
    "allapsus1": {"lemma": "allapsus", "uri": "a1401", "pos": "n", "morpho": "n-s---mn4-"},
    "allapsus2": {"lemma": "allapsus", "uri": "a1401", "pos": "n", "morpho": "n-s---mn4-"},
    "allector1": {"lemma": "allector", "uri": "a2640", "pos": "n", "morpho": "n-s---mn3-"},
    "allector2": {"lemma": "allector", "uri": "a2640", "pos": "n", "morpho": "n-s---mn3-"},
    "allectus1": {"lemma": "allectus", "uri": "102187", "pos": "a", "morpho": "aps---mn1-"},
    "allectus2": {"lemma": "allectus", "uri": "102187", "pos": "a", "morpho": "aps---mn1-"},
    "allego1": {"lemma": "allego", "uri": "a1403", "pos": "v", "morpho": "v1spia--1-"},
    "allego2": {"lemma": "allego", "uri": "a1404", "pos": "v", "morpho": "v1spia--3-"},
    "allex1": {"lemma": "allex", "uri": "a9937", "pos": "n", "morpho": "n-s---mn3-"},
    "allex2": {"lemma": "allex", "uri": "a9937", "pos": "n", "morpho": "n-s---mn3-"},
    "alsius1": {"lemma": "alsius", "uri": "a1477", "pos": "a", "morpho": "aps---mn1-"},
    "althaea1": {"lemma": "althaea", "uri": "a1500", "pos": "n", "morpho": "n-s---fn1-"},
    "Althaea2": {"lemma": "Althaea", "uri": "58605", "pos": "n", "morpho": "n-s---fn1-"},
    "altus1": {"lemma": "altus", "uri": "19744", "pos": "a", "morpho": "aps---mn1-"},
    "altus2": {"lemma": "altus", "uri": "a8935", "pos": "n", "morpho": "n-s---mn4-"},
    "ambitus1": {"lemma": "ambitus", "uri": "102304", "pos": "a", "morpho": "aps---mn1-"},
    "ambitus2": {"lemma": "ambitus", "uri": "a8896", "pos": "n", "morpho": "n-s---mn4-"},
    "ambrosia1": {"lemma": "ambrosia", "uri": "a2297", "pos": "n", "morpho": "n-s---fn1-"},
    "ambrosius1": {"lemma": "ambrosius", "uri": "a2370", "pos": "a", "morpho": "aps---mn1-"},
    "amictus1": {"lemma": "amictus", "uri": "102337", "pos": "a", "morpho": "aps---mn1-"},
    "amictus2": {"lemma": "amictus", "uri": "a8898", "pos": "n", "morpho": "n-s---mn4-"},
    "amicus1": {"lemma": "amicus", "uri": "a0783", "pos": "a", "morpho": "aps---mn1-"},
    "amicus2": {"lemma": "amicus", "uri": "a1687", "pos": "n", "morpho": "n-s---mn2-"},
    "amissus1": {"lemma": "amissus", "uri": "102341", "pos": "a", "morpho": "aps---mn1-"},
    "amissus2": {"lemma": "amissus", "uri": "a1734", "pos": "n", "morpho": "n-s---mn4-"},
    "ampelos1": {"lemma": "ampelos", "uri": "a1729", "pos": "n", "morpho": "n-s---fn2g"},
    "Ampelos3": {"lemma": "Ampelos", "uri": "58630", "pos": "n", "morpho": "n-s---mn2-"},
    "amplexus1": {"lemma": "amplexus", "uri": "102396", "pos": "a", "morpho": "aps---mn1-"},
    "amplexus2": {"lemma": "amplexus", "uri": "a1780", "pos": "n", "morpho": "n-s---mn4-"},
    "Anas3": {"lemma": "Anas", "uri": "101222", "pos": "n", "morpho": "n-s---mn1g"},
    "ancon1": {"lemma": "ancon", "uri": "a1926", "pos": "n", "morpho": "n-s---mn3-"},
    "ancus1": {"lemma": "ancus", "uri": "30758", "pos": "n", "morpho": "n-s---mn2-"},
    "Andes1": {"lemma": "Andes", "uri": "58669", "pos": "n", "morpho": "n-p---mn3i"},
    "Andes2": {"lemma": "Andes", "uri": "58669", "pos": "n", "morpho": "n-p---mn3i"},
    "anfractus1": {"lemma": "anfractus", "uri": "a1968", "pos": "a", "morpho": "aps---mn1-"},
    "anfractus2": {"lemma": "anfractus", "uri": "a1968", "pos": "n", "morpho": "n-s---mn4-"},
    "anhydros1": {"lemma": "anhydros", "uri": "a2018", "pos": "n", "morpho": "n-s---fn2g"},
    "Anhydros2": {"lemma": "Anhydros", "uri": "58680", "pos": "n", "morpho": "n-s---mn2-"},
    "animatus1": {"lemma": "animatus", "uri": "19882", "pos": "a", "morpho": "aps---mn1-"},
    "animatus2": {"lemma": "animatus", "uri": "a2055", "pos": "n", "morpho": "n-s---mn4-"},
    "animosus1": {"lemma": "animosus", "uri": "a2043", "pos": "a", "morpho": "aps---mn1-"},
    "animosus2": {"lemma": "animosus", "uri": "a2043", "pos": "a", "morpho": "aps---mn1-"},
    "animula1": {"lemma": "animula", "uri": "a2044", "pos": "n", "morpho": "n-s---fn1-"},
    "annexus1": {"lemma": "annexus", "uri": "43574", "pos": "a", "morpho": "aps---mn1-"},
    "annexus2": {"lemma": "annexus", "uri": "53389", "pos": "n", "morpho": "n-s---mn4-"},
    "annisus1": {"lemma": "annisus", "uri": "102575", "pos": "a", "morpho": "aps---mn1-"},
    "annisus2": {"lemma": "annisus", "uri": "102576", "pos": "n", "morpho": "n-s---mn4-"},
    "annixus1": {"lemma": "annixus", "uri": "30176", "pos": "a", "morpho": "aps---mn1-"},
    "annixus2": {"lemma": "annixus", "uri": "30176", "pos": "a", "morpho": "aps---mn1-"},
    "anno1": {"lemma": "anno", "uri": "a7061", "pos": "v", "morpho": "v1spia--1-"},
    "anno2": {"lemma": "anno", "uri": "a7061", "pos": "v", "morpho": "v1spia--1-"},
    "anser1": {"lemma": "anser", "uri": "a0919", "pos": "n", "morpho": "n-s---mn3-"},
    "anthedon1": {"lemma": "anthedon", "uri": "a2187", "pos": "n", "morpho": "n-s---fn3-"},
    "Anthedon2": {"lemma": "Anthedon", "uri": "58694", "pos": "n", "morpho": "n-s---nn3-"},
    "anthrax1": {"lemma": "anthrax", "uri": "a2201", "pos": "n", "morpho": "n-s---mn3-"},
    "Anthrax2": {"lemma": "Anthrax", "uri": "58698", "pos": "n", "morpho": "n-s---mn3-"},
    "Antiochensis1": {"lemma": "Antiochensis", "uri": "58709", "pos": "n", "morpho": "n-s---fn3-"},
    "Antiochensis2": {"lemma": "Antiochensis", "uri": "58709", "pos": "n", "morpho": "n-s---fn3-"},
    "Antiochenus1": {"lemma": "Antiochenus", "uri": "58710", "pos": "a", "morpho": "aps---mn1-"},
    "Antiochenus2": {"lemma": "Antiochenus", "uri": "58710", "pos": "a", "morpho": "aps---mn1-"},
    "antipathes1": {"lemma": "antipathes", "uri": "a2228", "pos": "n", "morpho": "n-s---fn3i"},
    "antipathes2": {"lemma": "antipathes", "uri": "a2228", "pos": "n", "morpho": "n-s---fn3i"},
    "anulus1": {"lemma": "anulus", "uri": "a2290", "pos": "n", "morpho": "n-s---mn2-"},
    "anulus2": {"lemma": "anulus", "uri": "a2290", "pos": "n", "morpho": "n-s---mn2-"},
    "anus1": {"lemma": "anus", "uri": "a2292", "pos": "n", "morpho": "n-s---mn2-"},
    "aper1": {"lemma": "aper", "uri": "a2320", "pos": "n", "morpho": "n-s---mn2r"},
    "Aphrodisias1": {"lemma": "Aphrodisias", "uri": "58739", "pos": "n", "morpho": "n-s---mn3-"},
    "apicius1": {"lemma": "apicius", "uri": "a2359", "pos": "a", "morpho": "aps---mn1-"},
    "Apicius2": {"lemma": "Apicius", "uri": "58742", "pos": "a", "morpho": "aps---mn1-"},
    "apis1": {"lemma": "apis", "uri": "a2369", "pos": "n", "morpho": "n-s---fn3i"},
    "Apis2": {"lemma": "Apis", "uri": "7030", "pos": "n", "morpho": "n-s---mn3g"},
    "Apis3": {"lemma": "Apis", "uri": "7030", "pos": "n", "morpho": "n-s---mn3g"},
    "apparatus1": {"lemma": "apparatus", "uri": "19985", "pos": "a", "morpho": "aps---mn1-"},
    "apparatus2": {"lemma": "apparatus", "uri": "a2502", "pos": "n", "morpho": "n-s---mn4-"},
    "appello1": {"lemma": "appello", "uri": "a2482", "pos": "v", "morpho": "v1spia--3-"},
    "appello2": {"lemma": "appello", "uri": "a2481", "pos": "v", "morpho": "v1spia--1-"},
    "appetitus1": {"lemma": "appetitus", "uri": "a8901", "pos": "n", "morpho": "n-s---mn4-"},
    "appetitus2": {"lemma": "appetitus", "uri": "a8901", "pos": "n", "morpho": "n-s---mn4-"},
    "appeto2": {"lemma": "appeto", "uri": "a2499", "pos": "n", "morpho": "n-s---mn3-"},
    "Appianus1": {"lemma": "Appianus", "uri": "58756", "pos": "a", "morpho": "aps---mn1-"},
    "Appianus2": {"lemma": "Appianus", "uri": "58756", "pos": "a", "morpho": "aps---mn1-"},
    "Appianus3": {"lemma": "Appianus", "uri": "58756", "pos": "a", "morpho": "aps---mn1-"},
    "appingo1": {"lemma": "appingo", "uri": "a2501", "pos": "v", "morpho": "v1spia--3-"},
    "appingo2": {"lemma": "appingo", "uri": "a2501", "pos": "v", "morpho": "v1spia--3-"},
    "appositus1": {"lemma": "appositus", "uri": "20007", "pos": "a", "morpho": "aps---mn1-"},
    "appositus2": {"lemma": "appositus", "uri": "a2509", "pos": "n", "morpho": "n-s---mn4-"},
    "appulsus1": {"lemma": "appulsus", "uri": "a8903", "pos": "n", "morpho": "n-s---mn4-"},
    "appulsus2": {"lemma": "appulsus", "uri": "a8903", "pos": "n", "morpho": "n-s---mn4-"},
    "apus1": {"lemma": "apus", "uri": "a2581", "pos": "n", "morpho": "n-s---mn3-"},
    "aquila1": {"lemma": "aquila", "uri": "a1531", "pos": "n", "morpho": "n-s---fn1-"},
    "Aquila2": {"lemma": "Aquila", "uri": "58765", "pos": "n", "morpho": "n-s---fn1-"},
    "Arabus1": {"lemma": "Arabus", "uri": "58775", "pos": "n", "morpho": "n-s---mn2-"},
    "Arabus2": {"lemma": "Arabus", "uri": "58775", "pos": "n", "morpho": "n-s---mn2-"},
    "Arabus3": {"lemma": "Arabus", "uri": "58775", "pos": "n", "morpho": "n-s---mn2-"},
    "aracia1": {"lemma": "aracia", "uri": "32659", "pos": "n", "morpho": "n-s---fn1-"},
    "Aracia2": {"lemma": "Aracia", "uri": "58778", "pos": "n", "morpho": "n-s---fn1-"},
    "araneus1": {"lemma": "araneus", "uri": "a2639", "pos": "n", "morpho": "n-s---mn2-"},
    "araneus2": {"lemma": "araneus", "uri": "a2639", "pos": "a", "morpho": "aps---mn1-"},
    "aratus1": {"lemma": "aratus", "uri": "102950", "pos": "a", "morpho": "aps---mn1-"},
    "Aratus2": {"lemma": "Aratus", "uri": "58783", "pos": "n", "morpho": "n-s---mn2-"},
    "Arbis1": {"lemma": "Arbis", "uri": "58786", "pos": "n", "morpho": "n-s---fn3-"},
    "Arbis2": {"lemma": "Arbis", "uri": "58786", "pos": "n", "morpho": "n-s---fn3-"},
    "arbitratus1": {"lemma": "arbitratus", "uri": "102954", "pos": "a", "morpho": "aps---mn1-"},
    "arbitratus2": {"lemma": "arbitratus", "uri": "a8904", "pos": "n", "morpho": "n-s---mn4-"},
    "arbor1": {"lemma": "arbor", "uri": "a2659", "pos": "n", "morpho": "n-s---fn3-"},
    "arbuscula1": {"lemma": "arbuscula", "uri": "a2665", "pos": "n", "morpho": "n-s---fn1-"},
    "Arbuscula2": {"lemma": "Arbuscula", "uri": "58788", "pos": "n", "morpho": "n-s---fn1-"},
    "Arcadia1": {"lemma": "Arcadia", "uri": "58789", "pos": "n", "morpho": "n-s---fn1-"},
    "Arcadia2": {"lemma": "Arcadia", "uri": "58789", "pos": "n", "morpho": "n-s---fn1-"},
    "arcanus1": {"lemma": "arcanus", "uri": "a2675", "pos": "a", "morpho": "aps---mn1-"},
    "Arcanus2": {"lemma": "Arcanus", "uri": "58790", "pos": "a", "morpho": "aps---mn1-"},
    "arcessitus1": {"lemma": "arcessitus", "uri": "97663", "pos": "a", "morpho": "aps---mn1-"},
    "arcessitus2": {"lemma": "arcessitus", "uri": "a2676", "pos": "n", "morpho": "n-s---mn4-"},
    "arctus1": {"lemma": "arctus", "uri": "55642", "pos": "a", "morpho": "aps---mn1-"},
    "arctus2": {"lemma": "arctus", "uri": "97666", "pos": "n", "morpho": "n-s---mn2-"},
    "ardea1": {"lemma": "ardea", "uri": "a2766", "pos": "n", "morpho": "n-s---fn1-"},
    "Ardea2": {"lemma": "Ardea", "uri": "58799", "pos": "a", "morpho": "aps---fn1-"},
    "argentarius1": {"lemma": "argentarius", "uri": "a2788", "pos": "a", "morpho": "aps---mn1-"},
    "argenteus1": {"lemma": "argenteus", "uri": "a2578", "pos": "a", "morpho": "aps---mn1-"},
    "Argenteus2": {"lemma": "Argenteus", "uri": "58811", "pos": "n", "morpho": "n-s---mn2-"},
    "argestes1": {"lemma": "argestes", "uri": "a2796", "pos": "n", "morpho": "n-s---mn1g"},
    "Argestes2": {"lemma": "Argestes", "uri": "132172", "pos": "n", "morpho": "n-s---mn3i"},
    "Aria1": {"lemma": "Aria", "uri": "58820", "pos": "n", "morpho": "n-s---fn1-"},
    "Aria2": {"lemma": "Aria", "uri": "58820", "pos": "n", "morpho": "n-s---fn1-"},
    "aris1": {"lemma": "aris", "uri": "a2839", "pos": "n", "morpho": "n-s---fn3-"},
    "Aris2": {"lemma": "Aris", "uri": "58828", "pos": "n", "morpho": "n-s---fn3-"},
    "Arius1": {"lemma": "Arius", "uri": "58836", "pos": "n", "morpho": "n-s---mn2-"},
    "Arius2": {"lemma": "Arius", "uri": "58836", "pos": "n", "morpho": "n-s---mn2-"},
    "armatus1": {"lemma": "armatus", "uri": "45112", "pos": "a", "morpho": "aps---mn1-"},
    "armatus2": {"lemma": "armatus", "uri": "a2909", "pos": "n", "morpho": "n-s---mn4-"},
    "Arna1": {"lemma": "Arna", "uri": "58838", "pos": "n", "morpho": "n-s---fn1-"},
    "arna2": {"lemma": "arna", "uri": "31502", "pos": "n", "morpho": "n-s---fn1-"},
    "Arne1": {"lemma": "Arne", "uri": "58839", "pos": "n", "morpho": "n-s---fn1-"},
    "Arne2": {"lemma": "Arne", "uri": "58839", "pos": "n", "morpho": "n-s---fn1-"},
    "artio1": {"lemma": "artio", "uri": "a2967", "pos": "v", "morpho": "v1spia--4-"},
    "artio2": {"lemma": "artio", "uri": "a2967", "pos": "v", "morpho": "v1spia--4-"},
    "artus1": {"lemma": "artus", "uri": "a1891", "pos": "a", "morpho": "aps---mn1-"},
    "artus2": {"lemma": "artus", "uri": "a1967", "pos": "n", "morpho": "n-s---mn4-"},
    "Ascanius1": {"lemma": "Ascanius", "uri": "58860", "pos": "a", "morpho": "aps---mn1-"},
    "Ascanius2": {"lemma": "Ascanius", "uri": "58860", "pos": "a", "morpho": "aps---mn1-"},
    "ascensus1": {"lemma": "ascensus", "uri": "a2969", "pos": "n", "morpho": "n-s---mn4-"},
    "ascensus2": {"lemma": "ascensus", "uri": "a2969", "pos": "n", "morpho": "n-s---mn4-"},
    "ascio1": {"lemma": "ascio", "uri": "a2285", "pos": "v", "morpho": "v1spia--1-"},
    "ascio2": {"lemma": "ascio", "uri": "a2285", "pos": "v", "morpho": "v1spia--1-"},
    "ascitus1": {"lemma": "ascitus", "uri": "33308", "pos": "a", "morpho": "aps---mn1-"},
    "ascitus2": {"lemma": "ascitus", "uri": "55283", "pos": "n", "morpho": "n-s---mn4-"},
    "aspargo1": {"lemma": "aspargo", "uri": "51315", "pos": "v", "morpho": "v1spia--3-"},
    "aspargo2": {"lemma": "aspargo", "uri": "97699", "pos": "n", "morpho": "n-s---fn3-"},
    "aspectus1": {"lemma": "aspectus", "uri": "a3106", "pos": "n", "morpho": "n-s---mn4-"},
    "aspectus2": {"lemma": "aspectus", "uri": "a3106", "pos": "n", "morpho": "n-s---mn4-"},
    "asper1": {"lemma": "asper", "uri": "a3072", "pos": "a", "morpho": "aps---mn1r"},
    "aspergo2": {"lemma": "aspergo", "uri": "a3076", "pos": "n", "morpho": "n-s---fn3-"},
    "aspersus1": {"lemma": "aspersus", "uri": "a8905", "pos": "n", "morpho": "n-s---mn4-"},
    "aspersus2": {"lemma": "aspersus", "uri": "a8905", "pos": "n", "morpho": "n-s---mn4-"},
    "assarius1": {"lemma": "assarius", "uri": "a3113", "pos": "a", "morpho": "aps---mn1-"},
    "assarius2": {"lemma": "assarius", "uri": "a3112", "pos": "n", "morpho": "n-s---mn2-"},
    "assensus1": {"lemma": "assensus", "uri": "a3151", "pos": "n", "morpho": "n-s---mn4-"},
    "assensus2": {"lemma": "assensus", "uri": "a3151", "pos": "n", "morpho": "n-s---mn4-"},
    "assero1": {"lemma": "assero", "uri": "a3141", "pos": "v", "morpho": "v1spia--3-"},
    "assero2": {"lemma": "assero", "uri": "a3141", "pos": "v", "morpho": "v1spia--3-"},
    "assessus1": {"lemma": "assessus", "uri": "a8906", "pos": "n", "morpho": "n-s---mn4-"},
    "assessus2": {"lemma": "assessus", "uri": "a8906", "pos": "n", "morpho": "n-s---mn4-"},
    "assiduo1": {"lemma": "assiduo", "uri": "41409", "pos": "r", "morpho": "rp--------"},
    "assiduo2": {"lemma": "assiduo", "uri": "a3162", "pos": "v", "morpho": "v1spia--1-"},
    "assiduus1": {"lemma": "assiduus", "uri": "32714", "pos": "n", "morpho": "n-s---mn2-"},
    "assiduus2": {"lemma": "assiduus", "uri": "a3163", "pos": "a", "morpho": "aps---mn1-"},
    "assis1": {"lemma": "assis", "uri": "103226", "pos": "n", "morpho": "n-s---mn3i"},
    "assis2": {"lemma": "assis", "uri": "103226", "pos": "n", "morpho": "n-s---mn3i"},
    "assitus1": {"lemma": "assitus", "uri": "a6183", "pos": "a", "morpho": "aps---mn1-"},
    "assitus2": {"lemma": "assitus", "uri": "a6183", "pos": "a", "morpho": "aps---mn1-"},
    "astacus1": {"lemma": "astacus", "uri": "a3216", "pos": "n", "morpho": "n-s---mn2-"},
    "Astacus2": {"lemma": "Astacus", "uri": "58880", "pos": "n", "morpho": "n-s---mn2-"},
    "Astacus3": {"lemma": "Astacus", "uri": "58880", "pos": "n", "morpho": "n-s---mn2-"},
    "asteria1": {"lemma": "asteria", "uri": "a3223", "pos": "n", "morpho": "n-s---fn1-"},
    "Asteria2": {"lemma": "Asteria", "uri": "58883", "pos": "n", "morpho": "n-s---fn1-"},
    "asterion1": {"lemma": "asterion", "uri": "a3226", "pos": "n", "morpho": "n-s---nn2g"},
    "astur1": {"lemma": "astur", "uri": "a3281", "pos": "n", "morpho": "n-s---mn3-"},
    "Astur2": {"lemma": "Astur", "uri": "58890", "pos": "n", "morpho": "n-s---mn3-"},
    "astus1": {"lemma": "astus", "uri": "97703", "pos": "a", "morpho": "aps---mn1-"},
    "astus2": {"lemma": "astus", "uri": "a3282", "pos": "n", "morpho": "n-s---mn4-"},
    "ater1": {"lemma": "ater", "uri": "a6288", "pos": "a", "morpho": "aps---mn1r"},
    "atratus1": {"lemma": "atratus", "uri": "a3307", "pos": "a", "morpho": "aps---mn1-"},
    "Atratus2": {"lemma": "Atratus", "uri": "58922", "pos": "n", "morpho": "n-s---mn2-"},
    "atta1": {"lemma": "atta", "uri": "a3399", "pos": "n", "morpho": "n-s---mn1-"},
    "Atta2": {"lemma": "Atta", "uri": "58927", "pos": "n", "morpho": "n-s---fn1-"},
    "attactus1": {"lemma": "attactus", "uri": "a8909", "pos": "n", "morpho": "n-s---mn4-"},
    "attactus2": {"lemma": "attactus", "uri": "a8909", "pos": "n", "morpho": "n-s---mn4-"},
    "attentus1": {"lemma": "attentus", "uri": "20219", "pos": "a", "morpho": "aps---mn1-"},
    "attentus2": {"lemma": "attentus", "uri": "20219", "pos": "a", "morpho": "aps---mn1-"},
    "attractus1": {"lemma": "attractus", "uri": "51775", "pos": "a", "morpho": "aps---mn1-"},
    "attractus2": {"lemma": "attractus", "uri": "a8911", "pos": "n", "morpho": "n-s---mn4-"},
    "attritus1": {"lemma": "attritus", "uri": "20243", "pos": "a", "morpho": "aps---mn1-"},
    "attritus2": {"lemma": "attritus", "uri": "a8913", "pos": "n", "morpho": "n-s---mn4-"},
    "auctumnus1": {"lemma": "auctumnus", "uri": "33721", "pos": "n", "morpho": "n-s---mn2-"},
    "auctumnus2": {"lemma": "auctumnus", "uri": "45822", "pos": "a", "morpho": "aps---mn1-"},
    "auctus1": {"lemma": "auctus", "uri": "97715", "pos": "a", "morpho": "aps---mn1-"},
    "auctus2": {"lemma": "auctus", "uri": "a3499", "pos": "n", "morpho": "n-s---mn4-"},
    "auditus1": {"lemma": "auditus", "uri": "103348", "pos": "a", "morpho": "aps---mn1-"},
    "auditus2": {"lemma": "auditus", "uri": "a3449", "pos": "n", "morpho": "n-s---mn4-"},
    "augustus1": {"lemma": "augustus", "uri": "a3492", "pos": "a", "morpho": "aps---mn1-"},
    "aula1": {"lemma": "aula", "uri": "a3672", "pos": "n", "morpho": "n-s---fn1-"},
    "aula2": {"lemma": "aula", "uri": "a3672", "pos": "n", "morpho": "n-s---fn1-"},
    "aulicus1": {"lemma": "aulicus", "uri": "a3673", "pos": "a", "morpho": "aps---mn1-"},
    "aulicus2": {"lemma": "aulicus", "uri": "a3673", "pos": "a", "morpho": "aps---mn1-"},
    "Aulus2": {"lemma": "Aulus", "uri": "103380", "pos": "n", "morpho": "n-s---mn2-"},
    "aurarius1": {"lemma": "aurarius", "uri": "a3531", "pos": "a", "morpho": "aps---mn1-"},
    "aurarius2": {"lemma": "aurarius", "uri": "a8934", "pos": "n", "morpho": "n-s---mn2-"},
    "auspicatus1": {"lemma": "auspicatus", "uri": "20300", "pos": "a", "morpho": "aps---mn1-"},
    "auspicatus2": {"lemma": "auspicatus", "uri": "97727", "pos": "n", "morpho": "n-s---mn4-"},
    "auster1": {"lemma": "auster", "uri": "a3595", "pos": "n", "morpho": "n-s---mn2r"},
    "auster2": {"lemma": "auster", "uri": "a3595", "pos": "n", "morpho": "n-s---mn2r"},
    "ausus1": {"lemma": "ausus", "uri": "103422", "pos": "a", "morpho": "aps---mn1-"},
    "ausus2": {"lemma": "ausus", "uri": "a3436", "pos": "n", "morpho": "n-s---mn4-"},
    "aveo1": {"lemma": "aueo", "uri": "a3465", "pos": "v", "morpho": "v1spia--2-"},
    "aveo2": {"lemma": "aueo", "uri": "a3465", "pos": "v", "morpho": "v1spia--2-"},
    "aversor1": {"lemma": "auersor", "uri": "a3463", "pos": "v", "morpho": "v1spid--1-"},
    "aversor2": {"lemma": "auersor", "uri": "a3464", "pos": "n", "morpho": "n-s---mn3-"},
    "avia1": {"lemma": "auia", "uri": "a3628", "pos": "n", "morpho": "n-s---fn1-"},
    "avia2": {"lemma": "auia", "uri": "a3628", "pos": "n", "morpho": "n-s---fn1-"},
    "avitus1": {"lemma": "auitus", "uri": "a3504", "pos": "a", "morpho": "aps---mn1-"},
    "Avitus2": {"lemma": "Auitus", "uri": "58967", "pos": "n", "morpho": "n-s---mn2-"},
    "Axius1": {"lemma": "Axius", "uri": "58968", "pos": "n", "morpho": "n-s---mn2-"},
    "Axius2": {"lemma": "Axius", "uri": "58968", "pos": "n", "morpho": "n-s---mn2-"},
    "axon1": {"lemma": "axon", "uri": "a3658", "pos": "n", "morpho": "n-s---mn3-"},
    "Axon2": {"lemma": "Axon", "uri": "58969", "pos": "n", "morpho": "n-s---nn3-"},
    "Baccha1": {"lemma": "Baccha", "uri": "58978", "pos": "n", "morpho": "n-s---fn3-"},
    "Baccha2": {"lemma": "Baccha", "uri": "58978", "pos": "n", "morpho": "n-s---fn3-"},
    "Bacchus1": {"lemma": "Bacchus", "uri": "20344", "pos": "n", "morpho": "n-s---mn2-"},
    "Bacchus2": {"lemma": "Bacchus", "uri": "20344", "pos": "n", "morpho": "n-s---mn2-"},
    "balatro1": {"lemma": "balatro", "uri": "b0054", "pos": "n", "morpho": "n-s---mn3-"},
    "balbus1": {"lemma": "balbus", "uri": "b0056", "pos": "a", "morpho": "aps---mn1-"},
    "Balbus2": {"lemma": "Balbus", "uri": "58991", "pos": "n", "morpho": "n-s---mn2-"},
    "balista1": {"lemma": "balista", "uri": "49010", "pos": "n", "morpho": "n-s---fn1-"},
    "Balista2": {"lemma": "Balista", "uri": "58995", "pos": "n", "morpho": "n-s---fn1-"},
    "ballista1": {"lemma": "ballista", "uri": "b0070", "pos": "n", "morpho": "n-s---fn1-"},
    "barba1": {"lemma": "barba", "uri": "b0114", "pos": "n", "morpho": "n-s---fn1-"},
    "Barba2": {"lemma": "Barba", "uri": "59006", "pos": "n", "morpho": "n-s---fn1-"},
    "barbarum1": {"lemma": "barbarum", "uri": "b0121", "pos": "n", "morpho": "n-s---nn2-"},
    "barbarum2": {"lemma": "barbarum", "uri": "b0121", "pos": "n", "morpho": "n-s---nn2-"},
    "Barea1": {"lemma": "Barea", "uri": "59014", "pos": "n", "morpho": "n-s---fn1-"},
    "Barea2": {"lemma": "Barea", "uri": "59014", "pos": "n", "morpho": "n-s---fn1-"},
    "barritus1": {"lemma": "barritus", "uri": "b9690", "pos": "n", "morpho": "n-s---mn4-"},
    "barritus2": {"lemma": "barritus", "uri": "b9690", "pos": "n", "morpho": "n-s---mn4-"},
    "Basilia1": {"lemma": "Basilia", "uri": "59023", "pos": "n", "morpho": "n-s---fn1-"},
    "Basilia2": {"lemma": "Basilia", "uri": "59023", "pos": "n", "morpho": "n-s---fn1-"},
    "batrachus1": {"lemma": "batrachus", "uri": "b0187", "pos": "n", "morpho": "n-s---mn2-"},
    "Batrachus2": {"lemma": "Batrachus", "uri": "59038", "pos": "n", "morpho": "n-s---mn2-"},
    "batus1": {"lemma": "batus", "uri": "b0192", "pos": "n", "morpho": "n-s---fn2-"},
    "batus2": {"lemma": "batus", "uri": "b9692", "pos": "n", "morpho": "n-s---mn2-"},
    "Bebryces1": {"lemma": "Bebryces", "uri": "59045", "pos": "n", "morpho": "n-p---mn3-"},
    "Bebryces2": {"lemma": "Bebryces", "uri": "59045", "pos": "n", "morpho": "n-p---mn3-"},
    "bestia1": {"lemma": "bestia", "uri": "b0491", "pos": "n", "morpho": "n-s---fn1-"},
    "Bestia2": {"lemma": "Bestia", "uri": "59080", "pos": "n", "morpho": "n-s---fn1-"},
    "beta1": {"lemma": "beta", "uri": "b0287", "pos": "n", "morpho": "n-s---fn1-"},
    "beta2": {"lemma": "beta", "uri": "b0801", "pos": "n", "morpho": "n-s---nn--"},
    "betis1": {"lemma": "betis", "uri": "b0287", "pos": "n", "morpho": "n-s---fn3i"},
    "bibo1": {"lemma": "bibo", "uri": "b0311", "pos": "v", "morpho": "v1spia--3-"},
    "bibo2": {"lemma": "bibo", "uri": "b0312", "pos": "n", "morpho": "n-s---mn3-"},
    "bibulus1": {"lemma": "bibulus", "uri": "b0315", "pos": "a", "morpho": "aps---mn1-"},
    "Bibulus2": {"lemma": "Bibulus", "uri": "59088", "pos": "n", "morpho": "n-s---mn2-"},
    "bipennis1": {"lemma": "bipennis", "uri": "b0410", "pos": "a", "morpho": "aps---cn3i"},
    "bipennis2": {"lemma": "bipennis", "uri": "b0410", "pos": "a", "morpho": "aps---cn3i"},
    "bito1": {"lemma": "bito", "uri": "b0436", "pos": "v", "morpho": "v1spia--3-"},
    "Bito2": {"lemma": "Bito", "uri": "59100", "pos": "n", "morpho": "n-s---mn3-"},
    "blaesus1": {"lemma": "blaesus", "uri": "b0450", "pos": "a", "morpho": "aps---mn1-"},
    "Blaesus2": {"lemma": "Blaesus", "uri": "59105", "pos": "n", "morpho": "n-s---mn2-"},
    "blatero1": {"lemma": "blatero", "uri": "b0477", "pos": "v", "morpho": "v1spia--1-"},
    "blatero2": {"lemma": "blatero", "uri": "b0478", "pos": "n", "morpho": "n-s---mn3-"},
    "blatta1": {"lemma": "blatta", "uri": "b0496", "pos": "n", "morpho": "n-s---fn1-"},
    "blatta2": {"lemma": "blatta", "uri": "b0496", "pos": "n", "morpho": "n-s---fn1-"},
    "boethus1": {"lemma": "boethus", "uri": "b0498", "pos": "n", "morpho": "n-s---mn2-"},
    "bonum1": {"lemma": "bonum", "uri": "b0144", "pos": "n", "morpho": "n-s---nn2-"},
    "bonum2": {"lemma": "bonum", "uri": "b0144", "pos": "n", "morpho": "n-s---nn2-"},
    "botrys1": {"lemma": "botrys", "uri": "b0567", "pos": "n", "morpho": "n-s---fn3g"},
    "Botrys2": {"lemma": "Botrys", "uri": "59131", "pos": "n", "morpho": "n-s---mn3-"},
    "bova1": {"lemma": "boua", "uri": "58095", "pos": "n", "morpho": "n-s---fn1-"},
    "bova2": {"lemma": "boua", "uri": "58095", "pos": "n", "morpho": "n-s---fn1-"},
    "brigantes1": {"lemma": "brigantes", "uri": "b0634", "pos": "n", "morpho": "n-s---mn3-"},
    "brochus1": {"lemma": "brochus", "uri": "37576", "pos": "a", "morpho": "aps---mn1-"},
    "Brochus2": {"lemma": "Brochus", "uri": "59153", "pos": "n", "morpho": "n-s---mn2-"},
    "brutus1": {"lemma": "brutus", "uri": "b0651", "pos": "a", "morpho": "aps---mn1-"},
    "Brutus2": {"lemma": "Brutus", "uri": "20488", "pos": "n", "morpho": "n-s---mn2-"},
    "bu1": {"lemma": "bu", "uri": "103883", "pos": "n", "morpho": "n-s---fn--"},
    "bu2": {"lemma": "bu", "uri": "103883", "pos": "n", "morpho": "n-s---fn--"},
    "bubo1": {"lemma": "bubo", "uri": "b0664", "pos": "n", "morpho": "n-s---mn3-"},
    "bubo2": {"lemma": "bubo", "uri": "103890", "pos": "v", "morpho": "v1spia--3-"},
    "bubulcus1": {"lemma": "bubulcus", "uri": "b0670", "pos": "n", "morpho": "n-s---mn2-"},
    "Bubulcus2": {"lemma": "Bubulcus", "uri": "59173", "pos": "n", "morpho": "n-s---mn2-"},
    "bulbus1": {"lemma": "bulbus", "uri": "b0720", "pos": "n", "morpho": "n-s---mn2-"},
    "Bulbus2": {"lemma": "Bulbus", "uri": "59178", "pos": "n", "morpho": "n-s---mn2-"},
    "bura1": {"lemma": "bura", "uri": "b0744", "pos": "n", "morpho": "n-s---fn1-"},
    "Bura2": {"lemma": "Bura", "uri": "59179", "pos": "n", "morpho": "n-s---fn1-"},
    "buris1": {"lemma": "buris", "uri": "b0744", "pos": "n", "morpho": "n-s---mn3i"},
    "Buris2": {"lemma": "Buris", "uri": "59181", "pos": "n", "morpho": "n-s---fn3-"},
    "burrus1": {"lemma": "burrus", "uri": "b0758", "pos": "a", "morpho": "aps---mn1-"},
    "butio1": {"lemma": "butio", "uri": "b0774", "pos": "n", "morpho": "n-s---mn3-"},
    "butio2": {"lemma": "butio", "uri": "b0775", "pos": "v", "morpho": "v1spia--4-"},
    "caballus1": {"lemma": "caballus", "uri": "c0002", "pos": "n", "morpho": "n-s---mn2-"},
    "Caballus2": {"lemma": "Caballus", "uri": "59195", "pos": "n", "morpho": "n-s---mn2-"},
    "cachinno1": {"lemma": "cachinno", "uri": "c0029", "pos": "v", "morpho": "v1spia--1-"},
    "cachinno2": {"lemma": "cachinno", "uri": "c0030", "pos": "n", "morpho": "n-s---mn3-"},
    "Cacus1": {"lemma": "Cacus", "uri": "59199", "pos": "n", "morpho": "n-s---mn2-"},
    "cacus2": {"lemma": "cacus", "uri": "103996", "pos": "n", "morpho": "n-s---mn2-"},
    "cadmea1": {"lemma": "cadmea", "uri": "c0059", "pos": "n", "morpho": "n-s---fn1-"},
    "Caecina1": {"lemma": "Caecina", "uri": "59205", "pos": "n", "morpho": "n-s---fn1-"},
    "Caecina2": {"lemma": "Caecina", "uri": "59205", "pos": "n", "morpho": "n-s---fn1-"},
    "caecus1": {"lemma": "caecus", "uri": "c0080", "pos": "a", "morpho": "aps---mn1-"},
    "caelestinus1": {"lemma": "caelestinus", "uri": "c0089", "pos": "a", "morpho": "aps---mn1-"},
    "caeparius1": {"lemma": "caeparius", "uri": "c0541", "pos": "n", "morpho": "n-s---mn2-"},
    "caeruleus1": {"lemma": "caeruleus", "uri": "c0626", "pos": "a", "morpho": "aps---mn1-"},
    "Caeruleus2": {"lemma": "Caeruleus", "uri": "59214", "pos": "n", "morpho": "n-s---mn2-"},
    "caesius1": {"lemma": "caesius", "uri": "c0137", "pos": "a", "morpho": "aps---mn1-"},
    "Caesius2": {"lemma": "Caesius", "uri": "59218", "pos": "n", "morpho": "n-s---mn2-"},
    "caesus1": {"lemma": "caesus", "uri": "104045", "pos": "a", "morpho": "aps---mn1-"},
    "caesus2": {"lemma": "caesus", "uri": "c9913", "pos": "n", "morpho": "n-s---mn4-"},
    "caia2": {"lemma": "caia", "uri": "c0150", "pos": "n", "morpho": "n-s---fn1-"},
    "calcatus1": {"lemma": "calcatus", "uri": "20551", "pos": "a", "morpho": "aps---mn1-"},
    "calcatus2": {"lemma": "calcatus", "uri": "c0221", "pos": "n", "morpho": "n-s---mn4-"},
    "calceatus1": {"lemma": "calceatus", "uri": "104072", "pos": "a", "morpho": "aps---mn1-"},
    "calceatus2": {"lemma": "calceatus", "uri": "c9980", "pos": "n", "morpho": "n-s---mn4-"},
    "calcitro1": {"lemma": "calcitro", "uri": "c0200", "pos": "v", "morpho": "v1spia--1-"},
    "calcitro2": {"lemma": "calcitro", "uri": "c0201", "pos": "n", "morpho": "n-s---mn3-"},
    "calculatio1": {"lemma": "calculatio", "uri": "c0204", "pos": "n", "morpho": "n-s---fn3-"},
    "calculatio2": {"lemma": "calculatio", "uri": "c0204", "pos": "n", "morpho": "n-s---fn3-"},
    "calculo1": {"lemma": "calculo", "uri": "c0209", "pos": "v", "morpho": "v1spia--1-"},
    "calculo2": {"lemma": "calculo", "uri": "c0210", "pos": "n", "morpho": "n-s---mn3-"},
    "caldus1": {"lemma": "caldus", "uri": "52842", "pos": "a", "morpho": "aps---mn1-"},
    "Caldus2": {"lemma": "Caldus", "uri": "59231", "pos": "n", "morpho": "n-s---mn2-"},
    "calefactus1": {"lemma": "calefactus", "uri": "33490", "pos": "a", "morpho": "aps---mn1-"},
    "calefactus2": {"lemma": "calefactus", "uri": "c9982", "pos": "n", "morpho": "n-s---mn4-"},
    "caligo1": {"lemma": "caligo", "uri": "c0239", "pos": "n", "morpho": "n-s---fn3-"},
    "caligo2": {"lemma": "caligo", "uri": "c0240", "pos": "v", "morpho": "v1spia--1-"},
    "calo2": {"lemma": "calo", "uri": "c1152", "pos": "n", "morpho": "n-s---mn3-"},
    "calor1": {"lemma": "calor", "uri": "c0276", "pos": "n", "morpho": "n-s---mn3-"},
    "Calor2": {"lemma": "Calor", "uri": "59258", "pos": "n", "morpho": "n-s---mn3-"},
    "calvus1": {"lemma": "caluus", "uri": "c2611", "pos": "a", "morpho": "aps---mn1-"},
    "calyx1": {"lemma": "calyx", "uri": "c0306", "pos": "n", "morpho": "n-s---mn3-"},
    "calyx2": {"lemma": "calyx", "uri": "c0306", "pos": "n", "morpho": "n-s---mn3-"},
    "camilla1": {"lemma": "camilla", "uri": "c0319", "pos": "n", "morpho": "n-s---fn1-"},
    "camillum1": {"lemma": "camillum", "uri": "104145", "pos": "n", "morpho": "n-s---nn2-"},
    "camillum2": {"lemma": "camillum", "uri": "104145", "pos": "n", "morpho": "n-s---nn2-"},
    "camillus1": {"lemma": "camillus", "uri": "c0422", "pos": "n", "morpho": "n-s---mn2-"},
    "Camillus2": {"lemma": "Camillus", "uri": "59273", "pos": "n", "morpho": "n-s---mn2-"},
    "campana1": {"lemma": "campana", "uri": "c9916", "pos": "n", "morpho": "n-s---fn1-"},
    "campus1": {"lemma": "campus", "uri": "c1593", "pos": "n", "morpho": "n-s---mn2-"},
    "campus2": {"lemma": "campus", "uri": "c1593", "pos": "n", "morpho": "n-s---mn2-"},
    "cancellarius1": {"lemma": "cancellarius", "uri": "c0369", "pos": "n", "morpho": "n-s---mn2-"},
    "cancellarius2": {"lemma": "cancellarius", "uri": "c0369", "pos": "a", "morpho": "aps---mn1-"},
    "cancer1": {"lemma": "cancer", "uri": "c0375", "pos": "n", "morpho": "n-s---mn2r"},
    "cancer2": {"lemma": "cancer", "uri": "c0375", "pos": "n", "morpho": "n-s---mn2r"},
    "candidatus1": {"lemma": "candidatus", "uri": "c9722", "pos": "a", "morpho": "aps---mn1-"},
    "candidatus2": {"lemma": "candidatus", "uri": "c9721", "pos": "n", "morpho": "n-s---mn4-"},
    "canens1": {"lemma": "canens", "uri": "104185", "pos": "a", "morpho": "aps---an3i"},
    "canens2": {"lemma": "canens", "uri": "104185", "pos": "a", "morpho": "aps---an3i"},
    "Canens3": {"lemma": "Canens", "uri": "59281", "pos": "n", "morpho": "n-s---fn3-"},
    "canis1": {"lemma": "canis", "uri": "20611", "pos": "n", "morpho": "n-s---mn3-"},
    "Canis2": {"lemma": "Canis", "uri": "59285", "pos": "n", "morpho": "n-s---fn3-"},
    "Canopus1": {"lemma": "Canopus", "uri": "59289", "pos": "n", "morpho": "n-s---mn2-"},
    "Canopus2": {"lemma": "Canopus", "uri": "59289", "pos": "n", "morpho": "n-s---mn2-"},
    "canthus1": {"lemma": "canthus", "uri": "c0456", "pos": "n", "morpho": "n-s---mn2-"},
    "Canthus2": {"lemma": "Canthus", "uri": "59294", "pos": "n", "morpho": "n-s---mn2-"},
    "capella1": {"lemma": "capella", "uri": "c0480", "pos": "n", "morpho": "n-s---fn1-"},
    "Capella2": {"lemma": "Capella", "uri": "59297", "pos": "n", "morpho": "n-s---fn1-"},
    "capillor1": {"lemma": "capillor", "uri": "104237", "pos": "n", "morpho": "n-s---mn3-"},
    "capillor2": {"lemma": "capillor", "uri": "104237", "pos": "n", "morpho": "n-s---mn3-"},
    "capio1": {"lemma": "capio", "uri": "c0500", "pos": "v", "morpho": "v1spia--3i"},
    "capio2": {"lemma": "capio", "uri": "c0501", "pos": "n", "morpho": "n-s---fn3-"},
    "capitium1": {"lemma": "capitium", "uri": "c0515", "pos": "n", "morpho": "n-s---nn2-"},
    "Capitium2": {"lemma": "Capitium", "uri": "59303", "pos": "n", "morpho": "n-s---nn2-"},
    "capito1": {"lemma": "capito", "uri": "c0516", "pos": "n", "morpho": "n-s---mn3-"},
    "Capito2": {"lemma": "Capito", "uri": "59304", "pos": "n", "morpho": "n-s---mn3-"},
    "capitulum1": {"lemma": "capitulum", "uri": "c0522", "pos": "n", "morpho": "n-s---nn2-"},
    "Capitulum2": {"lemma": "Capitulum", "uri": "59307", "pos": "n", "morpho": "n-s---nn2-"},
    "capsa1": {"lemma": "capsa", "uri": "c0557", "pos": "n", "morpho": "n-s---fn1-"},
    "captus1": {"lemma": "captus", "uri": "104282", "pos": "a", "morpho": "aps---mn1-"},
    "captus2": {"lemma": "captus", "uri": "c9984", "pos": "n", "morpho": "n-s---mn4-"},
    "capulo1": {"lemma": "capulo", "uri": "c3549", "pos": "v", "morpho": "v1spia--1-"},
    "capulo2": {"lemma": "capulo", "uri": "c3549", "pos": "v", "morpho": "v1spia--1-"},
    "carabus1": {"lemma": "carabus", "uri": "c4053", "pos": "n", "morpho": "n-s---mn2-"},
    "carabus2": {"lemma": "carabus", "uri": "c4053", "pos": "n", "morpho": "n-s---mn2-"},
    "carbo1": {"lemma": "carbo", "uri": "c0599", "pos": "n", "morpho": "n-s---mn3-"},
    "Carbo2": {"lemma": "Carbo", "uri": "59314", "pos": "n", "morpho": "n-s---mn3-"},
    "carina1": {"lemma": "carina", "uri": "c0643", "pos": "n", "morpho": "n-s---fn1-"},
    "Carina2": {"lemma": "Carina", "uri": "59319", "pos": "n", "morpho": "n-s---fn1-"},
    "Carina3": {"lemma": "Carina", "uri": "59319", "pos": "n", "morpho": "n-s---fn1-"},
    "carmen1": {"lemma": "carmen", "uri": "c4060", "pos": "n", "morpho": "n-s---nn3-"},
    "carmen2": {"lemma": "carmen", "uri": "c4060", "pos": "n", "morpho": "n-s---nn3-"},
    "carmino1": {"lemma": "carmino", "uri": "c4412", "pos": "v", "morpho": "v1spia--1-"},
    "carmino2": {"lemma": "carmino", "uri": "c4412", "pos": "v", "morpho": "v1spia--1-"},
    "caro1": {"lemma": "caro", "uri": "c0680", "pos": "v", "morpho": "v1spia--3-"},
    "caro2": {"lemma": "caro", "uri": "c0681", "pos": "n", "morpho": "n-s---fn3-"},
    "caro3": {"lemma": "caro", "uri": "104340", "pos": "r", "morpho": "rp--------"},
    "carruca1": {"lemma": "carruca", "uri": "c0710", "pos": "n", "morpho": "n-s---fn1-"},
    "Carthago1": {"lemma": "Carthago", "uri": "20701", "pos": "n", "morpho": "n-s---fn3-"},
    "Carthago2": {"lemma": "Carthago", "uri": "20701", "pos": "n", "morpho": "n-s---fn3-"},
    "carus1": {"lemma": "carus", "uri": "c0721", "pos": "a", "morpho": "aps---mn1-"},
    "casnar1": {"lemma": "casnar", "uri": "c0731", "pos": "n", "morpho": "n-s---mn3-"},
    "casnar2": {"lemma": "casnar", "uri": "c0731", "pos": "n", "morpho": "n-s---mn3-"},
    "Cassiope1": {"lemma": "Cassiope", "uri": "59342", "pos": "n", "morpho": "n-s---fn1-"},
    "Cassiope2": {"lemma": "Cassiope", "uri": "59342", "pos": "n", "morpho": "n-s---fn1-"},
    "cassis1": {"lemma": "cassis", "uri": "c0753", "pos": "n", "morpho": "n-s---fn3-"},
    "cassis2": {"lemma": "cassis", "uri": "c0753", "pos": "n", "morpho": "n-s---fn3-"},
    "casso1": {"lemma": "casso", "uri": "q0155", "pos": "v", "morpho": "v1spia--1-"},
    "casso2": {"lemma": "casso", "uri": "q0155", "pos": "v", "morpho": "v1spia--1-"},
    "castor1": {"lemma": "castor", "uri": "c0783", "pos": "n", "morpho": "n-s---mn3-"},
    "Castor2": {"lemma": "Castor", "uri": "59347", "pos": "n", "morpho": "n-s---mn3-"},
    "castus1": {"lemma": "castus", "uri": "c0798", "pos": "a", "morpho": "aps---mn1-"},
    "castus2": {"lemma": "castus", "uri": "c0798", "pos": "n", "morpho": "n-s---mn4-"},
    "casus1": {"lemma": "casus", "uri": "c9985", "pos": "n", "morpho": "n-s---mn4-"},
    "Casus2": {"lemma": "Casus", "uri": "59349", "pos": "n", "morpho": "n-s---mn2-"},
    "catella1": {"lemma": "catella", "uri": "c0871", "pos": "n", "morpho": "n-s---fn1-"},
    "catella2": {"lemma": "catella", "uri": "c0871", "pos": "n", "morpho": "n-s---fn1-"},
    "catellus1": {"lemma": "catellus", "uri": "c0871", "pos": "n", "morpho": "n-s---mn2-"},
    "catellus2": {"lemma": "catellus", "uri": "c0871", "pos": "n", "morpho": "n-s---mn2-"},
    "catillo1": {"lemma": "catillo", "uri": "c0898", "pos": "v", "morpho": "v1spia--1-"},
    "catillo2": {"lemma": "catillo", "uri": "c0899", "pos": "n", "morpho": "n-s---mn3-"},
    "catillus1": {"lemma": "catillus", "uri": "c0900", "pos": "n", "morpho": "n-s---mn2-"},
    "catulinus1": {"lemma": "catulinus", "uri": "c0920", "pos": "a", "morpho": "aps---mn1-"},
    "catulus1": {"lemma": "catulus", "uri": "c0923", "pos": "n", "morpho": "n-s---mn2-"},
    "catus1": {"lemma": "catus", "uri": "c0925", "pos": "a", "morpho": "aps---mn1-"},
    "catus2": {"lemma": "catus", "uri": "97850", "pos": "n", "morpho": "n-s---mn2-"},
    "caudex1": {"lemma": "caudex", "uri": "c0937", "pos": "n", "morpho": "n-s---mn3-"},
    "cedo1": {"lemma": "cedo", "uri": "c1031", "pos": "v", "morpho": "v1spia--3-"},
    "cedo2": {"lemma": "cedo", "uri": "c1031", "pos": "v", "morpho": "v1spia--3-"},
    "celer1": {"lemma": "celer", "uri": "c1051", "pos": "a", "morpho": "aps---an3-"},
    "Celer2": {"lemma": "Celer", "uri": "59372", "pos": "n", "morpho": "n-s---mn3-"},
    "Celer3": {"lemma": "Celer", "uri": "59372", "pos": "n", "morpho": "n-s---mn3-"},
    "cello1": {"lemma": "cello", "uri": "104533", "pos": "v", "morpho": "v1spia--3-"},
    "cello2": {"lemma": "cello", "uri": "104533", "pos": "v", "morpho": "v1spia--3-"},
    "celsus1": {"lemma": "celsus", "uri": "c1085", "pos": "a", "morpho": "aps---mn1-"},
    "censeo1": {"lemma": "censeo", "uri": "c1119", "pos": "v", "morpho": "v1spia--2-"},
    "censeo2": {"lemma": "censeo", "uri": "c1119", "pos": "v", "morpho": "v1spia--2-"},
    "census1": {"lemma": "census", "uri": "104558", "pos": "a", "morpho": "aps---mn1-"},
    "census2": {"lemma": "census", "uri": "c1130", "pos": "n", "morpho": "n-s---mn4-"},
    "cento1": {"lemma": "cento", "uri": "c1150", "pos": "n", "morpho": "n-s---mn3-"},
    "Cento2": {"lemma": "Cento", "uri": "59384", "pos": "n", "morpho": "n-s---mn3-"},
    "centuriatus1": {"lemma": "centuriatus", "uri": "57877", "pos": "a", "morpho": "aps---mn1-"},
    "centuriatus2": {"lemma": "centuriatus", "uri": "c4468", "pos": "n", "morpho": "n-s---mn4-"},
    "centurio1": {"lemma": "centurio", "uri": "c1169", "pos": "v", "morpho": "v1spia--1-"},
    "Ceramicus1": {"lemma": "Ceramicus", "uri": "59392", "pos": "n", "morpho": "n-s---mn2-"},
    "Ceramicus2": {"lemma": "Ceramicus", "uri": "59392", "pos": "n", "morpho": "n-s---mn2-"},
    "cerasus1": {"lemma": "cerasus", "uri": "c1206", "pos": "n", "morpho": "n-s---fn2-"},
    "ceraunus1": {"lemma": "ceraunus", "uri": "c9106", "pos": "n", "morpho": "n-s---mn2-"},
    "cereus1": {"lemma": "cereus", "uri": "c1233", "pos": "a", "morpho": "aps---mn1-"},
    "cereus2": {"lemma": "cereus", "uri": "c1233", "pos": "n", "morpho": "n-s---mn2-"},
    "cernuus1": {"lemma": "cernuus", "uri": "c1249", "pos": "a", "morpho": "aps---mn1-"},
    "cernuus2": {"lemma": "cernuus", "uri": "c1249", "pos": "n", "morpho": "n-s---mn2-"},
    "certatus1": {"lemma": "certatus", "uri": "104635", "pos": "a", "morpho": "aps---mn1-"},
    "certatus2": {"lemma": "certatus", "uri": "c1310", "pos": "n", "morpho": "n-s---mn4-"},
    "certo1": {"lemma": "certo", "uri": "20833", "pos": "r", "morpho": "rp--------"},
    "certo2": {"lemma": "certo", "uri": "c1274", "pos": "v", "morpho": "v1spia--1-"},
    "cestus1": {"lemma": "cestus", "uri": "50303", "pos": "n", "morpho": "n-s---mn2-"},
    "chalcis1": {"lemma": "chalcis", "uri": "c1338", "pos": "n", "morpho": "n-s---fn3-"},
    "Chalcis2": {"lemma": "Chalcis", "uri": "59416", "pos": "n", "morpho": "n-s---fn3-"},
    "chalybs1": {"lemma": "chalybs", "uri": "c1343", "pos": "n", "morpho": "n-s---mn3-"},
    "chelonitis1": {"lemma": "chelonitis", "uri": "c1419", "pos": "n", "morpho": "n-s---fn3-"},
    "Chelonitis2": {"lemma": "Chelonitis", "uri": "59432", "pos": "n", "morpho": "n-s---fn3-"},
    "Chilo1": {"lemma": "Chilo", "uri": "59435", "pos": "n", "morpho": "n-s---mn3-"},
    "Chilo2": {"lemma": "Chilo", "uri": "59435", "pos": "n", "morpho": "n-s---mn3-"},
    "chordus1": {"lemma": "chordus", "uri": "58352", "pos": "a", "morpho": "aps---mn1-"},
    "Chordus2": {"lemma": "Chordus", "uri": "59448", "pos": "n", "morpho": "n-s---mn2-"},
    "cicuta1": {"lemma": "cicuta", "uri": "c1600", "pos": "n", "morpho": "n-s---fn1-"},
    "cillo1": {"lemma": "cillo", "uri": "c1613", "pos": "v", "morpho": "v1spia--3-"},
    "cillo2": {"lemma": "cillo", "uri": "104857", "pos": "n", "morpho": "n-s---mn3-"},
    "cilo1": {"lemma": "cilo", "uri": "c1615", "pos": "n", "morpho": "n-s---mn3-"},
    "Cilo2": {"lemma": "Cilo", "uri": "59462", "pos": "n", "morpho": "n-s---mn3-"},
    "cinaedus1": {"lemma": "cinaedus", "uri": "c1631", "pos": "n", "morpho": "n-s---mn2-"},
    "cinaedus2": {"lemma": "cinaedus", "uri": "c1631", "pos": "a", "morpho": "aps---mn1-"},
    "cinara1": {"lemma": "cinara", "uri": "c1632", "pos": "n", "morpho": "n-s---fn1-"},
    "cincinnatus1": {"lemma": "cincinnatus", "uri": "c1636", "pos": "a", "morpho": "aps---mn1-"},
    "Cincinnatus2": {"lemma": "Cincinnatus", "uri": "59468", "pos": "n", "morpho": "n-s---mn2-"},
    "cinctus1": {"lemma": "cinctus", "uri": "104874", "pos": "a", "morpho": "aps---mn1-"},
    "cinctus2": {"lemma": "cinctus", "uri": "c9988", "pos": "n", "morpho": "n-s---mn4-"},
    "cingulum1": {"lemma": "cingulum", "uri": "c1652", "pos": "n", "morpho": "n-s---nn2-"},
    "Cingulum2": {"lemma": "Cingulum", "uri": "59470", "pos": "n", "morpho": "n-s---nn2-"},
    "circa1": {"lemma": "circa", "uri": "c1668", "pos": "p", "morpho": "p---------"},
    "circuitus1": {"lemma": "circuitus", "uri": "104899", "pos": "a", "morpho": "aps---mn1-"},
    "circuitus2": {"lemma": "circuitus", "uri": "20906", "pos": "n", "morpho": "n-s---mn4-"},
    "circumactus1": {"lemma": "circumactus", "uri": "104904", "pos": "a", "morpho": "aps---mn1-"},
    "circumactus2": {"lemma": "circumactus", "uri": "c1716", "pos": "n", "morpho": "n-s---mn4-"},
    "circumductus1": {"lemma": "circumductus", "uri": "104930", "pos": "a", "morpho": "aps---mn1-"},
    "circumductus2": {"lemma": "circumductus", "uri": "c9990", "pos": "n", "morpho": "n-s---mn4-"},
    "circumflexus1": {"lemma": "circumflexus", "uri": "104937", "pos": "a", "morpho": "aps---mn1-"},
    "circumflexus2": {"lemma": "circumflexus", "uri": "c9991", "pos": "n", "morpho": "n-s---mn4-"},
    "circumgressus1": {"lemma": "circumgressus", "uri": "104942", "pos": "a", "morpho": "aps---mn1-"},
    "circumgressus2": {"lemma": "circumgressus", "uri": "c9992", "pos": "n", "morpho": "n-s---mn4-"},
    "circumjectus1": {"lemma": "circumiectus", "uri": "55504", "pos": "a", "morpho": "aps---mn1-"},
    "circumjectus2": {"lemma": "circumiectus", "uri": "c9993", "pos": "n", "morpho": "n-s---mn4-"},
    "circumplexus1": {"lemma": "circumplexus", "uri": "104983", "pos": "a", "morpho": "aps---mn1-"},
    "circumplexus2": {"lemma": "circumplexus", "uri": "c1799", "pos": "n", "morpho": "n-s---mn4-"},
    "circumspectus1": {"lemma": "circumspectus", "uri": "20952", "pos": "a", "morpho": "aps---mn1-"},
    "circumspectus2": {"lemma": "circumspectus", "uri": "c1885", "pos": "n", "morpho": "n-s---mn4-"},
    "cito1": {"lemma": "cito", "uri": "20971", "pos": "r", "morpho": "rp--------"},
    "cito2": {"lemma": "cito", "uri": "c1991", "pos": "v", "morpho": "v1spia--1-"},
    "citratus1": {"lemma": "citratus", "uri": "c4640", "pos": "a", "morpho": "aps---mn1-"},
    "citratus2": {"lemma": "citratus", "uri": "c4640", "pos": "a", "morpho": "aps---mn1-"},
    "civilis1": {"lemma": "ciuilis", "uri": "c2006", "pos": "a", "morpho": "aps---cn3i"},
    "claritas1": {"lemma": "claritas", "uri": "c2041", "pos": "n", "morpho": "n-s---fn3-"},
    "clausula1": {"lemma": "clausula", "uri": "c2078", "pos": "n", "morpho": "n-s---fn1-"},
    "clausus1": {"lemma": "clausus", "uri": "21002", "pos": "a", "morpho": "aps---mn1-"},
    "Clausus2": {"lemma": "Clausus", "uri": "59493", "pos": "n", "morpho": "n-s---mn2-"},
    "claviger1": {"lemma": "clauiger", "uri": "c7933", "pos": "a", "morpho": "aps---mn1r"},
    "claviger2": {"lemma": "clauiger", "uri": "31489", "pos": "n", "morpho": "n-s---mn2r"},
    "clemens1": {"lemma": "clemens", "uri": "c2085", "pos": "a", "morpho": "aps---an3i"},
    "Clitae1": {"lemma": "Clitae", "uri": "59505", "pos": "n", "morpho": "n-p---fn1-"},
    "Clitae2": {"lemma": "Clitae", "uri": "59505", "pos": "n", "morpho": "n-p---fn1-"},
    "cluo1": {"lemma": "cluo", "uri": "c7146", "pos": "v", "morpho": "v1spia--3-"},
    "cluo2": {"lemma": "cluo", "uri": "c7146", "pos": "v", "morpho": "v1spia--3-"},
    "Coa1": {"lemma": "Coa", "uri": "48414", "pos": "n", "morpho": "n-s---fn1-"},
    "Coa2": {"lemma": "Coa", "uri": "48414", "pos": "n", "morpho": "n-s---fn1-"},
    "coactus1": {"lemma": "coactus", "uri": "50379", "pos": "a", "morpho": "aps---mn1-"},
    "coactus2": {"lemma": "coactus", "uri": "c9997", "pos": "n", "morpho": "n-s---mn4-"},
    "coalitus1": {"lemma": "coalitus", "uri": "105195", "pos": "a", "morpho": "aps---mn1-"},
    "coalitus2": {"lemma": "coalitus", "uri": "c9998", "pos": "n", "morpho": "n-s---mn4-"},
    "coaxo1": {"lemma": "coaxo", "uri": "c2241", "pos": "v", "morpho": "v1spia--1-"},
    "coaxo2": {"lemma": "coaxo", "uri": "c2241", "pos": "v", "morpho": "v1spia--1-"},
    "Cocles2": {"lemma": "Cocles", "uri": "105238", "pos": "n", "morpho": "n-s---mn3-"},
    "coctio1": {"lemma": "coctio", "uri": "c7249", "pos": "n", "morpho": "n-s---fn3-"},
    "coctio2": {"lemma": "coctio", "uri": "c7249", "pos": "n", "morpho": "n-s---fn3-"},
    "coeptus1": {"lemma": "coeptus", "uri": "c9999", "pos": "n", "morpho": "n-s---mn4-"},
    "coeptus2": {"lemma": "coeptus", "uri": "c9999", "pos": "n", "morpho": "n-s---mn4-"},
    "cogitatus1": {"lemma": "cogitatus", "uri": "105294", "pos": "a", "morpho": "aps---mn1-"},
    "cogitatus2": {"lemma": "cogitatus", "uri": "c9859", "pos": "n", "morpho": "n-s---mn4-"},
    "cognitus1": {"lemma": "cognitus", "uri": "21066", "pos": "a", "morpho": "aps---mn1-"},
    "cognitus2": {"lemma": "cognitus", "uri": "c9860", "pos": "n", "morpho": "n-s---mn4-"},
    "cohum1": {"lemma": "cohum", "uri": "c4308", "pos": "n", "morpho": "n-s---nn2-"},
    "cohum2": {"lemma": "cohum", "uri": "c4308", "pos": "n", "morpho": "n-s---nn2-"},
    "coitus1": {"lemma": "coitus", "uri": "105332", "pos": "a", "morpho": "aps---mn1-"},
    "coitus2": {"lemma": "coitus", "uri": "c2292", "pos": "n", "morpho": "n-s---mn4-"},
    "collatus1": {"lemma": "collatus", "uri": "c9863", "pos": "n", "morpho": "n-s---mn4-"},
    "collatus2": {"lemma": "collatus", "uri": "c9863", "pos": "n", "morpho": "n-s---mn4-"},
    "collectus1": {"lemma": "collectus", "uri": "97926", "pos": "a", "morpho": "aps---mn1-"},
    "collectus2": {"lemma": "collectus", "uri": "c9936", "pos": "n", "morpho": "n-s---mn4-"},
    "colligo1": {"lemma": "colligo", "uri": "c2426", "pos": "v", "morpho": "v1spia--3-"},
    "colligo2": {"lemma": "colligo", "uri": "c2425", "pos": "v", "morpho": "v1spia--1-"},
    "collina1": {"lemma": "collina", "uri": "c2433", "pos": "n", "morpho": "n-s---fn1-"},
    "collisus1": {"lemma": "collisus", "uri": "105380", "pos": "a", "morpho": "aps---mn1-"},
    "collisus2": {"lemma": "collisus", "uri": "c9864", "pos": "n", "morpho": "n-s---mn4-"},
    "colo1": {"lemma": "colo", "uri": None, "pos": "v", "morpho": "v1spia--3-"},
    "colo2": {"lemma": "colo", "uri": "c2479", "pos": "v", "morpho": "v1spia--1-"},
    "colonia1": {"lemma": "colonia", "uri": "c2494", "pos": "n", "morpho": "n-s---fn1-"},
    "Colophon1": {"lemma": "Colophon", "uri": "59533", "pos": "n", "morpho": "n-s---nn3-"},
    "colophon2": {"lemma": "colophon", "uri": "c2498", "pos": "n", "morpho": "n-s---mn3-"},
    "colotes1": {"lemma": "colotes", "uri": "c2514", "pos": "n", "morpho": "n-s---mn1g"},
    "Colotes2": {"lemma": "Colotes", "uri": "59535", "pos": "n", "morpho": "n-p---mn3-"},
    "colum1": {"lemma": "colum", "uri": "c2520", "pos": "n", "morpho": "n-s---nn2-"},
    "colum2": {"lemma": "colum", "uri": "c2520", "pos": "n", "morpho": "n-s---nn2-"},
    "columella1": {"lemma": "columella", "uri": "c2531", "pos": "n", "morpho": "n-s---fn1-"},
    "combibo1": {"lemma": "combibo", "uri": "c2560", "pos": "v", "morpho": "v1spia--3-"},
    "combibo2": {"lemma": "combibo", "uri": "c2561", "pos": "n", "morpho": "n-s---mn3-"},
    "come1": {"lemma": "come", "uri": "c2568", "pos": "n", "morpho": "n-s---fn1g"},
    "comedo1": {"lemma": "comedo", "uri": "c2569", "pos": "v", "morpho": "v1spia--3-"},
    "comedo2": {"lemma": "comedo", "uri": "c2570", "pos": "n", "morpho": "n-s---mn3-"},
    "comesus1": {"lemma": "comesus", "uri": "105455", "pos": "a", "morpho": "aps---mn1-"},
    "comesus2": {"lemma": "comesus", "uri": "c9865", "pos": "n", "morpho": "n-s---mn4-"},
    "cometes1": {"lemma": "cometes", "uri": "c2576", "pos": "n", "morpho": "n-s---mn1g"},
    "Cometes2": {"lemma": "Cometes", "uri": "59538", "pos": "n", "morpho": "n-p---mn3-"},
    "Cominius1": {"lemma": "Cominius", "uri": "59540", "pos": "n", "morpho": "n-s---mn2-"},
    "comitatus1": {"lemma": "comitatus", "uri": "45884", "pos": "a", "morpho": "aps---mn1-"},
    "comitatus2": {"lemma": "comitatus", "uri": "c2588", "pos": "n", "morpho": "n-s---mn4-"},
    "comitiatus1": {"lemma": "comitiatus", "uri": "30852", "pos": "n", "morpho": "n-s---mn2-"},
    "comitiatus2": {"lemma": "comitiatus", "uri": "c9866", "pos": "n", "morpho": "n-s---mn4-"},
    "commensus1": {"lemma": "commensus", "uri": "105497", "pos": "a", "morpho": "aps---mn1-"},
    "commensus2": {"lemma": "commensus", "uri": "c9868", "pos": "n", "morpho": "n-s---mn4-"},
    "commentor1": {"lemma": "commentor", "uri": "c2656", "pos": "v", "morpho": "v1spid--1-"},
    "commentor2": {"lemma": "commentor", "uri": "c2657", "pos": "n", "morpho": "n-s---mn3-"},
    "commeto1": {"lemma": "commeto", "uri": "c3528", "pos": "v", "morpho": "v1spia--1-"},
    "commeto2": {"lemma": "commeto", "uri": "c3528", "pos": "v", "morpho": "v1spia--1-"},
    "commilito1": {"lemma": "commilito", "uri": "c2672", "pos": "n", "morpho": "n-s---mn3-"},
    "commilito2": {"lemma": "commilito", "uri": "c2671", "pos": "v", "morpho": "v1spia--1-"},
    "commodo1": {"lemma": "commodo", "uri": "97946", "pos": "r", "morpho": "rp--------"},
    "commodo2": {"lemma": "commodo", "uri": "c2704", "pos": "v", "morpho": "v1spia--1-"},
    "commodulum1": {"lemma": "commodulum", "uri": "c2707", "pos": "n", "morpho": "n-s---nn2-"},
    "commodum1": {"lemma": "commodum", "uri": "c2708", "pos": "n", "morpho": "n-s---nn2-"},
    "commodum2": {"lemma": "commodum", "uri": "21210", "pos": "r", "morpho": "rp--------"},
    "commodus1": {"lemma": "commodus", "uri": "c2708", "pos": "a", "morpho": "aps---mn1-"},
    "commolitus1": {"lemma": "commolitus", "uri": "105535", "pos": "a", "morpho": "aps---mn1-"},
    "commolitus2": {"lemma": "commolitus", "uri": "105535", "pos": "a", "morpho": "aps---mn1-"},
    "commotus1": {"lemma": "commotus", "uri": "97947", "pos": "a", "morpho": "aps---mn1-"},
    "commotus2": {"lemma": "commotus", "uri": "c9869", "pos": "n", "morpho": "n-s---mn4-"},
    "communicatus1": {"lemma": "communicatus", "uri": "105555", "pos": "a", "morpho": "aps---mn1-"},
    "communicatus2": {"lemma": "communicatus", "uri": "c9870", "pos": "n", "morpho": "n-s---mn4-"},
    "communio1": {"lemma": "communio", "uri": "c2746", "pos": "v", "morpho": "v1spia--4-"},
    "communio2": {"lemma": "communio", "uri": "c2747", "pos": "n", "morpho": "n-s---fn3-"},
    "communitus1": {"lemma": "communitus", "uri": "c2751", "pos": "r", "morpho": "rp--------"},
    "communitus2": {"lemma": "communitus", "uri": "105558", "pos": "a", "morpho": "aps---mn1-"},
    "como1": {"lemma": "como", "uri": "c2757", "pos": "v", "morpho": "v1spia--3-"},
    "como2": {"lemma": "como", "uri": "c2758", "pos": "v", "morpho": "v1spia--1-"},
    "compactus1": {"lemma": "compactus", "uri": "21238", "pos": "a", "morpho": "aps---mn1-"},
    "compactus2": {"lemma": "compactus", "uri": "21238", "pos": "a", "morpho": "aps---mn1-"},
    "comparaticius1": {"lemma": "comparaticius", "uri": "c4723", "pos": "a", "morpho": "aps---mn1-"},
    "comparaticius2": {"lemma": "comparaticius", "uri": "c4723", "pos": "a", "morpho": "aps---mn1-"},
    "comparatio1": {"lemma": "comparatio", "uri": "c4786", "pos": "n", "morpho": "n-s---fn3-"},
    "comparatio2": {"lemma": "comparatio", "uri": "c4786", "pos": "n", "morpho": "n-s---fn3-"},
    "comparator1": {"lemma": "comparator", "uri": "c4804", "pos": "n", "morpho": "n-s---mn3-"},
    "comparator2": {"lemma": "comparator", "uri": "c4804", "pos": "n", "morpho": "n-s---mn3-"},
    "comparo1": {"lemma": "comparo", "uri": "c4812", "pos": "v", "morpho": "v1spia--1-"},
    "comparo2": {"lemma": "comparo", "uri": "c4812", "pos": "v", "morpho": "v1spia--1-"},
    "compello1": {"lemma": "compello", "uri": "c2810", "pos": "v", "morpho": "v1spia--3-"},
    "compello2": {"lemma": "compello", "uri": "c2811", "pos": "v", "morpho": "v1spia--1-"},
    "compertus1": {"lemma": "compertus", "uri": "41846", "pos": "a", "morpho": "aps---mn1-"},
    "compertus2": {"lemma": "compertus", "uri": "42075", "pos": "n", "morpho": "n-s---mn4-"},
    "compes1": {"lemma": "compes", "uri": "105601", "pos": "a", "morpho": "aps---an3-"},
    "compes2": {"lemma": "compes", "uri": "105601", "pos": "a", "morpho": "aps---an3-"},
    "compingo1": {"lemma": "compingo", "uri": "c2841", "pos": "v", "morpho": "v1spia--3-"},
    "compingo2": {"lemma": "compingo", "uri": "c2841", "pos": "v", "morpho": "v1spia--3-"},
    "complexus1": {"lemma": "complexus", "uri": "105620", "pos": "a", "morpho": "aps---mn1-"},
    "complexus2": {"lemma": "complexus", "uri": "c9874", "pos": "n", "morpho": "n-s---mn4-"},
    "compressus1": {"lemma": "compressus", "uri": "21291", "pos": "a", "morpho": "aps---mn1-"},
    "compressus2": {"lemma": "compressus", "uri": "c9876", "pos": "n", "morpho": "n-s---mn4-"},
    "comptus1": {"lemma": "comptus", "uri": "21296", "pos": "a", "morpho": "aps---mn1-"},
    "comptus2": {"lemma": "comptus", "uri": "c9877", "pos": "n", "morpho": "n-s---mn4-"},
    "comptus3": {"lemma": "comptus", "uri": "c9877", "pos": "n", "morpho": "n-s---mn4-"},
    "compulsus1": {"lemma": "compulsus", "uri": "105666", "pos": "a", "morpho": "aps---mn1-"},
    "compulsus2": {"lemma": "compulsus", "uri": "105667", "pos": "n", "morpho": "n-s---mn4-"},
    "comtus1": {"lemma": "comtus", "uri": "30749", "pos": "a", "morpho": "aps---mn1-"},
    "comtus2": {"lemma": "comtus", "uri": "35550", "pos": "n", "morpho": "n-s---mn4-"},
    "conceptus1": {"lemma": "conceptus", "uri": "c9881", "pos": "n", "morpho": "n-s---mn4-"},
    "conceptus2": {"lemma": "conceptus", "uri": "c9881", "pos": "n", "morpho": "n-s---mn4-"},
    "concessus1": {"lemma": "concessus", "uri": "21331", "pos": "a", "morpho": "aps---mn1-"},
    "concessus2": {"lemma": "concessus", "uri": "c9882", "pos": "n", "morpho": "n-s---mn4-"},
    "conciliatus1": {"lemma": "conciliatus", "uri": "105726", "pos": "a", "morpho": "aps---mn1-"},
    "conciliatus2": {"lemma": "conciliatus", "uri": "c9883", "pos": "n", "morpho": "n-s---mn4-"},
    "concio1": {"lemma": "concio", "uri": "c3013", "pos": "v", "morpho": "v1spia--4-"},
    "concio2": {"lemma": "concio", "uri": "c3013", "pos": "v", "morpho": "v1spia--4-"},
    "concitatus1": {"lemma": "concitatus", "uri": "21355", "pos": "a", "morpho": "aps---mn1-"},
    "concitatus2": {"lemma": "concitatus", "uri": "c9884", "pos": "n", "morpho": "n-s---mn4-"},
    "concitus1": {"lemma": "concitus", "uri": "21359", "pos": "a", "morpho": "aps---mn1-"},
    "concitus2": {"lemma": "concitus", "uri": "105733", "pos": "n", "morpho": "n-s---mn4-"},
    "conclusus1": {"lemma": "conclusus", "uri": "21365", "pos": "a", "morpho": "aps---mn1-"},
    "conclusus2": {"lemma": "conclusus", "uri": "c9885", "pos": "n", "morpho": "n-s---mn4-"},
    "concordia1": {"lemma": "concordia", "uri": "c3063", "pos": "n", "morpho": "n-s---fn1-"},
    "Concordia2": {"lemma": "Concordia", "uri": "59547", "pos": "n", "morpho": "n-s---fn1-"},
    "concordialis1": {"lemma": "concordialis", "uri": "c3064", "pos": "a", "morpho": "aps---cn3i"},
    "concretus1": {"lemma": "concretus", "uri": "21377", "pos": "a", "morpho": "aps---mn1-"},
    "concretus2": {"lemma": "concretus", "uri": "c9886", "pos": "n", "morpho": "n-s---mn4-"},
    "concussus1": {"lemma": "concussus", "uri": "21395", "pos": "a", "morpho": "aps---mn1-"},
    "concussus2": {"lemma": "concussus", "uri": "c9890", "pos": "n", "morpho": "n-s---mn4-"},
    "conditura1": {"lemma": "conditura", "uri": "c3169", "pos": "n", "morpho": "n-s---fn1-"},
    "conditura2": {"lemma": "conditura", "uri": "c3169", "pos": "n", "morpho": "n-s---fn1-"},
    "conditus1": {"lemma": "conditus", "uri": "105823", "pos": "a", "morpho": "aps---mn1-"},
    "conditus2": {"lemma": "conditus", "uri": "105823", "pos": "a", "morpho": "aps---mn1-"},
    "conductus1": {"lemma": "conductus", "uri": "47142", "pos": "a", "morpho": "aps---mn1-"},
    "conductus2": {"lemma": "conductus", "uri": "c9893", "pos": "n", "morpho": "n-s---mn4-"},
    "conexus1": {"lemma": "conexus", "uri": "97979", "pos": "a", "morpho": "aps---mn1-"},
    "conexus2": {"lemma": "conexus", "uri": "c9894", "pos": "n", "morpho": "n-s---mn4-"},
    "conflictus1": {"lemma": "conflictus", "uri": "105883", "pos": "a", "morpho": "aps---mn1-"},
    "conflictus2": {"lemma": "conflictus", "uri": "c9896", "pos": "n", "morpho": "n-s---mn4-"},
    "congener1": {"lemma": "congener", "uri": "c3347", "pos": "a", "morpho": "aps---an3-"},
    "congener2": {"lemma": "congener", "uri": "41819", "pos": "n", "morpho": "n-s---mn2r"},
    "congero1": {"lemma": "congero", "uri": "c3360", "pos": "v", "morpho": "v1spia--3-"},
    "congero2": {"lemma": "congero", "uri": "105933", "pos": "n", "morpho": "n-s---mn3-"},
    "congestus1": {"lemma": "congestus", "uri": "97988", "pos": "a", "morpho": "aps---mn1-"},
    "congestus2": {"lemma": "congestus", "uri": "c9898", "pos": "n", "morpho": "n-s---mn4-"},
    "congressus1": {"lemma": "congressus", "uri": "105945", "pos": "a", "morpho": "aps---mn1-"},
    "congressus2": {"lemma": "congressus", "uri": "c9900", "pos": "n", "morpho": "n-s---mn4-"},
    "conjectus1": {"lemma": "coniectus", "uri": "105953", "pos": "a", "morpho": "aps---mn1-"},
    "conjectus2": {"lemma": "coniectus", "uri": "c9901", "pos": "n", "morpho": "n-s---mn4-"},
    "conjunctus1": {"lemma": "coniunctus", "uri": "37590", "pos": "a", "morpho": "aps---mn1-"},
    "conjunctus2": {"lemma": "coniunctus", "uri": "c9902", "pos": "n", "morpho": "n-s---mn4-"},
    "conquestus1": {"lemma": "conquestus", "uri": "105989", "pos": "a", "morpho": "aps---mn1-"},
    "conquestus2": {"lemma": "conquestus", "uri": "c9903", "pos": "n", "morpho": "n-s---mn4-"},
    "conscensus1": {"lemma": "conscensus", "uri": "105999", "pos": "a", "morpho": "aps---mn1-"},
    "conscensus2": {"lemma": "conscensus", "uri": "c9904", "pos": "n", "morpho": "n-s---mn4-"},
    "consedo1": {"lemma": "consedo", "uri": "c3500", "pos": "v", "morpho": "v1spia--1-"},
    "consedo2": {"lemma": "consedo", "uri": "c3501", "pos": "n", "morpho": "n-s---mn3-"},
    "consensus1": {"lemma": "consensus", "uri": "106020", "pos": "a", "morpho": "aps---mn1-"},
    "consensus2": {"lemma": "consensus", "uri": "c9905", "pos": "n", "morpho": "n-s---mn4-"},
    "Consentia2": {"lemma": "Consentia", "uri": "59552", "pos": "n", "morpho": "n-s---fn1-"},
    "consero1": {"lemma": "consero", "uri": "c3517", "pos": "v", "morpho": "v1spia--3-"},
    "consero2": {"lemma": "consero", "uri": "c3517", "pos": "v", "morpho": "v1spia--3-"},
    "conspectus1": {"lemma": "conspectus", "uri": "21596", "pos": "a", "morpho": "aps---mn1-"},
    "conspectus2": {"lemma": "conspectus", "uri": "c9906", "pos": "n", "morpho": "n-s---mn4-"},
    "conspicio1": {"lemma": "conspicio", "uri": "c3588", "pos": "v", "morpho": "v1spia--3i"},
    "conspicio2": {"lemma": "conspicio", "uri": "c3589", "pos": "n", "morpho": "n-s---fn3-"},
    "conspiratus1": {"lemma": "conspiratus", "uri": "106083", "pos": "a", "morpho": "aps---mn1-"},
    "conspiratus2": {"lemma": "conspiratus", "uri": "106083", "pos": "a", "morpho": "aps---mn1-"},
    "conspiratus3": {"lemma": "conspiratus", "uri": "c9907", "pos": "n", "morpho": "n-s---mn4-"},
    "conspiro1": {"lemma": "conspiro", "uri": "c4835", "pos": "v", "morpho": "v1spia--1-"},
    "conspiro2": {"lemma": "conspiro", "uri": "c4835", "pos": "v", "morpho": "v1spia--1-"},
    "constans1": {"lemma": "constans", "uri": "21607", "pos": "a", "morpho": "aps---an3i"},
    "constantia1": {"lemma": "constantia", "uri": "c9964", "pos": "n", "morpho": "n-s---fn1-"},
    "consterno1": {"lemma": "consterno", "uri": "c3610", "pos": "v", "morpho": "v1spia--3-"},
    "consterno2": {"lemma": "consterno", "uri": "c3610", "pos": "v", "morpho": "v1spia--3-"},
    "constitutus1": {"lemma": "constitutus", "uri": "45373", "pos": "a", "morpho": "aps---mn1-"},
    "constitutus2": {"lemma": "constitutus", "uri": "c9908", "pos": "n", "morpho": "n-s---mn4-"},
    "consulto1": {"lemma": "consulto", "uri": "58339", "pos": "r", "morpho": "rp--------"},
    "consulto2": {"lemma": "consulto", "uri": "c3656", "pos": "v", "morpho": "v1spia--1-"},
    "consultor1": {"lemma": "consultor", "uri": "c3657", "pos": "n", "morpho": "n-s---mn3-"},
    "consultor2": {"lemma": "consultor", "uri": "c3657", "pos": "n", "morpho": "n-s---mn3-"},
    "consultus1": {"lemma": "consultus", "uri": "21635", "pos": "a", "morpho": "aps---mn1-"},
    "contactus1": {"lemma": "contactus", "uri": "106140", "pos": "a", "morpho": "aps---mn1-"},
    "contactus2": {"lemma": "contactus", "uri": "c9909", "pos": "n", "morpho": "n-s---mn4-"},
    "contatus1": {"lemma": "contatus", "uri": "c3685", "pos": "n", "morpho": "n-s---mn2-"},
    "contatus2": {"lemma": "contatus", "uri": "c3685", "pos": "n", "morpho": "n-s---mn2-"},
    "contemplatus1": {"lemma": "contemplatus", "uri": "106157", "pos": "a", "morpho": "aps---mn1-"},
    "contemplatus2": {"lemma": "contemplatus", "uri": "c3681", "pos": "n", "morpho": "n-s---mn4-"},
    "contemptus1": {"lemma": "contemptus", "uri": "21659", "pos": "a", "morpho": "aps---mn1-"},
    "contemptus2": {"lemma": "contemptus", "uri": "c9910", "pos": "n", "morpho": "n-s---mn4-"},
    "contente1": {"lemma": "contente", "uri": "21661", "pos": "r", "morpho": "rp--------"},
    "contente2": {"lemma": "contente", "uri": "21661", "pos": "r", "morpho": "rp--------"},
    "contentus1": {"lemma": "contentus", "uri": "21663", "pos": "a", "morpho": "aps---mn1-"},
    "contentus2": {"lemma": "contentus", "uri": "21663", "pos": "a", "morpho": "aps---mn1-"},
    "contextus1": {"lemma": "contextus", "uri": "21667", "pos": "a", "morpho": "aps---mn1-"},
    "contextus2": {"lemma": "contextus", "uri": "c9824", "pos": "n", "morpho": "n-s---mn4-"},
    "continentia1": {"lemma": "continentia", "uri": "c9967", "pos": "n", "morpho": "n-p---nn3i"},
    "continentia2": {"lemma": "continentia", "uri": "c9967", "pos": "n", "morpho": "n-p---nn3i"},
    "contingo1": {"lemma": "contingo", "uri": "c3751", "pos": "v", "morpho": "v1spia--3-"},
    "contingo2": {"lemma": "contingo", "uri": "c3751", "pos": "v", "morpho": "v1spia--3-"},
    "continuo1": {"lemma": "continuo", "uri": "21677", "pos": "r", "morpho": "rp--------"},
    "continuo2": {"lemma": "continuo", "uri": "c3757", "pos": "v", "morpho": "v1spia--1-"},
    "contractus1": {"lemma": "contractus", "uri": "21682", "pos": "a", "morpho": "aps---mn1-"},
    "contractus2": {"lemma": "contractus", "uri": "c9825", "pos": "n", "morpho": "n-s---mn4-"},
    "contuitus1": {"lemma": "contuitus", "uri": "106245", "pos": "a", "morpho": "aps---mn1-"},
    "contuitus2": {"lemma": "contuitus", "uri": "c9826", "pos": "n", "morpho": "n-s---mn4-"},
    "contutor1": {"lemma": "contutor", "uri": "c3852", "pos": "n", "morpho": "n-s---mn3-"},
    "contutor2": {"lemma": "contutor", "uri": "c3853", "pos": "v", "morpho": "v1spid--1-"},
    "convector1": {"lemma": "conuector", "uri": "c4841", "pos": "n", "morpho": "n-s---mn3-"},
    "convector2": {"lemma": "conuector", "uri": "c4841", "pos": "n", "morpho": "n-s---mn3-"},
    "conventus1": {"lemma": "conuentus", "uri": "106272", "pos": "a", "morpho": "aps---mn1-"},
    "conventus2": {"lemma": "conuentus", "uri": "c9969", "pos": "n", "morpho": "n-s---mn4-"},
    "conversus1": {"lemma": "conuersus", "uri": "28946", "pos": "a", "morpho": "aps---mn1-"},
    "conversus2": {"lemma": "conuersus", "uri": "28946", "pos": "a", "morpho": "aps---mn1-"},
    "conversus3": {"lemma": "conuersus", "uri": "c9827", "pos": "n", "morpho": "n-s---mn4-"},
    "convexus1": {"lemma": "conuexus", "uri": "c3900", "pos": "a", "morpho": "aps---mn1-"},
    "convexus2": {"lemma": "conuexus", "uri": "106283", "pos": "n", "morpho": "n-s---mn4-"},
    "convictus1": {"lemma": "conuictus", "uri": "106288", "pos": "a", "morpho": "aps---mn1-"},
    "convictus2": {"lemma": "conuictus", "uri": "c3925", "pos": "n", "morpho": "n-s---mn4-"},
    "convivo1": {"lemma": "conuiuo", "uri": "c3924", "pos": "v", "morpho": "v1spia--3-"},
    "convivo2": {"lemma": "conuiuo", "uri": "c3924", "pos": "v", "morpho": "v1spia--3-"},
    "coortus1": {"lemma": "coortus", "uri": "106324", "pos": "a", "morpho": "aps---mn1-"},
    "coortus2": {"lemma": "coortus", "uri": "c9828", "pos": "n", "morpho": "n-s---mn4-"},
    "copia1": {"lemma": "copia", "uri": "c3960", "pos": "n", "morpho": "n-s---fn1-"},
    "copis2": {"lemma": "copis", "uri": "c3966", "pos": "n", "morpho": "n-s---fn3i"},
    "copulatus1": {"lemma": "copulatus", "uri": "21775", "pos": "a", "morpho": "aps---mn1-"},
    "copulatus2": {"lemma": "copulatus", "uri": "c9829", "pos": "n", "morpho": "n-s---mn4-"},
    "cora1": {"lemma": "cora", "uri": "c3994", "pos": "n", "morpho": "n-s---fn1-"},
    "Cora2": {"lemma": "Cora", "uri": "59563", "pos": "n", "morpho": "n-s---fn1-"},
    "Cora3": {"lemma": "Cora", "uri": "59563", "pos": "n", "morpho": "n-s---fn1-"},
    "coracinus1": {"lemma": "coracinus", "uri": "c3998", "pos": "a", "morpho": "aps---mn1-"},
    "coracinus2": {"lemma": "coracinus", "uri": "c4052", "pos": "n", "morpho": "n-s---mn2-"},
    "corax1": {"lemma": "corax", "uri": "c4006", "pos": "n", "morpho": "n-s---mn3-"},
    "Corax2": {"lemma": "Corax", "uri": "59565", "pos": "n", "morpho": "n-s---mn3-"},
    "Corax3": {"lemma": "Corax", "uri": "59565", "pos": "n", "morpho": "n-s---mn3-"},
    "cordus1": {"lemma": "cordus", "uri": "c4025", "pos": "a", "morpho": "aps---mn1-"},
    "corneus1": {"lemma": "corneus", "uri": "c4862", "pos": "a", "morpho": "aps---mn1-"},
    "corneus2": {"lemma": "corneus", "uri": "c4862", "pos": "a", "morpho": "aps---mn1-"},
    "cornicen1": {"lemma": "cornicen", "uri": "c4042", "pos": "n", "morpho": "n-s---mn3-"},
    "Cornicen2": {"lemma": "Cornicen", "uri": "59576", "pos": "n", "morpho": "n-s---mn3-"},
    "corniculum1": {"lemma": "corniculum", "uri": "c1276", "pos": "n", "morpho": "n-s---nn2-"},
    "Corniculum2": {"lemma": "Corniculum", "uri": "59577", "pos": "n", "morpho": "n-s---nn2-"},
    "cornum1": {"lemma": "cornum", "uri": "c4062", "pos": "n", "morpho": "n-s---nn2-"},
    "cornum2": {"lemma": "cornum", "uri": "c4062", "pos": "n", "morpho": "n-s---nn2-"},
    "cornus1": {"lemma": "cornus", "uri": "c4062", "pos": "n", "morpho": "n-s---fn2-"},
    "cornus2": {"lemma": "cornus", "uri": "c4062", "pos": "n", "morpho": "n-s---fn2-"},
    "Cornus3": {"lemma": "Cornus", "uri": "59578", "pos": "n", "morpho": "n-s---mn2-"},
    "cornutus1": {"lemma": "cornutus", "uri": "c4063", "pos": "a", "morpho": "aps---mn1-"},
    "Cornutus2": {"lemma": "Cornutus", "uri": "59579", "pos": "n", "morpho": "n-s---mn2-"},
    "coronis1": {"lemma": "coronis", "uri": "c4077", "pos": "n", "morpho": "n-s---fn3-"},
    "Coronis2": {"lemma": "Coronis", "uri": "59584", "pos": "n", "morpho": "n-s---fn3-"},
    "corycus1": {"lemma": "corycus", "uri": "c4168", "pos": "n", "morpho": "n-s---mn2-"},
    "Corycus2": {"lemma": "Corycus", "uri": "59590", "pos": "n", "morpho": "n-s---mn2-"},
    "cos1": {"lemma": "cos", "uri": "c4181", "pos": "n", "morpho": "n-s---fn3i"},
    "Cos2": {"lemma": "Cos", "uri": "59596", "pos": "n", "morpho": "n-s---mn2-"},
    "cossus1": {"lemma": "cossus", "uri": "c4192", "pos": "n", "morpho": "n-s---mn2-"},
    "Cossus2": {"lemma": "Cossus", "uri": "59599", "pos": "n", "morpho": "n-s---mn2-"},
    "cotyla1": {"lemma": "cotyla", "uri": "53593", "pos": "n", "morpho": "n-s---fn1-"},
    "Cotyla2": {"lemma": "Cotyla", "uri": "59604", "pos": "n", "morpho": "n-s---fn1-"},
    "crassus1": {"lemma": "crassus", "uri": "c4256", "pos": "a", "morpho": "aps---mn1-"},
    "Crassus2": {"lemma": "Crassus", "uri": "59611", "pos": "n", "morpho": "n-s---mn2-"},
    "crastinus1": {"lemma": "crastinus", "uri": "c4258", "pos": "a", "morpho": "aps---mn1-"},
    "Crates1": {"lemma": "Crates", "uri": "59614", "pos": "n", "morpho": "n-p---mn3-"},
    "creo1": {"lemma": "creo", "uri": "c4307", "pos": "v", "morpho": "v1spia--1-"},
    "Creo2": {"lemma": "Creo", "uri": "59621", "pos": "n", "morpho": "n-s---mn3-"},
    "Creta1": {"lemma": "Creta", "uri": "21890", "pos": "n", "morpho": "n-s---fn1-"},
    "creta2": {"lemma": "creta", "uri": "c4332", "pos": "n", "morpho": "n-s---fn1-"},
    "cretus1": {"lemma": "cretus", "uri": "39702", "pos": "a", "morpho": "aps---mn1-"},
    "cretus2": {"lemma": "cretus", "uri": "39702", "pos": "a", "morpho": "aps---mn1-"},
    "crispus1": {"lemma": "crispus", "uri": "c4375", "pos": "a", "morpho": "aps---mn1-"},
    "crista1": {"lemma": "crista", "uri": "c4376", "pos": "n", "morpho": "n-s---fn1-"},
    "Crista2": {"lemma": "Crista", "uri": "59624", "pos": "n", "morpho": "n-s---fn1-"},
    "Ctesiphon1": {"lemma": "Ctesiphon", "uri": "59639", "pos": "n", "morpho": "n-s---nn3-"},
    "Ctesiphon2": {"lemma": "Ctesiphon", "uri": "59639", "pos": "n", "morpho": "n-s---nn3-"},
    "cudo1": {"lemma": "cudo", "uri": "c4524", "pos": "v", "morpho": "v1spia--3-"},
    "cudo2": {"lemma": "cudo", "uri": "c4525", "pos": "n", "morpho": "n-s---mn3-"},
    "cujus1": {"lemma": "cuius", "uri": "35423", "pos": "a", "morpho": "aps----n3-"},
    "cujus2": {"lemma": "cuius", "uri": "35423", "pos": "a", "morpho": "aps----n3-"},
    "culex1": {"lemma": "culex", "uri": "c4541", "pos": "n", "morpho": "n-s---mn3-"},
    "culex2": {"lemma": "culex", "uri": "c4541", "pos": "n", "morpho": "n-s---mn3-"},
    "cultus1": {"lemma": "cultus", "uri": "21960", "pos": "a", "morpho": "aps---mn1-"},
    "cultus2": {"lemma": "cultus", "uri": "c9831", "pos": "n", "morpho": "n-s---mn4-"},
    "cum1": {"lemma": "cum", "uri": "c4579", "pos": "p", "morpho": "p---------"},
    "cunctator1": {"lemma": "cunctator", "uri": "c4616", "pos": "n", "morpho": "n-s---mn3-"},
    "cuneus1": {"lemma": "cuneus", "uri": "c4628", "pos": "n", "morpho": "n-s---mn2-"},
    "cupa1": {"lemma": "cupa", "uri": "c4650", "pos": "n", "morpho": "n-s---fn1-"},
    "cupa2": {"lemma": "cupa", "uri": "c4650", "pos": "n", "morpho": "n-s---fn1-"},
    "cupla1": {"lemma": "cupla", "uri": "47263", "pos": "n", "morpho": "n-s---fn1-"},
    "cupla2": {"lemma": "cupla", "uri": "47263", "pos": "n", "morpho": "n-s---fn1-"},
    "cuppedo1": {"lemma": "cuppedo", "uri": "c4661", "pos": "n", "morpho": "n-s---fn3-"},
    "cuppedo2": {"lemma": "cuppedo", "uri": "c4661", "pos": "n", "morpho": "n-s---fn3-"},
    "cupula1": {"lemma": "cupula", "uri": "c4677", "pos": "n", "morpho": "n-s---fn1-"},
    "cupula2": {"lemma": "cupula", "uri": "c4677", "pos": "n", "morpho": "n-s---fn1-"},
    "curio1": {"lemma": "curio", "uri": "c4687", "pos": "n", "morpho": "n-s---mn3-"},
    "curio3": {"lemma": "curio", "uri": "c4687", "pos": "n", "morpho": "n-s---mn3-"},
    "curius1": {"lemma": "curius", "uri": "49459", "pos": "a", "morpho": "aps---mn1-"},
    "Curius2": {"lemma": "Curius", "uri": "59651", "pos": "a", "morpho": "aps---mn1-"},
    "cursor1": {"lemma": "cursor", "uri": "c4722", "pos": "n", "morpho": "n-s---mn3-"},
    "cycnus1": {"lemma": "cycnus", "uri": "c4784", "pos": "n", "morpho": "n-s---mn2-"},
    "Cyme1": {"lemma": "Cyme", "uri": "59666", "pos": "n", "morpho": "n-s---fn1-"},
    "Cyme2": {"lemma": "Cyme", "uri": "59666", "pos": "n", "morpho": "n-s---fn1-"},
    "Cynosura1": {"lemma": "Cynosura", "uri": "59677", "pos": "n", "morpho": "n-s---fn1-"},
    "Cyprus1": {"lemma": "Cyprus", "uri": "59683", "pos": "n", "morpho": "n-s---mn2-"},
    "cyprus2": {"lemma": "cyprus", "uri": "c4853", "pos": "n", "morpho": "n-s---fn2-"},
    "cypselus1": {"lemma": "cypselus", "uri": "c4854", "pos": "n", "morpho": "n-s---mn2-"},
    "Cypselus2": {"lemma": "Cypselus", "uri": "59685", "pos": "n", "morpho": "n-s---mn2-"},
    "Cyrene1": {"lemma": "Cyrene", "uri": "59687", "pos": "n", "morpho": "n-s---fn1-"},
    "Cyrene2": {"lemma": "Cyrene", "uri": "59687", "pos": "n", "morpho": "n-s---fn1-"},
    "Cytis1": {"lemma": "Cytis", "uri": "59700", "pos": "n", "morpho": "n-s---fn3-"},
    "cytis2": {"lemma": "cytis", "uri": "106773", "pos": "n", "morpho": "n-s---fn3i"},
    "daemon1": {"lemma": "daemon", "uri": "d0011", "pos": "n", "morpho": "n-s---mn3-"},
    "Daemon2": {"lemma": "Daemon", "uri": "59707", "pos": "n", "morpho": "n-s---nn3-"},
    "Dama2": {"lemma": "Dama", "uri": "33826", "pos": "n", "morpho": "n-s---fn1-"},
    "Dardanus1": {"lemma": "Dardanus", "uri": "59722", "pos": "n", "morpho": "n-s---mn2-"},
    "Dardanus2": {"lemma": "Dardanus", "uri": "59722", "pos": "n", "morpho": "n-s---mn2-"},
    "de1": {"lemma": "de", "uri": "d0071", "pos": "p", "morpho": "p---------"},
    "de2": {"lemma": "de", "uri": "d0071", "pos": "p", "morpho": "p---------"},
    "deceptus1": {"lemma": "deceptus", "uri": "106879", "pos": "a", "morpho": "aps---mn1-"},
    "deceptus2": {"lemma": "deceptus", "uri": "d9519", "pos": "n", "morpho": "n-s---mn4-"},
    "Decianus1": {"lemma": "Decianus", "uri": "59728", "pos": "n", "morpho": "n-s---mn2-"},
    "Decianus2": {"lemma": "Decianus", "uri": "59728", "pos": "n", "morpho": "n-s---mn2-"},
    "decimus1": {"lemma": "decimus", "uri": "d0935", "pos": "a", "morpho": "aps---mn1-"},
    "Decimus2": {"lemma": "Decimus", "uri": "59730", "pos": "n", "morpho": "n-s---mn2-"},
    "decoctus1": {"lemma": "decoctus", "uri": "56347", "pos": "a", "morpho": "aps---mn1-"},
    "decoctus2": {"lemma": "decoctus", "uri": "d0240", "pos": "n", "morpho": "n-s---mn4-"},
    "decurio1": {"lemma": "decurio", "uri": "d0274", "pos": "v", "morpho": "v1spia--1-"},
    "decurio2": {"lemma": "decurio", "uri": "d0275", "pos": "n", "morpho": "n-s---mn3-"},
    "decursus1": {"lemma": "decursus", "uri": "106947", "pos": "a", "morpho": "aps---mn1-"},
    "decursus2": {"lemma": "decursus", "uri": "d0290", "pos": "n", "morpho": "n-s---mn4-"},
    "decutio1": {"lemma": "decutio", "uri": "d0295", "pos": "v", "morpho": "v1spia--3i"},
    "decutio2": {"lemma": "decutio", "uri": "d0295", "pos": "v", "morpho": "v1spia--3i"},
    "deductus2": {"lemma": "deductus", "uri": "32801", "pos": "a", "morpho": "aps---mn1-"},
    "deductus3": {"lemma": "deductus", "uri": "d9521", "pos": "n", "morpho": "n-s---mn4-"},
    "defectus1": {"lemma": "defectus", "uri": "98101", "pos": "a", "morpho": "aps---mn1-"},
    "defectus2": {"lemma": "defectus", "uri": "d9522", "pos": "n", "morpho": "n-s---mn4-"},
    "deflexus1": {"lemma": "deflexus", "uri": "107005", "pos": "a", "morpho": "aps---mn1-"},
    "deflexus2": {"lemma": "deflexus", "uri": "d9523", "pos": "n", "morpho": "n-s---mn4-"},
    "deformatio1": {"lemma": "deformatio", "uri": "d1467", "pos": "n", "morpho": "n-s---fn3-"},
    "deformatio2": {"lemma": "deformatio", "uri": "d1467", "pos": "n", "morpho": "n-s---fn3-"},
    "deformo1": {"lemma": "deformo", "uri": "d0403", "pos": "v", "morpho": "v1spia--1-"},
    "deformo2": {"lemma": "deformo", "uri": "d0403", "pos": "v", "morpho": "v1spia--1-"},
    "defossus1": {"lemma": "defossus", "uri": "107016", "pos": "a", "morpho": "aps---mn1-"},
    "defossus2": {"lemma": "defossus", "uri": "d9525", "pos": "n", "morpho": "n-s---mn4-"},
    "defunctus1": {"lemma": "defunctus", "uri": None, "pos": "a", "morpho": "aps---mn1-"},
    "defunctus2": {"lemma": "defunctus", "uri": "d9526", "pos": "n", "morpho": "n-s---mn4-"},
    "dejectus1": {"lemma": "deiectus", "uri": "48126", "pos": "a", "morpho": "aps---mn1-"},
    "dejectus2": {"lemma": "deiectus", "uri": "d9528", "pos": "n", "morpho": "n-s---mn4-"},
    "delapsus1": {"lemma": "delapsus", "uri": "107085", "pos": "a", "morpho": "aps---mn1-"},
    "delapsus2": {"lemma": "delapsus", "uri": "d9529", "pos": "n", "morpho": "n-s---mn4-"},
    "delector1": {"lemma": "delector", "uri": "132405", "pos": "v", "morpho": "v1spid--1-"},
    "delector2": {"lemma": "delector", "uri": "d0519", "pos": "n", "morpho": "n-s---mn3-"},
    "delectus1": {"lemma": "delectus", "uri": "45090", "pos": "a", "morpho": "aps---mn1-"},
    "delectus2": {"lemma": "delectus", "uri": "d9530", "pos": "n", "morpho": "n-s---mn4-"},
    "delicia1": {"lemma": "delicia", "uri": "d0550", "pos": "n", "morpho": "n-s---fn1-"},
    "delicia2": {"lemma": "delicia", "uri": "d0550", "pos": "n", "morpho": "n-s---fn1-"},
    "deligo1": {"lemma": "deligo", "uri": "d0563", "pos": "v", "morpho": "v1spia--3-"},
    "deligo2": {"lemma": "deligo", "uri": "d0564", "pos": "v", "morpho": "v1spia--1-"},
    "deliquium1": {"lemma": "deliquium", "uri": "d1469", "pos": "n", "morpho": "n-s---nn2-"},
    "deliquium2": {"lemma": "deliquium", "uri": "d1469", "pos": "n", "morpho": "n-s---nn2-"},
    "demersus1": {"lemma": "demersus", "uri": "33872", "pos": "a", "morpho": "aps---mn1-"},
    "demersus2": {"lemma": "demersus", "uri": "d9532", "pos": "n", "morpho": "n-s---mn4-"},
    "demeto1": {"lemma": "demeto", "uri": "d0628", "pos": "v", "morpho": "v1spia--3-"},
    "demeto2": {"lemma": "demeto", "uri": "107156", "pos": "v", "morpho": "v1spia--1-"},
    "dentio1": {"lemma": "dentio", "uri": "d0727", "pos": "v", "morpho": "v1spia--4-"},
    "dentio2": {"lemma": "dentio", "uri": "d0728", "pos": "n", "morpho": "n-s---fn3-"},
    "derelictus1": {"lemma": "derelictus", "uri": "98135", "pos": "a", "morpho": "aps---mn1-"},
    "derelictus2": {"lemma": "derelictus", "uri": "d9535", "pos": "n", "morpho": "n-s---mn4-"},
    "derisus1": {"lemma": "derisus", "uri": "107315", "pos": "a", "morpho": "aps---mn1-"},
    "derisus2": {"lemma": "derisus", "uri": "d9536", "pos": "n", "morpho": "n-s---mn4-"},
    "descensus1": {"lemma": "descensus", "uri": "107333", "pos": "a", "morpho": "aps---mn1-"},
    "descensus2": {"lemma": "descensus", "uri": "d9537", "pos": "n", "morpho": "n-s---mn4-"},
    "desero1": {"lemma": "desero", "uri": None, "pos": "v", "morpho": "v1spia--3-"},
    "desero2": {"lemma": "desero", "uri": None, "pos": "v", "morpho": "v1spia--3-"},
    "desitus1": {"lemma": "desitus", "uri": "40687", "pos": "a", "morpho": "aps---mn1-"},
    "desitus2": {"lemma": "desitus", "uri": "40687", "pos": "a", "morpho": "aps---mn1-"},
    "desitus3": {"lemma": "desitus", "uri": "d9538", "pos": "n", "morpho": "n-s---mn4-"},
    "despectus1": {"lemma": "despectus", "uri": "22389", "pos": "a", "morpho": "aps---mn1-"},
    "despectus2": {"lemma": "despectus", "uri": "d9539", "pos": "n", "morpho": "n-s---mn4-"},
    "despicatus1": {"lemma": "despicatus", "uri": "107368", "pos": "a", "morpho": "aps---mn1-"},
    "despicatus2": {"lemma": "despicatus", "uri": "d8010", "pos": "n", "morpho": "n-s---mn4-"},
    "detentus1": {"lemma": "detentus", "uri": "107407", "pos": "a", "morpho": "aps---mn1-"},
    "detentus2": {"lemma": "detentus", "uri": "d1090", "pos": "n", "morpho": "n-s---mn4-"},
    "detestatio1": {"lemma": "detestatio", "uri": "d1470", "pos": "n", "morpho": "n-s---fn3-"},
    "detestatio2": {"lemma": "detestatio", "uri": "d1470", "pos": "n", "morpho": "n-s---fn3-"},
    "detractus1": {"lemma": "detractus", "uri": "107422", "pos": "a", "morpho": "aps---mn1-"},
    "detractus2": {"lemma": "detractus", "uri": "d9541", "pos": "n", "morpho": "n-s---mn4-"},
    "detritus1": {"lemma": "detritus", "uri": "22456", "pos": "a", "morpho": "aps---mn1-"},
    "detritus2": {"lemma": "detritus", "uri": "d9540", "pos": "n", "morpho": "n-s---mn4-"},
    "deversor1": {"lemma": "deuersor", "uri": "d1147", "pos": "v", "morpho": "v1spid--1-"},
    "deversor2": {"lemma": "deuersor", "uri": "d1148", "pos": "n", "morpho": "n-s---mn3-"},
    "dico1": {"lemma": "dico", "uri": "d1349", "pos": "v", "morpho": "v1spia--1-"},
    "dico2": {"lemma": "dico", "uri": "d1350", "pos": "v", "morpho": "v1spia--3-"},
    "dictus1": {"lemma": "dictus", "uri": "107591", "pos": "a", "morpho": "aps---mn1-"},
    "dictus2": {"lemma": "dictus", "uri": "d9542", "pos": "n", "morpho": "n-s---mn4-"},
    "dido1": {"lemma": "dido", "uri": "d1372", "pos": "v", "morpho": "v1spia--3-"},
    "Dido2": {"lemma": "Dido", "uri": "22505", "pos": "n", "morpho": "n-s---fn3-"},
    "digestus1": {"lemma": "digestus", "uri": "52948", "pos": "a", "morpho": "aps---mn1-"},
    "digestus2": {"lemma": "digestus", "uri": "d9544", "pos": "n", "morpho": "n-s---mn4-"},
    "digitus1": {"lemma": "digitus", "uri": "d1434", "pos": "n", "morpho": "n-s---mn2-"},
    "Digitus2": {"lemma": "Digitus", "uri": "59776", "pos": "n", "morpho": "n-s---mn2-"},
    "digressus1": {"lemma": "digressus", "uri": "107650", "pos": "a", "morpho": "aps---mn1-"},
    "digressus2": {"lemma": "digressus", "uri": "d9545", "pos": "n", "morpho": "n-s---mn4-"},
    "dilectus1": {"lemma": "dilectus", "uri": "98172", "pos": "a", "morpho": "aps---mn1-"},
    "dilectus2": {"lemma": "dilectus", "uri": "d9530", "pos": "n", "morpho": "n-s---mn4-"},
    "diluvio1": {"lemma": "diluuio", "uri": "d1596", "pos": "v", "morpho": "v1spia--1-"},
    "diluvio2": {"lemma": "diluuio", "uri": "d1597", "pos": "n", "morpho": "n-s---fn3-"},
    "Dionysia1": {"lemma": "Dionysia", "uri": "59788", "pos": "n", "morpho": "n-s---fn1-"},
    "Dionysia2": {"lemma": "Dionysia", "uri": "59788", "pos": "n", "morpho": "n-s---fn1-"},
    "dipsas1": {"lemma": "dipsas", "uri": "d1655", "pos": "n", "morpho": "n-s---fn3-"},
    "Dipsas2": {"lemma": "Dipsas", "uri": "59797", "pos": "n", "morpho": "n-s---mn3-"},
    "diremptus1": {"lemma": "diremptus", "uri": "107739", "pos": "a", "morpho": "aps---mn1-"},
    "diremptus2": {"lemma": "diremptus", "uri": "d9547", "pos": "n", "morpho": "n-s---mn4-"},
    "direptus1": {"lemma": "direptus", "uri": "107740", "pos": "a", "morpho": "aps---mn1-"},
    "direptus2": {"lemma": "direptus", "uri": "d9548", "pos": "n", "morpho": "n-s---mn4-"},
    "dis1": {"lemma": "dis", "uri": "d2023", "pos": "a", "morpho": "aps---an3-"},
    "dis3": {"lemma": "dis", "uri": None, "pos": "r", "morpho": "rp--------"},
    "discessus1": {"lemma": "discessus", "uri": "107767", "pos": "a", "morpho": "aps---mn1-"},
    "discessus2": {"lemma": "discessus", "uri": "d9549", "pos": "n", "morpho": "n-s---mn4-"}, "discruciatus1": {
        "lemma": "discruciatus",
        "uri": "d9550",
        "pos": "n",
        "morpho": "n-s---mn4-"
    },
    "discruciatus2": {
        "lemma": "discruciatus", "uri": "d9550", "pos": "n", "morpho": "n-s---mn4-"
    }, "discursus1": {"lemma": "discursus", "uri": "107828", "pos": "a", "morpho": "aps---mn1-"}, "discursus2": {
        "lemma": "discursus", "uri": "d9552", "pos": "n", "morpho": "n-s---mn4-"
    }, "discus1": {"lemma": "discus", "uri": "d1778", "pos": "n", "morpho": "n-s---mn2-"}, "discussus1": {
        "lemma": "discussus", "uri": "107834", "pos": "a", "morpho": "aps---mn1-"
    }, "discussus2": {"lemma": "discussus", "uri": "107835", "pos": "n", "morpho": "n-s---mn4-"}, "disjectus1": {
        "lemma": "disiectus", "uri": "107846", "pos": "a", "morpho": "aps---mn1-"
    }, "disjectus2": {"lemma": "disiectus", "uri": "d1803", "pos": "n", "morpho": "n-s---mn4-"}, "dispectus1": {
        "lemma": "dispectus", "uri": "107868", "pos": "a", "morpho": "aps---mn1-"
    }, "dispectus2": {"lemma": "dispectus", "uri": "d9553", "pos": "n", "morpho": "n-s---mn4-"}, "dispendo1": {
        "lemma": "dispendo", "uri": "d1463", "pos": "v", "morpho": "v1spia--3-"
    }, "dispendo2": {"lemma": "dispendo", "uri": "d1463", "pos": "v", "morpho": "v1spia--3-"}, "dispositus1": {
        "lemma": "dispositus", "uri": "98205", "pos": "a", "morpho": "aps---mn1-"
    }, "dispositus2": {"lemma": "dispositus", "uri": None, "pos": "n", "morpho": "n-s---mn4-"}, "dissensus1": {
        "lemma": "dissensus", "uri": "29603", "pos": "a", "morpho": "aps---mn1-"
    }, "dissensus2": {"lemma": "dissensus", "uri": "d9556", "pos": "n", "morpho": "n-s---mn4-"}, "dissero1": {
        "lemma": "dissero", "uri": "d1885", "pos": "v", "morpho": "v1spia--3-"
    }, "dissero2": {"lemma": "dissero", "uri": "d1885", "pos": "v", "morpho": "v1spia--3-"}, "dissitus1": {
        "lemma": "dissitus", "uri": "d1916", "pos": "a", "morpho": "aps---mn1-"
    }, "dissitus2": {"lemma": "dissitus", "uri": "d1916", "pos": "a", "morpho": "aps---mn1-"}, "distentus1": {
        "lemma": "distentus", "uri": "22641", "pos": "a", "morpho": "aps---mn1-"
    }, "distentus2": {"lemma": "distentus", "uri": "22641", "pos": "a", "morpho": "aps---mn1-"}, "distentus3": {
        "lemma": "distentus", "uri": None, "pos": "n", "morpho": "n-s---mn4-"
    }, "distinctus1": {"lemma": "distinctus", "uri": "22644", "pos": "a", "morpho": "aps---mn1-"}, "distinctus2": {
        "lemma": "distinctus", "uri": "d9558", "pos": "n", "morpho": "n-s---mn4-"
    }, "distractus1": {"lemma": "distractus", "uri": "57050", "pos": "a", "morpho": "aps---mn1-"}, "distractus2": {
        "lemma": "distractus", "uri": "d9559", "pos": "n", "morpho": "n-s---mn4-"
    }, "dius1": {"lemma": "dius", "uri": "d1461", "pos": "a", "morpho": "aps---mn1-"}, "dius2": {
        "lemma": "dius", "uri": "50061", "pos": "r", "morpho": "rp--------"
    }, "divisus1": {"lemma": "diuisus", "uri": "98223", "pos": "a", "morpho": "aps---mn1-"}, "divisus2": {
        "lemma": "diuisus", "uri": "d2003", "pos": "n", "morpho": "n-s---mn4-"
    }, "do1": {"lemma": "do", "uri": "d2066", "pos": "v", "morpho": "v1spia--1-"}, "do2": {
        "lemma": "do", "uri": "d2066", "pos": "v", "morpho": "v1spia--1-"
    }, "do3": {"lemma": "do", "uri": "d2066", "pos": "v", "morpho": "v1spia--1-"}, "dolabella1": {
        "lemma": "dolabella", "uri": "d2103", "pos": "n", "morpho": "n-s---fn1-"
    }, "dolichos2": {"lemma": "dolichos", "uri": "d2117", "pos": "n", "morpho": "n-s---mn2g"}, "dolo1": {
        "lemma": "dolo", "uri": "d2124", "pos": "v", "morpho": "v1spia--1-"
    }, "domitius1": {"lemma": "domitius", "uri": "108152", "pos": "a", "morpho": "aps---mn1-"}, "Domitius2": {
        "lemma": "Domitius", "uri": "59805", "pos": "n", "morpho": "n-s---mn2-"
    }, "domitus1": {"lemma": "domitus", "uri": "108154", "pos": "a", "morpho": "aps---mn1-"}, "domitus2": {
        "lemma": "domitus", "uri": "d9563", "pos": "n", "morpho": "n-s---mn4-"
    }, "Dossennus2": {"lemma": "Dossennus", "uri": "108190", "pos": "n", "morpho": "n-s---mn2-"}, "doto1": {
        "lemma": "doto", "uri": "d2200", "pos": "v", "morpho": "v1spia--1-"
    }, "draco1": {"lemma": "draco", "uri": "d2206", "pos": "n", "morpho": "n-s---mn3-"}, "Draco2": {
        "lemma": "Draco", "uri": "59812", "pos": "n", "morpho": "n-s---mn3-"
    }, "dromo1": {"lemma": "dromo", "uri": "d2232", "pos": "n", "morpho": "n-s---mn3-"}, "Dryas1": {
        "lemma": "Dryas", "uri": "d2245", "pos": "n", "morpho": "n-s---fn3-"
    }, "Dryas2": {"lemma": "Dryas", "uri": "d2245", "pos": "n", "morpho": "n-s---fn3-"}, "ductus1": {
        "lemma": "ductus", "uri": "108269", "pos": "a", "morpho": "aps---mn1-"
    }, "ductus2": {"lemma": "ductus", "uri": "d9564", "pos": "n", "morpho": "n-s---mn4-"}, "duplo1": {
        "lemma": "duplo", "uri": "d2378", "pos": "v", "morpho": "v1spia--1-"
    }, "duplo2": {"lemma": "duplo", "uri": "22749", "pos": "r", "morpho": "rp--------"}, "durius1": {
        "lemma": "durius", "uri": "d2398", "pos": "a", "morpho": "aps---mn1-"
    }, "echinus1": {"lemma": "echinus", "uri": "e0048", "pos": "n", "morpho": "n-s---mn2-"}, "Echinus2": {
        "lemma": "Echinus", "uri": "59834", "pos": "n", "morpho": "n-s---mn2-"
    }, "echion1": {"lemma": "echion", "uri": "108433", "pos": "n", "morpho": "n-s---nn2g"}, "ecqui1": {
        "lemma": "ecqui", "uri": "98280", "pos": "r", "morpho": "rp--------"
    }, "ecqui2": {"lemma": "ecqui", "uri": "98280", "pos": "r", "morpho": "rp--------"}, "editus1": {
        "lemma": "editus", "uri": "22779", "pos": "a", "morpho": "aps---mn1-"
    }, "editus2": {"lemma": "editus", "uri": "e0128", "pos": "n", "morpho": "n-s---mn4-"}, "edo3": {
        "lemma": "edo", "uri": "e0096", "pos": "n", "morpho": "n-s---mn3-"
    }, "educo1": {"lemma": "educo", "uri": "e0106", "pos": "v", "morpho": "v1spia--3-"}, "educo2": {
        "lemma": "educo", "uri": "e0105", "pos": "v", "morpho": "v1spia--1-"
    }, "effectus1": {"lemma": "effectus", "uri": "98287", "pos": "a", "morpho": "aps---mn1-"}, "effectus2": {
        "lemma": "effectus", "uri": "e9981", "pos": "n", "morpho": "n-s---mn4-"
    }, "effero1": {"lemma": "effero", "uri": "e0127", "pos": "v", "morpho": "v1spia--1-"}, "effero2": {
        "lemma": "effero", "uri": "e0127", "pos": "v", "morpho": "v1spia--1-"
    }, "egestus1": {"lemma": "egestus", "uri": "108588", "pos": "a", "morpho": "aps---mn1-"}, "egestus2": {
        "lemma": "egestus", "uri": "e9965", "pos": "n", "morpho": "n-s---mn4-"
    }, "egressus1": {"lemma": "egressus", "uri": "e9966", "pos": "n", "morpho": "n-s---mn4-"}, "egressus2": {
        "lemma": "egressus", "uri": "e9966", "pos": "n", "morpho": "n-s---mn4-"
    }, "ejectus1": {"lemma": "eiectus", "uri": "108608", "pos": "a", "morpho": "aps---mn1-"}, "ejectus2": {
        "lemma": "eiectus", "uri": "e9967", "pos": "n", "morpho": "n-s---mn4-"
    }, "elate1": {"lemma": "elate", "uri": "48335", "pos": "r", "morpho": "rp--------"}, "elate2": {
        "lemma": "elate", "uri": "e0262", "pos": "n", "morpho": "n-s---fn1g"
    }, "elector1": {"lemma": "elector", "uri": "e0277", "pos": "n", "morpho": "n-s---mn3-"}, "elector2": {
        "lemma": "elector", "uri": "e0277", "pos": "n", "morpho": "n-s---mn3-"
    }, "electrus1": {"lemma": "electrus", "uri": "e0281", "pos": "a", "morpho": "aps---mn1-"}, "Electrus2": {
        "lemma": "Electrus", "uri": "59846", "pos": "n", "morpho": "n-s---mn2-"
    }, "electus1": {"lemma": "electus", "uri": "58144", "pos": "a", "morpho": "aps---mn1-"}, "electus2": {
        "lemma": "electus", "uri": "e9970", "pos": "n", "morpho": "n-s---mn4-"
    }, "elegus1": {"lemma": "elegus", "uri": "108669", "pos": "a", "morpho": "aps---mn1-"}, "elegus2": {
        "lemma": "elegus", "uri": "30651", "pos": "n", "morpho": "n-s---mn2-"
    }, "Elias1": {"lemma": "Elias", "uri": "101252", "pos": "n", "morpho": "n-s---mn1g"}, "Elias2": {
        "lemma": "Elias", "uri": "101252", "pos": "n", "morpho": "n-s---mn1g"
    }, "emersus1": {"lemma": "emersus", "uri": "108809", "pos": "a", "morpho": "aps---mn1-"}, "emersus2": {
        "lemma": "emersus", "uri": "e0451", "pos": "n", "morpho": "n-s---mn4-"
    }, "emissus1": {"lemma": "emissus", "uri": "108826", "pos": "a", "morpho": "aps---mn1-"}, "emissus2": {
        "lemma": "emissus", "uri": "e9971", "pos": "n", "morpho": "n-s---mn4-"
    }, "enixus1": {"lemma": "enixus", "uri": "50725", "pos": "a", "morpho": "aps---mn1-"}, "enixus2": {
        "lemma": "enixus", "uri": "e0580", "pos": "n", "morpho": "n-s---mn4-"
    }, "eo1": {"lemma": "eo", "uri": "e0655", "pos": "v", "morpho": "v1spia--4-"}, "eo2": {
        "lemma": "eo", "uri": "98345", "pos": "r", "morpho": "rp--------"
    }, "ephorus1": {"lemma": "ephorus", "uri": "e0699", "pos": "n", "morpho": "n-s---mn2-"}, "Ephorus2": {
        "lemma": "Ephorus", "uri": "59879", "pos": "n", "morpho": "n-s---mn2-"
    }, "Epiphania1": {"lemma": "Epiphania", "uri": "29277", "pos": "n", "morpho": "n-s---fn1-"}, "Epiphania2": {
        "lemma": "Epiphania", "uri": "29277", "pos": "n", "morpho": "n-s---fn1-"
    }, "epulo1": {"lemma": "epulo", "uri": "e0291", "pos": "n", "morpho": "n-s---mn3-"}, "equitatus1": {
        "lemma": "equitatus", "uri": "e0863", "pos": "n", "morpho": "n-s---mn4-"
    }, "equitatus2": {"lemma": "equitatus", "uri": "e0863", "pos": "n", "morpho": "n-s---mn4-"}, "er1": {
        "lemma": "er", "uri": "e0842", "pos": "n", "morpho": "n-s---mn3-"
    }, "Er2": {"lemma": "Er", "uri": "59896", "pos": "n", "morpho": "n-s---mn3-"}, "erro1": {
        "lemma": "erro", "uri": "e0925", "pos": "v", "morpho": "v1spia--1-"
    }, "erro2": {"lemma": "erro", "uri": "e0926", "pos": "n", "morpho": "n-s---mn3-"}, "eruditus1": {
        "lemma": "eruditus", "uri": "22942", "pos": "a", "morpho": "aps---mn1-"
    }, "eruditus2": {"lemma": "eruditus", "uri": "e0947", "pos": "n", "morpho": "n-s---mn4-"}, "erugo1": {
        "lemma": "erugo", "uri": "e0944", "pos": "v", "morpho": "v1spia--1-"
    }, "erugo2": {"lemma": "erugo", "uri": "e0944", "pos": "v", "morpho": "v1spia--1-"}, "esurio1": {
        "lemma": "esurio", "uri": "e0993", "pos": "v", "morpho": "v1spia--4-"
    }, "esurio2": {"lemma": "esurio", "uri": "e0994", "pos": "n", "morpho": "n-s---mn3-"}, "esus1": {
        "lemma": "esus", "uri": "109353", "pos": "a", "morpho": "aps---mn1-"
    },
    "esus2": {"lemma": "esus", "uri": "e9959", "pos": "n", "morpho": "n-s---mn4-"},
    "etiam1": {"lemma": "etiam", "uri": "e1010", "pos": "r", "morpho": "rp--------"},
    "Euryalus1": {
        "lemma": "Euryalus", "uri": "59957", "pos": "n", "morpho": "n-s---mn2-"
    }, "Euryalus2": {"lemma": "Euryalus", "uri": "59957", "pos": "n", "morpho": "n-s---mn2-"}, "eusebes1": {
        "lemma": "eusebes", "uri": "e1155", "pos": "n", "morpho": "n-s---nn3-"
    }, "Eusebes2": {"lemma": "Eusebes", "uri": "59968", "pos": "n", "morpho": "n-p---mn3-"}, "evallo1": {
        "lemma": "euallo", "uri": "e1027", "pos": "v", "morpho": "v1spia--1-"
    }, "evallo2": {"lemma": "euallo", "uri": "e1028", "pos": "v", "morpho": "v1spia--3-"}, "evectus1": {
        "lemma": "euectus", "uri": "109398", "pos": "a", "morpho": "aps---mn1-"
    }, "evectus2": {"lemma": "euectus", "uri": "e9928", "pos": "n", "morpho": "n-s---mn4-"}, "evito1": {
        "lemma": "euito", "uri": "e1102", "pos": "v", "morpho": "v1spia--1-"
    }, "evito2": {"lemma": "euito", "uri": "e1102", "pos": "v", "morpho": "v1spia--1-"}, "exactus1": {
        "lemma": "exactus", "uri": "22995", "pos": "a", "morpho": "aps---mn1-"
    }, "exactus2": {"lemma": "exactus", "uri": "e9931", "pos": "n", "morpho": "n-s---mn4-"}, "excidium1": {
        "lemma": "excidium", "uri": "e8306", "pos": "n", "morpho": "n-s---nn2-"
    }, "excidium2": {"lemma": "excidium", "uri": "e8306", "pos": "n", "morpho": "n-s---nn2-"}, "excitus1": {
        "lemma": "excitus", "uri": "98395", "pos": "a", "morpho": "aps---mn1-"
    }, "excitus2": {"lemma": "excitus", "uri": "e9933", "pos": "n", "morpho": "n-s---mn4-"}, "excogitatus1": {
        "lemma": "excogitatus", "uri": "109681", "pos": "a", "morpho": "aps---mn1-"
    }, "excogitatus2": {"lemma": "excogitatus", "uri": "109681", "pos": "a", "morpho": "aps---mn1-"}, "excolo1": {
        "lemma": "excolo", "uri": "e1348", "pos": "v", "morpho": "v1spia--3-"
    }, "excolo2": {"lemma": "excolo", "uri": "e1349", "pos": "v", "morpho": "v1spia--1-"}, "excrementum1": {
        "lemma": "excrementum", "uri": "e1367", "pos": "n", "morpho": "n-s---nn2-"
    }, "excrementum2": {"lemma": "excrementum", "uri": "e1367", "pos": "n", "morpho": "n-s---nn2-"}, "excretus1": {
        "lemma": "excretus", "uri": "109703", "pos": "a", "morpho": "aps---mn1-"
    }, "excretus2": {"lemma": "excretus", "uri": "109703", "pos": "a", "morpho": "aps---mn1-"}, "excursus1": {
        "lemma": "excursus", "uri": "109727", "pos": "a", "morpho": "aps---mn1-"
    }, "excursus2": {"lemma": "excursus", "uri": "e9936", "pos": "n", "morpho": "n-s---mn4-"}, "excussus1": {
        "lemma": "excussus", "uri": "57914", "pos": "a", "morpho": "aps---mn1-"
    }, "excussus2": {"lemma": "excussus", "uri": "e1412", "pos": "n", "morpho": "n-s---mn4-"}, "exemptus1": {
        "lemma": "exemptus", "uri": "109766", "pos": "a", "morpho": "aps---mn1-"
    }, "exemptus2": {"lemma": "exemptus", "uri": "e9937", "pos": "n", "morpho": "n-s---mn4-"}, "exercitus1": {
        "lemma": "exercitus", "uri": "98406", "pos": "a", "morpho": "aps---mn1-"
    }, "exercitus2": {"lemma": "exercitus", "uri": "e1414", "pos": "n", "morpho": "n-s---mn4-"}, "exitus1": {
        "lemma": "exitus", "uri": "109841", "pos": "a", "morpho": "aps---mn1-"
    }, "exitus2": {"lemma": "exitus", "uri": "e9938", "pos": "n", "morpho": "n-s---mn4-"}, "exorsus1": {
        "lemma": "exorsus", "uri": "109882", "pos": "a", "morpho": "aps---mn1-"
    }, "exorsus2": {"lemma": "exorsus", "uri": "e9939", "pos": "n", "morpho": "n-s---mn4-"}, "exortus1": {
        "lemma": "exortus", "uri": "109884", "pos": "a", "morpho": "aps---mn1-"
    }, "exortus2": {"lemma": "exortus", "uri": "e9940", "pos": "n", "morpho": "n-s---mn4-"}, "explicatus1": {
        "lemma": "explicatus", "uri": "109952", "pos": "a", "morpho": "aps---mn1-"
    }, "explicatus2": {"lemma": "explicatus", "uri": "e9942", "pos": "n", "morpho": "n-s---mn4-"}, "expressus1": {
        "lemma": "expressus", "uri": "23138", "pos": "a", "morpho": "aps---mn1-"
    }, "expressus2": {"lemma": "expressus", "uri": "e9944", "pos": "n", "morpho": "n-s---mn4-"}, "exstinctus1": {
        "lemma": "exstinctus", "uri": "49596", "pos": "a", "morpho": "aps---mn1-"
    }, "exstinctus2": {"lemma": "exstinctus", "uri": "e9946", "pos": "n", "morpho": "n-s---mn4-"}, "extentus1": {
        "lemma": "extentus", "uri": "42005", "pos": "a", "morpho": "aps---mn1-"
    }, "extentus2": {"lemma": "extentus", "uri": "50941", "pos": "n", "morpho": "n-s---mn4-"}, "extersus1": {
        "lemma": "extersus", "uri": "110156", "pos": "a", "morpho": "aps---mn1-"
    }, "extersus2": {"lemma": "extersus", "uri": "e9948", "pos": "n", "morpho": "n-s---mn4-"}, "extrinsecus1": {
        "lemma": "extrinsecus", "uri": "e1887", "pos": "r", "morpho": "rp--------"
    }, "extrinsecus2": {"lemma": "extrinsecus", "uri": "28546", "pos": "a", "morpho": "aps---mn1-"}, "faber1": {
        "lemma": "faber", "uri": "f0011", "pos": "n", "morpho": "n-s---mn2r"
    }, "faber3": {"lemma": "faber", "uri": "f0011", "pos": "n", "morpho": "n-s---mn2r"}, "factus1": {
        "lemma": "factus", "uri": "29797", "pos": "a", "morpho": "aps---mn1-"
    }, "factus2": {"lemma": "factus", "uri": "f9201", "pos": "n", "morpho": "n-s---mn4-"}, "falcula1": {
        "lemma": "falcula", "uri": "f0119", "pos": "n", "morpho": "n-s---fn1-"
    }, "Falcula2": {"lemma": "Falcula", "uri": "59980", "pos": "n", "morpho": "n-s---fn1-"}, "falso1": {
        "lemma": "falso", "uri": "f0144", "pos": "v", "morpho": "v1spia--1-"
    }, "falso2": {"lemma": "falso", "uri": "98485", "pos": "r", "morpho": "rp--------"}, "famulus1": {
        "lemma": "famulus", "uri": "f0172", "pos": "n", "morpho": "n-s---mn2-"
    }, "famulus2": {"lemma": "famulus", "uri": "f0083", "pos": "a", "morpho": "aps---mn1-"}, "fanum1": {
        "lemma": "fanum", "uri": "f0187", "pos": "n", "morpho": "n-s---nn2-"
    }, "Fanum2": {"lemma": "Fanum", "uri": "59985", "pos": "n", "morpho": "n-s---nn2-"}, "Farfarus2": {
        "lemma": "Farfarus", "uri": "110386", "pos": "n", "morpho": "n-s---mn2-"
    }, "fartus1": {"lemma": "fartus", "uri": "110419", "pos": "a", "morpho": "aps---mn1-"}, "fartus2": {
        "lemma": "fartus", "uri": "f1272", "pos": "n", "morpho": "n-s---mn4-"
    }, "fastus1": {"lemma": "fastus", "uri": "f0248", "pos": "a", "morpho": "aps---mn1-"}, "fastus2": {
        "lemma": "fastus", "uri": "f0248", "pos": "n", "morpho": "n-s---mn4-"
    }, "fastus3": {"lemma": "fastus", "uri": "f0248", "pos": "n", "morpho": "n-s---mn4-"}, "fatuor1": {
        "lemma": "fatuor", "uri": "f0270", "pos": "v", "morpho": "v1spid--1-"
    }, "fatuor2": {"lemma": "fatuor", "uri": "f0270", "pos": "v", "morpho": "v1spid--1-"}, "fatus1": {
        "lemma": "fatus", "uri": "110464", "pos": "a", "morpho": "aps---mn1-"
    }, "fatus2": {"lemma": "fatus", "uri": "f0779", "pos": "n", "morpho": "n-s---mn4-"}, "fatuus1": {
        "lemma": "fatuus", "uri": "f9271", "pos": "a", "morpho": "aps---mn1-"
    }, "faustus1": {"lemma": "faustus", "uri": "f0287", "pos": "a", "morpho": "aps---mn1-"}, "Faustus2": {
        "lemma": "Faustus", "uri": "59986", "pos": "a", "morpho": "aps---fn1-"
    }, "faventia1": {"lemma": "fauentia", "uri": "f0236", "pos": "n", "morpho": "n-s---fn1-"}, "Faventia2": {
        "lemma": "Fauentia", "uri": "59987", "pos": "n", "morpho": "n-s---fn1-"
    }, "felicitas1": {"lemma": "felicitas", "uri": "f0322", "pos": "n", "morpho": "n-s---fn3-"}, "felix1": {
        "lemma": "felix", "uri": "f0327", "pos": "a", "morpho": "aps---an3i"
    }, "ferrarius1": {"lemma": "ferrarius", "uri": "f0390", "pos": "a", "morpho": "aps---mn1-"}, "ferrarius2": {
        "lemma": "ferrarius", "uri": "f0390", "pos": "n", "morpho": "n-s---mn2-"
    }, "festus1": {"lemma": "festus", "uri": "f0444", "pos": "a", "morpho": "aps---mn1-"}, "Festus2": {
        "lemma": "Festus", "uri": "59993", "pos": "n", "morpho": "n-s---mn2-"
    }, "fetus1": {"lemma": "fetus", "uri": "f0456", "pos": "a", "morpho": "aps---mn1-"}, "fetus2": {
        "lemma": "fetus", "uri": "f0456", "pos": "n", "morpho": "n-s---mn4-"
    }, "fidentia1": {"lemma": "fidentia", "uri": "f0486", "pos": "n", "morpho": "n-s---fn1-"}, "Fidentia2": {
        "lemma": "Fidentia", "uri": "60000", "pos": "n", "morpho": "n-s---fn1-"
    }, "fides1": {"lemma": "fides", "uri": "f0495", "pos": "n", "morpho": "n-s---fn5-"}, "fides2": {
        "lemma": "fides", "uri": "f0496", "pos": "n", "morpho": "n-s---fn3i"
    }, "fidus1": {"lemma": "fidus", "uri": "f0507", "pos": "a", "morpho": "aps---mn1-"}, "fidus2": {
        "lemma": "fidus", "uri": "f0507", "pos": "a", "morpho": "aps---mn1-"
    }, "figulus1": {"lemma": "figulus", "uri": "f0517", "pos": "n", "morpho": "n-s---mn2-"}, "Figulus2": {
        "lemma": "Figulus", "uri": "60001", "pos": "n", "morpho": "n-s---mn2-"
    }, "fimbria1": {"lemma": "fimbria", "uri": "f0542", "pos": "n", "morpho": "n-s---fn1-"}, "fimbriatus1": {
        "lemma": "fimbriatus", "uri": "f0543", "pos": "a", "morpho": "aps---mn1-"
    }, "fiscellus1": {"lemma": "fiscellus", "uri": "f9567", "pos": "n", "morpho": "n-s---mn2-"}, "Fiscellus2": {
        "lemma": "Fiscellus", "uri": "60004", "pos": "n", "morpho": "n-s---mn2-"
    }, "flaccus1": {"lemma": "flaccus", "uri": "f0598", "pos": "a", "morpho": "aps---mn1-"}, "Flaccus2": {
        "lemma": "Flaccus", "uri": "60005", "pos": "n", "morpho": "n-s---mn2-"
    }, "flamen1": {"lemma": "flamen", "uri": "f1301", "pos": "n", "morpho": "n-s---nn3-"}, "flamen2": {
        "lemma": "flamen", "uri": "f1301", "pos": "n", "morpho": "n-s---nn3-"
    }, "Flamen3": {"lemma": "Flamen", "uri": "60006", "pos": "n", "morpho": "n-s---mn3-"}, "flaminius1": {
        "lemma": "flaminius", "uri": "f0622", "pos": "a", "morpho": "aps---mn1-"
    }, "Flaminius2": {"lemma": "Flaminius", "uri": "60008", "pos": "a", "morpho": "aps---mn1-"}, "flamma1": {
        "lemma": "flamma", "uri": "f0623", "pos": "n", "morpho": "n-s---fn1-"
    }, "fletus1": {"lemma": "fletus", "uri": "110809", "pos": "a", "morpho": "aps---mn1-"}, "fletus2": {
        "lemma": "fletus", "uri": "f9207", "pos": "n", "morpho": "n-s---mn4-"
    }, "flexus1": {"lemma": "flexus", "uri": "110817", "pos": "a", "morpho": "aps---mn1-"}, "flexus2": {
        "lemma": "flexus", "uri": "f9208", "pos": "n", "morpho": "n-s---mn4-"
    }, "florus1": {"lemma": "florus", "uri": "f0702", "pos": "a", "morpho": "aps---mn1-"}, "Florus2": {
        "lemma": "Florus", "uri": "60014", "pos": "n", "morpho": "n-s---mn2-"
    }, "fluxus1": {"lemma": "fluxus", "uri": "42805", "pos": "a", "morpho": "aps---mn1-"}, "fluxus2": {
        "lemma": "fluxus", "uri": "f9211", "pos": "n", "morpho": "n-s---mn4-"
    }, "foedus1": {"lemma": "foedus", "uri": "f0763", "pos": "a", "morpho": "aps---mn1-"}, "foedus2": {
        "lemma": "foedus", "uri": "f0764", "pos": "n", "morpho": "n-s---nn3-"
    }, "foris1": {"lemma": "foris", "uri": "f0830", "pos": "n", "morpho": "n-s---fn3i"}, "foris2": {
        "lemma": "foris", "uri": "f0831", "pos": "r", "morpho": "rp--------"
    }, "formido1": {"lemma": "formido", "uri": "f0851", "pos": "v", "morpho": "v1spia--1-"}, "formido2": {
        "lemma": "formido", "uri": "f0852", "pos": "n", "morpho": "n-s---fn3-"
    }, "fornicatio1": {"lemma": "fornicatio", "uri": "f0873", "pos": "n", "morpho": "n-s---fn3-"}, "fornicatio2": {
        "lemma": "fornicatio", "uri": "f0873", "pos": "n", "morpho": "n-s---fn3-"
    }, "foruli1": {"lemma": "foruli", "uri": "29786", "pos": "n", "morpho": "n-p---mn2-"}, "Foruli2": {
        "lemma": "Foruli", "uri": "60018", "pos": "n", "morpho": "n-p---mn2-"
    }, "forus1": {"lemma": "forus", "uri": "f0901", "pos": "n", "morpho": "n-s---mn2-"}, "forus2": {
        "lemma": "forus", "uri": "f0901", "pos": "n", "morpho": "n-s---mn2-"
    }, "fotus1": {"lemma": "fotus", "uri": "111046", "pos": "a", "morpho": "aps---mn1-"}, "fotus2": {
        "lemma": "fotus", "uri": "f9213", "pos": "n", "morpho": "n-s---mn4-"
    }, "fratria1": {"lemma": "fratria", "uri": "f0940", "pos": "n", "morpho": "n-s---fn1-"}, "fratria2": {
        "lemma": "fratria", "uri": "f0940", "pos": "n", "morpho": "n-s---fn1-"
    }, "fraus1": {"lemma": "fraus", "uri": "f0956", "pos": "n", "morpho": "n-s---fn3-"}, "fraxinus1": {
        "lemma": "fraxinus", "uri": "f0958", "pos": "n", "morpho": "n-s---fn2-"
    }, "fraxinus2": {"lemma": "fraxinus", "uri": "52283", "pos": "a", "morpho": "aps---mn1-"}, "fretus1": {
        "lemma": "fretus", "uri": "f0981", "pos": "a", "morpho": "aps---mn1-"
    }, "frictus1": {"lemma": "frictus", "uri": "111127", "pos": "a", "morpho": "aps---mn1-"}, "frictus2": {
        "lemma": "frictus", "uri": "111128", "pos": "n", "morpho": "n-s---mn4-"
    }, "frigo1": {"lemma": "frigo", "uri": "f1302", "pos": "v", "morpho": "v1spia--3-"}, "frigo2": {
        "lemma": "frigo", "uri": "f1302", "pos": "v", "morpho": "v1spia--3-"
    }, "frigo3": {"lemma": "frigo", "uri": "f1302", "pos": "v", "morpho": "v1spia--3-"}, "frons1": {
        "lemma": "frons", "uri": "f1031", "pos": "n", "morpho": "n-s---fn3i"
    }, "frons2": {"lemma": "frons", "uri": "f1031", "pos": "n", "morpho": "n-s---fn3i"}, "fronto1": {
        "lemma": "fronto", "uri": "f8034", "pos": "n", "morpho": "n-s---mn3-"
    }, "Fronto2": {"lemma": "Fronto", "uri": "60025", "pos": "n", "morpho": "n-s---mn3-"}, "fructus1": {
        "lemma": "fructus", "uri": "f1058", "pos": "n", "morpho": "n-s---mn4-"
    }, "fructus2": {"lemma": "fructus", "uri": "f1058", "pos": "n", "morpho": "n-s---mn4-"}, "fucinus1": {
        "lemma": "fucinus", "uri": "f1084", "pos": "a", "morpho": "aps---mn1-"
    }, "Fucinus2": {"lemma": "Fucinus", "uri": "60027", "pos": "n", "morpho": "n-s---mn2-"}, "fundo1": {
        "lemma": "fundo", "uri": "f1176", "pos": "v", "morpho": "v1spia--3-"
    }, "fundo2": {"lemma": "fundo", "uri": "f1177", "pos": "v", "morpho": "v1spia--1-"}, "furio1": {
        "lemma": "furio", "uri": "f1221", "pos": "v", "morpho": "v1spia--1-"
    }, "furio2": {"lemma": "furio", "uri": "f1222", "pos": "v", "morpho": "v1spia--4-"}, "furor1": {
        "lemma": "furor", "uri": None, "pos": "v", "morpho": "v1spid--1-"
    }, "furor2": {"lemma": "furor", "uri": "f1231", "pos": "n", "morpho": "n-s---mn3-"}, "fuscus1": {
        "lemma": "fuscus", "uri": "f1246", "pos": "a", "morpho": "aps---mn1-"
    }, "fusus1": {"lemma": "fusus", "uri": "23570", "pos": "a", "morpho": "aps---mn1-"}, "fusus2": {
        "lemma": "fusus", "uri": "f9220", "pos": "n", "morpho": "n-s---mn4-"
    }, "fusus3": {"lemma": "fusus", "uri": "f9221", "pos": "n", "morpho": "n-s---mn2-"}, "futtile1": {
        "lemma": "futtile", "uri": "111373", "pos": "n", "morpho": "n-s---nn3i"
    }, "futtile2": {"lemma": "futtile", "uri": "111374", "pos": "r", "morpho": "rp--------"}, "galbus1": {
        "lemma": "galbus", "uri": "111404", "pos": "a", "morpho": "aps---mn1-"
    }, "galbus2": {"lemma": "galbus", "uri": "111404", "pos": "a", "morpho": "aps---mn1-"}, "galla1": {
        "lemma": "galla", "uri": "g0045", "pos": "n", "morpho": "n-s---fn1-"
    }, "Galli1": {"lemma": "Galli", "uri": "60051", "pos": "n", "morpho": "n-p---mn2-"}, "Galli2": {
        "lemma": "Galli", "uri": "60051", "pos": "n", "morpho": "n-p---mn2-"
    }, "gallina1": {"lemma": "gallina", "uri": "g0057", "pos": "n", "morpho": "n-s---fn1-"}, "gallus1": {
        "lemma": "gallus", "uri": "g0229", "pos": "n", "morpho": "n-s---mn2-"
    }, "Gallus2": {"lemma": "Gallus", "uri": "60052", "pos": "n", "morpho": "n-s---mn2-"}, "Gallus3": {
        "lemma": "Gallus", "uri": "60052", "pos": "n", "morpho": "n-s---mn2-"
    }, "Gallus4": {"lemma": "Gallus", "uri": "60052", "pos": "n", "morpho": "n-s---mn2-"}, "gelo1": {
        "lemma": "gelo", "uri": "g0128", "pos": "v", "morpho": "v1spia--1-"
    }, "Gelo2": {"lemma": "Gelo", "uri": "60067", "pos": "n", "morpho": "n-s---mn3-"}, "genitus1": {
        "lemma": "genitus", "uri": "40132", "pos": "a", "morpho": "aps---mn1-"
    }, "genitus2": {"lemma": "genitus", "uri": "g2283", "pos": "n", "morpho": "n-s---mn4-"}, "genuinus1": {
        "lemma": "genuinus", "uri": "g0214", "pos": "a", "morpho": "aps---mn1-"
    }, "genuinus2": {"lemma": "genuinus", "uri": "g0214", "pos": "a", "morpho": "aps---mn1-"}, "genus1": {
        "lemma": "genus", "uri": "g0213", "pos": "n", "morpho": "n-s---nn3-"
    }, "germanus1": {"lemma": "germanus", "uri": "g0230", "pos": "a", "morpho": "aps---mn1-"}, "gero1": {
        "lemma": "gero", "uri": "g0238", "pos": "v", "morpho": "v1spia--3-"
    }, "gero2": {"lemma": "gero", "uri": "111591", "pos": "n", "morpho": "n-s---mn3-"}, "gestio1": {
        "lemma": "gestio", "uri": "g0270", "pos": "n", "morpho": "n-s---fn3-"
    }, "gestio2": {"lemma": "gestio", "uri": "g0271", "pos": "v", "morpho": "v1spia--4-"}, "gestus1": {
        "lemma": "gestus", "uri": "111622", "pos": "a", "morpho": "aps---mn1-"
    }, "gestus2": {"lemma": "gestus", "uri": "g0279", "pos": "n", "morpho": "n-s---mn4-"}, "gibber1": {
        "lemma": "gibber", "uri": "g0280", "pos": "a", "morpho": "aps---mn1r"
    }, "gibber2": {"lemma": "gibber", "uri": "g0280", "pos": "n", "morpho": "n-s---mn3-"}, "gibbus1": {
        "lemma": "gibbus", "uri": "g0284", "pos": "a", "morpho": "aps---mn1-"
    }, "gibbus2": {"lemma": "gibbus", "uri": "g0284", "pos": "n", "morpho": "n-s---mn2-"}, "gillo1": {
        "lemma": "gillo", "uri": "g0301", "pos": "n", "morpho": "n-s---mn3-"
    }, "Gillo2": {"lemma": "Gillo", "uri": "60076", "pos": "n", "morpho": "n-s---mn3-"}, "Graecus1": {
        "lemma": "Graecus", "uri": "23675", "pos": "a", "morpho": "aps---mn1-"
    }, "Graecus2": {"lemma": "Graecus", "uri": "23675", "pos": "a", "morpho": "aps---mn1-"}, "gramma1": {
        "lemma": "gramma", "uri": "111854", "pos": "n", "morpho": "n-s---fn1-"
    }, "gramma2": {"lemma": "gramma", "uri": "g0511", "pos": "n", "morpho": "n-s---nn3-"}, "grammatice1": {
        "lemma": "grammatice", "uri": "98689", "pos": "n", "morpho": "n-s---fn1g"
    }, "grammatice2": {"lemma": "grammatice", "uri": "29402", "pos": "r", "morpho": "rp--------"}, "grammaticus1": {
        "lemma": "grammaticus", "uri": "g0516", "pos": "a", "morpho": "aps---mn1-"
    }, "grammaticus2": {"lemma": "grammaticus", "uri": "g0516", "pos": "n", "morpho": "n-s---mn2-"}, "graphice1": {
        "lemma": "graphice", "uri": "111888", "pos": "r", "morpho": "rp--------"
    }, "graphice2": {"lemma": "graphice", "uri": "g0551", "pos": "n", "morpho": "n-s---fn1g"}, "gressus1": {
        "lemma": "gressus", "uri": "111926", "pos": "a", "morpho": "aps---mn1-"
    }, "gressus2": {"lemma": "gressus", "uri": "g0481", "pos": "n", "morpho": "n-s---mn4-"}, "Grosphus2": {
        "lemma": "Grosphus", "uri": "111940", "pos": "n", "morpho": "n-s---mn2-"
    }, "grossus1": {"lemma": "grossus", "uri": "g0701", "pos": "n", "morpho": "n-s---cn2-"}, "grossus2": {
        "lemma": "grossus", "uri": "g0624", "pos": "a", "morpho": "aps---mn1-"
    }, "gryllus1": {"lemma": "gryllus", "uri": "g0634", "pos": "n", "morpho": "n-s---mn2-"}, "Gryllus2": {
        "lemma": "Gryllus", "uri": "60111", "pos": "n", "morpho": "n-s---mn2-"
    }, "gurges1": {"lemma": "gurges", "uri": "g0656", "pos": "n", "morpho": "n-s---mn3-"}, "Gurges2": {
        "lemma": "Gurges", "uri": "60114", "pos": "n", "morpho": "n-p---mn3-"
    }, "gurgulio1": {"lemma": "gurgulio", "uri": "g0657", "pos": "n", "morpho": "n-s---mn3-"}, "gurgulio2": {
        "lemma": "gurgulio", "uri": "g0657", "pos": "n", "morpho": "n-s---mn3-"
    }, "gutta1": {"lemma": "gutta", "uri": "g0669", "pos": "n", "morpho": "n-s---fn1-"}, "Gutta2": {
        "lemma": "Gutta", "uri": "60115", "pos": "n", "morpho": "n-s---fn1-"
    }, "gymnasium1": {"lemma": "gymnasium", "uri": "g0679", "pos": "n", "morpho": "n-s---nn2-"}, "habitus1": {
        "lemma": "habitus", "uri": "98716", "pos": "a", "morpho": "aps---mn1-"
    }, "habitus2": {"lemma": "habitus", "uri": "h0050", "pos": "n", "morpho": "n-s---mn4-"}, "harmonia1": {
        "lemma": "harmonia", "uri": "h0122", "pos": "n", "morpho": "n-s---fn1-"
    }, "Harmonia2": {"lemma": "Harmonia", "uri": "60140", "pos": "n", "morpho": "n-s---fn1-"}, "harpago1": {
        "lemma": "harpago", "uri": "h0127", "pos": "v", "morpho": "v1spia--1-"
    }, "harpago2": {"lemma": "harpago", "uri": "h0128", "pos": "n", "morpho": "n-s---mn3-"}, "harpax1": {
        "lemma": "harpax", "uri": "h0130", "pos": "a", "morpho": "aps---an3-"
    }, "Harpax2": {"lemma": "Harpax", "uri": "h0130", "pos": "n", "morpho": "n-s---mn3-"}, "haustus1": {
        "lemma": "haustus", "uri": "112141", "pos": "a", "morpho": "aps---mn1-"
    }, "haustus2": {"lemma": "haustus", "uri": "h0159", "pos": "n", "morpho": "n-s---mn4-"}, "hemina1": {
        "lemma": "hemina", "uri": "h0226", "pos": "n", "morpho": "n-s---fn1-"
    }, "Heniochus1": {"lemma": "Heniochus", "uri": "60172", "pos": "n", "morpho": "n-s---mn2-"}, "Heniochus2": {
        "lemma": "Heniochus", "uri": "60172", "pos": "n", "morpho": "n-s---mn2-"
    }, "hera1": {"lemma": "hera", "uri": "29841", "pos": "n", "morpho": "n-s---fn1-"}, "Hera2": {
        "lemma": "Hera", "uri": "60179", "pos": "n", "morpho": "n-s---fn1-"
    }, "Hera3": {"lemma": "Hera", "uri": "60179", "pos": "n", "morpho": "n-s---fn1-"}, "Heracleus1": {
        "lemma": "Heracleus", "uri": "60185", "pos": "a", "morpho": "aps---mn1-"
    }, "Heracleus2": {"lemma": "Heracleus", "uri": "60185", "pos": "a", "morpho": "aps---mn1-"}, "Heraclides1": {
        "lemma": "Heraclides", "uri": "60186", "pos": "n", "morpho": "n-s---mn3-"
    }, "Heraclides2": {"lemma": "Heraclides", "uri": "60186", "pos": "n", "morpho": "n-s---mn3-"}, "here1": {
        "lemma": "here", "uri": "46374", "pos": "r", "morpho": "rp--------"
    }, "Here2": {"lemma": "Here", "uri": "46118", "pos": "n", "morpho": "n-s---fn3g"}, "herous2": {
        "lemma": "herous", "uri": "h0318", "pos": "a", "morpho": "aps---mn1-"
    }, "hicine1": {"lemma": "hicine", "uri": "112358", "pos": "r", "morpho": "rp--------"}, "hicine2": {
        "lemma": "hicine", "uri": "112358", "pos": "r", "morpho": "rp--------"
    }, "hiera1": {"lemma": "hiera", "uri": "h0379", "pos": "n", "morpho": "n-s---fn1-"}, "hilaria1": {
        "lemma": "hilaria", "uri": "h9382", "pos": "n", "morpho": "n-s---fn1-"
    }, "hilaria2": {"lemma": "hilaria", "uri": "112383", "pos": "n", "morpho": "n-p---nn2-"}, "hilarus1": {
        "lemma": "hilarus", "uri": "h0388", "pos": "a", "morpho": "aps---mn1-"
    }, "Hilarus2": {"lemma": "Hilarus", "uri": "60226", "pos": "a", "morpho": "aps---mn1-"}, "Hister1": {
        "lemma": "Hister", "uri": "60254", "pos": "n", "morpho": "n-s---mn3-"
    }, "hister2": {"lemma": "hister", "uri": "112467", "pos": "n", "morpho": "n-s---mn2-"}, "historice1": {
        "lemma": "historice", "uri": "98760", "pos": "r", "morpho": "rp--------"
    }, "historice2": {"lemma": "historice", "uri": "h0465", "pos": "n", "morpho": "n-s---fn1g"}, "hoc1": {
        "lemma": "hoc", "uri": "46306", "pos": "r", "morpho": "rp--------"
    }, "hoc2": {"lemma": "hoc", "uri": "46306", "pos": "r", "morpho": "rp--------"}, "hora1": {
        "lemma": "hora", "uri": "h0553", "pos": "n", "morpho": "n-s---fn1-"
    }, "Horatius1": {"lemma": "Horatius", "uri": "60261", "pos": "a", "morpho": "aps---mn1-"}, "Horatius2": {
        "lemma": "Horatius", "uri": "60261", "pos": "a", "morpho": "aps---mn1-"
    }, "horreum1": {"lemma": "horreum", "uri": "h0589", "pos": "n", "morpho": "n-s---nn2-"}, "Horreum2": {
        "lemma": "Horreum", "uri": "60262", "pos": "n", "morpho": "n-s---nn2-"
    }, "hortator1": {"lemma": "hortator", "uri": "h0608", "pos": "n", "morpho": "n-s---mn3-"}, "hortensius1": {
        "lemma": "hortensius", "uri": "h0247", "pos": "a", "morpho": "aps---mn1-"
    }, "hostio1": {"lemma": "hostio", "uri": "h0638", "pos": "v", "morpho": "v1spia--4-"}, "hostio2": {
        "lemma": "hostio", "uri": "h0638", "pos": "v", "morpho": "v1spia--4-"
    }, "hostus1": {"lemma": "hostus", "uri": "h0642", "pos": "n", "morpho": "n-s---mn2-"}, "Hostus2": {
        "lemma": "Hostus", "uri": "60266", "pos": "n", "morpho": "n-s---mn2-"
    }, "Hyas1": {"lemma": "Hyas", "uri": "60273", "pos": "n", "morpho": "n-s---mn3-"}, "Hyas2": {
        "lemma": "Hyas", "uri": "60273", "pos": "n", "morpho": "n-s---mn3-"
    }, "hydrus1": {"lemma": "hydrus", "uri": "h0711", "pos": "n", "morpho": "n-s---mn2-"}, "Hydrus2": {
        "lemma": "Hydrus", "uri": "60279", "pos": "n", "morpho": "n-s---mn2-"
    }, "Iasius1": {"lemma": "Iasius", "uri": "60323", "pos": "n", "morpho": "n-s---mn2-"}, "Iasius2": {
        "lemma": "Iasius", "uri": "60323", "pos": "n", "morpho": "n-s---mn2-"
    }, "ictus1": {"lemma": "ictus", "uri": "112865", "pos": "a", "morpho": "aps---mn1-"}, "ictus2": {
        "lemma": "ictus", "uri": "i0094", "pos": "n", "morpho": "n-s---mn4-"
    }, "ignotus1": {"lemma": "ignotus", "uri": "35051", "pos": "a", "morpho": "aps---mn1-"}, "ignotus2": {
        "lemma": "ignotus", "uri": "35051", "pos": "a", "morpho": "aps---mn1-"
    }, "ilia1": {"lemma": "ilia", "uri": "98803", "pos": "n", "morpho": "n-s---fn1-"}, "Ilia2": {
        "lemma": "Ilia", "uri": "60346", "pos": "n", "morpho": "n-s---fn1-"
    }, "iliacus2": {"lemma": "iliacus", "uri": "i9165", "pos": "a", "morpho": "aps---mn1-"}, "Ilienses1": {
        "lemma": "Ilienses", "uri": "60347", "pos": "n", "morpho": "n-p---mn3-"
    }, "Ilienses2": {"lemma": "Ilienses", "uri": "60347", "pos": "n", "morpho": "n-p---mn3-"}, "Ilium1": {
        "lemma": "Ilium", "uri": "60350", "pos": "n", "morpho": "n-s---nn3-"
    }, "ilium2": {"lemma": "ilium", "uri": "112950", "pos": "n", "morpho": "n-s---nn2-"}, "illapsus1": {
        "lemma": "illapsus", "uri": "i9854", "pos": "n", "morpho": "n-s---mn4-"
    }, "illapsus2": {"lemma": "illapsus", "uri": "i9854", "pos": "n", "morpho": "n-s---mn4-"}, "illectus1": {
        "lemma": "illectus", "uri": "98812", "pos": "a", "morpho": "aps---mn1-"
    }, "illectus2": {"lemma": "illectus", "uri": "98812", "pos": "a", "morpho": "aps---mn1-"}, "illectus3": {
        "lemma": "illectus", "uri": "i0225", "pos": "n", "morpho": "n-s---mn4-"
    }, "illex1": {"lemma": "illex", "uri": "i0228", "pos": "a", "morpho": "aps---an3-"}, "illex2": {
        "lemma": "illex", "uri": "i0228", "pos": "a", "morpho": "aps---an3-"
    }, "illic1": {"lemma": "illic", "uri": "45900", "pos": "r", "morpho": "rp--------"}, "illic2": {
        "lemma": "illic", "uri": "45900", "pos": "r", "morpho": "rp--------"
    }, "illisus1": {"lemma": "illisus", "uri": "i0243", "pos": "n", "morpho": "n-s---mn4-"}, "illisus2": {
        "lemma": "illisus", "uri": "i0243", "pos": "n", "morpho": "n-s---mn4-"
    }, "illitus1": {"lemma": "illitus", "uri": "i9855", "pos": "n", "morpho": "n-s---mn4-"}, "illitus2": {
        "lemma": "illitus", "uri": "i9855", "pos": "n", "morpho": "n-s---mn4-"
    }, "illuc1": {"lemma": "illuc", "uri": "37414", "pos": "r", "morpho": "rp--------"}, "illuc2": {
        "lemma": "illuc", "uri": "37414", "pos": "r", "morpho": "rp--------"
    }, "imminutus1": {"lemma": "imminutus", "uri": "i3122", "pos": "a", "morpho": "aps---mn1-"}, "imminutus2": {
        "lemma": "imminutus", "uri": "i3122", "pos": "a", "morpho": "aps---mn1-"
    }, "immissus1": {"lemma": "immissus", "uri": "113114", "pos": "a", "morpho": "aps---mn1-"}, "immissus2": {
        "lemma": "immissus", "uri": "i9857", "pos": "n", "morpho": "n-s---mn4-"
    }, "immixtus1": {"lemma": "immixtus", "uri": "i3123", "pos": "a", "morpho": "aps---mn1-"}, "immixtus2": {
        "lemma": "immixtus", "uri": "i3123", "pos": "a", "morpho": "aps---mn1-"
    }, "immutabilis1": {"lemma": "immutabilis", "uri": "i1337", "pos": "a", "morpho": "aps---cn3i"}, "immutabilis2": {
        "lemma": "immutabilis", "uri": "i1337", "pos": "a", "morpho": "aps---cn3i"
    }, "immutatus1": {"lemma": "immutatus", "uri": "i3127", "pos": "a", "morpho": "aps---mn1-"}, "immutatus2": {
        "lemma": "immutatus", "uri": "i3127", "pos": "a", "morpho": "aps---mn1-"
    }, "immutilatus1": {"lemma": "immutilatus", "uri": "i0429", "pos": "a", "morpho": "aps---mn1-"}, "immutilatus2": {
        "lemma": "immutilatus", "uri": "i0429", "pos": "a", "morpho": "aps---mn1-"
    }, "impensus1": {"lemma": "impensus", "uri": "45422", "pos": "a", "morpho": "aps---mn1-"}, "impensus2": {
        "lemma": "impensus", "uri": "i0491", "pos": "n", "morpho": "n-s---mn4-"
    }, "impetibilis1": {"lemma": "impetibilis", "uri": "i3129", "pos": "a", "morpho": "aps---cn3i"}, "impetibilis2": {
        "lemma": "impetibilis", "uri": "i3129", "pos": "a", "morpho": "aps---cn3i"
    }, "implexus1": {"lemma": "implexus", "uri": "33824", "pos": "a", "morpho": "aps---mn1-"}, "implexus2": {
        "lemma": "implexus", "uri": "i9858", "pos": "n", "morpho": "n-s---mn4-"
    }, "impressus1": {"lemma": "impressus", "uri": "50044", "pos": "a", "morpho": "aps---mn1-"}, "impressus2": {
        "lemma": "impressus", "uri": "50044", "pos": "a", "morpho": "aps---mn1-"
    }, "impressus3": {"lemma": "impressus", "uri": "i0621", "pos": "n", "morpho": "n-s---mn4-"}, "impropero1": {
        "lemma": "impropero", "uri": "i0652", "pos": "v", "morpho": "v1spia--1-"
    }, "impropero2": {"lemma": "impropero", "uri": "i0652", "pos": "v", "morpho": "v1spia--1-"}, "impugnatus1": {
        "lemma": "impugnatus", "uri": "98859", "pos": "a", "morpho": "aps---mn1-"
    }, "impugnatus2": {"lemma": "impugnatus", "uri": "98859", "pos": "a", "morpho": "aps---mn1-"}, "impulsus1": {
        "lemma": "impulsus", "uri": "i9860", "pos": "n", "morpho": "n-s---mn4-"
    }, "impulsus2": {"lemma": "impulsus", "uri": "i9860", "pos": "n", "morpho": "n-s---mn4-"}, "imputatus1": {
        "lemma": "imputatus", "uri": "i3133", "pos": "a", "morpho": "aps---mn1-"
    }, "imputatus2": {"lemma": "imputatus", "uri": "i3133", "pos": "a", "morpho": "aps---mn1-"}, "in1": {
        "lemma": "in", "uri": "i0702", "pos": "p", "morpho": "p---------"
    }, "in2": {"lemma": "in", "uri": "i0702", "pos": "p", "morpho": "p---------"}, "inauditus1": {
        "lemma": "inauditus", "uri": "i3138", "pos": "a", "morpho": "aps---mn1-"
    }, "inauditus2": {"lemma": "inauditus", "uri": "i3138", "pos": "a", "morpho": "aps---mn1-"}, "inauratus1": {
        "lemma": "inauratus", "uri": "i1003", "pos": "a", "morpho": "aps---mn1-"
    }, "inauratus2": {"lemma": "inauratus", "uri": "i1003", "pos": "a", "morpho": "aps---mn1-"}, "incensus1": {
        "lemma": "incensus", "uri": "i0863", "pos": "a", "morpho": "aps---mn1-"
    }, "incensus2": {"lemma": "incensus", "uri": "i0863", "pos": "a", "morpho": "aps---mn1-"}, "inceptus1": {
        "lemma": "inceptus", "uri": "113503", "pos": "a", "morpho": "aps---mn1-"
    }, "inceptus2": {"lemma": "inceptus", "uri": "i9861", "pos": "n", "morpho": "n-s---mn4-"}, "incerto1": {
        "lemma": "incerto", "uri": "113507", "pos": "r", "morpho": "rp--------"
    }, "incerto2": {"lemma": "incerto", "uri": "i0877", "pos": "v", "morpho": "v1spia--1-"}, "incestus1": {
        "lemma": "incestus", "uri": "i0888", "pos": "a", "morpho": "aps---mn1-"
    }, "incestus2": {"lemma": "incestus", "uri": "i0888", "pos": "n", "morpho": "n-s---mn4-"},
"incido1": {"lemma": "incido", "uri": "i0897", "pos": "v", "morpho": "v1spia--3-"},
"incido2": {"lemma": "incido", "uri": "i0898", "pos": "v", "morpho": "v1spia--3-"},
    "incisus1": {
        "lemma": "incisus", "uri": "113538", "pos": "a", "morpho": "aps---mn1-"
    }, "incisus2": {"lemma": "incisus", "uri": "i9862", "pos": "n", "morpho": "n-s---mn4-"}, "incitatus1": {
        "lemma": "incitatus", "uri": "57905", "pos": "a", "morpho": "aps---mn1-"
    }, "incitatus2": {"lemma": "incitatus", "uri": "113547", "pos": "n", "morpho": "n-s---mn4-"}, "incitus1": {
        "lemma": "incitus", "uri": "i9849", "pos": "a", "morpho": "aps---mn1-"
    }, "incitus2": {"lemma": "incitus", "uri": "i9849", "pos": "a", "morpho": "aps---mn1-"}, "incitus3": {
        "lemma": "incitus", "uri": "i9849", "pos": "n", "morpho": "n-s---mn4-"
    }, "inclinatus1": {"lemma": "inclinatus", "uri": "44070", "pos": "a", "morpho": "aps---mn1-"}, "inclinatus2": {
        "lemma": "inclinatus", "uri": "i9863", "pos": "n", "morpho": "n-s---mn4-"
    }, "inclinis1": {"lemma": "inclinis", "uri": "i1347", "pos": "a", "morpho": "aps---cn3i"}, "inclinis2": {
        "lemma": "inclinis", "uri": "i1347", "pos": "a", "morpho": "aps---cn3i"
    }, "incoctus1": {"lemma": "incoctus", "uri": "i3144", "pos": "a", "morpho": "aps---mn1-"}, "incoctus2": {
        "lemma": "incoctus", "uri": "i3144", "pos": "a", "morpho": "aps---mn1-"
    }, "incolo1": {"lemma": "incolo", "uri": "i0965", "pos": "v", "morpho": "v1spia--3-"}, "incolo2": {
        "lemma": "incolo", "uri": "113593", "pos": "v", "morpho": "v1spia--1-"
    }, "inconsultus1": {"lemma": "inconsultus", "uri": "i1052", "pos": "a", "morpho": "aps---mn1-"}, "inconsultus2": {
        "lemma": "inconsultus", "uri": "i1052", "pos": "n", "morpho": "n-s---mn4-"
    }, "incorporatus1": {"lemma": "incorporatus", "uri": "113722", "pos": "a", "morpho": "aps---mn1-"},
    "incorporatus2": {
        "lemma": "incorporatus", "uri": "113722", "pos": "a", "morpho": "aps---mn1-"
    }, "increpitus1": {"lemma": "increpitus", "uri": "113742", "pos": "a", "morpho": "aps---mn1-"}, "increpitus2": {
        "lemma": "increpitus", "uri": "i1108", "pos": "n", "morpho": "n-s---mn4-"
    }, "incretus1": {"lemma": "incretus", "uri": "i3149", "pos": "a", "morpho": "aps---mn1-"}, "incretus2": {
        "lemma": "incretus", "uri": "i3149", "pos": "a", "morpho": "aps---mn1-"
    }, "incruentatus1": {"lemma": "incruentatus", "uri": "i1123", "pos": "a", "morpho": "aps---mn1-"},
    "incruentatus2": {
        "lemma": "incruentatus", "uri": "i1123", "pos": "a", "morpho": "aps---mn1-"
    }, "incubitus1": {"lemma": "incubitus", "uri": "113758", "pos": "a", "morpho": "aps---mn1-"}, "incubitus2": {
        "lemma": "incubitus", "uri": "i9865", "pos": "n", "morpho": "n-s---mn4-"
    }, "incubo1": {"lemma": "incubo", "uri": "i1131", "pos": "v", "morpho": "v1spia--1-"}, "incubo2": {
        "lemma": "incubo", "uri": "i1132", "pos": "n", "morpho": "n-s---mn3-"
    }, "incultus1": {"lemma": "incultus", "uri": "i9866", "pos": "a", "morpho": "aps---mn1-"}, "incultus2": {
        "lemma": "incultus", "uri": "i9866", "pos": "n", "morpho": "n-s---mn4-"
    }, "incursus1": {"lemma": "incursus", "uri": "113768", "pos": "a", "morpho": "aps---mn1-"}, "incursus2": {
        "lemma": "incursus", "uri": "i9867", "pos": "n", "morpho": "n-s---mn4-"
    }, "incussus1": {"lemma": "incussus", "uri": "113781", "pos": "a", "morpho": "aps---mn1-"}, "incussus2": {
        "lemma": "incussus", "uri": "i9868", "pos": "n", "morpho": "n-s---mn4-"
    }, "indagatus1": {"lemma": "indagatus", "uri": "113784", "pos": "a", "morpho": "aps---mn1-"}, "indagatus2": {
        "lemma": "indagatus", "uri": "i9869", "pos": "n", "morpho": "n-s---mn4-"
    }, "indago1": {"lemma": "indago", "uri": "i1185", "pos": "v", "morpho": "v1spia--1-"}, "indago2": {
        "lemma": "indago", "uri": "i1186", "pos": "n", "morpho": "n-s---fn3-"
    }, "indico1": {"lemma": "indico", "uri": "i1252", "pos": "v", "morpho": "v1spia--1-"}, "indico2": {
        "lemma": "indico", "uri": "i1253", "pos": "v", "morpho": "v1spia--3-"
    }, "indictus1": {"lemma": "indictus", "uri": "i3155", "pos": "a", "morpho": "aps---mn1-"}, "indictus2": {
        "lemma": "indictus", "uri": "i3155", "pos": "a", "morpho": "aps---mn1-"
    }, "indiges2": {"lemma": "indiges", "uri": "i1273", "pos": "a", "morpho": "aps---an3-"}, "indigestus1": {
        "lemma": "indigestus", "uri": "i1269", "pos": "a", "morpho": "aps---mn1-"
    }, "indigestus2": {"lemma": "indigestus", "uri": "i1269", "pos": "n", "morpho": "n-s---mn4-"}, "inductus1": {
        "lemma": "inductus", "uri": "29509", "pos": "a", "morpho": "aps---mn1-"
    }, "inductus2": {"lemma": "inductus", "uri": "i9870", "pos": "n", "morpho": "n-s---mn4-"}, "indultus1": {
        "lemma": "indultus", "uri": "113949", "pos": "a", "morpho": "aps---mn1-"
    }, "indultus2": {"lemma": "indultus", "uri": "i9871", "pos": "n", "morpho": "n-s---mn4-"}, "Indus1": {
        "lemma": "Indus", "uri": "60361", "pos": "n", "morpho": "n-s---mn2-"
    }, "Indus2": {"lemma": "Indus", "uri": "60361", "pos": "n", "morpho": "n-s---mn2-"}, "industria1": {
        "lemma": "industria", "uri": "i1376", "pos": "n", "morpho": "n-s---fn1-"
    }, "Industria2": {"lemma": "Industria", "uri": "60362", "pos": "n", "morpho": "n-s---fn1-"}, "indutus1": {
        "lemma": "indutus", "uri": "113955", "pos": "a", "morpho": "aps---mn1-"
    }, "indutus2": {"lemma": "indutus", "uri": "i9872", "pos": "n", "morpho": "n-s---mn4-"}, "infectio1": {
        "lemma": "infectio", "uri": "i1525", "pos": "n", "morpho": "n-s---fn3-"
    }, "infectio2": {"lemma": "infectio", "uri": "i1525", "pos": "n", "morpho": "n-s---fn3-"}, "infectus1": {
        "lemma": "infectus", "uri": "i3164", "pos": "a", "morpho": "aps---mn1-"
    }, "infectus2": {"lemma": "infectus", "uri": "i3164", "pos": "a", "morpho": "aps---mn1-"}, "infectus3": {
        "lemma": "infectus", "uri": "i9873", "pos": "n", "morpho": "n-s---mn4-"
    }, "inferius1": {"lemma": "inferius", "uri": "98975", "pos": "r", "morpho": "rp--------"}, "inferius2": {
        "lemma": "inferius", "uri": "i8542", "pos": "a", "morpho": "aps---mn1-"
    }, "inficiens1": {"lemma": "inficiens", "uri": "i3167", "pos": "a", "morpho": "aps---an3i"}, "inficiens2": {
        "lemma": "inficiens", "uri": "i3167", "pos": "a", "morpho": "aps---an3i"
    }, "infirmo1": {"lemma": "infirmo", "uri": "i1584", "pos": "v", "morpho": "v1spia--1-"}, "infirmo2": {
        "lemma": "infirmo", "uri": "i1584", "pos": "v", "morpho": "v1spia--1-"
    }, "inflatus1": {"lemma": "inflatus", "uri": "24183", "pos": "a", "morpho": "aps---mn1-"}, "inflatus2": {
        "lemma": "inflatus", "uri": "i1591", "pos": "n", "morpho": "n-s---mn4-"
    }, "inflexus1": {"lemma": "inflexus", "uri": "i3168", "pos": "a", "morpho": "aps---mn1-"}, "inflexus2": {
        "lemma": "inflexus", "uri": "i3168", "pos": "a", "morpho": "aps---mn1-"
    }, "inflexus3": {"lemma": "inflexus", "uri": "i9874", "pos": "n", "morpho": "n-s---mn4-"}, "inflictus1": {
        "lemma": "inflictus", "uri": "114184", "pos": "a", "morpho": "aps---mn1-"
    }, "inflictus2": {"lemma": "inflictus", "uri": "i9875", "pos": "n", "morpho": "n-s---mn4-"}, "inforo1": {
        "lemma": "inforo", "uri": "i1629", "pos": "v", "morpho": "v1spia--1-"
    }, "inforo2": {"lemma": "inforo", "uri": "i1629", "pos": "v", "morpho": "v1spia--1-"}, "infractus1": {
        "lemma": "infractus", "uri": "i3170", "pos": "a", "morpho": "aps---mn1-"
    }, "infractus2": {"lemma": "infractus", "uri": "i3170", "pos": "a", "morpho": "aps---mn1-"}, "infrenatus1": {
        "lemma": "infrenatus", "uri": "i3171", "pos": "a", "morpho": "aps---mn1-"
    }, "infrenatus2": {"lemma": "infrenatus", "uri": "i3171", "pos": "a", "morpho": "aps---mn1-"}, "infucatus1": {
        "lemma": "infucatus", "uri": "i3172", "pos": "a", "morpho": "aps---mn1-"
    }, "infucatus2": {"lemma": "infucatus", "uri": "i3172", "pos": "a", "morpho": "aps---mn1-"}, "infusus1": {
        "lemma": "infusus", "uri": "114246", "pos": "a", "morpho": "aps---mn1-"
    }, "infusus2": {"lemma": "infusus", "uri": "i9878", "pos": "n", "morpho": "n-s---mn4-"}, "ingenitus1": {
        "lemma": "ingenitus", "uri": "i3174", "pos": "a", "morpho": "aps---mn1-"
    }, "ingenitus2": {"lemma": "ingenitus", "uri": "i3174", "pos": "a", "morpho": "aps---mn1-"}, "ingestus1": {
        "lemma": "ingestus", "uri": "114269", "pos": "a", "morpho": "aps---mn1-"
    }, "ingestus2": {"lemma": "ingestus", "uri": "i9879", "pos": "n", "morpho": "n-s---mn4-"}, "inhabitabilis1": {
        "lemma": "inhabitabilis", "uri": "i1723", "pos": "a", "morpho": "aps---cn3i"
    }, "inhabitabilis2": {"lemma": "inhabitabilis", "uri": "i1723", "pos": "a", "morpho": "aps---cn3i"}, "initus1": {
        "lemma": "initus", "uri": "114358", "pos": "a", "morpho": "aps---mn1-"
    }, "initus2": {"lemma": "initus", "uri": "i9883", "pos": "n", "morpho": "n-s---mn4-"}, "injectus1": {
        "lemma": "iniectus", "uri": "114329", "pos": "a", "morpho": "aps---mn1-"
    }, "injectus2": {"lemma": "iniectus", "uri": "i9882", "pos": "n", "morpho": "n-s---mn4-"}, "injunctus1": {
        "lemma": "iniunctus", "uri": "i3177", "pos": "a", "morpho": "aps---mn1-"
    }, "injunctus2": {"lemma": "iniunctus", "uri": "i3177", "pos": "a", "morpho": "aps---mn1-"}, "injussus1": {
        "lemma": "iniussus", "uri": "i1805", "pos": "a", "morpho": "aps---mn1-"
    }, "injussus2": {"lemma": "iniussus", "uri": "99003", "pos": "n", "morpho": "n-s---mn4-"}, "innatus1": {
        "lemma": "innatus", "uri": "i3180", "pos": "a", "morpho": "aps---mn1-"
    }, "innatus2": {"lemma": "innatus", "uri": "i3180", "pos": "a", "morpho": "aps---mn1-"}, "innutritus1": {
        "lemma": "innutritus", "uri": "i3181", "pos": "a", "morpho": "aps---mn1-"
    }, "innutritus2": {"lemma": "innutritus", "uri": "i3181", "pos": "a", "morpho": "aps---mn1-"}, "inquies1": {
        "lemma": "inquies", "uri": None, "pos": "n", "morpho": "n-s---fn3-"
    }, "inquies2": {"lemma": "inquies", "uri": "i1921", "pos": "a", "morpho": "aps---an3-"}, "inquilinus1": {
        "lemma": "inquilinus", "uri": "i1922", "pos": "n", "morpho": "n-s---mn2-"
    }, "inquilinus2": {"lemma": "inquilinus", "uri": "114472", "pos": "a", "morpho": "aps---mn1-"}, "inquisitus1": {
        "lemma": "inquisitus", "uri": "i3184", "pos": "a", "morpho": "aps---mn1-"
    }, "inquisitus2": {"lemma": "inquisitus", "uri": "i3184", "pos": "a", "morpho": "aps---mn1-"}, "insaeptus1": {
        "lemma": "insaeptus", "uri": "i3185", "pos": "a", "morpho": "aps---mn1-"
    }, "insaeptus2": {"lemma": "insaeptus", "uri": "i3185", "pos": "a", "morpho": "aps---mn1-"}, "inscensus1": {
        "lemma": "inscensus", "uri": "114498", "pos": "a", "morpho": "aps---mn1-"
    }, "inscensus2": {"lemma": "inscensus", "uri": "i9884", "pos": "n", "morpho": "n-s---mn4-"}, "inscriptus1": {
        "lemma": "inscriptus", "uri": "i3187", "pos": "a", "morpho": "aps---mn1-"
    }, "inscriptus2": {"lemma": "inscriptus", "uri": "i3187", "pos": "a", "morpho": "aps---mn1-"}, "inseco1": {
        "lemma": "inseco", "uri": "i1973", "pos": "v", "morpho": "v1spia--1-"
    }, "inseco2": {"lemma": "inseco", "uri": "i1974", "pos": "v", "morpho": "v1spia--3-"}, "insectus1": {
        "lemma": "insectus", "uri": "i3189", "pos": "a", "morpho": "aps---mn1-"
    }, "insectus2": {"lemma": "insectus", "uri": "i3189", "pos": "a", "morpho": "aps---mn1-"}, "insequenter1": {
        "lemma": "insequenter", "uri": "114545", "pos": "r", "morpho": "rp--------"
    }, "insequenter2": {"lemma": "insequenter", "uri": "114545", "pos": "r", "morpho": "rp--------"}, "insero1": {
        "lemma": "insero", "uri": "i2002", "pos": "v", "morpho": "v1spia--3-"
    }, "insero2": {"lemma": "insero", "uri": "i2002", "pos": "v", "morpho": "v1spia--3-"}, "insessus1": {
        "lemma": "insessus", "uri": "i3190", "pos": "a", "morpho": "aps---mn1-"
    }, "insessus2": {"lemma": "insessus", "uri": "i3190", "pos": "a", "morpho": "aps---mn1-"}, "insitor1": {
        "lemma": "insitor", "uri": "i2047", "pos": "n", "morpho": "n-s---mn3-"
    }, "insitus1": {"lemma": "insitus", "uri": "57089", "pos": "a", "morpho": "aps---mn1-"}, "insitus2": {
        "lemma": "insitus", "uri": "i9885", "pos": "n", "morpho": "n-s---mn4-"
    }, "insomnium1": {"lemma": "insomnium", "uri": "i2067", "pos": "n", "morpho": "n-s---nn2-"}, "insomnium2": {
        "lemma": "insomnium", "uri": "i2067", "pos": "n", "morpho": "n-s---nn2-"
    }, "inspectus1": {"lemma": "inspectus", "uri": "114623", "pos": "a", "morpho": "aps---mn1-"}, "inspectus2": {
        "lemma": "inspectus", "uri": "i9886", "pos": "n", "morpho": "n-s---mn4-"
    }, "inspersus1": {"lemma": "inspersus", "uri": "114627", "pos": "a", "morpho": "aps---mn1-"}, "inspersus2": {
        "lemma": "inspersus", "uri": "i9887", "pos": "n", "morpho": "n-s---mn4-"
    }, "instinctus1": {"lemma": "instinctus", "uri": "114660", "pos": "a", "morpho": "aps---mn1-"}, "instinctus2": {
        "lemma": "instinctus", "uri": "i9889", "pos": "n", "morpho": "n-s---mn4-"
    }, "instratus1": {"lemma": "instratus", "uri": "32932", "pos": "a", "morpho": "aps---mn1-"}, "instratus2": {
        "lemma": "instratus", "uri": "32932", "pos": "a", "morpho": "aps---mn1-"
    }, "instructus1": {"lemma": "instructus", "uri": "24319", "pos": "a", "morpho": "aps---mn1-"}, "instructus2": {
        "lemma": "instructus", "uri": "i9891", "pos": "n", "morpho": "n-s---mn4-"
    }, "insuetus1": {"lemma": "insuetus", "uri": "i3192", "pos": "a", "morpho": "aps---mn1-"}, "insuetus2": {
        "lemma": "insuetus", "uri": "i3192", "pos": "a", "morpho": "aps---mn1-"
    }, "insula1": {"lemma": "insula", "uri": "i2175", "pos": "n", "morpho": "n-s---fn1-"}, "intactus1": {
        "lemma": "intactus", "uri": "i2209", "pos": "a", "morpho": "aps---mn1-"
    }, "intactus2": {"lemma": "intactus", "uri": "i2209", "pos": "n", "morpho": "n-s---mn4-"}, "intectus1": {
        "lemma": "intectus", "uri": "i3194", "pos": "a", "morpho": "aps---mn1-"
    }, "intectus2": {"lemma": "intectus", "uri": "i3194", "pos": "a", "morpho": "aps---mn1-"}, "intellectus1": {
        "lemma": "intellectus", "uri": "114755", "pos": "a", "morpho": "aps---mn1-"
    }, "intellectus2": {"lemma": "intellectus", "uri": "i9893", "pos": "n", "morpho": "n-s---mn4-"}, "intentatus1": {
        "lemma": "intentatus", "uri": "114783", "pos": "a", "morpho": "aps---mn1-"
    }, "intentatus2": {"lemma": "intentatus", "uri": "114783", "pos": "a", "morpho": "aps---mn1-"}, "intentus1": {
        "lemma": "intentus", "uri": "24351", "pos": "a", "morpho": "aps---mn1-"
    }, "intentus2": {"lemma": "intentus", "uri": "i2276", "pos": "n", "morpho": "n-s---mn4-"}, "interceptus1": {
        "lemma": "interceptus", "uri": "114808", "pos": "a", "morpho": "aps---mn1-"
    }, "interceptus2": {"lemma": "interceptus", "uri": "i9894", "pos": "n", "morpho": "n-s---mn4-"}, "intercursus1": {
        "lemma": "intercursus", "uri": "114824", "pos": "a", "morpho": "aps---mn1-"
    }, "intercursus2": {"lemma": "intercursus", "uri": "i9896", "pos": "n", "morpho": "n-s---mn4-"}, "interdictus1": {
        "lemma": "interdictus", "uri": "114832", "pos": "a", "morpho": "aps---mn1-"
    }, "interdictus2": {"lemma": "interdictus", "uri": "114833", "pos": "n", "morpho": "n-s---mn4-"}, "interitus1": {
        "lemma": "interitus", "uri": "114881", "pos": "a", "morpho": "aps---mn1-"
    }, "interitus2": {"lemma": "interitus", "uri": "i9897", "pos": "n", "morpho": "n-s---mn4-"}, "interjectus1": {
        "lemma": "interiectus", "uri": "35899", "pos": "a", "morpho": "aps---mn1-"
    }, "interjectus2": {"lemma": "interiectus", "uri": "i2350", "pos": "n", "morpho": "n-s---mn4-"}, "interminatus1": {
        "lemma": "interminatus", "uri": "i3195", "pos": "a", "morpho": "aps---mn1-"
    }, "interminatus2": {"lemma": "interminatus", "uri": "i3195", "pos": "a", "morpho": "aps---mn1-"}, "intermissus1": {
        "lemma": "intermissus", "uri": "114909", "pos": "a", "morpho": "aps---mn1-"
    }, "intermissus2": {"lemma": "intermissus", "uri": "i9898", "pos": "n", "morpho": "n-s---mn4-"}, "interpellatus1": {
        "lemma": "interpellatus", "uri": "114950", "pos": "a", "morpho": "aps---mn1-"
    }, "interpellatus2": {"lemma": "interpellatus", "uri": "114951", "pos": "n", "morpho": "n-s---mn4-"},
    "interpositus1": {
        "lemma": "interpositus", "uri": "114964", "pos": "a", "morpho": "aps---mn1-"
    }, "interpositus2": {"lemma": "interpositus", "uri": "i9899", "pos": "n", "morpho": "n-s---mn4-"}, "intersero1": {
        "lemma": "intersero", "uri": "i2491", "pos": "v", "morpho": "v1spia--3-"
    }, "intersero2": {"lemma": "intersero", "uri": "i2491", "pos": "v", "morpho": "v1spia--3-"}, "interversor1": {
        "lemma": "interuersor", "uri": "i2534", "pos": "v", "morpho": "v1spid--1-"
    }, "interversor2": {"lemma": "interuersor", "uri": "i2535", "pos": "n", "morpho": "n-s---mn3-"}, "intestabilis1": {
        "lemma": "intestabilis", "uri": "i2548", "pos": "a", "morpho": "aps---cn3i"
    }, "intestabilis2": {"lemma": "intestabilis", "uri": "i2548", "pos": "a", "morpho": "aps---cn3i"}, "intestatus1": {
        "lemma": "intestatus", "uri": "i2549", "pos": "a", "morpho": "aps---mn1-"
    }, "intestatus2": {"lemma": "intestatus", "uri": "i2549", "pos": "a", "morpho": "aps---mn1-"}, "intextus1": {
        "lemma": "intextus", "uri": "115061", "pos": "a", "morpho": "aps---mn1-"
    }, "intextus2": {"lemma": "intextus", "uri": "i2542", "pos": "n", "morpho": "n-s---mn4-"}, "intinctus1": {
        "lemma": "intinctus", "uri": "115074", "pos": "a", "morpho": "aps---mn1-"
    }, "intinctus2": {"lemma": "intinctus", "uri": "i9900", "pos": "n", "morpho": "n-s---mn4-"}, "intonsus1": {
        "lemma": "intonsus", "uri": "i3199", "pos": "a", "morpho": "aps---mn1-"
    }, "intonsus2": {"lemma": "intonsus", "uri": "i3199", "pos": "a", "morpho": "aps---mn1-"}, "intremulus1": {
        "lemma": "intremulus", "uri": "i2586", "pos": "a", "morpho": "aps---mn1-"
    }, "intremulus2": {"lemma": "intremulus", "uri": "i2586", "pos": "a", "morpho": "aps---mn1-"}, "intrinsecus1": {
        "lemma": "intrinsecus", "uri": "i2593", "pos": "r", "morpho": "rp--------"
    }, "intrinsecus2": {"lemma": "intrinsecus", "uri": "115111", "pos": "a", "morpho": "aps---mn1-"}, "intritus1": {
        "lemma": "intritus", "uri": "i3203", "pos": "a", "morpho": "aps---mn1-"
    }, "intritus2": {"lemma": "intritus", "uri": "i3203", "pos": "a", "morpho": "aps---mn1-"}, "intro1": {
        "lemma": "intro", "uri": "i2595", "pos": "r", "morpho": "rp--------"
    }, "intro2": {"lemma": "intro", "uri": "i2596", "pos": "v", "morpho": "v1spia--1-"}, "introitus1": {
        "lemma": "introitus", "uri": "115122", "pos": "a", "morpho": "aps---mn1-"
    }, "introitus2": {"lemma": "introitus", "uri": "i2599", "pos": "n", "morpho": "n-s---mn4-"}, "inustus1": {
        "lemma": "inustus", "uri": "i3206", "pos": "a", "morpho": "aps---mn1-"
    }, "inustus2": {"lemma": "inustus", "uri": "i3206", "pos": "a", "morpho": "aps---mn1-"}, "invasus1": {
        "lemma": "inuasus", "uri": "115153", "pos": "a", "morpho": "aps---mn1-"
    }, "invasus2": {"lemma": "inuasus", "uri": "i2600", "pos": "n", "morpho": "n-s---mn4-"}, "invectus1": {
        "lemma": "inuectus", "uri": "115164", "pos": "a", "morpho": "aps---mn1-"
    }, "invectus2": {"lemma": "inuectus", "uri": "i9903", "pos": "n", "morpho": "n-s---mn4-"}, "inventus1": {
        "lemma": "inuentus", "uri": "115174", "pos": "a", "morpho": "aps---mn1-"
    }, "inventus2": {"lemma": "inuentus", "uri": "i9904", "pos": "n", "morpho": "n-s---mn4-"}, "investigabilis1": {
        "lemma": "inuestigabilis", "uri": "i2667", "pos": "a", "morpho": "aps---cn3i"
    }, "investigabilis2": {"lemma": "inuestigabilis", "uri": "i2667", "pos": "a", "morpho": "aps---cn3i"},
    "invidens1": {
        "lemma": "inuidens", "uri": "115194", "pos": "a", "morpho": "aps---an3i"
    }, "invidens2": {"lemma": "inuidens", "uri": "115194", "pos": "a", "morpho": "aps---an3i"}, "invisus1": {
        "lemma": "inuisus", "uri": "i3208", "pos": "a", "morpho": "aps---mn1-"
    }, "invisus2": {"lemma": "inuisus", "uri": "i3208", "pos": "a", "morpho": "aps---mn1-"}, "invocatus1": {
        "lemma": "inuocatus", "uri": "i9915", "pos": "a", "morpho": "aps---mn1-"
    }, "invocatus2": {"lemma": "inuocatus", "uri": "i9915", "pos": "a", "morpho": "aps---mn1-"}, "invocatus3": {
        "lemma": "inuocatus", "uri": "115243", "pos": "n", "morpho": "n-s---mn4-"
    }, "Io2": {"lemma": "Io", "uri": "60367", "pos": "n", "morpho": "n-s---fn3-"}, "ion1": {
        "lemma": "ion", "uri": "i2774", "pos": "n", "morpho": "n-s---nn2g"
    }, "Ion2": {"lemma": "Ion", "uri": "i2774", "pos": "n", "morpho": "n-s---mn3-"}, "Iphis1": {
        "lemma": "Iphis", "uri": "60380", "pos": "n", "morpho": "n-s---fn3-"
    }, "Iphis2": {"lemma": "Iphis", "uri": "60380", "pos": "n", "morpho": "n-s---fn3-"}, "irrasus1": {
        "lemma": "irrasus", "uri": "i3212", "pos": "a", "morpho": "aps---mn1-"
    }, "irrasus2": {"lemma": "irrasus", "uri": "i3212", "pos": "a", "morpho": "aps---mn1-"}, "irrisus1": {
        "lemma": "irrisus", "uri": "i9908", "pos": "n", "morpho": "n-s---mn4-"
    }, "irrisus2": {"lemma": "irrisus", "uri": "i9908", "pos": "n", "morpho": "n-s---mn4-"}, "irritatus1": {
        "lemma": "irritatus", "uri": "99148", "pos": "a", "morpho": "aps---mn1-"
    }, "irritatus2": {"lemma": "irritatus", "uri": "i9909", "pos": "n", "morpho": "n-s---mn4-"}, "irritus1": {
        "lemma": "irritus", "uri": "i2888", "pos": "a", "morpho": "aps---mn1-"
    }, "irritus2": {"lemma": "irritus", "uri": "115380", "pos": "n", "morpho": "n-s---mn4-"}, "irruptus1": {
        "lemma": "irruptus", "uri": "115393", "pos": "n", "morpho": "n-s---mn4-"
    }, "irruptus2": {"lemma": "irruptus", "uri": "i3213", "pos": "a", "morpho": "aps---mn1-"}, "irruptus3": {
        "lemma": "irruptus", "uri": "i3213", "pos": "a", "morpho": "aps---mn1-"
    }, "Isaurus1": {"lemma": "Isaurus", "uri": "60391", "pos": "n", "morpho": "n-s---mn2-"}, "Isaurus2": {
        "lemma": "Isaurus", "uri": "60391", "pos": "n", "morpho": "n-s---mn2-"
    }, "Ismarus1": {"lemma": "Ismarus", "uri": "60399", "pos": "n", "morpho": "n-s---mn2-"}, "Ismarus2": {
        "lemma": "Ismarus", "uri": "60399", "pos": "n", "morpho": "n-s---mn2-"
    }, "issus1": {"lemma": "issus", "uri": "115425", "pos": "a", "morpho": "aps---mn1-"}, "istic2": {
        "lemma": "istic", "uri": "48378", "pos": "r", "morpho": "rp--------"
    }, "itero1": {"lemma": "itero", "uri": "i2966", "pos": "v", "morpho": "v1spia--1-"}, "itero2": {
        "lemma": "itero", "uri": "i7967", "pos": "r", "morpho": "rp--------"
    }, "iulis1": {"lemma": "iulis", "uri": "i3029", "pos": "n", "morpho": "n-s---fn3-"}, "Iulis2": {
        "lemma": "Iulis", "uri": "60414", "pos": "n", "morpho": "n-s---fn3-"
    }, "iulus1": {"lemma": "iulus", "uri": "i3030", "pos": "n", "morpho": "n-s---mn2-"}, "Iulus2": {
        "lemma": "Iulus", "uri": "60415", "pos": "n", "morpho": "n-s---mn2-"
    }, "jactus1": {"lemma": "iactus", "uri": "112815", "pos": "a", "morpho": "aps---mn1-"}, "jactus2": {
        "lemma": "iactus", "uri": "i9852", "pos": "n", "morpho": "n-s---mn4-"
    }, "juba1": {"lemma": "iuba", "uri": "i2977", "pos": "n", "morpho": "n-s---fn1-"}, "judicatus1": {
        "lemma": "iudicatus", "uri": "115462", "pos": "a", "morpho": "aps---mn1-"
    }, "judicatus2": {"lemma": "iudicatus", "uri": "i9912", "pos": "n", "morpho": "n-s---mn4-"}, "jugis1": {
        "lemma": "iugis", "uri": "i3011", "pos": "a", "morpho": "aps---cn3i"
    }, "jugis2": {"lemma": "iugis", "uri": "i3011", "pos": "a", "morpho": "aps---cn3i"}, "jugo1": {
        "lemma": "iugo", "uri": "i3015", "pos": "v", "morpho": "v1spia--1-"
    }, "jugo2": {"lemma": "iugo", "uri": "i3016", "pos": "v", "morpho": "v1spia--3-"}, "junctus1": {
        "lemma": "iunctus", "uri": "54817", "pos": "a", "morpho": "aps---mn1-"
    }, "junctus2": {"lemma": "iunctus", "uri": "i3065", "pos": "n", "morpho": "n-s---mn4-"}, "jus1": {
        "lemma": "ius", "uri": "i3100", "pos": "n", "morpho": "n-s---nn3-"
    }, "jus2": {"lemma": "ius", "uri": "i3100", "pos": "n", "morpho": "n-s---nn3-"}, "jussus1": {
        "lemma": "iussus", "uri": "115530", "pos": "a", "morpho": "aps---mn1-"
    }, "jussus2": {"lemma": "iussus", "uri": "i9913", "pos": "n", "morpho": "n-s---mn4-"}, "juvenalis1": {
        "lemma": "iuuenalis", "uri": "i3093", "pos": "a", "morpho": "aps---cn3i"
    }, "juvencus1": {"lemma": "iuuencus", "uri": "i3094", "pos": "a", "morpho": "aps---mn1-"}, "labeo1": {
        "lemma": "labeo", "uri": "l0012", "pos": "n", "morpho": "n-s---mn3-"
    }, "Labeo2": {"lemma": "Labeo", "uri": "60447", "pos": "n", "morpho": "n-s---mn3-"}, "labes1": {
        "lemma": "labes", "uri": "l0014", "pos": "n", "morpho": "n-s---fn3i"
    }, "labes2": {"lemma": "labes", "uri": "l0014", "pos": "n", "morpho": "n-s---fn3i"}, "labor1": {
        "lemma": "labor", "uri": "l0025", "pos": "v", "morpho": "v1spid--3-"
    }, "labor2": {"lemma": "labor", "uri": "24521", "pos": "n", "morpho": "n-s---mn3-"}, "laboratus1": {
        "lemma": "laboratus", "uri": "115579", "pos": "n", "morpho": "n-s---mn4-"
    }, "laboratus2": {"lemma": "laboratus", "uri": "115578", "pos": "a", "morpho": "aps---mn1-"}, "lacerna1": {
        "lemma": "lacerna", "uri": "l0051", "pos": "n", "morpho": "n-s---fn1-"
    }, "Lacerna2": {"lemma": "Lacerna", "uri": "60453", "pos": "n", "morpho": "n-s---fn1-"}, "lacertus1": {
        "lemma": "lacertus", "uri": "l0057", "pos": "n", "morpho": "n-s---mn2-"
    }, "lacertus2": {"lemma": "lacertus", "uri": "l0057", "pos": "n", "morpho": "n-s---mn2-"}, "lactans1": {
        "lemma": "lactans", "uri": "l0077", "pos": "a", "morpho": "aps---an3i"
    }, "lacto1": {"lemma": "lacto", "uri": "l0502", "pos": "v", "morpho": "v1spia--1-"}, "lacto2": {
        "lemma": "lacto", "uri": "l0502", "pos": "v", "morpho": "v1spia--1-"
    }, "laetus1": {"lemma": "laetus", "uri": "l0130", "pos": "a", "morpho": "aps---mn1-"}, "laetus2": {
        "lemma": "laetus", "uri": "l0130", "pos": "n", "morpho": "n-s---mn2-"
    }, "lamia1": {"lemma": "lamia", "uri": "l0168", "pos": "n", "morpho": "n-s---fn1-"}, "Lamia2": {
        "lemma": "Lamia", "uri": "60477", "pos": "n", "morpho": "n-s---fn1-"
    }, "Lamia3": {"lemma": "Lamia", "uri": "60477", "pos": "n", "morpho": "n-s---fn1-"}, "lanarius1": {
        "lemma": "lanarius", "uri": "l0186", "pos": "a", "morpho": "aps---mn1-"
    }, "Lanarius2": {"lemma": "Lanarius", "uri": "60483", "pos": "n", "morpho": "n-s---mn2-"}, "lanatus1": {
        "lemma": "lanatus", "uri": "l0188", "pos": "a", "morpho": "aps---mn1-"
    }, "Lanatus2": {"lemma": "Lanatus", "uri": "60484", "pos": "n", "morpho": "n-s---mn2-"}, "lanio1": {
        "lemma": "lanio", "uri": "l0228", "pos": "v", "morpho": "v1spia--1-"
    }, "lanio2": {"lemma": "lanio", "uri": "l0229", "pos": "n", "morpho": "n-s---mn3-"}, "lapsus1": {
        "lemma": "lapsus", "uri": "115819", "pos": "a", "morpho": "aps---mn1-"
    }, "lapsus2": {"lemma": "lapsus", "uri": "l0003", "pos": "n", "morpho": "n-s---mn4-"}, "laqueatus1": {
        "lemma": "laqueatus", "uri": "46157", "pos": "a", "morpho": "aps---mn1-"
    }, "laqueatus2": {"lemma": "laqueatus", "uri": "46157", "pos": "a", "morpho": "aps---mn1-"}, "laqueo1": {
        "lemma": "laqueo", "uri": "l0284", "pos": "v", "morpho": "v1spia--1-"
    }, "laqueo2": {"lemma": "laqueo", "uri": "l0284", "pos": "v", "morpho": "v1spia--1-"}, "largitor1": {
        "lemma": "largitor", "uri": None, "pos": "v", "morpho": "v1spid--1-"
    }, "largitor2": {"lemma": "largitor", "uri": "l0298", "pos": "n", "morpho": "n-s---mn3-"}, "largitus1": {
        "lemma": "largitus", "uri": "l0300", "pos": "r", "morpho": "rp--------"
    }, "largitus2": {"lemma": "largitus", "uri": "115838", "pos": "a", "morpho": "aps---mn1-"}, "largus1": {
        "lemma": "largus", "uri": "l0302", "pos": "a", "morpho": "aps---mn1-"
    }, "Largus2": {"lemma": "Largus", "uri": "60499", "pos": "n", "morpho": "n-s---mn2-"}, "laterarius1": {
        "lemma": "laterarius", "uri": "l0353", "pos": "a", "morpho": "aps---mn1-"
    }, "laterarius2": {"lemma": "laterarius", "uri": "l0353", "pos": "a", "morpho": "aps---mn1-"}, "laterensis1": {
        "lemma": "laterensis", "uri": "l0349", "pos": "a", "morpho": "aps---cn3i"
    }, "Laterensis2": {"lemma": "Laterensis", "uri": "60506", "pos": "n", "morpho": "n-s---fn3-"}, "latesco1": {
        "lemma": "latesco", "uri": "l1297", "pos": "v", "morpho": "v1spia--3-"
    }, "latesco2": {"lemma": "latesco", "uri": "l1297", "pos": "v", "morpho": "v1spia--3-"}, "Latinus1": {
        "lemma": "Latinus", "uri": "24590", "pos": "a", "morpho": "aps---mn1-"
    }, "Latinus2": {"lemma": "Latinus", "uri": "60508", "pos": "n", "morpho": "n-s---mn2-"}, "latro1": {
        "lemma": "latro", "uri": "l0383", "pos": "v", "morpho": "v1spia--1-"
    }, "latro2": {"lemma": "latro", "uri": "l0384", "pos": "n", "morpho": "n-s---mn3-"}, "latus1": {
        "lemma": "latus", "uri": "l0392", "pos": "a", "morpho": "aps---mn1-"
    }, "latus2": {"lemma": "latus", "uri": "l0393", "pos": "n", "morpho": "n-s---nn3-"}, "latus3": {
        "lemma": "latus", "uri": "l0392", "pos": "a", "morpho": "aps---mn1-"
    }, "laus1": {"lemma": "laus", "uri": "l0432", "pos": "n", "morpho": "n-s---fn3-"}, "Laus2": {
        "lemma": "Laus", "uri": "60516", "pos": "n", "morpho": "n-s---mn2-"
    }, "leaena1": {"lemma": "leaena", "uri": "l0449", "pos": "n", "morpho": "n-s---fn1-"}, "Leaena2": {
        "lemma": "Leaena", "uri": "60520", "pos": "n", "morpho": "n-s---fn1-"
    }, "lectus1": {"lemma": "lectus", "uri": "24624", "pos": "a", "morpho": "aps---mn1-"}, "lectus2": {
        "lemma": "lectus", "uri": "l0471", "pos": "n", "morpho": "n-s---mn2-"
    }, "lectus3": {"lemma": "lectus", "uri": "l0488", "pos": "n", "morpho": "n-s---mn4-"}, "Leda1": {
        "lemma": "Leda", "uri": "60526", "pos": "n", "morpho": "n-s---fn1-"
    }, "leda2": {"lemma": "leda", "uri": "l0473", "pos": "n", "morpho": "n-s---fn1-"}, "lego1": {
        "lemma": "lego", "uri": "l0495", "pos": "v", "morpho": "v1spia--1-"
    }, "lego2": {"lemma": "lego", "uri": "l0496", "pos": "v", "morpho": "v1spia--3-"}, "lenis1": {
        "lemma": "lenis", "uri": "l0517", "pos": "a", "morpho": "aps---cn3i"
    }, "lenis2": {"lemma": "lenis", "uri": "116022", "pos": "n", "morpho": "n-s---mn3i"}, "leno1": {
        "lemma": "leno", "uri": "l0521", "pos": "v", "morpho": "v1spia--1-"
    }, "leno2": {"lemma": "leno", "uri": "l0520", "pos": "n", "morpho": "n-s---mn3-"}, "lento1": {
        "lemma": "lento", "uri": "l0541", "pos": "v", "morpho": "v1spia--1-"
    }, "lentulus1": {"lemma": "lentulus", "uri": "l0544", "pos": "a", "morpho": "aps---mn1-"}, "Lentulus2": {
        "lemma": "Lentulus", "uri": "60533", "pos": "n", "morpho": "n-s---mn2-"
    }, "lenunculus1": {"lemma": "lenunculus", "uri": "l9919", "pos": "n", "morpho": "n-s---mn2-"}, "lenunculus2": {
        "lemma": "lenunculus", "uri": "l9919", "pos": "n", "morpho": "n-s---mn2-"
    }, "leo1": {"lemma": "leo", "uri": "l0550", "pos": "v", "morpho": "v1spia--2-"}, "leo2": {
        "lemma": "leo", "uri": "l0549", "pos": "n", "morpho": "n-s---mn3-"
    }, "leoninus1": {"lemma": "leoninus", "uri": "l0551", "pos": "a", "morpho": "aps---mn1-"}, "Leoninus2": {
        "lemma": "Leoninus", "uri": "60538", "pos": "a", "morpho": "aps---mn1-"
    }, "lepidus1": {"lemma": "lepidus", "uri": "l0565", "pos": "a", "morpho": "aps---mn1-"}, "Lepidus2": {
        "lemma": "Lepidus", "uri": "60541", "pos": "n", "morpho": "n-s---mn2-"
    }, "levatus1": {"lemma": "leuatus", "uri": "116094", "pos": "a", "morpho": "aps---mn1-"}, "levatus2": {
        "lemma": "leuatus", "uri": "116094", "pos": "a", "morpho": "aps---mn1-"
    }, "levitas1": {"lemma": "leuitas", "uri": "l0643", "pos": "n", "morpho": "n-s---fn3-"}, "levitas2": {
        "lemma": "leuitas", "uri": "l0643", "pos": "n", "morpho": "n-s---fn3-"
    }, "Libanus1": {"lemma": "Libanus", "uri": "60566", "pos": "n", "morpho": "n-s---mn2-"}, "Libanus2": {
        "lemma": "Libanus", "uri": "60566", "pos": "n", "morpho": "n-s---mn2-"
    }, "liber1": {"lemma": "liber", "uri": "l0675", "pos": "a", "morpho": "aps---mn1r"}, "liber2": {
        "lemma": "liber", "uri": "l0676", "pos": "n", "morpho": "n-s---mn2r"
    }, "liber4": {"lemma": "liber", "uri": "l0676", "pos": "n", "morpho": "n-s---mn2r"}, "liberalis1": {
        "lemma": "liberalis", "uri": "l0677", "pos": "a", "morpho": "aps---cn3i"
    }, "Liberalis2": {"lemma": "Liberalis", "uri": "60567", "pos": "a", "morpho": "aps---fn3i"}, "libertinus1": {
        "lemma": "libertinus", "uri": "l0689", "pos": "a", "morpho": "aps---mn1-"
    }, "libertinus2": {"lemma": "libertinus", "uri": "l0689", "pos": "n", "morpho": "n-s---mn2-"}, "Libo2": {
        "lemma": "Libo", "uri": "60570", "pos": "n", "morpho": "n-s---mn3-"
    }, "licinus1": {"lemma": "licinus", "uri": "l0724", "pos": "a", "morpho": "aps---mn1-"}, "Licinus2": {
        "lemma": "Licinus", "uri": "60578", "pos": "n", "morpho": "n-s---mn2-"
    }, "ligo1": {"lemma": "ligo", "uri": "l0753", "pos": "v", "morpho": "v1spia--1-"}, "ligo2": {
        "lemma": "ligo", "uri": "l0754", "pos": "n", "morpho": "n-s---mn3-"
    }, "ligurius1": {"lemma": "ligurius", "uri": "31611", "pos": "n", "morpho": "n-s---mn2-"}, "ligurius2": {
        "lemma": "ligurius", "uri": "31611", "pos": "n", "morpho": "n-s---mn2-"
    }, "limo1": {"lemma": "limo", "uri": "116263", "pos": "r", "morpho": "rp--------"}, "limo2": {
        "lemma": "limo", "uri": "l0855", "pos": "v", "morpho": "v1spia--1-"
    }, "limo3": {"lemma": "limo", "uri": "l0855", "pos": "v", "morpho": "v1spia--1-"}, "limus1": {
        "lemma": "limus", "uri": "l0805", "pos": "a", "morpho": "aps---mn1-"
    }, "linctus1": {"lemma": "linctus", "uri": "116282", "pos": "a", "morpho": "aps---mn1-"}, "linctus2": {
        "lemma": "linctus", "uri": "l9896", "pos": "n", "morpho": "n-s---mn4-"
    }, "linitus1": {"lemma": "linitus", "uri": "116311", "pos": "a", "morpho": "aps---mn1-"}, "linitus2": {
        "lemma": "linitus", "uri": "l9897", "pos": "n", "morpho": "n-s---mn4-"
    }, "Lipara1": {"lemma": "Lipara", "uri": "60592", "pos": "a", "morpho": "aps---fn1-"}, "lipara2": {
        "lemma": "lipara", "uri": "l0865", "pos": "n", "morpho": "n-s---fn1-"
    }, "liquens1": {"lemma": "liquens", "uri": "116350", "pos": "a", "morpho": "aps---an3i"}, "liquens2": {
        "lemma": "liquens", "uri": "116350", "pos": "a", "morpho": "aps---an3i"
    }, "liquor1": {"lemma": "liquor", "uri": "l0888", "pos": "v", "morpho": "v1spid--3-"}, "liquor2": {
        "lemma": "liquor", "uri": "l0889", "pos": "n", "morpho": "n-s---mn3-"
    }, "litus1": {"lemma": "litus", "uri": "116400", "pos": "a", "morpho": "aps---mn1-"}, "litus2": {
        "lemma": "litus", "uri": "l9899", "pos": "n", "morpho": "n-s---mn4-"
    }, "litus3": {"lemma": "litus", "uri": "l0938", "pos": "n", "morpho": "n-s---nn3-"}, "locusta1": {
        "lemma": "locusta", "uri": "l0977", "pos": "n", "morpho": "n-s---fn1-"
    }, "Locusta2": {"lemma": "Locusta", "uri": "60603", "pos": "n", "morpho": "n-s---fn1-"}, "Locusta3": {
        "lemma": "Locusta", "uri": "60603", "pos": "n", "morpho": "n-s---fn1-"
    }, "locutus1": {"lemma": "locutus", "uri": "116449", "pos": "a", "morpho": "aps---mn1-"}, "locutus2": {
        "lemma": "locutus", "uri": "l9900", "pos": "n", "morpho": "n-s---mn4-"
    }, "longinquo1": {"lemma": "longinquo", "uri": "30599", "pos": "r", "morpho": "rp--------"}, "longinquo2": {
        "lemma": "longinquo", "uri": "l1017", "pos": "v", "morpho": "v1spia--1-"
    }, "lora1": {"lemma": "lora", "uri": "l1043", "pos": "n", "morpho": "n-s---fn1-"}, "lotus1": {
        "lemma": "lotus", "uri": "44462", "pos": "a", "morpho": "aps---mn1-"
    }, "lotus3": {"lemma": "lotus", "uri": "116525", "pos": "n", "morpho": "n-s---mn4-"}, "Luca1": {
        "lemma": "Luca", "uri": "l1068", "pos": "n", "morpho": "n-s---fn1-"
    }, "Luca2": {"lemma": "Luca", "uri": "l1068", "pos": "n", "morpho": "n-s---fn1-"}, "lucinus1": {
        "lemma": "lucinus", "uri": "l1095", "pos": "a", "morpho": "aps---mn1-"
    }, "lucinus2": {"lemma": "lucinus", "uri": "l1095", "pos": "a", "morpho": "aps---mn1-"}, "lucius2": {
        "lemma": "lucius", "uri": "l1100", "pos": "n", "morpho": "n-s---mn2-"
    }, "lucus1": {"lemma": "lucus", "uri": "l1140", "pos": "n", "morpho": "n-s---mn2-"}, "lucus3": {
        "lemma": "lucus", "uri": "116606", "pos": "n", "morpho": "n-s---mn4-"
    }, "ludius1": {"lemma": "ludius", "uri": "l1156", "pos": "n", "morpho": "n-s---mn2-"}, "lues1": {
        "lemma": "lues", "uri": "l1160", "pos": "n", "morpho": "n-s---fn3i"
    }, "lues2": {"lemma": "lues", "uri": "l1160", "pos": "n", "morpho": "n-s---fn3i"}, "luna1": {
        "lemma": "luna", "uri": "l1180", "pos": "n", "morpho": "n-s---fn1-"
    }, "Luna2": {"lemma": "Luna", "uri": "60623", "pos": "n", "morpho": "n-s---fn1-"}, "luo1": {
        "lemma": "luo", "uri": "l1185", "pos": "v", "morpho": "v1spia--3-"
    }, "luo2": {"lemma": "luo", "uri": "l1185", "pos": "v", "morpho": "v1spia--3-"}, "lupinus1": {
        "lemma": "lupinus", "uri": "l1197", "pos": "a", "morpho": "aps---mn1-"
    }, "lupinus2": {"lemma": "lupinus", "uri": "l1197", "pos": "n", "morpho": "n-s---mn2-"}, "lupus1": {
        "lemma": "lupus", "uri": "l1186", "pos": "n", "morpho": "n-s---mn2-"
    }, "lurco1": {"lemma": "lurco", "uri": "42017", "pos": "v", "morpho": "v1spia--1-"}, "lurco2": {
        "lemma": "lurco", "uri": "42779", "pos": "n", "morpho": "n-s---mn3-"
    }, "luscinius1": {"lemma": "luscinius", "uri": "l1209", "pos": "n", "morpho": "n-s---mn2-"}, "luscinius2": {
        "lemma": "luscinius", "uri": "l1212", "pos": "a", "morpho": "aps---mn1-"
    }, "luscinus1": {"lemma": "luscinus", "uri": "l1212", "pos": "a", "morpho": "aps---mn1-"}, "luscinus3": {
        "lemma": "luscinus", "uri": "116668", "pos": "n", "morpho": "n-s---mn2-"
    }, "lustramentum1": {"lemma": "lustramentum", "uri": "l1226", "pos": "n", "morpho": "n-s---nn2-"},
    "lustramentum2": {
        "lemma": "lustramentum", "uri": "l1226", "pos": "n", "morpho": "n-s---nn2-"
    }, "lustro1": {"lemma": "lustro", "uri": "l1232", "pos": "v", "morpho": "v1spia--1-"}, "lustro2": {
        "lemma": "lustro", "uri": "l1233", "pos": "n", "morpho": "n-s---mn3-"
    }, "lustrum1": {"lemma": "lustrum", "uri": "l8222", "pos": "n", "morpho": "n-s---nn2-"}, "lustrum2": {
        "lemma": "lustrum", "uri": "l8222", "pos": "n", "morpho": "n-s---nn2-"
    }, "lusus1": {"lemma": "lusus", "uri": "116685", "pos": "a", "morpho": "aps---mn1-"}, "lusus2": {
        "lemma": "lusus", "uri": "l9903", "pos": "n", "morpho": "n-s---mn4-"
    }, "luto1": {"lemma": "luto", "uri": "l1244", "pos": "v", "morpho": "v1spia--1-"}, "luto2": {
        "lemma": "luto", "uri": "l1244", "pos": "v", "morpho": "v1spia--1-"
    }, "luxus1": {"lemma": "luxus", "uri": "l1257", "pos": "a", "morpho": "aps---mn1-"}, "luxus2": {
        "lemma": "luxus", "uri": "l1258", "pos": "n", "morpho": "n-s---mn4-"
    }, "luxus3": {"lemma": "luxus", "uri": "l1258", "pos": "n", "morpho": "n-s---mn4-"}, "Lycaon1": {
        "lemma": "Lycaon", "uri": "60631", "pos": "n", "morpho": "n-s---mn3-"
    }, "lycaon2": {"lemma": "lycaon", "uri": "l1259", "pos": "n", "morpho": "n-s---mn3-"}, "Lycium1": {
        "lemma": "Lycium", "uri": "60636", "pos": "n", "morpho": "n-s---nn2-"
    }, "Lycium2": {"lemma": "Lycium", "uri": "60636", "pos": "n", "morpho": "n-s---nn2-"}, "lygos1": {
        "lemma": "lygos", "uri": "l1275", "pos": "n", "morpho": "n-s---fn2g"
    }, "Lygos2": {"lemma": "Lygos", "uri": "60651", "pos": "n", "morpho": "n-s---mn2-"}, "lymphatus1": {
        "lemma": "lymphatus", "uri": "24827", "pos": "a", "morpho": "aps---mn1-"
    }, "lymphatus2": {"lemma": "lymphatus", "uri": "l9904", "pos": "n", "morpho": "n-s---mn4-"}, "lysimachia1": {
        "lemma": "lysimachia", "uri": "l1289", "pos": "n", "morpho": "n-s---fn1-"
    }, "Lysimachia2": {"lemma": "Lysimachia", "uri": "60660", "pos": "n", "morpho": "n-s---fn1-"}, "lysis1": {
        "lemma": "lysis", "uri": "l1292", "pos": "n", "morpho": "n-s---fn3i"
    }, "Lysis2": {"lemma": "Lysis", "uri": "60664", "pos": "n", "morpho": "n-s---fn3-"}, "Lysis3": {
        "lemma": "Lysis", "uri": "60664", "pos": "n", "morpho": "n-s---fn3-"
    }, "Macedo1": {"lemma": "Macedo", "uri": "24829", "pos": "n", "morpho": "n-s---mn3-"}, "Macedo2": {
        "lemma": "Macedo", "uri": "24829", "pos": "n", "morpho": "n-s---mn3-"
    }, "macellus1": {"lemma": "macellus", "uri": "m9804", "pos": "a", "morpho": "aps---mn1-"}, "macellus2": {
        "lemma": "macellus", "uri": "m0008", "pos": "n", "morpho": "n-s---mn2-"
    }, "macer1": {"lemma": "macer", "uri": "m0010", "pos": "a", "morpho": "aps---mn1r"}, "Macer2": {
        "lemma": "Macer", "uri": "60673", "pos": "n", "morpho": "n-s---mn3-"
    }, "maceries1": {"lemma": "maceries", "uri": "m0092", "pos": "n", "morpho": "n-s---fn5-"}, "maceries2": {
        "lemma": "maceries", "uri": "m0092", "pos": "n", "morpho": "n-s---fn5-"
    }, "machaera1": {"lemma": "machaera", "uri": "m0019", "pos": "n", "morpho": "n-s---fn1-"}, "Machaera2": {
        "lemma": "Machaera", "uri": "60677", "pos": "n", "morpho": "n-s---fn1-"
    }, "mactus1": {"lemma": "mactus", "uri": "m0943", "pos": "a", "morpho": "aps---mn1-"}, "mactus2": {
        "lemma": "mactus", "uri": "m0943", "pos": "a", "morpho": "aps---mn1-"
    }, "macula1": {"lemma": "macula", "uri": "m0055", "pos": "n", "morpho": "n-s---fn1-"}, "Macula2": {
        "lemma": "Macula", "uri": "60685", "pos": "n", "morpho": "n-s---fn1-"
    }, "Maecius1": {"lemma": "Maecius", "uri": "60691", "pos": "n", "morpho": "n-s---mn2-"}, "Maecius2": {
        "lemma": "Maecius", "uri": "60691", "pos": "n", "morpho": "n-s---mn2-"
    }, "magis1": {"lemma": "magis", "uri": "m0095", "pos": "r", "morpho": "rp--------"}, "magis2": {
        "lemma": "magis", "uri": "m0096", "pos": "n", "morpho": "n-s---fn3-"
    }, "magnes1": {"lemma": "magnes", "uri": "m0118", "pos": "n", "morpho": "n-s---mn3-"}, "magnus1": {
        "lemma": "magnus", "uri": "m0132", "pos": "a", "morpho": "aps---mn1-"
    }, "magus1": {"lemma": "magus", "uri": "m0134", "pos": "n", "morpho": "n-s---mn2-"}, "magus2": {
        "lemma": "magus", "uri": "m0134", "pos": "a", "morpho": "aps---mn1-"
    }, "maia1": {"lemma": "maia", "uri": "116859", "pos": "n", "morpho": "n-s---fn1-"}, "Maia2": {
        "lemma": "Maia", "uri": "60708", "pos": "n", "morpho": "n-s---fn1-"
    }, "malus1": {"lemma": "malus", "uri": "m0216", "pos": "a", "morpho": "aps---mn1-"}, "malus2": {
        "lemma": "malus", "uri": "m0219", "pos": "n", "morpho": "n-s---fn2-"
    }, "malus3": {"lemma": "malus", "uri": "m0218", "pos": "n", "morpho": "n-s---mn2-"}, "mammula1": {
        "lemma": "mammula", "uri": "m0235", "pos": "n", "morpho": "n-s---fn1-"
    }, "Mammula2": {"lemma": "Mammula", "uri": "60718", "pos": "n", "morpho": "n-s---fn1-"}, "Mana1": {
        "lemma": "Mana", "uri": "60720", "pos": "n", "morpho": "n-s---fn1-"
    }, "manalis1": {"lemma": "manalis", "uri": "m0239", "pos": "a", "morpho": "aps---cn3i"}, "mandatus1": {
        "lemma": "mandatus", "uri": "116966", "pos": "a", "morpho": "aps---mn1-"
    }, "mandatus2": {"lemma": "mandatus", "uri": "m9996", "pos": "n", "morpho": "n-s---mn4-"}, "mando1": {
        "lemma": "mando", "uri": "m0260", "pos": "v", "morpho": "v1spia--1-"
    }, "mando2": {"lemma": "mando", "uri": "m0261", "pos": "v", "morpho": "v1spia--3-"}, "mando3": {
        "lemma": "mando", "uri": "m0262", "pos": "n", "morpho": "n-s---mn3-"
    }, "manduco1": {"lemma": "manduco", "uri": "m0269", "pos": "v", "morpho": "v1spia--1-"}, "manduco2": {
        "lemma": "manduco", "uri": "m0270", "pos": "n", "morpho": "n-s---mn3-"
    }, "mania2": {"lemma": "mania", "uri": "m0280", "pos": "n", "morpho": "n-s---fn1-"}, "manifesto1": {
        "lemma": "manifesto", "uri": "24906", "pos": "r", "morpho": "rp--------"
    }, "manifesto2": {"lemma": "manifesto", "uri": "m0291", "pos": "v", "morpho": "v1spia--1-"}, "manto1": {
        "lemma": "manto", "uri": "m0334", "pos": "v", "morpho": "v1spia--1-"
    }, "Manto2": {"lemma": "Manto", "uri": "60730", "pos": "n", "morpho": "n-s---fn3-"}, "manus1": {
        "lemma": "manus", "uri": "m0362", "pos": "n", "morpho": "n-s---fn4-"
    }, "manus2": {"lemma": "manus", "uri": "m0362", "pos": "n", "morpho": "n-s---fn4-"}, "Marathus1": {
        "lemma": "Marathus", "uri": "60733", "pos": "n", "morpho": "n-s---mn2-"
    }, "Marathus2": {"lemma": "Marathus", "uri": "60733", "pos": "n", "morpho": "n-s---mn2-"}, "marculus1": {
        "lemma": "marculus", "uri": "m0376", "pos": "n", "morpho": "n-s---mn2-"
    }, "marcus1": {"lemma": "marcus", "uri": "m0944", "pos": "n", "morpho": "n-s---mn2-"}, "Maria1": {
        "lemma": "Maria", "uri": "60744", "pos": "n", "morpho": "n-s---fn1-"
    }, "Maria2": {"lemma": "Maria", "uri": "60744", "pos": "n", "morpho": "n-s---fn1-"}, "maritus1": {
        "lemma": "maritus", "uri": "m0114", "pos": "a", "morpho": "aps---mn1-"
    }, "maritus2": {"lemma": "maritus", "uri": "m0126", "pos": "n", "morpho": "n-s---mn2-"}, "Maro1": {
        "lemma": "Maro", "uri": "60752", "pos": "n", "morpho": "n-s---mn3-"
    }, "Maro2": {"lemma": "Maro", "uri": "60752", "pos": "n", "morpho": "n-s---mn3-"}, "Maro3": {
        "lemma": "Maro", "uri": "60752", "pos": "n", "morpho": "n-s---mn3-"
    }, "marrubium1": {"lemma": "marrubium", "uri": "m0410", "pos": "n", "morpho": "n-s---nn2-"}, "Marrubium2": {
        "lemma": "Marrubium", "uri": "60754", "pos": "n", "morpho": "n-s---nn2-"
    }, "Marsus1": {"lemma": "Marsus", "uri": "60758", "pos": "n", "morpho": "n-s---mn2-"}, "Marsus2": {
        "lemma": "Marsus", "uri": "60758", "pos": "n", "morpho": "n-s---mn2-"
    }, "Marsyas1": {"lemma": "Marsyas", "uri": "60759", "pos": "n", "morpho": "n-s---mn1-"}, "Marsyas2": {
        "lemma": "Marsyas", "uri": "60759", "pos": "n", "morpho": "n-s---mn1-"
    }, "Martialis1": {"lemma": "Martialis", "uri": "60760", "pos": "n", "morpho": "n-s---fn3-"}, "Martialis2": {
        "lemma": "Martialis", "uri": "60760", "pos": "n", "morpho": "n-s---fn3-"
    }, "massa1": {"lemma": "massa", "uri": "m0425", "pos": "n", "morpho": "n-s---fn1-"}, "Massa2": {
        "lemma": "Massa", "uri": "60769", "pos": "n", "morpho": "n-s---fn1-"
    }, "masso1": {"lemma": "masso", "uri": "m0428", "pos": "v", "morpho": "v1spia--1-"}, "maternus1": {
        "lemma": "maternus", "uri": "m0458", "pos": "a", "morpho": "aps---mn1-"
    }, "matrona1": {"lemma": "matrona", "uri": "m0475", "pos": "n", "morpho": "n-s---fn1-"}, "medialis1": {
        "lemma": "medialis", "uri": "m0550", "pos": "a", "morpho": "aps---cn3i"
    }, "medialis2": {"lemma": "medialis", "uri": "m0550", "pos": "a", "morpho": "aps---cn3i"}, "Medica1": {
        "lemma": "Medica", "uri": "m0639", "pos": "n", "morpho": "n-s---fn1-"
    }, "medicatus1": {"lemma": "medicatus", "uri": "32283", "pos": "a", "morpho": "aps---mn1-"}, "medicatus2": {
        "lemma": "medicatus", "uri": "m0536", "pos": "n", "morpho": "n-s---mn4-"
    }, "medicus1": {"lemma": "medicus", "uri": "m0549", "pos": "a", "morpho": "aps---mn1-"}, "Medicus2": {
        "lemma": "Medicus", "uri": "m0643", "pos": "a", "morpho": "aps---mn1-"
    }, "medion1": {"lemma": "medion", "uri": "m0560", "pos": "n", "morpho": "n-s---nn2g"}, "Medion2": {
        "lemma": "Medion", "uri": "60792", "pos": "n", "morpho": "n-s---nn3-"
    }, "meditatus1": {"lemma": "meditatus", "uri": "117232", "pos": "a", "morpho": "aps---mn1-"}, "meditatus2": {
        "lemma": "meditatus", "uri": "m9999", "pos": "n", "morpho": "n-s---mn4-"
    }, "Medus1": {"lemma": "Medus", "uri": "60796", "pos": "n", "morpho": "n-s---mn2-"}, "Medus2": {
        "lemma": "Medus", "uri": "60796", "pos": "n", "morpho": "n-s---mn2-"
    }, "Medus3": {"lemma": "Medus", "uri": "60796", "pos": "n", "morpho": "n-s---mn2-"}, "Megara1": {
        "lemma": "Megara", "uri": "60805", "pos": "n", "morpho": "n-s---fn1-"
    }, "Megara2": {"lemma": "Megara", "uri": "60805", "pos": "n", "morpho": "n-s---fn1-"}, "Megara3": {
        "lemma": "Megara", "uri": "60805", "pos": "n", "morpho": "n-s---fn1-"
    }, "Megareus1": {"lemma": "Megareus", "uri": "60807", "pos": "n", "morpho": "n-s---mn2-"}, "Megareus2": {
        "lemma": "Megareus", "uri": "60807", "pos": "n", "morpho": "n-s---mn2-"
    }, "meles1": {"lemma": "meles", "uri": "m0611", "pos": "n", "morpho": "n-s---fn3i"}, "Meles2": {
        "lemma": "Meles", "uri": "60824", "pos": "n", "morpho": "n-p---mn3-"
    }, "Meles3": {"lemma": "Meles", "uri": "60824", "pos": "n", "morpho": "n-p---mn3-"}, "melicus1": {
        "lemma": "melicus", "uri": "m0620", "pos": "a", "morpho": "aps---mn1-"
    }, "melina1": {"lemma": "melina", "uri": "117285", "pos": "n", "morpho": "n-s---fn1-"}, "melina2": {
        "lemma": "melina", "uri": "117285", "pos": "n", "morpho": "n-s---fn1-"
    }, "melinum1": {"lemma": "melinum", "uri": "m0624", "pos": "n", "morpho": "n-s---nn2-"}, "melinus1": {
        "lemma": "melinus", "uri": "m0624", "pos": "a", "morpho": "aps---mn1-"
    }, "melinus2": {"lemma": "melinus", "uri": "m0624", "pos": "a", "morpho": "aps---mn1-"}, "melinus3": {
        "lemma": "melinus", "uri": "m0624", "pos": "a", "morpho": "aps---mn1-"
    }, "Melinus4": {"lemma": "Melinus", "uri": "60829", "pos": "a", "morpho": "aps---mn1-"}, "melitinus1": {
        "lemma": "melitinus", "uri": "m0632", "pos": "a", "morpho": "aps---mn1-"
    }, "Melius2": {"lemma": "Melius", "uri": "60834", "pos": "a", "morpho": "aps---mn1-"}, "mella1": {
        "lemma": "mella", "uri": "m0642", "pos": "n", "morpho": "n-s---fn1-"
    }, "Mella2": {"lemma": "Mella", "uri": "60835", "pos": "n", "morpho": "n-s---fn1-"}, "Mella3": {
        "lemma": "Mella", "uri": "60835", "pos": "n", "morpho": "n-s---fn1-"
    }, "melo2": {"lemma": "melo", "uri": "m0664", "pos": "n", "morpho": "n-s---mn3-"}, "melos1": {
        "lemma": "melos", "uri": "m0673", "pos": "n", "morpho": "n-s---nn2-"
    }, "Melos2": {"lemma": "Melos", "uri": "60838", "pos": "n", "morpho": "n-s---mn2-"}, "memor1": {
        "lemma": "memor", "uri": "99398", "pos": "a", "morpho": "aps---an3-"
    }, "memoratus1": {"lemma": "memoratus", "uri": "47868", "pos": "a", "morpho": "aps---mn1-"}, "memoratus2": {
        "lemma": "memoratus", "uri": "m9791", "pos": "n", "morpho": "n-s---mn4-"
    }, "mena1": {"lemma": "mena", "uri": "m0063", "pos": "n", "morpho": "n-s---fn1-"}, "menaeus2": {
        "lemma": "menaeus", "uri": "117376", "pos": "n", "morpho": "n-s---mn2-"
    }, "mensus1": {"lemma": "mensus", "uri": "117415", "pos": "a", "morpho": "aps---mn1-"}, "mensus2": {
        "lemma": "mensus", "uri": "99405", "pos": "n", "morpho": "n-s---mn4-"
    }, "mentio1": {"lemma": "mentio", "uri": "m0759", "pos": "n", "morpho": "n-s---fn3-"}, "mentio2": {
        "lemma": "mentio", "uri": "117420", "pos": "v", "morpho": "v1spia--4-"
    }, "mento1": {"lemma": "mento", "uri": "m0763", "pos": "n", "morpho": "n-s---mn3-"}, "mentum1": {
        "lemma": "mentum", "uri": "m0945", "pos": "n", "morpho": "n-s---nn2-"
    }, "mentum2": {"lemma": "mentum", "uri": "m0945", "pos": "n", "morpho": "n-s---nn2-"}, "merces1": {
        "lemma": "merces", "uri": "m0785", "pos": "n", "morpho": "n-s---fn3-"
    }, "merces2": {"lemma": "merces", "uri": "m0785", "pos": "n", "morpho": "n-s---fn3-"}, "merenda1": {
        "lemma": "merenda", "uri": "m9984", "pos": "n", "morpho": "n-s---fn1-"
    }, "Merenda2": {"lemma": "Merenda", "uri": "60867", "pos": "n", "morpho": "n-s---fn1-"}, "mergulus1": {
        "lemma": "mergulus", "uri": "m0804", "pos": "n", "morpho": "n-s---mn2-"
    }, "mergulus2": {"lemma": "mergulus", "uri": "m0804", "pos": "n", "morpho": "n-s---mn2-"}, "merito1": {
        "lemma": "merito", "uri": "m0819", "pos": "r", "morpho": "rp--------"
    }, "merito2": {"lemma": "merito", "uri": "m0817", "pos": "v", "morpho": "v1spia--1-"}, "Merops1": {
        "lemma": "Merops", "uri": "60873", "pos": "n", "morpho": "n-s---mn3-"
    }, "merops2": {"lemma": "merops", "uri": "m0823", "pos": "n", "morpho": "n-s---mn3-"}, "merula1": {
        "lemma": "merula", "uri": "m0828", "pos": "n", "morpho": "n-s---fn1-"
    }, "Merula2": {"lemma": "Merula", "uri": "60874", "pos": "n", "morpho": "n-s---fn1-"}, "Merula3": {
        "lemma": "Merula", "uri": "60874", "pos": "n", "morpho": "n-s---fn1-"
    }, "meto2": {"lemma": "meto", "uri": "m0897", "pos": "v", "morpho": "v1spia--3-"}, "metropolis1": {
        "lemma": "metropolis", "uri": "m0911", "pos": "n", "morpho": "n-s---fn3i"
    }, "Metropolis2": {"lemma": "Metropolis", "uri": "60897", "pos": "n", "morpho": "n-s---fn3-"}, "metropolitanus1": {
        "lemma": "metropolitanus", "uri": "m0913", "pos": "a", "morpho": "aps---mn1-"
    }, "Metropolitanus2": {"lemma": "Metropolitanus", "uri": "60898", "pos": "a", "morpho": "aps---mn1-"}, "Miletus1": {
        "lemma": "Miletus", "uri": "60913", "pos": "n", "morpho": "n-s---mn2-"
    }, "Miletus2": {"lemma": "Miletus", "uri": "60913", "pos": "n", "morpho": "n-s---mn2-"}, "Milo1": {
        "lemma": "Milo", "uri": "60917", "pos": "n", "morpho": "n-s---mn3-"
    }, "Milo2": {"lemma": "Milo", "uri": "60917", "pos": "n", "morpho": "n-s---mn3-"}, "mina1": {
        "lemma": "mina", "uri": "m1016", "pos": "n", "morpho": "n-s---fn1-"
    }, "mina2": {"lemma": "mina", "uri": "m1016", "pos": "n", "morpho": "n-s---fn1-"}, "minio1": {
        "lemma": "minio", "uri": "m1032", "pos": "v", "morpho": "v1spia--1-"
    }, "minius1": {"lemma": "minius", "uri": "32702", "pos": "a", "morpho": "aps---mn1-"}, "minor1": {
        "lemma": "minor", "uri": "m1048", "pos": "v", "morpho": "v1spid--1-"
    }, "minor2": {"lemma": "minor", "uri": "m1048", "pos": "v", "morpho": "v1spid--1-"}, "minus2": {
        "lemma": "minus", "uri": "m1049", "pos": "a", "morpho": "aps---mn1-"
    }, "minutius2": {"lemma": "minutius", "uri": "53682", "pos": "r", "morpho": "rp--------"}, "Minyas1": {
        "lemma": "Minyas", "uri": "117689", "pos": "n", "morpho": "n-s---fn3-"
    }, "missor1": {"lemma": "missor", "uri": "m1123", "pos": "n", "morpho": "n-s---mn3-"}, "missus1": {
        "lemma": "missus", "uri": "117735", "pos": "a", "morpho": "aps---mn1-"
    }, "missus2": {"lemma": "missus", "uri": "m9994", "pos": "n", "morpho": "n-s---mn4-"}, "mistus1": {
        "lemma": "mistus", "uri": "49429", "pos": "a", "morpho": "aps---mn1-"
    }, "mistus2": {"lemma": "mistus", "uri": "117741", "pos": "n", "morpho": "n-s---mn4-"}, "mnester1": {
        "lemma": "mnester", "uri": "m1155", "pos": "n", "morpho": "n-s---mn3-"
    }, "Mnester2": {"lemma": "Mnester", "uri": "60943", "pos": "n", "morpho": "n-s---mn3-"}, "modulatus1": {
        "lemma": "modulatus", "uri": "57027", "pos": "a", "morpho": "aps---mn1-"
    }, "modulatus2": {"lemma": "modulatus", "uri": "m9796", "pos": "n", "morpho": "n-s---mn4-"}, "moenia1": {
        "lemma": "moenia", "uri": "m1725", "pos": "n", "morpho": "n-p---nn3i"
    }, "moenia2": {"lemma": "moenia", "uri": "m1725", "pos": "n", "morpho": "n-p---nn3i"}, "moera1": {
        "lemma": "moera", "uri": "m1202", "pos": "n", "morpho": "n-s---fn1-"
    }, "Moera2": {"lemma": "Moera", "uri": "60946", "pos": "n", "morpho": "n-s---fn1-"}, "Moeris1": {
        "lemma": "Moeris", "uri": "60947", "pos": "n", "morpho": "n-s---mn3-"
    }, "Moeris2": {"lemma": "Moeris", "uri": "60947", "pos": "n", "morpho": "n-s---mn3-"}, "Moeris3": {
        "lemma": "Moeris", "uri": "60947", "pos": "n", "morpho": "n-s---mn3-"
    }, "molitus1": {"lemma": "molitus", "uri": "117820", "pos": "a", "morpho": "aps---mn1-"}, "molitus2": {
        "lemma": "molitus", "uri": "117820", "pos": "a", "morpho": "aps---mn1-"
    }, "molliculus1": {"lemma": "molliculus", "uri": "m1231", "pos": "a", "morpho": "aps---mn1-"}, "Molliculus2": {
        "lemma": "Molliculus", "uri": "60951", "pos": "n", "morpho": "n-s---mn2-"
    }, "molo1": {"lemma": "molo", "uri": "m1245", "pos": "v", "morpho": "v1spia--3-"}, "Molo2": {
        "lemma": "Molo", "uri": "60952", "pos": "n", "morpho": "n-s---nn3-"
    }, "molon2": {"lemma": "molon", "uri": "m1251", "pos": "n", "morpho": "n-s---nn2g"}, "Molossus1": {
        "lemma": "Molossus", "uri": "58406", "pos": "a", "morpho": "aps---mn1-"
    }, "Molossus2": {"lemma": "Molossus", "uri": "57423", "pos": "n", "morpho": "n-s---mn2-"}, "Molus1": {
        "lemma": "Molus", "uri": "60956", "pos": "n", "morpho": "n-s---mn2-"
    }, "Molus2": {"lemma": "Molus", "uri": "60956", "pos": "n", "morpho": "n-s---mn2-"}, "monitus1": {
        "lemma": "monitus", "uri": "117885", "pos": "a", "morpho": "aps---mn1-"
    }, "monitus2": {"lemma": "monitus", "uri": "m9797", "pos": "n", "morpho": "n-s---mn4-"}, "monstratus1": {
        "lemma": "monstratus", "uri": "46215", "pos": "a", "morpho": "aps---mn1-"
    }, "monstratus2": {"lemma": "monstratus", "uri": "m9798", "pos": "n", "morpho": "n-s---mn4-"}, "montanus1": {
        "lemma": "montanus", "uri": "m1360", "pos": "a", "morpho": "aps---mn1-"
    }, "mora1": {"lemma": "mora", "uri": "m1374", "pos": "n", "morpho": "n-s---fn1-"}, "mora2": {
        "lemma": "mora", "uri": "m1374", "pos": "n", "morpho": "n-s---fn1-"
    }, "mora3": {"lemma": "mora", "uri": "m1374", "pos": "n", "morpho": "n-s---fn1-"}, "moratus1": {
        "lemma": "moratus", "uri": "m1382", "pos": "a", "morpho": "aps---mn1-"
    }, "moratus2": {"lemma": "moratus", "uri": "m1382", "pos": "a", "morpho": "aps---mn1-"}, "mordicus1": {
        "lemma": "mordicus", "uri": "25162", "pos": "r", "morpho": "rp--------"
    }, "mordicus2": {"lemma": "mordicus", "uri": "m1401", "pos": "a", "morpho": "aps---mn1-"}, "morio1": {
        "lemma": "morio", "uri": "m1409", "pos": "n", "morpho": "n-s---mn3-"
    }, "morio2": {"lemma": "morio", "uri": "m1409", "pos": "n", "morpho": "n-s---mn3-"}, "moror1": {
        "lemma": "moror", "uri": "m1416", "pos": "v", "morpho": "v1spid--1-"
    }, "moror2": {"lemma": "moror", "uri": "m1416", "pos": "v", "morpho": "v1spid--1-"}, "morsus1": {
        "lemma": "morsus", "uri": "118005", "pos": "a", "morpho": "aps---mn1-"
    }, "morsus2": {"lemma": "morsus", "uri": "m9799", "pos": "n", "morpho": "n-s---mn4-"}, "morus1": {
        "lemma": "morus", "uri": "m1591", "pos": "a", "morpho": "aps---mn1-"
    }, "morus2": {"lemma": "morus", "uri": "m1441", "pos": "n", "morpho": "n-s---fn2-"}, "motus1": {
        "lemma": "motus", "uri": "118032", "pos": "a", "morpho": "aps---mn1-"
    }, "motus2": {"lemma": "motus", "uri": "m9800", "pos": "n", "morpho": "n-s---mn4-"}, "mugio1": {
        "lemma": "mugio", "uri": "m1477", "pos": "v", "morpho": "v1spia--4-"
    }, "mulio1": {"lemma": "mulio", "uri": "m1604", "pos": "n", "morpho": "n-s---mn3-"}, "multa1": {
        "lemma": "multa", "uri": "m1613", "pos": "n", "morpho": "n-s---fn1-"
    }, "multa2": {"lemma": "multa", "uri": "118083", "pos": "n", "morpho": "n-p---nn2-"}, "multo1": {
        "lemma": "multo", "uri": "25204", "pos": "r", "morpho": "rp--------"
    }, "multo2": {"lemma": "multo", "uri": "m1693", "pos": "v", "morpho": "v1spia--1-"}, "mundus1": {
        "lemma": "mundus", "uri": "m1715", "pos": "a", "morpho": "aps---mn1-"
    }, "mundus2": {"lemma": "mundus", "uri": "m1717", "pos": "n", "morpho": "n-s---mn2-"}, "munificus1": {
        "lemma": "munificus", "uri": "m1740", "pos": "a", "morpho": "aps---mn1-"
    }, "munificus2": {"lemma": "munificus", "uri": "m1740", "pos": "a", "morpho": "aps---mn1-"}, "munio1": {
        "lemma": "munio", "uri": "m1743", "pos": "v", "morpho": "v1spia--4-"
    }, "munio2": {"lemma": "munio", "uri": "118187", "pos": "n", "morpho": "n-s---mn3-"}, "muraena1": {
        "lemma": "muraena", "uri": "45194", "pos": "n", "morpho": "n-s---fn1-"
    }, "murcus1": {"lemma": "murcus", "uri": "m1756", "pos": "n", "morpho": "n-s---mn2-"}, "Murcus2": {
        "lemma": "Murcus", "uri": "60976", "pos": "n", "morpho": "n-s---mn2-"
    }, "murra1": {"lemma": "murra", "uri": "m0934", "pos": "n", "morpho": "n-s---fn1-"}, "murra2": {
        "lemma": "murra", "uri": "m0934", "pos": "n", "morpho": "n-s---fn1-"
    }, "murra3": {"lemma": "murra", "uri": "m0934", "pos": "n", "morpho": "n-s---fn1-"}, "murreus1": {
        "lemma": "murreus", "uri": "m0936", "pos": "a", "morpho": "aps---mn1-"
    }, "murreus2": {"lemma": "murreus", "uri": "m0936", "pos": "a", "morpho": "aps---mn1-"}, "murrinus1": {
        "lemma": "murrinus", "uri": "m0312", "pos": "a", "morpho": "aps---mn1-"
    }, "murrinus2": {"lemma": "murrinus", "uri": "m0312", "pos": "a", "morpho": "aps---mn1-"}, "mus1": {
        "lemma": "mus", "uri": "m1804", "pos": "n", "morpho": "n-s---mn3-"
    }, "Mus2": {"lemma": "Mus", "uri": "60981", "pos": "n", "morpho": "n-s---mn2-"}, "Musa1": {
        "lemma": "Musa", "uri": "60982", "pos": "n", "morpho": "n-s---fn1-"
    }, "Musa2": {"lemma": "Musa", "uri": "60982", "pos": "n", "morpho": "n-s---fn1-"}, "Musaeus1": {
        "lemma": "Musaeus", "uri": "60983", "pos": "n", "morpho": "n-s---mn2-"
    }, "Musaeus2": {"lemma": "Musaeus", "uri": "60983", "pos": "n", "morpho": "n-s---mn2-"}, "musca1": {
        "lemma": "musca", "uri": "m1807", "pos": "n", "morpho": "n-s---fn1-"
    }, "Musca2": {"lemma": "Musca", "uri": "60984", "pos": "n", "morpho": "n-s---fn1-"}, "musice1": {
        "lemma": "musice", "uri": "118265", "pos": "r", "morpho": "rp--------"
    }, "muto1": {"lemma": "muto", "uri": "m1864", "pos": "v", "morpho": "v1spia--1-"}, "muto2": {
        "lemma": "muto", "uri": "25239", "pos": "n", "morpho": "n-s---mn3-"
    }, "mutuo1": {"lemma": "mutuo", "uri": "30765", "pos": "r", "morpho": "rp--------"}, "mutuo2": {
        "lemma": "mutuo", "uri": "51273", "pos": "v", "morpho": "v1spia--1-"
    }, "myrice1": {"lemma": "myrice", "uri": "m1901", "pos": "n", "morpho": "n-s---fn1g"}, "Myron1": {
        "lemma": "Myron", "uri": "61007", "pos": "n", "morpho": "n-s---nn3-"
    }, "myron2": {"lemma": "myron", "uri": "m1911", "pos": "n", "morpho": "n-s---nn2g"}, "myrrhis1": {
        "lemma": "myrrhis", "uri": "m9993", "pos": "n", "morpho": "n-s---fn3-"
    }, "myrrhis2": {"lemma": "myrrhis", "uri": "m9993", "pos": "n", "morpho": "n-s---fn3-"}, "mys1": {
        "lemma": "mys", "uri": "m1928", "pos": "n", "morpho": "n-s---mn3g"
    }, "Mys2": {"lemma": "Mys", "uri": "61010", "pos": "n", "morpho": "n-s---mn3-"}, "naevius1": {
        "lemma": "naeuius", "uri": "n0005", "pos": "a", "morpho": "aps---mn1-"
    }, "Naevius2": {"lemma": "Naeuius", "uri": "61017", "pos": "a", "morpho": "aps---mn1-"}, "nana1": {
        "lemma": "nana", "uri": "n0010", "pos": "n", "morpho": "n-s---fn1-"
    }, "Nar1": {"lemma": "Nar", "uri": "61019", "pos": "n", "morpho": "n-s---mn3-"}, "Nar2": {
        "lemma": "Nar", "uri": "61019", "pos": "n", "morpho": "n-s---mn3-"
    }, "Nar3": {"lemma": "Nar", "uri": "61019", "pos": "n", "morpho": "n-s---mn3-"}, "narcissus1": {
        "lemma": "narcissus", "uri": "n0024", "pos": "n", "morpho": "n-s---mn2-"
    }, "Narcissus2": {"lemma": "Narcissus", "uri": "61021", "pos": "n", "morpho": "n-s---mn2-"}, "narratus1": {
        "lemma": "narratus", "uri": "118457", "pos": "a", "morpho": "aps---mn1-"
    }, "narratus2": {"lemma": "narratus", "uri": "n9765", "pos": "n", "morpho": "n-s---mn4-"}, "nascentia1": {
        "lemma": "nascentia", "uri": "n0033", "pos": "n", "morpho": "n-p---nn3i"
    }, "nascentia2": {"lemma": "nascentia", "uri": "n0033", "pos": "n", "morpho": "n-p---nn3i"}, "nasica1": {
        "lemma": "nasica", "uri": "n0047", "pos": "n", "morpho": "n-s---mn1-"
    }, "Nasica2": {"lemma": "Nasica", "uri": "61027", "pos": "n", "morpho": "n-s---fn1-"}, "nasus1": {
        "lemma": "nasus", "uri": "n0053", "pos": "n", "morpho": "n-s---mn2-"
    }, "natalis1": {"lemma": "natalis", "uri": "n0059", "pos": "a", "morpho": "aps---cn3i"}, "natus1": {
        "lemma": "natus", "uri": "25271", "pos": "a", "morpho": "aps---mn1-"
    }, "natus2": {"lemma": "natus", "uri": "57753", "pos": "n", "morpho": "n-s---mn4-"}, "Nauplius1": {
        "lemma": "Nauplius", "uri": "61034", "pos": "n", "morpho": "n-s---mn2-"
    }, "nauplius2": {"lemma": "nauplius", "uri": "n0111", "pos": "n", "morpho": "n-s---mn2-"}, "Nazaraeus1": {
        "lemma": "Nazaraeus", "uri": "61042", "pos": "n", "morpho": "n-s---mn2-"
    }, "Nazaraeus2": {"lemma": "Nazaraeus", "uri": "61042", "pos": "n", "morpho": "n-s---mn2-"}, "ne1": {
        "lemma": "ne", "uri": "n0131", "pos": "r", "morpho": "rp--------"
    }, "ne2": {"lemma": "ne", "uri": "n0131", "pos": "r", "morpho": "rp--------"}, "ne3": {
        "lemma": "ne", "uri": "n0131", "pos": "r", "morpho": "rp--------"
    }, "nebris1": {"lemma": "nebris", "uri": "n0132", "pos": "n", "morpho": "n-s---fn3-"}, "nec1": {
        "lemma": "nec", "uri": "25286", "pos": "r", "morpho": "rp--------"
    }, "nec2": {"lemma": "nec", "uri": "25286", "pos": "r", "morpho": "rp--------"}, "neglectus1": {
        "lemma": "neglectus", "uri": "99565", "pos": "a", "morpho": "aps---mn1-"
    }, "neglectus2": {"lemma": "neglectus", "uri": "n9767", "pos": "n", "morpho": "n-s---mn4-"}, "Nemea1": {
        "lemma": "Nemea", "uri": "61051", "pos": "n", "morpho": "n-s---fn1-"
    }, "Nemea2": {"lemma": "Nemea", "uri": "61051", "pos": "n", "morpho": "n-s---fn1-"}, "Nemesis1": {
        "lemma": "Nemesis", "uri": "61052", "pos": "n", "morpho": "n-s---fn3-"
    }, "Nemesis2": {"lemma": "Nemesis", "uri": "61052", "pos": "n", "morpho": "n-s---fn3-"}, "neo1": {
        "lemma": "neo", "uri": "n0211", "pos": "v", "morpho": "v1spia--2-"
    }, "Neo2": {"lemma": "Neo", "uri": "61055", "pos": "n", "morpho": "n-s---nn3-"}, "Nepeta1": {
        "lemma": "Nepeta", "uri": "61059", "pos": "n", "morpho": "n-s---fn1-"
    }, "nepeta2": {"lemma": "nepeta", "uri": "n0220", "pos": "n", "morpho": "n-s---fn1-"}, "nepos1": {
        "lemma": "nepos", "uri": "n0224", "pos": "n", "morpho": "n-s---mn3-"
    }, "Nepos2": {"lemma": "Nepos", "uri": "61061", "pos": "n", "morpho": "n-s---mn2-"}, "nepotilla1": {
        "lemma": "nepotilla", "uri": "118642", "pos": "n", "morpho": "n-s---fn1-"
    }, "nepotinus1": {"lemma": "nepotinus", "uri": "99568", "pos": "a", "morpho": "aps---mn1-"}, "Nereis1": {
        "lemma": "Nereis", "uri": "61064", "pos": "n", "morpho": "n-s---fn3-"
    }, "Nereis2": {"lemma": "Nereis", "uri": "61064", "pos": "n", "morpho": "n-s---fn3-"}, "nervicus1": {
        "lemma": "neruicus", "uri": "n0242", "pos": "a", "morpho": "aps---mn1-"
    }, "netus1": {"lemma": "netus", "uri": "118674", "pos": "a", "morpho": "aps---mn1-"}, "netus2": {
        "lemma": "netus", "uri": "n9769", "pos": "n", "morpho": "n-s---mn4-"
    }, "nexus1": {"lemma": "nexus", "uri": "118697", "pos": "a", "morpho": "aps---mn1-"}, "nexus2": {
        "lemma": "nexus", "uri": "n9770", "pos": "n", "morpho": "n-s---mn4-"
    }, "nico1": {"lemma": "nico", "uri": "118701", "pos": "v", "morpho": "v1spia--3-"}, "Nico2": {
        "lemma": "Nico", "uri": "61092", "pos": "n", "morpho": "n-s---nn3-"
    }, "nigellus1": {"lemma": "nigellus", "uri": "n0289", "pos": "a", "morpho": "aps---mn1-"}, "niger1": {
        "lemma": "niger", "uri": "n0291", "pos": "a", "morpho": "aps---mn1r"
    }, "Niger2": {"lemma": "Niger", "uri": "61098", "pos": "n", "morpho": "n-s---mn3-"}, "Niger3": {
        "lemma": "Niger", "uri": "61098", "pos": "n", "morpho": "n-s---mn3-"
    }, "nisus1": {"lemma": "nisus", "uri": "118744", "pos": "a", "morpho": "aps---mn1-"}, "nisus2": {
        "lemma": "nisus", "uri": "n0303", "pos": "n", "morpho": "n-s---mn4-"
    }, "Nisus3": {"lemma": "Nisus", "uri": "61109", "pos": "n", "morpho": "n-s---mn2-"}, "nitela1": {
        "lemma": "nitela", "uri": "n0323", "pos": "n", "morpho": "n-s---fn1-"
    }, "nitela2": {"lemma": "nitela", "uri": "n0323", "pos": "n", "morpho": "n-s---fn1-"}, "nitens1": {
        "lemma": "nitens", "uri": "118750", "pos": "a", "morpho": "aps---an3i"
    }, "nitens2": {"lemma": "nitens", "uri": "118750", "pos": "a", "morpho": "aps---an3i"}, "nitor1": {
        "lemma": "nitor", "uri": "n0322", "pos": "v", "morpho": "v1spid--3-"
    }, "nitor2": {"lemma": "nitor", "uri": "n9323", "pos": "n", "morpho": "n-s---mn3-"}, "nixus1": {
        "lemma": "nixus", "uri": "118771", "pos": "a", "morpho": "aps---mn1-"
    }, "nixus2": {"lemma": "nixus", "uri": "n0303", "pos": "n", "morpho": "n-s---mn4-"}, "no1": {
        "lemma": "no", "uri": "n0444", "pos": "v", "morpho": "v1spia--1-"
    }, "noctua1": {"lemma": "noctua", "uri": "n0465", "pos": "n", "morpho": "n-s---fn1-"}, "Nola1": {
        "lemma": "Nola", "uri": "61112", "pos": "n", "morpho": "n-s---fn1-"
    }, "Nola3": {"lemma": "Nola", "uri": "61112", "pos": "n", "morpho": "n-s---fn1-"}, "nominatus1": {
        "lemma": "nominatus", "uri": "41718", "pos": "a", "morpho": "aps---mn1-"
    }, "nominatus2": {"lemma": "nominatus", "uri": "n9771", "pos": "n", "morpho": "n-s---mn4-"}, "nona1": {
        "lemma": "nona", "uri": "n0177", "pos": "n", "morpho": "n-s---fn1-"
    }, "notos2": {"lemma": "notos", "uri": "118875", "pos": "n", "morpho": "n-s---mn3-"}, "notus1": {
        "lemma": "notus", "uri": "55561", "pos": "a", "morpho": "aps---mn1-"
    }, "Notus2": {"lemma": "Notus", "uri": "n0544", "pos": "n", "morpho": "n-s---mn2-"}, "novellus1": {
        "lemma": "nouellus", "uri": "n0568", "pos": "a", "morpho": "aps---mn1-"
    }, "Novellus2": {"lemma": "Nouellus", "uri": "61125", "pos": "n", "morpho": "n-s---mn2-"}, "nucula1": {
        "lemma": "nucula", "uri": "n0619", "pos": "n", "morpho": "n-s---fn1-"
    }, "numerius1": {"lemma": "numerius", "uri": "n0657", "pos": "a", "morpho": "aps---mn1-"}, "Numerius2": {
        "lemma": "Numerius", "uri": "61133", "pos": "a", "morpho": "aps---mn1-"
    }, "Numerius3": {"lemma": "Numerius", "uri": "61133", "pos": "a", "morpho": "aps---mn1-"}, "numero1": {
        "lemma": "numero", "uri": "n0658", "pos": "v", "morpho": "v1spia--1-"
    }, "numero2": {"lemma": "numero", "uri": "n0659", "pos": "r", "morpho": "rp--------"}, "Numicius1": {
        "lemma": "Numicius", "uri": "61134", "pos": "n", "morpho": "n-s---mn2-"
    }, "Numicius2": {"lemma": "Numicius", "uri": "61134", "pos": "n", "morpho": "n-s---mn2-"}, "nundina1": {
        "lemma": "nundina", "uri": "48148", "pos": "n", "morpho": "n-s---fn1-"
    }, "nuptus1": {"lemma": "nuptus", "uri": "119020", "pos": "a", "morpho": "aps---mn1-"}, "nuptus2": {
        "lemma": "nuptus", "uri": "n9764", "pos": "n", "morpho": "n-s---mn4-"
    }, "nutritus1": {"lemma": "nutritus", "uri": "119041", "pos": "a", "morpho": "aps---mn1-"}, "nutritus2": {
        "lemma": "nutritus", "uri": "119042", "pos": "n", "morpho": "n-s---mn4-"
    }, "nymphaeum2": {"lemma": "nymphaeum", "uri": "n0353", "pos": "n", "morpho": "n-s---nn2-"}, "Nysa1": {
        "lemma": "Nysa", "uri": "61142", "pos": "n", "morpho": "n-s---fn1-"
    }, "Nysa2": {"lemma": "Nysa", "uri": "61142", "pos": "n", "morpho": "n-s---fn1-"}, "obba1": {
        "lemma": "obba", "uri": "o0021", "pos": "n", "morpho": "n-s---fn1-"
    }, "Obba2": {"lemma": "Obba", "uri": "61147", "pos": "n", "morpho": "n-s---fn1-"}, "obitus1": {
        "lemma": "obitus", "uri": "99634", "pos": "a", "morpho": "aps---mn1-"
    }, "obitus2": {"lemma": "obitus", "uri": "o9990", "pos": "n", "morpho": "n-s---mn4-"}, "objectus1": {
        "lemma": "obiectus", "uri": "34673", "pos": "a", "morpho": "aps---mn1-"
    }, "objectus2": {"lemma": "obiectus", "uri": "o0060", "pos": "n", "morpho": "n-s---mn4-"}, "oblitus1": {
        "lemma": "oblitus", "uri": "47277", "pos": "a", "morpho": "aps---mn1-"
    }, "oblitus2": {"lemma": "oblitus", "uri": "47277", "pos": "a", "morpho": "aps---mn1-"}, "obnisus1": {
        "lemma": "obnisus", "uri": "119182", "pos": "a", "morpho": "aps---mn1-"
    }, "obnisus2": {"lemma": "obnisus", "uri": "o9991", "pos": "n", "morpho": "n-s---mn4-"}, "obortus1": {
        "lemma": "obortus", "uri": "54136", "pos": "a", "morpho": "aps---mn1-"
    }, "obortus2": {"lemma": "obortus", "uri": "119196", "pos": "n", "morpho": "n-s---mn4-"}, "obsequens1": {
        "lemma": "obsequens", "uri": "99654", "pos": "a", "morpho": "aps---an3i"
    }, "Obsequens2": {"lemma": "Obsequens", "uri": "101317", "pos": "n", "morpho": "n-s---mn3i"}, "obsero1": {
        "lemma": "obsero", "uri": "o0221", "pos": "v", "morpho": "v1spia--1-"
    }, "obsero2": {"lemma": "obsero", "uri": "o0222", "pos": "v", "morpho": "v1spia--3-"}, "obsidium1": {
        "lemma": "obsidium", "uri": "o9722", "pos": "n", "morpho": "n-s---nn2-"
    }, "obsidium2": {"lemma": "obsidium", "uri": "o9722", "pos": "n", "morpho": "n-s---nn2-"}, "obstantia1": {
        "lemma": "obstantia", "uri": "o0261", "pos": "n", "morpho": "n-p---nn3i"
    }, "obstantia2": {"lemma": "obstantia", "uri": "o0261", "pos": "n", "morpho": "n-p---nn3i"}, "obstrictus1": {
        "lemma": "obstrictus", "uri": "119300", "pos": "a", "morpho": "aps---mn1-"
    }, "obstrictus2": {"lemma": "obstrictus", "uri": "119301", "pos": "n", "morpho": "n-s---mn4-"}, "obtectus1": {
        "lemma": "obtectus", "uri": "119320", "pos": "n", "morpho": "n-s---mn4-"
    }, "obtectus2": {"lemma": "obtectus", "uri": "119319", "pos": "a", "morpho": "aps---mn1-"}, "obtentus1": {
        "lemma": "obtentus", "uri": "119328", "pos": "a", "morpho": "aps---mn1-"
    }, "obtentus2": {"lemma": "obtentus", "uri": "o9994", "pos": "n", "morpho": "n-s---mn4-"}, "obtritus1": {
        "lemma": "obtritus", "uri": "119341", "pos": "a", "morpho": "aps---mn1-"
    }, "obtritus2": {"lemma": "obtritus", "uri": "o9995", "pos": "n", "morpho": "n-s---mn4-"}, "occasus1": {
        "lemma": "occasus", "uri": "53845", "pos": "a", "morpho": "aps---mn1-"
    }, "occasus2": {"lemma": "occasus", "uri": "o9998", "pos": "n", "morpho": "n-s---mn4-"}, "occulto1": {
        "lemma": "occulto", "uri": "119438", "pos": "r", "morpho": "rp--------"
    }, "occulto2": {"lemma": "occulto", "uri": "o0411", "pos": "v", "morpho": "v1spia--1-"}, "occupatus1": {
        "lemma": "occupatus", "uri": "38555", "pos": "a", "morpho": "aps---mn1-"
    }, "occupatus2": {"lemma": "occupatus", "uri": "o9709", "pos": "n", "morpho": "n-s---mn4-"}, "ocrea1": {
        "lemma": "ocrea", "uri": "o0438", "pos": "n", "morpho": "n-s---fn1-"
    }, "Ocrea2": {"lemma": "Ocrea", "uri": "61153", "pos": "n", "morpho": "n-s---fn1-"}, "October1": {
        "lemma": "October", "uri": "61157", "pos": "n", "morpho": "n-s---mn3-"
    }, "October2": {"lemma": "October", "uri": "61157", "pos": "n", "morpho": "n-s---mn3-"}, "odium1": {
        "lemma": "odium", "uri": "o0513", "pos": "n", "morpho": "n-s---nn2-"
    }, "odium2": {"lemma": "odium", "uri": "o0513", "pos": "n", "morpho": "n-s---nn2-"}, "odoratus1": {
        "lemma": "odoratus", "uri": "25528", "pos": "a", "morpho": "aps---mn1-"
    }, "odoratus2": {"lemma": "odoratus", "uri": "o9711", "pos": "n", "morpho": "n-s---mn4-"}, "Oeneus1": {
        "lemma": "Oeneus", "uri": "61179", "pos": "n", "morpho": "n-s---mn2-"
    }, "Oeneus2": {"lemma": "Oeneus", "uri": "61179", "pos": "n", "morpho": "n-s---mn2-"}, "oenus1": {
        "lemma": "oenus", "uri": "119565", "pos": "a", "morpho": "aps---mn1-"
    }, "Oenus2": {"lemma": "Oenus", "uri": "101321", "pos": "n", "morpho": "n-s---mn3i"}, "ofella1": {
        "lemma": "ofella", "uri": "o0551", "pos": "n", "morpho": "n-s---fn1-"
    }, "Ofella2": {"lemma": "Ofella", "uri": "61192", "pos": "n", "morpho": "n-s---fn1-"}, "offectus1": {
        "lemma": "offectus", "uri": "119576", "pos": "a", "morpho": "aps---mn1-"
    }, "offectus2": {"lemma": "offectus", "uri": "o0606", "pos": "n", "morpho": "n-s---mn4-"}, "offendo1": {
        "lemma": "offendo", "uri": "o0562", "pos": "v", "morpho": "v1spia--3-"
    }, "offendo2": {"lemma": "offendo", "uri": "o0561", "pos": "n", "morpho": "n-s---fn3-"}, "offensus1": {
        "lemma": "offensus", "uri": "99696", "pos": "a", "morpho": "aps---mn1-"
    }, "offensus2": {"lemma": "offensus", "uri": "o9987", "pos": "n", "morpho": "n-s---mn4-"}, "offerumenta1": {
        "lemma": "offerumenta", "uri": "49843", "pos": "n", "morpho": "n-s---fn1-"
    }, "offerumenta2": {"lemma": "offerumenta", "uri": "119589", "pos": "n", "morpho": "n-p---nn2-"}, "Olenos1": {
        "lemma": "Olenos", "uri": "61203", "pos": "n", "morpho": "n-s---mn2-"
    }, "Olenos2": {"lemma": "Olenos", "uri": "61203", "pos": "n", "morpho": "n-s---mn2-"}, "oleo1": {
        "lemma": "oleo", "uri": "o0637", "pos": "v", "morpho": "v1spia--2-"
    }, "oleo2": {"lemma": "oleo", "uri": "o0637", "pos": "v", "morpho": "v1spia--2-"}, "oletum1": {
        "lemma": "oletum", "uri": "o0652", "pos": "n", "morpho": "n-s---nn2-"
    }, "oletum2": {"lemma": "oletum", "uri": "o0652", "pos": "n", "morpho": "n-s---nn2-"}, "olfactus1": {
        "lemma": "olfactus", "uri": "119637", "pos": "a", "morpho": "aps---mn1-"
    }, "olfactus2": {"lemma": "olfactus", "uri": "o0653", "pos": "n", "morpho": "n-s---mn4-"}, "olor1": {
        "lemma": "olor", "uri": "o0682", "pos": "n", "morpho": "n-s---mn3-"
    }, "olor2": {"lemma": "olor", "uri": "o0682", "pos": "n", "morpho": "n-s---mn3-"}, "Olympias1": {
        "lemma": "Olympias", "uri": "61208", "pos": "n", "morpho": "n-s---mn3-"
    }, "Olympias2": {"lemma": "Olympias", "uri": "61208", "pos": "n", "morpho": "n-s---mn3-"}, "Olympias3": {
        "lemma": "Olympias", "uri": "61208", "pos": "n", "morpho": "n-s---mn3-"
    }, "omnigenus1": {"lemma": "omnigenus", "uri": "o0709", "pos": "a", "morpho": "aps---mn1-"}, "omnigenus2": {
        "lemma": "omnigenus", "uri": "o0709", "pos": "a", "morpho": "aps---mn1-"
    }, "Onchestus1": {"lemma": "Onchestus", "uri": "61216", "pos": "n", "morpho": "n-s---mn2-"}, "Onchestus2": {
        "lemma": "Onchestus", "uri": "61216", "pos": "n", "morpho": "n-s---mn2-"
    }, "opertus1": {"lemma": "opertus", "uri": "41510", "pos": "a", "morpho": "aps---mn1-"}, "opertus2": {
        "lemma": "opertus", "uri": "o9712", "pos": "n", "morpho": "n-s---mn4-"
    }, "ophion1": {"lemma": "ophion", "uri": "o0805", "pos": "n", "morpho": "n-s---mn3-"}, "Ophion2": {
        "lemma": "Ophion", "uri": "61220", "pos": "n", "morpho": "n-s---nn3-"
    }, "ophites1": {"lemma": "ophites", "uri": "o0809", "pos": "n", "morpho": "n-s---mn1g"}, "Ophites2": {
        "lemma": "Ophites", "uri": "61222", "pos": "n", "morpho": "n-p---mn3-"
    }, "ophiusa1": {"lemma": "ophiusa", "uri": "o0810", "pos": "n", "morpho": "n-s---fn1-"}, "Ophiusa2": {
        "lemma": "Ophiusa", "uri": "61224", "pos": "n", "morpho": "n-s---fn1-"
    }, "opinatus1": {"lemma": "opinatus", "uri": "36313", "pos": "a", "morpho": "aps---mn1-"}, "opinatus2": {
        "lemma": "opinatus", "uri": "o9713", "pos": "n", "morpho": "n-s---mn4-"
    }, "oppositus1": {"lemma": "oppositus", "uri": "52307", "pos": "a", "morpho": "aps---mn1-"}, "oppositus2": {
        "lemma": "oppositus", "uri": "o9716", "pos": "n", "morpho": "n-s---mn4-"
    }, "oppressus1": {"lemma": "oppressus", "uri": "119829", "pos": "a", "morpho": "aps---mn1-"}, "oppressus2": {
        "lemma": "oppressus", "uri": "o9717", "pos": "n", "morpho": "n-s---mn4-"
    }, "oppugno1": {"lemma": "oppugno", "uri": "o0894", "pos": "v", "morpho": "v1spia--1-"}, "oppugno2": {
        "lemma": "oppugno", "uri": "o0894", "pos": "v", "morpho": "v1spia--1-"
    }, "ops1": {"lemma": "ops", "uri": "o0897", "pos": "n", "morpho": "n-s---fn3-"}, "optio1": {
        "lemma": "optio", "uri": "o0906", "pos": "n", "morpho": "n-s---fn3-"
    }, "optio2": {"lemma": "optio", "uri": "o0906", "pos": "n", "morpho": "n-s---fn3-"}, "opus1": {
        "lemma": "opus", "uri": "o0918", "pos": "n", "morpho": "n-s---fn3i"
    }, "Opus2": {"lemma": "Opus", "uri": "61229", "pos": "n", "morpho": "n-s---mn2-"}, "ora1": {
        "lemma": "ora", "uri": "o0923", "pos": "n", "morpho": "n-s---fn1-"
    }, "Ora2": {"lemma": "Ora", "uri": "61230", "pos": "n", "morpho": "n-s---fn1-"}, "orca1": {
        "lemma": "orca", "uri": "o0953", "pos": "n", "morpho": "n-s---fn1-"
    }, "Orca2": {"lemma": "Orca", "uri": "61232", "pos": "n", "morpho": "n-s---fn1-"}, "origo1": {
        "lemma": "origo", "uri": "o1004", "pos": "n", "morpho": "n-s---fn3-"
    }, "ornatus1": {"lemma": "ornatus", "uri": "40146", "pos": "a", "morpho": "aps---mn1-"}, "ornatus2": {
        "lemma": "ornatus", "uri": "o9719", "pos": "n", "morpho": "n-s---mn4-"
    }, "orneus1": {"lemma": "orneus", "uri": "o1019", "pos": "a", "morpho": "aps---mn1-"}, "Orneus2": {
        "lemma": "Orneus", "uri": "61254", "pos": "n", "morpho": "n-s---mn2-"
    }, "orsus1": {"lemma": "orsus", "uri": "119955", "pos": "a", "morpho": "aps---mn1-"}, "orsus2": {
        "lemma": "orsus", "uri": "o0962", "pos": "n", "morpho": "n-s---mn4-"
    }, "ortus1": {"lemma": "ortus", "uri": "119976", "pos": "a", "morpho": "aps---mn1-"}, "ortus2": {
        "lemma": "ortus", "uri": "o9720", "pos": "n", "morpho": "n-s---mn4-"
    }, "ortygia1": {"lemma": "ortygia", "uri": "119978", "pos": "n", "morpho": "n-s---fn1-"}, "Ortygia2": {
        "lemma": "Ortygia", "uri": "61265", "pos": "n", "morpho": "n-s---fn1-"
    }, "os1": {"lemma": "os", "uri": "o1065", "pos": "n", "morpho": "n-s---nn3-"}, "os2": {
        "lemma": "os", "uri": "o1065", "pos": "n", "morpho": "n-s---nn3-"
    }, "oscillum1": {"lemma": "oscillum", "uri": "o1071", "pos": "n", "morpho": "n-s---nn2-"}, "oscillum2": {
        "lemma": "oscillum", "uri": "o1071", "pos": "n", "morpho": "n-s---nn2-"
    }, "osculo1": {"lemma": "osculo", "uri": "o1201", "pos": "v", "morpho": "v1spia--1-"}, "osculo2": {
        "lemma": "osculo", "uri": "o1201", "pos": "v", "morpho": "v1spia--1-"
    }, "ostentus1": {"lemma": "ostentus", "uri": "120024", "pos": "a", "morpho": "aps---mn1-"}, "ostentus2": {
        "lemma": "ostentus", "uri": "o9721", "pos": "n", "morpho": "n-s---mn4-"
    }, "ostiarius1": {"lemma": "ostiarius", "uri": "o1110", "pos": "n", "morpho": "n-s---mn2-"}, "ostiarius2": {
        "lemma": "ostiarius", "uri": "o1110", "pos": "a", "morpho": "aps---mn1-"
    }, "otus1": {"lemma": "otus", "uri": "o1150", "pos": "n", "morpho": "n-s---mn2-"}, "ovatus1": {
        "lemma": "ouatus", "uri": "o9726", "pos": "a", "morpho": "aps---mn1-"
    }, "ovatus2": {"lemma": "ouatus", "uri": "o9726", "pos": "a", "morpho": "aps---mn1-"}, "ovatus3": {
        "lemma": "ouatus", "uri": "o1198", "pos": "n", "morpho": "n-s---mn4-"
    }, "paco1": {"lemma": "paco", "uri": "p0023", "pos": "v", "morpho": "v1spia--3-"}, "paco2": {
        "lemma": "paco", "uri": "p0022", "pos": "v", "morpho": "v1spia--1-"
    }, "pactus1": {"lemma": "pactus", "uri": "58353", "pos": "a", "morpho": "aps---mn1-"}, "pactus2": {
        "lemma": "pactus", "uri": "58353", "pos": "a", "morpho": "aps---mn1-"
    }, "pactus3": {"lemma": "pactus", "uri": "p9863", "pos": "n", "morpho": "n-s---mn2-"}, "paedico1": {
        "lemma": "paedico", "uri": "p0041", "pos": "v", "morpho": "v1spia--1-"
    }, "paedico2": {"lemma": "paedico", "uri": "p0042", "pos": "n", "morpho": "n-s---mn3-"}, "paenula1": {
        "lemma": "paenula", "uri": "p0018", "pos": "n", "morpho": "n-s---fn1-"
    }, "Paenula2": {"lemma": "Paenula", "uri": "61294", "pos": "n", "morpho": "n-s---fn1-"}, "paeonia1": {
        "lemma": "paeonia", "uri": "p0061", "pos": "n", "morpho": "n-s---fn1-"
    }, "Paeonius1": {"lemma": "Paeonius", "uri": "61296", "pos": "a", "morpho": "aps---mn1-"}, "Paeonius2": {
        "lemma": "Paeonius", "uri": "61296", "pos": "a", "morpho": "aps---mn1-"
    }, "paetus1": {"lemma": "paetus", "uri": "p0064", "pos": "a", "morpho": "aps---mn1-"}, "Paetus2": {
        "lemma": "Paetus", "uri": "61298", "pos": "n", "morpho": "n-s---mn2-"
    }, "Palici1": {"lemma": "Palici", "uri": "61310", "pos": "n", "morpho": "n-p---mn2-"}, "Palici2": {
        "lemma": "Palici", "uri": "61310", "pos": "n", "morpho": "n-p---mn2-"
    }, "Pallas1": {"lemma": "Pallas", "uri": "61314", "pos": "n", "morpho": "n-s---mn3-"}, "Pallas2": {
        "lemma": "Pallas", "uri": "61314", "pos": "n", "morpho": "n-s---mn3-"
    }, "palma1": {"lemma": "palma", "uri": "p0229", "pos": "n", "morpho": "n-s---fn1-"}, "palma2": {
        "lemma": "palma", "uri": "p0229", "pos": "n", "morpho": "n-s---fn1-"
    }, "palmipes1": {"lemma": "palmipes", "uri": "p0140", "pos": "a", "morpho": "aps---an3-"}, "palmipes2": {
        "lemma": "palmipes", "uri": "p0140", "pos": "a", "morpho": "aps---an3-"
    }, "palo1": {"lemma": "palo", "uri": "p4330", "pos": "v", "morpho": "v1spia--1-"}, "palo2": {
        "lemma": "palo", "uri": "p4330", "pos": "v", "morpho": "v1spia--1-"
    }, "palpo1": {"lemma": "palpo", "uri": "p0161", "pos": "v", "morpho": "v1spia--1-"}, "palpo2": {
        "lemma": "palpo", "uri": "p0162", "pos": "n", "morpho": "n-s---mn3-"
    }, "palus1": {"lemma": "palus", "uri": "p0177", "pos": "n", "morpho": "n-s---mn2-"}, "pampinatus1": {
        "lemma": "pampinatus", "uri": "120253", "pos": "a", "morpho": "aps---mn1-"
    }, "pampinatus2": {"lemma": "pampinatus", "uri": "120253", "pos": "a", "morpho": "aps---mn1-"}, "panacea1": {
        "lemma": "panacea", "uri": "p0192", "pos": "n", "morpho": "n-s---fn1-"
    }, "pando1": {"lemma": "pando", "uri": "p0214", "pos": "v", "morpho": "v1spia--1-"}, "pando2": {
        "lemma": "pando", "uri": "p0215", "pos": "v", "morpho": "v1spia--3-"
    }, "panniculus1": {"lemma": "panniculus", "uri": "p0237", "pos": "n", "morpho": "n-s---mn2-"}, "panniculus2": {
        "lemma": "panniculus", "uri": "p0237", "pos": "n", "morpho": "n-s---mn2-"
    }, "Panope1": {"lemma": "Panope", "uri": "61341", "pos": "n", "morpho": "n-s---fn1-"}, "Panope2": {
        "lemma": "Panope", "uri": "61341", "pos": "n", "morpho": "n-s---fn1-"
    }, "pansa1": {"lemma": "pansa", "uri": "p9864", "pos": "n", "morpho": "n-s---mn1-"}, "Pansa2": {
        "lemma": "Pansa", "uri": "59610", "pos": "n", "morpho": "n-s---mn1-"
    }, "panther1": {"lemma": "panther", "uri": "p7100", "pos": "n", "morpho": "n-s---mn3-"}, "panther2": {
        "lemma": "panther", "uri": "p7100", "pos": "n", "morpho": "n-s---mn3-"
    }, "panthera1": {"lemma": "panthera", "uri": "p7100", "pos": "n", "morpho": "n-s---fn1-"}, "panthera2": {
        "lemma": "panthera", "uri": "p7100", "pos": "n", "morpho": "n-s---fn1-"
    }, "papa1": {"lemma": "papa", "uri": "p0244", "pos": "n", "morpho": "n-s---mn1-"}, "papa2": {
        "lemma": "papa", "uri": "p0244", "pos": "n", "morpho": "n-s---mn1-"
    }, "Paphos1": {"lemma": "Paphos", "uri": "61349", "pos": "n", "morpho": "n-s---mn2-"}, "Paphos2": {
        "lemma": "Paphos", "uri": "61349", "pos": "n", "morpho": "n-s---mn2-"
    }, "pararius1": {"lemma": "pararius", "uri": "p0343", "pos": "a", "morpho": "aps---mn1-"}, "pararius2": {
        "lemma": "pararius", "uri": "p0343", "pos": "n", "morpho": "n-s---mn2-"
    }, "paratus1": {"lemma": "paratus", "uri": "25725", "pos": "a", "morpho": "aps---mn1-"}, "paratus2": {
        "lemma": "paratus", "uri": "p9874", "pos": "n", "morpho": "n-s---mn4-"
    }, "parens2": {"lemma": "parens", "uri": None, "pos": "n", "morpho": "n-s---cn3-"}, "pario1": {
        "lemma": "pario", "uri": "p0410", "pos": "v", "morpho": "v1spia--1-"
    }, "parma1": {"lemma": "parma", "uri": "p0414", "pos": "n", "morpho": "n-s---fn1-"}, "Parma2": {
        "lemma": "Parma", "uri": "61363", "pos": "n", "morpho": "n-s---fn1-"
    }, "paro1": {"lemma": "paro", "uri": "p4697", "pos": "v", "morpho": "v1spia--1-"}, "paro2": {
        "lemma": "paro", "uri": "p4697", "pos": "v", "morpho": "v1spia--1-"
    }, "paro3": {"lemma": "paro", "uri": "120492", "pos": "n", "morpho": "n-s---mn3-"}, "parra1": {
        "lemma": "parra", "uri": "p0248", "pos": "n", "morpho": "n-s---fn1-"
    }, "Parrhasius1": {"lemma": "Parrhasius", "uri": "61370", "pos": "n", "morpho": "n-s---mn2-"}, "Parrhasius2": {
        "lemma": "Parrhasius", "uri": "61370", "pos": "n", "morpho": "n-s---mn2-"
    }, "Parthus1": {"lemma": "Parthus", "uri": "61381", "pos": "n", "morpho": "n-s---mn2-"}, "Parthus2": {
        "lemma": "Parthus", "uri": "61381", "pos": "n", "morpho": "n-s---mn2-"
    }, "Parthus3": {"lemma": "Parthus", "uri": "61381", "pos": "n", "morpho": "n-s---mn2-"}, "partio1": {
        "lemma": "partio", "uri": "p0467", "pos": "n", "morpho": "n-s---fn3-"
    }, "partio2": {"lemma": "partio", "uri": "p0468", "pos": "v", "morpho": "v1spia--4-"}, "partus1": {
        "lemma": "partus", "uri": "120553", "pos": "a", "morpho": "aps---mn1-"
    }, "partus2": {"lemma": "partus", "uri": None, "pos": "n", "morpho": "n-s---mn4-"}, "parus1": {
        "lemma": "parus", "uri": "49086", "pos": "n", "morpho": "n-s---mn2-"
    }, "passer1": {"lemma": "passer", "uri": "p0502", "pos": "n", "morpho": "n-s---mn3-"}, "passerinus1": {
        "lemma": "passerinus", "uri": "p0506", "pos": "a", "morpho": "aps---mn1-"
    }, "Passerinus2": {"lemma": "Passerinus", "uri": "61385", "pos": "n", "morpho": "n-s---mn2-"}, "passive1": {
        "lemma": "passiue", "uri": "56717", "pos": "r", "morpho": "rp--------"
    }, "passive2": {"lemma": "passiue", "uri": "56717", "pos": "r", "morpho": "rp--------"}, "passivus1": {
        "lemma": "passiuus", "uri": "p4358", "pos": "a", "morpho": "aps---mn1-"
    }, "passivus2": {"lemma": "passiuus", "uri": "p4358", "pos": "a", "morpho": "aps---mn1-"}, "passus1": {
        "lemma": "passus", "uri": "99826", "pos": "a", "morpho": "aps---mn1-"
    }, "passus2": {"lemma": "passus", "uri": "99826", "pos": "a", "morpho": "aps---mn1-"}, "passus3": {
        "lemma": "passus", "uri": "p9877", "pos": "n", "morpho": "n-s---mn4-"
    }, "pastus2": {"lemma": "pastus", "uri": "p0498", "pos": "n", "morpho": "n-s---mn4-"}, "patella1": {
        "lemma": "patella", "uri": "p0546", "pos": "n", "morpho": "n-s---fn1-"
    }, "patibulus1": {"lemma": "patibulus", "uri": "120622", "pos": "a", "morpho": "aps---mn1-"}, "patibulus2": {
        "lemma": "patibulus", "uri": "120623", "pos": "n", "morpho": "n-s---mn2-"
    }, "patina1": {"lemma": "patina", "uri": "p0564", "pos": "n", "morpho": "n-s---fn1-"}, "Patina2": {
        "lemma": "Patina", "uri": "61390", "pos": "n", "morpho": "n-s---fn1-"
    }, "patrius1": {"lemma": "patrius", "uri": "p0588", "pos": "a", "morpho": "aps---mn1-"}, "patrius2": {
        "lemma": "patrius", "uri": "p0588", "pos": "a", "morpho": "aps---mn1-"
    }, "patruus1": {"lemma": "patruus", "uri": "p0598", "pos": "n", "morpho": "n-s---mn2-"}, "patruus2": {
        "lemma": "patruus", "uri": "p0598", "pos": "a", "morpho": "aps---mn1-"
    }, "paulus1": {"lemma": "paulus", "uri": "25786", "pos": "a", "morpho": "aps---mn1-"}, "Paulus2": {
        "lemma": "Paulus", "uri": "61396", "pos": "n", "morpho": "n-s---mn2-"
    }, "pavo1": {"lemma": "pauo", "uri": "p0626", "pos": "n", "morpho": "n-s---mn3-"}, "pax1": {
        "lemma": "pax", "uri": "p0650", "pos": "n", "morpho": "n-s---fn3-"
    }, "Pax2": {"lemma": "Pax", "uri": "61401", "pos": "n", "morpho": "n-s---mn3-"}, "pecus1": {
        "lemma": "pecus", "uri": "p0698", "pos": "n", "morpho": "n-s---nn3-"
    }, "pecus2": {"lemma": "pecus", "uri": "p0698", "pos": "n", "morpho": "n-s---nn3-"}, "pecus3": {
        "lemma": "pecus", "uri": "p0698", "pos": "n", "morpho": "n-s---nn3-"
    }, "pedatura1": {"lemma": "pedatura", "uri": "p8705", "pos": "n", "morpho": "n-s---fn1-"}, "pedatura2": {
        "lemma": "pedatura", "uri": "p8705", "pos": "n", "morpho": "n-s---fn1-"
    }, "pedatus1": {"lemma": "pedatus", "uri": "p8706", "pos": "a", "morpho": "aps---mn1-"}, "pedatus2": {
        "lemma": "pedatus", "uri": None, "pos": "n", "morpho": "n-s---mn4-"
    }, "pedicularius1": {"lemma": "pedicularius", "uri": "p9705", "pos": "a", "morpho": "aps---mn1-"},
    "pedicularius2": {
        "lemma": "pedicularius", "uri": "120744", "pos": "n", "morpho": "n-s---mn2-"
    }, "pediculus1": {"lemma": "pediculus", "uri": "p4329", "pos": "n", "morpho": "n-s---mn2-"}, "pediculus2": {
        "lemma": "pediculus", "uri": "p4329", "pos": "n", "morpho": "n-s---mn2-"
    }, "pedo1": {"lemma": "pedo", "uri": "p0724", "pos": "v", "morpho": "v1spia--1-"}, "pedo2": {
        "lemma": "pedo", "uri": "p0725", "pos": "v", "morpho": "v1spia--3-"
    }, "pedo3": {"lemma": "pedo", "uri": "120752", "pos": "n", "morpho": "n-s---mn3-"}, "Pedo4": {
        "lemma": "Pedo", "uri": "61403", "pos": "n", "morpho": "n-s---mn3-"
    }, "pedum1": {"lemma": "pedum", "uri": "p0730", "pos": "n", "morpho": "n-s---nn2-"}, "Pedum2": {
        "lemma": "Pedum", "uri": "61405", "pos": "n", "morpho": "n-s---nn2-"
    }, "Pegasus1": {"lemma": "Pegasus", "uri": "61406", "pos": "n", "morpho": "n-s---mn2-"}, "Pegasus2": {
        "lemma": "Pegasus", "uri": "61406", "pos": "n", "morpho": "n-s---mn2-"
    }, "Pelias1": {"lemma": "Pelias", "uri": "61412", "pos": "n", "morpho": "n-s---mn3-"}, "Pelias2": {
        "lemma": "Pelias", "uri": "61412", "pos": "n", "morpho": "n-s---mn3-"
    }, "peloris1": {"lemma": "peloris", "uri": "p0772", "pos": "n", "morpho": "n-s---fn3-"}, "Peloris2": {
        "lemma": "Peloris", "uri": "61423", "pos": "n", "morpho": "n-s---fn3-"
    }, "penitus1": {"lemma": "penitus", "uri": "p9801", "pos": "a", "morpho": "aps---mn1-"}, "penitus2": {
        "lemma": "penitus", "uri": "p9801", "pos": "a", "morpho": "aps---mn1-"
    }, "pennus1": {"lemma": "pennus", "uri": "120833", "pos": "a", "morpho": "aps---mn1-"}, "Pennus2": {
        "lemma": "Pennus", "uri": "61431", "pos": "n", "morpho": "n-s---mn2-"
    }, "Peraea1": {"lemma": "Peraea", "uri": "61438", "pos": "n", "morpho": "n-s---fn1-"}, "Peraea2": {
        "lemma": "Peraea", "uri": "61438", "pos": "n", "morpho": "n-s---fn1-"
    }, "percolo1": {"lemma": "percolo", "uri": "p0967", "pos": "v", "morpho": "v1spia--1-"}, "percolo2": {
        "lemma": "percolo", "uri": "p0966", "pos": "v", "morpho": "v1spia--3-"
    }, "perculsus1": {"lemma": "perculsus", "uri": "120985", "pos": "a", "morpho": "aps---mn1-"}, "perculsus2": {
        "lemma": "perculsus", "uri": "p0952", "pos": "n", "morpho": "n-s---mn4-"
    }, "percussus1": {"lemma": "percussus", "uri": "121002", "pos": "a", "morpho": "aps---mn1-"}, "percussus2": {
        "lemma": "percussus", "uri": "p1005", "pos": "n", "morpho": "n-s---mn4-"
    }, "perdix1": {"lemma": "perdix", "uri": "p1031", "pos": "n", "morpho": "n-s---cn3-"}, "perfectus1": {
        "lemma": "perfectus", "uri": "25866", "pos": "a", "morpho": "aps---mn1-"
    }, "perfectus2": {"lemma": "perfectus", "uri": "p9881", "pos": "n", "morpho": "n-s---mn4-"}, "perfrictio1": {
        "lemma": "perfrictio", "uri": "p4388", "pos": "n", "morpho": "n-s---fn3-"
    }, "perfrictio2": {"lemma": "perfrictio", "uri": "p4388", "pos": "n", "morpho": "n-s---fn3-"}, "Pergamum1": {
        "lemma": "Pergamum", "uri": "61441", "pos": "n", "morpho": "n-s---nn2-"
    }, "Pergamum2": {"lemma": "Pergamum", "uri": "61441", "pos": "n", "morpho": "n-s---nn2-"}, "Pergamum3": {
        "lemma": "Pergamum", "uri": "61441", "pos": "n", "morpho": "n-s---nn2-"
    }, "permissus1": {"lemma": "permissus", "uri": "121296", "pos": "a", "morpho": "aps---mn1-"}, "permissus2": {
        "lemma": "permissus", "uri": "p9884", "pos": "n", "morpho": "n-s---mn4-"
    }, "pero1": {"lemma": "pero", "uri": "p1419", "pos": "n", "morpho": "n-s---mn3-"}, "perpetuo1": {
        "lemma": "perpetuo", "uri": "25920", "pos": "r", "morpho": "rp--------"
    }, "perpetuo2": {"lemma": "perpetuo", "uri": "p1483", "pos": "v", "morpho": "v1spia--1-"}, "Persa1": {
        "lemma": "Persa", "uri": "61458", "pos": "n", "morpho": "n-s---fn1-"
    }, "Persa2": {"lemma": "Persa", "uri": "61458", "pos": "n", "morpho": "n-s---fn1-"}, "Persa3": {
        "lemma": "Persa", "uri": "61458", "pos": "n", "morpho": "n-s---fn1-"
    }, "persero1": {"lemma": "persero", "uri": "p9933", "pos": "v", "morpho": "v1spia--3-"}, "persero2": {
        "lemma": "persero", "uri": "p9933", "pos": "v", "morpho": "v1spia--3-"
    }, "Perseus1": {"lemma": "Perseus", "uri": "61463", "pos": "n", "morpho": "n-s---mn2-"}, "Perseus2": {
        "lemma": "Perseus", "uri": "61463", "pos": "n", "morpho": "n-s---mn2-"
    }, "Persicus1": {"lemma": "Persicus", "uri": "25930", "pos": "a", "morpho": "aps---mn1-"}, "perspectus1": {
        "lemma": "perspectus", "uri": "41679", "pos": "a", "morpho": "aps---mn1-"
    }, "perspectus2": {"lemma": "perspectus", "uri": "121491", "pos": "n", "morpho": "n-s---mn4-"}, "persuasus1": {
        "lemma": "persuasus", "uri": "31693", "pos": "a", "morpho": "aps---mn1-"
    }, "persuasus2": {"lemma": "persuasus", "uri": "p9885", "pos": "n", "morpho": "n-s---mn4-"}, "pertractus1": {
        "lemma": "pertractus", "uri": "121541", "pos": "a", "morpho": "aps---mn1-"
    }, "pertractus2": {"lemma": "pertractus", "uri": "p1682", "pos": "n", "morpho": "n-s---mn4-"}, "pertritus1": {
        "lemma": "pertritus", "uri": "99979", "pos": "a", "morpho": "aps---mn1-"
    }, "pertritus2": {"lemma": "pertritus", "uri": "99979", "pos": "a", "morpho": "aps---mn1-"}, "pervolo1": {
        "lemma": "peruolo", "uri": "p1755", "pos": "v", "morpho": "v1spia--1-"
    }, "pervolo2": {"lemma": "peruolo", "uri": "p1756", "pos": "v", "morpho": "v1spia--3-"}, "pessulum1": {
        "lemma": "pessulum", "uri": "p1783", "pos": "n", "morpho": "n-s---nn2-"
    }, "pessulum2": {"lemma": "pessulum", "uri": "p1783", "pos": "n", "morpho": "n-s---nn2-"}, "pessum1": {
        "lemma": "pessum", "uri": "p1774", "pos": "r", "morpho": "rp--------"
    }, "pessum2": {"lemma": "pessum", "uri": "p1775", "pos": "n", "morpho": "n-s---nn2-"}, "petasunculus1": {
        "lemma": "petasunculus", "uri": "p4395", "pos": "n", "morpho": "n-s---mn2-"
    }, "petasunculus2": {"lemma": "petasunculus", "uri": "p4395", "pos": "n", "morpho": "n-s---mn2-"}, "petitus1": {
        "lemma": "petitus", "uri": "48672", "pos": "a", "morpho": "aps---mn1-"
    }, "petitus2": {"lemma": "petitus", "uri": "p1776", "pos": "n", "morpho": "n-s---mn4-"}, "petra1": {
        "lemma": "petra", "uri": "p1811", "pos": "n", "morpho": "n-s---fn1-"
    }, "Petra2": {"lemma": "Petra", "uri": "61473", "pos": "n", "morpho": "n-s---fn1-"}, "Petra3": {
        "lemma": "Petra", "uri": "61473", "pos": "n", "morpho": "n-s---fn1-"
    }, "petraeus1": {"lemma": "petraeus", "uri": "p1812", "pos": "a", "morpho": "aps---mn1-"}, "petro1": {
        "lemma": "petro", "uri": "p1819", "pos": "n", "morpho": "n-s---mn3-"
    }, "petronius1": {"lemma": "petronius", "uri": "121657", "pos": "a", "morpho": "aps---mn1-"}, "Petronius2": {
        "lemma": "Petronius", "uri": "61476", "pos": "n", "morpho": "n-s---mn2-"
    }, "peuce1": {"lemma": "peuce", "uri": "p1827", "pos": "n", "morpho": "n-s---fn1g"}, "phalangarius1": {
        "lemma": "phalangarius", "uri": "p1843", "pos": "n", "morpho": "n-s---mn2-"
    }, "phalangarius2": {"lemma": "phalangarius", "uri": "p1843", "pos": "n", "morpho": "n-s---mn2-"}, "phalaris1": {
        "lemma": "phalaris", "uri": "p1848", "pos": "n", "morpho": "n-s---fn3-"
    }, "Phalaris2": {"lemma": "Phalaris", "uri": "61492", "pos": "n", "morpho": "n-s---fn3-"}, "Phasis1": {
        "lemma": "Phasis", "uri": "61505", "pos": "n", "morpho": "n-s---fn3-"
    }, "Phasis2": {"lemma": "Phasis", "uri": "61505", "pos": "n", "morpho": "n-s---fn3-"}, "phiala1": {
        "lemma": "phiala", "uri": "p1892", "pos": "n", "morpho": "n-s---fn1-"
    }, "Phiala2": {"lemma": "Phiala", "uri": "61517", "pos": "n", "morpho": "n-s---fn1-"}, "philus1": {
        "lemma": "philus", "uri": "121758", "pos": "a", "morpho": "aps---mn1-"
    }, "Philus2": {"lemma": "Philus", "uri": "61546", "pos": "n", "morpho": "n-s---mn2-"}, "philyra1": {
        "lemma": "philyra", "uri": "p1922", "pos": "n", "morpho": "n-s---fn1-"
    }, "Philyra2": {"lemma": "Philyra", "uri": "61547", "pos": "n", "morpho": "n-s---fn1-"}, "Phlegraeus1": {
        "lemma": "Phlegraeus", "uri": "61554", "pos": "n", "morpho": "n-s---mn2-"
    }, "Phlegraeus2": {"lemma": "Phlegraeus", "uri": "61554", "pos": "n", "morpho": "n-s---mn2-"}, "phocis1": {
        "lemma": "phocis", "uri": "p1944", "pos": "n", "morpho": "n-s---fn3-"
    }, "Phocis2": {"lemma": "Phocis", "uri": "61559", "pos": "n", "morpho": "n-s---fn3-"}, "Phoenice1": {
        "lemma": "Phoenice", "uri": "61564", "pos": "a", "morpho": "aps---fn1-"
    }, "phoenice2": {"lemma": "phoenice", "uri": "p1946", "pos": "n", "morpho": "n-s---fn1g"}, "Phoenix1": {
        "lemma": "Phoenix", "uri": "61565", "pos": "n", "morpho": "n-s---mn3-"
    }, "Phoenix2": {"lemma": "Phoenix", "uri": "61565", "pos": "n", "morpho": "n-s---mn3-"}, "phoenix3": {
        "lemma": "phoenix", "uri": "p1956", "pos": "n", "morpho": "n-s---mn3-"
    }, "Phormio2": {"lemma": "Phormio", "uri": "121794", "pos": "n", "morpho": "n-s---mn3-"}, "Phryx1": {
        "lemma": "Phryx", "uri": "61575", "pos": "n", "morpho": "n-s---mn3-"
    }, "Phryx2": {"lemma": "Phryx", "uri": "61575", "pos": "n", "morpho": "n-s---mn3-"}, "phu1": {
        "lemma": "phu", "uri": "p1985", "pos": "n", "morpho": "n-s---nn--"
    }, "phu2": {"lemma": "phu", "uri": "p1985", "pos": "n", "morpho": "n-s---nn--"}, "physica1": {
        "lemma": "physica", "uri": "p0963", "pos": "n", "morpho": "n-s---fn1-"
    }, "physica2": {"lemma": "physica", "uri": "121831", "pos": "n", "morpho": "n-p---nn2-"}, "pictor1": {
        "lemma": "pictor", "uri": "p2029", "pos": "n", "morpho": "n-s---mn3-"
    }, "picus1": {"lemma": "picus", "uri": "p2034", "pos": "n", "morpho": "n-s---mn2-"}, "Picus2": {
        "lemma": "Picus", "uri": "61588", "pos": "n", "morpho": "n-s---mn2-"
    }, "pietas1": {"lemma": "pietas", "uri": "p2035", "pos": "n", "morpho": "n-s---fn3-"}, "Pietas2": {
        "lemma": "Pietas", "uri": "61591", "pos": "n", "morpho": "n-s---mn3-"
    }, "pigror1": {"lemma": "pigror", "uri": None, "pos": "v", "morpho": "v1spid--1-"}, "pigror2": {
        "lemma": "pigror", "uri": "p2054", "pos": "n", "morpho": "n-s---mn3-"
    }, "pilatus1": {"lemma": "pilatus", "uri": "p4504", "pos": "a", "morpho": "aps---mn1-"}, "pilatus2": {
        "lemma": "pilatus", "uri": "p4504", "pos": "a", "morpho": "aps---mn1-"
    }, "Pilatus3": {"lemma": "Pilatus", "uri": "61592", "pos": "n", "morpho": "n-s---mn2-"}, "pinna1": {
        "lemma": "pinna", "uri": "p4538", "pos": "n", "morpho": "n-s---fn1-"
    }, "pinna2": {"lemma": "pinna", "uri": "p4538", "pos": "n", "morpho": "n-s---fn1-"}, "pipio1": {
        "lemma": "pipio", "uri": "p2128", "pos": "v", "morpho": "v1spia--1-"
    }, "pipio2": {"lemma": "pipio", "uri": "p2128", "pos": "v", "morpho": "v1spia--1-"}, "pipio3": {
        "lemma": "pipio", "uri": "p2129", "pos": "n", "morpho": "n-s---mn3-"
    }, "pisa1": {"lemma": "pisa", "uri": "p2138", "pos": "n", "morpho": "n-s---fn1-"}, "Pisa2": {
        "lemma": "Pisa", "uri": "61603", "pos": "n", "morpho": "n-s---fn1-"
    }, "pisciculus1": {"lemma": "pisciculus", "uri": "p2148", "pos": "n", "morpho": "n-s---mn2-"}, "Pisciculus2": {
        "lemma": "Pisciculus", "uri": "61607", "pos": "n", "morpho": "n-s---mn2-"
    }, "piso2": {"lemma": "piso", "uri": "p2162", "pos": "n", "morpho": "n-s---mn3-"}, "Piso3": {
        "lemma": "Piso", "uri": "61611", "pos": "n", "morpho": "n-s---mn3-"
    }, "pithecium1": {"lemma": "pithecium", "uri": "p2188", "pos": "n", "morpho": "n-s---nn2-"}, "Pithecium2": {
        "lemma": "Pithecium", "uri": "61614", "pos": "n", "morpho": "n-s---nn2-"
    }, "placentia1": {"lemma": "placentia", "uri": "p2217", "pos": "n", "morpho": "n-s---fn1-"}, "Placentia2": {
        "lemma": "Placentia", "uri": "61617", "pos": "n", "morpho": "n-s---fn1-"
    }, "plancus1": {"lemma": "plancus", "uri": "42458", "pos": "n", "morpho": "n-s---mn2-"}, "plantarium1": {
        "lemma": "plantarium", "uri": "p2267", "pos": "n", "morpho": "n-s---nn2-"
    }, "plantarium2": {"lemma": "plantarium", "uri": "p2267", "pos": "n", "morpho": "n-s---nn2-"}, "planus1": {
        "lemma": "planus", "uri": "p2273", "pos": "a", "morpho": "aps---mn1-"
    }, "planus2": {"lemma": "planus", "uri": "p9867", "pos": "n", "morpho": "n-s---mn2-"}, "platea1": {
        "lemma": "platea", "uri": "p2291", "pos": "n", "morpho": "n-s---fn1-"
    }, "platea2": {"lemma": "platea", "uri": "p2291", "pos": "n", "morpho": "n-s---fn1-"}, "platice1": {
        "lemma": "platice", "uri": "122083", "pos": "r", "morpho": "rp--------"
    }, "platice2": {"lemma": "platice", "uri": "p2293", "pos": "n", "morpho": "n-s---fn1g"}, "plausus2": {
        "lemma": "plausus", "uri": "122103", "pos": "n", "morpho": "n-s---mn2-"
    }, "plausus3": {"lemma": "plausus", "uri": "p9887", "pos": "n", "morpho": "n-s---mn4-"}, "plautus1": {
        "lemma": "plautus", "uri": "p2294", "pos": "a", "morpho": "aps---mn1-"
    }, "Plautus2": {"lemma": "Plautus", "uri": "133193", "pos": "n", "morpho": "n-s---mn2-"}, "plecto1": {
        "lemma": "plecto", "uri": "p1977", "pos": "v", "morpho": "v1spia--3-"
    }, "plecto2": {"lemma": "plecto", "uri": "p1977", "pos": "v", "morpho": "v1spia--3-"}, "plexus1": {
        "lemma": "plexus", "uri": "44590", "pos": "a", "morpho": "aps---mn1-"
    }, "plexus2": {"lemma": "plexus", "uri": "122137", "pos": "n", "morpho": "n-s---mn4-"}, "poetice1": {
        "lemma": "poetice", "uri": "100040", "pos": "n", "morpho": "n-s---fn1g"
    }, "poetice2": {"lemma": "poetice", "uri": "45894", "pos": "r", "morpho": "rp--------"}, "polio1": {
        "lemma": "polio", "uri": "p2455", "pos": "v", "morpho": "v1spia--4-"
    }, "polio2": {"lemma": "polio", "uri": "122234", "pos": "n", "morpho": "n-s---mn3-"}, "Polio3": {
        "lemma": "Polio", "uri": "61644", "pos": "n", "morpho": "n-s---mn3-"
    }, "pollentia1": {"lemma": "pollentia", "uri": "p9840", "pos": "n", "morpho": "n-s---fn1-"}, "Pollentia2": {
        "lemma": "Pollentia", "uri": "61647", "pos": "n", "morpho": "n-s---fn1-"
    }, "pollex1": {"lemma": "pollex", "uri": "p2464", "pos": "n", "morpho": "n-s---mn3-"}, "Pollex2": {
        "lemma": "Pollex", "uri": "61648", "pos": "n", "morpho": "n-s---mn3-"
    }, "pollio1": {"lemma": "pollio", "uri": "p2475", "pos": "n", "morpho": "n-s---mn3-"}, "Pollio2": {
        "lemma": "Pollio", "uri": "61649", "pos": "n", "morpho": "n-s---mn3-"
    }, "polus1": {"lemma": "polus", "uri": "p2485", "pos": "n", "morpho": "n-s---mn2-"}, "Polus2": {
        "lemma": "Polus", "uri": "61650", "pos": "n", "morpho": "n-s---mn2-"
    }, "pons1": {"lemma": "pons", "uri": "p2563", "pos": "n", "morpho": "n-s---mn3i"}, "Pontia1": {
        "lemma": "Pontia", "uri": "61677", "pos": "n", "morpho": "n-s---fn1-"
    }, "Pontia2": {"lemma": "Pontia", "uri": "61677", "pos": "n", "morpho": "n-s---fn1-"}, "pontus1": {
        "lemma": "pontus", "uri": "p2575", "pos": "n", "morpho": "n-s---mn2-"
    }, "Pontus2": {"lemma": "Pontus", "uri": "61679", "pos": "n", "morpho": "n-s---mn2-"}, "populatio1": {
        "lemma": "populatio", "uri": "p4607", "pos": "n", "morpho": "n-s---fn3-"
    }, "populatio2": {"lemma": "populatio", "uri": "p4607", "pos": "n", "morpho": "n-s---fn3-"}, "Populonia1": {
        "lemma": "Populonia", "uri": "61682", "pos": "n", "morpho": "n-s---fn1-"
    }, "Populonia2": {"lemma": "Populonia", "uri": "61682", "pos": "n", "morpho": "n-s---fn1-"}, "populus1": {
        "lemma": "populus", "uri": "p2606", "pos": "n", "morpho": "n-s---mn2-"
    }, "populus2": {"lemma": "populus", "uri": "p2639", "pos": "n", "morpho": "n-s---fn2-"}, "porca1": {
        "lemma": "porca", "uri": "p2627", "pos": "n", "morpho": "n-s---fn1-"
    }, "porca2": {"lemma": "porca", "uri": "p2627", "pos": "n", "morpho": "n-s---fn1-"}, "porrigo1": {
        "lemma": "porrigo", "uri": "p2638", "pos": "v", "morpho": "v1spia--3-"
    }, "porrigo2": {"lemma": "porrigo", "uri": "p2640", "pos": "n", "morpho": "n-s---fn3-"}, "porthmos1": {
        "lemma": "porthmos", "uri": "p2661", "pos": "n", "morpho": "n-s---mn2g"
    }, "Porthmos2": {"lemma": "Porthmos", "uri": "61687", "pos": "n", "morpho": "n-s---mn2-"}, "portitor1": {
        "lemma": "portitor", "uri": "p2668", "pos": "n", "morpho": "n-s---mn3-"
    }, "portitor2": {"lemma": "portitor", "uri": "p2668", "pos": "n", "morpho": "n-s---mn3-"}, "posca1": {
        "lemma": "posca", "uri": "p2678", "pos": "n", "morpho": "n-s---fn1-"
    }, "Posca2": {"lemma": "Posca", "uri": "61689", "pos": "n", "morpho": "n-s---fn1-"}, "positus1": {
        "lemma": "positus", "uri": "122428", "pos": "a", "morpho": "aps---mn1-"
    }, "positus2": {"lemma": "positus", "uri": "p9890", "pos": "n", "morpho": "n-s---mn4-"}, "possessus1": {
        "lemma": "possessus", "uri": "122431", "pos": "a", "morpho": "aps---mn1-"
    }, "possessus2": {"lemma": "possessus", "uri": "p2699", "pos": "n", "morpho": "n-s---mn4-"}, "postumus1": {
        "lemma": "postumus", "uri": "p2752", "pos": "a", "morpho": "aps---mn1-"
    }, "Postumus2": {"lemma": "Postumus", "uri": "61694", "pos": "n", "morpho": "n-s---mn2-"}, "potentia1": {
        "lemma": "potentia", "uri": "p2698", "pos": "n", "morpho": "n-s---fn1-"
    }, "Potentia2": {"lemma": "Potentia", "uri": "61696", "pos": "n", "morpho": "n-s---fn1-"}, "potio1": {
        "lemma": "potio", "uri": "p2773", "pos": "n", "morpho": "n-s---fn3-"
    }, "potio2": {"lemma": "potio", "uri": "p2774", "pos": "v", "morpho": "v1spia--4-"}, "potior1": {
        "lemma": "potior", "uri": "p2776", "pos": "v", "morpho": "v1spid--4-"
    }, "potior2": {"lemma": "potior", "uri": "32717", "pos": "a", "morpho": "aps---cn3-"}, "potitus2": {
        "lemma": "potitus", "uri": "122507", "pos": "a", "morpho": "aps---mn1-"
    }, "Potitus3": {"lemma": "Potitus", "uri": "61699", "pos": "n", "morpho": "n-s---mn2-"}, "potus1": {
        "lemma": "potus", "uri": "122509", "pos": "a", "morpho": "aps---mn1-"
    }, "potus2": {"lemma": "potus", "uri": "p9930", "pos": "n", "morpho": "n-s---mn4-"}, "praecia1": {
        "lemma": "praecia", "uri": "p3474", "pos": "n", "morpho": "n-s---mn1-"
    }, "praecia2": {"lemma": "praecia", "uri": "p3474", "pos": "n", "morpho": "n-s---mn1-"}, "praecinctus1": {
        "lemma": "praecinctus", "uri": "100077", "pos": "a", "morpho": "aps---mn1-"
    }, "praecinctus2": {"lemma": "praecinctus", "uri": "p9893", "pos": "n", "morpho": "n-s---mn4-"}, "praecursus1": {
        "lemma": "praecursus", "uri": "122624", "pos": "a", "morpho": "aps---mn1-"
    }, "praecursus2": {"lemma": "praecursus", "uri": "p9895", "pos": "n", "morpho": "n-s---mn4-"}, "praedatus1": {
        "lemma": "praedatus", "uri": "p2907", "pos": "a", "morpho": "aps---mn1-"
    }, "praedatus2": {"lemma": "praedatus", "uri": "p2907", "pos": "a", "morpho": "aps---mn1-"}, "praedico1": {
        "lemma": "praedico", "uri": "p2928", "pos": "v", "morpho": "v1spia--1-"
    }, "praedico2": {"lemma": "praedico", "uri": "p2929", "pos": "v", "morpho": "v1spia--3-"}, "praedo1": {
        "lemma": "praedo", "uri": "26206", "pos": "v", "morpho": "v1spia--1-"
    }, "praedo2": {"lemma": "praedo", "uri": "p2946", "pos": "n", "morpho": "n-s---mn3-"}, "praefatus1": {
        "lemma": "praefatus", "uri": "122685", "pos": "a", "morpho": "aps---mn1-"
    }, "praefatus2": {"lemma": "praefatus", "uri": "p9897", "pos": "n", "morpho": "n-s---mn4-"}, "praefectus1": {
        "lemma": "praefectus", "uri": "122691", "pos": "a", "morpho": "aps---mn1-"
    }, "praefectus2": {"lemma": "praefectus", "uri": "122691", "pos": "a", "morpho": "aps---mn1-"}, "praefectus3": {
        "lemma": "praefectus", "uri": "p9943", "pos": "n", "morpho": "n-s---mn2-"
    }, "praegressus1": {"lemma": "praegressus", "uri": "122743", "pos": "a", "morpho": "aps---mn1-"}, "praegressus2": {
        "lemma": "praegressus", "uri": "p9898", "pos": "n", "morpho": "n-s---mn4-"
    }, "praelego1": {"lemma": "praelego", "uri": "p3068", "pos": "v", "morpho": "v1spia--1-"}, "praelego2": {
        "lemma": "praelego", "uri": "p3069", "pos": "v", "morpho": "v1spia--3-"
    }, "praemando1": {"lemma": "praemando", "uri": "p3096", "pos": "v", "morpho": "v1spia--1-"}, "praemando2": {
        "lemma": "praemando", "uri": "p3097", "pos": "v", "morpho": "v1spia--3-"
    }, "praemonitus1": {"lemma": "praemonitus", "uri": "122856", "pos": "a", "morpho": "aps---mn1-"}, "praemonitus2": {
        "lemma": "praemonitus", "uri": "p9899", "pos": "n", "morpho": "n-s---mn4-"
    }, "praeparatus1": {"lemma": "praeparatus", "uri": "54200", "pos": "a", "morpho": "aps---mn1-"}, "praeparatus2": {
        "lemma": "praeparatus", "uri": "p9900", "pos": "n", "morpho": "n-s---mn4-"
    }, "praepositus1": {"lemma": "praepositus", "uri": "122922", "pos": "a", "morpho": "aps---mn1-"}, "praepositus2": {
        "lemma": "praepositus", "uri": "p9956", "pos": "n", "morpho": "n-s---mn2-"
    }, "praes1": {"lemma": "praes", "uri": "p3245", "pos": "n", "morpho": "n-s---mn3-"}, "praes2": {
        "lemma": "praes", "uri": "p3246", "pos": "r", "morpho": "rp--------"
    }, "praescriptus1": {"lemma": "praescriptus", "uri": "122976", "pos": "a", "morpho": "aps---mn1-"},
    "praescriptus2": {
        "lemma": "praescriptus", "uri": "p9903", "pos": "n", "morpho": "n-s---mn4-"
    }, "praesentia1": {"lemma": "praesentia", "uri": "p9852", "pos": "n", "morpho": "n-p---nn3i"}, "praesentia2": {
        "lemma": "praesentia", "uri": "p9852", "pos": "n", "morpho": "n-p---nn3i"
    }, "praesto2": {"lemma": "praesto", "uri": "p3327", "pos": "v", "morpho": "v1spia--1-"}, "praetextus1": {
        "lemma": "praetextus", "uri": "44379", "pos": "a", "morpho": "aps---mn1-"
    }, "praetextus2": {"lemma": "praetextus", "uri": "p3424", "pos": "n", "morpho": "n-s---mn4-"}, "praetorianus1": {
        "lemma": "praetorianus", "uri": "p4683", "pos": "a", "morpho": "aps---mn1-"
    }, "praetorianus2": {"lemma": "praetorianus", "uri": "p4683", "pos": "a", "morpho": "aps---mn1-"}, "praeventus1": {
        "lemma": "praeuentus", "uri": "123142", "pos": "a", "morpho": "aps---mn1-"
    }, "praeventus2": {"lemma": "praeuentus", "uri": "p3426", "pos": "n", "morpho": "n-s---mn4-"}, "precarium1": {
        "lemma": "precarium", "uri": "123194", "pos": "n", "morpho": "n-s---nn2-"
    }, "precarium2": {"lemma": "precarium", "uri": "123194", "pos": "n", "morpho": "n-s---nn2-"}, "pressus1": {
        "lemma": "pressus", "uri": "49546", "pos": "a", "morpho": "aps---mn1-"
    }, "pressus2": {"lemma": "pressus", "uri": "p9907", "pos": "n", "morpho": "n-s---mn4-"}, "Priapus1": {
        "lemma": "Priapus", "uri": "61714", "pos": "n", "morpho": "n-s---mn2-"
    }, "Priapus2": {"lemma": "Priapus", "uri": "61714", "pos": "n", "morpho": "n-s---mn2-"}, "princeps1": {
        "lemma": "princeps", "uri": "p3563", "pos": "a", "morpho": "aps---an3-"
    }, "priscus1": {"lemma": "priscus", "uri": "p3576", "pos": "a", "morpho": "aps---mn1-"}, "Priscus2": {
        "lemma": "Priscus", "uri": "61716", "pos": "n", "morpho": "n-s---mn2-"
    }, "pristinus1": {"lemma": "pristinus", "uri": "p4685", "pos": "a", "morpho": "aps---mn1-"}, "pristinus2": {
        "lemma": "pristinus", "uri": "p4685", "pos": "a", "morpho": "aps---mn1-"
    }, "pro1": {"lemma": "pro", "uri": "p2610", "pos": "p", "morpho": "p---------"}, "pro2": {
        "lemma": "pro", "uri": "p2610", "pos": "p", "morpho": "p---------"
    }, "probus1": {"lemma": "probus", "uri": "p3631", "pos": "a", "morpho": "aps---mn1-"}, "Probus2": {
        "lemma": "Probus", "uri": "61718", "pos": "n", "morpho": "n-s---mn2-"
    }, "processus1": {"lemma": "processus", "uri": "123318", "pos": "a", "morpho": "aps---mn1-"}, "processus2": {
        "lemma": "processus", "uri": "p9908", "pos": "n", "morpho": "n-s---mn4-"
    }, "procidentia1": {"lemma": "procidentia", "uri": "p9856", "pos": "n", "morpho": "n-p---nn3i"}, "procidentia2": {
        "lemma": "procidentia", "uri": "p9856", "pos": "n", "morpho": "n-p---nn3i"
    }, "procido1": {"lemma": "procido", "uri": "p3652", "pos": "v", "morpho": "v1spia--3-"}, "procido2": {
        "lemma": "procido", "uri": "p3652", "pos": "v", "morpho": "v1spia--3-"
    }, "procinctus1": {"lemma": "procinctus", "uri": "100168", "pos": "a", "morpho": "aps---mn1-"}, "procinctus2": {
        "lemma": "procinctus", "uri": "p9909", "pos": "n", "morpho": "n-s---mn4-"
    }, "procus1": {"lemma": "procus", "uri": "p4686", "pos": "n", "morpho": "n-s---mn2-"}, "procus2": {
        "lemma": "procus", "uri": "p4686", "pos": "n", "morpho": "n-s---mn2-"
    }, "prodicius1": {"lemma": "prodicius", "uri": "123352", "pos": "a", "morpho": "aps---mn1-"}, "proditio1": {
        "lemma": "proditio", "uri": "p4687", "pos": "n", "morpho": "n-s---fn3-"
    }, "proditio2": {"lemma": "proditio", "uri": "p4687", "pos": "n", "morpho": "n-s---fn3-"}, "proditus1": {
        "lemma": "proditus", "uri": "123367", "pos": "a", "morpho": "aps---mn1-"
    }, "proditus2": {"lemma": "proditus", "uri": "123368", "pos": "n", "morpho": "n-s---mn4-"}, "profano1": {
        "lemma": "profano", "uri": "p4688", "pos": "v", "morpho": "v1spia--1-"
    }, "profano2": {"lemma": "profano", "uri": "p4688", "pos": "v", "morpho": "v1spia--1-"}, "profectus1": {
        "lemma": "profectus", "uri": "123398", "pos": "a", "morpho": "aps---mn1-"
    }, "profectus2": {"lemma": "profectus", "uri": "123398", "pos": "a", "morpho": "aps---mn1-"}, "profectus3": {
        "lemma": "profectus", "uri": "p9911", "pos": "n", "morpho": "n-s---mn4-"
    }, "profligo1": {"lemma": "profligo", "uri": "p3771", "pos": "v", "morpho": "v1spia--1-"}, "profligo2": {
        "lemma": "profligo", "uri": "p3772", "pos": "v", "morpho": "v1spia--3-"
    }, "progressus1": {"lemma": "progressus", "uri": "100185", "pos": "a", "morpho": "aps---mn1-"}, "progressus2": {
        "lemma": "progressus", "uri": "p9913", "pos": "n", "morpho": "n-s---mn4-"
    }, "projectus1": {"lemma": "proiectus", "uri": "53242", "pos": "a", "morpho": "aps---mn1-"}, "projectus2": {
        "lemma": "proiectus", "uri": "p9914", "pos": "n", "morpho": "n-s---mn4-"
    }, "prolapsus1": {"lemma": "prolapsus", "uri": "123450", "pos": "a", "morpho": "aps---mn1-"}, "prolapsus2": {
        "lemma": "prolapsus", "uri": "p9915", "pos": "n", "morpho": "n-s---mn4-"
    }, "prolatus1": {"lemma": "prolatus", "uri": "123456", "pos": "a", "morpho": "aps---mn1-"}, "prolatus2": {
        "lemma": "prolatus", "uri": "p9916", "pos": "n", "morpho": "n-s---mn4-"
    }, "promissus1": {"lemma": "promissus", "uri": "31796", "pos": "a", "morpho": "aps---mn1-"}, "promissus2": {
        "lemma": "promissus", "uri": "p3896", "pos": "n", "morpho": "n-s---mn4-"
    }, "promotus1": {"lemma": "promotus", "uri": "123512", "pos": "a", "morpho": "aps---mn1-"}, "promotus2": {
        "lemma": "promotus", "uri": "p9917", "pos": "n", "morpho": "n-s---mn4-"
    }, "promptus1": {"lemma": "promptus", "uri": "26396", "pos": "a", "morpho": "aps---mn1-"}, "promptus2": {
        "lemma": "promptus", "uri": "p9918", "pos": "n", "morpho": "n-s---mn4-"
    }, "pronatus1": {"lemma": "pronatus", "uri": "123532", "pos": "a", "morpho": "aps---mn1-"}, "pronatus2": {
        "lemma": "pronatus", "uri": "123532", "pos": "a", "morpho": "aps---mn1-"
    }, "propago1": {"lemma": "propago", "uri": "p3945", "pos": "v", "morpho": "v1spia--1-"}, "propudium1": {
        "lemma": "propudium", "uri": "p4690", "pos": "n", "morpho": "n-s---nn2-"
    }, "propudium2": {"lemma": "propudium", "uri": "p4690", "pos": "n", "morpho": "n-s---nn2-"}, "propulsus1": {
        "lemma": "propulsus", "uri": "123629", "pos": "a", "morpho": "aps---mn1-"
    }, "propulsus2": {"lemma": "propulsus", "uri": "p9921", "pos": "n", "morpho": "n-s---mn4-"}, "prorsus1": {
        "lemma": "prorsus", "uri": "26437", "pos": "r", "morpho": "rp--------"
    }, "prorsus2": {"lemma": "prorsus", "uri": "p4049", "pos": "a", "morpho": "aps---mn1-"}, "prosectus1": {
        "lemma": "prosectus", "uri": "123673", "pos": "a", "morpho": "aps---mn1-"
    }, "prosectus2": {"lemma": "prosectus", "uri": "p4063", "pos": "n", "morpho": "n-s---mn4-"}, "prosero1": {
        "lemma": "prosero", "uri": "p4100", "pos": "v", "morpho": "v1spia--3-"
    }, "prosero2": {"lemma": "prosero", "uri": "p4100", "pos": "v", "morpho": "v1spia--3-"}, "prospectus1": {
        "lemma": "prospectus", "uri": "123710", "pos": "a", "morpho": "aps---mn1-"
    }, "prospectus2": {"lemma": "prospectus", "uri": "p9922", "pos": "n", "morpho": "n-s---mn4-"}, "prosum1": {
        "lemma": "prosum", "uri": "p4150", "pos": "v", "morpho": "v1spia--4-"
    }, "protectus1": {"lemma": "protectus", "uri": "123751", "pos": "a", "morpho": "aps---mn1-"}, "protectus2": {
        "lemma": "protectus", "uri": "p9923", "pos": "n", "morpho": "n-s---mn4-"
    }, "protractus1": {"lemma": "protractus", "uri": "123791", "pos": "a", "morpho": "aps---mn1-"}, "protractus2": {
        "lemma": "protractus", "uri": "p9924", "pos": "n", "morpho": "n-s---mn4-"
    }, "provectus1": {"lemma": "prouectus", "uri": "26473", "pos": "a", "morpho": "aps---mn1-"}, "provectus2": {
        "lemma": "prouectus", "uri": "p9925", "pos": "n", "morpho": "n-s---mn4-"
    }, "proviso1": {"lemma": "prouiso", "uri": "123814", "pos": "r", "morpho": "rp--------"}, "proviso2": {
        "lemma": "prouiso", "uri": "p4221", "pos": "v", "morpho": "v1spia--3-"
    }, "provisus1": {"lemma": "prouisus", "uri": "123815", "pos": "a", "morpho": "aps---mn1-"}, "provisus2": {
        "lemma": "prouisus", "uri": "p9927", "pos": "n", "morpho": "n-s---mn4-"
    }, "proximo1": {"lemma": "proximo", "uri": "123831", "pos": "r", "morpho": "rp--------"}, "proximo2": {
        "lemma": "proximo", "uri": "p4244", "pos": "v", "morpho": "v1spia--1-"
    }, "psecas1": {"lemma": "psecas", "uri": "p4279", "pos": "n", "morpho": "n-s---fn3-"}, "Psecas2": {
        "lemma": "Psecas", "uri": "61748", "pos": "n", "morpho": "n-s---mn3-"
    }, "pubes1": {"lemma": "pubes", "uri": "54925", "pos": "a", "morpho": "aps---an3-"}, "pubes2": {
        "lemma": "pubes", "uri": "p4368", "pos": "n", "morpho": "n-s---fn3i"
    }, "pulcher1": {"lemma": "pulcher", "uri": "p4435", "pos": "a", "morpho": "aps---mn1r"}, "Pulcher2": {
        "lemma": "Pulcher", "uri": "61770", "pos": "n", "morpho": "n-s---mn2r"
    }, "pullulus1": {"lemma": "pullulus", "uri": "p4463", "pos": "n", "morpho": "n-s---mn2-"}, "pullulus2": {
        "lemma": "pullulus", "uri": "p5463", "pos": "a", "morpho": "aps---mn1-"
    }, "pullus1": {"lemma": "pullus", "uri": "p4464", "pos": "n", "morpho": "n-s---mn2-"}, "pullus2": {
        "lemma": "pullus", "uri": "p4691", "pos": "a", "morpho": "aps---mn1-"
    }, "pullus3": {"lemma": "pullus", "uri": "p4691", "pos": "a", "morpho": "aps---mn1-"}, "pulsus1": {
        "lemma": "pulsus", "uri": "124044", "pos": "a", "morpho": "aps---mn1-"
    }, "pulsus2": {"lemma": "pulsus", "uri": "p0758", "pos": "n", "morpho": "n-s---mn4-"}, "pulto1": {
        "lemma": "pulto", "uri": "p4494", "pos": "v", "morpho": "v1spia--1-"
    }, "punctus1": {"lemma": "punctus", "uri": "100245", "pos": "a", "morpho": "aps---mn1-"}, "punctus2": {
        "lemma": "punctus", "uri": "p9871", "pos": "n", "morpho": "n-s---mn4-"
    }, "purgatus1": {"lemma": "purgatus", "uri": "38630", "pos": "a", "morpho": "aps---mn1-"}, "purgatus2": {
        "lemma": "purgatus", "uri": "38630", "pos": "a", "morpho": "aps---mn1-"
    }, "puritas1": {"lemma": "puritas", "uri": "p4693", "pos": "n", "morpho": "n-s---fn3-"}, "puritas2": {
        "lemma": "puritas", "uri": "p4693", "pos": "n", "morpho": "n-s---fn3-"
    }, "puta1": {"lemma": "puta", "uri": "56829", "pos": "r", "morpho": "rp--------"}, "putus1": {
        "lemma": "putus", "uri": "p4629", "pos": "a", "morpho": "aps---mn1-"
    }, "putus2": {"lemma": "putus", "uri": "p4630", "pos": "n", "morpho": "n-s---mn2-"}, "Pyramus1": {
        "lemma": "Pyramus", "uri": "61786", "pos": "n", "morpho": "n-s---mn2-"
    }, "Pyramus2": {"lemma": "Pyramus", "uri": "61786", "pos": "n", "morpho": "n-s---mn2-"}, "pyrgus1": {
        "lemma": "pyrgus", "uri": "p4652", "pos": "n", "morpho": "n-s---mn2-"
    }, "Pyrgus2": {"lemma": "Pyrgus", "uri": "61792", "pos": "n", "morpho": "n-s---mn2-"}, "Pyrrhias1": {
        "lemma": "Pyrrhias", "uri": "61798", "pos": "n", "morpho": "n-s---mn3-"
    }, "Pyrrhias2": {"lemma": "Pyrrhias", "uri": "61798", "pos": "n", "morpho": "n-s---mn3-"}, "Pytho1": {
        "lemma": "Pytho", "uri": "61805", "pos": "n", "morpho": "n-s---mn3-"
    }, "Pytho2": {"lemma": "Pytho", "uri": "61805", "pos": "n", "morpho": "n-s---mn3-"}, "Pytho3": {
        "lemma": "Pytho", "uri": "61805", "pos": "n", "morpho": "n-s---mn3-"
    }, "quadra1": {"lemma": "quadra", "uri": "q0004", "pos": "n", "morpho": "n-s---fn1-"}, "quadratus1": {
        "lemma": "quadratus", "uri": "58105", "pos": "a", "morpho": "aps---mn1-"
    }, "quadratus2": {"lemma": "quadratus", "uri": "q9330", "pos": "n", "morpho": "n-s---mn2-"}, "Quadratus3": {
        "lemma": "Quadratus", "uri": "61808", "pos": "n", "morpho": "n-s---mn2-"
    }, "quadrigarius1": {"lemma": "quadrigarius", "uri": "q0043", "pos": "a", "morpho": "aps---mn1-"},
    "Quadrigarius2": {
        "lemma": "Quadrigarius", "uri": "61810", "pos": "n", "morpho": "n-s---mn2-"
    }, "quadruplator1": {"lemma": "quadruplator", "uri": "q0085", "pos": "n", "morpho": "n-s---mn3-"},
    "quadruplator2": {
        "lemma": "quadruplator", "uri": "q0085", "pos": "n", "morpho": "n-s---mn3-"
    }, "quaesitus1": {"lemma": "quaesitus", "uri": "26578", "pos": "a", "morpho": "aps---mn1-"}, "quaesitus2": {
        "lemma": "quaesitus", "uri": "q9327", "pos": "n", "morpho": "n-s---mn4-"
    }, "quam1": {"lemma": "quam", "uri": "26584", "pos": "r", "morpho": "rp--------"},
    "quam2": {"lemma": "quam", "uri": "26584", "pos": "r", "morpho": "rp--------"},
    "quam3": {"lemma": "quam", "uri": "26584", "pos": "r", "morpho": "rp--------"},
    "quam4": {"lemma": "quam", "uri": "26584", "pos": "r", "morpho": "rp--------"},
    "quandoque1": {"lemma": "quandoque", "uri": "q0139", "pos": "r", "morpho": "rp--------"}, "quandoque2": {
        "lemma": "quandoque", "uri": "q0139", "pos": "r", "morpho": "rp--------"
    }, "quassus1": {"lemma": "quassus", "uri": "40492", "pos": "a", "morpho": "aps---mn1-"}, "quassus2": {
        "lemma": "quassus", "uri": "q9328", "pos": "n", "morpho": "n-s---mn4-"
    }, "questus1": {"lemma": "questus", "uri": "124370", "pos": "a", "morpho": "aps---mn1-"}, "questus2": {
        "lemma": "questus", "uri": "q9329", "pos": "n", "morpho": "n-s---mn4-"
    }, "quies1": {"lemma": "quies", "uri": "q0205", "pos": "n", "morpho": "n-s---fn3-"}, "quies2": {
        "lemma": "quies", "uri": "q0205", "pos": "n", "morpho": "n-s---fn3-"
    }, "quinque1": {"lemma": "quinque", "uri": "q0251", "pos": "a", "morpho": "aps---an--"}, "quinque2": {
        "lemma": "quinque", "uri": "q0251", "pos": "a", "morpho": "aps---an--"
    }, "Quintilianus1": {"lemma": "Quintilianus", "uri": "61812", "pos": "n", "morpho": "n-s---mn2-"},
    "Quintilianus2": {
        "lemma": "Quintilianus", "uri": "61812", "pos": "n", "morpho": "n-s---mn2-"
    }, "quintus1": {"lemma": "quintus", "uri": "q0144", "pos": "a", "morpho": "aps---mn1-"}, "Quintus2": {
        "lemma": "Quintus", "uri": "61816", "pos": "n", "morpho": "n-s---mn2-"
    }, "Quirinus1": {"lemma": "Quirinus", "uri": "61818", "pos": "n", "morpho": "n-s---mn2-"}, "Quirinus2": {
        "lemma": "Quirinus", "uri": "61818", "pos": "n", "morpho": "n-s---mn2-"
    }, "Quiris2": {"lemma": "Quiris", "uri": "52554", "pos": "n", "morpho": "n-s---fn3-"}, "quod1": {
        "lemma": "quod", "uri": "56475", "pos": "r", "morpho": "rp--------"
    }, "quo1": {"lemma": "quo", "uri": "33941", "pos": "r", "morpho": "rp--------"},
"quo2": {"lemma": "quo", "uri": "33941", "pos": "r", "morpho": "rp--------"},
"quo3": {"lemma": "quo", "uri": "33941", "pos": "r", "morpho": "rp--------"},
    "quod2": {"lemma": "quod", "uri": "56475", "pos": "r", "morpho": "rp--------"}, "quojus1": {
        "lemma": "quoius", "uri": "29469", "pos": "a", "morpho": "aps---mn1-"
    }, "quojus2": {"lemma": "quoius", "uri": "29469", "pos": "a", "morpho": "aps---mn1-"}, "quoque1": {
        "lemma": "quoque", "uri": "26601", "pos": "r", "morpho": "rp--------"
    }, "quoque2": {"lemma": "quoque", "uri": "26601", "pos": "r", "morpho": "rp--------"}, "rabo1": {
        "lemma": "rabo", "uri": "100314", "pos": "v", "morpho": "v1spia--3-"
    }, "rabo2": {"lemma": "rabo", "uri": "124486", "pos": "n", "morpho": "n-s---mn3-"}, "raptus1": {
        "lemma": "raptus", "uri": "124549", "pos": "a", "morpho": "aps---mn1-"
    }, "raptus2": {"lemma": "raptus", "uri": "r0957", "pos": "n", "morpho": "n-s---mn4-"}, "rasus1": {
        "lemma": "rasus", "uri": "124566", "pos": "a", "morpho": "aps---mn1-"
    }, "rasus2": {"lemma": "rasus", "uri": "r7013", "pos": "n", "morpho": "n-s---mn4-"}, "ravus1": {
        "lemma": "rauus", "uri": "r0398", "pos": "a", "morpho": "aps---mn1-"
    }, "ravus2": {"lemma": "rauus", "uri": "r0398", "pos": "a", "morpho": "aps---mn1-"}, "rebellio1": {
        "lemma": "rebellio", "uri": "r0132", "pos": "n", "morpho": "n-s---fn3-"
    }, "rebellio2": {"lemma": "rebellio", "uri": "r0437", "pos": "n", "morpho": "n-s---mn3-"}, "recensus1": {
        "lemma": "recensus", "uri": "124644", "pos": "a", "morpho": "aps---mn1-"
    }, "recensus2": {"lemma": "recensus", "uri": "r7015", "pos": "n", "morpho": "n-s---mn4-"}, "receptus1": {
        "lemma": "receptus", "uri": "100338", "pos": "a", "morpho": "aps---mn1-"
    }, "receptus2": {"lemma": "receptus", "uri": "r7016", "pos": "n", "morpho": "n-s---mn4-"}, "recessus1": {
        "lemma": "recessus", "uri": "124660", "pos": "a", "morpho": "aps---mn1-"
    }, "recessus2": {"lemma": "recessus", "uri": "r7012", "pos": "n", "morpho": "n-s---mn4-"}, "recolo1": {
        "lemma": "recolo", "uri": "r1025", "pos": "v", "morpho": "v1spia--3-"
    }, "recolo2": {"lemma": "recolo", "uri": "r1024", "pos": "v", "morpho": "v1spia--1-"}, "recussus1": {
        "lemma": "recussus", "uri": "47755", "pos": "a", "morpho": "aps---mn1-"
    }, "recussus2": {"lemma": "recussus", "uri": "r7020", "pos": "n", "morpho": "n-s---mn4-"}, "redactus1": {
        "lemma": "redactus", "uri": "124762", "pos": "a", "morpho": "aps---mn1-"
    }, "redactus2": {"lemma": "redactus", "uri": "r7021", "pos": "n", "morpho": "n-s---mn4-"}, "refectus2": {
        "lemma": "refectus", "uri": "r7024", "pos": "n", "morpho": "n-s---mn4-"
    }, "reflexus1": {"lemma": "reflexus", "uri": "124845", "pos": "a", "morpho": "aps---mn1-"}, "reflexus2": {
        "lemma": "reflexus", "uri": "r7025", "pos": "n", "morpho": "n-s---mn4-"
    }, "regillus1": {"lemma": "regillus", "uri": "r0302", "pos": "a", "morpho": "aps---mn1-"}, "Regillus2": {
        "lemma": "Regillus", "uri": "61830", "pos": "a", "morpho": "aps---mn1-"
    }, "regressus1": {"lemma": "regressus", "uri": "124921", "pos": "a", "morpho": "aps---mn1-"}, "regressus2": {
        "lemma": "regressus", "uri": "r7030", "pos": "n", "morpho": "n-s---mn4-"
    }, "regulus1": {"lemma": "regulus", "uri": "r0320", "pos": "n", "morpho": "n-s---mn2-"}, "Regulus2": {
        "lemma": "Regulus", "uri": "61832", "pos": "n", "morpho": "n-s---mn2-"
    }, "rejectus1": {"lemma": "reiectus", "uri": "124930", "pos": "a", "morpho": "aps---mn1-"}, "rejectus2": {
        "lemma": "reiectus", "uri": "r7031", "pos": "n", "morpho": "n-s---mn4-"
    }, "relatus1": {"lemma": "relatus", "uri": "124946", "pos": "a", "morpho": "aps---mn1-"}, "relatus2": {
        "lemma": "relatus", "uri": "r7032", "pos": "n", "morpho": "n-s---mn4-"
    }, "relego1": {"lemma": "relego", "uri": "r1171", "pos": "v", "morpho": "v1spia--1-"}, "relego2": {
        "lemma": "relego", "uri": "r1172", "pos": "v", "morpho": "v1spia--3-"
    }, "relictus1": {"lemma": "relictus", "uri": "58076", "pos": "a", "morpho": "aps---mn1-"}, "relictus2": {
        "lemma": "relictus", "uri": "r7033", "pos": "n", "morpho": "n-s---mn4-"
    }, "remando1": {"lemma": "remando", "uri": "r1195", "pos": "v", "morpho": "v1spia--1-"}, "remando2": {
        "lemma": "remando", "uri": "r1196", "pos": "v", "morpho": "v1spia--3-"
    }, "remano1": {"lemma": "remano", "uri": "r1198", "pos": "v", "morpho": "v1spia--1-"}, "remano2": {
        "lemma": "remano", "uri": "r1198", "pos": "v", "morpho": "v1spia--1-"
    }, "remora1": {"lemma": "remora", "uri": "r0382", "pos": "n", "morpho": "n-s---fn1-"}, "remulus1": {
        "lemma": "remulus", "uri": "r0390", "pos": "n", "morpho": "n-s---mn2-"
    }, "Remulus2": {"lemma": "Remulus", "uri": "61833", "pos": "n", "morpho": "n-s---mn2-"}, "remus1": {
        "lemma": "remus", "uri": "r0394", "pos": "n", "morpho": "n-s---mn2-"
    }, "Remus2": {"lemma": "Remus", "uri": "61834", "pos": "n", "morpho": "n-s---mn2-"}, "Remus3": {
        "lemma": "Remus", "uri": "61834", "pos": "n", "morpho": "n-s---mn2-"
    }, "repens2": {"lemma": "repens", "uri": "r7054", "pos": "a", "morpho": "aps---an3i"}, "repens3": {
        "lemma": "repens", "uri": "125094", "pos": "r", "morpho": "rp--------"
    }, "repercussus1": {"lemma": "repercussus", "uri": "125106", "pos": "a", "morpho": "aps---mn1-"}, "repercussus2": {
        "lemma": "repercussus", "uri": "r7036", "pos": "n", "morpho": "n-s---mn4-"
    }, "repertus1": {"lemma": "repertus", "uri": "125111", "pos": "a", "morpho": "aps---mn1-"}, "repertus2": {
        "lemma": "repertus", "uri": "r7037", "pos": "n", "morpho": "n-s---mn4-"
    }, "reposco1": {"lemma": "reposco", "uri": "r1292", "pos": "v", "morpho": "v1spia--3-"}, "reposco2": {
        "lemma": "reposco", "uri": "r0450", "pos": "n", "morpho": "n-s---mn3-"
    }, "repugnantia1": {"lemma": "repugnantia", "uri": "r9995", "pos": "n", "morpho": "n-p---nn3i"}, "repugnantia2": {
        "lemma": "repugnantia", "uri": "r9995", "pos": "n", "morpho": "n-p---nn3i"
    }, "repulsus1": {"lemma": "repulsus", "uri": "100395", "pos": "a", "morpho": "aps---mn1-"}, "repulsus2": {
        "lemma": "repulsus", "uri": "r7010", "pos": "n", "morpho": "n-s---mn4-"
    }, "resero1": {"lemma": "resero", "uri": "r1332", "pos": "v", "morpho": "v1spia--3-"}, "resero2": {
        "lemma": "resero", "uri": "r1333", "pos": "v", "morpho": "v1spia--1-"
    }, "resonus1": {"lemma": "resonus", "uri": "r0529", "pos": "a", "morpho": "aps---mn1-"}, "resonus2": {
        "lemma": "resonus", "uri": "125256", "pos": "n", "morpho": "n-s---mn4-"
    }, "respectus1": {"lemma": "respectus", "uri": "125260", "pos": "a", "morpho": "aps---mn1-"}, "respectus2": {
        "lemma": "respectus", "uri": "r7039", "pos": "n", "morpho": "n-s---mn4-"
    }, "respergo1": {"lemma": "respergo", "uri": "r1348", "pos": "v", "morpho": "v1spia--3-"}, "respergo2": {
        "lemma": "respergo", "uri": "r0531", "pos": "n", "morpho": "n-s---fn3-"
    }, "respersus1": {"lemma": "respersus", "uri": "125262", "pos": "a", "morpho": "aps---mn1-"}, "respersus2": {
        "lemma": "respersus", "uri": "r7040", "pos": "n", "morpho": "n-s---mn4-"
    }, "responsus1": {"lemma": "responsus", "uri": "125274", "pos": "a", "morpho": "aps---mn1-"}, "responsus2": {
        "lemma": "responsus", "uri": "r7042", "pos": "n", "morpho": "n-s---mn4-"
    }, "restitutus1": {"lemma": "restitutus", "uri": "125292", "pos": "a", "morpho": "aps---mn1-"}, "Restitutus2": {
        "lemma": "Restitutus", "uri": "61835", "pos": "n", "morpho": "n-s---mn2-"
    }, "retento1": {"lemma": "retento", "uri": "r1506", "pos": "v", "morpho": "v1spia--1-"}, "retento2": {
        "lemma": "retento", "uri": "r1506", "pos": "v", "morpho": "v1spia--1-"
    }, "retentus1": {"lemma": "retentus", "uri": "125328", "pos": "a", "morpho": "aps---mn1-"}, "retentus2": {
        "lemma": "retentus", "uri": "r7043", "pos": "n", "morpho": "n-s---mn4-"
    }, "retractatus1": {"lemma": "retractatus", "uri": "48147", "pos": "a", "morpho": "aps---mn1-"}, "retractatus2": {
        "lemma": "retractatus", "uri": "r7044", "pos": "n", "morpho": "n-s---mn4-"
    }, "retractus1": {"lemma": "retractus", "uri": "30496", "pos": "a", "morpho": "aps---mn1-"}, "retractus2": {
        "lemma": "retractus", "uri": "r7045", "pos": "n", "morpho": "n-s---mn4-"
    }, "rex1": {"lemma": "rex", "uri": "r0645", "pos": "n", "morpho": "n-s---mn3-"}, "Rex2": {
        "lemma": "Rex", "uri": "61836", "pos": "n", "morpho": "n-s---mn3-"
    }, "Rhea1": {"lemma": "Rhea", "uri": "61842", "pos": "n", "morpho": "n-s---fn1-"}, "Rhea2": {
        "lemma": "Rhea", "uri": "61842", "pos": "n", "morpho": "n-s---fn1-"
    }, "Rhoeteus1": {"lemma": "Rhoeteus", "uri": "61856", "pos": "a", "morpho": "aps---mn1-"}, "Rhoeteus2": {
        "lemma": "Rhoeteus", "uri": "61856", "pos": "a", "morpho": "aps---mn1-"
    }, "ricinus1": {"lemma": "ricinus", "uri": "r0709", "pos": "a", "morpho": "aps---mn1-"}, "ricinus2": {
        "lemma": "ricinus", "uri": "r0959", "pos": "n", "morpho": "n-s---mn2-"
    }, "robus1": {"lemma": "robus", "uri": "r9763", "pos": "a", "morpho": "aps---mn1-"}, "robus2": {
        "lemma": "robus", "uri": "r9763", "pos": "a", "morpho": "aps---mn1-"
    }, "Romulus1": {"lemma": "Romulus", "uri": "26886", "pos": "n", "morpho": "n-s---mn2-"}, "Romulus2": {
        "lemma": "Romulus", "uri": "26886", "pos": "n", "morpho": "n-s---mn2-"
    }, "roseus1": {"lemma": "roseus", "uri": "r0804", "pos": "a", "morpho": "aps---mn1-"}, "rubeta1": {
        "lemma": "rubeta", "uri": "r0840", "pos": "n", "morpho": "n-s---fn1-"
    }, "rubeta2": {"lemma": "rubeta", "uri": "125657", "pos": "n", "morpho": "n-p---nn2-"}, "rubeus1": {
        "lemma": "rubeus", "uri": "26896", "pos": "a", "morpho": "aps---mn1-"
    }, "rubeus2": {"lemma": "rubeus", "uri": "26896", "pos": "a", "morpho": "aps---mn1-"}, "rubricatus1": {
        "lemma": "rubricatus", "uri": "45067", "pos": "a", "morpho": "aps---mn1-"
    }, "Rubricatus2": {"lemma": "Rubricatus", "uri": "61867", "pos": "n", "morpho": "n-s---mn2-"}, "rudens1": {
        "lemma": "rudens", "uri": "r0863", "pos": "n", "morpho": "n-s---mn3i"
    }, "rudens2": {"lemma": "rudens", "uri": "125677", "pos": "a", "morpho": "aps---an3i"}, "rudis1": {
        "lemma": "rudis", "uri": "r9872", "pos": "a", "morpho": "aps---cn3i"
    }, "rudis2": {"lemma": "rudis", "uri": "r0872", "pos": "n", "morpho": "n-s---fn3i"}, "rudus1": {
        "lemma": "rudus", "uri": "r1990", "pos": "n", "morpho": "n-s---nn3-"
    }, "rudus2": {"lemma": "rudus", "uri": "r1990", "pos": "n", "morpho": "n-s---nn3-"}, "rufus1": {
        "lemma": "rufus", "uri": "r0878", "pos": "a", "morpho": "aps---mn1-"
    }, "ruga1": {"lemma": "ruga", "uri": "r0879", "pos": "n", "morpho": "n-s---fn1-"}, "rumex1": {
        "lemma": "rumex", "uri": "r0441", "pos": "n", "morpho": "n-s---mn3-"
    }, "rumex2": {"lemma": "rumex", "uri": "r0891", "pos": "n", "morpho": "n-s---fn3-"}, "Rumina1": {
        "lemma": "Rumina", "uri": "61871", "pos": "n", "morpho": "n-s---fn1-"
    }, "Rumina2": {"lemma": "Rumina", "uri": "61871", "pos": "n", "morpho": "n-s---fn1-"}, "ruminalis2": {
        "lemma": "ruminalis", "uri": "r0894", "pos": "a", "morpho": "aps---cn3i"
    }, "runcina1": {"lemma": "runcina", "uri": "r0906", "pos": "n", "morpho": "n-s---fn1-"}, "runco1": {
        "lemma": "runco", "uri": "r1498", "pos": "v", "morpho": "v1spia--1-"
    }, "runco2": {"lemma": "runco", "uri": "r0907", "pos": "n", "morpho": "n-s---mn3-"}, "rusco1": {
        "lemma": "rusco", "uri": "125738", "pos": "v", "morpho": "v1spia--1-"
    }, "rusco2": {"lemma": "rusco", "uri": "125739", "pos": "n", "morpho": "n-s---mn3-"}, "ruta2": {
        "lemma": "ruta", "uri": "r0944", "pos": "n", "morpho": "n-s---fn1-"
    }, "rutilus1": {"lemma": "rutilus", "uri": "r0950", "pos": "a", "morpho": "aps---mn1-"}, "rutuba1": {
        "lemma": "rutuba", "uri": "r0954", "pos": "n", "morpho": "n-s---fn1-"
    }, "saburra1": {"lemma": "saburra", "uri": "s0015", "pos": "n", "morpho": "n-s---fn1-"}, "sacerdos1": {
        "lemma": "sacerdos", "uri": "26922", "pos": "n", "morpho": "n-s---mn3-"
    }, "sacrator1": {"lemma": "sacrator", "uri": "s0056", "pos": "n", "morpho": "n-s---mn3-"}, "saga1": {
        "lemma": "saga", "uri": "s0134", "pos": "n", "morpho": "n-s---fn1-"
    }, "saga2": {"lemma": "saga", "uri": "s0134", "pos": "n", "morpho": "n-s---fn1-"}, "Sagaris1": {
        "lemma": "Sagaris", "uri": "61893", "pos": "n", "morpho": "n-s---fn3-"
    }, "Sagaris2": {"lemma": "Sagaris", "uri": "61893", "pos": "n", "morpho": "n-s---fn3-"}, "sagarius1": {
        "lemma": "sagarius", "uri": "s0106", "pos": "a", "morpho": "aps---mn1-"
    }, "sagus1": {"lemma": "sagus", "uri": "s0134", "pos": "a", "morpho": "aps---mn1-"}, "sagus2": {
        "lemma": "sagus", "uri": "125890", "pos": "n", "morpho": "n-s---mn2-"
    }, "sale1": {"lemma": "sale", "uri": "s0136", "pos": "n", "morpho": "n-s---nn3i"}, "Sale2": {
        "lemma": "Sale", "uri": "61901", "pos": "n", "morpho": "n-s---fn1-"
    }, "Saliaris1": {"lemma": "Saliaris", "uri": "61906", "pos": "a", "morpho": "aps---fn3i"}, "Saliaris2": {
        "lemma": "Saliaris", "uri": "61906", "pos": "a", "morpho": "aps---fn3i"
    }, "Salii1": {"lemma": "Salii", "uri": "61907", "pos": "n", "morpho": "n-p---mn2-"}, "Salii2": {
        "lemma": "Salii", "uri": "61907", "pos": "n", "morpho": "n-p---mn2-"
    }, "salinator1": {"lemma": "salinator", "uri": "s0166", "pos": "n", "morpho": "n-s---mn3-"}, "salio1": {
        "lemma": "salio", "uri": "s0182", "pos": "v", "morpho": "v1spia--4-"
    }, "salio2": {"lemma": "salio", "uri": "s0182", "pos": "v", "morpho": "v1spia--4-"}, "salo1": {
        "lemma": "salo", "uri": "125936", "pos": "v", "morpho": "v1spia--3-"
    }, "Salo2": {"lemma": "Salo", "uri": "61911", "pos": "n", "morpho": "n-s---mn3-"}, "saltus1": {
        "lemma": "saltus", "uri": "s9948", "pos": "n", "morpho": "n-s---mn4-"
    }, "saltus2": {"lemma": "saltus", "uri": "s9948", "pos": "n", "morpho": "n-s---mn4-"}, "salve1": {
        "lemma": "salue", "uri": "41465", "pos": "r", "morpho": "rp--------"
    }, "sambucus1": {"lemma": "sambucus", "uri": "s0249", "pos": "n", "morpho": "n-s---mn2-"}, "sambucus2": {
        "lemma": "sambucus", "uri": "125992", "pos": "n", "morpho": "n-s---fn2-"
    }, "sapineus1": {"lemma": "sapineus", "uri": "44930", "pos": "a", "morpho": "aps---mn1-"}, "sarda1": {
        "lemma": "sarda", "uri": "s3319", "pos": "n", "morpho": "n-s---fn1-"
    }, "Sarda2": {"lemma": "Sarda", "uri": "61940", "pos": "n", "morpho": "n-s---fn1-"}, "sartor1": {
        "lemma": "sartor", "uri": "s0407", "pos": "n", "morpho": "n-s---mn3-"
    }, "sartor2": {"lemma": "sartor", "uri": "s0407", "pos": "n", "morpho": "n-s---mn3-"}, "sartura1": {
        "lemma": "sartura", "uri": "s0355", "pos": "n", "morpho": "n-s---fn1-"
    }, "sartura2": {"lemma": "sartura", "uri": "s0355", "pos": "n", "morpho": "n-s---fn1-"}, "satio1": {
        "lemma": "satio", "uri": "s0424", "pos": "v", "morpho": "v1spia--1-"
    }, "satio2": {"lemma": "satio", "uri": "s0425", "pos": "n", "morpho": "n-s---fn3-"}, "satus1": {
        "lemma": "satus", "uri": "39002", "pos": "a", "morpho": "aps---mn1-"
    }, "satus2": {"lemma": "satus", "uri": "s9949", "pos": "n", "morpho": "n-s---mn4-"}, "satyricus1": {
        "lemma": "satyricus", "uri": "s0457", "pos": "a", "morpho": "aps---mn1-"
    }, "satyricus2": {"lemma": "satyricus", "uri": "s0457", "pos": "a", "morpho": "aps---mn1-"}, "scaeva1": {
        "lemma": "scaeua", "uri": "s4025", "pos": "n", "morpho": "n-s---mn1-"
    }, "scaeva2": {"lemma": "scaeua", "uri": "s4025", "pos": "n", "morpho": "n-s---mn1-"}, "Scapula1": {
        "lemma": "Scapula", "uri": "61969", "pos": "n", "morpho": "n-s---fn1-"
    }, "scapula2": {"lemma": "scapula", "uri": "s7605", "pos": "n", "morpho": "n-s---fn1-"}, "scapula3": {
        "lemma": "scapula", "uri": "s7605", "pos": "n", "morpho": "n-s---fn1-"
    }, "scipio1": {"lemma": "scipio", "uri": "s0658", "pos": "n", "morpho": "n-s---mn3-"}, "Scipio2": {
        "lemma": "Scipio", "uri": "61977", "pos": "a", "morpho": "aps---mn3-"
    }, "Sciron1": {"lemma": "Sciron", "uri": "61978", "pos": "n", "morpho": "n-s---nn3-"}, "Sciron2": {
        "lemma": "Sciron", "uri": "61978", "pos": "n", "morpho": "n-s---nn3-"
    }, "scissus1": {"lemma": "scissus", "uri": "51481", "pos": "a", "morpho": "aps---mn1-"}, "scitus1": {
        "lemma": "scitus", "uri": "27058", "pos": "a", "morpho": "aps---mn1-"
    }, "scitus2": {"lemma": "scitus", "uri": "s9950", "pos": "n", "morpho": "n-s---mn4-"}, "scopo1": {
        "lemma": "scopo", "uri": "s0708", "pos": "v", "morpho": "v1spia--3-"
    }, "scopo2": {"lemma": "scopo", "uri": "s0707", "pos": "v", "morpho": "v1spia--1-"}, "scriptus1": {
        "lemma": "scriptus", "uri": "126481", "pos": "a", "morpho": "aps---mn1-"
    }, "scriptus2": {"lemma": "scriptus", "uri": "s9951", "pos": "n", "morpho": "n-s---mn4-"}, "scrofa1": {
        "lemma": "scrofa", "uri": "s0781", "pos": "n", "morpho": "n-s---fn1-"
    }, "scutula1": {"lemma": "scutula", "uri": "s4027", "pos": "n", "morpho": "n-s---fn1-"}, "scutula2": {
        "lemma": "scutula", "uri": "s4027", "pos": "n", "morpho": "n-s---fn1-"
    }, "se1": {"lemma": "se", "uri": None, "pos": "r", "morpho": "rp--------"}, "se2": {
        "lemma": "se", "uri": None, "pos": "r", "morpho": "rp--------"
    }, "sebosus1": {"lemma": "sebosus", "uri": "s0850", "pos": "a", "morpho": "aps---mn1-"}, "secta1": {
        "lemma": "secta", "uri": "s9868", "pos": "n", "morpho": "n-s---fn1-"
    }, "secta2": {"lemma": "secta", "uri": "126557", "pos": "n", "morpho": "n-p---nn2-"}, "sector1": {
        "lemma": "sector", "uri": "s0876", "pos": "n", "morpho": "n-s---mn3-"
    }, "sector2": {"lemma": "sector", "uri": "s0875", "pos": "v", "morpho": "v1spid--1-"}, "sectus1": {
        "lemma": "sectus", "uri": "126563", "pos": "a", "morpho": "aps---mn1-"
    }, "sectus2": {"lemma": "sectus", "uri": "126563", "pos": "a", "morpho": "aps---mn1-"}, "secundo1": {
        "lemma": "secundo", "uri": "126575", "pos": "r", "morpho": "rp--------"
    }, "secundo2": {"lemma": "secundo", "uri": "s0887", "pos": "v", "morpho": "v1spia--1-"}, "secundus1": {
        "lemma": "secundus", "uri": "s9990", "pos": "a", "morpho": "aps---mn1-"
    }, "secus1": {"lemma": "secus", "uri": "s9897", "pos": "n", "morpho": "n-s---nn--"}, "sed1": {
        "lemma": "sed", "uri": "34186", "pos": "r", "morpho": "rp--------"
    }, "sed2": {"lemma": "sed", "uri": "34186", "pos": "r", "morpho": "rp--------"}, "sed3": {
        "lemma": "sed", "uri": "34186", "pos": "r", "morpho": "rp--------"
    }, "sedum1": {"lemma": "sedum", "uri": "s0933", "pos": "n", "morpho": "n-s---nn2-"}, "sedum2": {
        "lemma": "sedum", "uri": "s0933", "pos": "n", "morpho": "n-s---nn2-"
    }, "Segesta1": {"lemma": "Segesta", "uri": "62000", "pos": "a", "morpho": "aps---fn1-"}, "Segesta2": {
        "lemma": "Segesta", "uri": "62000", "pos": "a", "morpho": "aps---fn1-"
    }, "sejugis1": {"lemma": "seiugis", "uri": "s8000", "pos": "a", "morpho": "aps---cn3i"}, "sejugis2": {
        "lemma": "seiugis", "uri": "s8000", "pos": "a", "morpho": "aps---cn3i"
    }, "semestris1": {"lemma": "semestris", "uri": "126656", "pos": "a", "morpho": "aps---cn3i"}, "semestris2": {
        "lemma": "semestris", "uri": "126656", "pos": "a", "morpho": "aps---cn3i"
    }, "senecio1": {"lemma": "senecio", "uri": "s1204", "pos": "n", "morpho": "n-s---mn3-"}, "senecio3": {
        "lemma": "senecio", "uri": "s1204", "pos": "n", "morpho": "n-s---mn3-"
    }, "senectus1": {"lemma": "senectus", "uri": "s1205", "pos": "a", "morpho": "aps---mn1-"}, "senectus2": {
        "lemma": "senectus", "uri": "s1206", "pos": "n", "morpho": "n-s---fn3-"
    }, "sensus1": {"lemma": "sensus", "uri": "126853", "pos": "a", "morpho": "aps---mn1-"}, "sensus2": {
        "lemma": "sensus", "uri": "s1245", "pos": "n", "morpho": "n-s---mn4-"
    }, "sentis1": {"lemma": "sentis", "uri": "s1244", "pos": "n", "morpho": "n-s---fn3i"}, "separatus1": {
        "lemma": "separatus", "uri": "29373", "pos": "a", "morpho": "aps---mn1-"
    }, "separatus2": {"lemma": "separatus", "uri": None, "pos": "n", "morpho": "n-s---mn4-"}, "sepes1": {
        "lemma": "sepes", "uri": "46042", "pos": "a", "morpho": "aps---an3-"
    }, "sepes2": {"lemma": "sepes", "uri": "s1262", "pos": "n", "morpho": "n-s---fn3i"}, "seps1": {
        "lemma": "seps", "uri": "s1270", "pos": "n", "morpho": "n-s---mn3-"
    }, "seps2": {"lemma": "seps", "uri": "s1270", "pos": "n", "morpho": "n-s---mn3-"}, "serenus1": {
        "lemma": "serenus", "uri": "s1358", "pos": "a", "morpho": "aps---mn1-"
    }, "seresco1": {"lemma": "seresco", "uri": "s4028", "pos": "v", "morpho": "v1spia--3-"}, "seresco2": {
        "lemma": "seresco", "uri": "s4028", "pos": "v", "morpho": "v1spia--3-"
    }, "serius1": {"lemma": "serius", "uri": "s1375", "pos": "a", "morpho": "aps---mn1-"}, "sero3": {
        "lemma": "sero", "uri": "s1386", "pos": "v", "morpho": "v1spia--1-"
    }, "sero4": {"lemma": "sero", "uri": "100571", "pos": "r", "morpho": "rp--------"}, "servus1": {
        "lemma": "seruus", "uri": "s1432", "pos": "a", "morpho": "aps---mn1-"
    }, "servus2": {"lemma": "seruus", "uri": "s1432", "pos": "n", "morpho": "n-s---mn2-"}, "severus1": {
        "lemma": "seuerus", "uri": "s1507", "pos": "a", "morpho": "aps---mn1-"
    }, "sextus1": {"lemma": "sextus", "uri": "s1541", "pos": "a", "morpho": "aps---mn1-"}, "Sextus2": {
        "lemma": "Sextus", "uri": "62054", "pos": "n", "morpho": "n-s---mn2-"
    }, "sibilus1": {"lemma": "sibilus", "uri": None, "pos": "n", "morpho": "n-s---mn2-"}, "sibilus2": {
        "lemma": "sibilus", "uri": "s0664", "pos": "a", "morpho": "aps---mn1-"
    }, "sil1": {"lemma": "sil", "uri": "s4022", "pos": "n", "morpho": "n-s---nn3-"}, "sil2": {
        "lemma": "sil", "uri": "s4022", "pos": "n", "morpho": "n-s---nn3-"
    }, "Silanus1": {"lemma": "Silanus", "uri": "62071", "pos": "n", "morpho": "n-s---mn2-"}, "silanus2": {
        "lemma": "silanus", "uri": "s1631", "pos": "n", "morpho": "n-s---mn2-"
    }, "Silanus3": {"lemma": "Silanus", "uri": "62071", "pos": "n", "morpho": "n-s---mn2-"}, "siler1": {
        "lemma": "siler", "uri": "s1639", "pos": "n", "morpho": "n-s---nn3-"
    }, "silo1": {"lemma": "silo", "uri": "s8660", "pos": "n", "morpho": "n-s---mn3-"}, "silus1": {
        "lemma": "silus", "uri": "s1674", "pos": "a", "morpho": "aps---mn1-"
    }, "simo1": {"lemma": "simo", "uri": "s1695", "pos": "v", "morpho": "v1spia--1-"}, "Simon1": {
        "lemma": "Simon", "uri": "62082", "pos": "n", "morpho": "n-s---nn3-"
    }, "Simon2": {"lemma": "Simon", "uri": "62082", "pos": "n", "morpho": "n-s---nn3-"}, "simulus1": {
        "lemma": "simulus", "uri": "s1725", "pos": "a", "morpho": "aps---mn1-"
    }, "sinus1": {"lemma": "sinus", "uri": "s1764", "pos": "n", "morpho": "n-s---mn4-"}, "sinus2": {
        "lemma": "sinus", "uri": "127315", "pos": "n", "morpho": "n-s---mn2-"
    }, "sion1": {"lemma": "sion", "uri": "s1765", "pos": "n", "morpho": "n-s---nn2g"}, "Siris2": {
        "lemma": "Siris", "uri": "62104", "pos": "n", "morpho": "n-s---fn3-"
    }, "situs1": {"lemma": "situs", "uri": "100625", "pos": "a", "morpho": "aps---mn1-"}, "situs2": {
        "lemma": "situs", "uri": "s4029", "pos": "n", "morpho": "n-s---mn4-"
    }, "smyrna1": {"lemma": "smyrna", "uri": "s1827", "pos": "n", "morpho": "n-s---fn1-"}, "Smyrna2": {
        "lemma": "Smyrna", "uri": "27231", "pos": "n", "morpho": "n-s---fn1-"
    }, "solarium1": {"lemma": "solarium", "uri": "s4023", "pos": "n", "morpho": "n-s---nn2-"}, "solarium2": {
        "lemma": "solarium", "uri": "s4023", "pos": "n", "morpho": "n-s---nn2-"
    }, "solitaneus1": {"lemma": "solitaneus", "uri": "s4030", "pos": "a", "morpho": "aps---mn1-"}, "solitaneus2": {
        "lemma": "solitaneus", "uri": "s4030", "pos": "a", "morpho": "aps---mn1-"
    }, "solo1": {"lemma": "solo", "uri": "s1932", "pos": "v", "morpho": "v1spia--1-"}, "Solon1": {
        "lemma": "Solon", "uri": "62123", "pos": "n", "morpho": "n-s---nn3-"
    }, "Solon2": {"lemma": "Solon", "uri": "62123", "pos": "n", "morpho": "n-s---nn3-"}, "solum1": {
        "lemma": "solum", "uri": "s1944", "pos": "n", "morpho": "n-s---nn2-"
    }, "solum2": {"lemma": "solum", "uri": "27266", "pos": "r", "morpho": "rp--------"}, "solus1": {
        "lemma": "solus", "uri": "s1947", "pos": "a", "morpho": "aps---mn1p"
    }, "Solus2": {"lemma": "Solus", "uri": "62127", "pos": "n", "morpho": "n-s---mn2-"}, "solus3": {
        "lemma": "solus", "uri": "127475", "pos": "n", "morpho": "n-s---mn4-"
    }, "sonus2": {"lemma": "sonus", "uri": "s1981", "pos": "a", "morpho": "aps---mn1-"}, "sophistice1": {
        "lemma": "sophistice", "uri": "32242", "pos": "r", "morpho": "rp--------"
    }, "sophistice2": {"lemma": "sophistice", "uri": "s1986", "pos": "n", "morpho": "n-s---fn1g"}, "sophos1": {
        "lemma": "sophos", "uri": "s1988", "pos": "n", "morpho": "n-s---mn2g"
    }, "sophos2": {"lemma": "sophos", "uri": "s9989", "pos": "r", "morpho": "rp--------"}, "sophus1": {
        "lemma": "sophus", "uri": "54401", "pos": "n", "morpho": "n-s---mn2-"
    }, "sortitus1": {"lemma": "sortitus", "uri": "36517", "pos": "a", "morpho": "aps---mn1-"}, "sortitus2": {
        "lemma": "sortitus", "uri": "s2058", "pos": "n", "morpho": "n-s---mn4-"
    }, "Sosus1": {"lemma": "Sosus", "uri": "62146", "pos": "n", "morpho": "n-s---mn2-"}, "Sosus2": {
        "lemma": "Sosus", "uri": "62146", "pos": "n", "morpho": "n-s---mn2-"
    }, "spargo1": {"lemma": "spargo", "uri": "s2064", "pos": "v", "morpho": "v1spia--3-"}, "spargo2": {
        "lemma": "spargo", "uri": "s2063", "pos": "n", "morpho": "n-s---fn3-"
    }, "speculatus1": {"lemma": "speculatus", "uri": "127606", "pos": "a", "morpho": "aps---mn1-"}, "speculatus2": {
        "lemma": "speculatus", "uri": "127606", "pos": "a", "morpho": "aps---mn1-"
    }, "Spinther2": {"lemma": "Spinther", "uri": "127659", "pos": "n", "morpho": "n-s---nn3-"}, "spongia1": {
        "lemma": "spongia", "uri": "s1676", "pos": "n", "morpho": "n-s---fn1-"
    }, "Spongia2": {"lemma": "Spongia", "uri": "62165", "pos": "n", "morpho": "n-s---fn1-"}, "spretus1": {
        "lemma": "spretus", "uri": "127737", "pos": "a", "morpho": "aps---mn1-"
    }, "spretus2": {"lemma": "spretus", "uri": "s2148", "pos": "n", "morpho": "n-s---mn4-"}, "spurius1": {
        "lemma": "spurius", "uri": "s2308", "pos": "a", "morpho": "aps---mn1-"
    }, "squalus1": {"lemma": "squalus", "uri": "s2321", "pos": "a", "morpho": "aps---mn1-"}, "squalus2": {
        "lemma": "squalus", "uri": "s2321", "pos": "n", "morpho": "n-s---mn2-"
    }, "stagno1": {"lemma": "stagno", "uri": "s4031", "pos": "v", "morpho": "v1spia--1-"}, "stagno2": {
        "lemma": "stagno", "uri": "s4031", "pos": "v", "morpho": "v1spia--1-"
    }, "stagnum1": {"lemma": "stagnum", "uri": "s2364", "pos": "n", "morpho": "n-s---nn2-"}, "stagnum2": {
        "lemma": "stagnum", "uri": "s2364", "pos": "n", "morpho": "n-s---nn2-"
    }, "stator1": {"lemma": "stator", "uri": "s4032", "pos": "n", "morpho": "n-s---mn3-"}, "status1": {
        "lemma": "status", "uri": "100688", "pos": "a", "morpho": "aps---mn1-"
    }, "status2": {"lemma": "status", "uri": "s9962", "pos": "n", "morpho": "n-s---mn4-"}, "stellio1": {
        "lemma": "stellio", "uri": "s2422", "pos": "n", "morpho": "n-s---mn3-"
    }, "Stephane1": {"lemma": "Stephane", "uri": "62186", "pos": "n", "morpho": "n-s---fn1-"}, "Stephane2": {
        "lemma": "Stephane", "uri": "62186", "pos": "n", "morpho": "n-s---fn1-"
    }, "stilo1": {"lemma": "stilo", "uri": "s2479", "pos": "v", "morpho": "v1spia--1-"}, "Stilo2": {
        "lemma": "Stilo", "uri": "62201", "pos": "n", "morpho": "n-s---mn3-"
    }, "stips1": {"lemma": "stips", "uri": "s2503", "pos": "n", "morpho": "n-s---fn3-"}, "stips2": {
        "lemma": "stips", "uri": "s2503", "pos": "n", "morpho": "n-s---fn3-"
    }, "stiria1": {"lemma": "stiria", "uri": "s2509", "pos": "n", "morpho": "n-s---fn1-"}, "Stiria2": {
        "lemma": "Stiria", "uri": "62203", "pos": "n", "morpho": "n-s---fn1-"
    }, "stolo1": {"lemma": "stolo", "uri": "s2531", "pos": "n", "morpho": "n-s---mn3-"}, "storia1": {
        "lemma": "storia", "uri": "56338", "pos": "n", "morpho": "n-s---fn1-"
    }, "storia2": {"lemma": "storia", "uri": "56338", "pos": "n", "morpho": "n-s---fn1-"}, "strabo1": {
        "lemma": "strabo", "uri": "s2547", "pos": "n", "morpho": "n-s---mn3-"
    }, "stratus1": {"lemma": "stratus", "uri": "127977", "pos": "a", "morpho": "aps---mn1-"}, "stratus2": {
        "lemma": "stratus", "uri": "s9943", "pos": "n", "morpho": "n-s---mn4-"
    }, "stratus3": {"lemma": "stratus", "uri": "s9943", "pos": "n", "morpho": "n-s---mn4-"}, "striga1": {
        "lemma": "striga", "uri": "s4033", "pos": "n", "morpho": "n-s---fn1-"
    }, "striga2": {"lemma": "striga", "uri": "s4033", "pos": "n", "morpho": "n-s---fn1-"}, "strio1": {
        "lemma": "strio", "uri": "128004", "pos": "n", "morpho": "n-s---mn3-"
    }, "strio2": {"lemma": "strio", "uri": "128004", "pos": "n", "morpho": "n-s---mn3-"}, "strix1": {
        "lemma": "strix", "uri": "s4034", "pos": "n", "morpho": "n-s---fn3-"
    }, "strix2": {"lemma": "strix", "uri": "s4034", "pos": "n", "morpho": "n-s---fn3-"}, "strobilus1": {
        "lemma": "strobilus", "uri": "s2618", "pos": "n", "morpho": "n-s---mn2-"
    }, "Strobilus2": {"lemma": "Strobilus", "uri": "62217", "pos": "n", "morpho": "n-s---mn2-"}, "strongyle1": {
        "lemma": "strongyle", "uri": "s2623", "pos": "n", "morpho": "n-s---fn1g"
    }, "structus1": {"lemma": "structus", "uri": "128027", "pos": "a", "morpho": "aps---mn1-"}, "structus2": {
        "lemma": "structus", "uri": "s9966", "pos": "n", "morpho": "n-s---mn4-"
    }, "struma1": {"lemma": "struma", "uri": "s2640", "pos": "n", "morpho": "n-s---fn1-"}, "suasum1": {
        "lemma": "suasum", "uri": "s9967", "pos": "n", "morpho": "n-s---nn2-"
    }, "suasum2": {"lemma": "suasum", "uri": "s9967", "pos": "n", "morpho": "n-s---nn2-"}, "suasus2": {
        "lemma": "suasus", "uri": "s2713", "pos": "n", "morpho": "n-s---mn4-"
    }, "subactus1": {"lemma": "subactus", "uri": "128103", "pos": "a", "morpho": "aps---mn1-"}, "subactus2": {
        "lemma": "subactus", "uri": "s9968", "pos": "n", "morpho": "n-s---mn4-"
    }, "suberinus1": {"lemma": "suberinus", "uri": "s2849", "pos": "a", "morpho": "aps---mn1-"}, "subis1": {
        "lemma": "subis", "uri": "s2905", "pos": "n", "morpho": "n-s---fn3i"
    }, "subjectus1": {"lemma": "subiectus", "uri": "36202", "pos": "a", "morpho": "aps---mn1-"}, "subjectus2": {
        "lemma": "subiectus", "uri": "s9969", "pos": "n", "morpho": "n-s---mn4-"
    }, "subsero1": {"lemma": "subsero", "uri": "s3114", "pos": "v", "morpho": "v1spia--3-"}, "subsero2": {
        "lemma": "subsero", "uri": "s3114", "pos": "v", "morpho": "v1spia--3-"
    }, "substratus1": {"lemma": "substratus", "uri": "128491", "pos": "a", "morpho": "aps---mn1-"}, "substratus2": {
        "lemma": "substratus", "uri": "s9975", "pos": "n", "morpho": "n-s---mn4-"
    }, "subulo1": {"lemma": "subulo", "uri": "s4037", "pos": "n", "morpho": "n-s---mn3-"}, "subvectus1": {
        "lemma": "subuectus", "uri": "128573", "pos": "a", "morpho": "aps---mn1-"
    }, "subvectus2": {"lemma": "subuectus", "uri": "s3245", "pos": "n", "morpho": "n-s---mn4-"}, "succensio1": {
        "lemma": "succensio", "uri": "s3837", "pos": "n", "morpho": "n-s---fn3-"
    }, "succensio2": {"lemma": "succensio", "uri": "s3837", "pos": "n", "morpho": "n-s---fn3-"}, "succenturio1": {
        "lemma": "succenturio", "uri": "s3266", "pos": "v", "morpho": "v1spia--1-"
    }, "succenturio2": {"lemma": "succenturio", "uri": "s3266", "pos": "v", "morpho": "v1spia--1-"}, "successus1": {
        "lemma": "successus", "uri": "128619", "pos": "a", "morpho": "aps---mn1-"
    }, "successus2": {"lemma": "successus", "uri": "s3269", "pos": "n", "morpho": "n-s---mn4-"}, "succubo2": {
        "lemma": "succubo", "uri": "s3298", "pos": "n", "morpho": "n-s---mn3-"
    }, "succussus2": {"lemma": "succussus", "uri": "s9976", "pos": "n", "morpho": "n-s---mn4-"}, "suctus1": {
        "lemma": "suctus", "uri": "s3441", "pos": "n", "morpho": "n-s---mn4-"
    }, "suctus2": {"lemma": "suctus", "uri": "s3441", "pos": "n", "morpho": "n-s---mn4-"}, "sucula1": {
        "lemma": "sucula", "uri": "s3316", "pos": "n", "morpho": "n-s---fn1-"
    }, "sucula2": {"lemma": "sucula", "uri": "s3316", "pos": "n", "morpho": "n-s---fn1-"}, "sucula3": {
        "lemma": "sucula", "uri": "s3316", "pos": "n", "morpho": "n-s---fn1-"
    }, "suffitus1": {"lemma": "suffitus", "uri": "s9977", "pos": "n", "morpho": "n-s---mn4-"}, "suffitus2": {
        "lemma": "suffitus", "uri": "s9977", "pos": "n", "morpho": "n-s---mn4-"
    }, "sufflatus1": {"lemma": "sufflatus", "uri": "s9978", "pos": "n", "morpho": "n-s---mn4-"}, "sufflatus2": {
        "lemma": "sufflatus", "uri": "100769", "pos": "a", "morpho": "aps---mn1-"
    }, "suffrago1": {"lemma": "suffrago", "uri": "s3380", "pos": "n", "morpho": "n-s---fn3-"}, "suffrago2": {
        "lemma": "suffrago", "uri": "128717", "pos": "v", "morpho": "v1spia--1-"
    }, "suggestus1": {"lemma": "suggestus", "uri": "s9979", "pos": "n", "morpho": "n-s---mn4-"}, "suggestus2": {
        "lemma": "suggestus", "uri": "s9979", "pos": "n", "morpho": "n-s---mn4-"
    }, "sulcus1": {"lemma": "sulcus", "uri": "s3426", "pos": "a", "morpho": "aps---mn1-"}, "sulcus2": {
        "lemma": "sulcus", "uri": "s3426", "pos": "n", "morpho": "n-s---mn2-"
    }, "sum1": {"lemma": "sum", "uri": "s3436", "pos": "v", "morpho": "v1spia--3-"}, "sum2": {
        "lemma": "sum", "uri": "s3436", "pos": "v", "morpho": "v1spia--3-"
    }, "sum3": {"lemma": "sum", "uri": "s3436", "pos": "v", "morpho": "v1spia--3-"}, "summissus1": {
        "lemma": "summissus", "uri": "33682", "pos": "a", "morpho": "aps---mn1-"
    }, "summissus2": {"lemma": "summissus", "uri": "30237", "pos": "n", "morpho": "n-s---mn2-"}, "sumptus1": {
        "lemma": "sumptus", "uri": "128795", "pos": "a", "morpho": "aps---mn1-"
    }, "sumptus2": {"lemma": "sumptus", "uri": "s9980", "pos": "n", "morpho": "n-s---mn4-"}, "super1": {
        "lemma": "super", "uri": "s3737", "pos": "a", "morpho": "aps---mn1r"
    }, "super2": {"lemma": "super", "uri": "27541", "pos": "r", "morpho": "rp--------"}, "supergressus1": {
        "lemma": "supergressus", "uri": "128927", "pos": "a", "morpho": "aps---mn1-"
    }, "supergressus2": {"lemma": "supergressus", "uri": "s9981", "pos": "n", "morpho": "n-s---mn4-"}, "superjectus1": {
        "lemma": "superiectus", "uri": "128934", "pos": "a", "morpho": "aps---mn1-"
    }, "superjectus2": {"lemma": "superiectus", "uri": "s9982", "pos": "n", "morpho": "n-s---mn4-"}, "supparo1": {
        "lemma": "supparo", "uri": "s4038", "pos": "v", "morpho": "v1spia--1-"
    }, "supparo2": {"lemma": "supparo", "uri": "s4038", "pos": "v", "morpho": "v1spia--1-"}, "suppingo1": {
        "lemma": "suppingo", "uri": "s3761", "pos": "v", "morpho": "v1spia--3-"
    }, "suppingo2": {"lemma": "suppingo", "uri": "s3761", "pos": "v", "morpho": "v1spia--3-"}, "sura1": {
        "lemma": "sura", "uri": "s3814", "pos": "n", "morpho": "n-s---fn1-"
    }, "Sura2": {"lemma": "Sura", "uri": "62273", "pos": "n", "morpho": "n-s---fn1-"}, "Sura3": {
        "lemma": "Sura", "uri": "62273", "pos": "n", "morpho": "n-s---fn1-"
    }, "surena1": {"lemma": "surena", "uri": "s3829", "pos": "n", "morpho": "n-s---fn1-"}, "surena2": {
        "lemma": "surena", "uri": "129223", "pos": "n", "morpho": "n-s---mn1-"
    }, "surrectus1": {"lemma": "surrectus", "uri": "129234", "pos": "a", "morpho": "aps---mn1-"}, "surrectus2": {
        "lemma": "surrectus", "uri": "129234", "pos": "a", "morpho": "aps---mn1-"
    }, "surus1": {"lemma": "surus", "uri": "s3833", "pos": "n", "morpho": "n-s---mn2-"}, "Surus2": {
        "lemma": "Surus", "uri": "62277", "pos": "n", "morpho": "n-s---mn2-"
    }, "suspecto1": {"lemma": "suspecto", "uri": "s3853", "pos": "v", "morpho": "v1spia--1-"}, "suspecto2": {
        "lemma": "suspecto", "uri": "129279", "pos": "r", "morpho": "rp--------"
    }, "suspector1": {"lemma": "suspector", "uri": "133155", "pos": "v", "morpho": "v1spid--1-"}, "suspector2": {
        "lemma": "suspector", "uri": "s3854", "pos": "n", "morpho": "n-s---mn3-"
    }, "suspectus1": {"lemma": "suspectus", "uri": "40940", "pos": "a", "morpho": "aps---mn1-"}, "suspectus2": {
        "lemma": "suspectus", "uri": "s9985", "pos": "n", "morpho": "n-s---mn4-"
    }, "suspicio1": {"lemma": "suspicio", "uri": "s3862", "pos": "v", "morpho": "v1spia--3i"}, "suspicio2": {
        "lemma": "suspicio", "uri": "s3863", "pos": "n", "morpho": "n-s---fn3-"
    }, "susurro1": {"lemma": "susurro", "uri": "s3884", "pos": "v", "morpho": "v1spia--1-"}, "susurro2": {
        "lemma": "susurro", "uri": "s3885", "pos": "n", "morpho": "n-s---mn3-"
    }, "susurrus1": {"lemma": "susurrus", "uri": "s3886", "pos": "n", "morpho": "n-s---mn2-"}, "susurrus2": {
        "lemma": "susurrus", "uri": "s1362", "pos": "a", "morpho": "aps---mn1-"
    }, "sutrinus1": {"lemma": "sutrinus", "uri": "s3893", "pos": "a", "morpho": "aps---mn1-"}, "synodus1": {
        "lemma": "synodus", "uri": None, "pos": "n", "morpho": "n-s---fn2-"
    }, "synodus2": {"lemma": "synodus", "uri": None, "pos": "n", "morpho": "n-s---fn2-"}, "syrus1": {
        "lemma": "syrus", "uri": "s4014", "pos": "n", "morpho": "n-s---mn2-"
    }, "Syrus2": {"lemma": "Syrus", "uri": "62309", "pos": "n", "morpho": "n-s---mn2-"}, "Syrus3": {
        "lemma": "Syrus", "uri": "62309", "pos": "n", "morpho": "n-s---mn2-"
    }, "tabularius1": {"lemma": "tabularius", "uri": "t0028", "pos": "a", "morpho": "aps---mn1-"}, "tabularius2": {
        "lemma": "tabularius", "uri": "t0028", "pos": "n", "morpho": "n-s---mn2-"
    }, "tacitus1": {"lemma": "tacitus", "uri": "58354", "pos": "a", "morpho": "aps---mn1-"}, "tactus1": {
        "lemma": "tactus", "uri": "129489", "pos": "a", "morpho": "aps---mn1-"
    }, "tactus2": {"lemma": "tactus", "uri": "t9994", "pos": "n", "morpho": "n-s---mn4-"}, "Tartarus1": {
        "lemma": "Tartarus", "uri": "62351", "pos": "a", "morpho": "aps---mn1-"
    }, "Tartarus2": {"lemma": "Tartarus", "uri": "62351", "pos": "a", "morpho": "aps---mn1-"}, "tau1": {
        "lemma": "tau", "uri": "t0144", "pos": "n", "morpho": "n-s---nn--"
    }, "tau2": {"lemma": "tau", "uri": "t0144", "pos": "n", "morpho": "n-s---nn--"}, "taurinus1": {
        "lemma": "taurinus", "uri": "t0153", "pos": "a", "morpho": "aps---mn1-"
    }, "Tauriscus1": {"lemma": "Tauriscus", "uri": "62357", "pos": "n", "morpho": "n-s---mn2-"}, "Tauriscus2": {
        "lemma": "Tauriscus", "uri": "62357", "pos": "n", "morpho": "n-s---mn2-"
    }, "taurus1": {"lemma": "taurus", "uri": "t0162", "pos": "n", "morpho": "n-s---mn2-"}, "Taurus2": {
        "lemma": "Taurus", "uri": "62360", "pos": "n", "morpho": "n-s---mn2-"
    }, "Taurus3": {"lemma": "Taurus", "uri": "62360", "pos": "n", "morpho": "n-s---mn2-"}, "taxim1": {
        "lemma": "taxim", "uri": "t0173", "pos": "r", "morpho": "rp--------"
    }, "taxim2": {"lemma": "taxim", "uri": "t0173", "pos": "r", "morpho": "rp--------"}, "telamo1": {
        "lemma": "telamo", "uri": "129623", "pos": "n", "morpho": "n-s---mn3-"
    }, "Telamo2": {"lemma": "Telamo", "uri": "62370", "pos": "n", "morpho": "n-s---nn3-"}, "Temenitis1": {
        "lemma": "Temenitis", "uri": "62389", "pos": "n", "morpho": "n-s---fn3-"
    }, "Temenitis2": {"lemma": "Temenitis", "uri": "62389", "pos": "n", "morpho": "n-s---fn3-"}, "temo1": {
        "lemma": "temo", "uri": "t0232", "pos": "n", "morpho": "n-s---mn3-"
    }, "temo2": {"lemma": "temo", "uri": "t0232", "pos": "n", "morpho": "n-s---mn3-"}, "tentus1": {
        "lemma": "tentus", "uri": "t9996", "pos": "n", "morpho": "n-s---mn4-"
    }, "tentus2": {"lemma": "tentus", "uri": "t9996", "pos": "n", "morpho": "n-s---mn4-"}, "tenus1": {
        "lemma": "tenus", "uri": "t9310", "pos": "n", "morpho": "n-s---nn3-"
    }, "tenus2": {"lemma": "tenus", "uri": "t9310", "pos": "n", "morpho": "n-s---nn3-"}, "termes1": {
        "lemma": "termes", "uri": "t0355", "pos": "n", "morpho": "n-s---mn3-"
    }, "termes2": {"lemma": "termes", "uri": "t0355", "pos": "n", "morpho": "n-s---mn3-"}, "Termes3": {
        "lemma": "Termes", "uri": "62407", "pos": "n", "morpho": "n-p---mn3-"
    }, "tersus1": {"lemma": "tersus", "uri": "33755", "pos": "a", "morpho": "aps---mn1-"}, "tersus2": {
        "lemma": "tersus", "uri": "t9999", "pos": "n", "morpho": "n-s---mn4-"
    }, "tertio1": {"lemma": "tertio", "uri": "57806", "pos": "r", "morpho": "rp--------"}, "tertio2": {
        "lemma": "tertio", "uri": "t0410", "pos": "v", "morpho": "v1spia--1-"
    }, "testis1": {"lemma": "testis", "uri": "t1502", "pos": "n", "morpho": "n-s---mn3i"}, "testis2": {
        "lemma": "testis", "uri": "t1502", "pos": "n", "morpho": "n-s---mn3i"
    }, "textus1": {"lemma": "textus", "uri": "129905", "pos": "a", "morpho": "aps---mn1-"}, "textus2": {
        "lemma": "textus", "uri": "t9914", "pos": "n", "morpho": "n-s---mn4-"
    }, "thymbra1": {"lemma": "thymbra", "uri": "t0639", "pos": "n", "morpho": "n-s---fn1-"}, "Thymbra2": {
        "lemma": "Thymbra", "uri": "62494", "pos": "n", "morpho": "n-s---fn1-"
    }, "Tifata1": {"lemma": "Tifata", "uri": "62511", "pos": "n", "morpho": "n-s---fn1-"}, "Tifata2": {
        "lemma": "Tifata", "uri": "62511", "pos": "n", "morpho": "n-s---fn1-"
    }, "tigris1": {"lemma": "tigris", "uri": "t0688", "pos": "n", "morpho": "n-s---cn3-"}, "tinctus1": {
        "lemma": "tinctus", "uri": "130090", "pos": "a", "morpho": "aps---mn1-"
    }, "tinctus2": {"lemma": "tinctus", "uri": "t9915", "pos": "n", "morpho": "n-s---mn4-"}, "tiro1": {
        "lemma": "tiro", "uri": "t0731", "pos": "n", "morpho": "n-s---mn3-"
    }, "Tiro2": {"lemma": "Tiro", "uri": "62527", "pos": "n", "morpho": "n-s---mn3-"}, "tonsus1": {
        "lemma": "tonsus", "uri": "54607", "pos": "a", "morpho": "aps---mn1-"
    }, "tonsus2": {"lemma": "tonsus", "uri": "t9919", "pos": "n", "morpho": "n-s---mn4-"}, "torquatus1": {
        "lemma": "torquatus", "uri": "t0859", "pos": "a", "morpho": "aps---mn1-"
    }, "tortus1": {"lemma": "tortus", "uri": "100903", "pos": "a", "morpho": "aps---mn1-"}, "tortus2": {
        "lemma": "tortus", "uri": "t9913", "pos": "n", "morpho": "n-s---mn4-"
    }, "totus1": {"lemma": "totus", "uri": "t9931", "pos": "a", "morpho": "aps---mn1p"}, "totus2": {
        "lemma": "totus", "uri": "t9931", "pos": "a", "morpho": "aps---mn1p"
    }, "trabea1": {"lemma": "trabea", "uri": "t0897", "pos": "n", "morpho": "n-s---fn1-"}, "Trabea2": {
        "lemma": "Trabea", "uri": "62555", "pos": "n", "morpho": "n-s---fn1-"
    }, "tractus1": {"lemma": "tractus", "uri": "130285", "pos": "a", "morpho": "aps---mn1-"}, "tractus2": {
        "lemma": "tractus", "uri": "t9993", "pos": "n", "morpho": "n-s---mn4-"
    }, "traditus1": {"lemma": "traditus", "uri": "130286", "pos": "a", "morpho": "aps---mn1-"}, "traditus2": {
        "lemma": "traditus", "uri": "t9921", "pos": "n", "morpho": "n-s---mn4-"
    }, "traductus1": {"lemma": "traductus", "uri": "130291", "pos": "a", "morpho": "aps---mn1-"}, "traductus2": {
        "lemma": "traductus", "uri": "t9922", "pos": "n", "morpho": "n-s---mn4-"
    }, "tragos1": {"lemma": "tragos", "uri": "130310", "pos": "n", "morpho": "n-s---mn2g"}, "tragos2": {
        "lemma": "tragos", "uri": "130310", "pos": "n", "morpho": "n-s---mn2g"
    }, "trajectus1": {"lemma": "traiectus", "uri": "36816", "pos": "a", "morpho": "aps---mn1-"}, "trajectus2": {
        "lemma": "traiectus", "uri": "t9923", "pos": "n", "morpho": "n-s---mn4-"
    }, "Tralles1": {"lemma": "Tralles", "uri": "62561", "pos": "n", "morpho": "n-p---mn3-"}, "Tralles2": {
        "lemma": "Tralles", "uri": "62561", "pos": "n", "morpho": "n-p---mn3-"
    }, "tranquillo1": {"lemma": "tranquillo", "uri": "130332", "pos": "r", "morpho": "rp--------"}, "tranquillo2": {
        "lemma": "tranquillo", "uri": "t0967", "pos": "v", "morpho": "v1spia--1-"
    }, "transcensus1": {"lemma": "transcensus", "uri": "130342", "pos": "a", "morpho": "aps---mn1-"}, "transcensus2": {
        "lemma": "transcensus", "uri": "t9924", "pos": "n", "morpho": "n-s---mn4-"
    }, "transcursus1": {"lemma": "transcursus", "uri": "130353", "pos": "a", "morpho": "aps---mn1-"}, "transcursus2": {
        "lemma": "transcursus", "uri": "t9925", "pos": "n", "morpho": "n-s---mn4-"
    }, "transgressus1": {"lemma": "transgressus", "uri": "130382", "pos": "a", "morpho": "aps---mn1-"},
    "transgressus2": {
        "lemma": "transgressus", "uri": "t9926", "pos": "n", "morpho": "n-s---mn4-"
    }, "transitus1": {"lemma": "transitus", "uri": "130394", "pos": "a", "morpho": "aps---mn1-"}, "transitus2": {
        "lemma": "transitus", "uri": "t9927", "pos": "n", "morpho": "n-s---mn4-"
    }, "translatus1": {"lemma": "translatus", "uri": "130404", "pos": "a", "morpho": "aps---mn1-"}, "translatus2": {
        "lemma": "translatus", "uri": "t9928", "pos": "n", "morpho": "n-s---mn4-"
    }, "transmissus1": {"lemma": "transmissus", "uri": "43825", "pos": "a", "morpho": "aps---mn1-"}, "transmissus2": {
        "lemma": "transmissus", "uri": "t9929", "pos": "n", "morpho": "n-s---mn4-"
    }, "Trebia1": {"lemma": "Trebia", "uri": "62571", "pos": "n", "morpho": "n-s---fn1-"}, "Trebia2": {
        "lemma": "Trebia", "uri": "62571", "pos": "n", "morpho": "n-s---fn1-"
    }, "tributus1": {"lemma": "tributus", "uri": "49498", "pos": "a", "morpho": "aps---mn1-"}, "tributus2": {
        "lemma": "tributus", "uri": "49498", "pos": "a", "morpho": "aps---mn1-"
    }, "tributus3": {"lemma": "tributus", "uri": "t1173", "pos": "n", "morpho": "n-s---mn2-"}, "trigonus1": {
        "lemma": "trigonus", "uri": None, "pos": "a", "morpho": "aps---mn1-"
    }, "trigonus2": {"lemma": "trigonus", "uri": "42299", "pos": "n", "morpho": "n-s---mn2-"}, "tritus1": {
        "lemma": "tritus", "uri": "27828", "pos": "a", "morpho": "aps---mn1-"
    }, "tritus2": {"lemma": "tritus", "uri": "t9930", "pos": "n", "morpho": "n-s---mn4-"}, "tropa1": {
        "lemma": "tropa", "uri": "t1437", "pos": "n", "morpho": "n-s---fn1-"
    }, "tropa2": {"lemma": "tropa", "uri": "t8437", "pos": "r", "morpho": "rp--------"}, "Tros1": {
        "lemma": "Tros", "uri": "62600", "pos": "n", "morpho": "n-s---mn2-"
    }, "Tros2": {"lemma": "Tros", "uri": "62600", "pos": "n", "morpho": "n-s---mn2-"}, "truncus1": {
        "lemma": "truncus", "uri": "t1466", "pos": "a", "morpho": "aps---mn1-"
    }, "truncus2": {"lemma": "truncus", "uri": "t1466", "pos": "n", "morpho": "n-s---mn2-"}, "tuber1": {
        "lemma": "tuber", "uri": "t1687", "pos": "n", "morpho": "n-s---nn3-"
    }, "tubulus1": {"lemma": "tubulus", "uri": "t1702", "pos": "n", "morpho": "n-s---mn2-"}, "tuor1": {
        "lemma": "tuor", "uri": "132802", "pos": "v", "morpho": "v1spid--3-"
    }, "tuor2": {"lemma": "tuor", "uri": "t1750", "pos": "n", "morpho": "n-s---mn3-"}, "turbo1": {
        "lemma": "turbo", "uri": "t1770", "pos": "v", "morpho": "v1spia--1-"
    }, "turbo2": {"lemma": "turbo", "uri": "t1771", "pos": "n", "morpho": "n-s---mn3-"}, "tusculum1": {
        "lemma": "tusculum", "uri": "t1822", "pos": "n", "morpho": "n-s---nn2-"
    }, "Tusculum2": {"lemma": "Tusculum", "uri": "62621", "pos": "n", "morpho": "n-s---nn2-"}, "tute1": {
        "lemma": "tute", "uri": "36734", "pos": "r", "morpho": "rp--------"
    }, "tute2": {"lemma": "tute", "uri": "36734", "pos": "r", "morpho": "rp--------"}, "tuto1": {
        "lemma": "tuto", "uri": "100998", "pos": "r", "morpho": "rp--------"
    }, "tuto2": {"lemma": "tuto", "uri": "27879", "pos": "v", "morpho": "v1spia--1-"}, "tutor1": {
        "lemma": "tutor", "uri": "t1842", "pos": "n", "morpho": "n-s---mn3-"
    }, "tutor2": {"lemma": "tutor", "uri": "t1843", "pos": "v", "morpho": "v1spid--1-"}, "typhon1": {
        "lemma": "typhon", "uri": "t1863", "pos": "n", "morpho": "n-s---mn3-"
    }, "uber1": {"lemma": "uber", "uri": "u9157", "pos": "n", "morpho": "n-s---nn3-"}, "uber2": {
        "lemma": "uber", "uri": "u9157", "pos": "a", "morpho": "aps---an3-"
    }, "udo1": {"lemma": "udo", "uri": "u0174", "pos": "v", "morpho": "v1spia--1-"}, "udo2": {
        "lemma": "udo", "uri": "u0175", "pos": "n", "morpho": "n-s---mn3-"
    }, "ultimo1": {"lemma": "ultimo", "uri": "101006", "pos": "r", "morpho": "rp--------"}, "ultimo2": {
        "lemma": "ultimo", "uri": "u0942", "pos": "v", "morpho": "v1spia--1-"
    }, "unctus1": {"lemma": "unctus", "uri": "43318", "pos": "a", "morpho": "aps---mn1-"}, "unctus2": {
        "lemma": "unctus", "uri": "u9984", "pos": "n", "morpho": "n-s---mn4-"
    }, "uncus1": {"lemma": "uncus", "uri": "u1026", "pos": "n", "morpho": "n-s---mn2-"}, "uncus2": {
        "lemma": "uncus", "uri": "u1026", "pos": "a", "morpho": "aps---mn1-"
    }, "unio1": {"lemma": "unio", "uri": "u1111", "pos": "v", "morpho": "v1spia--4-"}, "unio2": {
        "lemma": "unio", "uri": "u1112", "pos": "n", "morpho": "n-s---cn3-"
    }, "urbicus1": {"lemma": "urbicus", "uri": "u1241", "pos": "a", "morpho": "aps---mn1-"}, "Urbicus2": {
        "lemma": "Urbicus", "uri": "62644", "pos": "n", "morpho": "n-s---mn2-"
    }, "usucapio1": {"lemma": "usucapio", "uri": "u1302", "pos": "v", "morpho": "v1spia--3i"}, "usucapio2": {
        "lemma": "usucapio", "uri": "u1303", "pos": "n", "morpho": "n-s---fn3-"
    }, "usus1": {"lemma": "usus", "uri": "131976", "pos": "a", "morpho": "aps---mn1-"}, "usus2": {
        "lemma": "usus", "uri": "u9985", "pos": "n", "morpho": "n-s---mn4-"
    }, "ut1": {"lemma": "ut", "uri": "37549", "pos": "r", "morpho": "rp--------"},
    "ut2": {"lemma": "ut", "uri": "37549", "pos": "r", "morpho": "rp--------"},  # in the manner of
"ut3": {"lemma": "ut", "uri": "37549", "pos": "r", "morpho": "rp--------"},  # such as
    "Utens2": {"lemma": "Utens", "uri": "62648", "pos": "n", "morpho": "n-s---mn3-"}, "uter1": {
        "lemma": "uter", "uri": "131984", "pos": "n", "morpho": "n-s---mn2r"
    }, "uter2": {"lemma": "uter", "uri": "131984", "pos": "n", "morpho": "n-s---mn2r"}, "uter3": {
        "lemma": "uter", "uri": "33134", "pos": "a", "morpho": "aps---mn1p"
    }, "utique2": {"lemma": "utique", "uri": "u1332", "pos": "r", "morpho": "rp--------"}, "utriculus1": {
        "lemma": "utriculus", "uri": "u1340", "pos": "n", "morpho": "n-s---mn2-"
    }, "utriculus2": {"lemma": "utriculus", "uri": "u1340", "pos": "n", "morpho": "n-s---mn2-"}, "vacca1": {
        "lemma": "uacca", "uri": "u0003", "pos": "n", "morpho": "n-s---fn1-"
    }, "Vada1": {"lemma": "Vada", "uri": "62654", "pos": "n", "morpho": "n-s---fn1-"}, "Vada2": {
        "lemma": "Vada", "uri": "62654", "pos": "n", "morpho": "n-s---fn1-"
    }, "Vada3": {"lemma": "Vada", "uri": "62654", "pos": "n", "morpho": "n-s---fn1-"}, "vado1": {
        "lemma": "uado", "uri": "u0021", "pos": "v", "morpho": "v1spia--3-"
    }, "vado2": {"lemma": "uado", "uri": "u0024", "pos": "v", "morpho": "v1spia--1-"}, "vagor1": {
        "lemma": "uagor", "uri": "u0038", "pos": "v", "morpho": "v1spid--1-"
    }, "vagor2": {"lemma": "uagor", "uri": "u0039", "pos": "n", "morpho": "n-s---mn3-"}, "valens2": {
        "lemma": "ualens", "uri": "27976", "pos": "a", "morpho": "aps---an3i"
    }, "valentia1": {"lemma": "ualentia", "uri": "u0015", "pos": "n", "morpho": "n-s---fn1-"}, "Valentia2": {
        "lemma": "Valentia", "uri": "62661", "pos": "n", "morpho": "n-s---fn1-"
    }, "vallus1": {"lemma": "uallus", "uri": "u0067", "pos": "n", "morpho": "n-s---mn2-"}, "vallus2": {
        "lemma": "uallus", "uri": "u0068", "pos": "n", "morpho": "n-s---fn2-"
    }, "varia1": {"lemma": "uaria", "uri": "u0120", "pos": "n", "morpho": "n-s---fn1-"}, "varianus1": {
        "lemma": "uarianus", "uri": "u0108", "pos": "a", "morpho": "aps---mn1-"
    }, "varicus1": {"lemma": "uaricus", "uri": "u0115", "pos": "a", "morpho": "aps---mn1-"}, "varicus2": {
        "lemma": "uaricus", "uri": "u0116", "pos": "r", "morpho": "rp--------"
    }, "varo1": {"lemma": "uaro", "uri": "131012", "pos": "n", "morpho": "n-s---mn3-"}, "varo2": {
        "lemma": "uaro", "uri": "u0122", "pos": "v", "morpho": "v1spia--1-"
    }, "varus1": {"lemma": "uarus", "uri": "u0103", "pos": "a", "morpho": "aps---mn1-"}, "varus2": {
        "lemma": "uarus", "uri": "u0125", "pos": "n", "morpho": "n-s---mn2-"
    }, "Varus3": {"lemma": "Varus", "uri": "62673", "pos": "n", "morpho": "n-s---mn2-"}, "vas1": {
        "lemma": "uas", "uri": None, "pos": "n", "morpho": "n-s---mn3-"
    }, "vas2": {"lemma": "uas", "uri": None, "pos": "n", "morpho": "n-s---mn3-"}, "vectis1": {
        "lemma": "uectis", "uri": "u0191", "pos": "n", "morpho": "n-s---mn3i"
    }, "Vectis2": {"lemma": "Vectis", "uri": "62681", "pos": "n", "morpho": "n-s---fn3-"}, "Vedius1": {
        "lemma": "Vedius", "uri": "62683", "pos": "n", "morpho": "n-s---mn2-"
    }, "Vedius2": {"lemma": "Vedius", "uri": "62683", "pos": "n", "morpho": "n-s---mn2-"}, "velabrum1": {
        "lemma": "uelabrum", "uri": "u0221", "pos": "n", "morpho": "n-s---nn2-"
    }, "Velabrum2": {"lemma": "Velabrum", "uri": "62686", "pos": "a", "morpho": "aps---nn3-"}, "venilia1": {
        "lemma": "uenilia", "uri": "u0299", "pos": "n", "morpho": "n-s---fn1-"
    }, "Venilia2": {"lemma": "Venilia", "uri": "62697", "pos": "n", "morpho": "n-s---fn1-"}, "Venus1": {
        "lemma": "Venus", "uri": "28044", "pos": "n", "morpho": "n-s---fn3-"
    }, "venus2": {"lemma": "uenus", "uri": "u0470", "pos": "n", "morpho": "n-s---mn4-"}, "verbero1": {
        "lemma": "uerbero", "uri": "u0361", "pos": "v", "morpho": "v1spia--1-"
    }, "verbero2": {"lemma": "uerbero", "uri": "u0362", "pos": "n", "morpho": "n-s---mn3-"}, "vernus1": {
        "lemma": "uernus", "uri": "u0409", "pos": "a", "morpho": "aps---mn1-"
    }, "vernus2": {"lemma": "uernus", "uri": "u0409", "pos": "a", "morpho": "aps---mn1-"}, "vero1": {
        "lemma": "uero", "uri": "28066", "pos": "r", "morpho": "rp--------"
    }, "vero2": {"lemma": "uero", "uri": "u0410", "pos": "v", "morpho": "v1spia--1-"}, "vero3": {
        "lemma": "uero", "uri": "u0411", "pos": "n", "morpho": "n-s---mn3-"
    }, "verres1": {"lemma": "uerres", "uri": "u0414", "pos": "n", "morpho": "n-s---mn3i"}, "Verres2": {
        "lemma": "Verres", "uri": "62710", "pos": "n", "morpho": "n-p---mn3-"
    }, "verrinus1": {"lemma": "uerrinus", "uri": "u0416", "pos": "a", "morpho": "aps---mn1-"}, "versus3": {
        "lemma": "uersus", "uri": "u0516", "pos": "n", "morpho": "n-s---mn4-"
    }, "verum3": {"lemma": "uerum", "uri": "28081", "pos": "r", "morpho": "rp--------"}, "vestitus1": {
        "lemma": "uestitus", "uri": "101117", "pos": "a", "morpho": "aps---mn1-"
    }, "vestitus2": {"lemma": "uestitus", "uri": "u9983", "pos": "n", "morpho": "n-s---mn4-"}, "veternus1": {
        "lemma": "ueternus", "uri": "u0536", "pos": "a", "morpho": "aps---mn1-"
    }, "veternus2": {"lemma": "ueternus", "uri": "u0536", "pos": "n", "morpho": "n-s---mn2-"}, "Vibo2": {
        "lemma": "Vibo", "uri": "62731", "pos": "n", "morpho": "n-s---mn3-"
    }, "vibratus1": {"lemma": "uibratus", "uri": "131384", "pos": "a", "morpho": "aps---mn1-"}, "vibratus2": {
        "lemma": "uibratus", "uri": "u9229", "pos": "n", "morpho": "n-s---mn4-"
    }, "victor1": {"lemma": "uictor", "uri": "u0614", "pos": "n", "morpho": "n-s---mn3-"}, "victoriatus1": {
        "lemma": "uictoriatus", "uri": "u0617", "pos": "n", "morpho": "n-s---mn2-"
    }, "victoriatus2": {"lemma": "uictoriatus", "uri": "u0617", "pos": "a", "morpho": "aps---mn1-"}, "victus1": {
        "lemma": "uictus", "uri": "131429", "pos": "a", "morpho": "aps---mn1-"
    }, "victus2": {"lemma": "uictus", "uri": "u9986", "pos": "n", "morpho": "n-s---mn4-"}, "vilico2": {
        "lemma": "uilico", "uri": "u0656", "pos": "n", "morpho": "n-s---mn3-"
    }, "vinctus1": {"lemma": "uinctus", "uri": "131487", "pos": "a", "morpho": "aps---mn1-"}, "vinctus2": {
        "lemma": "uinctus", "uri": "u0666", "pos": "n", "morpho": "n-s---mn4-"
    }, "violatus1": {"lemma": "uiolatus", "uri": "131519", "pos": "a", "morpho": "aps---mn1-"}, "violatus2": {
        "lemma": "uiolatus", "uri": "131519", "pos": "a", "morpho": "aps---mn1-"
    }, "viratus1": {"lemma": "uiratus", "uri": "131526", "pos": "a", "morpho": "aps---mn1-"}, "viratus2": {
        "lemma": "uiratus", "uri": "u0755", "pos": "n", "morpho": "n-s---mn4-"
    }, "vireo1": {"lemma": "uireo", "uri": "u0757", "pos": "v", "morpho": "v1spia--2-"}, "vireo2": {
        "lemma": "uireo", "uri": "u0758", "pos": "n", "morpho": "n-s---mn3-"
    }, "viripotens1": {"lemma": "uiripotens", "uri": "u7505", "pos": "a", "morpho": "aps---an3i"}, "viripotens2": {
        "lemma": "uiripotens", "uri": "u7505", "pos": "a", "morpho": "aps---an3i"
    }, "viscus1": {"lemma": "uiscus", "uri": "u0816", "pos": "n", "morpho": "n-s---nn3-"}, "viscus2": {
        "lemma": "uiscus", "uri": "u0816", "pos": "n", "morpho": "n-s---nn3-"
    }, "visus1": {"lemma": "uisus", "uri": "131591", "pos": "a", "morpho": "aps---mn1-"}, "visus2": {
        "lemma": "uisus", "uri": "u9988", "pos": "n", "morpho": "n-s---mn4-"
    }, "vitula1": {"lemma": "uitula", "uri": "u0889", "pos": "n", "morpho": "n-s---fn1-"}, "vitupero1": {
        "lemma": "uitupero", "uri": "u0894", "pos": "v", "morpho": "v1spia--1-"
    }, "vitupero2": {"lemma": "uitupero", "uri": "u0895", "pos": "n", "morpho": "n-s---mn3-"},
    "volo1": {
        "lemma": "uolo", "uri": "u1167", "pos": "v", "morpho": "v1spia--3-"
    },
    "volo2": {
        "lemma": "uolo", "uri": "u1168", "pos": "v", "morpho": "v1spia--1-"
    },
    "volo3": {"lemma": "uolo", "uri": "u1169", "pos": "n", "morpho": "n-s---mn3-"}, "volutus1": {
        "lemma": "uolutus", "uri": "131872", "pos": "a", "morpho": "aps---mn1-"
    }, "volutus2": {"lemma": "uolutus", "uri": "u9994", "pos": "n", "morpho": "n-s---mn4-"}, "vopiscus1": {
        "lemma": "uopiscus", "uri": "u1215", "pos": "n", "morpho": "n-s---mn2-"
    }, "vulgatus1": {"lemma": "uulgatus", "uri": "28215", "pos": "a", "morpho": "aps---mn1-"}, "vulgatus2": {
        "lemma": "uulgatus", "uri": "u1335", "pos": "n", "morpho": "n-s---mn4-"
    }, "vulgo1": {"lemma": "uulgo", "uri": "u1364", "pos": "r", "morpho": "rp--------"}, "vulgo2": {
        "lemma": "uulgo", "uri": "u1363", "pos": "v", "morpho": "v1spia--1-"
    }, "vultur1": {"lemma": "uultur", "uri": "u1383", "pos": "n", "morpho": "n-s---mn3-"}, "Vultur2": {
        "lemma": "Vultur", "uri": "62765", "pos": "n", "morpho": "n-s---mn3-"
    }, "zeta1": {"lemma": "zeta", "uri": "56123", "pos": "n", "morpho": "n-s---nn3-"}, "zeta2": {
        "lemma": "zeta", "uri": "56123", "pos": "n", "morpho": "n-s---nn3-"
    }, "zeugma1": {"lemma": "zeugma", "uri": "z0023", "pos": "n", "morpho": "n-s---nn3-"}, "Zeugma2": {
        "lemma": "Zeugma", "uri": "62791", "pos": "n", "morpho": "n-s---fn1-"
    }, "zoster1": {"lemma": "zoster", "uri": "z0047", "pos": "n", "morpho": "n-s---mn3-"}, "Zoster2": {
        "lemma": "Zoster", "uri": "62795", "pos": "n", "morpho": "n-s---mn2r"
    }, "zygia1": {"lemma": "zygia", "uri": "z0052", "pos": "n", "morpho": "n-s---fn1-"}
}
