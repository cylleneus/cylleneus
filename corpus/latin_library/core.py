import codecs
import re
from pathlib import Path

import settings


def get(hit, meta, fragment):
    with codecs.open(
        Path(
            settings.ROOT_DIR + '/corpus/latin_library/text/' + hit['filename']
        )
    ) as fp:
        content = fp.read()

    # Do some tidying up
    subs = [
        (r"\.,", "."),
        (r"([\w])\.([\w])", r"\1. \2"),
        (r",([\w])", r", \1"),
        (r"(?<=\w)\.\.", r" . ."),
        (r"([.,;:])([.,;:])", r"\1 \2"),
        (r"[\t\r\n ]+", " "),
        (r'\.\"', r'\"\.'),
        (r' ,', ','),
        (r'\[ \d+ \] ', ''),
        (r' \[,', '[,'),
        (r'\]\.', '.]')
    ]
    for pattern, repl in subs:
        content = re.sub(pattern, repl, content)
    offset = content.find(fragment)

    # Reference and hlite values
    start = ', '.join(
        [f"{k}: {v}" for k, v in meta['start'].items() if v]
    )
    end = ', '.join(
        [f"{k}: {v}" for k, v in meta['end'].items() if v]
    )
    reference = '-'.join([start, end]) if end != start else start

    hlite_starts = [
        startchar
        for startchar, endchar, pos in meta['hlites']
    ]
    hlite_ends = [
        endchar
        for startchar, endchar, pos in meta['hlites']
    ]

    # Collect text and context
    lbound = fragment.rfind(' ', 0, settings.CHARS_OF_CONTEXT)
    rbound = fragment.find(' ', -settings.CHARS_OF_CONTEXT)

    pre = f"<pre>{fragment[:lbound]}</pre>"
    post = f"<post>{fragment[rbound + 1:]}</post>"

    hlite = ''
    cursor = lbound + offset - 1
    for c in fragment[lbound + 1:rbound]:
        if cursor in hlite_starts:
            hlite += '<em>' + c
        elif cursor in hlite_ends:
            hlite += '</em>' + c
        else:
            hlite += c
        cursor += 1
    if cursor in hlite_ends:
        hlite += '</em>'
    match = f"<match>{hlite}</match>"

    text = f' '.join([pre, match, post])

    urn = hit.get('urn', None)

    return urn, reference, text


FILE_TAB = {
    "12tables.txt":                              {"fileid": 0, "author": None, "title": "DUODECIM TABULARUM LEGES"},
    "1644.txt":                                  {
        "fileid": 1, "author": None, "title": "Cafraria"
    }, "abbofloracensis.txt":                    {
        "fileid": 2, "author": None,
        "title":  "Abbo Floriacensis"
    }, "abelard/dialogus.txt":                   {
        "fileid": 3, "author": "PETRUS ABAELARDUS",
        "title":  "DIALOGUS INTER PHILOSOPHUM, IUDAEUM ET CHRISTIANUM"
    }, "abelard/epistola.txt":                   {
        "fileid": 4,
        "author": "PETRUS ABAELARDUS", "title": "HELOYSAE EPISTOLA AD ABELARDUM"
    }, "abelard/historia.txt":                   {
        "fileid": 5, "author": "PETRUS ABAELARDUS", "title": "AD AMICUM SUUM CONSOLATORIA"
    }, "addison/barometri.txt":                  {
        "fileid": 6, "author": "JOSEPHUS ADDISON", "title": "BAROMETRI DESCRIPTIO"
    }, "addison/burnett.txt":                    {
        "fileid": 7, "author": "JOSEPHUS ADDISON", "title": "AD INSIGNISSIMUM VIRUM"
    }, "addison/hannes.txt":                     {"fileid": 8, "author": "Joseph Addison", "title": ""},
    "addison/machinae.txt":                      {"fileid": 9, "author": None, "title": "Joseph Addison "},
    "addison/pax.txt":                           {"fileid": 10, "author": "Joseph Addison", "title": "Pax Gulielmi "},
    "addison/praelium.txt":                      {"fileid": 11, "author": None, "title": "Joseph Addison "},
    "addison/preface.txt":                       {
        "fileid": 12, "author": "Addison", "title": "Preface and Dedication "
    }, "addison/resurr.txt":                     {"fileid": 13, "author": None, "title": "Joseph Addison "},
    "addison/sphaer.txt":                        {"fileid": 14, "author": "Joseph Addison", "title": "Sphaeristerium "},
    "adso.txt":                                  {"fileid": 15, "author": None, "title": "Adso Deruensis"},
    "aelredus.txt":                              {
        "fileid": 16, "author": "Aelredus Rievallensis", "title": "de Amicitia"
    }, "agnes.txt":                              {"fileid": 17, "author": None, "title": "Blessed Agnes of Bohemia"},
    "alanus/alanus1.txt":                        {
        "fileid": 18, "author": "Alanus de Insulis", "title": "Liber de plantcu naturae"
    }, "alanus/alanus2.txt":                     {
        "fileid": 19, "author": "Alanus de Insulis", "title": "Anticlaudianus"
    }, "albertanus/albertanus.arsloquendi.txt":  {"fileid": 20, "author": None, "title": "Albertano of Brescia"},
    "albertanus/albertanus.liberconsol.txt":     {"fileid": 21, "author": None, "title": "Albertano of Brescia "},
    "albertanus/albertanus.sermo.txt":           {"fileid": 22, "author": None, "title": "Albertano of Brescia "},
    "albertanus/albertanus.sermo1.txt":          {"fileid": 23, "author": None, "title": "Albertano of Brescia "},
    "albertanus/albertanus.sermo2.txt":          {"fileid": 24, "author": None, "title": "Albertano of Brescia "},
    "albertanus/albertanus.sermo3.txt":          {"fileid": 25, "author": None, "title": "Albertano of Brescia "},
    "albertanus/albertanus.sermo4.txt":          {"fileid": 26, "author": None, "title": "Albertano of Brescia "},
    "albertanus/albertanus1.txt":                {"fileid": 27, "author": None, "title": "Albertano of Brescia "},
    "albertanus/albertanus2.txt":                {"fileid": 28, "author": None, "title": "Albertano of Brescia "},
    "albertanus/albertanus3.txt":                {"fileid": 29, "author": None, "title": "Albertano of Brescia "},
    "albertanus/albertanus4.txt":                {"fileid": 30, "author": None, "title": "Albertano of Brescia "},
    "albertofaix/hist1.txt":                     {
        "fileid": 31, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "albertofaix/hist10.txt":                 {
        "fileid": 32, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "albertofaix/hist11.txt":                 {
        "fileid": 33, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "albertofaix/hist12.txt":                 {
        "fileid": 34, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "albertofaix/hist2.txt":                  {
        "fileid": 35, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "albertofaix/hist3.txt":                  {
        "fileid": 36, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "albertofaix/hist4.txt":                  {
        "fileid": 37, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "albertofaix/hist5.txt":                  {
        "fileid": 38, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "albertofaix/hist6.txt":                  {
        "fileid": 39, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "albertofaix/hist7.txt":                  {
        "fileid": 40, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "albertofaix/hist8.txt":                  {
        "fileid": 41, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "albertofaix/hist9.txt":                  {
        "fileid": 42, "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis"
    }, "alcuin/cella.txt":                       {"fileid": 43, "author": "[Fredugis]", "title": "Cella Alcuini"},
    "alcuin/conflictus.txt":                     {
        "fileid": 44, "author": "Alcuin", "title": "Conflictus Veris et Hiemis"
    }, "alcuin/epitaphium.txt":                  {"fileid": 45, "author": "Alcuin", "title": "Epitaphium"},
    "alcuin/luscinia.txt":                       {"fileid": 46, "author": "Alcuin", "title": "de Luscinia"},
    "alcuin/propos.txt":                         {"fileid": 47, "author": "Alcuin", "title": "Propositiones "},
    "alcuin/rec.txt":                            {
        "fileid": 48, "author": "Alcuin", "title": "Letter of Recommendation"
    }, "alcuin/rhetorica.txt":                   {"fileid": 49, "author": "Alcuin", "title": "Disputatio de Rhetorica"},
    "alcuin/sequentia.txt":                      {
        "fileid": 50, "author": "Alcuin", "title": "Sequentia de Sancto Michaele"
    }, "alcuin/versus.txt":                      {"fileid": 51, "author": "Alcuin", "title": "Versus de Cuculo"},
    "alfonsi.disciplina.txt":                    {
        "fileid": 52, "author": "Peter Alfonsi", "title": "Disciplina clericalis"
    }, "ambrose/epist.txt":                      {
        "fileid": 53, "author": "Ambrosius", "title": "ad sororem Marcellinam"
    }, "ambrose/epistvaria.txt":                 {"fileid": 54, "author": "Ambrosi", "title": "Epistulae Variae"},
    "ambrose/hymns.txt":                         {"fileid": 55, "author": "Ambrosius", "title": "Hymni"},
    "ambrose/mysteriis.txt":                     {"fileid": 56, "author": "Ambrosius", "title": "de Mysteriis"},
    "ammianus/14.txt":                           {"fileid": 57, "author": "Ammianus", "title": "Liber XIV"},
    "ammianus/15.txt":                           {"fileid": 58, "author": "Ammianus", "title": "Liber XV"},
    "ammianus/16.txt":                           {"fileid": 59, "author": "Ammianus", "title": "Liber XVI"},
    "ammianus/17.txt":                           {"fileid": 60, "author": "Ammianus", "title": "Liber XVII"},
    "ammianus/18.txt":                           {"fileid": 61, "author": "Ammianus", "title": "Liber XVIII"},
    "ammianus/19.txt":                           {"fileid": 62, "author": "Ammianus", "title": "Liber XIX"},
    "ammianus/20.txt":                           {"fileid": 63, "author": "Ammianus", "title": "Liber XX"},
    "ammianus/21.txt":                           {"fileid": 64, "author": "Ammianus", "title": "Liber XXI"},
    "ammianus/22.txt":                           {"fileid": 65, "author": "Ammianus", "title": "Liber XXII"},
    "ammianus/23.txt":                           {"fileid": 66, "author": "Ammianus", "title": "Liber XXIII"},
    "ammianus/24.txt":                           {"fileid": 67, "author": "Ammianus", "title": "Liber XVIV"},
    "ammianus/25.txt":                           {"fileid": 68, "author": "Ammianus", "title": "Liber XXV"},
    "ammianus/26.txt":                           {"fileid": 69, "author": "Ammianus", "title": "Liber XXVI"},
    "ammianus/27.txt":                           {"fileid": 70, "author": "Ammianus", "title": "Liber XXVII"},
    "ammianus/28.txt":                           {"fileid": 71, "author": "Ammianus", "title": "Liber XXVIII"},
    "ammianus/29.txt":                           {"fileid": 72, "author": "Ammianus", "title": "Liber XXIX"},
    "ammianus/30.txt":                           {"fileid": 73, "author": "Ammianus", "title": "Liber XXX"},
    "ammianus/31.txt":                           {"fileid": 74, "author": "Ammianus", "title": "Liber XXXI"},
    "ampelius.txt":                              {"fileid": 75, "author": "Ampelius", "title": "Liber Memorialis"},
    "andecavis.txt":                             {"fileid": 76, "author": None, "title": "Andecavis Abbas "},
    "andreasbergoma.txt":                        {"fileid": 77, "author": None, "title": "Andreas of Bergoma"},
    "andronicus.txt":                            {"fileid": 78, "author": "Livius Andronicus", "title": "Odussia"},
    "angilbert.txt":                             {"fileid": 79, "author": None, "title": "Angilbert"},
    "annalesregnifrancorum.txt":                 {"fileid": 80, "author": None, "title": "Annesl Regni Francorum"},
    "annalesvedastini.txt":                      {"fileid": 81, "author": None, "title": "Annales Vedastini"},
    "anon.deramis.txt":                          {
        "fileid": 82, "author": None, "title": "Carmen de Martyrio Maccabaeorum"
    }, "anon.martyrio.txt":                      {
        "fileid": 83, "author": None, "title": "Carmen de Martyrio Maccabaeorum"
    }, "anon.nev.txt":                           {"fileid": 84, "author": None, "title": "Anonymus Neveleti"},
    "anselmepistula.txt":                        {"fileid": 85, "author": None, "title": "Anselm"},
    "anselmproslogion.txt":                      {"fileid": 86, "author": None, "title": "Anselm"},
    "apicius/apicius1.txt":                      {
        "fileid": 87, "author": "Apicius", "title": "de Re Coquinaria Liber I"
    }, "apicius/apicius2.txt":                   {
        "fileid": 88, "author": "Apicius", "title": "de Re Coquinaria Liber II"
    }, "apicius/apicius3.txt":                   {
        "fileid": 89, "author": "Apicius", "title": "de Re Coquinaria Liber III"
    }, "apicius/apicius4.txt":                   {
        "fileid": 90, "author": "Apicius", "title": "de Re Coquinaria Liber IV"
    }, "apicius/apicius5.txt":                   {
        "fileid": 91, "author": "Apicius", "title": "de Re Coquinaria Liber V"
    }, "appverg.aetna.txt":                      {"fileid": 92, "author": "Appendix Vergiliana", "title": "Aetna  "},
    "appverg.catalepton.txt":                    {
        "fileid": 93, "author": "Appendix Vergiliana", "title": "Catalepton  "
    }, "appverg.ciris.txt":                      {"fileid": 94, "author": "Appendix Vergiliana", "title": "Ciris  "},
    "appvergcomp.txt":                           {"fileid": 95, "author": None, "title": "Appendix Vergiliana"},
    "appvergculex.txt":                          {"fileid": 96, "author": "Appendix Vergiliana", "title": "Culex"},
    "apuleius/apuleius.apol.txt":                {"fileid": 97, "author": "Apuleius", "title": "Apology"},
    "apuleius/apuleius.cupid.txt":               {"fileid": 98, "author": "Apuleius", "title": "Cupid and Psyche"},
    "apuleius/apuleius.deosocratis.txt":         {"fileid": 99, "author": "Apuleius", "title": "de Deo Socratis"},
    "apuleius/apuleius.dog1.txt":                {
        "fileid": 100, "author": "Apuleius", "title": "de Dogmate Platonis I"
    }, "apuleius/apuleius.dog2.txt":             {
        "fileid": 101, "author": "Apuleius", "title": "de Dogmate Platonis II"
    }, "apuleius/apuleius.florida.txt":          {"fileid": 102, "author": "Apuleius", "title": "Florida"},
    "apuleius/apuleius.mundo.txt":               {"fileid": 103, "author": "Apuleius", "title": "de Mundo"},
    "apuleius/apuleius1.txt":                    {"fileid": 104, "author": "Metamorphoses", "title": "Liber I"},
    "apuleius/apuleius10.txt":                   {"fileid": 105, "author": "Metamorphoses", "title": "Liber X"},
    "apuleius/apuleius11.txt":                   {"fileid": 106, "author": "Metamorphoses", "title": "Liber XI"},
    "apuleius/apuleius2.txt":                    {"fileid": 107, "author": "Metamorphoses", "title": "Liber II"},
    "apuleius/apuleius3.txt":                    {"fileid": 108, "author": "Metamorphoses", "title": "Liber III"},
    "apuleius/apuleius4.txt":                    {"fileid": 109, "author": "Metamorphoses", "title": "Liber IV"},
    "apuleius/apuleius5.txt":                    {"fileid": 110, "author": "Metamorphoses", "title": "Liber V"},
    "apuleius/apuleius6.txt":                    {"fileid": 111, "author": "Metamorphoses", "title": "Liber VI"},
    "apuleius/apuleius7.txt":                    {"fileid": 112, "author": "Metamorphoses", "title": "Liber VII"},
    "apuleius/apuleius8.txt":                    {"fileid": 113, "author": "Metamorphoses", "title": "Liber VIII"},
    "apuleius/apuleius9.txt":                    {"fileid": 114, "author": "Metamorphoses", "title": "Liber IX"},
    "aquinas/corpuschristi.txt":                 {
        "fileid": 115, "author": "St. Thomas Aquinas",
        "title":  "Corpus Christi  CORPUS CHRISTI   Verbum supernum prodiens,  Nec Patris linquens dexteram, "
                  "Ad opus suum exiens,  Venit advitae vesperam. In mortem a discipulo  Suis tradendus aemulis, Prius in vitae "
                  "ferculo  Se tradidit discipulis. Quibus sub bina specie  Carnem dedit et sanguinem: Ut duplicis substantiae  "
                  "Totum cibaret hominem. Se nascens dedit socium,  Convescens in edulium, Se moriens in pretium,  Se regnans "
                  "dat in praemium. O Salutaris Hostia,  Quae caeli pandis ostium: Bella premunt hostilia,  Da robur, "
                  "fer auxilium. Uni trinoque Domino  Sit sempiterna gloria, Qui vitam sine termino  Nobis donet in patria. "
                  "Amen.  "
    }, "aquinas/ente.txt":                       {
        "fileid": 116, "author": None, "title": "St. Thomas Aquinas De Ente et Essentia "
    }, "aquinas/epist.txt":                      {
        "fileid": 117, "author": "St. Thomas Aquinas", "title": "Epistola de Modo Studendi "
    }, "aquinas/expositio.txt":                  {
        "fileid": 118, "author": "St. Thomas Aquinas", "title": "Expositio in Orationem Dominicam"
    }, "aquinas/p1.txt":                         {
        "fileid": 119, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars "
    }, "aquinas/princ.txt":                      {
        "fileid": 120, "author": "St. Thomas Aquinas", "title": "De Principio Individuationis "
    }, "aquinas/prologus.txt":                   {
        "fileid": 121, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prologus "
    }, "aquinas/q1.1.txt":                       {
        "fileid": 122, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio I "
    }, "aquinas/q1.10.txt":                      {
        "fileid": 123, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio X "
    }, "aquinas/q1.11.txt":                      {
        "fileid": 124, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XI "
    }, "aquinas/q1.12.txt":                      {
        "fileid": 125, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XII "
    }, "aquinas/q1.13.txt":                      {
        "fileid": 126, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XIII "
    }, "aquinas/q1.14.txt":                      {
        "fileid": 127, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XIV "
    }, "aquinas/q1.15.txt":                      {
        "fileid": 128, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XV "
    }, "aquinas/q1.16.txt":                      {
        "fileid": 129, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XVI "
    }, "aquinas/q1.17.txt":                      {
        "fileid": 130, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XVII "
    }, "aquinas/q1.18.txt":                      {
        "fileid": 131, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XVIII "
    }, "aquinas/q1.19.txt":                      {
        "fileid": 132, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XIX "
    }, "aquinas/q1.2.txt":                       {
        "fileid": 133, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio II "
    }, "aquinas/q1.20.txt":                      {
        "fileid": 134, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XX "
    }, "aquinas/q1.21.txt":                      {
        "fileid": 135, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXI "
    }, "aquinas/q1.22.txt":                      {
        "fileid": 136, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXII "
    }, "aquinas/q1.23.txt":                      {
        "fileid": 137, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXIII "
    }, "aquinas/q1.24.txt":                      {
        "fileid": 138, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXIV "
    }, "aquinas/q1.25.txt":                      {
        "fileid": 139, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXV "
    }, "aquinas/q1.26.txt":                      {
        "fileid": 140, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXIVI "
    }, "aquinas/q1.27.txt":                      {
        "fileid": 141, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXVII "
    }, "aquinas/q1.28.txt":                      {
        "fileid": 142, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXVIII "
    }, "aquinas/q1.29.txt":                      {
        "fileid": 143, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXIX "
    }, "aquinas/q1.3.txt":                       {
        "fileid": 144, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio III "
    }, "aquinas/q1.30.txt":                      {
        "fileid": 145, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXX "
    }, "aquinas/q1.31.txt":                      {
        "fileid": 146, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXI "
    }, "aquinas/q1.32.txt":                      {
        "fileid": 147, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXII "
    }, "aquinas/q1.33.txt":                      {
        "fileid": 148, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXIII "
    }, "aquinas/q1.34.txt":                      {
        "fileid": 149, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXIV "
    }, "aquinas/q1.35.txt":                      {
        "fileid": 150, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXV "
    }, "aquinas/q1.36.txt":                      {
        "fileid": 151, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXVI "
    }, "aquinas/q1.37.txt":                      {
        "fileid": 152, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXVII "
    }, "aquinas/q1.38.txt":                      {
        "fileid": 153, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXVIII "
    }, "aquinas/q1.39.txt":                      {
        "fileid": 154, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXIX "
    }, "aquinas/q1.4.txt":                       {
        "fileid": 155, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio IV "
    }, "aquinas/q1.40.txt":                      {
        "fileid": 156, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XL "
    }, "aquinas/q1.41.txt":                      {
        "fileid": 157, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLI "
    }, "aquinas/q1.42.txt":                      {
        "fileid": 158, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLII "
    }, "aquinas/q1.43.txt":                      {
        "fileid": 159, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLIII "
    }, "aquinas/q1.44.txt":                      {
        "fileid": 160, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLIV "
    }, "aquinas/q1.45.txt":                      {
        "fileid": 161, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLV "
    }, "aquinas/q1.46.txt":                      {
        "fileid": 162, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLVI "
    }, "aquinas/q1.47.txt":                      {
        "fileid": 163, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLVII "
    }, "aquinas/q1.48.txt":                      {
        "fileid": 164, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLVIII "
    }, "aquinas/q1.49.txt":                      {
        "fileid": 165, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLIX "
    }, "aquinas/q1.5.txt":                       {
        "fileid": 166, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio V "
    }, "aquinas/q1.50.txt":                      {
        "fileid": 167, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio L "
    }, "aquinas/q1.51.txt":                      {
        "fileid": 168, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LI "
    }, "aquinas/q1.52.txt":                      {
        "fileid": 169, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LII "
    }, "aquinas/q1.53.txt":                      {
        "fileid": 170, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LIII "
    }, "aquinas/q1.54.txt":                      {
        "fileid": 171, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LIV "
    }, "aquinas/q1.55.txt":                      {
        "fileid": 172, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LV "
    }, "aquinas/q1.56.txt":                      {
        "fileid": 173, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LVI "
    }, "aquinas/q1.57.txt":                      {
        "fileid": 174, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LIVII "
    }, "aquinas/q1.58.txt":                      {
        "fileid": 175, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LVIII "
    }, "aquinas/q1.59.txt":                      {
        "fileid": 176, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LIX "
    }, "aquinas/q1.6.txt":                       {
        "fileid": 177, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio VI "
    }, "aquinas/q1.60.txt":                      {
        "fileid": 178, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LX "
    }, "aquinas/q1.61.txt":                      {
        "fileid": 179, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXI "
    }, "aquinas/q1.62.txt":                      {
        "fileid": 180, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXII "
    }, "aquinas/q1.63.txt":                      {
        "fileid": 181, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXIII "
    }, "aquinas/q1.64.txt":                      {
        "fileid": 182, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXIV "
    }, "aquinas/q1.65.txt":                      {
        "fileid": 183, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXV "
    }, "aquinas/q1.66.txt":                      {
        "fileid": 184, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXVI "
    }, "aquinas/q1.67.txt":                      {
        "fileid": 185, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXVII "
    }, "aquinas/q1.68.txt":                      {
        "fileid": 186, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXVIII "
    }, "aquinas/q1.69.txt":                      {
        "fileid": 187, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXIX "
    }, "aquinas/q1.7.txt":                       {
        "fileid": 188, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio VII "
    }, "aquinas/q1.70.txt":                      {
        "fileid": 189, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXX "
    }, "aquinas/q1.71.txt":                      {
        "fileid": 190, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXI "
    }, "aquinas/q1.72.txt":                      {
        "fileid": 191, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXII "
    }, "aquinas/q1.73.txt":                      {
        "fileid": 192, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXIII "
    }, "aquinas/q1.74.txt":                      {
        "fileid": 193, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXIV "
    }, "aquinas/q1.8.txt":                       {
        "fileid": 194, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio VIII "
    }, "aquinas/q1.80.txt":                      {
        "fileid": 195, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXX "
    }, "aquinas/q1.81.txt":                      {
        "fileid": 196, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXXI "
    }, "aquinas/q1.82.txt":                      {
        "fileid": 197, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXXII "
    }, "aquinas/q1.83.txt":                      {
        "fileid": 198, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXXIII "
    }, "aquinas/q1.86.txt":                      {
        "fileid": 199, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXXVI "
    }, "aquinas/q1.87.txt":                      {
        "fileid": 200, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXXVII "
    }, "aquinas/q1.9.txt":                       {
        "fileid": 201, "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio IX "
    }, "arbroath.txt":                           {"fileid": 202, "author": None, "title": "Declaration of Arbroath"},
    "archpoet.txt":                              {"fileid": 203, "author": None, "title": "Archpoeta"},
    "arnobius/arnobius1.txt":                    {
        "fileid": 204, "author": "Arnobius", "title": "Adversus Nationes Liber I"
    }, "arnobius/arnobius2.txt":                 {
        "fileid": 205, "author": "Arnobius", "title": "Adversus Nationes Liber II"
    }, "arnobius/arnobius3.txt":                 {
        "fileid": 206, "author": "Arnobius", "title": "Adversus Nationes Liber III"
    }, "arnobius/arnobius4.txt":                 {
        "fileid": 207, "author": "Arnobius", "title": "Adversus Nationes Liber IV"
    }, "arnobius/arnobius5.txt":                 {
        "fileid": 208, "author": "Arnobius", "title": "Adversus Nationes Liber V"
    }, "arnobius/arnobius6.txt":                 {
        "fileid": 209, "author": "Arnobius", "title": "Adversus Nationes Liber VI"
    }, "arnobius/arnobius7.txt":                 {
        "fileid": 210, "author": "Arnobius", "title": "Adversus Nationes Liber VII"
    }, "arnulf.txt":                             {
        "fileid": 211, "author": "Arnulf of Lisieux", "title": "De Nativitate Domini"
    }, "asconius.txt":                           {"fileid": 212, "author": None, "title": "Asconius"},
    "asserius.txt":                              {"fileid": 213, "author": "Asserius", "title": "Life of Alfred"},
    "augustine/catechizandis.txt":               {
        "fileid": 214, "author": "Augustinus", "title": "de Catechizandis Rudibus"
    }, "augustine/civ1.txt":                     {
        "fileid": 215, "author": "Augustine", "title": "De Civitate Dei Liber I"
    }, "augustine/civ10.txt":                    {
        "fileid": 216, "author": "Augustine", "title": "De Civitate Dei Liber X"
    }, "augustine/civ11.txt":                    {
        "fileid": 217, "author": "Augustine", "title": "De Civitate Dei Liber XI"
    }, "augustine/civ12.txt":                    {
        "fileid": 218, "author": "Augustine", "title": "De Civitate Dei Liber XII"
    }, "augustine/civ13.txt":                    {
        "fileid": 219, "author": "Augustine", "title": "De Civitate Dei Liber XIII"
    }, "augustine/civ14.txt":                    {
        "fileid": 220, "author": "Augustine", "title": "De Civitate Dei Liber XIV"
    }, "augustine/civ15.txt":                    {
        "fileid": 221, "author": "Augustine", "title": "De Civitate Dei Liber XV"
    }, "augustine/civ16.txt":                    {
        "fileid": 222, "author": "Augustine", "title": "De Civitate Dei Liber XVI"
    }, "augustine/civ17.txt":                    {
        "fileid": 223, "author": "Augustine", "title": "De Civitate Dei Liber XVII"
    }, "augustine/civ18.txt":                    {
        "fileid": 224, "author": "Augustine", "title": "De Civitate Dei Liber XVIII"
    }, "augustine/civ19.txt":                    {
        "fileid": 225, "author": "Augustine", "title": "De Civitate Dei Liber XIX"
    }, "augustine/civ2.txt":                     {
        "fileid": 226, "author": "Augustine", "title": "De Civitate Dei Liber II"
    }, "augustine/civ20.txt":                    {
        "fileid": 227, "author": "Augustine", "title": "De Civitate Dei Liber XX"
    }, "augustine/civ21.txt":                    {
        "fileid": 228, "author": "Augustine", "title": "De Civitate Dei Liber XXI"
    }, "augustine/civ22.txt":                    {
        "fileid": 229, "author": "Augustine", "title": "De Civitate Dei Liber XXII"
    }, "augustine/civ3.txt":                     {
        "fileid": 230, "author": "Augustine", "title": "De Civitate Dei Liber III"
    }, "augustine/civ4.txt":                     {
        "fileid": 231, "author": "Augustine", "title": "De Civitate Dei Liber IV"
    }, "augustine/civ5.txt":                     {
        "fileid": 232, "author": "Augustine", "title": "De Civitate Dei Liber V"
    }, "augustine/civ6.txt":                     {
        "fileid": 233, "author": "Augustine", "title": "De Civitate Dei Liber VI"
    }, "augustine/civ7.txt":                     {
        "fileid": 234, "author": "Augustine", "title": "De Civitate Dei Liber VII"
    }, "augustine/civ8.txt":                     {
        "fileid": 235, "author": "Augustine", "title": "De Civitate Dei Liber VIII"
    }, "augustine/civ9.txt":                     {
        "fileid": 236, "author": "Augustine", "title": "De Civitate Dei Liber IX"
    }, "augustine/conf1.txt":                    {"fileid": 237, "author": "Augustine", "title": "Confessions I"},
    "augustine/conf10.txt":                      {"fileid": 238, "author": "Augustine", "title": "Confessions X"},
    "augustine/conf11.txt":                      {"fileid": 239, "author": "Augustine", "title": "Confessions XI"},
    "augustine/conf12.txt":                      {"fileid": 240, "author": "Augustine", "title": "Confessions XII"},
    "augustine/conf13.txt":                      {"fileid": 241, "author": "Augustine", "title": "Confessions XIII"},
    "augustine/conf2.txt":                       {"fileid": 242, "author": "Augustine", "title": "Confessions II"},
    "augustine/conf3.txt":                       {"fileid": 243, "author": "Augustine", "title": "Confessions III"},
    "augustine/conf4.txt":                       {"fileid": 244, "author": "Augustine", "title": "Confessions IV"},
    "augustine/conf5.txt":                       {"fileid": 245, "author": "Augustine", "title": "Confessions V"},
    "augustine/conf6.txt":                       {"fileid": 246, "author": "Augustine", "title": "Confessions VI"},
    "augustine/conf7.txt":                       {"fileid": 247, "author": "Augustine", "title": "Confessions VII"},
    "augustine/conf8.txt":                       {"fileid": 248, "author": "Augustine", "title": "Confessions VIII"},
    "augustine/conf9.txt":                       {"fileid": 249, "author": "Augustine", "title": "Confessions IX"},
    "augustine/dia.txt":                         {"fileid": 250, "author": "Augustine", "title": "de Dialectica"},
    "augustine/epistula.txt":                    {"fileid": 251, "author": None, "title": "Augustine"},
    "augustine/fide.txt":                        {"fileid": 252, "author": "Augustine", "title": "de Fide et Symbolo"},
    "augustine/iulianus1.txt":                   {"fileid": 253, "author": None, "title": "St. Augustine"},
    "augustine/iulianus2.txt":                   {"fileid": 254, "author": None, "title": "St. Augustine"},
    "augustine/reg.txt":                         {"fileid": 255, "author": None, "title": "Rule of St. Augustine"},
    "augustine/serm1.txt":                       {"fileid": 256, "author": "Augustine", "title": "Sermon 1"},
    "augustine/serm10.txt":                      {"fileid": 257, "author": "Augustine", "title": "Sermon 10"},
    "augustine/serm11.txt":                      {"fileid": 258, "author": "Augustine", "title": "Sermon 11"},
    "augustine/serm12.txt":                      {"fileid": 259, "author": "Augustine", "title": "Sermon 12"},
    "augustine/serm13.txt":                      {"fileid": 260, "author": "Augustine", "title": "Sermon 13"},
    "augustine/serm14.txt":                      {"fileid": 261, "author": "Augustine", "title": "Sermon 14"},
    "augustine/serm15.txt":                      {"fileid": 262, "author": "Augustine", "title": "Sermon 15"},
    "augustine/serm16.txt":                      {"fileid": 263, "author": "Augustine", "title": "Sermon 16"},
    "augustine/serm17.txt":                      {"fileid": 264, "author": "Augustine", "title": "Sermon 17"},
    "augustine/serm18.txt":                      {"fileid": 265, "author": "Augustine", "title": "Sermon 18"},
    "augustine/serm19.txt":                      {"fileid": 266, "author": "Augustine", "title": "Sermon 19"},
    "augustine/serm2.txt":                       {"fileid": 267, "author": "Augustine", "title": "Sermon 2"},
    "augustine/serm20.txt":                      {"fileid": 268, "author": "Augustine", "title": "Sermon 20"},
    "augustine/serm4.txt":                       {"fileid": 269, "author": "Augustine", "title": "Sermon 4"},
    "augustine/serm5.txt":                       {"fileid": 270, "author": "Augustine", "title": "Sermon 5"},
    "augustine/serm6.txt":                       {"fileid": 271, "author": "Augustine", "title": "Sermon 6"},
    "augustine/serm7.txt":                       {"fileid": 272, "author": "Augustine", "title": "Sermon 7"},
    "augustine/serm71.txt":                      {"fileid": 273, "author": "Augustine", "title": "Sermon 71"},
    "augustine/serm72.txt":                      {"fileid": 274, "author": "Augustine", "title": "Sermon 72"},
    "augustine/serm73.txt":                      {"fileid": 275, "author": "Augustine", "title": "Sermon 73"},
    "augustine/serm74.txt":                      {"fileid": 276, "author": "Augustine", "title": "Sermon 74"},
    "augustine/serm75.txt":                      {"fileid": 277, "author": "Augustine", "title": "Sermon 75"},
    "augustine/serm76.txt":                      {"fileid": 278, "author": "Augustine", "title": "Sermon 76"},
    "augustine/serm77.txt":                      {"fileid": 279, "author": "Augustine", "title": "Sermon 77"},
    "augustine/serm78.txt":                      {"fileid": 280, "author": "Augustine", "title": "Sermon 78"},
    "augustine/serm79.txt":                      {"fileid": 281, "author": "Augustine", "title": "Sermon 79"},
    "augustine/serm8.txt":                       {"fileid": 282, "author": "Augustine", "title": "Sermon 8"},
    "augustine/serm80.txt":                      {"fileid": 283, "author": "Augustine", "title": "Sermon 80"},
    "augustine/serm81.txt":                      {"fileid": 284, "author": "Augustine", "title": "Sermon 81"},
    "augustine/serm82.txt":                      {"fileid": 285, "author": "Augustine", "title": "Sermon 82"},
    "augustine/serm83.txt":                      {"fileid": 286, "author": "Augustine", "title": "Sermon 83"},
    "augustine/serm87.txt":                      {"fileid": 287, "author": "Augustine", "title": "Sermon 87"},
    "augustine/serm88.txt":                      {"fileid": 288, "author": "Augustine", "title": "Sermon 88"},
    "augustine/serm9.txt":                       {"fileid": 289, "author": "Augustine", "title": "Sermon 9"},
    "augustine/serm90.txt":                      {"fileid": 290, "author": "Augustine", "title": "Sermon 90"},
    "augustine/serm92.txt":                      {"fileid": 291, "author": "Augustine", "title": "Sermon 92"},
    "augustine/serm95.txt":                      {"fileid": 292, "author": "Augustine", "title": "Sermon 95"},
    "augustine/serm99.txt":                      {"fileid": 293, "author": "Augustine", "title": "Sermon 99"},
    "augustine/trin1.txt":                       {
        "fileid": 294, "author": "Augustinus", "title": "de Trinitate Liber I"
    }, "augustine/trin10.txt":                   {
        "fileid": 295, "author": "Augustinus", "title": "de Trinitate Liber X"
    }, "augustine/trin11.txt":                   {
        "fileid": 296, "author": "Augustinus", "title": "de Trinitate Liber XI"
    }, "augustine/trin12.txt":                   {
        "fileid": 297, "author": "Augustinus", "title": "de Trinitate Liber XII"
    }, "augustine/trin13.txt":                   {
        "fileid": 298, "author": "Augustinus", "title": "de Trinitate Liber XIII"
    }, "augustine/trin14.txt":                   {
        "fileid": 299, "author": "Augustinus", "title": "de Trinitate Liber XIV"
    }, "augustine/trin15.txt":                   {
        "fileid": 300, "author": "Augustinus", "title": "de Trinitate Liber XV"
    }, "augustine/trin2.txt":                    {
        "fileid": 301, "author": "Augustinus", "title": "de Trinitate Liber II"
    }, "augustine/trin3.txt":                    {
        "fileid": 302, "author": "Augustinus", "title": "de Trinitate Liber III"
    }, "augustine/trin4.txt":                    {
        "fileid": 303, "author": "Augustinus", "title": "de Trinitate Liber IV"
    }, "augustine/trin5.txt":                    {
        "fileid": 304, "author": "Augustinus", "title": "de Trinitate Liber V"
    }, "augustine/trin6.txt":                    {
        "fileid": 305, "author": "Augustinus", "title": "de Trinitate Liber VI"
    }, "augustine/trin7.txt":                    {
        "fileid": 306, "author": "Augustinus", "title": "de Trinitate Liber VII"
    }, "augustine/trin8.txt":                    {
        "fileid": 307, "author": "Augustinus", "title": "de Trinitate Liber VIII"
    }, "augustine/trin9.txt":                    {
        "fileid": 308, "author": "Augustinus", "title": "de Trinitate Liber IX"
    }, "aus.mos.txt":                            {"fileid": 309, "author": "Ausonius", "title": "Mosella"},
    "aus.sept.sent.txt":                         {
        "fileid": 310, "author": "Ausonius", "title": "Septem Sapientum Sententiae"
    }, "ave.phoen.txt":                          {"fileid": 311, "author": None, "title": "Phoenix"},
    "avianus.txt":                               {"fileid": 312, "author": "Avianus", "title": "Fabulae"},
    "avienus.ora.txt":                           {"fileid": 313, "author": "Avienus", "title": "Ora Maritima"},
    "avienus.periegesis.txt":                    {"fileid": 314, "author": "Avienus", "title": "Periegesis"},
    "axio.txt":                                  {"fileid": 315, "author": None, "title": "Pseudo-Plato "},
    "bacon/bacon.distributio.txt":               {"fileid": 316, "author": "Bacon", "title": "Distributio"},
    "bacon/bacon.epistola.txt":                  {"fileid": 317, "author": "Bacon", "title": "Epistola"},
    "bacon/bacon.hist1.txt":                     {
        "fileid": 318, "author": "Bacon", "title": "History of the Reign of Henry VII"
    }, "bacon/bacon.hist10.txt":                 {
        "fileid": 319, "author": "Bacon", "title": "History of the Reign of Henry VII"
    }, "bacon/bacon.hist11.txt":                 {
        "fileid": 320, "author": "Bacon", "title": "History of the Reign of Henry VII"
    }, "bacon/bacon.hist2.txt":                  {
        "fileid": 321, "author": "Bacon", "title": "History of the Reign of Henry VII"
    }, "bacon/bacon.hist3.txt":                  {
        "fileid": 322, "author": "Bacon", "title": "History of the Reign of Henry VII"
    }, "bacon/bacon.hist4.txt":                  {
        "fileid": 323, "author": "Bacon", "title": "History of the Reign of Henry VII"
    }, "bacon/bacon.hist5.txt":                  {
        "fileid": 324, "author": "Bacon", "title": "History of the Reign of Henry VII"
    }, "bacon/bacon.hist6.txt":                  {
        "fileid": 325, "author": "Bacon", "title": "History of the Reign of Henry VII"
    }, "bacon/bacon.hist7.txt":                  {
        "fileid": 326, "author": "Bacon", "title": "History of the Reign of Henry VII"
    }, "bacon/bacon.hist8.txt":                  {
        "fileid": 327, "author": "Bacon", "title": "History of the Reign of Henry VII"
    }, "bacon/bacon.hist9.txt":                  {
        "fileid": 328, "author": "Bacon", "title": "History of the Reign of Henry VII"
    }, "bacon/bacon.intro.txt":                  {"fileid": 329, "author": "Bacon", "title": "Introduction"},
    "bacon/bacon.liber1.txt":                    {"fileid": 330, "author": "Bacon", "title": "Liber Primus"},
    "bacon/bacon.liber2.txt":                    {"fileid": 331, "author": "Bacon", "title": "Liber Secundus"},
    "bacon/bacon.praefatio.txt":                 {"fileid": 332, "author": "Bacon", "title": "Praefatio"},
    "bacon/bacon.praefatio2.txt":                {"fileid": 333, "author": "Bacon", "title": "Praefatio "},
    "bacon/bacon.sermones.txt":                  {
        "fileid": 334, "author": "Francis Bacon", "title": "Sermones Fideles sive Interiora Rerum"
    }, "bacon/bacon.titlepage.txt":              {"fileid": 335, "author": "Bacon", "title": "Title Page"},
    "balbus.txt":                                {"fileid": 336, "author": None, "title": "Balbus"},
    "balde1.txt":                                {"fileid": 337, "author": "Balde", "title": "Melancholia"},
    "balde2.txt":                                {
        "fileid": 338, "author": "Balde", "title": "Ad Iulium Orstenam de more unguendorum cadaverum"
    }, "baldo.txt":                              {"fileid": 339, "author": "Baldo", "title": "Novus Aesopus"},
    "bebel.txt":                                 {"fileid": 340, "author": "Bebel", "title": "Liber Facetiarum"},
    "bede/bede1.txt":                            {"fileid": 341, "author": "Bede", "title": "Book I"},
    "bede/bede2.txt":                            {"fileid": 342, "author": "Bede", "title": "Book II"},
    "bede/bede3.txt":                            {"fileid": 343, "author": "Bede", "title": "Book III"},
    "bede/bede4.txt":                            {"fileid": 344, "author": "Bede", "title": "Book IV"},
    "bede/bede5.txt":                            {"fileid": 345, "author": "Bede", "title": "Book V"},
    "bede/bedecontinuatio.txt":                  {"fileid": 346, "author": "[Bede", "title": "Continuatio]"},
    "bede/bedepraef.txt":                        {"fileid": 347, "author": "Bede", "title": "Praefatio"},
    "bede/bedeproverbs.txt":                     {"fileid": 348, "author": "Psuedo-Bede", "title": "Proverbs"},
    "benedict.txt":                              {"fileid": 349, "author": None, "title": "Rule of St. Benedict"},
    "berengar.txt":                              {"fileid": 350, "author": "Berengar", "title": "Apologeticus"},
    "bernardcluny1.txt":                         {
        "fileid": 351, "author": "Bernard of Cluny", "title": "De contemptu mundi I"
    }, "bernardcluny2.txt":                      {
        "fileid": 352, "author": "Bernard of Cluny", "title": "De contemptu mundi II"
    }, "bible/acts.txt":                         {"fileid": 353, "author": "Vulgate", "title": "Acts"},
    "bible/amos.txt":                            {"fileid": 354, "author": "Vulgate", "title": "Amos "},
    "bible/baruch.txt":                          {"fileid": 355, "author": "Vulgate", "title": "Baruch "},
    "bible/chronicles1.txt":                     {"fileid": 356, "author": "Vulgate", "title": "First Chronicles "},
    "bible/chronicles2.txt":                     {"fileid": 357, "author": "Vulgate", "title": "Second Chronicles "},
    "bible/colossians.txt":                      {
        "fileid": 358, "author": "Vulgate", "title": "Paul to the Colossians "
    }, "bible/corinthians1.txt":                 {
        "fileid": 359, "author": "Vulgate", "title": "Paul to the Corinthians I "
    }, "bible/corinthians2.txt":                 {
        "fileid": 360, "author": "Vulgate", "title": "Paul to the Corinthians II "
    }, "bible/daniel.txt":                       {"fileid": 361, "author": "Vulgate", "title": "Daniel "},
    "bible/deuteronomy.txt":                     {"fileid": 362, "author": "Vulgate", "title": "Deuteronomy "},
    "bible/ecclesiastes.txt":                    {"fileid": 363, "author": "Vulgate", "title": "Ecclesiastes "},
    "bible/ephesians.txt":                       {
        "fileid": 364, "author": "Vulgate", "title": "Paul to the Ephesians "
    }, "bible/esdras1.txt":                      {"fileid": 365, "author": "Vulgate", "title": "First Book of Esdras "},
    "bible/esdras2.txt":                         {
        "fileid": 366, "author": "Vulgate", "title": "Second Book of Esdras "
    }, "bible/esther.txt":                       {"fileid": 367, "author": "Vulgate", "title": "Esther "},
    "bible/exodus.txt":                          {"fileid": 368, "author": "Vulgate", "title": "Exodus"},
    "bible/ezekiel.txt":                         {"fileid": 369, "author": "Vulgate", "title": "Ezekiel "},
    "bible/ezra.txt":                            {"fileid": 370, "author": "Vulgate", "title": "Ezra "},
    "bible/galatians.txt":                       {
        "fileid": 371, "author": "Vulgate", "title": "Paul to the Galatians "
    }, "bible/genesis.txt":                      {"fileid": 372, "author": "Vulgate", "title": "Genesis"},
    "bible/habakkuk.txt":                        {"fileid": 373, "author": "Vulgate", "title": "Habakkuk "},
    "bible/haggai.txt":                          {"fileid": 374, "author": "Vulgate", "title": "Haggai "},
    "bible/hebrews.txt":                         {"fileid": 375, "author": "Vulgate", "title": "Letter to Hebrews "},
    "bible/hosea.txt":                           {"fileid": 376, "author": "Vulgate", "title": "Hosea "},
    "bible/isaiah.txt":                          {"fileid": 377, "author": "Vulgate", "title": "Isaiah "},
    "bible/james.txt":                           {"fileid": 378, "author": "Vulgate", "title": "A Letter to James "},
    "bible/jeremiah.txt":                        {"fileid": 379, "author": "Vulgate", "title": "Jeremiah "},
    "bible/job.txt":                             {"fileid": 380, "author": "Vulgate", "title": "Job "},
    "bible/joel.txt":                            {"fileid": 381, "author": "Vulgate", "title": "Joel "},
    "bible/john.txt":                            {"fileid": 382, "author": "Vulgate", "title": "John "},
    "bible/john1.txt":                           {"fileid": 383, "author": None, "title": "John 1 "},
    "bible/john2.txt":                           {"fileid": 384, "author": None, "title": "John 2 "},
    "bible/john3.txt":                           {"fileid": 385, "author": None, "title": "John 3 "},
    "bible/jonah.txt":                           {"fileid": 386, "author": "Vulgate", "title": "Jonah "},
    "bible/joshua.txt":                          {"fileid": 387, "author": "Vulgate", "title": "Joshua "},
    "bible/jude.txt":                            {"fileid": 388, "author": "Vulgate", "title": "Letter of Jude "},
    "bible/judges.txt":                          {"fileid": 389, "author": "Vulgate", "title": "Judges "},
    "bible/judith.txt":                          {"fileid": 390, "author": "Vulgate", "title": "Judith "},
    "bible/kings1.txt":                          {"fileid": 391, "author": "Vulgate", "title": "Kings I "},
    "bible/kings2.txt":                          {"fileid": 392, "author": "Vulgate", "title": "Kings II "},
    "bible/lamentations.txt":                    {"fileid": 393, "author": "Vulgate", "title": "Lamentations "},
    "bible/leviticus.txt":                       {"fileid": 394, "author": "Vulgate", "title": "Leviticus "},
    "bible/luke.txt":                            {"fileid": 395, "author": "Vulgate", "title": "Luke "},
    "bible/macabees1.txt":                       {
        "fileid": 396, "author": "Vulgate", "title": "First Book of Macabees "
    }, "bible/macabees2.txt":                    {
        "fileid": 397, "author": "Vulgate", "title": "Second Book of Macabees "
    }, "bible/malachias.txt":                    {"fileid": 398, "author": "Vulgate", "title": "Malachias "},
    "bible/manasses.txt":                        {"fileid": 399, "author": "Vulgate", "title": "Prayer of Manasses "},
    "bible/mark.txt":                            {"fileid": 400, "author": None, "title": "Gospel of Mark "},
    "bible/matthew.txt":                         {"fileid": 401, "author": ">Vulgate", "title": "Matthew"},
    "bible/micah.txt":                           {"fileid": 402, "author": "Vulgate", "title": "Micah "},
    "bible/nahum.txt":                           {"fileid": 403, "author": "Vulgate", "title": "Nahum "},
    "bible/nehemiah.txt":                        {"fileid": 404, "author": "Vulgate", "title": "Nehemiah "},
    "bible/numbers.txt":                         {"fileid": 405, "author": "Vulgate", "title": "Numbers "},
    "bible/obadiah.txt":                         {"fileid": 406, "author": "Vulgate", "title": "Obadiah "},
    "bible/peter1.txt":                          {
        "fileid": 407, "author": "Vulgate", "title": "First Letter of Peter "
    }, "bible/peter2.txt":                       {
        "fileid": 408, "author": "Vulgate", "title": "Second Letter of Peter "
    }, "bible/philemon.txt":                     {"fileid": 409, "author": "Vulgate", "title": "Paul to Philemon "},
    "bible/philip.txt":                          {"fileid": 410, "author": None, "title": "Epistula ad Philippenses "},
    "bible/prologi.txt":                         {"fileid": 411, "author": None, "title": "The Bible"},
    "bible/proverbs.txt":                        {"fileid": 412, "author": "Vulgate", "title": "Proverbs "},
    "bible/psalms.txt":                          {"fileid": 413, "author": "Vulgate", "title": "Psalms"},
    "bible/revelation.txt":                      {"fileid": 414, "author": "Vulgate", "title": "Revelation of John "},
    "bible/romans.txt":                          {"fileid": 415, "author": "Vulgate", "title": "Paul to the Romans "},
    "bible/ruth.txt":                            {"fileid": 416, "author": "Vulgate", "title": "Ruth "},
    "bible/samuel1.txt":                         {"fileid": 417, "author": "Vulgate", "title": "Samuel "},
    "bible/samuel2.txt":                         {"fileid": 418, "author": "Vulgate", "title": "Second Samuel "},
    "bible/sirach.txt":                          {"fileid": 419, "author": "Vulgate", "title": "Sirach "},
    "bible/songofsongs.txt":                     {"fileid": 420, "author": "Vulgate", "title": "Song of Songs "},
    "bible/thessalonians1.txt":                  {
        "fileid": 421, "author": "Vulgate", "title": "Paul to the Thessalonians I "
    }, "bible/thessalonians2.txt":               {
        "fileid": 422, "author": "Vulgate", "title": "Paul to the Thessalonians II "
    }, "bible/timothy1.txt":                     {"fileid": 423, "author": "Vulgate", "title": "Paul to Timothy I "},
    "bible/timothy2.txt":                        {"fileid": 424, "author": "Vulgate", "title": "Paul to Timothy II "},
    "bible/titum.txt":                           {"fileid": 425, "author": None, "title": "Epistula ad Titum "},
    "bible/tobia.txt":                           {"fileid": 426, "author": "Vulgate", "title": "Tobias "},
    "bible/wisdom.txt":                          {"fileid": 427, "author": "Vulgate", "title": "Wisdom "},
    "bible/zacharias.txt":                       {"fileid": 428, "author": "Vulgate", "title": "Zacharias "},
    "bible/zephaniah.txt":                       {"fileid": 429, "author": "Vulgate", "title": "Zephaniah "},
    "biggs.txt":                                 {
        "fileid": 430, "author": "Bigges", "title": "Expeditio Francisci Draki Equitis Angli"
    }, "bill.rights.txt":                        {"fileid": 431, "author": None, "title": "Bill of Rights"},
    "blesensis.txt":                             {"fileid": 432, "author": None, "title": "Petrus Blesensis"},
    "boethiusdacia/deaeternitate.txt":           {"fileid": 433, "author": None, "title": "Boethius de Dacia"},
    "boethiusdacia/desummobono.txt":             {"fileid": 434, "author": None, "title": "Boethius de Dacia"},
    "bonaventura.itinerarium.txt":               {"fileid": 435, "author": None, "title": "St. Bonaventure"},
    "boskovic.txt":                              {"fileid": 436, "author": None, "title": "Bartolomej Boskovic"},
    "brevechronicon.txt":                        {
        "fileid": 437, "author": None, "title": "Breve Chronicon Northmannicum"
    }, "buchanan.txt":                           {
        "fileid": 438, "author": "Buchanan", "title": "de Maria Scotorum Regina"
    }, "bultelius/bultelius1.txt":               {"fileid": 439, "author": "Bultelius", "title": "Ad Noctem"},
    "bultelius/bultelius2.txt":                  {"fileid": 440, "author": "Bultelius", "title": "Somnium"},
    "caeciliusbalbus.txt":                       {"fileid": 441, "author": None, "title": "Pseudo-Caecilius Balbus"},
    "caesar/alex.txt":                           {
        "fileid": 442, "author": None, "title": "INCERTI AVCTORIS DE BELLO ALEXANDRINO LIBER"
    }, "caesar/bc1.txt":                         {
        "fileid": 443, "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO CIVILI LIBER PRIMVS"
    }, "caesar/bc2.txt":                         {
        "fileid": 444, "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO CIVILI LIBER SECVNDVS"
    }, "caesar/bc3.txt":                         {"fileid": 445, "author": None, "title": ""}, "caesar/bellafr.txt": {
        "fileid": 446, "author": None, "title": "INCERTI AVCTORIS DE BELLO AFRICO LIBER"
    }, "caesar/gall1.txt":                       {
        "fileid": 447, "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER PRIMUS"
    }, "caesar/gall2.txt":                       {
        "fileid": 448, "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER SECVNDVS"
    }, "caesar/gall3.txt":                       {
        "fileid": 449, "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER TERTIVS"
    }, "caesar/gall4.txt":                       {
        "fileid": 450, "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER QVARTVS"
    }, "caesar/gall5.txt":                       {
        "fileid": 451, "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER QVINTVS"
    }, "caesar/gall6.txt":                       {
        "fileid": 452, "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER SEXTVS"
    }, "caesar/gall7.txt":                       {
        "fileid": 453, "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER SEPTIMVS"
    }, "caesar/gall8.txt":                       {
        "fileid": 454, "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER OCTAVVS"
    }, "caesar/hisp.txt":                        {
        "fileid": 455, "author": None, "title": "INCERTI AVCTORIS DE BELLO HISPANIENSI LIBER"
    }, "calpurniusflaccus.txt":                  {
        "fileid": 456, "author": "Calpurnius Flaccus", "title": "Declamationes"
    }, "calpurniussiculus.txt":                  {"fileid": 457, "author": None, "title": "T. Calpunius Siculus"},
    "campion/campion.elegies.txt":               {"fileid": 458, "author": "Campion", "title": "Elegies"},
    "campion/campion.epigr1.txt":                {"fileid": 459, "author": "Campion", "title": "Epigrams I"},
    "campion/campion.epigr2.txt":                {"fileid": 460, "author": "Campion", "title": "Epigrams II"},
    "campion/campion.misc.txt":                  {"fileid": 461, "author": "Campion", "title": "Miscellaneous Poetry"},
    "campion/campion.plot1.txt":                 {
        "fileid": 462, "author": "Campion", "title": "De Pulverea Coniuratione I"
    }, "campion/campion.plot2.txt":              {
        "fileid": 463, "author": "Campion", "title": "De Pulverea Coniuratione II"
    }, "campion/campion.thamesin.txt":           {"fileid": 464, "author": "Campion", "title": "Ad Thamesin"},
    "campion/campion.umbra.txt":                 {"fileid": 465, "author": "Campion", "title": "Umbra"},
    "capellanus/capellanus1.txt":                {"fileid": 466, "author": "Andreas Capellanus", "title": "de Amore I"},
    "capellanus/capellanus2.txt":                {
        "fileid": 467, "author": "Andreas Capellanus", "title": "de Amore II"
    }, "capellanus/capellanus3.txt":             {
        "fileid": 468, "author": "Andreas Capellanus", "title": "de Amore III"
    }, "carm.bur.txt":                           {"fileid": 469, "author": None, "title": "Carmina Burana "},
    "carmenarvale.txt":                          {"fileid": 470, "author": None, "title": "Carmen Arvale"},
    "carmeninvictoriam.txt":                     {
        "fileid": 471, "author": None, "title": "CARMEN IN VICTORIAM PISANORUM"
    }, "carmensaliare.txt":                      {"fileid": 472, "author": None, "title": "Carmen Saliare"},
    "cassiodorus/anima.txt":                     {"fileid": 473, "author": "Cassiodorus", "title": "de Anima"},
    "cassiodorus/epist.txt":                     {"fileid": 474, "author": "Cassiodorus", "title": "Variae"},
    "cassiodorus/musica.txt":                    {"fileid": 475, "author": "Cassiodorus", "title": "de Musica"},
    "cassiodorus/orationes.txt":                 {"fileid": 476, "author": "Cassiodorus", "title": "Orationes"},
    "cassiodorus/varia.praef.txt":               {"fileid": 477, "author": "Cassiodorus", "title": "Variae, Praefatio"},
    "cassiodorus/varia1.txt":                    {"fileid": 478, "author": "Cassiodorus", "title": "Variae I"},
    "cassiodorus/varia10.txt":                   {"fileid": 479, "author": "Cassiodorus", "title": "Variae X"},
    "cassiodorus/varia11.txt":                   {"fileid": 480, "author": "Cassiodorus", "title": "Variae XI"},
    "cassiodorus/varia12.txt":                   {"fileid": 481, "author": "Cassiodorus", "title": "Variae XII"},
    "cassiodorus/varia2.txt":                    {"fileid": 482, "author": "Cassiodorus", "title": "Variae II"},
    "cassiodorus/varia3.txt":                    {"fileid": 483, "author": "Cassiodorus", "title": "Variae III"},
    "cassiodorus/varia4.txt":                    {"fileid": 484, "author": "Cassiodorus", "title": "Variae IV"},
    "cassiodorus/varia5.txt":                    {"fileid": 485, "author": "Cassiodorus", "title": "Variae V"},
    "cassiodorus/varia6.txt":                    {"fileid": 486, "author": "Cassiodorus", "title": "Variae VI"},
    "cassiodorus/varia7.txt":                    {"fileid": 487, "author": "Cassiodorus", "title": "Variae VII"},
    "cassiodorus/varia8.txt":                    {"fileid": 488, "author": "Cassiodorus", "title": "Variae VIII"},
    "cassiodorus/varia9.txt":                    {"fileid": 489, "author": "Cassiodorus", "title": "Variae IX"},
    "catalogueliberien.txt":                     {"fileid": 490, "author": None, "title": "Catalogue Lib\u00e9rien"},
    "cato.dis.txt":                              {"fileid": 491, "author": "[Cato]", "title": "Disticha Catonis"},
    "cato/cato.agri.txt":                        {"fileid": 492, "author": "Cato", "title": "DE AGRI CVLTVRA"},
    "cato/cato.frag.txt":                        {
        "fileid": 493, "author": "Cato", "title": "ORATIONVM M. PORCI CATONIS FRAGMENTA"
    }, "catullus.txt":                           {"fileid": 494, "author": "Catullus", "title": "Carmina"},
    "celtis.odes.txt":                           {
        "fileid": 495, "author": "Conrad Celtis", "title": "Odes   CONRADUS CELTIS: ODES    "
    }, "celtis.oratio.txt":                      {"fileid": 496, "author": None, "title": ""}, "censorinus.txt": {
        "fileid": 497, "author": "Censorinus", "title": "de Die Natali Liber"
    }, "cicero/acad.txt":                        {"fileid": 498, "author": "Cicero", "title": "Academica"},
    "cicero/adbrutum1.txt":                      {"fileid": 499, "author": "Cicero", "title": "ad Brutum I"},
    "cicero/adbrutum2.txt":                      {"fileid": 500, "author": "Cicero", "title": "ad Brutum II"},
    "cicero/amic.txt":                           {"fileid": 501, "author": "Cicero", "title": "de Amicitia"},
    "cicero/arch.txt":                           {"fileid": 502, "author": "Cicero", "title": "Pro Archia"},
    "cicero/att1.txt":                           {"fileid": 503, "author": "Cicero", "title": "ad Atticum I"},
    "cicero/att10.txt":                          {"fileid": 504, "author": "Cicero", "title": "ad Atticum X"},
    "cicero/att11.txt":                          {"fileid": 505, "author": "Cicero", "title": "ad Atticum XI"},
    "cicero/att12.txt":                          {"fileid": 506, "author": "Cicero", "title": "ad Atticum XII"},
    "cicero/att13.txt":                          {"fileid": 507, "author": "Cicero", "title": "ad Atticum XIII"},
    "cicero/att14.txt":                          {"fileid": 508, "author": "Cicero", "title": "ad Atticum XIV"},
    "cicero/att15.txt":                          {"fileid": 509, "author": "Cicero", "title": "ad Atticum XV"},
    "cicero/att16.txt":                          {"fileid": 510, "author": "Cicero", "title": "ad Atticum XVI"},
    "cicero/att2.txt":                           {"fileid": 511, "author": "Cicero", "title": "ad Atticum II"},
    "cicero/att3.txt":                           {"fileid": 512, "author": "Cicero", "title": "ad Atticum III"},
    "cicero/att4.txt":                           {"fileid": 513, "author": "Cicero", "title": "ad Atticum IV"},
    "cicero/att5.txt":                           {"fileid": 514, "author": "Cicero", "title": "ad Atticum V"},
    "cicero/att6.txt":                           {"fileid": 515, "author": "Cicero", "title": "ad Atticum VI"},
    "cicero/att7.txt":                           {"fileid": 516, "author": "Cicero", "title": "ad Atticum VII"},
    "cicero/att8.txt":                           {"fileid": 517, "author": "Cicero", "title": "ad Atticum VIII"},
    "cicero/att9.txt":                           {"fileid": 518, "author": "Cicero", "title": "ad Atticum IX"},
    "cicero/balbo.txt":                          {
        "fileid": 519, "author": "Cicero", "title": "PRO L. CORNELIO BALBO ORATIO"
    }, "cicero/brut.txt":                        {"fileid": 520, "author": "Cicero", "title": "BRUTUS"},
    "cicero/caecilium.txt":                      {"fileid": 521, "author": "Cicero", "title": "IN CAECILIUM ORATIO"},
    "cicero/caecina.txt":                        {"fileid": 522, "author": "Cicero", "title": "PRO A. CAECINA ORATIO"},
    "cicero/cael.txt":                           {"fileid": 523, "author": "Cicero", "title": "PRO M. CAELIO ORATIO"},
    "cicero/cat1.txt":                           {"fileid": 524, "author": "Cicero", "title": "In Catilinam I"},
    "cicero/cat2.txt":                           {"fileid": 525, "author": "Cicero", "title": "In Catilinam II"},
    "cicero/cat3.txt":                           {"fileid": 526, "author": "Cicero", "title": "In Catilinam III"},
    "cicero/cat4.txt":                           {"fileid": 527, "author": "Cicero", "title": "In Catilinam IV"},
    "cicero/cluentio.txt":                       {"fileid": 528, "author": "Cicero", "title": "PRO A. CLVENTIO ORATIO"},
    "cicero/compet.txt":                         {
        "fileid": 529, "author": "Cicero", "title": "COMMENTARIOLVM PETITIONIS"
    }, "cicero/consulatu.txt":                   {
        "fileid": 530, "author": "Cicero", "title": "DE CONSVLATV SVO FRAGMENTA"
    }, "cicero/deio.txt":                        {"fileid": 531, "author": "Cicero", "title": "PRO REGE DEIOTARO"},
    "cicero/divinatione1.txt":                   {
        "fileid": 532, "author": "Cicero", "title": "DE DIVINATIONE LIBER PRIOR"
    }, "cicero/divinatione2.txt":                {
        "fileid": 533, "author": "Cicero", "title": "DE DIVINATIONE LIBER ALTER"
    }, "cicero/domo.txt":                        {"fileid": 534, "author": "Cicero", "title": "DE DOMO SVA"},
    "cicero/fam1.txt":                           {"fileid": 535, "author": "Cicero", "title": "ad Familiares I"},
    "cicero/fam10.txt":                          {"fileid": 536, "author": "Cicero", "title": "ad Familiares X"},
    "cicero/fam11.txt":                          {"fileid": 537, "author": "Cicero", "title": "ad Familiares XI"},
    "cicero/fam12.txt":                          {"fileid": 538, "author": "Cicero", "title": "ad Familiares XII"},
    "cicero/fam13.txt":                          {"fileid": 539, "author": "Cicero", "title": "ad Familiares XIII"},
    "cicero/fam14.txt":                          {"fileid": 540, "author": "Cicero", "title": "ad Familiares XIV"},
    "cicero/fam15.txt":                          {"fileid": 541, "author": "Cicero", "title": "ad Familiares XV"},
    "cicero/fam16.txt":                          {"fileid": 542, "author": "Cicero", "title": "ad Familiares XVI"},
    "cicero/fam2.txt":                           {"fileid": 543, "author": "Cicero", "title": "ad Familiares II"},
    "cicero/fam3.txt":                           {"fileid": 544, "author": "Cicero", "title": "ad Familiares III"},
    "cicero/fam4.txt":                           {"fileid": 545, "author": "Cicero", "title": "ad Familiares IV"},
    "cicero/fam5.txt":                           {"fileid": 546, "author": "Cicero", "title": "ad Familiares V"},
    "cicero/fam6.txt":                           {"fileid": 547, "author": "Cicero", "title": "ad Familiares VI"},
    "cicero/fam7.txt":                           {"fileid": 548, "author": "Cicero", "title": "ad Familiares VII"},
    "cicero/fam8.txt":                           {"fileid": 549, "author": "Cicero", "title": "ad Familiares VIII"},
    "cicero/fam9.txt":                           {"fileid": 550, "author": "Cicero", "title": "ad Familiares IX"},
    "cicero/fato.txt":                           {"fileid": 551, "author": "Cicero", "title": "de Fato"},
    "cicero/fin1.txt":                           {"fileid": 552, "author": "Cicero", "title": "de Finibus I"},
    "cicero/fin2.txt":                           {"fileid": 553, "author": "Cicero", "title": "de Finibus II"},
    "cicero/fin3.txt":                           {"fileid": 554, "author": "Cicero", "title": "de Finibus III"},
    "cicero/fin4.txt":                           {"fileid": 555, "author": "Cicero", "title": "de Finibus IV"},
    "cicero/fin5.txt":                           {"fileid": 556, "author": "Cicero", "title": "de Finibus V"},
    "cicero/flacco.txt":                         {"fileid": 557, "author": "Cicero", "title": "PRO L. FLACCO"},
    "cicero/fonteio.txt":                        {"fileid": 558, "author": "Cicero", "title": "PRO PRO M. FONTEIO"},
    "cicero/fratrem1.txt":                       {"fileid": 559, "author": "Cicero", "title": "ad Quintum Fratrem I"},
    "cicero/fratrem2.txt":                       {"fileid": 560, "author": "Cicero", "title": "ad Quintum Fratrem II"},
    "cicero/fratrem3.txt":                       {"fileid": 561, "author": "Cicero", "title": "ad Quintum Fratrem III"},
    "cicero/haruspicum.txt":                     {
        "fileid": 562, "author": "Cicero", "title": "ORATIO DE HARVSPICVM RESPONSO"
    }, "cicero/imp.txt":                         {"fileid": 563, "author": "Cicero", "title": "DE IMPERIO CN. POMPEI"},
    "cicero/inventione1.txt":                    {"fileid": 564, "author": "Cicero", "title": "de Inventione I"},
    "cicero/inventione2.txt":                    {"fileid": 565, "author": "Cicero", "title": "de Inventione II"},
    "cicero/leg1.txt":                           {"fileid": 566, "author": "Cicero", "title": "de Legibus I"},
    "cicero/leg2.txt":                           {"fileid": 567, "author": "Cicero", "title": "de Legibus II"},
    "cicero/leg3.txt":                           {"fileid": 568, "author": "Cicero", "title": "de Legibus III"},
    "cicero/legagr1.txt":                        {"fileid": 569, "author": "Cicero", "title": "de Lege Agraria I"},
    "cicero/legagr2.txt":                        {"fileid": 570, "author": "Cicero", "title": "de Lege Agraria II"},
    "cicero/legagr3.txt":                        {"fileid": 571, "author": "Cicero", "title": "de Lege Agraria III"},
    "cicero/lig.txt":                            {"fileid": 572, "author": "Cicero", "title": "pro Ligario"},
    "cicero/marc.txt":                           {"fileid": 573, "author": "Cicero", "title": "pro Marcello"},
    "cicero/milo.txt":                           {"fileid": 574, "author": "Cicero", "title": "pro Milone"},
    "cicero/murena.txt":                         {"fileid": 575, "author": "Cicero", "title": "pro Murena"},
    "cicero/nd1.txt":                            {"fileid": 576, "author": "Cicero", "title": "De Natura Deorum I"},
    "cicero/nd2.txt":                            {"fileid": 577, "author": "Cicero", "title": "De Natura Deorum II"},
    "cicero/nd3.txt":                            {"fileid": 578, "author": "Cicero", "title": "De Natura Deorum III"},
    "cicero/off1.txt":                           {"fileid": 579, "author": "Cicero", "title": "de Officiis I"},
    "cicero/off2.txt":                           {"fileid": 580, "author": "Cicero", "title": "de Officiis II"},
    "cicero/off3.txt":                           {"fileid": 581, "author": "Cicero", "title": "de Officiis III"},
    "cicero/optgen.txt":                         {
        "fileid": 582, "author": "Cicero", "title": "de Optimo Genere Oratorum"
    }, "cicero/orator.txt":                      {"fileid": 583, "author": "Cicero", "title": "Orator ad M. Brutum"},
    "cicero/oratore1.txt":                       {"fileid": 584, "author": "Cicero", "title": "de Oratore I"},
    "cicero/oratore2.txt":                       {"fileid": 585, "author": "Cicero", "title": "de Oratore II"},
    "cicero/oratore3.txt":                       {"fileid": 586, "author": "Cicero", "title": "de Oratore III"},
    "cicero/paradoxa.txt":                       {"fileid": 587, "author": "Cicero", "title": "Paradoxa"},
    "cicero/partitione.txt":                     {"fileid": 588, "author": "Cicero", "title": "de Partitione"},
    "cicero/phil1.txt":                          {"fileid": 589, "author": "Cicero", "title": "Philippic I"},
    "cicero/phil10.txt":                         {"fileid": 590, "author": "Cicero", "title": "Philippic X"},
    "cicero/phil11.txt":                         {"fileid": 591, "author": "Cicero", "title": "Philippic XI"},
    "cicero/phil12.txt":                         {"fileid": 592, "author": "Cicero", "title": "Philippic XII"},
    "cicero/phil13.txt":                         {"fileid": 593, "author": "Cicero", "title": "Philippic XIII"},
    "cicero/phil14.txt":                         {"fileid": 594, "author": "Cicero", "title": "Philippic XIV"},
    "cicero/phil2.txt":                          {"fileid": 595, "author": "Cicero", "title": "Philippic II"},
    "cicero/phil3.txt":                          {"fileid": 596, "author": "Cicero", "title": "Philippic III"},
    "cicero/phil4.txt":                          {"fileid": 597, "author": "Cicero", "title": "Philippic IV"},
    "cicero/phil5.txt":                          {"fileid": 598, "author": "Cicero", "title": "Philippic V"},
    "cicero/phil6.txt":                          {"fileid": 599, "author": "Cicero", "title": "Philippic VI"},
    "cicero/phil7.txt":                          {"fileid": 600, "author": "Cicero", "title": "Philippic VII"},
    "cicero/phil8.txt":                          {"fileid": 601, "author": "Cicero", "title": "Philippic VIII"},
    "cicero/phil9.txt":                          {"fileid": 602, "author": "Cicero", "title": "Philippic IX"},
    "cicero/piso.txt":                           {"fileid": 603, "author": "Cicero", "title": "In Pisonem"},
    "cicero/plancio.txt":                        {"fileid": 604, "author": "Cicero", "title": "Pro Plancio"},
    "cicero/postreditum.txt":                    {"fileid": 605, "author": "Cicero", "title": "Post Reditum in Senatu"},
    "cicero/postreditum2.txt":                   {
        "fileid": 606, "author": "Cicero", "title": "Post Reditum ad Quirites"
    }, "cicero/prov.txt":                        {
        "fileid": 607, "author": "Cicero", "title": "De Provinciis Consularibus"
    }, "cicero/quinc.txt":                       {"fileid": 608, "author": "Cicero", "title": "Pro Quinctio"},
    "cicero/rabirio.txt":                        {
        "fileid": 609, "author": "Cicero", "title": "Pro Rabiro Perduellionis"
    }, "cicero/rabiriopost.txt":                 {"fileid": 610, "author": "Cicero", "title": "Pro Rabiro Postumo"},
    "cicero/repub1.txt":                         {"fileid": 611, "author": "Cicero", "title": "de Re Publica I"},
    "cicero/repub2.txt":                         {"fileid": 612, "author": "Cicero", "title": "de Re Publica II"},
    "cicero/repub3.txt":                         {"fileid": 613, "author": "Cicero", "title": "de Re Publica III"},
    "cicero/repub4.txt":                         {"fileid": 614, "author": "Cicero", "title": "de Re Publica IV"},
    "cicero/repub5.txt":                         {"fileid": 615, "author": "Cicero", "title": "de Re Publica V"},
    "cicero/repub6.txt":                         {"fileid": 616, "author": "Cicero", "title": "de Re Publica VI"},
    "cicero/rosccom.txt":                        {"fileid": 617, "author": "Cicero", "title": "Pro Roscio Comodeo"},
    "cicero/scauro.txt":                         {"fileid": 618, "author": "Cicero", "title": "Pro Scauro"},
    "cicero/senectute.txt":                      {"fileid": 619, "author": "Cicero", "title": "de Senectute"},
    "cicero/sestio.txt":                         {"fileid": 620, "author": "Cicero", "title": "Pro Sestio"},
    "cicero/sex.rosc.txt":                       {
        "fileid": 621, "author": "Cicero", "title": "Pro Sex. Roscio Amerino"
    }, "cicero/sulla.txt":                       {"fileid": 622, "author": "Cicero", "title": "Pro Sulla"},
    "cicero/topica.txt":                         {"fileid": 623, "author": "Cicero", "title": "Topica"},
    "cicero/tusc1.txt":                          {
        "fileid": 624, "author": "Cicero", "title": "Tusculan Disputations I"
    }, "cicero/tusc2.txt":                       {
        "fileid": 625, "author": "Cicero", "title": "Tusculan Disputations II"
    }, "cicero/tusc3.txt":                       {
        "fileid": 626, "author": "Cicero", "title": "Tusculan Disputations III"
    }, "cicero/tusc4.txt":                       {
        "fileid": 627, "author": "Cicero", "title": "Tusculan Disputations IV"
    }, "cicero/tusc5.txt":                       {
        "fileid": 628, "author": "Cicero", "title": "Tusculan Disputations IV"
    }, "cicero/vatin.txt":                       {"fileid": 629, "author": "Cicero", "title": "In Vatinium"},
    "cicero/ver1.txt":                           {"fileid": 630, "author": "Cicero", "title": "In Verrem I"},
    "cicero/verres.2.1.txt":                     {"fileid": 631, "author": "Cicero", "title": "In Verrem II.1"},
    "cicero/verres.2.2.txt":                     {"fileid": 632, "author": "Cicero", "title": "In Verrem II.2"},
    "cicero/verres.2.3.txt":                     {"fileid": 633, "author": "Cicero", "title": "In Verrem II.3"},
    "cicero/verres.2.4.txt":                     {"fileid": 634, "author": "Cicero", "title": "In Verrem II.4"},
    "cicero/verres.2.5.txt":                     {"fileid": 635, "author": "Cicero", "title": "In Verrem II.5"},
    "cinna.txt":                                 {"fileid": 636, "author": None, "title": "Helvius Cinna"},
    "claud.inscr.txt":                           {"fileid": 637, "author": None, "title": "Speech of Claudius"},
    "claudian/claudian.cons6.txt":               {"fileid": 638, "author": None, "title": "Claudian"},
    "claudian/claudian.olyb.txt":                {
        "fileid": 639, "author": "Claudian", "title": "Panegyricus Dictus Olybrio et Probino Consulibus"
    }, "claudian/claudian.proserp1.txt":         {
        "fileid": 640, "author": "Claudian", "title": "De Raptu Proserpinae I "
    }, "claudian/claudian.proserp2.txt":         {
        "fileid": 641, "author": "Claudian", "title": "De Raptu Proserpinae II "
    }, "claudian/claudian.proserp3.txt":         {
        "fileid": 642, "author": "Claudian", "title": "De Raptu Proserpinae III "
    }, "claudian/claudian.ruf1.txt":             {"fileid": 643, "author": "Claudian", "title": "In Rufinum I "},
    "clitophon.txt":                             {"fileid": 644, "author": "Pseudo-Plato", "title": "Clitophon"},
    "colman.txt":                                {"fileid": 645, "author": None, "title": "Coleman the Irishman "},
    "columba1.txt":                              {"fileid": 646, "author": "Life of St. Columba", "title": "Book I"},
    "columba2.txt":                              {"fileid": 647, "author": "Life of St. Columba", "title": "Book II"},
    "columbus.txt":                              {"fileid": 648, "author": None, "title": "Christopher Columbus"},
    "columella/columella.arbor.txt":             {"fileid": 649, "author": "Columella", "title": "de Arboribus "},
    "columella/columella.rr1.txt":               {"fileid": 650, "author": "Columella", "title": "de Re Rustica I "},
    "columella/columella.rr10.txt":              {"fileid": 651, "author": "Columella", "title": "de Re Rustica X "},
    "columella/columella.rr11.txt":              {"fileid": 652, "author": "Columella", "title": "de Re Rustica XI "},
    "columella/columella.rr12.txt":              {"fileid": 653, "author": "Columella", "title": "de Re Rustica XII "},
    "columella/columella.rr2.txt":               {"fileid": 654, "author": "Columella", "title": "de Re Rustica II"},
    "columella/columella.rr3.txt":               {"fileid": 655, "author": "Columella", "title": "de Re Rustica III"},
    "columella/columella.rr4.txt":               {"fileid": 656, "author": "Columella", "title": "de Re Rustica IV"},
    "columella/columella.rr5.txt":               {"fileid": 657, "author": "Columella", "title": "de Re Rustica V"},
    "columella/columella.rr6.txt":               {"fileid": 658, "author": "Columella", "title": "de Re Rustica VI "},
    "columella/columella.rr7.txt":               {"fileid": 659, "author": "Columella", "title": "de Re Rustica VII"},
    "columella/columella.rr8.txt":               {"fileid": 660, "author": "Columella", "title": "de Re Rustica VIII"},
    "columella/columella.rr9.txt":               {"fileid": 661, "author": "Columella", "title": "de Re Rustica IX "},
    "comes.txt":                                 {"fileid": 662, "author": None, "title": "O Comes"},
    "commodianus/commodianus1.txt":              {
        "fileid": 663, "author": "Commodianus", "title": "Carmen de Duobus Populis"
    }, "commodianus/commodianus2.txt":           {"fileid": 664, "author": "Commodianus", "title": "Instructiones"},
    "commodianus/commodianus3.txt":              {
        "fileid": 665, "author": "Commodian", "title": "De Saeculi Istius Fine"
    }, "corvinus1.txt":                          {"fileid": 666, "author": "Laurentius Corvinus", "title": "ad Famam"},
    "corvinus2.txt":                             {
        "fileid": 667, "author": "Laurentius Corvinus", "title": "Epithalamium"
    }, "cotta.txt":                              {
        "fileid": 668, "author": None, "title": "Poems of Giovanni Cotta (1480-1510)"
    }, "creeds.txt":                             {"fileid": 669, "author": None, "title": "Early Christian Creeds"},
    "curtius/curtius10.txt":                     {
        "fileid": 670, "author": "Curtius Rufus", "title": "Historiae Alexandri Magni X"
    }, "curtius/curtius3.txt":                   {
        "fileid": 671, "author": "Curtius Rufus", "title": "Historiae Alexandri Magni III"
    }, "curtius/curtius4.txt":                   {
        "fileid": 672, "author": "Curtius Rufus", "title": "Historiae Alexandri Magni IV"
    }, "curtius/curtius5.txt":                   {
        "fileid": 673, "author": "Curtius Rufus", "title": "Historiae Alexandri Magni V"
    }, "curtius/curtius6.txt":                   {
        "fileid": 674, "author": "Curtius Rufus", "title": "Historiae Alexandri Magni VI"
    }, "curtius/curtius7.txt":                   {
        "fileid": 675, "author": "Curtius Rufus", "title": "Historiae Alexandri Magni VII"
    }, "curtius/curtius8.txt":                   {
        "fileid": 676, "author": "Curtius Rufus", "title": "Historiae Alexandri Magni VIII"
    }, "curtius/curtius9.txt":                   {
        "fileid": 677, "author": "Curtius Rufus", "title": "Historiae Alexandri Magni III"
    }, "dante/ec1.txt":                          {"fileid": 678, "author": "Dante", "title": "Ecloga I"},
    "dante/ep.txt":                              {"fileid": 679, "author": "Dante", "title": "Epistolae"},
    "dante/mon1.txt":                            {"fileid": 680, "author": "Dante", "title": "Monarchia I"},
    "dante/mon2.txt":                            {"fileid": 681, "author": "Dante", "title": "Monarchia II"},
    "dante/mon3.txt":                            {"fileid": 682, "author": "Dante", "title": "Monarchia III"},
    "dante/vulgar.txt":                          {"fileid": 683, "author": "Dante", "title": "De Vulgari Eloquentia I"},
    "dante/vulgar2.txt":                         {
        "fileid": 684, "author": "Dante", "title": "De Vulgari Eloquentia II"
    }, "dares.txt":                              {
        "fileid": 685, "author": "Dares the Phrygian", "title": "De Excidio Trojae Historia"
    }, "dares1.txt":                             {
        "fileid": 686, "author": "Dares the Phrygian", "title": "De Excidio Trojae Historia"
    }, "debury.txt":                             {"fileid": 687, "author": "de Bury", "title": "Philobiblon"},
    "declaratio.txt":                            {
        "fileid": 688, "author": None, "title": "Universal Declaration of Human Rights"
    }, "decretum.txt":                           {"fileid": 689, "author": None, "title": "Decretum Gelasianum"},
    "descartes/des.ep.txt":                      {"fileid": 690, "author": "Descartes", "title": "Epistula"},
    "descartes/des.med1.txt":                    {"fileid": 691, "author": "Descartes", "title": "Meditatio I"},
    "descartes/des.med2.txt":                    {"fileid": 692, "author": "Descartes", "title": "Meditatio II"},
    "descartes/des.med3.txt":                    {"fileid": 693, "author": "Descartes", "title": "Meditatio III"},
    "descartes/des.med4.txt":                    {"fileid": 694, "author": "Descartes", "title": "Meditatio IV"},
    "descartes/des.med5.txt":                    {"fileid": 695, "author": "Descartes", "title": "Meditatio V"},
    "descartes/des.med6.txt":                    {"fileid": 696, "author": "Descartes", "title": "Meditatio VI"},
    "descartes/des.pr.txt":                      {"fileid": 697, "author": "Descartes", "title": "Praefatio"},
    "descartes/des.syn.txt":                     {"fileid": 698, "author": "Descartes", "title": "Synopsis"},
    "dicchristi.txt":                            {"fileid": 699, "author": None, "title": ""},
    "dicquid.txt":                               {"fileid": 700, "author": None, "title": "Dic quid agis "},
    "diesirae.txt":                              {"fileid": 701, "author": None, "title": "Dies Irae"}, "diravi.txt": {
        "fileid": 702, "author": "Anonymous", "title": "Dira vi amoris teror "
    }, "don.txt":                                {"fileid": 703, "author": "Donatus", "title": "Ars Minor"},
    "donation.txt":                              {"fileid": 704, "author": None, "title": "Donation of Constantine"},
    "dulcesolum.txt":                            {"fileid": 705, "author": None, "title": ""},
    "dumdiane.txt":                              {"fileid": 706, "author": "Anonymous", "title": "Dum Diane vitrea "},
    "dumdomus.txt":                              {"fileid": 707, "author": None, "title": "Dum domus lapidea "},
    "dumestas.txt":                              {"fileid": 708, "author": None, "title": ""}, "ebulo.txt": {
        "fileid": 709, "author": "Petrus de Ebulo", "title": "Liber ad honorem Augusti sive de rebus Siculis"
    }, "egeria1.txt":                            {"fileid": 710, "author": "Egeria", "title": "Itinerarium Pars Prima"},
    "egeria2.txt":                               {
        "fileid": 711, "author": "Egeria", "title": "Itinerarium Pars Secunda"
    }, "ein.txt":                                {"fileid": 712, "author": "Einhard", "title": "Life of Charlemagne"},
    "ency.fides.txt":                            {"fileid": 713, "author": None, "title": ""},
    "enn.txt":                                   {"fileid": 714, "author": "Ennius", "title": "Fragments"},
    "ennodius.txt":                              {
        "fileid": 715, "author": "Ennodius", "title": "Panegyricus Regi Theoderico"
    }, "ep.priapismo.txt":                       {
        "fileid": 716, "author": None, "title": "Epistolae de Priapismo Cleopatrae eiusque Remediis"
    }, "epistaustras.txt":                       {"fileid": 717, "author": None, "title": "Epistolae Austrasicae"},
    "epitaphs.txt":                              {"fileid": 718, "author": None, "title": "ROMAN EPITAPHS"},
    "epitomecononiana.txt":                      {"fileid": 719, "author": None, "title": "Epitome Cononiana"},
    "epitomefeliciana.txt":                      {"fileid": 720, "author": None, "title": "Epitome Feliciana"},
    "erasmus/antibarb.txt":                      {"fileid": 721, "author": "Eramus", "title": "Libri Antibarbarorum"},
    "erasmus/coll.txt":                          {"fileid": 722, "author": "Eramus", "title": "Colloquia"},
    "erasmus/ep.txt":                            {"fileid": 723, "author": "Eramus", "title": "Selected Writings"},
    "erasmus/inst.txt":                          {"fileid": 724, "author": "Erasmus", "title": "Institutio"},
    "erasmus/laude.txt":                         {"fileid": 725, "author": "Erasmus", "title": "de Laude Matrimonii"},
    "erasmus/moriae.txt":                        {"fileid": 726, "author": "Eramus", "title": "The Praise of Folly"},
    "erasmus/querela.txt":                       {"fileid": 727, "author": "Eramus", "title": "Querela Pacis"},
    "erchempert.txt":                            {
        "fileid": 728, "author": "Erchempert", "title": "Historia Langabardorum Beneventarnorum"
    }, "estas.txt":                              {"fileid": 729, "author": None, "title": "Estas non apparuit "},
    "eucherius.txt":                             {"fileid": 730, "author": "Eucherius", "title": "De laude eremi"},
    "eugenius.txt":                              {"fileid": 731, "author": None, "title": ""}, "eugippius.txt": {
        "fileid": 732, "author": "Eugippius", "title": "Life of Saint Severinus"
    }, "eutropius/eutropius1.txt":               {"fileid": 733, "author": "Eutropius", "title": "Book I"},
    "eutropius/eutropius10.txt":                 {"fileid": 734, "author": "Eutropius", "title": "Book X"},
    "eutropius/eutropius2.txt":                  {"fileid": 735, "author": "Eutropius", "title": "Book II"},
    "eutropius/eutropius3.txt":                  {"fileid": 736, "author": "Eutropius", "title": "Book III"},
    "eutropius/eutropius4.txt":                  {"fileid": 737, "author": "Eutropius", "title": "Book IV"},
    "eutropius/eutropius5.txt":                  {"fileid": 738, "author": "Eutropius", "title": "Book V"},
    "eutropius/eutropius6.txt":                  {"fileid": 739, "author": "Eutropius", "title": "Book II"},
    "eutropius/eutropius7.txt":                  {"fileid": 740, "author": "Eutropius", "title": "Book VII"},
    "eutropius/eutropius8.txt":                  {"fileid": 741, "author": "Eutropius", "title": "Book VIII"},
    "eutropius/eutropius9.txt":                  {"fileid": 742, "author": "Eutropius", "title": "Book IX"},
    "exivi.txt":                                 {"fileid": 743, "author": None, "title": "Exivi de paradiso "},
    "fabe.txt":                                  {"fileid": 744, "author": None, "title": "Guido Fabe "},
    "falcandus.txt":                             {"fileid": 745, "author": None, "title": "Hugo Falcandus"},
    "falcone.txt":                               {"fileid": 746, "author": None, "title": "Chronicon Beneventanum"},
    "ferraria.txt":                              {"fileid": 747, "author": None, "title": "Nicolai Borbonii "},
    "ficino.txt":                                {"fileid": 748, "author": "Marsilio Ficino", "title": "Theages "},
    "fletcher.txt":                              {"fileid": 749, "author": None, "title": "Locustae "},
    "florus1.txt":                               {"fileid": 750, "author": "Florus", "title": "Epitome of Roman Wars"},
    "florus2.txt":                               {"fileid": 751, "author": "Florus", "title": "Epitome of Roman Wars"},
    "foedusaeternum.txt":                        {"fileid": 752, "author": None, "title": "Eternal Bond of Brothers"},
    "forsett1.txt":                              {"fileid": 753, "author": "Pedantius", "title": "Act I  "},
    "forsett2.txt":                              {"fileid": 754, "author": "Pedantius", "title": "Act II  "},
    "fortunat.txt":                              {"fileid": 755, "author": None, "title": "Venance Fortunat "},
    "fragmentumlaurentianum.txt":                {"fileid": 756, "author": None, "title": "Fragmentum Laurentianum"},
    "fredegarius.txt":                           {"fileid": 757, "author": "Fredegarius", "title": "Chronicon"},
    "frodebertus.txt":                           {"fileid": 758, "author": None, "title": "Frodebertus & Importunus"},
    "frontinus/aqua1.txt":                       {
        "fileid": 759, "author": "Frontinus", "title": "De aquaeductu urbis Romae I"
    }, "frontinus/aqua2.txt":                    {
        "fileid": 760, "author": "Frontinus", "title": "De aquaeductu urbis Romae II"
    }, "frontinus/contro.txt":                   {"fileid": 761, "author": "Frontinus", "title": "De Controversiis"},
    "frontinus/lim.txt":                         {"fileid": 762, "author": "Frontinus", "title": "De Limitibus"},
    "frontinus/mensoria.txt":                    {"fileid": 763, "author": "Frontinus", "title": "De Arte Mensoria"},
    "frontinus/qualitate.txt":                   {
        "fileid": 764, "author": "Frontinus", "title": "De Agrorum Qualitate"
    }, "frontinus/strat1.txt":                   {"fileid": 765, "author": "Frontinus", "title": "Strategemata I"},
    "frontinus/strat2.txt":                      {"fileid": 766, "author": "Frontinus", "title": "Strategemata II"},
    "frontinus/strat3.txt":                      {"fileid": 767, "author": "Frontinus", "title": "Strategemata III"},
    "frontinus/strat4.txt":                      {"fileid": 768, "author": "Frontinus", "title": "Strategemata IIII"},
    "fronto.txt":                                {
        "fileid": 769, "author": "M. Cornelius Fronto", "title": "Epistulae "
    }, "fulbert.txt":                            {"fileid": 770, "author": None, "title": "St. Fulbert of Chartres"},
    "fulgentius/fulgentius1.txt":                {
        "fileid": 771, "author": "Fulgentius", "title": "Mitologiarum Liber I"
    }, "fulgentius/fulgentius2.txt":             {
        "fileid": 772, "author": "Fulgentius", "title": "Mitologiarum Liber II"
    }, "fulgentius/fulgentius3.txt":             {
        "fileid": 773, "author": "Fulgentius", "title": "Mitologiarum Liber III"
    }, "fulgentius/fulgentius4.txt":             {
        "fileid": 774, "author": "Fulgentius", "title": "Expositio Sermonum Antiquorum"
    }, "fulgentius/fulgentius5.txt":             {
        "fileid": 775, "author": "Fulgentius", "title": "Expositio Virgilianae"
    }, "gaius1.txt":                             {"fileid": 776, "author": "Gaius", "title": "Commentary I"},
    "gaius2.txt":                                {"fileid": 777, "author": "Gaius", "title": "Commentary II"},
    "gaius3.txt":                                {"fileid": 778, "author": "Gaius", "title": "Commentary III"},
    "gaius4.txt":                                {"fileid": 779, "author": "Gaius", "title": "Commentary IV"},
    "galileo/galileo.sid.txt":                   {
        "fileid": 780, "author": "Galileo Galilei", "title": "Sidereus Nuncius"
    }, "garcilaso.txt":                          {"fileid": 781, "author": None, "title": "Garcilaso de la Vega "},
    "garland.txt":                               {"fileid": 782, "author": None, "title": "John of Garland"},
    "gaud.txt":                                  {"fileid": 783, "author": None, "title": "Gaudeamus Igitur"},
    "gauss.txt":                                 {"fileid": 784, "author": "Gauss", "title": "Demonstratio Nova"},
    "gellius/gellius1.txt":                      {
        "fileid": 785, "author": "Auli Gellii Noctes Atticae", "title": "Liber I"
    }, "gellius/gellius10.txt":                  {
        "fileid": 786, "author": "Auli Gellii Noctes Atticae", "title": "Liber X"
    }, "gellius/gellius11.txt":                  {
        "fileid": 787, "author": "Auli Gellii Noctes Atticae", "title": "Liber XI"
    }, "gellius/gellius13.txt":                  {
        "fileid": 788, "author": "Auli Gellii Noctes Atticae", "title": "Liber XIII"
    }, "gellius/gellius2.txt":                   {
        "fileid": 789, "author": "Auli Gellii Noctes Atticae", "title": "Liber II"
    }, "gellius/gellius20.txt":                  {
        "fileid": 790, "author": "Auli Gellii Noctes Atticae", "title": "Liber XX"
    }, "gellius/gellius3.txt":                   {
        "fileid": 791, "author": "Auli Gellii Noctes Atticae", "title": "Liber III"
    }, "gellius/gellius4.txt":                   {
        "fileid": 792, "author": "Auli Gellii Noctes Atticae", "title": "Liber IV"
    }, "gellius/gellius5.txt":                   {
        "fileid": 793, "author": "Auli Gellii Noctes Atticae", "title": "Liber V"
    }, "gellius/gellius6.txt":                   {
        "fileid": 794, "author": "Auli Gellii Noctes Atticae", "title": "Liber VI"
    }, "gellius/gellius7.txt":                   {
        "fileid": 795, "author": "Auli Gellii Noctes Atticae", "title": "Liber VII"
    }, "gellius/gellius8.txt":                   {
        "fileid": 796, "author": "Auli Gellii Noctes Atticae", "title": "Liber VIII"
    }, "gellius/gellius9.txt":                   {
        "fileid": 797, "author": "Auli Gellii Noctes Atticae", "title": "Liber IX"
    }, "gellius/gelliuscapitula.txt":            {
        "fileid": 798, "author": "Auli Gellii Noctes Atticae", "title": "Capitula"
    }, "gellius/gelliuspraef.txt":               {
        "fileid": 799, "author": "Auli Gellii Noctes Atticae", "title": "Praefatio"
    }, "germanicus.txt":                         {"fileid": 800, "author": "Germanicus", "title": "Aratea"},
    "gestafrancorum/gestafrancorum1.txt":        {"fileid": 801, "author": None, "title": "Gesta Francorum I"},
    "gestafrancorum/gestafrancorum10.txt":       {"fileid": 802, "author": None, "title": "Gesta Francorum X"},
    "gestafrancorum/gestafrancorum2.txt":        {"fileid": 803, "author": None, "title": "Gesta Francorum II"},
    "gestafrancorum/gestafrancorum3.txt":        {"fileid": 804, "author": None, "title": "Gesta Francorum III"},
    "gestafrancorum/gestafrancorum4.txt":        {"fileid": 805, "author": None, "title": "Gesta Francorum IIII"},
    "gestafrancorum/gestafrancorum5.txt":        {"fileid": 806, "author": None, "title": "Gesta Francorum V"},
    "gestafrancorum/gestafrancorum6.txt":        {"fileid": 807, "author": None, "title": "Gesta Francorum VI"},
    "gestafrancorum/gestafrancorum7.txt":        {"fileid": 808, "author": None, "title": "Gesta Francorum VII"},
    "gestafrancorum/gestafrancorum8.txt":        {"fileid": 809, "author": None, "title": "Gesta Francorum VIII"},
    "gestafrancorum/gestafrancorum9.txt":        {"fileid": 810, "author": None, "title": "Gesta Francorum IX"},
    "gestarom.txt":                              {"fileid": 811, "author": None, "title": "Gesta Romanorum"},
    "gioacchino.txt":                            {
        "fileid": 812, "author": "Gioacchino da Fiore", "title": "Adversus Iudeos"
    }, "godfrey.epigrammata.txt":                {
        "fileid": 813, "author": "Godfrey of Winchester", "title": "Epigrammata"
    }, "godfrey.epigrammatahist.txt":            {
        "fileid": 814, "author": "Godfrey of Winchester", "title": "Epigrammata Historica"
    }, "grattius.txt":                           {"fileid": 815, "author": "Grattius", "title": "Cynegetica"},
    "gravissimas.txt":                           {"fileid": 816, "author": None, "title": "Inter Gravissimas "},
    "greg.txt":                                  {
        "fileid": 817, "author": None, "title": "Letter of Gregory the Great"
    }, "gregdecretals1.txt":                     {"fileid": 818, "author": "Gregory IX", "title": "Decretals I"},
    "gregdecretals2.txt":                        {"fileid": 819, "author": "Gregory IX", "title": "Decretals II"},
    "gregdecretals3.txt":                        {"fileid": 820, "author": "Gregory IX", "title": "Decretals III"},
    "gregdecretals4.txt":                        {"fileid": 821, "author": "Gregory IX", "title": "Decretals IV"},
    "gregdecretals5.txt":                        {"fileid": 822, "author": "Gregory IX", "title": "Decretals IV"},
    "gregory7.txt":                              {
        "fileid": 823, "author": "Gregory VII", "title": "Epistolae Vagantes"
    }, "gregorytours/gregorytours1.txt":         {"fileid": 824, "author": None, "title": "Gregory of Tours I"},
    "gregorytours/gregorytours10.txt":           {"fileid": 825, "author": None, "title": "Gregory of Tours X"},
    "gregorytours/gregorytours2.txt":            {"fileid": 826, "author": None, "title": "Gregory of Tours II"},
    "gregorytours/gregorytours3.txt":            {"fileid": 827, "author": None, "title": "Gregory of Tours III"},
    "gregorytours/gregorytours4.txt":            {"fileid": 828, "author": None, "title": "Gregory of Tours IV"},
    "gregorytours/gregorytours5.txt":            {"fileid": 829, "author": None, "title": "Gregory of Tours V"},
    "gregorytours/gregorytours6.txt":            {"fileid": 830, "author": None, "title": "Gregory of Tours VI"},
    "gregorytours/gregorytours7.txt":            {"fileid": 831, "author": None, "title": "Gregory of Tours VII"},
    "gregorytours/gregorytours8.txt":            {"fileid": 832, "author": None, "title": "Gregory of Tours VIII"},
    "gregorytours/gregorytours9.txt":            {"fileid": 833, "author": None, "title": "Gregory of Tours IX"},
    "gwinne1.txt":                               {"fileid": 834, "author": "Nero", "title": "Act I  "},
    "gwinne2.txt":                               {"fileid": 835, "author": "Nero", "title": "Act II  "},
    "gwinne3.txt":                               {"fileid": 836, "author": "Nero", "title": "Act III "},
    "gwinne4.txt":                               {"fileid": 837, "author": "Nero", "title": "Act IV "},
    "gwinne5.1.txt":                             {"fileid": 838, "author": "Nero", "title": "Act V.1 "},
    "gwinne5.2.txt":                             {"fileid": 839, "author": "Nero", "title": "Act V.2 "},
    "gwinne5.3.txt":                             {"fileid": 840, "author": "Nero", "title": "Act V.3 "},
    "gwinne5.4.txt":                             {"fileid": 841, "author": "Nero", "title": "Act V.4 "}, "halley.txt": {
        "fileid": 842, "author": None, "title": "Edmond Halley (1656\u20131742)"
    }, "hebet.txt":                              {"fileid": 843, "author": None, "title": "Hebet Sidus Leti Visus"},
    "henry1.txt":                                {
        "fileid": 844, "author": None, "title": "Correspondence of Henry VII"
    }, "henry2.txt":                             {
        "fileid": 845, "author": None, "title": "Correspondence of Henry VII"
    }, "henry3.txt":                             {
        "fileid": 846, "author": None, "title": "Correspondence of Henry VII"
    }, "henrysettimello.txt":                    {"fileid": 847, "author": "Henry of Settimello", "title": "Elegia"},
    "hipp.txt":                                  {"fileid": 848, "author": None, "title": "Pseudo-Plato "},
    "histapoll.txt":                             {
        "fileid": 849, "author": None, "title": "Historia Apollonii regis Tyri"
    }, "histbrit.txt":                           {"fileid": 850, "author": None, "title": "Historia Brittonum"},
    "holberg.txt":                               {"fileid": 851, "author": None, "title": "Augustin T\u00fcnger"},
    "horace/arspoet.txt":                        {"fileid": 852, "author": "Horace", "title": "Ars Poetica"},
    "horace/carm1.txt":                          {"fileid": 853, "author": "Horace", "title": "Odes I"},
    "horace/carm2.txt":                          {"fileid": 854, "author": "Horace", "title": "Odes II"},
    "horace/carm3.txt":                          {"fileid": 855, "author": "Horace", "title": "Odes III"},
    "horace/carm4.txt":                          {"fileid": 856, "author": "Horace", "title": "Odes IV"},
    "horace/carmsaec.txt":                       {"fileid": 857, "author": "Horace", "title": "Carmen Saeculare"},
    "horace/ep.txt":                             {"fileid": 858, "author": "Horace", "title": "Epodes"},
    "horace/epist1.txt":                         {"fileid": 859, "author": "Horace", "title": "Epistulae I"},
    "horace/epist2.txt":                         {"fileid": 860, "author": "Horace", "title": "Epistulae II"},
    "horace/serm1.txt":                          {"fileid": 861, "author": "Horace", "title": "Sermonum Liber I"},
    "horace/serm2.txt":                          {"fileid": 862, "author": "Horace", "title": "Sermonum Liber II"},
    "hrabanus.txt":                              {"fileid": 863, "author": None, "title": "Hrabanus Maurus "},
    "hugo/hugo.solo.txt":                        {"fileid": 864, "author": None, "title": "Hugo of Saint Victor"},
    "hugo/hugo1.txt":                            {
        "fileid": 865, "author": "Hugo of St. Victor", "title": "Didascalicon I"
    }, "hugo/hugo2.txt":                         {
        "fileid": 866, "author": "Hugo of St. Victor", "title": "Didascalicon II"
    }, "hugo/hugo3.txt":                         {
        "fileid": 867, "author": "Hugo of St. Victor", "title": "Didascalicon III"
    }, "hugo/hugo4.txt":                         {
        "fileid": 868, "author": "Hugo of St. Victor", "title": "Didascalicon IV"
    }, "hugo/hugo5.txt":                         {
        "fileid": 869, "author": "Hugo of St. Victor", "title": "Didascalicon V"
    }, "hugo/hugo6.txt":                         {
        "fileid": 870, "author": "Hugo of St. Victor", "title": "Didascalicon VI"
    }, "hydatiuschronicon.txt":                  {"fileid": 871, "author": "Hydatius", "title": "Chronicon"},
    "hydatiusfasti.txt":                         {"fileid": 872, "author": "Hydatius", "title": "Fasti"},
    "hyginus/hyginus1.txt":                      {"fileid": 873, "author": "Hyginus", "title": "de Astronomia I"},
    "hyginus/hyginus2.txt":                      {"fileid": 874, "author": "Hyginus", "title": "de Astronomia II"},
    "hyginus/hyginus3.txt":                      {"fileid": 875, "author": "Hyginus", "title": "de Astronomia III"},
    "hyginus/hyginus4.txt":                      {"fileid": 876, "author": "Hyginus", "title": "de Astronomia IV"},
    "hyginus/hyginus5.txt":                      {"fileid": 877, "author": "Hyginus", "title": "Fabulae"},
    "hyginus/hyginus6.txt":                      {
        "fileid": 878, "author": "Pseudo-Hyginus", "title": "de Munitionibus Castrorum"
    }, "hymni.txt":                              {"fileid": 879, "author": None, "title": ""},
    "iabervocius.txt":                           {"fileid": 880, "author": "Lewis Carroll", "title": "Jabberwocky "},
    "iamdulcis.txt":                             {"fileid": 881, "author": "Anonymous", "title": "Iam, dulcis amica "},
    "ilias.txt":                                 {"fileid": 882, "author": None, "title": ""},
    "index.txt":                                 {"fileid": 883, "author": None, "title": ""},
    "indices.txt":                               {"fileid": 884, "author": None, "title": "INDEX AUCTORUM"},
    "innocent1.txt":                             {
        "fileid": 885, "author": "Lotario dei Segni", "title": "De Miseria Condicionis Humane"
    }, "innocent2.txt":                          {
        "fileid": 886, "author": "Lotario dei Segni", "title": "Dialogus inter Deum et Peccatorem"
    }, "inquisitio.txt":                         {"fileid": 887, "author": None, "title": "Inquisitio"},
    "inscriptions.txt":                          {"fileid": 888, "author": None, "title": "Inscriptiones"},
    "iordanes1.txt":                             {
        "fileid": 889, "author": None, "title": "Iordanis de Origine Actibusque Getarum"
    }, "iordanes2.txt":                          {
        "fileid": 890, "author": "Iordanes", "title": "De summa temporum vel origine actibusque gentis Romanorum"
    }, "ipsavivere.txt":                         {
        "fileid": 891, "author": "Anonymous", "title": "Ipsa vivere mihi reddidit! "
    }, "isidore/1.txt":                          {"fileid": 892, "author": "Isidore", "title": "Etymologiae I"},
    "isidore/10.txt":                            {"fileid": 893, "author": "Isidore", "title": "Etymologiae X"},
    "isidore/11.txt":                            {"fileid": 894, "author": "Isidore", "title": "Etymologiae XI"},
    "isidore/12.txt":                            {"fileid": 895, "author": "Isidore", "title": "Etymologiae XII"},
    "isidore/13.txt":                            {"fileid": 896, "author": "Isidore", "title": "Etymologiae XIII"},
    "isidore/14.txt":                            {"fileid": 897, "author": "Isidore", "title": "Etymologiae XIV"},
    "isidore/15.txt":                            {"fileid": 898, "author": "Isidore", "title": "Etymologiae XV"},
    "isidore/16.txt":                            {"fileid": 899, "author": "Isidore", "title": "Etymologiae XVI"},
    "isidore/17.txt":                            {"fileid": 900, "author": "Isidore", "title": "Etymologiae XVII "},
    "isidore/18.txt":                            {"fileid": 901, "author": "Isidore", "title": "Etymologiae XVIII "},
    "isidore/19.txt":                            {"fileid": 902, "author": "Isidore", "title": "Etymologiae XIX "},
    "isidore/2.txt":                             {"fileid": 903, "author": "Isidore", "title": "Etymologiae II"},
    "isidore/20.txt":                            {"fileid": 904, "author": "Isidore", "title": "Etymologiae XX "},
    "isidore/3.txt":                             {"fileid": 905, "author": "Isidore", "title": "Etymologiae III"},
    "isidore/4.txt":                             {"fileid": 906, "author": "Isidore", "title": "Etymologiae IV"},
    "isidore/5.txt":                             {"fileid": 907, "author": "Isidore", "title": "Etymologiae V"},
    "isidore/6.txt":                             {"fileid": 908, "author": "Isidore", "title": "Etymologiae VI"},
    "isidore/7.txt":                             {"fileid": 909, "author": "Isidore", "title": "Etymologiae VII"},
    "isidore/8.txt":                             {"fileid": 910, "author": "Isidore", "title": "Etymologiae VIII"},
    "isidore/9.txt":                             {"fileid": 911, "author": "Isidore", "title": "Etymologiae IX"},
    "isidore/historia.txt":                      {
        "fileid": 912, "author": "Isidorus Hispalensis", "title": "Historia de regibus Gothorum, Vandalorum et Suevorum"
    }, "isidore/sententiae1.txt":                {"fileid": 913, "author": "Isidore", "title": "Sentientiae I"},
    "isidore/sententiae2.txt":                   {"fileid": 914, "author": "Isidore", "title": "Sentientiae II"},
    "isidore/sententiae3.txt":                   {"fileid": 915, "author": "Isidore", "title": "Sentientiae III"},
    "janus1.txt":                                {"fileid": 916, "author": None, "title": "Janus Secundus"},
    "janus2.txt":                                {"fileid": 917, "author": None, "title": "Janus Secundus"},
    "jerome/contraioannem.txt":                  {"fileid": 918, "author": "St. Jerome", "title": "Contra Ioannem"},
    "jerome/epistulae.txt":                      {
        "fileid": 919, "author": "Sancti Hieronymi Epistulae", "title": "1-10 "
    }, "jerome/vitamalchus.txt":                 {"fileid": 920, "author": "Jerome", "title": "Life of Malchus"},
    "jerome/vitapauli.txt":                      {"fileid": 921, "author": "Jerome", "title": "Life of Paul"},
    "jfkhonor.txt":                              {
        "fileid": 922, "author": None, "title": "Honores Academici Praesidi J. F. Kennedy Berolini Tributi"
    }, "johannes.txt":                           {"fileid": 923, "author": None, "title": "Johannes de Plano Carpini"},
    "junillus.txt":                              {"fileid": 924, "author": None, "title": "Junillus"},
    "justin/1.txt":                              {"fileid": 925, "author": None, "title": "Justin I"},
    "justin/10.txt":                             {"fileid": 926, "author": None, "title": "Justin X"},
    "justin/11.txt":                             {"fileid": 927, "author": None, "title": "Justin XI"},
    "justin/12.txt":                             {"fileid": 928, "author": None, "title": "Justin XII"},
    "justin/13.txt":                             {"fileid": 929, "author": None, "title": "Justin XIII"},
    "justin/14.txt":                             {"fileid": 930, "author": None, "title": "Justin XIV"},
    "justin/15.txt":                             {"fileid": 931, "author": None, "title": "Justin XV"},
    "justin/16.txt":                             {"fileid": 932, "author": None, "title": "Justin XVI"},
    "justin/17.txt":                             {"fileid": 933, "author": None, "title": "Justin XVII"},
    "justin/18.txt":                             {"fileid": 934, "author": None, "title": "Justin XVIII"},
    "justin/19.txt":                             {"fileid": 935, "author": None, "title": "Justin XIX"},
    "justin/2.txt":                              {"fileid": 936, "author": None, "title": "Justin II"},
    "justin/20.txt":                             {"fileid": 937, "author": None, "title": "Justin XX"},
    "justin/21.txt":                             {"fileid": 938, "author": None, "title": "Justin XXI"},
    "justin/22.txt":                             {"fileid": 939, "author": None, "title": "Justin XXII"},
    "justin/23.txt":                             {"fileid": 940, "author": None, "title": "Justin XXIII"},
    "justin/24.txt":                             {"fileid": 941, "author": None, "title": "Justin XXIV"},
    "justin/25.txt":                             {"fileid": 942, "author": None, "title": "Justin XXV"},
    "justin/26.txt":                             {"fileid": 943, "author": None, "title": "Justin XXVI"},
    "justin/27.txt":                             {"fileid": 944, "author": None, "title": "Justin XXVII"},
    "justin/28.txt":                             {"fileid": 945, "author": None, "title": "Justin XXVIII"},
    "justin/29.txt":                             {"fileid": 946, "author": None, "title": "Justin XXIX"},
    "justin/3.txt":                              {"fileid": 947, "author": None, "title": "Justin III"},
    "justin/30.txt":                             {"fileid": 948, "author": None, "title": "Justin XXX"},
    "justin/31.txt":                             {"fileid": 949, "author": None, "title": "Justin XXXI"},
    "justin/32.txt":                             {"fileid": 950, "author": None, "title": "Justin XXXII"},
    "justin/33.txt":                             {"fileid": 951, "author": None, "title": "Justin XXXIII"},
    "justin/34.txt":                             {"fileid": 952, "author": None, "title": "Justin XXXIV"},
    "justin/35.txt":                             {"fileid": 953, "author": None, "title": "Justin XXXV"},
    "justin/36.txt":                             {"fileid": 954, "author": None, "title": "Justin XXXVI"},
    "justin/37.txt":                             {"fileid": 955, "author": None, "title": "Justin XXXVII"},
    "justin/38.txt":                             {"fileid": 956, "author": None, "title": "Justin XXXVIII"},
    "justin/39.txt":                             {"fileid": 957, "author": None, "title": "Justin XXXIX"},
    "justin/4.txt":                              {"fileid": 958, "author": None, "title": "Justin IV"},
    "justin/40.txt":                             {"fileid": 959, "author": None, "title": "Justin XL"},
    "justin/41.txt":                             {"fileid": 960, "author": None, "title": "Justin XLI"},
    "justin/42.txt":                             {"fileid": 961, "author": None, "title": "Justin XLII"},
    "justin/43.txt":                             {"fileid": 962, "author": None, "title": "Justin XLIII"},
    "justin/44.txt":                             {"fileid": 963, "author": None, "title": "Justin XIVL"},
    "justin/5.txt":                              {"fileid": 964, "author": None, "title": "Justin V"},
    "justin/6.txt":                              {"fileid": 965, "author": None, "title": "Justin VI"},
    "justin/7.txt":                              {"fileid": 966, "author": None, "title": "Justin VII"},
    "justin/8.txt":                              {"fileid": 967, "author": None, "title": "Justin VIII"},
    "justin/9.txt":                              {"fileid": 968, "author": None, "title": "Justin IX"},
    "justin/praefatio.txt":                      {"fileid": 969, "author": "Justin", "title": "Praefatio"},
    "justin/prologi.txt":                        {"fileid": 970, "author": "Justin", "title": "Prologues"},
    "justinian/codex1.txt":                      {"fileid": 971, "author": "Codex of Justinian", "title": "Liber I"},
    "justinian/codex10.txt":                     {"fileid": 972, "author": "Codex of Justinian", "title": "Liber X"},
    "justinian/codex11.txt":                     {"fileid": 973, "author": "Codex of Justinian", "title": "Liber XI"},
    "justinian/codex12.txt":                     {"fileid": 974, "author": "Codex of Justinian", "title": "Liber XII"},
    "justinian/codex2.txt":                      {"fileid": 975, "author": "Codex of Justinian", "title": "Liber II"},
    "justinian/codex3.txt":                      {"fileid": 976, "author": "Codex of Justinian", "title": "Liber III"},
    "justinian/codex4.txt":                      {"fileid": 977, "author": "Codex of Justinian", "title": "Liber IV"},
    "justinian/codex5.txt":                      {"fileid": 978, "author": "Codex of Justinian", "title": "Liber V"},
    "justinian/codex6.txt":                      {"fileid": 979, "author": "Codex of Justinian", "title": "Liber Vi"},
    "justinian/codex7.txt":                      {"fileid": 980, "author": "Codex of Justinian", "title": "Liber VII"},
    "justinian/codex8.txt":                      {"fileid": 981, "author": "Codex of Justinian", "title": "Liber VIII"},
    "justinian/codex9.txt":                      {"fileid": 982, "author": "Codex of Justinian", "title": "Liber IX"},
    "justinian/digest1.txt":                     {"fileid": 983, "author": "Digest of Justinian", "title": "Liber I"},
    "justinian/digest10.txt":                    {"fileid": 984, "author": "Digest of Justinian", "title": "Liber X"},
    "justinian/digest11.txt":                    {"fileid": 985, "author": "Digest of Justinian", "title": "Liber XI"},
    "justinian/digest12.txt":                    {"fileid": 986, "author": "Digest of Justinian", "title": "Liber XI"},
    "justinian/digest13.txt":                    {
        "fileid": 987, "author": "Digest of Justinian", "title": "Liber XIII"
    }, "justinian/digest14.txt":                 {"fileid": 988, "author": "Digest of Justinian", "title": "Liber XIV"},
    "justinian/digest15.txt":                    {"fileid": 989, "author": "Digest of Justinian", "title": "Liber XV"},
    "justinian/digest16.txt":                    {"fileid": 990, "author": "Digest of Justinian", "title": "Liber XVI"},
    "justinian/digest17.txt":                    {
        "fileid": 991, "author": "Digest of Justinian", "title": "Liber XVII"
    }, "justinian/digest18.txt":                 {
        "fileid": 992, "author": "Digest of Justinian", "title": "Liber XVIII"
    }, "justinian/digest19.txt":                 {"fileid": 993, "author": "Digest of Justinian", "title": "Liber XIX"},
    "justinian/digest2.txt":                     {"fileid": 994, "author": "Digest of Justinian", "title": "Liber II"},
    "justinian/digest20.txt":                    {"fileid": 995, "author": "Digest of Justinian", "title": "Liber XXX"},
    "justinian/digest21.txt":                    {"fileid": 996, "author": "Digest of Justinian", "title": "Liber XXI"},
    "justinian/digest22.txt":                    {
        "fileid": 997, "author": "Digest of Justinian", "title": "Liber XXII"
    }, "justinian/digest23.txt":                 {
        "fileid": 998, "author": "Digest of Justinian", "title": "Liber XXIII"
    }, "justinian/digest24.txt":                 {
        "fileid": 999, "author": "Digest of Justinian", "title": "Liber XXIV"
    }, "justinian/digest25.txt":                 {
        "fileid": 1000, "author": "Digest of Justinian", "title": "Liber XXV"
    }, "justinian/digest26.txt":                 {
        "fileid": 1001, "author": "Digest of Justinian", "title": "Liber XXVI"
    }, "justinian/digest27.txt":                 {
        "fileid": 1002, "author": "Digest of Justinian", "title": "Liber XXVII"
    }, "justinian/digest28.txt":                 {
        "fileid": 1003, "author": "Digest of Justinian", "title": "Liber XXVIII"
    }, "justinian/digest29.txt":                 {
        "fileid": 1004, "author": "Digest of Justinian", "title": "Liber XXIX"
    }, "justinian/digest3.txt":                  {
        "fileid": 1005, "author": "Digest of Justinian", "title": "Liber IIII"
    }, "justinian/digest30.txt":                 {
        "fileid": 1006, "author": "Digest of Justinian", "title": "Liber XXX"
    }, "justinian/digest31.txt":                 {
        "fileid": 1007, "author": "Digest of Justinian", "title": "Liber XXXI"
    }, "justinian/digest32.txt":                 {
        "fileid": 1008, "author": "Digest of Justinian", "title": "Liber XXXII"
    }, "justinian/digest33.txt":                 {
        "fileid": 1009, "author": "Digest of Justinian", "title": "Liber XXXIII"
    }, "justinian/digest34.txt":                 {
        "fileid": 1010, "author": "Digest of Justinian", "title": "Liber XXXIV"
    }, "justinian/digest35.txt":                 {
        "fileid": 1011, "author": "Digest of Justinian", "title": "Liber XXXV"
    }, "justinian/digest36.txt":                 {
        "fileid": 1012, "author": "Digest of Justinian", "title": "Liber XXXVI"
    }, "justinian/digest37.txt":                 {
        "fileid": 1013, "author": "Digest of Justinian", "title": "Liber XXXVII"
    }, "justinian/digest38.txt":                 {
        "fileid": 1014, "author": "Digest of Justinian", "title": "Liber XXXVIII"
    }, "justinian/digest39.txt":                 {
        "fileid": 1015, "author": "Digest of Justinian", "title": "Liber XXXIX"
    }, "justinian/digest4.txt":                  {"fileid": 1016, "author": "Digest of Justinian", "title": "Liber IV"},
    "justinian/digest40.txt":                    {"fileid": 1017, "author": "Digest of Justinian", "title": "Liber LX"},
    "justinian/digest41.txt":                    {
        "fileid": 1018, "author": "Digest of Justinian", "title": "Liber LXI"
    }, "justinian/digest42.txt":                 {
        "fileid": 1019, "author": "Digest of Justinian", "title": "Liber LXII"
    }, "justinian/digest43.txt":                 {
        "fileid": 1020, "author": "Digest of Justinian", "title": "Liber LXIII"
    }, "justinian/digest44.txt":                 {
        "fileid": 1021, "author": "Digest of Justinian", "title": "Liber LXIV"
    }, "justinian/digest45.txt":                 {
        "fileid": 1022, "author": "Digest of Justinian", "title": "Liber XLV"
    }, "justinian/digest46.txt":                 {
        "fileid": 1023, "author": "Digest of Justinian", "title": "Liber LXVI"
    }, "justinian/digest47.txt":                 {
        "fileid": 1024, "author": "Digest of Justinian", "title": "Liber XLVII"
    }, "justinian/digest48.txt":                 {
        "fileid": 1025, "author": "Digest of Justinian", "title": "Liber XLVIII"
    }, "justinian/digest49.txt":                 {
        "fileid": 1026, "author": "Digest of Justinian", "title": "Liber XLI"
    }, "justinian/digest5.txt":                  {"fileid": 1027, "author": "Digest of Justinian", "title": "Liber V"},
    "justinian/digest50.txt":                    {"fileid": 1028, "author": "Digest of Justinian", "title": "Liber L"},
    "justinian/digest6.txt":                     {"fileid": 1029, "author": "Digest of Justinian", "title": "Liber VI"},
    "justinian/digest7.txt":                     {
        "fileid": 1030, "author": "Digest of Justinian", "title": "Liber VII"
    }, "justinian/digest8.txt":                  {
        "fileid": 1031, "author": "Digest of Justinian", "title": "Liber VIII"
    }, "justinian/digest9.txt":                  {"fileid": 1032, "author": "Digest of Justinian", "title": "Liber IX"},
    "justinian/institutes.proem.txt":            {
        "fileid": 1033, "author": "The Institutes of Justinian", "title": "Introduction"
    }, "justinian/institutes1.txt":              {
        "fileid": 1034, "author": "The Institutes of Justinian", "title": "Book 1"
    }, "justinian/institutes2.txt":              {
        "fileid": 1035, "author": "The Institutes of Justinian", "title": "Book 1"
    }, "justinian/institutes3.txt":              {
        "fileid": 1036, "author": "The Institutes of Justinian", "title": "Book 3"
    }, "justinian/institutes4.txt":              {
        "fileid": 1037, "author": "The Institutes of Justinian", "title": "Book 4"
    }, "juvenal/1.txt":                          {"fileid": 1038, "author": "Juvenal", "title": "Satires I"},
    "juvenal/10.txt":                            {"fileid": 1039, "author": "Juvenal", "title": "Satires X"},
    "juvenal/11.txt":                            {"fileid": 1040, "author": "Juvenal", "title": "Satires XI"},
    "juvenal/12.txt":                            {"fileid": 1041, "author": "Juvenal", "title": "Satires XII"},
    "juvenal/13.txt":                            {"fileid": 1042, "author": "Juvenal", "title": "Satires XIII"},
    "juvenal/14.txt":                            {"fileid": 1043, "author": "Juvenal", "title": "Satires XIV"},
    "juvenal/15.txt":                            {"fileid": 1044, "author": "Juvenal", "title": "Satires XV"},
    "juvenal/16.txt":                            {"fileid": 1045, "author": "Juvenal", "title": "Satires XVI"},
    "juvenal/2.txt":                             {"fileid": 1046, "author": "Juvenal", "title": "Satires II"},
    "juvenal/3.txt":                             {"fileid": 1047, "author": "Juvenal", "title": "Satires III"},
    "juvenal/4.txt":                             {"fileid": 1048, "author": "Juvenal", "title": "Satires IV"},
    "juvenal/5.txt":                             {"fileid": 1049, "author": "Juvenal", "title": "Satires V"},
    "juvenal/6.txt":                             {"fileid": 1050, "author": "Juvenal", "title": "Satires VI"},
    "juvenal/7.txt":                             {"fileid": 1051, "author": "Juvenal", "title": "Satires VII"},
    "juvenal/8.txt":                             {"fileid": 1052, "author": "Juvenal", "title": "Satires VIII"},
    "juvenal/9.txt":                             {"fileid": 1053, "author": "Juvenal", "title": "Satires IX"},
    "kalila.txt":                                {"fileid": 1054, "author": None, "title": "Liber Kalilae et Dimnae"},
    "kempis/kempis1.txt":                        {
        "fileid": 1055, "author": "THOMAS \u00c0 KEMPIS", "title": "DE IMITATIONE CHRISTI LIBER PRIMUS"
    }, "kempis/kempis2.txt":                     {
        "fileid": 1056, "author": "THOMAS \u00c0 KEMPIS", "title": "DE IMITATIONE CHRISTI LIBER SECUNDUS"
    }, "kempis/kempis3.txt":                     {
        "fileid": 1057, "author": "THOMAS \u00c0 KEMPIS", "title": "DE IMITATIONE CHRISTI LIBER TERTIUS"
    }, "kempis/kempis4.txt":                     {
        "fileid": 1058, "author": "THOMAS \u00c0 KEMPIS", "title": "DE IMITATIONE CHRISTI LIBER QUARTUS"
    }, "kepler/strena.txt":                      {
        "fileid": 1059, "author": "JOANNIS KEPLERI", "title": "STRENA SEU DE NIVE SEXANGULA"
    }, "lactantius/demort.txt":                  {
        "fileid": 1060, "author": "Lactantius", "title": "de Mortibus Persecutorum"
    }, "lactantius/divinst1.txt":                {
        "fileid": 1061, "author": "Lactantius", "title": "Divinarum Institutionum Liber I"
    }, "landor.1858.txt":                        {"fileid": 1062, "author": "Dry Sticks Fagoted", "title": "1858 "},
    "landor1795.txt":                            {"fileid": 1063, "author": None, "title": ""},
    "landor1806.txt":                            {"fileid": 1064, "author": "Simonidea", "title": "1806 "},
    "landor1810.txt":                            {"fileid": 1065, "author": "Landor", "title": "Simonidea, 1806 "},
    "legenda.stephani.txt":                      {
        "fileid": 1066, "author": None, "title": "Legenda Maior Sancti Regis Stephani"
    }, "leo1.txt":                               {
        "fileid": 1067, "author": "Leo of Naples", "title": "Historia de preliis Alexandri Magni"
    }, "leo2.txt":                               {
        "fileid": 1068, "author": "Leo of Naples", "title": "Historia de preliis Alexandri Magni"
    }, "leo3.txt":                               {
        "fileid": 1069, "author": "Leo of Naples", "title": "Historia de preliis Alexandri Magni"
    }, "leothegreat/quadragesima1.txt":          {"fileid": 1070, "author": None, "title": "Leo the Great "},
    "leothegreat/quadragesima2.txt":             {"fileid": 1071, "author": None, "title": "Leo the Great "},
    "letabundus.txt":                            {"fileid": 1072, "author": "Anonymous", "title": "Letabundus rediit "},
    "levis.txt":                                 {"fileid": 1073, "author": None, "title": ""},
    "lhomond.historiae.txt":                     {
        "fileid": 1074, "author": "Lhomond", "title": "Epitome historiae sacrae"
    }, "lhomond.viris.txt":                      {"fileid": 1075, "author": "Lhomond", "title": "de viris illustribus"},
    "liberpontificalis1.txt":                    {"fileid": 1076, "author": None, "title": "Liber Pontificalis"},
    "livy/liv.1.txt":                            {"fileid": 1077, "author": "Livy", "title": "Book I"},
    "livy/liv.10.txt":                           {"fileid": 1078, "author": "Livy", "title": "Book X"},
    "livy/liv.2.txt":                            {"fileid": 1079, "author": "Livy", "title": "Book II"},
    "livy/liv.21.txt":                           {"fileid": 1080, "author": "Livy", "title": "Book XXI"},
    "livy/liv.22.txt":                           {"fileid": 1081, "author": "Livy", "title": "Book XXII"},
    "livy/liv.23.txt":                           {"fileid": 1082, "author": "Livy", "title": "Book XXIII"},
    "livy/liv.24.txt":                           {"fileid": 1083, "author": "Livy", "title": "Book XXIV"},
    "livy/liv.25.txt":                           {"fileid": 1084, "author": "Livy", "title": "Book XXV"},
    "livy/liv.26.txt":                           {"fileid": 1085, "author": "Livy", "title": "Book XXVI"},
    "livy/liv.27.txt":                           {"fileid": 1086, "author": "Livy", "title": "Book XXVII"},
    "livy/liv.28.txt":                           {"fileid": 1087, "author": "Livy", "title": "Book XXVIII"},
    "livy/liv.29.txt":                           {"fileid": 1088, "author": "Livy", "title": "Book XXIX"},
    "livy/liv.3.txt":                            {"fileid": 1089, "author": "Livy", "title": "Book III"},
    "livy/liv.30.txt":                           {"fileid": 1090, "author": "Livy", "title": "Book XXX"},
    "livy/liv.31.txt":                           {"fileid": 1091, "author": "Livy", "title": "Book XXXI"},
    "livy/liv.32.txt":                           {"fileid": 1092, "author": "Livy", "title": "Book XXXII"},
    "livy/liv.33.txt":                           {"fileid": 1093, "author": "Livy", "title": "Book XXXIII"},
    "livy/liv.34.txt":                           {"fileid": 1094, "author": "Livy", "title": "Book XXXIV"},
    "livy/liv.35.txt":                           {"fileid": 1095, "author": "Livy", "title": "Book XXXV"},
    "livy/liv.36.txt":                           {"fileid": 1096, "author": "Livy", "title": "Book XXXVI"},
    "livy/liv.37.txt":                           {"fileid": 1097, "author": "Livy", "title": "Book XXXVII"},
    "livy/liv.38.txt":                           {"fileid": 1098, "author": "Livy", "title": "Book XXXVIII"},
    "livy/liv.39.txt":                           {"fileid": 1099, "author": "Livy", "title": "Book XXXIX"},
    "livy/liv.4.txt":                            {"fileid": 1100, "author": "Livy", "title": "Book IV"},
    "livy/liv.40.txt":                           {"fileid": 1101, "author": "Livy", "title": "Book XL"},
    "livy/liv.41.txt":                           {"fileid": 1102, "author": "Livy", "title": "Book XLI"},
    "livy/liv.42.txt":                           {"fileid": 1103, "author": "Livy", "title": "Book XLII"},
    "livy/liv.43.txt":                           {"fileid": 1104, "author": "Livy", "title": "Book XLIII"},
    "livy/liv.44.txt":                           {"fileid": 1105, "author": "Livy", "title": "Book XLIV"},
    "livy/liv.45.txt":                           {"fileid": 1106, "author": "Livy", "title": "Book XLV"},
    "livy/liv.5.txt":                            {"fileid": 1107, "author": "Livy", "title": "Book V"},
    "livy/liv.6.txt":                            {"fileid": 1108, "author": "Livy", "title": "Book VI"},
    "livy/liv.7.txt":                            {"fileid": 1109, "author": "Livy", "title": "Book VII"},
    "livy/liv.8.txt":                            {"fileid": 1110, "author": "Livy", "title": "Book VIII"},
    "livy/liv.9.txt":                            {"fileid": 1111, "author": "Livy", "title": "Book IX"},
    "livy/liv.per.txt":                          {"fileid": 1112, "author": "Livy", "title": "Periochae"},
    "livy/liv.per1.txt":                         {"fileid": 1113, "author": "Livy", "title": "Periocha I"},
    "livy/liv.per10.txt":                        {"fileid": 1114, "author": "Livy", "title": "Periocha X"},
    "livy/liv.per100.txt":                       {"fileid": 1115, "author": "Livy", "title": "Periocha C"},
    "livy/liv.per101.txt":                       {"fileid": 1116, "author": "Livy", "title": "Periocha CI"},
    "livy/liv.per102.txt":                       {"fileid": 1117, "author": "Livy", "title": "Periocha CII"},
    "livy/liv.per103.txt":                       {"fileid": 1118, "author": "Livy", "title": "Periocha CIII"},
    "livy/liv.per104.txt":                       {"fileid": 1119, "author": "Livy", "title": "Periocha CIV"},
    "livy/liv.per105.txt":                       {"fileid": 1120, "author": "Livy", "title": "Periocha CV"},
    "livy/liv.per106.txt":                       {"fileid": 1121, "author": "Livy", "title": "Periocha CVI"},
    "livy/liv.per107.txt":                       {"fileid": 1122, "author": "Livy", "title": "Periocha CVII"},
    "livy/liv.per108.txt":                       {"fileid": 1123, "author": "Livy", "title": "Periocha CVIII"},
    "livy/liv.per109.txt":                       {"fileid": 1124, "author": "Livy", "title": "Periocha CIX"},
    "livy/liv.per11.txt":                        {"fileid": 1125, "author": "Livy", "title": "Periocha XI"},
    "livy/liv.per110.txt":                       {"fileid": 1126, "author": "Livy", "title": "Periocha CX"},
    "livy/liv.per111.txt":                       {"fileid": 1127, "author": "Livy", "title": "Periocha CXI"},
    "livy/liv.per112.txt":                       {"fileid": 1128, "author": "Livy", "title": "Periocha CXII"},
    "livy/liv.per113.txt":                       {"fileid": 1129, "author": "Livy", "title": "Periocha CXIII"},
    "livy/liv.per114.txt":                       {"fileid": 1130, "author": "Livy", "title": "Periocha CXIV"},
    "livy/liv.per115.txt":                       {"fileid": 1131, "author": "Livy", "title": "Periocha CXV"},
    "livy/liv.per116.txt":                       {"fileid": 1132, "author": "Livy", "title": "Periocha CXVI"},
    "livy/liv.per117.txt":                       {"fileid": 1133, "author": "Livy", "title": "Periocha CXVII"},
    "livy/liv.per118.txt":                       {"fileid": 1134, "author": "Livy", "title": "Periocha CXVIII"},
    "livy/liv.per119.txt":                       {"fileid": 1135, "author": "Livy", "title": "Periocha CXIX"},
    "livy/liv.per12.txt":                        {"fileid": 1136, "author": "Livy", "title": "Periocha XII"},
    "livy/liv.per120.txt":                       {"fileid": 1137, "author": "Livy", "title": "Periocha CXX"},
    "livy/liv.per121.txt":                       {"fileid": 1138, "author": "Livy", "title": "Periocha CXXI"},
    "livy/liv.per122.txt":                       {"fileid": 1139, "author": "Livy", "title": "Periocha CXXII"},
    "livy/liv.per123.txt":                       {"fileid": 1140, "author": "Livy", "title": "Periocha CXXIII"},
    "livy/liv.per124.txt":                       {"fileid": 1141, "author": "Livy", "title": "Periocha CXXIV"},
    "livy/liv.per125.txt":                       {"fileid": 1142, "author": "Livy", "title": "Periocha CXXV"},
    "livy/liv.per126.txt":                       {"fileid": 1143, "author": "Livy", "title": "Periocha CXXVI"},
    "livy/liv.per127.txt":                       {"fileid": 1144, "author": "Livy", "title": "Periocha CXXVII"},
    "livy/liv.per128.txt":                       {"fileid": 1145, "author": "Livy", "title": "Periocha CXXVIII"},
    "livy/liv.per129.txt":                       {"fileid": 1146, "author": "Livy", "title": "Periocha CXXIX"},
    "livy/liv.per13.txt":                        {"fileid": 1147, "author": "Livy", "title": "Periocha XIII"},
    "livy/liv.per130.txt":                       {"fileid": 1148, "author": "Livy", "title": "Periocha CXXX"},
    "livy/liv.per131.txt":                       {"fileid": 1149, "author": "Livy", "title": "Periocha CXXXI"},
    "livy/liv.per132.txt":                       {"fileid": 1150, "author": "Livy", "title": "Periocha CXXXII"},
    "livy/liv.per133.txt":                       {"fileid": 1151, "author": "Livy", "title": "Periocha CXXXIII"},
    "livy/liv.per134.txt":                       {"fileid": 1152, "author": "Livy", "title": "Periocha CXXXIV"},
    "livy/liv.per135.txt":                       {"fileid": 1153, "author": "Livy", "title": "Periocha CXXXV"},
    "livy/liv.per136-7.txt":                     {
        "fileid": 1154, "author": "Livy", "title": "Periocha CXXXVI et CXXXVII"
    }, "livy/liv.per138.txt":                    {"fileid": 1155, "author": "Livy", "title": "Periocha CXXXVIII"},
    "livy/liv.per139.txt":                       {"fileid": 1156, "author": "Livy", "title": "Periocha CXXXIX"},
    "livy/liv.per14.txt":                        {"fileid": 1157, "author": "Livy", "title": "Periocha XIV"},
    "livy/liv.per140.txt":                       {"fileid": 1158, "author": "Livy", "title": "Periocha CXL"},
    "livy/liv.per141.txt":                       {"fileid": 1159, "author": "Livy", "title": "Periocha CXLI"},
    "livy/liv.per142.txt":                       {"fileid": 1160, "author": "Livy", "title": "Periocha CXLII"},
    "livy/liv.per15.txt":                        {"fileid": 1161, "author": "Livy", "title": "Periocha XV"},
    "livy/liv.per16.txt":                        {"fileid": 1162, "author": "Livy", "title": "Periocha XVI"},
    "livy/liv.per17.txt":                        {"fileid": 1163, "author": "Livy", "title": "Periocha XVI"},
    "livy/liv.per18.txt":                        {"fileid": 1164, "author": "Livy", "title": "Periocha XVIII"},
    "livy/liv.per19.txt":                        {"fileid": 1165, "author": "Livy", "title": "Periocha XIX"},
    "livy/liv.per2.txt":                         {"fileid": 1166, "author": "Livy", "title": "Periocha II"},
    "livy/liv.per20.txt":                        {"fileid": 1167, "author": "Livy", "title": "Periocha XX"},
    "livy/liv.per21.txt":                        {"fileid": 1168, "author": "Livy", "title": "Periocha XXI"},
    "livy/liv.per22.txt":                        {"fileid": 1169, "author": "Livy", "title": "Periocha XXII"},
    "livy/liv.per23.txt":                        {"fileid": 1170, "author": "Livy", "title": "Periocha XXIII"},
    "livy/liv.per24.txt":                        {"fileid": 1171, "author": "Livy", "title": "Periocha XXIV"},
    "livy/liv.per25.txt":                        {"fileid": 1172, "author": "Livy", "title": "Periocha XXV"},
    "livy/liv.per26.txt":                        {"fileid": 1173, "author": "Livy", "title": "Periocha XXVI"},
    "livy/liv.per27.txt":                        {"fileid": 1174, "author": "Livy", "title": "Periocha XXVII"},
    "livy/liv.per28.txt":                        {"fileid": 1175, "author": "Livy", "title": "Periocha XXVIII"},
    "livy/liv.per29.txt":                        {"fileid": 1176, "author": "Livy", "title": "Periocha XXIX"},
    "livy/liv.per3.txt":                         {"fileid": 1177, "author": "Livy", "title": "Periocha III"},
    "livy/liv.per30.txt":                        {"fileid": 1178, "author": "Livy", "title": "Periocha XXX"},
    "livy/liv.per31.txt":                        {"fileid": 1179, "author": "Livy", "title": "Periocha XXXI"},
    "livy/liv.per32.txt":                        {"fileid": 1180, "author": "Livy", "title": "Periocha XXXII"},
    "livy/liv.per33.txt":                        {"fileid": 1181, "author": "Livy", "title": "Periocha XXXIII"},
    "livy/liv.per34.txt":                        {"fileid": 1182, "author": "Livy", "title": "Periocha XXXIV"},
    "livy/liv.per35.txt":                        {"fileid": 1183, "author": "Livy", "title": "Periocha XXXV"},
    "livy/liv.per36.txt":                        {"fileid": 1184, "author": "Livy", "title": "Periocha XXXVI"},
    "livy/liv.per37.txt":                        {"fileid": 1185, "author": "Livy", "title": "Periocha XXXVII"},
    "livy/liv.per38.txt":                        {"fileid": 1186, "author": "Livy", "title": "Periocha XXXVIII"},
    "livy/liv.per39.txt":                        {"fileid": 1187, "author": "Livy", "title": "Periocha XXXIX"},
    "livy/liv.per4.txt":                         {"fileid": 1188, "author": "Livy", "title": "Periocha IV"},
    "livy/liv.per40.txt":                        {"fileid": 1189, "author": "Livy", "title": "Periocha XL"},
    "livy/liv.per41.txt":                        {"fileid": 1190, "author": "Livy", "title": "Periocha XLI"},
    "livy/liv.per42.txt":                        {"fileid": 1191, "author": "Livy", "title": "Periocha XLII"},
    "livy/liv.per43.txt":                        {"fileid": 1192, "author": "Livy", "title": "Periocha XLIII"},
    "livy/liv.per44.txt":                        {"fileid": 1193, "author": "Livy", "title": "Periocha XLIV"},
    "livy/liv.per45.txt":                        {"fileid": 1194, "author": "Livy", "title": "Periocha XLV"},
    "livy/liv.per46.txt":                        {"fileid": 1195, "author": "Livy", "title": "Periocha XLVI"},
    "livy/liv.per47.txt":                        {"fileid": 1196, "author": "Livy", "title": "Periocha XLVII"},
    "livy/liv.per48.txt":                        {"fileid": 1197, "author": "Livy", "title": "Periocha XLVIII"},
    "livy/liv.per49.txt":                        {"fileid": 1198, "author": "Livy", "title": "Periocha XLIX"},
    "livy/liv.per5.txt":                         {"fileid": 1199, "author": "Livy", "title": "Periocha V"},
    "livy/liv.per50.txt":                        {"fileid": 1200, "author": "Livy", "title": "Periocha L"},
    "livy/liv.per51.txt":                        {"fileid": 1201, "author": "Livy", "title": "Periocha LI"},
    "livy/liv.per52.txt":                        {"fileid": 1202, "author": "Livy", "title": "Periocha LII"},
    "livy/liv.per53.txt":                        {"fileid": 1203, "author": "Livy", "title": "Periocha LIII"},
    "livy/liv.per54.txt":                        {"fileid": 1204, "author": "Livy", "title": "Periocha LIV"},
    "livy/liv.per55.txt":                        {"fileid": 1205, "author": "Livy", "title": "Periocha LV"},
    "livy/liv.per56.txt":                        {"fileid": 1206, "author": "Livy", "title": "Periocha LVI"},
    "livy/liv.per57.txt":                        {"fileid": 1207, "author": "Livy", "title": "Periocha LVII"},
    "livy/liv.per58.txt":                        {"fileid": 1208, "author": "Livy", "title": "Periocha LVIII"},
    "livy/liv.per59.txt":                        {"fileid": 1209, "author": "Livy", "title": "Periocha LIX"},
    "livy/liv.per6.txt":                         {"fileid": 1210, "author": "Livy", "title": "Periocha VI"},
    "livy/liv.per60.txt":                        {"fileid": 1211, "author": "Livy", "title": "Periocha LX"},
    "livy/liv.per61.txt":                        {"fileid": 1212, "author": "Livy", "title": "Periocha LXI"},
    "livy/liv.per62.txt":                        {"fileid": 1213, "author": "Livy", "title": "Periocha LXII"},
    "livy/liv.per63.txt":                        {"fileid": 1214, "author": "Livy", "title": "Periocha LXIII"},
    "livy/liv.per64.txt":                        {"fileid": 1215, "author": "Livy", "title": "Periocha LXIV"},
    "livy/liv.per65.txt":                        {"fileid": 1216, "author": "Livy", "title": "Periocha LXV"},
    "livy/liv.per66.txt":                        {"fileid": 1217, "author": "Livy", "title": "Periocha LXVI"},
    "livy/liv.per67.txt":                        {"fileid": 1218, "author": "Livy", "title": "Periocha LXVII"},
    "livy/liv.per68.txt":                        {"fileid": 1219, "author": "Livy", "title": "Periocha LXVIII"},
    "livy/liv.per69.txt":                        {"fileid": 1220, "author": "Livy", "title": "Periocha LXIX"},
    "livy/liv.per7.txt":                         {"fileid": 1221, "author": "Livy", "title": "Periocha VII"},
    "livy/liv.per70.txt":                        {"fileid": 1222, "author": "Livy", "title": "Periocha LXX"},
    "livy/liv.per71.txt":                        {"fileid": 1223, "author": "Livy", "title": "Periocha LXXI"},
    "livy/liv.per72.txt":                        {"fileid": 1224, "author": "Livy", "title": "Periocha LXXII"},
    "livy/liv.per73.txt":                        {"fileid": 1225, "author": "Livy", "title": "Periocha LXXIII"},
    "livy/liv.per74.txt":                        {"fileid": 1226, "author": "Livy", "title": "Periocha LXXIV"},
    "livy/liv.per75.txt":                        {"fileid": 1227, "author": "Livy", "title": "Periocha LXXV"},
    "livy/liv.per76.txt":                        {"fileid": 1228, "author": "Livy", "title": "Periocha LXXVI"},
    "livy/liv.per77.txt":                        {"fileid": 1229, "author": "Livy", "title": "Periocha LXXVII"},
    "livy/liv.per78.txt":                        {"fileid": 1230, "author": "Livy", "title": "Periocha LXXVIII"},
    "livy/liv.per79.txt":                        {"fileid": 1231, "author": "Livy", "title": "Periocha LXXIX"},
    "livy/liv.per8.txt":                         {"fileid": 1232, "author": "Livy", "title": "Periocha VIII"},
    "livy/liv.per80.txt":                        {"fileid": 1233, "author": "Livy", "title": "Periocha LXXX"},
    "livy/liv.per81.txt":                        {"fileid": 1234, "author": "Livy", "title": "Periocha LXXXI"},
    "livy/liv.per82.txt":                        {"fileid": 1235, "author": "Livy", "title": "Periocha LXXXII"},
    "livy/liv.per83.txt":                        {"fileid": 1236, "author": "Livy", "title": "Periocha LXXXIII"},
    "livy/liv.per84.txt":                        {"fileid": 1237, "author": "Livy", "title": "Periocha LXXXIV"},
    "livy/liv.per85.txt":                        {"fileid": 1238, "author": "Livy", "title": "Periocha LXXXV"},
    "livy/liv.per86.txt":                        {"fileid": 1239, "author": "Livy", "title": "Periocha LXXXVI"},
    "livy/liv.per87.txt":                        {"fileid": 1240, "author": "Livy", "title": "Periocha LXXXVII"},
    "livy/liv.per88.txt":                        {"fileid": 1241, "author": "Livy", "title": "Periocha LXXXVIII"},
    "livy/liv.per89.txt":                        {"fileid": 1242, "author": "Livy", "title": "Periocha LXXXIX"},
    "livy/liv.per9.txt":                         {"fileid": 1243, "author": "Livy", "title": "Periocha IX"},
    "livy/liv.per90.txt":                        {"fileid": 1244, "author": "Livy", "title": "Periocha XC"},
    "livy/liv.per91.txt":                        {"fileid": 1245, "author": "Livy", "title": "Periocha XCI"},
    "livy/liv.per92.txt":                        {"fileid": 1246, "author": "Livy", "title": "Periocha XCII"},
    "livy/liv.per93.txt":                        {"fileid": 1247, "author": "Livy", "title": "Periocha XCIII"},
    "livy/liv.per94.txt":                        {"fileid": 1248, "author": "Livy", "title": "Periocha XCIV"},
    "livy/liv.per95.txt":                        {"fileid": 1249, "author": "Livy", "title": "Periocha XCV"},
    "livy/liv.per96.txt":                        {"fileid": 1250, "author": "Livy", "title": "Periocha XCVI"},
    "livy/liv.per97.txt":                        {"fileid": 1251, "author": "Livy", "title": "Periocha XCVII"},
    "livy/liv.per98.txt":                        {"fileid": 1252, "author": "Livy", "title": "Periocha XCVIII"},
    "livy/liv.per99.txt":                        {"fileid": 1253, "author": "Livy", "title": "Periocha XCIX"},
    "livy/liv.pr.txt":                           {"fileid": 1254, "author": "Livy", "title": "Preface"},
    "lotichius.txt":                             {"fileid": 1255, "author": "Lotichius", "title": "De puella infelici"},
    "lucan/lucan1.txt":                          {"fileid": 1256, "author": "Lucan", "title": "Liber I"},
    "lucan/lucan10.txt":                         {"fileid": 1257, "author": "Lucan", "title": "Liber X"},
    "lucan/lucan2.txt":                          {"fileid": 1258, "author": "Lucan", "title": "Liber II"},
    "lucan/lucan3.txt":                          {"fileid": 1259, "author": "Lucan", "title": "Liber III"},
    "lucan/lucan4.txt":                          {"fileid": 1260, "author": "Lucan", "title": "Liber IV"},
    "lucan/lucan5.txt":                          {"fileid": 1261, "author": "Lucan", "title": "Liber V"},
    "lucan/lucan6.txt":                          {"fileid": 1262, "author": "Lucan", "title": "Liber VI"},
    "lucan/lucan7.txt":                          {"fileid": 1263, "author": "Lucan", "title": "Liber VII"},
    "lucan/lucan8.txt":                          {"fileid": 1264, "author": "Lucan", "title": "Liber VIII"},
    "lucan/lucan9.txt":                          {"fileid": 1265, "author": "Lucan", "title": "Liber IX"},
    "lucernarium.txt":                           {"fileid": 1266, "author": None, "title": "Ad Lucernarium "},
    "lucretius/lucretius1.txt":                  {"fileid": 1267, "author": "Lucretius", "title": "De Rerum Natura I"},
    "lucretius/lucretius2.txt":                  {"fileid": 1268, "author": "Lucretius", "title": "De Rerum Natura II"},
    "lucretius/lucretius3.txt":                  {
        "fileid": 1269, "author": "Lucretius", "title": "De Rerum Natura III"
    }, "lucretius/lucretius4.txt":               {"fileid": 1270, "author": "Lucretius", "title": "De Rerum Natura IV"},
    "lucretius/lucretius5.txt":                  {"fileid": 1271, "author": "Lucretius", "title": "De Rerum Natura V"},
    "lucretius/lucretius6.txt":                  {"fileid": 1272, "author": "Lucretius", "title": "De Rerum Natura VI"},
    "luther.95.txt":                             {"fileid": 1273, "author": "Luther", "title": "95 Theses "},
    "luther.lteramus.txt":                       {"fileid": 1274, "author": "Luther", "title": "Letter to Erasmus "},
    "luther.praef.txt":                          {"fileid": 1275, "author": None, "title": ""},
    "macarius.txt":                              {"fileid": 1276, "author": None, "title": "Macarius of Alexandria"},
    "macarius1.txt":                             {
        "fileid": 1277, "author": "Marcarius the Great", "title": "Apophthegmata"
    }, "magnacarta.txt":                         {"fileid": 1278, "author": None, "title": "Magna Carta"},
    "maidstone.txt":                             {
        "fileid": 1279, "author": None, "title": "Martyrium Ricardi Archiepiscopi"
    }, "malaterra1.txt":                         {
        "fileid": 1280, "author": "Gaufredo Malaterra",
        "title":  "De rebus gestis Rogerii Calabriae et Siciliae Comitis et Roberti Guiscardi Ducis fratris eius"
    }, "malaterra2.txt":                         {
        "fileid": 1281, "author": "Gaufredo Malaterra",
        "title":  "De rebus gestis Rogerii Calabriae et Siciliae Comitis et Roberti Guiscardi Ducis fratris eius"
    }, "malaterra3.txt":                         {
        "fileid": 1282, "author": "Gaufredo Malaterra",
        "title":  "De rebus gestis Rogerii Calabriae et Siciliae Comitis et Roberti Guiscardi Ducis fratris eius"
    }, "malaterra4.txt":                         {
        "fileid": 1283, "author": "Gaufredo Malaterra",
        "title":  "De rebus gestis Rogerii Calabriae et Siciliae Comitis et Roberti Guiscardi Ducis fratris eius"
    }, "manilius1.txt":                          {"fileid": 1284, "author": "Manilius", "title": "Liber I"},
    "manilius2.txt":                             {"fileid": 1285, "author": "Manilius", "title": "Liber II"},
    "manilius3.txt":                             {"fileid": 1286, "author": "Manilius", "title": "Liber IIi"},
    "manilius4.txt":                             {"fileid": 1287, "author": "Manilius", "title": "Liber IV"},
    "manilius5.txt":                             {"fileid": 1288, "author": "Manilius", "title": "Liber V"},
    "mapps1.txt":                                {
        "fileid": 1289, "author": "Walter Mapps", "title": "de Mauro et Zoilo"
    }, "mapps2.txt":                             {
        "fileid": 1290, "author": "Walter Mapps", "title": "de Phillide et Flora"
    }, "marbodus.txt":                           {
        "fileid": 1291, "author": "Marbodus", "title": "Libellus de ornamentis verborum"
    }, "marcellinus1.txt":                       {"fileid": 1292, "author": None, "title": "Marcellinus Comes"},
    "marcellinus2.txt":                          {"fileid": 1293, "author": None, "title": "Marcellinus Comes"},
    "martial/mart.spec.txt":                     {"fileid": 1294, "author": "Martial", "title": "Liber de Spectaculis"},
    "martial/mart1.txt":                         {"fileid": 1295, "author": None, "title": "Martial I"},
    "martial/mart10.txt":                        {"fileid": 1296, "author": None, "title": "Martial X"},
    "martial/mart11.txt":                        {"fileid": 1297, "author": None, "title": "Martial XI"},
    "martial/mart12.txt":                        {"fileid": 1298, "author": None, "title": "Martial XII"},
    "martial/mart13.txt":                        {"fileid": 1299, "author": None, "title": "Martial XIII"},
    "martial/mart14.txt":                        {"fileid": 1300, "author": "Martial", "title": "Apophoreta"},
    "martial/mart2.txt":                         {"fileid": 1301, "author": None, "title": "Martial II"},
    "martial/mart3.txt":                         {"fileid": 1302, "author": None, "title": "Martial III"},
    "martial/mart4.txt":                         {"fileid": 1303, "author": None, "title": "Martial IV"},
    "martial/mart5.txt":                         {"fileid": 1304, "author": None, "title": "Martial V"},
    "martial/mart6.txt":                         {"fileid": 1305, "author": None, "title": "Martial VI"},
    "martial/mart7.txt":                         {"fileid": 1306, "author": None, "title": "Martial VII"},
    "martial/mart8.txt":                         {"fileid": 1307, "author": None, "title": "Martial VIII"},
    "martial/mart9.txt":                         {"fileid": 1308, "author": None, "title": "Martial IX"},
    "martinbraga/capitula.txt":                  {
        "fileid": 1309, "author": "Martin of Braga", "title": "Capitula ex orientalium patrum synodis"
    }, "martinbraga/concilium1.txt":             {
        "fileid": 1310, "author": "Martin of Braga", "title": "Concilium Bracarense Primum"
    }, "martinbraga/concilium2.txt":             {
        "fileid": 1311, "author": "Martin of Braga", "title": "Concilium Bracarense Secundum"
    }, "martinbraga/exhortatio.txt":             {
        "fileid": 1312, "author": "Martin of Braga", "title": "Exhortatio Humilitatis"
    }, "martinbraga/formula.txt":                {
        "fileid": 1313, "author": "Martin of Braga", "title": "Formula Vitae Honestae"
    }, "martinbraga/ira.txt":                    {
        "fileid": 1314, "author": "Martin of Braga", "title": "de Trina Mersione"
    }, "martinbraga/pascha.txt":                 {"fileid": 1315, "author": "Martin of Braga", "title": "de Pascha"},
    "martinbraga/poems.txt":                     {"fileid": 1316, "author": "Martin of Braga", "title": "Versus"},
    "martinbraga/repellenda.txt":                {
        "fileid": 1317, "author": "Martin of Braga", "title": "pro Repellenda Iactantia"
    }, "martinbraga/rusticus.txt":               {
        "fileid": 1318, "author": "Martin of Braga", "title": "de Correctione Rusticorum"
    }, "martinbraga/sententiae.txt":             {
        "fileid": 1319, "author": "Martin of Braga", "title": "Sententiae Patrum Aegyptiorum"
    }, "martinbraga/superbia.txt":               {
        "fileid": 1320, "author": "Martin of Braga", "title": "Item de Superbia"
    }, "martinbraga/trina.txt":                  {
        "fileid": 1321, "author": "Martin of Braga", "title": "de Trina Mersione"
    }, "marullo.txt":                            {"fileid": 1322, "author": None, "title": "Michele Marullo"},
    "marx.txt":                                  {"fileid": 1323, "author": None, "title": "Karl Marx"},
    "maximianus.txt":                            {"fileid": 1324, "author": "Maximianus", "title": "Elegies"},
    "may/may1.txt":                              {"fileid": 1325, "author": "May", "title": "Liber I"},
    "may/may2.txt":                              {"fileid": 1326, "author": "May", "title": "Liber II"},
    "may/may3.txt":                              {"fileid": 1327, "author": "May", "title": "Liber III"},
    "may/may4.txt":                              {"fileid": 1328, "author": "May", "title": "Liber IV"},
    "may/may5.txt":                              {"fileid": 1329, "author": "May", "title": "Liber V"},
    "may/may6.txt":                              {"fileid": 1330, "author": "May", "title": "Liber VI"},
    "may/may7.txt":                              {"fileid": 1331, "author": "May", "title": "Liber VII"},
    "may/maytitle.txt":                          {"fileid": 1332, "author": "May", "title": "Title Page"},
    "melanchthon/conf.txt":                      {
        "fileid": 1333, "author": "Melanchthon", "title": "The Augsburg Confession"
    }, "melanchthon/hist.txt":                   {"fileid": 1334, "author": "Melanchthon", "title": "Life of Luther"},
    "melanchthon/laude.txt":                     {
        "fileid": 1335, "author": "Melanchthon", "title": "De Laude Vitae Scholasticae Oratio"
    }, "melanchthon/obitu.txt":                  {
        "fileid": 1336, "author": "Melanchthon", "title": "De Obitu Martini Lutheri"
    }, "milton.quintnov.txt":                    {
        "fileid": 1337, "author": "John Milton", "title": "In Quintum Novembris"
    }, "minucius.txt":                           {"fileid": 1338, "author": "M. Minucius Felix", "title": "Octavius"},
    "mirabilia.txt":                             {"fileid": 1339, "author": None, "title": "Mirabilia Urbis Romae"},
    "mirabilia1.txt":                            {
        "fileid": 1340, "author": "Gregorius", "title": "Narratio de Mirabilibus Urbis Romae"
    }, "mirandola/mir1.txt":                     {
        "fileid": 1341, "author": None, "title": "Carmina Ioannis Pici Mirandulae"
    }, "mirandola/mir2.txt":                     {
        "fileid": 1342, "author": None, "title": "Carmina Ioannis Pici Mirandulae"
    }, "mirandola/mir3.txt":                     {
        "fileid": 1343, "author": None, "title": "Carmina Ioannis Pici Mirandulae"
    }, "mirandola/mir4.txt":                     {
        "fileid": 1344, "author": None, "title": "Carmina Ioannis Pici Mirandulae"
    }, "mirandola/mir5.txt":                     {
        "fileid": 1345, "author": None, "title": "Carmina Ioannis Pici Mirandulae"
    }, "mirandola/mir6.txt":                     {
        "fileid": 1346, "author": None, "title": "Carmina Ioannis Pici Mirandulae"
    }, "mirandola/mir7.txt":                     {
        "fileid": 1347, "author": None, "title": "Carmina Ioannis Pici Mirandulae"
    }, "mirandola/mir8.txt":                     {
        "fileid": 1348, "author": None, "title": "Carmina Ioannis Pici Mirandulae"
    }, "mirandola/mir9.txt":                     {
        "fileid": 1349, "author": None, "title": "Carmina Ioannis Pici Mirandulae"
    }, "mirandola/oratio.txt":                   {
        "fileid": 1350, "author": "Pico della Mirandola", "title": "Oratio de hominis dignitate"
    }, "montanus.txt":                           {
        "fileid": 1351, "author": "Fabricius Montanus", "title": "De Wilhelmo Thellio elegia"
    }, "more.txt":                               {"fileid": 1352, "author": None, "title": "Thomas More"},
    "musavenit.txt":                             {"fileid": 1353, "author": None, "title": "Musa venit carmine "},
    "naevius.txt":                               {"fileid": 1354, "author": None, "title": "Naevius"},
    "navagero.txt":                              {"fileid": 1355, "author": None, "title": "Naugerius"},
    "nemesianus1.txt":                           {"fileid": 1356, "author": "Nemesianus", "title": "Ecloga I"},
    "nemesianus2.txt":                           {"fileid": 1357, "author": "Nemesianus", "title": "Ecloga II"},
    "nemesianus3.txt":                           {"fileid": 1358, "author": "Nemesianus", "title": "Ecloga III"},
    "nemesianus4.txt":                           {"fileid": 1359, "author": "Nemesianus", "title": "Ecloga IV"},
    "nepos/nepos.age.txt":                       {"fileid": 1360, "author": "Nepos", "title": "Life of Agesilaus"},
    "nepos/nepos.alc.txt":                       {"fileid": 1361, "author": "Nepos", "title": "Life of Alcibiades"},
    "nepos/nepos.aris.txt":                      {"fileid": 1362, "author": "Nepos", "title": "Life of Aristides"},
    "nepos/nepos.att.txt":                       {"fileid": 1363, "author": "Nepos", "title": "Life of Atticus"},
    "nepos/nepos.cat.txt":                       {"fileid": 1364, "author": "Nepos", "title": "Life of Cato"},
    "nepos/nepos.cha.txt":                       {"fileid": 1365, "author": "Nepos", "title": "Life of Chabrias"},
    "nepos/nepos.cim.txt":                       {"fileid": 1366, "author": "Nepos", "title": "Life of Cimon"},
    "nepos/nepos.con.txt":                       {"fileid": 1367, "author": "Nepos", "title": "Life of Conon"},
    "nepos/nepos.dat.txt":                       {"fileid": 1368, "author": "Nepos", "title": "Life of Datames"},
    "nepos/nepos.dion.txt":                      {"fileid": 1369, "author": "Nepos", "title": "Life of Dion"},
    "nepos/nepos.epam.txt":                      {"fileid": 1370, "author": "Nepos", "title": "Life of Epaminondas"},
    "nepos/nepos.eum.txt":                       {"fileid": 1371, "author": "Nepos", "title": "Life of Eumenes"},
    "nepos/nepos.fragmenta.txt":                 {"fileid": 1372, "author": "Nepos", "title": "Fragments"},
    "nepos/nepos.ham.txt":                       {"fileid": 1373, "author": "Nepos", "title": "Life of Hamilcar"},
    "nepos/nepos.han.txt":                       {"fileid": 1374, "author": "Nepos", "title": "Life of Hannibal"},
    "nepos/nepos.iph.txt":                       {"fileid": 1375, "author": "Nepos", "title": "Life of Iphicrates"},
    "nepos/nepos.kings.txt":                     {"fileid": 1376, "author": "Nepos", "title": "On Kings"},
    "nepos/nepos.lys.txt":                       {"fileid": 1377, "author": "Nepos", "title": "Life of Lysander"},
    "nepos/nepos.mil.txt":                       {"fileid": 1378, "author": "Nepos", "title": "Life of Miltiades"},
    "nepos/nepos.paus.txt":                      {"fileid": 1379, "author": "Nepos", "title": "Life of Pausanias"},
    "nepos/nepos.pel.txt":                       {"fileid": 1380, "author": "Nepos", "title": "Life of Pelopidas"},
    "nepos/nepos.phoc.txt":                      {"fileid": 1381, "author": "Nepos", "title": "Life of Phocion"},
    "nepos/nepos.pr.txt":                        {"fileid": 1382, "author": "Nepos", "title": "Praefatio"},
    "nepos/nepos.them.txt":                      {"fileid": 1383, "author": "Nepos", "title": "Life of Themistocles"},
    "nepos/nepos.thras.txt":                     {"fileid": 1384, "author": "Nepos", "title": "Life of Thrasybulus"},
    "nepos/nepos.tim.txt":                       {"fileid": 1385, "author": "Nepos", "title": "Life of Timoleon"},
    "nepos/nepos.timo.txt":                      {"fileid": 1386, "author": "Nepos", "title": "Life of Timotheus"},
    "newton.capita.txt":                         {
        "fileid": 1387, "author": "Newton", "title": "Index Capitum from the Principia "
    }, "newton.leges.txt":                       {
        "fileid": 1388, "author": "Newton", "title": "Leges Motus from the Principia "
    }, "newton.regulae.txt":                     {
        "fileid": 1389, "author": "Newton", "title": "Regulae Philosophandi from the Principia "
    }, "newton.scholium.txt":                    {
        "fileid": 1390, "author": "Newton", "title": "Scholium Generale from the Principia "
    }, "nithardus1.txt":                         {"fileid": 1391, "author": "Nithardus", "title": "Historiae I "},
    "nithardus2.txt":                            {"fileid": 1392, "author": "Nithardus", "title": "Historiae II "},
    "nithardus3.txt":                            {"fileid": 1393, "author": "Nithardus", "title": "Historiae III "},
    "nithardus4.txt":                            {"fileid": 1394, "author": "Nithardus", "title": "Historiae IV "},
    "nivis.txt":                                 {"fileid": 1395, "author": None, "title": ""},
    "nobilis.txt":                               {"fileid": 1396, "author": "Nobilis", "title": "me "},
    "notitia1.txt":                              {"fileid": 1397, "author": None, "title": "Notitia Dignitatum"},
    "notitia2.txt":                              {"fileid": 1398, "author": None, "title": "Notitia Dignitatum"},
    "novatian.txt":                              {"fileid": 1399, "author": None, "title": "Novatian"},
    "obsequens.txt":                             {"fileid": 1400, "author": None, "title": "Julius Obsequens"},
    "omnegenus.txt":                             {"fileid": 1401, "author": None, "title": "Omne genus demoniorum "},
    "oratio.stephani.txt":                       {"fileid": 1402, "author": None, "title": "Oratio Stephani de Varda"},
    "oresmius.txt":                              {"fileid": 1403, "author": None, "title": "Oresimius"}, "origo.txt": {
        "fileid": 1404, "author": None, "title": "Origo gentis Langobardorum"
    }, "orosius/orosius1.txt":                   {"fileid": 1405, "author": None, "title": "Orosius I"},
    "orosius/orosius2.txt":                      {"fileid": 1406, "author": None, "title": "Orosius II"},
    "orosius/orosius3.txt":                      {"fileid": 1407, "author": None, "title": "Orosius III"},
    "orosius/orosius4.txt":                      {"fileid": 1408, "author": None, "title": "Orosius IV"},
    "orosius/orosius5.txt":                      {"fileid": 1409, "author": None, "title": "Orosius V"},
    "orosius/orosius6.txt":                      {"fileid": 1410, "author": None, "title": "Orosius VI"},
    "orosius/orosius7.txt":                      {"fileid": 1411, "author": None, "title": "Orosius VII"},
    "ottofreising/1.txt":                        {"fileid": 1412, "author": "Otto of Freising", "title": "Liber I"},
    "ottofreising/2.txt":                        {"fileid": 1413, "author": "Otto of Freising", "title": "Liber II"},
    "ottofreising/3.txt":                        {"fileid": 1414, "author": "Otto of Freising", "title": "Liber III"},
    "ottofreising/4.txt":                        {"fileid": 1415, "author": "Otto of Freising", "title": "Liber IV"},
    "ottofreising/epistola.txt":                 {"fileid": 1416, "author": "Otto of Freising", "title": "Epistola"},
    "ovid/ovid.amor1.txt":                       {"fileid": 1417, "author": "Ovid", "title": "Amores I"},
    "ovid/ovid.amor2.txt":                       {"fileid": 1418, "author": "Ovid", "title": "Amores II"},
    "ovid/ovid.amor3.txt":                       {"fileid": 1419, "author": "Ovid", "title": "Amores III"},
    "ovid/ovid.artis1.txt":                      {"fileid": 1420, "author": "Ovid", "title": "Ars Amatoria I"},
    "ovid/ovid.artis2.txt":                      {"fileid": 1421, "author": "Ovid", "title": "Ars Amatoria II"},
    "ovid/ovid.artis3.txt":                      {"fileid": 1422, "author": "Ovid", "title": "Ars Amatoria III"},
    "ovid/ovid.fasti1.txt":                      {"fileid": 1423, "author": "Ovid", "title": "Fasti I"},
    "ovid/ovid.fasti2.txt":                      {"fileid": 1424, "author": "Ovid", "title": "Fasti II"},
    "ovid/ovid.fasti3.txt":                      {"fileid": 1425, "author": "Ovid", "title": "Fasti III"},
    "ovid/ovid.fasti4.txt":                      {"fileid": 1426, "author": "Ovid", "title": "Fasti IV"},
    "ovid/ovid.fasti5.txt":                      {"fileid": 1427, "author": "Ovid", "title": "Fasti V"},
    "ovid/ovid.fasti6.txt":                      {"fileid": 1428, "author": "Ovid", "title": "Fasti VI"},
    "ovid/ovid.her1.txt":                        {"fileid": 1429, "author": "Ovid", "title": "Heroides I"},
    "ovid/ovid.her10.txt":                       {"fileid": 1430, "author": "Ovid", "title": "Heroides X"},
    "ovid/ovid.her11.txt":                       {"fileid": 1431, "author": "Ovid", "title": "Heroides XI"},
    "ovid/ovid.her12.txt":                       {"fileid": 1432, "author": "Ovid", "title": "Heroides XII"},
    "ovid/ovid.her13.txt":                       {"fileid": 1433, "author": "Ovid", "title": "Heroides XIII"},
    "ovid/ovid.her14.txt":                       {"fileid": 1434, "author": "Ovid", "title": "Heroides XIV"},
    "ovid/ovid.her15.txt":                       {"fileid": 1435, "author": "Ovid", "title": "Heroides XV"},
    "ovid/ovid.her16.txt":                       {"fileid": 1436, "author": "Ovid", "title": "Heroides XVI"},
    "ovid/ovid.her17.txt":                       {"fileid": 1437, "author": "Ovid", "title": "Heroides XVII"},
    "ovid/ovid.her18.txt":                       {"fileid": 1438, "author": "Ovid", "title": "Heroides XVIII"},
    "ovid/ovid.her19.txt":                       {"fileid": 1439, "author": "Ovid", "title": "Heroides XIX"},
    "ovid/ovid.her2.txt":                        {"fileid": 1440, "author": "Ovid", "title": "Heroides II"},
    "ovid/ovid.her20.txt":                       {"fileid": 1441, "author": "Ovid", "title": "Heroides XX"},
    "ovid/ovid.her21.txt":                       {"fileid": 1442, "author": "Ovid", "title": "Heroides XXI"},
    "ovid/ovid.her3.txt":                        {"fileid": 1443, "author": "Ovid", "title": "Heroides III"},
    "ovid/ovid.her4.txt":                        {"fileid": 1444, "author": "Ovid", "title": "Heroides IV"},
    "ovid/ovid.her5.txt":                        {"fileid": 1445, "author": "Ovid", "title": "Heroides V"},
    "ovid/ovid.her6.txt":                        {"fileid": 1446, "author": "Ovid", "title": "Heroides VI"},
    "ovid/ovid.her7.txt":                        {"fileid": 1447, "author": "Ovid", "title": "Heroides VII"},
    "ovid/ovid.her8.txt":                        {"fileid": 1448, "author": "Ovid", "title": "Heroides VIII"},
    "ovid/ovid.her9.txt":                        {"fileid": 1449, "author": "Ovid", "title": "Heroides IX"},
    "ovid/ovid.ibis.txt":                        {"fileid": 1450, "author": "Ovid", "title": "Ibis"},
    "ovid/ovid.met1.txt":                        {"fileid": 1451, "author": "Ovid", "title": "Metamorphoses I"},
    "ovid/ovid.met10.txt":                       {"fileid": 1452, "author": "Ovid", "title": "Metamorphoses X"},
    "ovid/ovid.met11.txt":                       {"fileid": 1453, "author": "Ovid", "title": "Metamorphoses XI"},
    "ovid/ovid.met12.txt":                       {"fileid": 1454, "author": "Ovid", "title": "Metamorphoses XII"},
    "ovid/ovid.met13.txt":                       {"fileid": 1455, "author": "Ovid", "title": "Metamorphoses XIII"},
    "ovid/ovid.met14.txt":                       {"fileid": 1456, "author": "Ovid", "title": "Metamorphoses XIV"},
    "ovid/ovid.met15.txt":                       {"fileid": 1457, "author": "Ovid", "title": "Metamorphoses XV"},
    "ovid/ovid.met2.txt":                        {"fileid": 1458, "author": "Ovid", "title": "Metamorphoses II"},
    "ovid/ovid.met3.txt":                        {"fileid": 1459, "author": "Ovid", "title": "Metamorphoses III"},
    "ovid/ovid.met4.txt":                        {"fileid": 1460, "author": "Ovid", "title": "Metamorphoses IV"},
    "ovid/ovid.met5.txt":                        {"fileid": 1461, "author": "Ovid", "title": "Metamorphoses V"},
    "ovid/ovid.met6.txt":                        {"fileid": 1462, "author": "Ovid", "title": "Metamorphoses VI"},
    "ovid/ovid.met7.txt":                        {"fileid": 1463, "author": "Ovid", "title": "Metamorphoses VII"},
    "ovid/ovid.met8.txt":                        {"fileid": 1464, "author": "Ovid", "title": "Metamorphoses VIII"},
    "ovid/ovid.met9.txt":                        {"fileid": 1465, "author": "Ovid", "title": "Metamorphoses IX"},
    "ovid/ovid.ponto1.txt":                      {"fileid": 1466, "author": "Ovid", "title": "Ex Ponto I"},
    "ovid/ovid.ponto2.txt":                      {"fileid": 1467, "author": "Ovid", "title": "Ex Ponto II"},
    "ovid/ovid.ponto3.txt":                      {"fileid": 1468, "author": "Ovid", "title": "Ex Ponto III"},
    "ovid/ovid.ponto4.txt":                      {"fileid": 1469, "author": "Ovid", "title": "Ex Ponto IV"},
    "ovid/ovid.rem.txt":                         {"fileid": 1470, "author": "Ovid", "title": "Remedia Amoris"},
    "ovid/ovid.tristia1.txt":                    {"fileid": 1471, "author": "Ovid", "title": "Tristia I"},
    "ovid/ovid.tristia2.txt":                    {"fileid": 1472, "author": "Ovid", "title": "Tristia II"},
    "ovid/ovid.tristia3.txt":                    {"fileid": 1473, "author": "Ovid", "title": "Ovid: Tristia III"},
    "ovid/ovid.tristia4.txt":                    {"fileid": 1474, "author": "Ovid", "title": "Ovid: Tristia IV"},
    "ovid/ovid.tristia5.txt":                    {"fileid": 1475, "author": "Ovid", "title": "Ovid: Tristia V"},
    "owen.txt":                                  {"fileid": 1476, "author": None, "title": "John Owen "}, "paris.txt": {
        "fileid": 1477, "author": "Julius Paris", "title": "de Nominibus Epitome"
    }, "pascoli.catull.txt":                     {"fileid": 1478, "author": None, "title": "Catullocalvos-Satura "},
    "pascoli.iug.txt":                           {"fileid": 1479, "author": None, "title": "Iugurtha "},
    "pascoli.laur.txt":                          {"fileid": 1480, "author": None, "title": "Laureolo "},
    "pascoli.sen.txt":                           {"fileid": 1481, "author": None, "title": "Senex Corycius "},
    "pascoli.veianius.txt":                      {"fileid": 1482, "author": None, "title": "Veianius "},
    "passerat.txt":                              {"fileid": 1483, "author": None, "title": "Jean Passerat"},
    "patricius1.txt":                            {
        "fileid": 1484, "author": "Franciscus Patricius", "title": "Panaugiae I "
    }, "patricius2.txt":                         {
        "fileid": 1485, "author": "Franciscus Patricius", "title": "Panaugiae II "
    }, "pauldeacon/carmina.txt":                 {"fileid": 1486, "author": "Paulus Diaconus", "title": "Carmina"},
    "pauldeacon/fabulae.txt":                    {"fileid": 1487, "author": "Paulus Diaconus", "title": "Fabulae"},
    "pauldeacon/hist1.txt":                      {
        "fileid": 1488, "author": "Paulus Diaconus", "title": "Historia Langobardorum Liber I"
    }, "pauldeacon/hist2.txt":                   {
        "fileid": 1489, "author": "Paulus Diaconus", "title": "Historia Langobardorum Liber II"
    }, "pauldeacon/hist3.txt":                   {
        "fileid": 1490, "author": "Paulus Diaconus", "title": "Historia Langobardorum Liber III"
    }, "pauldeacon/hist4.txt":                   {
        "fileid": 1491, "author": "Paulus Diaconus", "title": "Historia Langobardorum Liber IV"
    }, "pauldeacon/hist5.txt":                   {
        "fileid": 1492, "author": "Paulus Diaconus", "title": "Historia Langobardorum Liber V"
    }, "pauldeacon/hist6.txt":                   {
        "fileid": 1493, "author": "Paulus Diaconus", "title": "Historia Langobardorum Liber VI"
    }, "pauldeacon/histrom1.txt":                {
        "fileid": 1494, "author": "Paulus Diaconus", "title": "Historia Romana Liber I"
    }, "pauldeacon/histrom10.txt":               {
        "fileid": 1495, "author": "Paulus Diaconus", "title": "Historia Romana Liber X"
    }, "pauldeacon/histrom11.txt":               {
        "fileid": 1496, "author": "Paulus Diaconus", "title": "Historia Romana Liber XI"
    }, "pauldeacon/histrom12.txt":               {
        "fileid": 1497, "author": "Paulus Diaconus", "title": "Historia Romana Liber XII"
    }, "pauldeacon/histrom13.txt":               {
        "fileid": 1498, "author": "Paulus Diaconus", "title": "Historia Romana Liber XIII"
    }, "pauldeacon/histrom14.txt":               {
        "fileid": 1499, "author": "Paulus Diaconus", "title": "Historia Romana Liber XIV"
    }, "pauldeacon/histrom15.txt":               {
        "fileid": 1500, "author": "Paulus Diaconus", "title": "Historia Romana Liber XV"
    }, "pauldeacon/histrom16.txt":               {
        "fileid": 1501, "author": "Paulus Diaconus", "title": "Historia Romana Liber XVI"
    }, "pauldeacon/histrom2.txt":                {
        "fileid": 1502, "author": "Paulus Diaconus", "title": "Historia Romana Liber II"
    }, "pauldeacon/histrom3.txt":                {
        "fileid": 1503, "author": "Paulus Diaconus", "title": "Historia Romana Liber III"
    }, "pauldeacon/histrom4.txt":                {
        "fileid": 1504, "author": "Paulus Diaconus", "title": "Historia Romana Liber IV"
    }, "pauldeacon/histrom5.txt":                {
        "fileid": 1505, "author": "Paulus Diaconus", "title": "Historia Romana Liber II"
    }, "pauldeacon/histrom6.txt":                {
        "fileid": 1506, "author": "Paulus Diaconus", "title": "Historia Romana Liber VI"
    }, "pauldeacon/histrom7.txt":                {
        "fileid": 1507, "author": "Paulus Diaconus", "title": "Historia Romana Liber VII"
    }, "pauldeacon/histrom8.txt":                {
        "fileid": 1508, "author": "Paulus Diaconus", "title": "Historia Romana Liber VIII"
    }, "pauldeacon/histrom9.txt":                {
        "fileid": 1509, "author": "Paulus Diaconus", "title": "Historia Romana Liber IX"
    }, "paulinus.ausonium.txt":                  {"fileid": 1510, "author": None, "title": "O Comes "},
    "paulinus.poemata.txt":                      {"fileid": 1511, "author": "Paulinus of Nola", "title": "Poems"},
    "perp.txt":                                  {"fileid": 1512, "author": None, "title": "Perpetua et Felicitatis"},
    "persius.txt":                               {"fileid": 1513, "author": None, "title": "Persius"},
    "pervig.txt":                                {"fileid": 1514, "author": None, "title": "Pervigilium Veneris"},
    "petrarch.ep1.txt":                          {
        "fileid": 1515, "author": "Petrarch", "title": "Epistula M. Tullio Ciceroni"
    }, "petrarch.numa.txt":                      {"fileid": 1516, "author": "Petrarch", "title": "Numa Pompilius"},
    "petrarch.rom.txt":                          {"fileid": 1517, "author": "Petrarch", "title": "Romulus"},
    "petrarchmedicus.txt":                       {
        "fileid": 1518, "author": "Petrarca", "title": "Contra Medicum Quendam"
    }, "petronius1.txt":                         {"fileid": 1519, "author": "Petronius", "title": "Satiricon"},
    "petroniusfrag.txt":                         {"fileid": 1520, "author": None, "title": "Fragmenta Petroniana"},
    "phaedr1.txt":                               {"fileid": 1521, "author": None, "title": "Phaedrus I"},
    "phaedr2.txt":                               {"fileid": 1522, "author": None, "title": "Phaedrus II"},
    "phaedr3.txt":                               {"fileid": 1523, "author": None, "title": "Phaedrus III"},
    "phaedr4.txt":                               {"fileid": 1524, "author": None, "title": "Phaedrus IV"},
    "phaedr5.txt":                               {"fileid": 1525, "author": None, "title": "Phaedrus V"},
    "phaedrapp.txt":                             {"fileid": 1526, "author": None, "title": "Phaedrus Appendix"},
    "piccolomini.carmen.txt":                    {
        "fileid": 1527, "author": "Enea Silvio Piccolomini (1405-1464", "title": "Pope Pius II from 1458) "
    }, "piccolomini.ep1.txt":                    {
        "fileid": 1528, "author": "Piccolomini", "title": "Letter to Johann Lauterbach "
    }, "piccolomini.ep2.txt":                    {
        "fileid": 1529, "author": "Piccolomini", "title": "Letter to His Father "
    }, "piccolomini.ep3.txt":                    {
        "fileid": 1530, "author": "Piccolomini", "title": "Letter to Wilhelm von Stein "
    }, "piccolomini.ep4.txt":                    {
        "fileid": 1531, "author": "Piccolomini", "title": "Letter to Procop van Rabenstein "
    }, "piccolomini.ep5.txt":                    {
        "fileid": 1532, "author": "Piccolomini", "title": "Letter to Prince Sigismund "
    }, "piccolomini.ep6.txt":                    {
        "fileid": 1533, "author": "Piccolomini", "title": "Letter to Caspar Schlick "
    }, "piccolomini.turcos.txt":                 {
        "fileid": 1534, "author": "Piccolomini", "title": "Oratio contra Turcos "
    }, "planctus.txt":                           {"fileid": 1535, "author": None, "title": "Anonymous"},
    "plautus/amphitruo.txt":                     {"fileid": 1536, "author": "Plautus", "title": "Amphitruo"},
    "plautus/asinaria.txt":                      {"fileid": 1537, "author": "Plautus", "title": "Asinaria"},
    "plautus/aulularia.txt":                     {"fileid": 1538, "author": "Plautus", "title": "Aulularia"},
    "plautus/bacchides.txt":                     {"fileid": 1539, "author": "Plautus", "title": "Bacchides"},
    "plautus/captivi.txt":                       {"fileid": 1540, "author": "Plautus", "title": "Captivi"},
    "plautus/cas.txt":                           {"fileid": 1541, "author": "Plautus", "title": "Casina"},
    "plautus/cistellaria.txt":                   {"fileid": 1542, "author": "Plautus", "title": "Cistellaria"},
    "plautus/curculio.txt":                      {"fileid": 1543, "author": "Plautus", "title": "Curculio"},
    "plautus/epidicus.txt":                      {"fileid": 1544, "author": "Plautus", "title": "Epidicus"},
    "plautus/menaechmi.txt":                     {"fileid": 1545, "author": "Plautus", "title": "Menaechmi"},
    "plautus/mercator.txt":                      {"fileid": 1546, "author": "Plautus", "title": "Mercator"},
    "plautus/miles.txt":                         {"fileid": 1547, "author": "Plautus", "title": "Miles Gloriosus"},
    "plautus/mostellaria.txt":                   {"fileid": 1548, "author": "Plautus", "title": "Mostellaria"},
    "plautus/persa.txt":                         {"fileid": 1549, "author": "Plautus", "title": "Persa"},
    "plautus/poenulus.txt":                      {"fileid": 1550, "author": "Plautus", "title": "Poenulus"},
    "plautus/pseudolus.txt":                     {"fileid": 1551, "author": "Plautus", "title": "Pseudolus"},
    "plautus/rudens.txt":                        {"fileid": 1552, "author": "Plautus", "title": "Rudens"},
    "plautus/stichus.txt":                       {"fileid": 1553, "author": "Plautus", "title": "Stichus"},
    "plautus/trinummus.txt":                     {"fileid": 1554, "author": "Plautus", "title": "Trinummus"},
    "plautus/truculentus.txt":                   {"fileid": 1555, "author": "Plautus", "title": "Truculentus"},
    "plautus/vidularia.txt":                     {"fileid": 1556, "author": "Plautus", "title": "Vidularia"},
    "pliny.ep1.txt":                             {"fileid": 1557, "author": None, "title": "Pliny the Younger"},
    "pliny.ep10.txt":                            {"fileid": 1558, "author": None, "title": "Pliny the Younger"},
    "pliny.ep2.txt":                             {"fileid": 1559, "author": None, "title": "Pliny the Younger"},
    "pliny.ep3.txt":                             {"fileid": 1560, "author": None, "title": "Pliny the Younger"},
    "pliny.ep4.txt":                             {"fileid": 1561, "author": None, "title": "Pliny the Younger"},
    "pliny.ep5.txt":                             {"fileid": 1562, "author": None, "title": "Pliny the Younger"},
    "pliny.ep6.txt":                             {"fileid": 1563, "author": None, "title": "Pliny the Younger"},
    "pliny.ep7.txt":                             {"fileid": 1564, "author": None, "title": "Pliny the Younger"},
    "pliny.ep8.txt":                             {"fileid": 1565, "author": None, "title": "Pliny the Younger"},
    "pliny.ep9.txt":                             {"fileid": 1566, "author": None, "title": "Pliny the Younger"},
    "pliny.nh1.txt":                             {
        "fileid": 1567, "author": "Pliny the Elder", "title": "Natural History, Book I"
    }, "pliny.nh2.txt":                          {"fileid": 1568, "author": None, "title": "Pliny the Elder"},
    "pliny.nh3.txt":                             {
        "fileid": 1569, "author": "Pliny the Elder", "title": "Natural History, Book III"
    }, "pliny.nh4.txt":                          {
        "fileid": 1570, "author": "Pliny the Elder", "title": "Natural History, Book IV"
    }, "pliny.nh5.txt":                          {
        "fileid": 1571, "author": "Pliny the Elder", "title": "Natural History, Book V"
    }, "pliny.nhpr.txt":                         {
        "fileid": 1572, "author": "Pliny the Elder", "title": "Natural History, Preface"
    }, "pliny.panegyricus.txt":                  {"fileid": 1573, "author": None, "title": "Pliny the Younger"},
    "poggio.txt":                                {"fileid": 1574, "author": None, "title": "Poggii Facetiae (1-120)"},
    "pomponius1.txt":                            {
        "fileid": 1575, "author": "Pomponius Mela", "title": "de Chorographia I "
    }, "pomponius2.txt":                         {
        "fileid": 1576, "author": "Pomponius Mela", "title": "de Chorographia II"
    }, "pomponius3.txt":                         {
        "fileid": 1577, "author": "Pomponius Mela", "title": "de Chorographia III"
    }, "pontano.txt":                            {
        "fileid": 1578, "author": None, "title": "Giovanni Pontano (1429-1503)"
    }, "poree.txt":                              {"fileid": 1579, "author": "Charles Poree", "title": "Caecus Amor "},
    "porphyrius.txt":                            {"fileid": 1580, "author": "Porphyrius", "title": "Carmina"},
    "potatores.txt":                             {"fileid": 1581, "author": None, "title": "Potatores exquisiti"},
    "prataiam.txt":                              {"fileid": 1582, "author": None, "title": "Prata iam rident omnia "},
    "prec.terr.txt":                             {"fileid": 1583, "author": None, "title": "Precatio Terrae"},
    "precatio.txt":                              {"fileid": 1584, "author": None, "title": "Precatio Omnium Herbarum "},
    "priapea.txt":                               {"fileid": 1585, "author": None, "title": "Priapea"},
    "professio.txt":                             {
        "fileid": 1586, "author": None, "title": "Professio contra Sectam Priscilliani"
    }, "prop2.txt":                              {"fileid": 1587, "author": None, "title": "Propertius Book II"},
    "prop3.txt":                                 {"fileid": 1588, "author": None, "title": "Propertius Book III"},
    "prop4.txt":                                 {
        "fileid": 1589, "author": None, "title": "SEXTI PROPERTI ELEGIARVM LIBER QVARTVS"
    }, "propertius1.txt":                        {
        "fileid": 1590, "author": None, "title": "SEXTI PROPERTI ELEGIARVM LIBER PRIMVS"
    }, "prosperus.epistola.txt":                 {
        "fileid": 1591, "author": "St. Prosperus of Aquitaine", "title": "Epistola ad Augustinum"
    }, "prosperus.rufinum.txt":                  {
        "fileid": 1592, "author": "St. Prosperus of Aquitaine", "title": "Epistola ad Rufinum"
    }, "prosperus.sententiae.txt":               {
        "fileid": 1593, "author": "St. Prosperus of Aquitaine", "title": "Liber Sententiarum"
    }, "protospatarius.txt":                     {
        "fileid": 1594, "author": "Protospatariu", "title": "Breve Chronicon"
    }, "prudentius/prud.psycho.txt":             {"fileid": 1595, "author": "Prudentius", "title": "Psychomachia"},
    "prudentius/prud1.txt":                      {"fileid": 1596, "author": None, "title": "Prudentius I"},
    "prudentius/prud10.txt":                     {"fileid": 1597, "author": None, "title": "Prudentius X"},
    "prudentius/prud11.txt":                     {"fileid": 1598, "author": None, "title": "Prudentius XI"},
    "prudentius/prud12.txt":                     {"fileid": 1599, "author": None, "title": "Prudentius XII"},
    "prudentius/prud13.txt":                     {"fileid": 1600, "author": None, "title": "Prudentius XIII"},
    "prudentius/prud14.txt":                     {"fileid": 1601, "author": None, "title": "Prudentius XIV"},
    "prudentius/prud2.txt":                      {"fileid": 1602, "author": None, "title": "Prudentius II"},
    "prudentius/prud3.txt":                      {"fileid": 1603, "author": None, "title": "Prudentius III"},
    "prudentius/prud4.txt":                      {"fileid": 1604, "author": None, "title": "Prudentius IIII"},
    "prudentius/prud5.txt":                      {"fileid": 1605, "author": None, "title": "Prudentius V"},
    "prudentius/prud6.txt":                      {"fileid": 1606, "author": None, "title": "Prudentius VI"},
    "prudentius/prud7.txt":                      {"fileid": 1607, "author": None, "title": "Prudentius VII"},
    "prudentius/prud8.txt":                      {"fileid": 1608, "author": None, "title": "Prudentius VIII"},
    "prudentius/prud9.txt":                      {"fileid": 1609, "author": None, "title": "Prudentius IX"},
    "psplato.amatores.txt":                      {
        "fileid": 1610, "author": None, "title": "Pseudo-Plato - De Virtute "
    }, "psplato.demodocus.txt":                  {"fileid": 1611, "author": "Pseudo-Plato", "title": "Demodocus "},
    "psplato.eryxias.txt":                       {"fileid": 1612, "author": None, "title": "Pseudo-Plato - Eryxias "},
    "psplato.halcyon.txt":                       {
        "fileid": 1613, "author": "Pseudo-Plato/Pseudo-Lucian", "title": "Halcyon "
    }, "psplato.iusto.txt":                      {"fileid": 1614, "author": None, "title": "Pseudo-Plato - De Iusto "},
    "psplato.minos.txt":                         {"fileid": 1615, "author": "Pseudo-Plato", "title": "Minos "},
    "psplato.sisyphus.txt":                      {"fileid": 1616, "author": None, "title": "Pseudo-Plato - Sisyphus "},
    "psplato.virtu.txt":                         {
        "fileid": 1617, "author": None, "title": "Pseudo-Plato - De Virtute "
    }, "pulchracomis.txt":                       {"fileid": 1618, "author": None, "title": "Pulchra comis "},
    "quintilian/quintilian.decl.mai1.txt":       {
        "fileid": 1619, "author": "Quintilian", "title": "Declamatio Maior I"
    }, "quintilian/quintilian.decl.mai10.txt":   {
        "fileid": 1620, "author": "Quintilian", "title": "Declamatio Maior X"
    }, "quintilian/quintilian.decl.mai11.txt":   {
        "fileid": 1621, "author": "Quintilian", "title": "Declamatio Maior XI"
    }, "quintilian/quintilian.decl.mai12.txt":   {
        "fileid": 1622, "author": "Quintilian", "title": "Declamatio Maior XII"
    }, "quintilian/quintilian.decl.mai13.txt":   {
        "fileid": 1623, "author": "Quintilian", "title": "Declamatio Maior XIII"
    }, "quintilian/quintilian.decl.mai14.txt":   {
        "fileid": 1624, "author": "Quintilian", "title": "Declamatio Maior XIV"
    }, "quintilian/quintilian.decl.mai15.txt":   {
        "fileid": 1625, "author": "Quintilian", "title": "Declamatio Maior XV"
    }, "quintilian/quintilian.decl.mai16.txt":   {
        "fileid": 1626, "author": "Quintilian", "title": "Declamatio Maior XVI"
    }, "quintilian/quintilian.decl.mai17.txt":   {
        "fileid": 1627, "author": "Quintilian", "title": "Declamatio Maior XVII"
    }, "quintilian/quintilian.decl.mai18.txt":   {
        "fileid": 1628, "author": "Quintilian", "title": "Declamatio Maior XVIII"
    }, "quintilian/quintilian.decl.mai19.txt":   {
        "fileid": 1629, "author": "Quintilian", "title": "Declamatio Maior I"
    }, "quintilian/quintilian.decl.mai2.txt":    {
        "fileid": 1630, "author": "Quintilian", "title": "Declamatio Maior II"
    }, "quintilian/quintilian.decl.mai4.txt":    {
        "fileid": 1631, "author": "Quintilian", "title": "Declamatio Maior IV"
    }, "quintilian/quintilian.decl.mai5.txt":    {
        "fileid": 1632, "author": "Quintilian", "title": "Declamatio Maior V"
    }, "quintilian/quintilian.decl.mai6.txt":    {
        "fileid": 1633, "author": "Quintilian", "title": "Declamatio Maior VI"
    }, "quintilian/quintilian.decl.mai7.txt":    {
        "fileid": 1634, "author": "Quintilian", "title": "Declamatio Maior VII"
    }, "quintilian/quintilian.decl.mai8.txt":    {
        "fileid": 1635, "author": "Quintilian", "title": "Declamatio Maior VIII"
    }, "quintilian/quintilian.decl.mai9.txt":    {
        "fileid": 1636, "author": "Quintilian", "title": "Declamatio Maior IX"
    }, "quintilian/quintilian.institutio1.txt":  {
        "fileid": 1637, "author": "Quintilian", "title": "Institutio Oratoria I"
    }, "quintilian/quintilian.institutio10.txt": {
        "fileid": 1638, "author": "Quintilian", "title": "Institutio Oratoria X"
    }, "quintilian/quintilian.institutio11.txt": {
        "fileid": 1639, "author": "Quintilian", "title": "Institutio Oratoria XI"
    }, "quintilian/quintilian.institutio12.txt": {
        "fileid": 1640, "author": "Quintilian", "title": "Institutio Oratoria XII"
    }, "quintilian/quintilian.institutio2.txt":  {
        "fileid": 1641, "author": "Quintilian", "title": "Institutio Oratoria II"
    }, "quintilian/quintilian.institutio3.txt":  {
        "fileid": 1642, "author": "Quintilian", "title": "Institutio Oratoria III"
    }, "quintilian/quintilian.institutio4.txt":  {
        "fileid": 1643, "author": "Quintilian", "title": "Institutio Oratoria IV"
    }, "quintilian/quintilian.institutio5.txt":  {
        "fileid": 1644, "author": "Quintilian", "title": "Institutio Oratoria V"
    }, "quintilian/quintilian.institutio6.txt":  {
        "fileid": 1645, "author": "Quintilian", "title": "Institutio Oratoria VI"
    }, "quintilian/quintilian.institutio7.txt":  {
        "fileid": 1646, "author": "Quintilian", "title": "Institutio Oratoria VII"
    }, "quintilian/quintilian.institutio8.txt":  {
        "fileid": 1647, "author": "Quintilian", "title": "Institutio Oratoria VIII"
    }, "quintilian/quintilian.institutio9.txt":  {
        "fileid": 1648, "author": "Quintilian", "title": "Institutio Oratoria IX"
    }, "quum.txt":                               {"fileid": 1649, "author": None, "title": "Quum inter nonNoneos "},
    "raoul.txt":                                 {
        "fileid": 1650, "author": "Raoul of Caen", "title": "Gesta Tancredi in expeditione Hierosolymitana"
    }, "regula.txt":                             {"fileid": 1651, "author": None, "title": "Regula ad Monachos"},
    "reposianus.txt":                            {
        "fileid": 1652, "author": "Reposianus", "title": "De concubitu Martis et Veneris "
    }, "resgestae.txt":                          {"fileid": 1653, "author": "AUGUSTUS", "title": "RES GESTAE I"},
    "resgestae1.txt":                            {"fileid": 1654, "author": "AUGUSTUS", "title": "RES GESTAE"},
    "rhetores.txt":                              {
        "fileid": 1655, "author": None, "title": "EDICTUM ADVERSUS LATINOS RHETORES"
    }, "richerus1.txt":                          {"fileid": 1656, "author": "Richerus", "title": "Liber I"},
    "richerus2.txt":                             {"fileid": 1657, "author": "Richerus", "title": "Liber II"},
    "richerus3.txt":                             {"fileid": 1658, "author": "Richerus", "title": "Liber III"},
    "richerus4.txt":                             {"fileid": 1659, "author": "Richerus", "title": "Liber IV"},
    "rimbaud.txt":                               {"fileid": 1660, "author": None, "title": "Arthur Rimbaud"},
    "ruaeus.txt":                                {
        "fileid": 1661, "author": None, "title": "Ruaeus' Prose Summary of Virgil's Aeneid"
    }, "rumor.txt":                              {"fileid": 1662, "author": None, "title": ""}, "rutilius.txt": {
        "fileid": 1663, "author": "Rutilius Namatianus", "title": "De Reditu Suo"
    }, "rutiliuslupus.txt":                      {
        "fileid": 1664, "author": "P. Rutilius Lupus", "title": "de Figuris Sententiarum et Elocutionis"
    }, "sabinus1.txt":                           {"fileid": 1665, "author": None, "title": "Sabinus"},
    "sabinus2.txt":                              {"fileid": 1666, "author": None, "title": "Sabinus"},
    "sabinus3.txt":                              {"fileid": 1667, "author": None, "title": "Sabinus"},
    "sall.1.txt":                                {"fileid": 1668, "author": "Sallust", "title": "Bellum Catilinae"},
    "sall.2.txt":                                {"fileid": 1669, "author": "Sallust", "title": "Bellum Iugurthinum"},
    "sall.cotta.txt":                            {"fileid": 1670, "author": "Sallust", "title": "Speech of Cotta"},
    "sall.ep1.txt":                              {"fileid": 1671, "author": "Sallust", "title": "Letter to Caesar I"},
    "sall.ep2.txt":                              {"fileid": 1672, "author": "Sallust", "title": "Letter to Caesar II"},
    "sall.frag.txt":                             {"fileid": 1673, "author": "Sallust", "title": "Fragmenta"},
    "sall.invectiva.txt":                        {
        "fileid": 1674, "author": "Sallust", "title": "Invective Against Cicero"
    }, "sall.lep.txt":                           {"fileid": 1675, "author": "Sallust", "title": "Speech of Lepidus"},
    "sall.macer.txt":                            {"fileid": 1676, "author": "Sallust", "title": "Speech of Macer"},
    "sall.mithr.txt":                            {
        "fileid": 1677, "author": "Sallust", "title": "Speech of Mithridates"
    }, "sall.phil.txt":                          {"fileid": 1678, "author": "Sallust", "title": "Speech of Philippus"},
    "sall.pomp.txt":                             {"fileid": 1679, "author": "Sallust", "title": "Speech of Pompey"},
    "sannazaro1.txt":                            {"fileid": 1680, "author": "Sannazaro", "title": "de Partu Virginis"},
    "sannazaro2.txt":                            {
        "fileid": 1681, "author": "Sannazaro", "title": "Lamentatio de morte Christi"
    }, "scaliger.txt":                           {"fileid": 1682, "author": None, "title": "Scaliger"},
    "scbaccanalibus.txt":                        {
        "fileid": 1683, "author": None, "title": "SENATUS CONSULTUM DE BACCHANALIBUS"
    }, "scottus.txt":                            {"fileid": 1684, "author": None, "title": "Sedulius Scottus "},
    "sedulius.solis.txt":                        {
        "fileid": 1685, "author": "Sedulius", "title": "A solis ortus cardine"
    }, "sedulius1.txt":                          {"fileid": 1686, "author": "Sedulius", "title": "Carmen Paschale I"},
    "sedulius2.txt":                             {"fileid": 1687, "author": "Sedulius", "title": "Carmen Paschale II"},
    "sedulius3.txt":                             {"fileid": 1688, "author": "Sedulius", "title": "Carmen Paschale III"},
    "sedulius4.txt":                             {"fileid": 1689, "author": "Sedulius", "title": "Carmen Paschale IV"},
    "sedulius5.txt":                             {"fileid": 1690, "author": "Sedulius", "title": "Carmen Paschale I"},
    "sen/ben1.txt":                              {"fileid": 1691, "author": "Seneca", "title": "On Benefits I "},
    "sen/ben2.txt":                              {"fileid": 1692, "author": "Seneca", "title": "On Benefits II "},
    "sen/ben3.txt":                              {"fileid": 1693, "author": "Seneca", "title": "On Benefits III "},
    "sen/octavia.txt":                           {"fileid": 1694, "author": "Seneca", "title": "Octavia"},
    "sen/sen.agamemnon.txt":                     {"fileid": 1695, "author": "Seneca", "title": "Agamemnon"},
    "sen/sen.apoc.txt":                          {"fileid": 1696, "author": "Seneca", "title": "Apocolocyntosis"},
    "sen/sen.brevita.txt":                       {
        "fileid": 1697, "author": "Seneca", "title": "On the Brevity of Life"
    }, "sen/sen.clem.txt":                       {"fileid": 1698, "author": "Seneca", "title": "On Clemency"},
    "sen/sen.consolatione1.txt":                 {
        "fileid": 1699, "author": "Seneca", "title": "On Consolation (ad Polybium)"
    }, "sen/sen.consolatione2.txt":              {
        "fileid": 1700, "author": "Seneca", "title": "On Consolation (ad Marciam)"
    }, "sen/sen.consolatione3.txt":              {"fileid": 1701, "author": "Seneca", "title": "On Consolatio"},
    "sen/sen.constantia.txt":                    {"fileid": 1702, "author": "Seneca", "title": "de Constantia"},
    "sen/sen.hercules.txt":                      {"fileid": 1703, "author": "Seneca", "title": "Hercules"},
    "sen/sen.ira1.txt":                          {"fileid": 1704, "author": "Seneca", "title": "On Anger I"},
    "sen/sen.ira2.txt":                          {"fileid": 1705, "author": "Seneca", "title": "On Anger II"},
    "sen/sen.ira3.txt":                          {"fileid": 1706, "author": "Seneca", "title": "On Anger III"},
    "sen/sen.medea.txt":                         {"fileid": 1707, "author": "Seneca", "title": "Medea"},
    "sen/sen.oedipus.txt":                       {"fileid": 1708, "author": "Seneca", "title": "Oedipus"},
    "sen/sen.otio.txt":                          {"fileid": 1709, "author": "Seneca", "title": "On Leisure"},
    "sen/sen.phaedra.txt":                       {"fileid": 1710, "author": "Seneca", "title": "Phaedra"},
    "sen/sen.phoen.txt":                         {"fileid": 1711, "author": "Seneca", "title": "Phoenissae"},
    "sen/sen.prov.txt":                          {"fileid": 1712, "author": "Seneca", "title": "On Providence"},
    "sen/sen.proverbs.txt":                      {"fileid": 1713, "author": None, "title": "Proverbia Senecae"},
    "sen/sen.qn1.txt":                           {
        "fileid": 1714, "author": "Seneca", "title": "Quaestiones Naturales I"
    }, "sen/sen.qn2.txt":                        {
        "fileid": 1715, "author": "Seneca", "title": "Quaestiones Naturales II"
    }, "sen/sen.qn3.txt":                        {
        "fileid": 1716, "author": "Seneca", "title": "Quaestiones Naturales III"
    }, "sen/sen.qn4.txt":                        {
        "fileid": 1717, "author": "Seneca", "title": "Quaestiones Naturales IV"
    }, "sen/sen.qn5.txt":                        {
        "fileid": 1718, "author": "Seneca", "title": "Quaestiones Naturales V"
    }, "sen/sen.qn6.txt":                        {
        "fileid": 1719, "author": "Seneca", "title": "Quaestiones Naturales VI"
    }, "sen/sen.qn7.txt":                        {
        "fileid": 1720, "author": "Seneca", "title": "Quaestiones Naturales VII"
    }, "sen/sen.thyestes.txt":                   {"fileid": 1721, "author": "Seneca", "title": "Thyestes"},
    "sen/sen.tranq.txt":                         {
        "fileid": 1722, "author": "Seneca", "title": "On Tranquility of the Mind"
    }, "sen/sen.vita.txt":                       {"fileid": 1723, "author": "Seneca", "title": "On the Good Life"},
    "sen/seneca.ep1.txt":                        {
        "fileid": 1724, "author": "Seneca", "title": "Epistulae Morales, Liber I"
    }, "sen/seneca.ep10.txt":                    {
        "fileid": 1725, "author": "Seneca", "title": "Epistulae Morales, Liber X"
    }, "sen/seneca.ep11-13.txt":                 {
        "fileid": 1726, "author": "Seneca", "title": "Epistulae Morales, Liber XI-XIII"
    }, "sen/seneca.ep14-15.txt":                 {
        "fileid": 1727, "author": "Seneca", "title": "Epistulae Morales, Liber XIV & XV"
    }, "sen/seneca.ep16.txt":                    {
        "fileid": 1728, "author": "Seneca", "title": "Epistulae Morales, Liber XVI"
    }, "sen/seneca.ep17-18.txt":                 {
        "fileid": 1729, "author": "Seneca", "title": "Epistulae Morales, Liber XVII & XVIII"
    }, "sen/seneca.ep19.txt":                    {
        "fileid": 1730, "author": "Seneca", "title": "Epistulae Morales, Liber XIX"
    }, "sen/seneca.ep2.txt":                     {
        "fileid": 1731, "author": "Seneca", "title": "Epistulae Morales, Liber II"
    }, "sen/seneca.ep20.txt":                    {
        "fileid": 1732, "author": "Seneca", "title": "Epistulae Morales, Liber XX"
    }, "sen/seneca.ep22.txt":                    {
        "fileid": 1733, "author": "Seneca", "title": "Epistulae Morales, Liber XXII (Fragmenta)"
    }, "sen/seneca.ep3.txt":                     {
        "fileid": 1734, "author": "Seneca", "title": "Epistulae Morales, Liber IIII"
    }, "sen/seneca.ep4.txt":                     {
        "fileid": 1735, "author": "Seneca", "title": "Epistulae Morales, Liber IV"
    }, "sen/seneca.ep5.txt":                     {
        "fileid": 1736, "author": "Seneca", "title": "Epistulae Morales, Liber V"
    }, "sen/seneca.ep6.txt":                     {
        "fileid": 1737, "author": "Seneca", "title": "Epistulae Morales, Liber VI"
    }, "sen/seneca.ep7.txt":                     {
        "fileid": 1738, "author": "Seneca", "title": "Epistulae Morales, Liber VII"
    }, "sen/seneca.ep8.txt":                     {
        "fileid": 1739, "author": "Seneca", "title": "Epistulae Morales, Liber VIII"
    }, "sen/seneca.ep9.txt":                     {
        "fileid": 1740, "author": "Seneca", "title": "Epistulae Morales, Liber IX"
    }, "seneca.contr1.txt":                      {"fileid": 1741, "author": None, "title": "Seneca the Elder"},
    "seneca.contr10.txt":                        {"fileid": 1742, "author": None, "title": "Seneca the Elder"},
    "seneca.contr2.txt":                         {"fileid": 1743, "author": None, "title": "Seneca the Elder"},
    "seneca.contr3.txt":                         {"fileid": 1744, "author": None, "title": "Seneca the Elder"},
    "seneca.contr4.txt":                         {"fileid": 1745, "author": None, "title": "Seneca the Elder"},
    "seneca.contr5.txt":                         {"fileid": 1746, "author": None, "title": "Seneca the Elder"},
    "seneca.contr6.txt":                         {"fileid": 1747, "author": None, "title": "Seneca the Elder"},
    "seneca.contr7.txt":                         {"fileid": 1748, "author": None, "title": "Seneca the Elder"},
    "seneca.contr8.txt":                         {"fileid": 1749, "author": None, "title": "Seneca the Elder"},
    "seneca.contr9.txt":                         {"fileid": 1750, "author": None, "title": "Seneca the Elder"},
    "seneca.fragmenta.txt":                      {"fileid": 1751, "author": None, "title": "Seneca the Elder"},
    "seneca.suasoriae.txt":                      {"fileid": 1752, "author": None, "title": "Seneca the Elder"},
    "septsap.txt":                               {
        "fileid": 1753, "author": None, "title": "The Story of the Seven Wise Men"
    }, "sha/30.txt":                             {"fileid": 1754, "author": None, "title": "The Thirty Tyrants"},
    "sha/aelii.txt":                             {"fileid": 1755, "author": None, "title": "Aelius"},
    "sha/alexsev.txt":                           {"fileid": 1756, "author": None, "title": "Alexander Severus"},
    "sha/ant.txt":                               {"fileid": 1757, "author": None, "title": "Antoninus Pius"},
    "sha/aurel.txt":                             {"fileid": 1758, "author": None, "title": "Aurelian"},
    "sha/avid.txt":                              {"fileid": 1759, "author": None, "title": "Avidius Cassius"},
    "sha/car.txt":                               {"fileid": 1760, "author": None, "title": "Caracalla"},
    "sha/carus.txt":                             {"fileid": 1761, "author": "Carus", "title": "Carinus, Numerianus"},
    "sha/claud.txt":                             {"fileid": 1762, "author": None, "title": "Claudius"},
    "sha/clod.txt":                              {"fileid": 1763, "author": None, "title": "Clodius Albinus"},
    "sha/com.txt":                               {"fileid": 1764, "author": None, "title": "Commodus"},
    "sha/diad.txt":                              {"fileid": 1765, "author": None, "title": "Diadumenus"},
    "sha/didiul.txt":                            {"fileid": 1766, "author": None, "title": "Didius Iulianus"},
    "sha/firmus.txt":                            {"fileid": 1767, "author": None, "title": "Tyrants"},
    "sha/gall.txt":                              {"fileid": 1768, "author": None, "title": "The Two Gallieni"},
    "sha/geta.txt":                              {"fileid": 1769, "author": None, "title": "Geta"},
    "sha/gord.txt":                              {"fileid": 1770, "author": None, "title": "The Three Gordians"},
    "sha/hadr.txt":                              {"fileid": 1771, "author": None, "title": "Hadrian"},
    "sha/helio.txt":                             {"fileid": 1772, "author": None, "title": "Elagabalus"},
    "sha/mac.txt":                               {"fileid": 1773, "author": None, "title": "Macrinus"},
    "sha/marcant.txt":                           {"fileid": 1774, "author": None, "title": "Marcus Aurelius"},
    "sha/max.txt":                               {"fileid": 1775, "author": None, "title": "Maximini"},
    "sha/maxbal.txt":                            {"fileid": 1776, "author": None, "title": "Maximus et Balbinus"},
    "sha/pert.txt":                              {"fileid": 1777, "author": None, "title": "Pertinax"},
    "sha/pesc.txt":                              {"fileid": 1778, "author": None, "title": "Pescenius Niger"},
    "sha/probus.txt":                            {"fileid": 1779, "author": None, "title": "Probus"},
    "sha/sepsev.txt":                            {"fileid": 1780, "author": None, "title": "Septimus Severus"},
    "sha/tacitus.txt":                           {"fileid": 1781, "author": None, "title": "Tacitus"},
    "sha/val.txt":                               {"fileid": 1782, "author": None, "title": "The Two Valerians"},
    "sha/verus.txt":                             {"fileid": 1783, "author": None, "title": "L. Verus"},
    "sicmeafata.txt":                            {
        "fileid": 1784, "author": None, "title": "Sic mea fata canendo solor "
    }, "sidonius1.txt":                          {"fileid": 1785, "author": "Sidonius", "title": "Epistularum Liber I"},
    "sidonius2.txt":                             {
        "fileid": 1786, "author": "Sidonius", "title": "Epistularum Liber II"
    }, "sidonius3.txt":                          {
        "fileid": 1787, "author": "Sidonius", "title": "Epistularum Liber III"
    }, "sidonius4.txt":                          {
        "fileid": 1788, "author": "Sidonius", "title": "Epistularum Liber IV"
    }, "sidonius5.txt":                          {"fileid": 1789, "author": "Sidonius", "title": "Epistularum Liber V"},
    "sidonius6.txt":                             {
        "fileid": 1790, "author": "Sidonius", "title": "Epistularum Liber VI"
    }, "sidonius7.txt":                          {
        "fileid": 1791, "author": "Sidonius", "title": "Epistularum Liber VII"
    }, "sidonius8.txt":                          {
        "fileid": 1792, "author": "Sidonius", "title": "Epistularum Liber VIII"
    }, "sidonius9.txt":                          {
        "fileid": 1793, "author": "Sidonius", "title": "Epistularum Liber IX"
    }, "sigebert.script.txt":                    {"fileid": 1794, "author": None, "title": "Sigebert of Gembloux"},
    "sigebert.virgin.txt":                       {"fileid": 1795, "author": None, "title": "Sigebert of Gembloux"},
    "sigebert.vitabrevior.txt":                  {"fileid": 1796, "author": None, "title": "Sigebert of Gembloux"},
    "silius/silius1.txt":                        {"fileid": 1797, "author": "Silius", "title": "Liber I"},
    "silius/silius10.txt":                       {"fileid": 1798, "author": "Silius", "title": "Liber X"},
    "silius/silius11.txt":                       {"fileid": 1799, "author": "Silius", "title": "Liber XI"},
    "silius/silius12.txt":                       {"fileid": 1800, "author": "Silius", "title": "Liber XII"},
    "silius/silius13.txt":                       {"fileid": 1801, "author": "Silius", "title": "Liber XIII"},
    "silius/silius14.txt":                       {"fileid": 1802, "author": "Silius", "title": "Liber XIV"},
    "silius/silius15.txt":                       {"fileid": 1803, "author": "Silius", "title": "Liber XV"},
    "silius/silius16.txt":                       {"fileid": 1804, "author": "Silius", "title": "Liber XVI"},
    "silius/silius17.txt":                       {"fileid": 1805, "author": "Silius", "title": "Liber XVII"},
    "silius/silius2.txt":                        {"fileid": 1806, "author": "Silius", "title": "Liber II"},
    "silius/silius3.txt":                        {"fileid": 1807, "author": "Silius", "title": "Liber IIII"},
    "silius/silius4.txt":                        {"fileid": 1808, "author": "Silius", "title": "Liber IV"},
    "silius/silius5.txt":                        {"fileid": 1809, "author": "Silius", "title": "Liber V"},
    "silius/silius6.txt":                        {"fileid": 1810, "author": "Silius", "title": "Liber VI"},
    "silius/silius7.txt":                        {"fileid": 1811, "author": "Silius", "title": "Liber VII"},
    "silius/silius8.txt":                        {"fileid": 1812, "author": "Silius", "title": "Liber VIII"},
    "silius/silius9.txt":                        {"fileid": 1813, "author": "Silius", "title": "Liber IX"},
    "simedignetur.txt":                          {
        "fileid": 1814, "author": None, "title": "Si me dignetur quam desidero "
    }, "smarius.txt":                            {"fileid": 1815, "author": None, "title": "Alexander Smarius"},
    "solet.txt":                                 {"fileid": 1816, "author": None, "title": "Solet annuere "},
    "solinus1.txt":                              {"fileid": 1817, "author": None, "title": "Solinus"},
    "solinus1a.txt":                             {"fileid": 1818, "author": None, "title": "Solinus"},
    "solinus2.txt":                              {"fileid": 1819, "author": None, "title": "Solinus"},
    "solinus2a.txt":                             {"fileid": 1820, "author": None, "title": "Solinus"},
    "solinus3.txt":                              {"fileid": 1821, "author": None, "title": "Solinus"},
    "solinus3a.txt":                             {"fileid": 1822, "author": None, "title": "Solinus"},
    "solinus4.txt":                              {"fileid": 1823, "author": None, "title": "Solinus"},
    "solinus4a.txt":                             {"fileid": 1824, "author": None, "title": "Solinus"},
    "solinus5.txt":                              {"fileid": 1825, "author": None, "title": "Solinus"},
    "spinoza.ethica1.txt":                       {"fileid": 1826, "author": "Spinoza", "title": "Ethica I"},
    "spinoza.ethica2.txt":                       {"fileid": 1827, "author": "Spinoza", "title": "Ethica I "},
    "spinoza.ethica3.txt":                       {"fileid": 1828, "author": "Spinoza", "title": "Ethica III "},
    "spinoza.ethica4.txt":                       {"fileid": 1829, "author": "Spinoza", "title": "Ethica IV "},
    "spinoza.ethica5.txt":                       {"fileid": 1830, "author": "Spinoza", "title": "Ethica V "},
    "statius/achilleid1.txt":                    {"fileid": 1831, "author": "Statius", "title": "Achilleid I"},
    "statius/achilleid2.txt":                    {"fileid": 1832, "author": "Statius", "title": "Achilleid II"},
    "statius/silvae1.txt":                       {"fileid": 1833, "author": "Statius", "title": "Silvae I"},
    "statius/silvae2.txt":                       {"fileid": 1834, "author": "Statius", "title": "Silvae II"},
    "statius/silvae3.txt":                       {"fileid": 1835, "author": "Statius", "title": "Silvae III"},
    "statius/silvae4.txt":                       {"fileid": 1836, "author": "Statius", "title": "Silvae IV"},
    "statius/silvae5.txt":                       {"fileid": 1837, "author": "Statius", "title": "Silvae V"},
    "statius/theb1.txt":                         {"fileid": 1838, "author": "Statius", "title": "Thebaid I"},
    "statius/theb10.txt":                        {"fileid": 1839, "author": "Statius", "title": "Thebaid X"},
    "statius/theb11.txt":                        {"fileid": 1840, "author": "Statius", "title": "Thebaid XI"},
    "statius/theb12.txt":                        {"fileid": 1841, "author": "Statius", "title": "Thebaid XII"},
    "statius/theb2.txt":                         {"fileid": 1842, "author": "Statius", "title": "Thebaid II"},
    "statius/theb3.txt":                         {"fileid": 1843, "author": "Statius", "title": "Thebaid III"},
    "statius/theb4.txt":                         {"fileid": 1844, "author": "Statius", "title": "Thebaid IV"},
    "statius/theb5.txt":                         {"fileid": 1845, "author": "Statius", "title": "Thebaid V"},
    "statius/theb6.txt":                         {"fileid": 1846, "author": "Statius", "title": "Thebaid VI"},
    "statius/theb7.txt":                         {"fileid": 1847, "author": "Statius", "title": "Thebaid VII"},
    "statius/theb8.txt":                         {"fileid": 1848, "author": "Statius", "title": "Thebaid VIII"},
    "statius/theb9.txt":                         {"fileid": 1849, "author": "Statius", "title": "Thebaid IX"},
    "suetonius/suet.aug.txt":                    {"fileid": 1850, "author": "Suetonius", "title": "Divus Augustus"},
    "suetonius/suet.caesar.txt":                 {"fileid": 1851, "author": "Suetonius", "title": "Divus Iulius"},
    "suetonius/suet.cal.txt":                    {"fileid": 1852, "author": None, "title": "\u0007 "},
    "suetonius/suet.claudius.txt":               {"fileid": 1853, "author": "Suetonius", "title": "Divus Claudius"},
    "suetonius/suet.crispus.txt":                {"fileid": 1854, "author": "Suetonius", "title": "Life of Crispus"},
    "suetonius/suet.dom.txt":                    {"fileid": 1855, "author": "Suetonius", "title": "Domitian"},
    "suetonius/suet.galba.txt":                  {"fileid": 1856, "author": "Suetonius", "title": "Life of Galba"},
    "suetonius/suet.gram.txt":                   {"fileid": 1857, "author": "Suetonius", "title": "de Grammaticis"},
    "suetonius/suet.horace.txt":                 {"fileid": 1858, "author": "Suetonius", "title": "Life of Horace"},
    "suetonius/suet.lucan.txt":                  {"fileid": 1859, "author": "Suetonius", "title": "Life of Lucan"},
    "suetonius/suet.nero.txt":                   {"fileid": 1860, "author": "Suetonius", "title": "Life of Nero"},
    "suetonius/suet.otho.txt":                   {"fileid": 1861, "author": "Suetonius", "title": "Life of Otho"},
    "suetonius/suet.persius.txt":                {"fileid": 1862, "author": "Suetonius", "title": "Life of Persius"},
    "suetonius/suet.pliny.txt":                  {"fileid": 1863, "author": "Suetonius", "title": "Life of Pliny"},
    "suetonius/suet.rhet.txt":                   {"fileid": 1864, "author": "Suetonius", "title": "de Rhetoribus"},
    "suetonius/suet.terence.txt":                {"fileid": 1865, "author": "Suetonius", "title": "Life of Terence"},
    "suetonius/suet.tib.txt":                    {"fileid": 1866, "author": "Suetonius", "title": "Life of Tiberius"},
    "suetonius/suet.tibullus.txt":               {"fileid": 1867, "author": "Suetonius", "title": "Life of Tibullus"},
    "suetonius/suet.titus.txt":                  {"fileid": 1868, "author": "Suetonius", "title": "Life of Titus"},
    "suetonius/suet.vesp.txt":                   {"fileid": 1869, "author": "Suetonius", "title": "Life of Vespasian"},
    "suetonius/suet.virgil.txt":                 {"fileid": 1870, "author": "Suetonius", "title": "Life of Vergil"},
    "suetonius/suet.vit.txt":                    {"fileid": 1871, "author": "Suetonius", "title": "Life of Vitellius"},
    "sulpicia.txt":                              {"fileid": 1872, "author": None, "title": "Sulpicia"},
    "sulpiciusseveruschron1.txt":                {
        "fileid": 1873, "author": "Sulpicius Severus", "title": "Chronicles I"
    }, "sulpiciusseveruschron2.txt":             {
        "fileid": 1874, "author": "Sulpicius Severus", "title": "Chronicles II"
    }, "sulpiciusseverusmartin.txt":             {
        "fileid": 1875, "author": "Sulpicius Severus", "title": "Life of St. Martin"
    }, "suscipeflos.txt":                        {"fileid": 1876, "author": None, "title": "Suscipe Flos "},
    "syrus.txt":                                 {"fileid": 1877, "author": None, "title": "Publilius Syrus"},
    "tacitus/tac.agri.txt":                      {"fileid": 1878, "author": "Tacitus", "title": "Agricola"},
    "tacitus/tac.ann1.txt":                      {"fileid": 1879, "author": "Tacitus", "title": "Annales I"},
    "tacitus/tac.ann11.txt":                     {"fileid": 1880, "author": "Tacitus", "title": "Annales XI"},
    "tacitus/tac.ann12.txt":                     {"fileid": 1881, "author": "Tacitus", "title": "Annales XII"},
    "tacitus/tac.ann13.txt":                     {"fileid": 1882, "author": "Tacitus", "title": "Annales XIII"},
    "tacitus/tac.ann14.txt":                     {"fileid": 1883, "author": "Tacitus", "title": "Annales XIV"},
    "tacitus/tac.ann15.txt":                     {"fileid": 1884, "author": "Tacitus", "title": "Annales XV"},
    "tacitus/tac.ann16.txt":                     {"fileid": 1885, "author": "Tacitus", "title": "Annales XVI"},
    "tacitus/tac.ann2.txt":                      {"fileid": 1886, "author": "Tacitus", "title": "Annales II"},
    "tacitus/tac.ann3.txt":                      {"fileid": 1887, "author": "Tacitus", "title": "Annales III"},
    "tacitus/tac.ann4.txt":                      {"fileid": 1888, "author": "Tacitus", "title": "Annales IV"},
    "tacitus/tac.ann5.txt":                      {"fileid": 1889, "author": "Tacitus", "title": "Annales V"},
    "tacitus/tac.ann6.txt":                      {"fileid": 1890, "author": "Tacitus", "title": "Annales VI"},
    "tacitus/tac.dialogus.txt":                  {
        "fileid": 1891, "author": "Tacitus", "title": "Dialogus de Oratoribus"
    }, "tacitus/tac.ger.txt":                    {"fileid": 1892, "author": "Tacitus", "title": "Germania"},
    "tacitus/tac.hist1.txt":                     {"fileid": 1893, "author": "Tacitus", "title": "Histories I"},
    "tacitus/tac.hist2.txt":                     {"fileid": 1894, "author": "Tacitus", "title": "Histories II"},
    "tacitus/tac.hist3.txt":                     {"fileid": 1895, "author": "Tacitus", "title": "Histories III"},
    "tacitus/tac.hist4.txt":                     {"fileid": 1896, "author": "Tacitus", "title": "Histories IV"},
    "tacitus/tac.hist5.txt":                     {"fileid": 1897, "author": "Tacitus", "title": "Histories V"},
    "tempusest.txt":                             {"fileid": 1898, "author": None, "title": "Tempus est iocundum "},
    "ter.adel.txt":                              {"fileid": 1899, "author": "Terence", "title": "Adelphoe"},
    "ter.andria.txt":                            {"fileid": 1900, "author": "Terence", "title": "Andria"},
    "ter.eunuchus.txt":                          {"fileid": 1901, "author": "Terence", "title": "Eunuchus"},
    "ter.heauton.txt":                           {"fileid": 1902, "author": "Terence", "title": "Heauton Timorumenos"},
    "ter.hecyra.txt":                            {"fileid": 1903, "author": "Terence", "title": "Hecyra"},
    "ter.phormio.txt":                           {"fileid": 1904, "author": "Terence", "title": "Phormio"},
    "terraiam.txt":                              {"fileid": 1905, "author": None, "title": "Terra iam pandit gremium "},
    "tertullian/tertullian.adsenatorem.txt":     {
        "fileid": 1906, "author": None, "title": "[Tertulliani] ad Senatorem "
    }, "tertullian/tertullian.anima.txt":        {"fileid": 1907, "author": "Tertullian", "title": "De Anima "},
    "tertullian/tertullian.apol.txt":            {"fileid": 1908, "author": "Tertullian", "title": "Apology"},
    "tertullian/tertullian.baptismo.txt":        {"fileid": 1909, "author": "Tertullian", "title": "de Baptismo "},
    "tertullian/tertullian.carne.txt":           {"fileid": 1910, "author": "Tertullian", "title": "de Carne Christi "},
    "tertullian/tertullian.castitatis.txt":      {
        "fileid": 1911, "author": "Tertullian", "title": "De Exhortatione Castitatis "
    }, "tertullian/tertullian.corona.txt":       {
        "fileid": 1912, "author": "Tertullian", "title": "Liber De Corona Militis "
    }, "tertullian/tertullian.cultu1.txt":       {
        "fileid": 1913, "author": "Tertullian", "title": "Tertulliani De Cultu Feminarum Libri Duo : Liber I "
    }, "tertullian/tertullian.cultu2.txt":       {
        "fileid": 1914, "author": "Tertullian", "title": "Tertulliani De Cultu Feminarum Libri Duo : Liber II "
    }, "tertullian/tertullian.deiudicio.txt":    {
        "fileid": 1915, "author": None, "title": "[Tertulliani] Carmen de Iudicio Domini "
    }, "tertullian/tertullian.fuga.txt":         {
        "fileid": 1916, "author": "Tertullian", "title": "De Fuga in Persecutione "
    }, "tertullian/tertullian.genesis.txt":      {"fileid": 1917, "author": "Tertullian", "title": "Carmen Genesis "},
    "tertullian/tertullian.gentium.txt":         {
        "fileid": 1918, "author": "Tertullian", "title": "De Execrandis Gentium Diis "
    }, "tertullian/tertullian.haereses.txt":     {
        "fileid": 1919, "author": "Tertullian", "title": "Adversus Omnes Haereses "
    }, "tertullian/tertullian.herm.txt":         {
        "fileid": 1920, "author": "Tertullian", "title": "Liber adversus Hermogenem "
    }, "tertullian/tertullian.idololatria.txt":  {"fileid": 1921, "author": "Tertullian", "title": "De Idololatria"},
    "tertullian/tertullian.ieiunio.txt":         {"fileid": 1922, "author": "Tertullian", "title": "de Ieiunio"},
    "tertullian/tertullian.iudaeos.txt":         {"fileid": 1923, "author": "Tertullian", "title": "Adversus Iudaeos "},
    "tertullian/tertullian.marcionem1.txt":      {
        "fileid": 1924, "author": "Tertullian", "title": "Adversus Marcionem I "
    }, "tertullian/tertullian.marcionem2.txt":   {
        "fileid": 1925, "author": "Tertullian", "title": "Adversus Marcionem II "
    }, "tertullian/tertullian.marcionem3.txt":   {
        "fileid": 1926, "author": "Tertullian", "title": "Adversus Marcionem III "
    }, "tertullian/tertullian.marcionem4.txt":   {
        "fileid": 1927, "author": "Tertullian", "title": "Adversus Marcionem IV "
    }, "tertullian/tertullian.marcionem5.txt":   {
        "fileid": 1928, "author": "Tertullian", "title": "Adversus Marcionem V "
    }, "tertullian/tertullian.martyres.txt":     {"fileid": 1929, "author": "Tertullian", "title": "Ad Martyres "},
    "tertullian/tertullian.monog.txt":           {
        "fileid": 1930, "author": "Tertullian", "title": "Liber de Monogamia "
    }, "tertullian/tertullian.nationes1.txt":    {"fileid": 1931, "author": "Tertullian", "title": "ad Nationes I "},
    "tertullian/tertullian.nationes2.txt":       {"fileid": 1932, "author": "Tertullian", "title": "ad Nationes II "},
    "tertullian/tertullian.oratione.txt":        {"fileid": 1933, "author": "Tertullian", "title": "de Oratione "},
    "tertullian/tertullian.paen.txt":            {"fileid": 1934, "author": "Tertullian", "title": "De Paenitentia "},
    "tertullian/tertullian.pallio.txt":          {"fileid": 1935, "author": "Tertullian", "title": "de Pallio "},
    "tertullian/tertullian.patientia.txt":       {"fileid": 1936, "author": "Tertullian", "title": "De Patientia "},
    "tertullian/tertullian.praescrip.txt":       {
        "fileid": 1937, "author": "Tertullian", "title": "De Praescriptione Haereticorum "
    }, "tertullian/tertullian.praxean.txt":      {
        "fileid": 1938, "author": "Tertullian", "title": "Adversus Praexean "
    }, "tertullian/tertullian.propheta.txt":     {
        "fileid": 1939, "author": "Tertullian", "title": "Carmen de Iona propheta "
    }, "tertullian/tertullian.pudicitia.txt":    {"fileid": 1940, "author": "Tertullian", "title": "de Oratione "},
    "tertullian/tertullian.resurrectione.txt":   {
        "fileid": 1941, "author": "Tertullian ", "title": "De Resurrectione Carnis "
    }, "tertullian/tertullian.scapulam.txt":     {"fileid": 1942, "author": "Tertullian", "title": "ad Scapulam "},
    "tertullian/tertullian.scorpiace.txt":       {"fileid": 1943, "author": "Tertullian ", "title": "Scorpiace "},
    "tertullian/tertullian.spect.txt":           {"fileid": 1944, "author": "Tertullian", "title": "de Spectaculis "},
    "tertullian/tertullian.testimonia.txt":      {
        "fileid": 1945, "author": "Tertullian", "title": "de Testimonio Animae "
    }, "tertullian/tertullian.uxor1.txt":        {"fileid": 1946, "author": "Tertullian", "title": "ad Uxorem I "},
    "tertullian/tertullian.uxor2.txt":           {"fileid": 1947, "author": "Tertullian", "title": "ad Uxorem II "},
    "tertullian/tertullian.valentinianos.txt":   {
        "fileid": 1948, "author": "Tertullian", "title": "Adversus Valentinianos "
    }, "tertullian/tertullian.virginibus.txt":   {
        "fileid": 1949, "author": "Tertullian", "title": "de Virginibus Velandis"
    }, "testamentum.txt":                        {"fileid": 1950, "author": None, "title": "Testamentum Porcelli"},
    "tevigilans.txt":                            {"fileid": 1951, "author": None, "title": ""}, "theganus.txt": {
        "fileid": 1952, "author": "Theganus", "title": "Vita Hludowici Imperatoris"
    }, "theodolus.txt":                          {"fileid": 1953, "author": None, "title": "Theodulus"},
    "theodosius/theod01.txt":                    {"fileid": 1954, "author": "Theodosiani Codex", "title": "Liber I"},
    "theodosius/theod02.txt":                    {"fileid": 1955, "author": "Theodosiani Codex", "title": "Liber II"},
    "theodosius/theod03.txt":                    {"fileid": 1956, "author": "Theodosiani Codex", "title": "Liber III"},
    "theodosius/theod04.txt":                    {"fileid": 1957, "author": "Theodosiani Codex", "title": "Liber IV"},
    "theodosius/theod05.txt":                    {"fileid": 1958, "author": "Theodosiani Codex", "title": "Liber V"},
    "theodosius/theod06.txt":                    {"fileid": 1959, "author": "Theodosiani Codex", "title": "Liber VI"},
    "theodosius/theod07.txt":                    {"fileid": 1960, "author": "Theodosiani Codex", "title": "Liber VII"},
    "theodosius/theod08.txt":                    {"fileid": 1961, "author": "Theodosiani Codex", "title": "Liber VIII"},
    "theodosius/theod09.txt":                    {"fileid": 1962, "author": "Theodosiani Codex", "title": "Liber IX"},
    "theodosius/theod10.txt":                    {"fileid": 1963, "author": "Theodosiani Codex", "title": "Liber X"},
    "theodosius/theod11.txt":                    {"fileid": 1964, "author": "Theodosiani Codex", "title": "Liber XI"},
    "theodosius/theod12.txt":                    {"fileid": 1965, "author": "Theodosiani Codex", "title": "Liber XII"},
    "theodosius/theod13.txt":                    {"fileid": 1966, "author": "Theodosiani Codex", "title": "Liber XIII"},
    "theodosius/theod14.txt":                    {"fileid": 1967, "author": "Theodosiani Codex", "title": "Liber XIV"},
    "theodosius/theod15.txt":                    {"fileid": 1968, "author": "Theodosiani Codex", "title": "Liber XV"},
    "theodosius/theod16.txt":                    {"fileid": 1969, "author": "Theodosiani Codex", "title": "Liber XVI"},
    "theophanes.txt":                            {
        "fileid": 1970, "author": "Theophanes Prokopovic", "title": "Epigrammata"
    }, "thesauro.txt":                           {
        "fileid": 1971, "author": "Johannes de Alta Silva", "title": "de Thesauro et Fure Astuto"
    }, "thomasedessa.txt":                       {"fileid": 1972, "author": None, "title": "Thomas of Edessa (Carr)"},
    "tibullus1.txt":                             {"fileid": 1973, "author": None, "title": "Tibullus Book I"},
    "tibullus2.txt":                             {"fileid": 1974, "author": None, "title": "Tibullus Book II"},
    "tibullus3.txt":                             {"fileid": 1975, "author": None, "title": "Tibullus Book III"},
    "tunger.txt":                                {"fileid": 1976, "author": None, "title": "Augustin T\u00fcnger"},
    "valeriusflaccus1.txt":                      {"fileid": 1977, "author": "Valerius Flaccus", "title": "Liber I"},
    "valeriusflaccus2.txt":                      {"fileid": 1978, "author": "Valerius Flaccus", "title": "Liber II"},
    "valeriusflaccus3.txt":                      {"fileid": 1979, "author": "Valerius Flaccus", "title": "Liber III"},
    "valeriusflaccus4.txt":                      {"fileid": 1980, "author": "Valerius Flaccus", "title": "Liber IV"},
    "valeriusflaccus5.txt":                      {"fileid": 1981, "author": "Valerius Flaccus", "title": "Liber V"},
    "valeriusflaccus6.txt":                      {"fileid": 1982, "author": "Valerius Flaccus", "title": "Liber VI"},
    "valeriusflaccus7.txt":                      {"fileid": 1983, "author": "Valerius Flaccus", "title": "Liber VII"},
    "valeriusflaccus8.txt":                      {"fileid": 1984, "author": "Valerius Flaccus", "title": "Liber VIII"},
    "valesianus.txt":                            {"fileid": 1985, "author": None, "title": "Anonymus Valesianus"},
    "valesianus1.txt":                           {
        "fileid": 1986, "author": "Anonymus Valesianus", "title": "Origo Constantini Imperatoris"
    }, "valesianus2.txt":                        {
        "fileid": 1987, "author": "Anonymus Valesianus", "title": "Chronica Theodericiana"
    }, "valmax1.txt":                            {"fileid": 1988, "author": None, "title": "Valerius Maximus I"},
    "valmax2.txt":                               {"fileid": 1989, "author": None, "title": "Valerius Maximus II"},
    "valmax3.txt":                               {"fileid": 1990, "author": None, "title": "Valerius Maximus III"},
    "valmax4.txt":                               {"fileid": 1991, "author": None, "title": "Valerius Maximus IV"},
    "valmax5.txt":                               {"fileid": 1992, "author": None, "title": "Valerius Maximus V"},
    "valmax6.txt":                               {"fileid": 1993, "author": None, "title": "Valerius Maximus VI"},
    "valmax7.txt":                               {"fileid": 1994, "author": None, "title": "Valerius Maximus VII"},
    "valmax8.txt":                               {"fileid": 1995, "author": None, "title": "Valerius Maximus VIII"},
    "valmax9.txt":                               {"fileid": 1996, "author": None, "title": "Valerius Maximus I"},
    "varro.frag.txt":                            {"fileid": 1997, "author": None, "title": ""},
    "varro.ll10.txt":                            {"fileid": 1998, "author": None, "title": ""},
    "varro.ll5.txt":                             {"fileid": 1999, "author": None, "title": ""},
    "varro.ll6.txt":                             {"fileid": 2000, "author": None, "title": ""},
    "varro.ll7.txt":                             {"fileid": 2001, "author": None, "title": ""},
    "varro.ll8.txt":                             {"fileid": 2002, "author": None, "title": ""},
    "varro.ll9.txt":                             {"fileid": 2003, "author": None, "title": ""},
    "varro.rr1.txt":                             {"fileid": 2004, "author": "Varro", "title": "De Agri Cultura I"},
    "varro.rr2.txt":                             {"fileid": 2005, "author": "Varro", "title": "De Agri Cultura II"},
    "varro.rr3.txt":                             {"fileid": 2006, "author": "Varro", "title": "De Agri Cultura III"},
    "vegetius1.txt":                             {"fileid": 2007, "author": None, "title": "Vegetius Liber I"},
    "vegetius2.txt":                             {"fileid": 2008, "author": None, "title": "Vegetius Liber II"},
    "vegetius3.txt":                             {"fileid": 2009, "author": None, "title": "Vegetius Liber III"},
    "vegetius4.txt":                             {"fileid": 2010, "author": None, "title": "Vegetius Liber IV"},
    "vegius.txt":                                {"fileid": 2011, "author": "Vegius", "title": "Aeneidos Supplementum"},
    "vell1.txt":                                 {"fileid": 2012, "author": None, "title": "Velleius Paterculus"},
    "vell2.txt":                                 {"fileid": 2013, "author": None, "title": "Velleius Paterculus"},
    "venantius.txt":                             {"fileid": 2014, "author": None, "title": "Venantius Fortunatus"},
    "vergil/aen1.txt":                           {"fileid": 2015, "author": "Vergil", "title": "Aeneid I"},
    "vergil/aen10.txt":                          {
        "fileid": 2016, "author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER DECIMVS"
    }, "vergil/aen11.txt":                       {
        "fileid": 2017, "author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER VNDECIMVS"
    }, "vergil/aen12.txt":                       {
        "fileid": 2018, "author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER PRIMVS"
    }, "vergil/aen2.txt":                        {
        "fileid": 2019, "author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER SECVNDVS"
    }, "vergil/aen3.txt":                        {
        "fileid": 2020, "author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER TERTIVS"
    }, "vergil/aen4.txt":                        {
        "fileid": 2021, "author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER QVARTVS"
    }, "vergil/aen5.txt":                        {
        "fileid": 2022, "author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER QVINTVS"
    }, "vergil/aen6.txt":                        {
        "fileid": 2023, "author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER SEXTVS"
    }, "vergil/aen7.txt":                        {
        "fileid": 2024, "author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER SEPTIMVS"
    }, "vergil/aen8.txt":                        {
        "fileid": 2025, "author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER OCTAVVS"
    }, "vergil/aen9.txt":                        {
        "fileid": 2026, "author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER NONVS"
    }, "vergil/ec1.txt":                         {
        "fileid": 2027, "author": "P. VERGILI MARONIS", "title": "ECLOGA PRIMA"
    }, "vergil/ec10.txt":                        {
        "fileid": 2028, "author": "P. VERGILI MARONIS", "title": "ECLOGA DECIMA"
    }, "vergil/ec2.txt":                         {
        "fileid": 2029, "author": "P. VERGILI MARONIS", "title": "ECLOGA SECVNDA"
    }, "vergil/ec3.txt":                         {
        "fileid": 2030, "author": "P. VERGILI MARONIS", "title": "ECLOGA TERTIA"
    }, "vergil/ec4.txt":                         {
        "fileid": 2031, "author": "P. VERGILI MARONIS", "title": "ECLOGA QVARTA"
    }, "vergil/ec5.txt":                         {
        "fileid": 2032, "author": "P. VERGILI MARONIS", "title": "ECLOGA QVINTA"
    }, "vergil/ec6.txt":                         {
        "fileid": 2033, "author": "P. VERGILI MARONIS", "title": "ECLOGA SEXTA"
    }, "vergil/ec7.txt":                         {
        "fileid": 2034, "author": "P. VERGILI MARONIS", "title": "ECLOGA SEPTIMA"
    }, "vergil/ec8.txt":                         {
        "fileid": 2035, "author": "P. VERGILI MARONIS", "title": "ECLOGA OCTAVA"
    }, "vergil/ec9.txt":                         {
        "fileid": 2036, "author": "P. VERGILI MARONIS", "title": "ECLOGA NONA"
    }, "vergil/geo1.txt":                        {
        "fileid": 2037, "author": "P. VERGILI MARONIS", "title": "GEORGICON LIBER PRIMVS"
    }, "vergil/geo2.txt":                        {
        "fileid": 2038, "author": "P. VERGILI MARONIS", "title": "GEORGICON LIBER SECVNDVS"
    }, "vergil/geo3.txt":                        {
        "fileid": 2039, "author": "P. VERGILI MARONIS", "title": "GEORGICON LIBER TERTIVS"
    }, "vergil/geo4.txt":                        {
        "fileid": 2040, "author": "P. VERGILI MARONIS", "title": "GEORGICON LIBER QVARTVS"
    }, "vestiunt.txt":                           {"fileid": 2041, "author": None, "title": ""}, "vicentius.txt": {
        "fileid": 2042, "author": "Vicentius Lerinensis", "title": "Commonitorium"
    }, "vico.orat6.txt":                         {"fileid": 2043, "author": "Vico", "title": "Oratio VI"},
    "victor.caes.txt":                           {"fileid": 2044, "author": None, "title": "LIBER DE CAESARIBUS"},
    "victor.caes2.txt":                          {"fileid": 2045, "author": None, "title": "EPITOME DE CAESARIBUS"},
    "victor.ill.txt":                            {"fileid": 2046, "author": None, "title": "DE VIRIS ILLVSTRIBVS"},
    "victor.origio.txt":                         {"fileid": 2047, "author": None, "title": "EPITOME DE CAESARIBUS"},
    "vida.txt":                                  {"fileid": 2048, "author": "Vida", "title": "Scacchia, Ludus"},
    "vitacaroli.txt":                            {"fileid": 2049, "author": None, "title": "Vita Caroli IV"},
    "vitruvius1.txt":                            {"fileid": 2050, "author": None, "title": "De Architectura Liber I"},
    "vitruvius10.txt":                           {"fileid": 2051, "author": None, "title": "De Architectura Liber X"},
    "vitruvius2.txt":                            {"fileid": 2052, "author": None, "title": "De Architectura Liber II"},
    "vitruvius3.txt":                            {"fileid": 2053, "author": None, "title": "De Architectura Liber III"},
    "vitruvius4.txt":                            {"fileid": 2054, "author": None, "title": "De Architectura Liber IV"},
    "vitruvius5.txt":                            {"fileid": 2055, "author": None, "title": "De Architectura Liber V"},
    "vitruvius6.txt":                            {"fileid": 2056, "author": None, "title": "De Architectura Liber VI"},
    "vitruvius7.txt":                            {"fileid": 2057, "author": None, "title": "De Architectura Liber VII"},
    "vitruvius8.txt":                            {
        "fileid": 2058, "author": None, "title": "De Architectura Liber VIII"
    }, "vitruvius9.txt":                         {"fileid": 2059, "author": None, "title": "De Architectura Liber IX"},
    "volovirum.txt":                             {
        "fileid": 2060, "author": None, "title": "Volo virum vivere viriliter "
    }, "voragine/alexio.txt":                    {
        "fileid": 2061, "author": "Iacobus de Voragine", "title": "de Sancto Alexio"
    }, "voragine/ambro.txt":                     {
        "fileid": 2062, "author": "Iacobus de Voragine", "title": "Historia de Sancto Ambrosio"
    }, "voragine/anast.txt":                     {
        "fileid": 2063, "author": "Iacobus de Voragine", "title": "Historia de Sancta Anastasia"
    }, "voragine/andrea.txt":                    {
        "fileid": 2064, "author": "Iacobus de Voragine", "title": "De Sancto Andrea Apostolo"
    }, "voragine/ant.txt":                       {
        "fileid": 2065, "author": "Iacobus de Voragine", "title": "Historia de Sancto Antonio"
    }, "voragine/blas.txt":                      {
        "fileid": 2066, "author": "Iacobus de Voragine", "title": "Historia de Sancto Blasio"
    }, "voragine/chris.txt":                     {
        "fileid": 2067, "author": "Iacobus de Voragine", "title": "Historia de Sancto Christophoro"
    }, "voragine/fran.txt":                      {
        "fileid": 2068, "author": "Iacobus de Voragine", "title": "Historia de Sancto Francisco"
    }, "voragine/georgio.txt":                   {
        "fileid": 2069, "author": "Iacobus de Voragine", "title": "Historia de Sancto Georgio"
    }, "voragine/iacob.txt":                     {
        "fileid": 2070, "author": "Iacobus de Voragine", "title": "Historia de Sancto Iacobo Maiore"
    }, "voragine/iul.txt":                       {
        "fileid": 2071, "author": "Iacobus de Voragine", "title": "Historia de Sancto Iuliano"
    }, "voragine/jud.txt":                       {
        "fileid": 2072, "author": "Iacobus de Voragine", "title": "Historia de Juda Ischariota"
    }, "voragine/luc.txt":                       {
        "fileid": 2073, "author": "Iacobus de Voragine", "title": "Historia Sanctae Luciae"
    }, "voragine/marc.txt":                      {
        "fileid": 2074, "author": "Iacobus de Voragine", "title": "Historia de Sancto Macario"
    }, "voragine/mariamag.txt":                  {
        "fileid": 2075, "author": None, "title": "Historia de Sancta Maria Magdalena"
    }, "voragine/marina.txt":                    {
        "fileid": 2076, "author": "Iacobus de Voragine", "title": "Historia de sancta Marina virgine"
    }, "voragine/nic.txt":                       {
        "fileid": 2077, "author": "Iacobus de Voragine", "title": "Historia Sancti Nicolai"
    }, "voragine/paulo.txt":                     {
        "fileid": 2078, "author": "Iacobus de Voragine", "title": "Historia de Sancto Paulo Eremita"
    }, "voragine/seb.txt":                       {
        "fileid": 2079, "author": "Iacobus de Voragine", "title": "Historia de Sancto Sebastiano"
    }, "voragine/septem.txt":                    {
        "fileid": 2080, "author": "Iacobus de Voragine", "title": "Historia de Septem Dormientibus"
    }, "voragine/silv.txt":                      {
        "fileid": 2081, "author": "Iacobus de Voragine", "title": "Historia de Sancto Silvestro"
    }, "voragine/thom.txt":                      {
        "fileid": 2082, "author": "Iacobus de Voragine", "title": "Historia de Sancto Thoma apostolo"
    }, "voragine/vin.txt":                       {
        "fileid": 2083, "author": "Iacobus de Voragine", "title": "Historia de Sancto Vincentio"
    }, "voragine/vir.txt":                       {
        "fileid": 2084, "author": "Iacobus de Voragine", "title": "Historia de Virgine Quadam Antiochena"
    }, "waardenburg.txt":                        {
        "fileid": 2085, "author": None, "title": "Carmina Henrici Waardenburg"
    }, "waltarius1.txt":                         {"fileid": 2086, "author": None, "title": "Waltharius I"},
    "waltarius2.txt":                            {"fileid": 2087, "author": None, "title": "Waltharius II"},
    "waltarius3.txt":                            {"fileid": 2088, "author": None, "title": "Waltharius III"},
    "walter/pastourelles.txt":                   {"fileid": 2089, "author": None, "title": "Walter of Ch\u00e2tillon"},
    "walter/walter1.txt":                        {"fileid": 2090, "author": None, "title": "Walter of Ch\u00e2tillon"},
    "walter/walter2.txt":                        {"fileid": 2091, "author": None, "title": "Walter of Ch\u00e2tillon"},
    "walter/walter3.txt":                        {"fileid": 2092, "author": None, "title": "Walter of Ch\u00e2tillon"},
    "walter10.txt":                              {
        "fileid": 2093, "author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon"
    }, "walter11.txt":                           {
        "fileid": 2094, "author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon"
    }, "walter12.txt":                           {
        "fileid": 2095, "author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon"
    }, "walter4.txt":                            {
        "fileid": 2096, "author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon"
    }, "walter5.txt":                            {
        "fileid": 2097, "author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon"
    }, "walter6.txt":                            {
        "fileid": 2098, "author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon"
    }, "walter7.txt":                            {
        "fileid": 2099, "author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon"
    }, "walter8.txt":                            {
        "fileid": 2100, "author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon"
    }, "walter9.txt":                            {
        "fileid": 2101, "author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon"
    }, "walton.txt":                             {"fileid": 2102, "author": None, "title": "Brad Walton"},
    "williamapulia.txt":                         {
        "fileid": 2103, "author": "William of Apulia", "title": "Gesta Roberti Wiscardi"
    }, "williamtyre/1.txt":                      {"fileid": 2104, "author": "William of Tyre", "title": "Liber I"},
    "williamtyre/10.txt":                        {"fileid": 2105, "author": "William of Tyre", "title": "Liber X"},
    "williamtyre/11.txt":                        {"fileid": 2106, "author": "William of Tyre", "title": "Liber XI"},
    "williamtyre/12.txt":                        {"fileid": 2107, "author": "William of Tyre", "title": "Liber XII"},
    "williamtyre/13.txt":                        {"fileid": 2108, "author": "William of Tyre", "title": "Liber XIII"},
    "williamtyre/14.txt":                        {"fileid": 2109, "author": "William of Tyre", "title": "Liber XIV"},
    "williamtyre/15.txt":                        {"fileid": 2110, "author": "William of Tyre", "title": "Liber XV"},
    "williamtyre/16.txt":                        {"fileid": 2111, "author": "William of Tyre", "title": "Liber XVI"},
    "williamtyre/17.txt":                        {"fileid": 2112, "author": "William of Tyre", "title": "Liber XVII"},
    "williamtyre/18.txt":                        {"fileid": 2113, "author": "William of Tyre", "title": "Liber XVIII"},
    "williamtyre/19.txt":                        {"fileid": 2114, "author": "William of Tyre", "title": "Liber XIX"},
    "williamtyre/2.txt":                         {"fileid": 2115, "author": "William of Tyre", "title": "Liber II"},
    "williamtyre/20.txt":                        {"fileid": 2116, "author": "William of Tyre", "title": "Liber XX"},
    "williamtyre/21.txt":                        {"fileid": 2117, "author": "William of Tyre", "title": "Liber XXI"},
    "williamtyre/22.txt":                        {"fileid": 2118, "author": "William of Tyre", "title": "Liber XXII"},
    "williamtyre/23.txt":                        {"fileid": 2119, "author": "William of Tyre", "title": "Liber XXIII"},
    "williamtyre/3.txt":                         {"fileid": 2120, "author": "William of Tyre", "title": "Liber III"},
    "williamtyre/4.txt":                         {"fileid": 2121, "author": "William of Tyre", "title": "Liber IV"},
    "williamtyre/5.txt":                         {"fileid": 2122, "author": "William of Tyre", "title": "Liber V"},
    "williamtyre/6.txt":                         {"fileid": 2123, "author": "William of Tyre", "title": "Liber VI"},
    "williamtyre/7.txt":                         {"fileid": 2124, "author": "William of Tyre", "title": "Liber VII"},
    "williamtyre/8.txt":                         {"fileid": 2125, "author": "William of Tyre", "title": "Liber VIII"},
    "williamtyre/9.txt":                         {"fileid": 2126, "author": "William of Tyre", "title": "Liber IX"},
    "williamtyre/prologus.txt":                  {"fileid": 2127, "author": "William of Tyre", "title": None},
    "withof.txt":                                {"fileid": 2128, "author": None, "title": "Johann Hildebrand Withof"},
    "withof1.txt":                               {"fileid": 2129, "author": None, "title": "Johann Hildebrand Withof"},
    "withof2.txt":                               {"fileid": 2130, "author": None, "title": "Johann Hildebrand Withof "},
    "withof3.txt":                               {"fileid": 2131, "author": None, "title": "Johann Hildebrand Withof "},
    "withof4.txt":                               {"fileid": 2132, "author": None, "title": "Johann Hildebrand Withof "},
    "withof5.txt":                               {"fileid": 2133, "author": None, "title": "Johann Hildebrand Withof "},
    "withof6.txt":                               {"fileid": 2134, "author": None, "title": "Johann Hildebrand Withof"},
    "withof7.txt":                               {
        "fileid": 2135, "author": None, "title": "Johann Philipp Lorenz Withof"
    }, "wmconchesdogma.txt":                     {
        "fileid": 2136, "author": "[William of Conches]", "title": "Moralium dogma philosophorum"
    }, "wmconchesphil.txt":                      {"fileid": 2137, "author": None, "title": "William of Conches"},
    "xanten.txt":                                {
        "fileid": 2138, "author": None, "title": "Annales qui dicuntur Xantenses"
    }, "xylander/caesar.txt":                    {"fileid": 2139, "author": "Xylander", "title": "Vita Caesaris"},
    "zonaras.txt":                               {"fileid": 2140, "author": "Zonaras", "title": "Excerpta"}
}

AUTHOR_TAB = {
    "0":       {"author": None, "title": "DUODECIM TABULARUM LEGES", "path": "12tables.txt"},
    "1":       {"author": None, "title": "Cafraria", "path": "1644.txt"},
    "2":       {"author": None, "title": "Abbo Floriacensis", "path": "abbofloracensis.txt"}, "3": {
        "author": "PETRUS ABAELARDUS", "title": "DIALOGUS INTER PHILOSOPHUM, IUDAEUM ET CHRISTIANUM",
        "path":   "abelard/dialogus.txt"
    }, "4":    {
        "author": "PETRUS ABAELARDUS", "title": "HELOYSAE EPISTOLA AD ABELARDUM", "path": "abelard/epistola.txt"
    }, "5":    {"author": "PETRUS ABAELARDUS", "title": "AD AMICUM SUUM CONSOLATORIA", "path": "abelard/historia.txt"},
    "6":       {"author": "JOSEPHUS ADDISON", "title": "BAROMETRI DESCRIPTIO", "path": "addison/barometri.txt"},
    "7":       {"author": "JOSEPHUS ADDISON", "title": "AD INSIGNISSIMUM VIRUM", "path": "addison/burnett.txt"},
    "8":       {"author": "Joseph Addison", "title": "", "path": "addison/hannes.txt"},
    "9":       {"author": None, "title": "Joseph Addison ", "path": "addison/machinae.txt"},
    "10":      {"author": "Joseph Addison", "title": "Pax Gulielmi ", "path": "addison/pax.txt"},
    "11":      {"author": None, "title": "Joseph Addison ", "path": "addison/praelium.txt"},
    "12":      {"author": "Addison", "title": "Preface and Dedication ", "path": "addison/preface.txt"},
    "13":      {"author": None, "title": "Joseph Addison ", "path": "addison/resurr.txt"},
    "14":      {"author": "Joseph Addison", "title": "Sphaeristerium ", "path": "addison/sphaer.txt"},
    "15":      {"author": None, "title": "Adso Deruensis", "path": "adso.txt"},
    "16":      {"author": "Aelredus Rievallensis", "title": "de Amicitia", "path": "aelredus.txt"},
    "17":      {"author": None, "title": "Blessed Agnes of Bohemia", "path": "agnes.txt"},
    "18":      {"author": "Alanus de Insulis", "title": "Liber de plantcu naturae", "path": "alanus/alanus1.txt"},
    "19":      {"author": "Alanus de Insulis", "title": "Anticlaudianus", "path": "alanus/alanus2.txt"},
    "20":      {"author": None, "title": "Albertano of Brescia", "path": "albertanus/albertanus.arsloquendi.txt"},
    "21":      {"author": None, "title": "Albertano of Brescia ", "path": "albertanus/albertanus.liberconsol.txt"},
    "22":      {"author": None, "title": "Albertano of Brescia ", "path": "albertanus/albertanus.sermo.txt"},
    "23":      {"author": None, "title": "Albertano of Brescia ", "path": "albertanus/albertanus.sermo1.txt"},
    "24":      {"author": None, "title": "Albertano of Brescia ", "path": "albertanus/albertanus.sermo2.txt"},
    "25":      {"author": None, "title": "Albertano of Brescia ", "path": "albertanus/albertanus.sermo3.txt"},
    "26":      {"author": None, "title": "Albertano of Brescia ", "path": "albertanus/albertanus.sermo4.txt"},
    "27":      {"author": None, "title": "Albertano of Brescia ", "path": "albertanus/albertanus1.txt"},
    "28":      {"author": None, "title": "Albertano of Brescia ", "path": "albertanus/albertanus2.txt"},
    "29":      {"author": None, "title": "Albertano of Brescia ", "path": "albertanus/albertanus3.txt"},
    "30":      {"author": None, "title": "Albertano of Brescia ", "path": "albertanus/albertanus4.txt"}, "31": {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist1.txt"
    }, "32":   {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist10.txt"
    }, "33":   {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist11.txt"
    }, "34":   {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist12.txt"
    }, "35":   {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist2.txt"
    }, "36":   {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist3.txt"
    }, "37":   {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist4.txt"
    }, "38":   {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist5.txt"
    }, "39":   {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist6.txt"
    }, "40":   {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist7.txt"
    }, "41":   {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist8.txt"
    }, "42":   {
        "author": "Albert of Aix", "title": "Historia Hierosolymitanae expeditionis", "path": "albertofaix/hist9.txt"
    }, "43":   {"author": "[Fredugis]", "title": "Cella Alcuini", "path": "alcuin/cella.txt"},
    "44":      {"author": "Alcuin", "title": "Conflictus Veris et Hiemis", "path": "alcuin/conflictus.txt"},
    "45":      {"author": "Alcuin", "title": "Epitaphium", "path": "alcuin/epitaphium.txt"},
    "46":      {"author": "Alcuin", "title": "de Luscinia", "path": "alcuin/luscinia.txt"},
    "47":      {"author": "Alcuin", "title": "Propositiones ", "path": "alcuin/propos.txt"},
    "48":      {"author": "Alcuin", "title": "Letter of Recommendation", "path": "alcuin/rec.txt"},
    "49":      {"author": "Alcuin", "title": "Disputatio de Rhetorica", "path": "alcuin/rhetorica.txt"},
    "50":      {"author": "Alcuin", "title": "Sequentia de Sancto Michaele", "path": "alcuin/sequentia.txt"},
    "51":      {"author": "Alcuin", "title": "Versus de Cuculo", "path": "alcuin/versus.txt"},
    "52":      {"author": "Peter Alfonsi", "title": "Disciplina clericalis", "path": "alfonsi.disciplina.txt"},
    "53":      {"author": "Ambrosius", "title": "ad sororem Marcellinam", "path": "ambrose/epist.txt"},
    "54":      {"author": "Ambrosi", "title": "Epistulae Variae", "path": "ambrose/epistvaria.txt"},
    "55":      {"author": "Ambrosius", "title": "Hymni", "path": "ambrose/hymns.txt"},
    "56":      {"author": "Ambrosius", "title": "de Mysteriis", "path": "ambrose/mysteriis.txt"},
    "57":      {"author": "Ammianus", "title": "Liber XIV", "path": "ammianus/14.txt"},
    "58":      {"author": "Ammianus", "title": "Liber XV", "path": "ammianus/15.txt"},
    "59":      {"author": "Ammianus", "title": "Liber XVI", "path": "ammianus/16.txt"},
    "60":      {"author": "Ammianus", "title": "Liber XVII", "path": "ammianus/17.txt"},
    "61":      {"author": "Ammianus", "title": "Liber XVIII", "path": "ammianus/18.txt"},
    "62":      {"author": "Ammianus", "title": "Liber XIX", "path": "ammianus/19.txt"},
    "63":      {"author": "Ammianus", "title": "Liber XX", "path": "ammianus/20.txt"},
    "64":      {"author": "Ammianus", "title": "Liber XXI", "path": "ammianus/21.txt"},
    "65":      {"author": "Ammianus", "title": "Liber XXII", "path": "ammianus/22.txt"},
    "66":      {"author": "Ammianus", "title": "Liber XXIII", "path": "ammianus/23.txt"},
    "67":      {"author": "Ammianus", "title": "Liber XVIV", "path": "ammianus/24.txt"},
    "68":      {"author": "Ammianus", "title": "Liber XXV", "path": "ammianus/25.txt"},
    "69":      {"author": "Ammianus", "title": "Liber XXVI", "path": "ammianus/26.txt"},
    "70":      {"author": "Ammianus", "title": "Liber XXVII", "path": "ammianus/27.txt"},
    "71":      {"author": "Ammianus", "title": "Liber XXVIII", "path": "ammianus/28.txt"},
    "72":      {"author": "Ammianus", "title": "Liber XXIX", "path": "ammianus/29.txt"},
    "73":      {"author": "Ammianus", "title": "Liber XXX", "path": "ammianus/30.txt"},
    "74":      {"author": "Ammianus", "title": "Liber XXXI", "path": "ammianus/31.txt"},
    "75":      {"author": "Ampelius", "title": "Liber Memorialis", "path": "ampelius.txt"},
    "76":      {"author": None, "title": "Andecavis Abbas ", "path": "andecavis.txt"},
    "77":      {"author": None, "title": "Andreas of Bergoma", "path": "andreasbergoma.txt"},
    "78":      {"author": "Livius Andronicus", "title": "Odussia", "path": "andronicus.txt"},
    "79":      {"author": None, "title": "Angilbert", "path": "angilbert.txt"},
    "80":      {"author": None, "title": "Annesl Regni Francorum", "path": "annalesregnifrancorum.txt"},
    "81":      {"author": None, "title": "Annales Vedastini", "path": "annalesvedastini.txt"},
    "82":      {"author": None, "title": "Carmen de Martyrio Maccabaeorum", "path": "anon.deramis.txt"},
    "83":      {"author": None, "title": "Carmen de Martyrio Maccabaeorum", "path": "anon.martyrio.txt"},
    "84":      {"author": None, "title": "Anonymus Neveleti", "path": "anon.nev.txt"},
    "85":      {"author": None, "title": "Anselm", "path": "anselmepistula.txt"},
    "86":      {"author": None, "title": "Anselm", "path": "anselmproslogion.txt"},
    "87":      {"author": "Apicius", "title": "de Re Coquinaria Liber I", "path": "apicius/apicius1.txt"},
    "88":      {"author": "Apicius", "title": "de Re Coquinaria Liber II", "path": "apicius/apicius2.txt"},
    "89":      {"author": "Apicius", "title": "de Re Coquinaria Liber III", "path": "apicius/apicius3.txt"},
    "90":      {"author": "Apicius", "title": "de Re Coquinaria Liber IV", "path": "apicius/apicius4.txt"},
    "91":      {"author": "Apicius", "title": "de Re Coquinaria Liber V", "path": "apicius/apicius5.txt"},
    "92":      {"author": "Appendix Vergiliana", "title": "Aetna  ", "path": "appverg.aetna.txt"},
    "93":      {"author": "Appendix Vergiliana", "title": "Catalepton  ", "path": "appverg.catalepton.txt"},
    "94":      {"author": "Appendix Vergiliana", "title": "Ciris  ", "path": "appverg.ciris.txt"},
    "95":      {"author": None, "title": "Appendix Vergiliana", "path": "appvergcomp.txt"},
    "96":      {"author": "Appendix Vergiliana", "title": "Culex", "path": "appvergculex.txt"},
    "97":      {"author": "Apuleius", "title": "Apology", "path": "apuleius/apuleius.apol.txt"},
    "98":      {"author": "Apuleius", "title": "Cupid and Psyche", "path": "apuleius/apuleius.cupid.txt"},
    "99":      {"author": "Apuleius", "title": "de Deo Socratis", "path": "apuleius/apuleius.deosocratis.txt"},
    "100":     {"author": "Apuleius", "title": "de Dogmate Platonis I", "path": "apuleius/apuleius.dog1.txt"},
    "101":     {"author": "Apuleius", "title": "de Dogmate Platonis II", "path": "apuleius/apuleius.dog2.txt"},
    "102":     {"author": "Apuleius", "title": "Florida", "path": "apuleius/apuleius.florida.txt"},
    "103":     {"author": "Apuleius", "title": "de Mundo", "path": "apuleius/apuleius.mundo.txt"},
    "104":     {"author": "Metamorphoses", "title": "Liber I", "path": "apuleius/apuleius1.txt"},
    "105":     {"author": "Metamorphoses", "title": "Liber X", "path": "apuleius/apuleius10.txt"},
    "106":     {"author": "Metamorphoses", "title": "Liber XI", "path": "apuleius/apuleius11.txt"},
    "107":     {"author": "Metamorphoses", "title": "Liber II", "path": "apuleius/apuleius2.txt"},
    "108":     {"author": "Metamorphoses", "title": "Liber III", "path": "apuleius/apuleius3.txt"},
    "109":     {"author": "Metamorphoses", "title": "Liber IV", "path": "apuleius/apuleius4.txt"},
    "110":     {"author": "Metamorphoses", "title": "Liber V", "path": "apuleius/apuleius5.txt"},
    "111":     {"author": "Metamorphoses", "title": "Liber VI", "path": "apuleius/apuleius6.txt"},
    "112":     {"author": "Metamorphoses", "title": "Liber VII", "path": "apuleius/apuleius7.txt"},
    "113":     {"author": "Metamorphoses", "title": "Liber VIII", "path": "apuleius/apuleius8.txt"},
    "114":     {"author": "Metamorphoses", "title": "Liber IX", "path": "apuleius/apuleius9.txt"}, "115": {
        "author": "St. Thomas Aquinas",
        "title":  "Corpus Christi  CORPUS CHRISTI   Verbum supernum prodiens,  Nec Patris linquens dexteram, "
                  "Ad opus suum exiens,  Venit advitae vesperam. In mortem a discipulo  Suis tradendus aemulis, Prius in vitae "
                  "ferculo  Se tradidit discipulis. Quibus sub bina specie  Carnem dedit et sanguinem: Ut duplicis substantiae  "
                  "Totum cibaret hominem. Se nascens dedit socium,  Convescens in edulium, Se moriens in pretium,  Se regnans "
                  "dat in praemium. O Salutaris Hostia,  Quae caeli pandis ostium: Bella premunt hostilia,  Da robur, "
                  "fer auxilium. Uni trinoque Domino  Sit sempiterna gloria, Qui vitam sine termino  Nobis donet in patria. "
                  "Amen.  ",
        "path":   "aquinas/corpuschristi.txt"
    }, "116":  {"author": None, "title": "St. Thomas Aquinas De Ente et Essentia ", "path": "aquinas/ente.txt"},
    "117":     {"author": "St. Thomas Aquinas", "title": "Epistola de Modo Studendi ", "path": "aquinas/epist.txt"},
    "118":     {
        "author": "St. Thomas Aquinas", "title": "Expositio in Orationem Dominicam", "path": "aquinas/expositio.txt"
    }, "119":  {"author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars ", "path": "aquinas/p1.txt"},
    "120":     {"author": "St. Thomas Aquinas", "title": "De Principio Individuationis ", "path": "aquinas/princ.txt"},
    "121":     {"author": "St. Thomas Aquinas", "title": "Summa Theologica, Prologus ", "path": "aquinas/prologus.txt"},
    "122":     {"author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio I ", "path": "aquinas/q1.1.txt"},
    "123":     {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio X ", "path": "aquinas/q1.10.txt"
    }, "124":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XI ",
        "path":   "aquinas/q1.11.txt"
    }, "125":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XII ",
        "path":   "aquinas/q1.12.txt"
    }, "126":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XIII ",
        "path":   "aquinas/q1.13.txt"
    }, "127":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XIV ",
        "path":   "aquinas/q1.14.txt"
    }, "128":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XV ",
        "path":   "aquinas/q1.15.txt"
    }, "129":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XVI ",
        "path":   "aquinas/q1.16.txt"
    }, "130":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XVII ",
        "path":   "aquinas/q1.17.txt"
    }, "131":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XVIII ",
        "path":   "aquinas/q1.18.txt"
    }, "132":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XIX ",
        "path":   "aquinas/q1.19.txt"
    }, "133":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio II ", "path": "aquinas/q1.2.txt"
    }, "134":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XX ",
        "path":   "aquinas/q1.20.txt"
    }, "135":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXI ",
        "path":   "aquinas/q1.21.txt"
    }, "136":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXII ",
        "path":   "aquinas/q1.22.txt"
    }, "137":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXIII ",
        "path":   "aquinas/q1.23.txt"
    }, "138":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXIV ",
        "path":   "aquinas/q1.24.txt"
    }, "139":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXV ",
        "path":   "aquinas/q1.25.txt"
    }, "140":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXIVI ",
        "path":   "aquinas/q1.26.txt"
    }, "141":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXVII ",
        "path":   "aquinas/q1.27.txt"
    }, "142":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXVIII ",
        "path":   "aquinas/q1.28.txt"
    }, "143":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXIX ",
        "path":   "aquinas/q1.29.txt"
    }, "144":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio III ",
        "path":   "aquinas/q1.3.txt"
    }, "145":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXX ",
        "path":   "aquinas/q1.30.txt"
    }, "146":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXI ",
        "path":   "aquinas/q1.31.txt"
    }, "147":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXII ",
        "path":   "aquinas/q1.32.txt"
    }, "148":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXIII ",
        "path":   "aquinas/q1.33.txt"
    }, "149":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXIV ",
        "path":   "aquinas/q1.34.txt"
    }, "150":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXV ",
        "path":   "aquinas/q1.35.txt"
    }, "151":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXVI ",
        "path":   "aquinas/q1.36.txt"
    }, "152":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXVII ",
        "path":   "aquinas/q1.37.txt"
    }, "153":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXVIII ",
        "path":   "aquinas/q1.38.txt"
    }, "154":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XXXIX ",
        "path":   "aquinas/q1.39.txt"
    }, "155":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio IV ", "path": "aquinas/q1.4.txt"
    }, "156":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XL ",
        "path":   "aquinas/q1.40.txt"
    }, "157":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLI ",
        "path":   "aquinas/q1.41.txt"
    }, "158":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLII ",
        "path":   "aquinas/q1.42.txt"
    }, "159":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLIII ",
        "path":   "aquinas/q1.43.txt"
    }, "160":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLIV ",
        "path":   "aquinas/q1.44.txt"
    }, "161":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLV ",
        "path":   "aquinas/q1.45.txt"
    }, "162":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLVI ",
        "path":   "aquinas/q1.46.txt"
    }, "163":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLVII ",
        "path":   "aquinas/q1.47.txt"
    }, "164":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLVIII ",
        "path":   "aquinas/q1.48.txt"
    }, "165":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio XLIX ",
        "path":   "aquinas/q1.49.txt"
    }, "166":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio V ", "path": "aquinas/q1.5.txt"
    }, "167":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio L ", "path": "aquinas/q1.50.txt"
    }, "168":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LI ",
        "path":   "aquinas/q1.51.txt"
    }, "169":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LII ",
        "path":   "aquinas/q1.52.txt"
    }, "170":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LIII ",
        "path":   "aquinas/q1.53.txt"
    }, "171":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LIV ",
        "path":   "aquinas/q1.54.txt"
    }, "172":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LV ",
        "path":   "aquinas/q1.55.txt"
    }, "173":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LVI ",
        "path":   "aquinas/q1.56.txt"
    }, "174":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio LIVII ",
        "path":   "aquinas/q1.57.txt"
    }, "175":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LVIII ", "path": "aquinas/q1.58.txt"
    }, "176":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LIX ", "path": "aquinas/q1.59.txt"
    }, "177":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio VI ", "path": "aquinas/q1.6.txt"
    }, "178":  {"author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LX ", "path": "aquinas/q1.60.txt"},
    "179":     {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXI ", "path": "aquinas/q1.61.txt"
    }, "180":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXII ", "path": "aquinas/q1.62.txt"
    }, "181":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXIII ", "path": "aquinas/q1.63.txt"
    }, "182":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXIV ", "path": "aquinas/q1.64.txt"
    }, "183":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXV ", "path": "aquinas/q1.65.txt"
    }, "184":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXVI ", "path": "aquinas/q1.66.txt"
    }, "185":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXVII ", "path": "aquinas/q1.67.txt"
    }, "186":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXVIII ", "path": "aquinas/q1.68.txt"
    }, "187":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXIX ", "path": "aquinas/q1.69.txt"
    }, "188":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio VII ",
        "path":   "aquinas/q1.7.txt"
    }, "189":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXX ", "path": "aquinas/q1.70.txt"
    }, "190":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXI ", "path": "aquinas/q1.71.txt"
    }, "191":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXII ", "path": "aquinas/q1.72.txt"
    }, "192":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXIII ", "path": "aquinas/q1.73.txt"
    }, "193":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXIV ", "path": "aquinas/q1.74.txt"
    }, "194":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio VIII ",
        "path":   "aquinas/q1.8.txt"
    }, "195":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXX ", "path": "aquinas/q1.80.txt"
    }, "196":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXXI ", "path": "aquinas/q1.81.txt"
    }, "197":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXXII ", "path": "aquinas/q1.82.txt"
    }, "198":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXXIII ", "path": "aquinas/q1.83.txt"
    }, "199":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXXVI ", "path": "aquinas/q1.86.txt"
    }, "200":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Quaestio LXXXVII ", "path": "aquinas/q1.87.txt"
    }, "201":  {
        "author": "St. Thomas Aquinas", "title": "Summa Theologica, Prima Pars Quaestio IX ", "path": "aquinas/q1.9.txt"
    }, "202":  {"author": None, "title": "Declaration of Arbroath", "path": "arbroath.txt"},
    "203":     {"author": None, "title": "Archpoeta", "path": "archpoet.txt"},
    "204":     {"author": "Arnobius", "title": "Adversus Nationes Liber I", "path": "arnobius/arnobius1.txt"},
    "205":     {"author": "Arnobius", "title": "Adversus Nationes Liber II", "path": "arnobius/arnobius2.txt"},
    "206":     {"author": "Arnobius", "title": "Adversus Nationes Liber III", "path": "arnobius/arnobius3.txt"},
    "207":     {"author": "Arnobius", "title": "Adversus Nationes Liber IV", "path": "arnobius/arnobius4.txt"},
    "208":     {"author": "Arnobius", "title": "Adversus Nationes Liber V", "path": "arnobius/arnobius5.txt"},
    "209":     {"author": "Arnobius", "title": "Adversus Nationes Liber VI", "path": "arnobius/arnobius6.txt"},
    "210":     {"author": "Arnobius", "title": "Adversus Nationes Liber VII", "path": "arnobius/arnobius7.txt"},
    "211":     {"author": "Arnulf of Lisieux", "title": "De Nativitate Domini", "path": "arnulf.txt"},
    "212":     {"author": None, "title": "Asconius", "path": "asconius.txt"},
    "213":     {"author": "Asserius", "title": "Life of Alfred", "path": "asserius.txt"},
    "214":     {"author": "Augustinus", "title": "de Catechizandis Rudibus", "path": "augustine/catechizandis.txt"},
    "215":     {"author": "Augustine", "title": "De Civitate Dei Liber I", "path": "augustine/civ1.txt"},
    "216":     {"author": "Augustine", "title": "De Civitate Dei Liber X", "path": "augustine/civ10.txt"},
    "217":     {"author": "Augustine", "title": "De Civitate Dei Liber XI", "path": "augustine/civ11.txt"},
    "218":     {"author": "Augustine", "title": "De Civitate Dei Liber XII", "path": "augustine/civ12.txt"},
    "219":     {"author": "Augustine", "title": "De Civitate Dei Liber XIII", "path": "augustine/civ13.txt"},
    "220":     {"author": "Augustine", "title": "De Civitate Dei Liber XIV", "path": "augustine/civ14.txt"},
    "221":     {"author": "Augustine", "title": "De Civitate Dei Liber XV", "path": "augustine/civ15.txt"},
    "222":     {"author": "Augustine", "title": "De Civitate Dei Liber XVI", "path": "augustine/civ16.txt"},
    "223":     {"author": "Augustine", "title": "De Civitate Dei Liber XVII", "path": "augustine/civ17.txt"},
    "224":     {"author": "Augustine", "title": "De Civitate Dei Liber XVIII", "path": "augustine/civ18.txt"},
    "225":     {"author": "Augustine", "title": "De Civitate Dei Liber XIX", "path": "augustine/civ19.txt"},
    "226":     {"author": "Augustine", "title": "De Civitate Dei Liber II", "path": "augustine/civ2.txt"},
    "227":     {"author": "Augustine", "title": "De Civitate Dei Liber XX", "path": "augustine/civ20.txt"},
    "228":     {"author": "Augustine", "title": "De Civitate Dei Liber XXI", "path": "augustine/civ21.txt"},
    "229":     {"author": "Augustine", "title": "De Civitate Dei Liber XXII", "path": "augustine/civ22.txt"},
    "230":     {"author": "Augustine", "title": "De Civitate Dei Liber III", "path": "augustine/civ3.txt"},
    "231":     {"author": "Augustine", "title": "De Civitate Dei Liber IV", "path": "augustine/civ4.txt"},
    "232":     {"author": "Augustine", "title": "De Civitate Dei Liber V", "path": "augustine/civ5.txt"},
    "233":     {"author": "Augustine", "title": "De Civitate Dei Liber VI", "path": "augustine/civ6.txt"},
    "234":     {"author": "Augustine", "title": "De Civitate Dei Liber VII", "path": "augustine/civ7.txt"},
    "235":     {"author": "Augustine", "title": "De Civitate Dei Liber VIII", "path": "augustine/civ8.txt"},
    "236":     {"author": "Augustine", "title": "De Civitate Dei Liber IX", "path": "augustine/civ9.txt"},
    "237":     {"author": "Augustine", "title": "Confessions I", "path": "augustine/conf1.txt"},
    "238":     {"author": "Augustine", "title": "Confessions X", "path": "augustine/conf10.txt"},
    "239":     {"author": "Augustine", "title": "Confessions XI", "path": "augustine/conf11.txt"},
    "240":     {"author": "Augustine", "title": "Confessions XII", "path": "augustine/conf12.txt"},
    "241":     {"author": "Augustine", "title": "Confessions XIII", "path": "augustine/conf13.txt"},
    "242":     {"author": "Augustine", "title": "Confessions II", "path": "augustine/conf2.txt"},
    "243":     {"author": "Augustine", "title": "Confessions III", "path": "augustine/conf3.txt"},
    "244":     {"author": "Augustine", "title": "Confessions IV", "path": "augustine/conf4.txt"},
    "245":     {"author": "Augustine", "title": "Confessions V", "path": "augustine/conf5.txt"},
    "246":     {"author": "Augustine", "title": "Confessions VI", "path": "augustine/conf6.txt"},
    "247":     {"author": "Augustine", "title": "Confessions VII", "path": "augustine/conf7.txt"},
    "248":     {"author": "Augustine", "title": "Confessions VIII", "path": "augustine/conf8.txt"},
    "249":     {"author": "Augustine", "title": "Confessions IX", "path": "augustine/conf9.txt"},
    "250":     {"author": "Augustine", "title": "de Dialectica", "path": "augustine/dia.txt"},
    "251":     {"author": None, "title": "Augustine", "path": "augustine/epistula.txt"},
    "252":     {"author": "Augustine", "title": "de Fide et Symbolo", "path": "augustine/fide.txt"},
    "253":     {"author": None, "title": "St. Augustine", "path": "augustine/iulianus1.txt"},
    "254":     {"author": None, "title": "St. Augustine", "path": "augustine/iulianus2.txt"},
    "255":     {"author": None, "title": "Rule of St. Augustine", "path": "augustine/reg.txt"},
    "256":     {"author": "Augustine", "title": "Sermon 1", "path": "augustine/serm1.txt"},
    "257":     {"author": "Augustine", "title": "Sermon 10", "path": "augustine/serm10.txt"},
    "258":     {"author": "Augustine", "title": "Sermon 11", "path": "augustine/serm11.txt"},
    "259":     {"author": "Augustine", "title": "Sermon 12", "path": "augustine/serm12.txt"},
    "260":     {"author": "Augustine", "title": "Sermon 13", "path": "augustine/serm13.txt"},
    "261":     {"author": "Augustine", "title": "Sermon 14", "path": "augustine/serm14.txt"},
    "262":     {"author": "Augustine", "title": "Sermon 15", "path": "augustine/serm15.txt"},
    "263":     {"author": "Augustine", "title": "Sermon 16", "path": "augustine/serm16.txt"},
    "264":     {"author": "Augustine", "title": "Sermon 17", "path": "augustine/serm17.txt"},
    "265":     {"author": "Augustine", "title": "Sermon 18", "path": "augustine/serm18.txt"},
    "266":     {"author": "Augustine", "title": "Sermon 19", "path": "augustine/serm19.txt"},
    "267":     {"author": "Augustine", "title": "Sermon 2", "path": "augustine/serm2.txt"},
    "268":     {"author": "Augustine", "title": "Sermon 20", "path": "augustine/serm20.txt"},
    "269":     {"author": "Augustine", "title": "Sermon 4", "path": "augustine/serm4.txt"},
    "270":     {"author": "Augustine", "title": "Sermon 5", "path": "augustine/serm5.txt"},
    "271":     {"author": "Augustine", "title": "Sermon 6", "path": "augustine/serm6.txt"},
    "272":     {"author": "Augustine", "title": "Sermon 7", "path": "augustine/serm7.txt"},
    "273":     {"author": "Augustine", "title": "Sermon 71", "path": "augustine/serm71.txt"},
    "274":     {"author": "Augustine", "title": "Sermon 72", "path": "augustine/serm72.txt"},
    "275":     {"author": "Augustine", "title": "Sermon 73", "path": "augustine/serm73.txt"},
    "276":     {"author": "Augustine", "title": "Sermon 74", "path": "augustine/serm74.txt"},
    "277":     {"author": "Augustine", "title": "Sermon 75", "path": "augustine/serm75.txt"},
    "278":     {"author": "Augustine", "title": "Sermon 76", "path": "augustine/serm76.txt"},
    "279":     {"author": "Augustine", "title": "Sermon 77", "path": "augustine/serm77.txt"},
    "280":     {"author": "Augustine", "title": "Sermon 78", "path": "augustine/serm78.txt"},
    "281":     {"author": "Augustine", "title": "Sermon 79", "path": "augustine/serm79.txt"},
    "282":     {"author": "Augustine", "title": "Sermon 8", "path": "augustine/serm8.txt"},
    "283":     {"author": "Augustine", "title": "Sermon 80", "path": "augustine/serm80.txt"},
    "284":     {"author": "Augustine", "title": "Sermon 81", "path": "augustine/serm81.txt"},
    "285":     {"author": "Augustine", "title": "Sermon 82", "path": "augustine/serm82.txt"},
    "286":     {"author": "Augustine", "title": "Sermon 83", "path": "augustine/serm83.txt"},
    "287":     {"author": "Augustine", "title": "Sermon 87", "path": "augustine/serm87.txt"},
    "288":     {"author": "Augustine", "title": "Sermon 88", "path": "augustine/serm88.txt"},
    "289":     {"author": "Augustine", "title": "Sermon 9", "path": "augustine/serm9.txt"},
    "290":     {"author": "Augustine", "title": "Sermon 90", "path": "augustine/serm90.txt"},
    "291":     {"author": "Augustine", "title": "Sermon 92", "path": "augustine/serm92.txt"},
    "292":     {"author": "Augustine", "title": "Sermon 95", "path": "augustine/serm95.txt"},
    "293":     {"author": "Augustine", "title": "Sermon 99", "path": "augustine/serm99.txt"},
    "294":     {"author": "Augustinus", "title": "de Trinitate Liber I", "path": "augustine/trin1.txt"},
    "295":     {"author": "Augustinus", "title": "de Trinitate Liber X", "path": "augustine/trin10.txt"},
    "296":     {"author": "Augustinus", "title": "de Trinitate Liber XI", "path": "augustine/trin11.txt"},
    "297":     {"author": "Augustinus", "title": "de Trinitate Liber XII", "path": "augustine/trin12.txt"},
    "298":     {"author": "Augustinus", "title": "de Trinitate Liber XIII", "path": "augustine/trin13.txt"},
    "299":     {"author": "Augustinus", "title": "de Trinitate Liber XIV", "path": "augustine/trin14.txt"},
    "300":     {"author": "Augustinus", "title": "de Trinitate Liber XV", "path": "augustine/trin15.txt"},
    "301":     {"author": "Augustinus", "title": "de Trinitate Liber II", "path": "augustine/trin2.txt"},
    "302":     {"author": "Augustinus", "title": "de Trinitate Liber III", "path": "augustine/trin3.txt"},
    "303":     {"author": "Augustinus", "title": "de Trinitate Liber IV", "path": "augustine/trin4.txt"},
    "304":     {"author": "Augustinus", "title": "de Trinitate Liber V", "path": "augustine/trin5.txt"},
    "305":     {"author": "Augustinus", "title": "de Trinitate Liber VI", "path": "augustine/trin6.txt"},
    "306":     {"author": "Augustinus", "title": "de Trinitate Liber VII", "path": "augustine/trin7.txt"},
    "307":     {"author": "Augustinus", "title": "de Trinitate Liber VIII", "path": "augustine/trin8.txt"},
    "308":     {"author": "Augustinus", "title": "de Trinitate Liber IX", "path": "augustine/trin9.txt"},
    "309":     {"author": "Ausonius", "title": "Mosella", "path": "aus.mos.txt"},
    "310":     {"author": "Ausonius", "title": "Septem Sapientum Sententiae", "path": "aus.sept.sent.txt"},
    "311":     {"author": None, "title": "Phoenix", "path": "ave.phoen.txt"},
    "312":     {"author": "Avianus", "title": "Fabulae", "path": "avianus.txt"},
    "313":     {"author": "Avienus", "title": "Ora Maritima", "path": "avienus.ora.txt"},
    "314":     {"author": "Avienus", "title": "Periegesis", "path": "avienus.periegesis.txt"},
    "315":     {"author": None, "title": "Pseudo-Plato ", "path": "axio.txt"},
    "316":     {"author": "Bacon", "title": "Distributio", "path": "bacon/bacon.distributio.txt"},
    "317":     {"author": "Bacon", "title": "Epistola", "path": "bacon/bacon.epistola.txt"},
    "318":     {"author": "Bacon", "title": "History of the Reign of Henry VII", "path": "bacon/bacon.hist1.txt"},
    "319":     {"author": "Bacon", "title": "History of the Reign of Henry VII", "path": "bacon/bacon.hist10.txt"},
    "320":     {"author": "Bacon", "title": "History of the Reign of Henry VII", "path": "bacon/bacon.hist11.txt"},
    "321":     {"author": "Bacon", "title": "History of the Reign of Henry VII", "path": "bacon/bacon.hist2.txt"},
    "322":     {"author": "Bacon", "title": "History of the Reign of Henry VII", "path": "bacon/bacon.hist3.txt"},
    "323":     {"author": "Bacon", "title": "History of the Reign of Henry VII", "path": "bacon/bacon.hist4.txt"},
    "324":     {"author": "Bacon", "title": "History of the Reign of Henry VII", "path": "bacon/bacon.hist5.txt"},
    "325":     {"author": "Bacon", "title": "History of the Reign of Henry VII", "path": "bacon/bacon.hist6.txt"},
    "326":     {"author": "Bacon", "title": "History of the Reign of Henry VII", "path": "bacon/bacon.hist7.txt"},
    "327":     {"author": "Bacon", "title": "History of the Reign of Henry VII", "path": "bacon/bacon.hist8.txt"},
    "328":     {"author": "Bacon", "title": "History of the Reign of Henry VII", "path": "bacon/bacon.hist9.txt"},
    "329":     {"author": "Bacon", "title": "Introduction", "path": "bacon/bacon.intro.txt"},
    "330":     {"author": "Bacon", "title": "Liber Primus", "path": "bacon/bacon.liber1.txt"},
    "331":     {"author": "Bacon", "title": "Liber Secundus", "path": "bacon/bacon.liber2.txt"},
    "332":     {"author": "Bacon", "title": "Praefatio", "path": "bacon/bacon.praefatio.txt"},
    "333":     {"author": "Bacon", "title": "Praefatio ", "path": "bacon/bacon.praefatio2.txt"}, "334": {
        "author": "Francis Bacon", "title": "Sermones Fideles sive Interiora Rerum", "path": "bacon/bacon.sermones.txt"
    }, "335":  {"author": "Bacon", "title": "Title Page", "path": "bacon/bacon.titlepage.txt"},
    "336":     {"author": None, "title": "Balbus", "path": "balbus.txt"},
    "337":     {"author": "Balde", "title": "Melancholia", "path": "balde1.txt"},
    "338":     {"author": "Balde", "title": "Ad Iulium Orstenam de more unguendorum cadaverum", "path": "balde2.txt"},
    "339":     {"author": "Baldo", "title": "Novus Aesopus", "path": "baldo.txt"},
    "340":     {"author": "Bebel", "title": "Liber Facetiarum", "path": "bebel.txt"},
    "341":     {"author": "Bede", "title": "Book I", "path": "bede/bede1.txt"},
    "342":     {"author": "Bede", "title": "Book II", "path": "bede/bede2.txt"},
    "343":     {"author": "Bede", "title": "Book III", "path": "bede/bede3.txt"},
    "344":     {"author": "Bede", "title": "Book IV", "path": "bede/bede4.txt"},
    "345":     {"author": "Bede", "title": "Book V", "path": "bede/bede5.txt"},
    "346":     {"author": "[Bede", "title": "Continuatio]", "path": "bede/bedecontinuatio.txt"},
    "347":     {"author": "Bede", "title": "Praefatio", "path": "bede/bedepraef.txt"},
    "348":     {"author": "Psuedo-Bede", "title": "Proverbs", "path": "bede/bedeproverbs.txt"},
    "349":     {"author": None, "title": "Rule of St. Benedict", "path": "benedict.txt"},
    "350":     {"author": "Berengar", "title": "Apologeticus", "path": "berengar.txt"},
    "351":     {"author": "Bernard of Cluny", "title": "De contemptu mundi I", "path": "bernardcluny1.txt"},
    "352":     {"author": "Bernard of Cluny", "title": "De contemptu mundi II", "path": "bernardcluny2.txt"},
    "353":     {"author": "Vulgate", "title": "Acts", "path": "bible/acts.txt"},
    "354":     {"author": "Vulgate", "title": "Amos ", "path": "bible/amos.txt"},
    "355":     {"author": "Vulgate", "title": "Baruch ", "path": "bible/baruch.txt"},
    "356":     {"author": "Vulgate", "title": "First Chronicles ", "path": "bible/chronicles1.txt"},
    "357":     {"author": "Vulgate", "title": "Second Chronicles ", "path": "bible/chronicles2.txt"},
    "358":     {"author": "Vulgate", "title": "Paul to the Colossians ", "path": "bible/colossians.txt"},
    "359":     {"author": "Vulgate", "title": "Paul to the Corinthians I ", "path": "bible/corinthians1.txt"},
    "360":     {"author": "Vulgate", "title": "Paul to the Corinthians II ", "path": "bible/corinthians2.txt"},
    "361":     {"author": "Vulgate", "title": "Daniel ", "path": "bible/daniel.txt"},
    "362":     {"author": "Vulgate", "title": "Deuteronomy ", "path": "bible/deuteronomy.txt"},
    "363":     {"author": "Vulgate", "title": "Ecclesiastes ", "path": "bible/ecclesiastes.txt"},
    "364":     {"author": "Vulgate", "title": "Paul to the Ephesians ", "path": "bible/ephesians.txt"},
    "365":     {"author": "Vulgate", "title": "First Book of Esdras ", "path": "bible/esdras1.txt"},
    "366":     {"author": "Vulgate", "title": "Second Book of Esdras ", "path": "bible/esdras2.txt"},
    "367":     {"author": "Vulgate", "title": "Esther ", "path": "bible/esther.txt"},
    "368":     {"author": "Vulgate", "title": "Exodus", "path": "bible/exodus.txt"},
    "369":     {"author": "Vulgate", "title": "Ezekiel ", "path": "bible/ezekiel.txt"},
    "370":     {"author": "Vulgate", "title": "Ezra ", "path": "bible/ezra.txt"},
    "371":     {"author": "Vulgate", "title": "Paul to the Galatians ", "path": "bible/galatians.txt"},
    "372":     {"author": "Vulgate", "title": "Genesis", "path": "bible/genesis.txt"},
    "373":     {"author": "Vulgate", "title": "Habakkuk ", "path": "bible/habakkuk.txt"},
    "374":     {"author": "Vulgate", "title": "Haggai ", "path": "bible/haggai.txt"},
    "375":     {"author": "Vulgate", "title": "Letter to Hebrews ", "path": "bible/hebrews.txt"},
    "376":     {"author": "Vulgate", "title": "Hosea ", "path": "bible/hosea.txt"},
    "377":     {"author": "Vulgate", "title": "Isaiah ", "path": "bible/isaiah.txt"},
    "378":     {"author": "Vulgate", "title": "A Letter to James ", "path": "bible/james.txt"},
    "379":     {"author": "Vulgate", "title": "Jeremiah ", "path": "bible/jeremiah.txt"},
    "380":     {"author": "Vulgate", "title": "Job ", "path": "bible/job.txt"},
    "381":     {"author": "Vulgate", "title": "Joel ", "path": "bible/joel.txt"},
    "382":     {"author": "Vulgate", "title": "John ", "path": "bible/john.txt"},
    "383":     {"author": None, "title": "John 1 ", "path": "bible/john1.txt"},
    "384":     {"author": None, "title": "John 2 ", "path": "bible/john2.txt"},
    "385":     {"author": None, "title": "John 3 ", "path": "bible/john3.txt"},
    "386":     {"author": "Vulgate", "title": "Jonah ", "path": "bible/jonah.txt"},
    "387":     {"author": "Vulgate", "title": "Joshua ", "path": "bible/joshua.txt"},
    "388":     {"author": "Vulgate", "title": "Letter of Jude ", "path": "bible/jude.txt"},
    "389":     {"author": "Vulgate", "title": "Judges ", "path": "bible/judges.txt"},
    "390":     {"author": "Vulgate", "title": "Judith ", "path": "bible/judith.txt"},
    "391":     {"author": "Vulgate", "title": "Kings I ", "path": "bible/kings1.txt"},
    "392":     {"author": "Vulgate", "title": "Kings II ", "path": "bible/kings2.txt"},
    "393":     {"author": "Vulgate", "title": "Lamentations ", "path": "bible/lamentations.txt"},
    "394":     {"author": "Vulgate", "title": "Leviticus ", "path": "bible/leviticus.txt"},
    "395":     {"author": "Vulgate", "title": "Luke ", "path": "bible/luke.txt"},
    "396":     {"author": "Vulgate", "title": "First Book of Macabees ", "path": "bible/macabees1.txt"},
    "397":     {"author": "Vulgate", "title": "Second Book of Macabees ", "path": "bible/macabees2.txt"},
    "398":     {"author": "Vulgate", "title": "Malachias ", "path": "bible/malachias.txt"},
    "399":     {"author": "Vulgate", "title": "Prayer of Manasses ", "path": "bible/manasses.txt"},
    "400":     {"author": None, "title": "Gospel of Mark ", "path": "bible/mark.txt"},
    "401":     {"author": ">Vulgate", "title": "Matthew", "path": "bible/matthew.txt"},
    "402":     {"author": "Vulgate", "title": "Micah ", "path": "bible/micah.txt"},
    "403":     {"author": "Vulgate", "title": "Nahum ", "path": "bible/nahum.txt"},
    "404":     {"author": "Vulgate", "title": "Nehemiah ", "path": "bible/nehemiah.txt"},
    "405":     {"author": "Vulgate", "title": "Numbers ", "path": "bible/numbers.txt"},
    "406":     {"author": "Vulgate", "title": "Obadiah ", "path": "bible/obadiah.txt"},
    "407":     {"author": "Vulgate", "title": "First Letter of Peter ", "path": "bible/peter1.txt"},
    "408":     {"author": "Vulgate", "title": "Second Letter of Peter ", "path": "bible/peter2.txt"},
    "409":     {"author": "Vulgate", "title": "Paul to Philemon ", "path": "bible/philemon.txt"},
    "410":     {"author": None, "title": "Epistula ad Philippenses ", "path": "bible/philip.txt"},
    "411":     {"author": None, "title": "The Bible", "path": "bible/prologi.txt"},
    "412":     {"author": "Vulgate", "title": "Proverbs ", "path": "bible/proverbs.txt"},
    "413":     {"author": "Vulgate", "title": "Psalms", "path": "bible/psalms.txt"},
    "414":     {"author": "Vulgate", "title": "Revelation of John ", "path": "bible/revelation.txt"},
    "415":     {"author": "Vulgate", "title": "Paul to the Romans ", "path": "bible/romans.txt"},
    "416":     {"author": "Vulgate", "title": "Ruth ", "path": "bible/ruth.txt"},
    "417":     {"author": "Vulgate", "title": "Samuel ", "path": "bible/samuel1.txt"},
    "418":     {"author": "Vulgate", "title": "Second Samuel ", "path": "bible/samuel2.txt"},
    "419":     {"author": "Vulgate", "title": "Sirach ", "path": "bible/sirach.txt"},
    "420":     {"author": "Vulgate", "title": "Song of Songs ", "path": "bible/songofsongs.txt"},
    "421":     {"author": "Vulgate", "title": "Paul to the Thessalonians I ", "path": "bible/thessalonians1.txt"},
    "422":     {"author": "Vulgate", "title": "Paul to the Thessalonians II ", "path": "bible/thessalonians2.txt"},
    "423":     {"author": "Vulgate", "title": "Paul to Timothy I ", "path": "bible/timothy1.txt"},
    "424":     {"author": "Vulgate", "title": "Paul to Timothy II ", "path": "bible/timothy2.txt"},
    "425":     {"author": None, "title": "Epistula ad Titum ", "path": "bible/titum.txt"},
    "426":     {"author": "Vulgate", "title": "Tobias ", "path": "bible/tobia.txt"},
    "427":     {"author": "Vulgate", "title": "Wisdom ", "path": "bible/wisdom.txt"},
    "428":     {"author": "Vulgate", "title": "Zacharias ", "path": "bible/zacharias.txt"},
    "429":     {"author": "Vulgate", "title": "Zephaniah ", "path": "bible/zephaniah.txt"},
    "430":     {"author": "Bigges", "title": "Expeditio Francisci Draki Equitis Angli", "path": "biggs.txt"},
    "431":     {"author": None, "title": "Bill of Rights", "path": "bill.rights.txt"},
    "432":     {"author": None, "title": "Petrus Blesensis", "path": "blesensis.txt"},
    "433":     {"author": None, "title": "Boethius de Dacia", "path": "boethiusdacia/deaeternitate.txt"},
    "434":     {"author": None, "title": "Boethius de Dacia", "path": "boethiusdacia/desummobono.txt"},
    "435":     {"author": None, "title": "St. Bonaventure", "path": "bonaventura.itinerarium.txt"},
    "436":     {"author": None, "title": "Bartolomej Boskovic", "path": "boskovic.txt"},
    "437":     {"author": None, "title": "Breve Chronicon Northmannicum", "path": "brevechronicon.txt"},
    "438":     {"author": "Buchanan", "title": "de Maria Scotorum Regina", "path": "buchanan.txt"},
    "439":     {"author": "Bultelius", "title": "Ad Noctem", "path": "bultelius/bultelius1.txt"},
    "440":     {"author": "Bultelius", "title": "Somnium", "path": "bultelius/bultelius2.txt"},
    "441":     {"author": None, "title": "Pseudo-Caecilius Balbus", "path": "caeciliusbalbus.txt"},
    "442":     {"author": None, "title": "INCERTI AVCTORIS DE BELLO ALEXANDRINO LIBER", "path": "caesar/alex.txt"},
    "443":     {
        "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO CIVILI LIBER PRIMVS",
        "path":   "caesar/bc1.txt"
    }, "444":  {
        "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO CIVILI LIBER SECVNDVS",
        "path":   "caesar/bc2.txt"
    }, "445":  {"author": None, "title": "", "path": "caesar/bc3.txt"},
    "446":     {"author": None, "title": "INCERTI AVCTORIS DE BELLO AFRICO LIBER", "path": "caesar/bellafr.txt"},
    "447":     {
        "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER PRIMUS",
        "path":   "caesar/gall1.txt"
    }, "448":  {
        "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER SECVNDVS",
        "path":   "caesar/gall2.txt"
    }, "449":  {
        "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER TERTIVS",
        "path":   "caesar/gall3.txt"
    }, "450":  {
        "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER QVARTVS",
        "path":   "caesar/gall4.txt"
    }, "451":  {
        "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER QVINTVS",
        "path":   "caesar/gall5.txt"
    }, "452":  {
        "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER SEXTVS",
        "path":   "caesar/gall6.txt"
    }, "453":  {
        "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER SEPTIMVS",
        "path":   "caesar/gall7.txt"
    }, "454":  {
        "author": None, "title": "C. IVLI CAESARIS COMMENTARIORVM DE BELLO GALLICO LIBER OCTAVVS",
        "path":   "caesar/gall8.txt"
    }, "455":  {"author": None, "title": "INCERTI AVCTORIS DE BELLO HISPANIENSI LIBER", "path": "caesar/hisp.txt"},
    "456":     {"author": "Calpurnius Flaccus", "title": "Declamationes", "path": "calpurniusflaccus.txt"},
    "457":     {"author": None, "title": "T. Calpunius Siculus", "path": "calpurniussiculus.txt"},
    "458":     {"author": "Campion", "title": "Elegies", "path": "campion/campion.elegies.txt"},
    "459":     {"author": "Campion", "title": "Epigrams I", "path": "campion/campion.epigr1.txt"},
    "460":     {"author": "Campion", "title": "Epigrams II", "path": "campion/campion.epigr2.txt"},
    "461":     {"author": "Campion", "title": "Miscellaneous Poetry", "path": "campion/campion.misc.txt"},
    "462":     {"author": "Campion", "title": "De Pulverea Coniuratione I", "path": "campion/campion.plot1.txt"},
    "463":     {"author": "Campion", "title": "De Pulverea Coniuratione II", "path": "campion/campion.plot2.txt"},
    "464":     {"author": "Campion", "title": "Ad Thamesin", "path": "campion/campion.thamesin.txt"},
    "465":     {"author": "Campion", "title": "Umbra", "path": "campion/campion.umbra.txt"},
    "466":     {"author": "Andreas Capellanus", "title": "de Amore I", "path": "capellanus/capellanus1.txt"},
    "467":     {"author": "Andreas Capellanus", "title": "de Amore II", "path": "capellanus/capellanus2.txt"},
    "468":     {"author": "Andreas Capellanus", "title": "de Amore III", "path": "capellanus/capellanus3.txt"},
    "469":     {"author": None, "title": "Carmina Burana ", "path": "carm.bur.txt"},
    "470":     {"author": None, "title": "Carmen Arvale", "path": "carmenarvale.txt"},
    "471":     {"author": None, "title": "CARMEN IN VICTORIAM PISANORUM", "path": "carmeninvictoriam.txt"},
    "472":     {"author": None, "title": "Carmen Saliare", "path": "carmensaliare.txt"},
    "473":     {"author": "Cassiodorus", "title": "de Anima", "path": "cassiodorus/anima.txt"},
    "474":     {"author": "Cassiodorus", "title": "Variae", "path": "cassiodorus/epist.txt"},
    "475":     {"author": "Cassiodorus", "title": "de Musica", "path": "cassiodorus/musica.txt"},
    "476":     {"author": "Cassiodorus", "title": "Orationes", "path": "cassiodorus/orationes.txt"},
    "477":     {"author": "Cassiodorus", "title": "Variae, Praefatio", "path": "cassiodorus/varia.praef.txt"},
    "478":     {"author": "Cassiodorus", "title": "Variae I", "path": "cassiodorus/varia1.txt"},
    "479":     {"author": "Cassiodorus", "title": "Variae X", "path": "cassiodorus/varia10.txt"},
    "480":     {"author": "Cassiodorus", "title": "Variae XI", "path": "cassiodorus/varia11.txt"},
    "481":     {"author": "Cassiodorus", "title": "Variae XII", "path": "cassiodorus/varia12.txt"},
    "482":     {"author": "Cassiodorus", "title": "Variae II", "path": "cassiodorus/varia2.txt"},
    "483":     {"author": "Cassiodorus", "title": "Variae III", "path": "cassiodorus/varia3.txt"},
    "484":     {"author": "Cassiodorus", "title": "Variae IV", "path": "cassiodorus/varia4.txt"},
    "485":     {"author": "Cassiodorus", "title": "Variae V", "path": "cassiodorus/varia5.txt"},
    "486":     {"author": "Cassiodorus", "title": "Variae VI", "path": "cassiodorus/varia6.txt"},
    "487":     {"author": "Cassiodorus", "title": "Variae VII", "path": "cassiodorus/varia7.txt"},
    "488":     {"author": "Cassiodorus", "title": "Variae VIII", "path": "cassiodorus/varia8.txt"},
    "489":     {"author": "Cassiodorus", "title": "Variae IX", "path": "cassiodorus/varia9.txt"},
    "490":     {"author": None, "title": "Catalogue Lib\u00e9rien", "path": "catalogueliberien.txt"},
    "491":     {"author": "[Cato]", "title": "Disticha Catonis", "path": "cato.dis.txt"},
    "492":     {"author": "Cato", "title": "DE AGRI CVLTVRA", "path": "cato/cato.agri.txt"},
    "493":     {"author": "Cato", "title": "ORATIONVM M. PORCI CATONIS FRAGMENTA", "path": "cato/cato.frag.txt"},
    "494":     {"author": "Catullus", "title": "Carmina", "path": "catullus.txt"},
    "495":     {"author": "Conrad Celtis", "title": "Odes   CONRADUS CELTIS: ODES    ", "path": "celtis.odes.txt"},
    "496":     {"author": None, "title": "", "path": "celtis.oratio.txt"},
    "497":     {"author": "Censorinus", "title": "de Die Natali Liber", "path": "censorinus.txt"},
    "498":     {"author": "Cicero", "title": "Academica", "path": "cicero/acad.txt"},
    "499":     {"author": "Cicero", "title": "ad Brutum I", "path": "cicero/adbrutum1.txt"},
    "500":     {"author": "Cicero", "title": "ad Brutum II", "path": "cicero/adbrutum2.txt"},
    "501":     {"author": "Cicero", "title": "de Amicitia", "path": "cicero/amic.txt"},
    "502":     {"author": "Cicero", "title": "Pro Archia", "path": "cicero/arch.txt"},
    "503":     {"author": "Cicero", "title": "ad Atticum I", "path": "cicero/att1.txt"},
    "504":     {"author": "Cicero", "title": "ad Atticum X", "path": "cicero/att10.txt"},
    "505":     {"author": "Cicero", "title": "ad Atticum XI", "path": "cicero/att11.txt"},
    "506":     {"author": "Cicero", "title": "ad Atticum XII", "path": "cicero/att12.txt"},
    "507":     {"author": "Cicero", "title": "ad Atticum XIII", "path": "cicero/att13.txt"},
    "508":     {"author": "Cicero", "title": "ad Atticum XIV", "path": "cicero/att14.txt"},
    "509":     {"author": "Cicero", "title": "ad Atticum XV", "path": "cicero/att15.txt"},
    "510":     {"author": "Cicero", "title": "ad Atticum XVI", "path": "cicero/att16.txt"},
    "511":     {"author": "Cicero", "title": "ad Atticum II", "path": "cicero/att2.txt"},
    "512":     {"author": "Cicero", "title": "ad Atticum III", "path": "cicero/att3.txt"},
    "513":     {"author": "Cicero", "title": "ad Atticum IV", "path": "cicero/att4.txt"},
    "514":     {"author": "Cicero", "title": "ad Atticum V", "path": "cicero/att5.txt"},
    "515":     {"author": "Cicero", "title": "ad Atticum VI", "path": "cicero/att6.txt"},
    "516":     {"author": "Cicero", "title": "ad Atticum VII", "path": "cicero/att7.txt"},
    "517":     {"author": "Cicero", "title": "ad Atticum VIII", "path": "cicero/att8.txt"},
    "518":     {"author": "Cicero", "title": "ad Atticum IX", "path": "cicero/att9.txt"},
    "519":     {"author": "Cicero", "title": "PRO L. CORNELIO BALBO ORATIO", "path": "cicero/balbo.txt"},
    "520":     {"author": "Cicero", "title": "BRUTUS", "path": "cicero/brut.txt"},
    "521":     {"author": "Cicero", "title": "IN CAECILIUM ORATIO", "path": "cicero/caecilium.txt"},
    "522":     {"author": "Cicero", "title": "PRO A. CAECINA ORATIO", "path": "cicero/caecina.txt"},
    "523":     {"author": "Cicero", "title": "PRO M. CAELIO ORATIO", "path": "cicero/cael.txt"},
    "524":     {"author": "Cicero", "title": "In Catilinam I", "path": "cicero/cat1.txt"},
    "525":     {"author": "Cicero", "title": "In Catilinam II", "path": "cicero/cat2.txt"},
    "526":     {"author": "Cicero", "title": "In Catilinam III", "path": "cicero/cat3.txt"},
    "527":     {"author": "Cicero", "title": "In Catilinam IV", "path": "cicero/cat4.txt"},
    "528":     {"author": "Cicero", "title": "PRO A. CLVENTIO ORATIO", "path": "cicero/cluentio.txt"},
    "529":     {"author": "Cicero", "title": "COMMENTARIOLVM PETITIONIS", "path": "cicero/compet.txt"},
    "530":     {"author": "Cicero", "title": "DE CONSVLATV SVO FRAGMENTA", "path": "cicero/consulatu.txt"},
    "531":     {"author": "Cicero", "title": "PRO REGE DEIOTARO", "path": "cicero/deio.txt"},
    "532":     {"author": "Cicero", "title": "DE DIVINATIONE LIBER PRIOR", "path": "cicero/divinatione1.txt"},
    "533":     {"author": "Cicero", "title": "DE DIVINATIONE LIBER ALTER", "path": "cicero/divinatione2.txt"},
    "534":     {"author": "Cicero", "title": "DE DOMO SVA", "path": "cicero/domo.txt"},
    "535":     {"author": "Cicero", "title": "ad Familiares I", "path": "cicero/fam1.txt"},
    "536":     {"author": "Cicero", "title": "ad Familiares X", "path": "cicero/fam10.txt"},
    "537":     {"author": "Cicero", "title": "ad Familiares XI", "path": "cicero/fam11.txt"},
    "538":     {"author": "Cicero", "title": "ad Familiares XII", "path": "cicero/fam12.txt"},
    "539":     {"author": "Cicero", "title": "ad Familiares XIII", "path": "cicero/fam13.txt"},
    "540":     {"author": "Cicero", "title": "ad Familiares XIV", "path": "cicero/fam14.txt"},
    "541":     {"author": "Cicero", "title": "ad Familiares XV", "path": "cicero/fam15.txt"},
    "542":     {"author": "Cicero", "title": "ad Familiares XVI", "path": "cicero/fam16.txt"},
    "543":     {"author": "Cicero", "title": "ad Familiares II", "path": "cicero/fam2.txt"},
    "544":     {"author": "Cicero", "title": "ad Familiares III", "path": "cicero/fam3.txt"},
    "545":     {"author": "Cicero", "title": "ad Familiares IV", "path": "cicero/fam4.txt"},
    "546":     {"author": "Cicero", "title": "ad Familiares V", "path": "cicero/fam5.txt"},
    "547":     {"author": "Cicero", "title": "ad Familiares VI", "path": "cicero/fam6.txt"},
    "548":     {"author": "Cicero", "title": "ad Familiares VII", "path": "cicero/fam7.txt"},
    "549":     {"author": "Cicero", "title": "ad Familiares VIII", "path": "cicero/fam8.txt"},
    "550":     {"author": "Cicero", "title": "ad Familiares IX", "path": "cicero/fam9.txt"},
    "551":     {"author": "Cicero", "title": "de Fato", "path": "cicero/fato.txt"},
    "552":     {"author": "Cicero", "title": "de Finibus I", "path": "cicero/fin1.txt"},
    "553":     {"author": "Cicero", "title": "de Finibus II", "path": "cicero/fin2.txt"},
    "554":     {"author": "Cicero", "title": "de Finibus III", "path": "cicero/fin3.txt"},
    "555":     {"author": "Cicero", "title": "de Finibus IV", "path": "cicero/fin4.txt"},
    "556":     {"author": "Cicero", "title": "de Finibus V", "path": "cicero/fin5.txt"},
    "557":     {"author": "Cicero", "title": "PRO L. FLACCO", "path": "cicero/flacco.txt"},
    "558":     {"author": "Cicero", "title": "PRO PRO M. FONTEIO", "path": "cicero/fonteio.txt"},
    "559":     {"author": "Cicero", "title": "ad Quintum Fratrem I", "path": "cicero/fratrem1.txt"},
    "560":     {"author": "Cicero", "title": "ad Quintum Fratrem II", "path": "cicero/fratrem2.txt"},
    "561":     {"author": "Cicero", "title": "ad Quintum Fratrem III", "path": "cicero/fratrem3.txt"},
    "562":     {"author": "Cicero", "title": "ORATIO DE HARVSPICVM RESPONSO", "path": "cicero/haruspicum.txt"},
    "563":     {"author": "Cicero", "title": "DE IMPERIO CN. POMPEI", "path": "cicero/imp.txt"},
    "564":     {"author": "Cicero", "title": "de Inventione I", "path": "cicero/inventione1.txt"},
    "565":     {"author": "Cicero", "title": "de Inventione II", "path": "cicero/inventione2.txt"},
    "566":     {"author": "Cicero", "title": "de Legibus I", "path": "cicero/leg1.txt"},
    "567":     {"author": "Cicero", "title": "de Legibus II", "path": "cicero/leg2.txt"},
    "568":     {"author": "Cicero", "title": "de Legibus III", "path": "cicero/leg3.txt"},
    "569":     {"author": "Cicero", "title": "de Lege Agraria I", "path": "cicero/legagr1.txt"},
    "570":     {"author": "Cicero", "title": "de Lege Agraria II", "path": "cicero/legagr2.txt"},
    "571":     {"author": "Cicero", "title": "de Lege Agraria III", "path": "cicero/legagr3.txt"},
    "572":     {"author": "Cicero", "title": "pro Ligario", "path": "cicero/lig.txt"},
    "573":     {"author": "Cicero", "title": "pro Marcello", "path": "cicero/marc.txt"},
    "574":     {"author": "Cicero", "title": "pro Milone", "path": "cicero/milo.txt"},
    "575":     {"author": "Cicero", "title": "pro Murena", "path": "cicero/murena.txt"},
    "576":     {"author": "Cicero", "title": "De Natura Deorum I", "path": "cicero/nd1.txt"},
    "577":     {"author": "Cicero", "title": "De Natura Deorum II", "path": "cicero/nd2.txt"},
    "578":     {"author": "Cicero", "title": "De Natura Deorum III", "path": "cicero/nd3.txt"},
    "579":     {"author": "Cicero", "title": "de Officiis I", "path": "cicero/off1.txt"},
    "580":     {"author": "Cicero", "title": "de Officiis II", "path": "cicero/off2.txt"},
    "581":     {"author": "Cicero", "title": "de Officiis III", "path": "cicero/off3.txt"},
    "582":     {"author": "Cicero", "title": "de Optimo Genere Oratorum", "path": "cicero/optgen.txt"},
    "583":     {"author": "Cicero", "title": "Orator ad M. Brutum", "path": "cicero/orator.txt"},
    "584":     {"author": "Cicero", "title": "de Oratore I", "path": "cicero/oratore1.txt"},
    "585":     {"author": "Cicero", "title": "de Oratore II", "path": "cicero/oratore2.txt"},
    "586":     {"author": "Cicero", "title": "de Oratore III", "path": "cicero/oratore3.txt"},
    "587":     {"author": "Cicero", "title": "Paradoxa", "path": "cicero/paradoxa.txt"},
    "588":     {"author": "Cicero", "title": "de Partitione", "path": "cicero/partitione.txt"},
    "589":     {"author": "Cicero", "title": "Philippic I", "path": "cicero/phil1.txt"},
    "590":     {"author": "Cicero", "title": "Philippic X", "path": "cicero/phil10.txt"},
    "591":     {"author": "Cicero", "title": "Philippic XI", "path": "cicero/phil11.txt"},
    "592":     {"author": "Cicero", "title": "Philippic XII", "path": "cicero/phil12.txt"},
    "593":     {"author": "Cicero", "title": "Philippic XIII", "path": "cicero/phil13.txt"},
    "594":     {"author": "Cicero", "title": "Philippic XIV", "path": "cicero/phil14.txt"},
    "595":     {"author": "Cicero", "title": "Philippic II", "path": "cicero/phil2.txt"},
    "596":     {"author": "Cicero", "title": "Philippic III", "path": "cicero/phil3.txt"},
    "597":     {"author": "Cicero", "title": "Philippic IV", "path": "cicero/phil4.txt"},
    "598":     {"author": "Cicero", "title": "Philippic V", "path": "cicero/phil5.txt"},
    "599":     {"author": "Cicero", "title": "Philippic VI", "path": "cicero/phil6.txt"},
    "600":     {"author": "Cicero", "title": "Philippic VII", "path": "cicero/phil7.txt"},
    "601":     {"author": "Cicero", "title": "Philippic VIII", "path": "cicero/phil8.txt"},
    "602":     {"author": "Cicero", "title": "Philippic IX", "path": "cicero/phil9.txt"},
    "603":     {"author": "Cicero", "title": "In Pisonem", "path": "cicero/piso.txt"},
    "604":     {"author": "Cicero", "title": "Pro Plancio", "path": "cicero/plancio.txt"},
    "605":     {"author": "Cicero", "title": "Post Reditum in Senatu", "path": "cicero/postreditum.txt"},
    "606":     {"author": "Cicero", "title": "Post Reditum ad Quirites", "path": "cicero/postreditum2.txt"},
    "607":     {"author": "Cicero", "title": "De Provinciis Consularibus", "path": "cicero/prov.txt"},
    "608":     {"author": "Cicero", "title": "Pro Quinctio", "path": "cicero/quinc.txt"},
    "609":     {"author": "Cicero", "title": "Pro Rabiro Perduellionis", "path": "cicero/rabirio.txt"},
    "610":     {"author": "Cicero", "title": "Pro Rabiro Postumo", "path": "cicero/rabiriopost.txt"},
    "611":     {"author": "Cicero", "title": "de Re Publica I", "path": "cicero/repub1.txt"},
    "612":     {"author": "Cicero", "title": "de Re Publica II", "path": "cicero/repub2.txt"},
    "613":     {"author": "Cicero", "title": "de Re Publica III", "path": "cicero/repub3.txt"},
    "614":     {"author": "Cicero", "title": "de Re Publica IV", "path": "cicero/repub4.txt"},
    "615":     {"author": "Cicero", "title": "de Re Publica V", "path": "cicero/repub5.txt"},
    "616":     {"author": "Cicero", "title": "de Re Publica VI", "path": "cicero/repub6.txt"},
    "617":     {"author": "Cicero", "title": "Pro Roscio Comodeo", "path": "cicero/rosccom.txt"},
    "618":     {"author": "Cicero", "title": "Pro Scauro", "path": "cicero/scauro.txt"},
    "619":     {"author": "Cicero", "title": "de Senectute", "path": "cicero/senectute.txt"},
    "620":     {"author": "Cicero", "title": "Pro Sestio", "path": "cicero/sestio.txt"},
    "621":     {"author": "Cicero", "title": "Pro Sex. Roscio Amerino", "path": "cicero/sex.rosc.txt"},
    "622":     {"author": "Cicero", "title": "Pro Sulla", "path": "cicero/sulla.txt"},
    "623":     {"author": "Cicero", "title": "Topica", "path": "cicero/topica.txt"},
    "624":     {"author": "Cicero", "title": "Tusculan Disputations I", "path": "cicero/tusc1.txt"},
    "625":     {"author": "Cicero", "title": "Tusculan Disputations II", "path": "cicero/tusc2.txt"},
    "626":     {"author": "Cicero", "title": "Tusculan Disputations III", "path": "cicero/tusc3.txt"},
    "627":     {"author": "Cicero", "title": "Tusculan Disputations IV", "path": "cicero/tusc4.txt"},
    "628":     {"author": "Cicero", "title": "Tusculan Disputations IV", "path": "cicero/tusc5.txt"},
    "629":     {"author": "Cicero", "title": "In Vatinium", "path": "cicero/vatin.txt"},
    "630":     {"author": "Cicero", "title": "In Verrem I", "path": "cicero/ver1.txt"},
    "631":     {"author": "Cicero", "title": "In Verrem II.1", "path": "cicero/verres.2.1.txt"},
    "632":     {"author": "Cicero", "title": "In Verrem II.2", "path": "cicero/verres.2.2.txt"},
    "633":     {"author": "Cicero", "title": "In Verrem II.3", "path": "cicero/verres.2.3.txt"},
    "634":     {"author": "Cicero", "title": "In Verrem II.4", "path": "cicero/verres.2.4.txt"},
    "635":     {"author": "Cicero", "title": "In Verrem II.5", "path": "cicero/verres.2.5.txt"},
    "636":     {"author": None, "title": "Helvius Cinna", "path": "cinna.txt"},
    "637":     {"author": None, "title": "Speech of Claudius", "path": "claud.inscr.txt"},
    "638":     {"author": None, "title": "Claudian", "path": "claudian/claudian.cons6.txt"}, "639": {
        "author": "Claudian", "title": "Panegyricus Dictus Olybrio et Probino Consulibus",
        "path":   "claudian/claudian.olyb.txt"
    }, "640":  {"author": "Claudian", "title": "De Raptu Proserpinae I ", "path": "claudian/claudian.proserp1.txt"},
    "641":     {"author": "Claudian", "title": "De Raptu Proserpinae II ", "path": "claudian/claudian.proserp2.txt"},
    "642":     {"author": "Claudian", "title": "De Raptu Proserpinae III ", "path": "claudian/claudian.proserp3.txt"},
    "643":     {"author": "Claudian", "title": "In Rufinum I ", "path": "claudian/claudian.ruf1.txt"},
    "644":     {"author": "Pseudo-Plato", "title": "Clitophon", "path": "clitophon.txt"},
    "645":     {"author": None, "title": "Coleman the Irishman ", "path": "colman.txt"},
    "646":     {"author": "Life of St. Columba", "title": "Book I", "path": "columba1.txt"},
    "647":     {"author": "Life of St. Columba", "title": "Book II", "path": "columba2.txt"},
    "648":     {"author": None, "title": "Christopher Columbus", "path": "columbus.txt"},
    "649":     {"author": "Columella", "title": "de Arboribus ", "path": "columella/columella.arbor.txt"},
    "650":     {"author": "Columella", "title": "de Re Rustica I ", "path": "columella/columella.rr1.txt"},
    "651":     {"author": "Columella", "title": "de Re Rustica X ", "path": "columella/columella.rr10.txt"},
    "652":     {"author": "Columella", "title": "de Re Rustica XI ", "path": "columella/columella.rr11.txt"},
    "653":     {"author": "Columella", "title": "de Re Rustica XII ", "path": "columella/columella.rr12.txt"},
    "654":     {"author": "Columella", "title": "de Re Rustica II", "path": "columella/columella.rr2.txt"},
    "655":     {"author": "Columella", "title": "de Re Rustica III", "path": "columella/columella.rr3.txt"},
    "656":     {"author": "Columella", "title": "de Re Rustica IV", "path": "columella/columella.rr4.txt"},
    "657":     {"author": "Columella", "title": "de Re Rustica V", "path": "columella/columella.rr5.txt"},
    "658":     {"author": "Columella", "title": "de Re Rustica VI ", "path": "columella/columella.rr6.txt"},
    "659":     {"author": "Columella", "title": "de Re Rustica VII", "path": "columella/columella.rr7.txt"},
    "660":     {"author": "Columella", "title": "de Re Rustica VIII", "path": "columella/columella.rr8.txt"},
    "661":     {"author": "Columella", "title": "de Re Rustica IX ", "path": "columella/columella.rr9.txt"},
    "662":     {"author": None, "title": "O Comes", "path": "comes.txt"},
    "663":     {"author": "Commodianus", "title": "Carmen de Duobus Populis", "path": "commodianus/commodianus1.txt"},
    "664":     {"author": "Commodianus", "title": "Instructiones", "path": "commodianus/commodianus2.txt"},
    "665":     {"author": "Commodian", "title": "De Saeculi Istius Fine", "path": "commodianus/commodianus3.txt"},
    "666":     {"author": "Laurentius Corvinus", "title": "ad Famam", "path": "corvinus1.txt"},
    "667":     {"author": "Laurentius Corvinus", "title": "Epithalamium", "path": "corvinus2.txt"},
    "668":     {"author": None, "title": "Poems of Giovanni Cotta (1480-1510)", "path": "cotta.txt"},
    "669":     {"author": None, "title": "Early Christian Creeds", "path": "creeds.txt"},
    "670":     {"author": "Curtius Rufus", "title": "Historiae Alexandri Magni X", "path": "curtius/curtius10.txt"},
    "671":     {"author": "Curtius Rufus", "title": "Historiae Alexandri Magni III", "path": "curtius/curtius3.txt"},
    "672":     {"author": "Curtius Rufus", "title": "Historiae Alexandri Magni IV", "path": "curtius/curtius4.txt"},
    "673":     {"author": "Curtius Rufus", "title": "Historiae Alexandri Magni V", "path": "curtius/curtius5.txt"},
    "674":     {"author": "Curtius Rufus", "title": "Historiae Alexandri Magni VI", "path": "curtius/curtius6.txt"},
    "675":     {"author": "Curtius Rufus", "title": "Historiae Alexandri Magni VII", "path": "curtius/curtius7.txt"},
    "676":     {"author": "Curtius Rufus", "title": "Historiae Alexandri Magni VIII", "path": "curtius/curtius8.txt"},
    "677":     {"author": "Curtius Rufus", "title": "Historiae Alexandri Magni III", "path": "curtius/curtius9.txt"},
    "678":     {"author": "Dante", "title": "Ecloga I", "path": "dante/ec1.txt"},
    "679":     {"author": "Dante", "title": "Epistolae", "path": "dante/ep.txt"},
    "680":     {"author": "Dante", "title": "Monarchia I", "path": "dante/mon1.txt"},
    "681":     {"author": "Dante", "title": "Monarchia II", "path": "dante/mon2.txt"},
    "682":     {"author": "Dante", "title": "Monarchia III", "path": "dante/mon3.txt"},
    "683":     {"author": "Dante", "title": "De Vulgari Eloquentia I", "path": "dante/vulgar.txt"},
    "684":     {"author": "Dante", "title": "De Vulgari Eloquentia II", "path": "dante/vulgar2.txt"},
    "685":     {"author": "Dares the Phrygian", "title": "De Excidio Trojae Historia", "path": "dares.txt"},
    "686":     {"author": "Dares the Phrygian", "title": "De Excidio Trojae Historia", "path": "dares1.txt"},
    "687":     {"author": "de Bury", "title": "Philobiblon", "path": "debury.txt"},
    "688":     {"author": None, "title": "Universal Declaration of Human Rights", "path": "declaratio.txt"},
    "689":     {"author": None, "title": "Decretum Gelasianum", "path": "decretum.txt"},
    "690":     {"author": "Descartes", "title": "Epistula", "path": "descartes/des.ep.txt"},
    "691":     {"author": "Descartes", "title": "Meditatio I", "path": "descartes/des.med1.txt"},
    "692":     {"author": "Descartes", "title": "Meditatio II", "path": "descartes/des.med2.txt"},
    "693":     {"author": "Descartes", "title": "Meditatio III", "path": "descartes/des.med3.txt"},
    "694":     {"author": "Descartes", "title": "Meditatio IV", "path": "descartes/des.med4.txt"},
    "695":     {"author": "Descartes", "title": "Meditatio V", "path": "descartes/des.med5.txt"},
    "696":     {"author": "Descartes", "title": "Meditatio VI", "path": "descartes/des.med6.txt"},
    "697":     {"author": "Descartes", "title": "Praefatio", "path": "descartes/des.pr.txt"},
    "698":     {"author": "Descartes", "title": "Synopsis", "path": "descartes/des.syn.txt"},
    "699":     {"author": None, "title": "", "path": "dicchristi.txt"},
    "700":     {"author": None, "title": "Dic quid agis ", "path": "dicquid.txt"},
    "701":     {"author": None, "title": "Dies Irae", "path": "diesirae.txt"},
    "702":     {"author": "Anonymous", "title": "Dira vi amoris teror ", "path": "diravi.txt"},
    "703":     {"author": "Donatus", "title": "Ars Minor", "path": "don.txt"},
    "704":     {"author": None, "title": "Donation of Constantine", "path": "donation.txt"},
    "705":     {"author": None, "title": "", "path": "dulcesolum.txt"},
    "706":     {"author": "Anonymous", "title": "Dum Diane vitrea ", "path": "dumdiane.txt"},
    "707":     {"author": None, "title": "Dum domus lapidea ", "path": "dumdomus.txt"},
    "708":     {"author": None, "title": "", "path": "dumestas.txt"}, "709": {
        "author": "Petrus de Ebulo", "title": "Liber ad honorem Augusti sive de rebus Siculis", "path": "ebulo.txt"
    }, "710":  {"author": "Egeria", "title": "Itinerarium Pars Prima", "path": "egeria1.txt"},
    "711":     {"author": "Egeria", "title": "Itinerarium Pars Secunda", "path": "egeria2.txt"},
    "712":     {"author": "Einhard", "title": "Life of Charlemagne", "path": "ein.txt"},
    "713":     {"author": None, "title": "", "path": "ency.fides.txt"},
    "714":     {"author": "Ennius", "title": "Fragments", "path": "enn.txt"},
    "715":     {"author": "Ennodius", "title": "Panegyricus Regi Theoderico", "path": "ennodius.txt"}, "716": {
        "author": None, "title": "Epistolae de Priapismo Cleopatrae eiusque Remediis", "path": "ep.priapismo.txt"
    }, "717":  {"author": None, "title": "Epistolae Austrasicae", "path": "epistaustras.txt"},
    "718":     {"author": None, "title": "ROMAN EPITAPHS", "path": "epitaphs.txt"},
    "719":     {"author": None, "title": "Epitome Cononiana", "path": "epitomecononiana.txt"},
    "720":     {"author": None, "title": "Epitome Feliciana", "path": "epitomefeliciana.txt"},
    "721":     {"author": "Eramus", "title": "Libri Antibarbarorum", "path": "erasmus/antibarb.txt"},
    "722":     {"author": "Eramus", "title": "Colloquia", "path": "erasmus/coll.txt"},
    "723":     {"author": "Eramus", "title": "Selected Writings", "path": "erasmus/ep.txt"},
    "724":     {"author": "Erasmus", "title": "Institutio", "path": "erasmus/inst.txt"},
    "725":     {"author": "Erasmus", "title": "de Laude Matrimonii", "path": "erasmus/laude.txt"},
    "726":     {"author": "Eramus", "title": "The Praise of Folly", "path": "erasmus/moriae.txt"},
    "727":     {"author": "Eramus", "title": "Querela Pacis", "path": "erasmus/querela.txt"},
    "728":     {"author": "Erchempert", "title": "Historia Langabardorum Beneventarnorum", "path": "erchempert.txt"},
    "729":     {"author": None, "title": "Estas non apparuit ", "path": "estas.txt"},
    "730":     {"author": "Eucherius", "title": "De laude eremi", "path": "eucherius.txt"},
    "731":     {"author": None, "title": "", "path": "eugenius.txt"},
    "732":     {"author": "Eugippius", "title": "Life of Saint Severinus", "path": "eugippius.txt"},
    "733":     {"author": "Eutropius", "title": "Book I", "path": "eutropius/eutropius1.txt"},
    "734":     {"author": "Eutropius", "title": "Book X", "path": "eutropius/eutropius10.txt"},
    "735":     {"author": "Eutropius", "title": "Book II", "path": "eutropius/eutropius2.txt"},
    "736":     {"author": "Eutropius", "title": "Book III", "path": "eutropius/eutropius3.txt"},
    "737":     {"author": "Eutropius", "title": "Book IV", "path": "eutropius/eutropius4.txt"},
    "738":     {"author": "Eutropius", "title": "Book V", "path": "eutropius/eutropius5.txt"},
    "739":     {"author": "Eutropius", "title": "Book II", "path": "eutropius/eutropius6.txt"},
    "740":     {"author": "Eutropius", "title": "Book VII", "path": "eutropius/eutropius7.txt"},
    "741":     {"author": "Eutropius", "title": "Book VIII", "path": "eutropius/eutropius8.txt"},
    "742":     {"author": "Eutropius", "title": "Book IX", "path": "eutropius/eutropius9.txt"},
    "743":     {"author": None, "title": "Exivi de paradiso ", "path": "exivi.txt"},
    "744":     {"author": None, "title": "Guido Fabe ", "path": "fabe.txt"},
    "745":     {"author": None, "title": "Hugo Falcandus", "path": "falcandus.txt"},
    "746":     {"author": None, "title": "Chronicon Beneventanum", "path": "falcone.txt"},
    "747":     {"author": None, "title": "Nicolai Borbonii ", "path": "ferraria.txt"},
    "748":     {"author": "Marsilio Ficino", "title": "Theages ", "path": "ficino.txt"},
    "749":     {"author": None, "title": "Locustae ", "path": "fletcher.txt"},
    "750":     {"author": "Florus", "title": "Epitome of Roman Wars", "path": "florus1.txt"},
    "751":     {"author": "Florus", "title": "Epitome of Roman Wars", "path": "florus2.txt"},
    "752":     {"author": None, "title": "Eternal Bond of Brothers", "path": "foedusaeternum.txt"},
    "753":     {"author": "Pedantius", "title": "Act I  ", "path": "forsett1.txt"},
    "754":     {"author": "Pedantius", "title": "Act II  ", "path": "forsett2.txt"},
    "755":     {"author": None, "title": "Venance Fortunat ", "path": "fortunat.txt"},
    "756":     {"author": None, "title": "Fragmentum Laurentianum", "path": "fragmentumlaurentianum.txt"},
    "757":     {"author": "Fredegarius", "title": "Chronicon", "path": "fredegarius.txt"},
    "758":     {"author": None, "title": "Frodebertus & Importunus", "path": "frodebertus.txt"},
    "759":     {"author": "Frontinus", "title": "De aquaeductu urbis Romae I", "path": "frontinus/aqua1.txt"},
    "760":     {"author": "Frontinus", "title": "De aquaeductu urbis Romae II", "path": "frontinus/aqua2.txt"},
    "761":     {"author": "Frontinus", "title": "De Controversiis", "path": "frontinus/contro.txt"},
    "762":     {"author": "Frontinus", "title": "De Limitibus", "path": "frontinus/lim.txt"},
    "763":     {"author": "Frontinus", "title": "De Arte Mensoria", "path": "frontinus/mensoria.txt"},
    "764":     {"author": "Frontinus", "title": "De Agrorum Qualitate", "path": "frontinus/qualitate.txt"},
    "765":     {"author": "Frontinus", "title": "Strategemata I", "path": "frontinus/strat1.txt"},
    "766":     {"author": "Frontinus", "title": "Strategemata II", "path": "frontinus/strat2.txt"},
    "767":     {"author": "Frontinus", "title": "Strategemata III", "path": "frontinus/strat3.txt"},
    "768":     {"author": "Frontinus", "title": "Strategemata IIII", "path": "frontinus/strat4.txt"},
    "769":     {"author": "M. Cornelius Fronto", "title": "Epistulae ", "path": "fronto.txt"},
    "770":     {"author": None, "title": "St. Fulbert of Chartres", "path": "fulbert.txt"},
    "771":     {"author": "Fulgentius", "title": "Mitologiarum Liber I", "path": "fulgentius/fulgentius1.txt"},
    "772":     {"author": "Fulgentius", "title": "Mitologiarum Liber II", "path": "fulgentius/fulgentius2.txt"},
    "773":     {"author": "Fulgentius", "title": "Mitologiarum Liber III", "path": "fulgentius/fulgentius3.txt"},
    "774":     {"author": "Fulgentius", "title": "Expositio Sermonum Antiquorum", "path": "fulgentius/fulgentius4.txt"},
    "775":     {"author": "Fulgentius", "title": "Expositio Virgilianae", "path": "fulgentius/fulgentius5.txt"},
    "776":     {"author": "Gaius", "title": "Commentary I", "path": "gaius1.txt"},
    "777":     {"author": "Gaius", "title": "Commentary II", "path": "gaius2.txt"},
    "778":     {"author": "Gaius", "title": "Commentary III", "path": "gaius3.txt"},
    "779":     {"author": "Gaius", "title": "Commentary IV", "path": "gaius4.txt"},
    "780":     {"author": "Galileo Galilei", "title": "Sidereus Nuncius", "path": "galileo/galileo.sid.txt"},
    "781":     {"author": None, "title": "Garcilaso de la Vega ", "path": "garcilaso.txt"},
    "782":     {"author": None, "title": "John of Garland", "path": "garland.txt"},
    "783":     {"author": None, "title": "Gaudeamus Igitur", "path": "gaud.txt"},
    "784":     {"author": "Gauss", "title": "Demonstratio Nova", "path": "gauss.txt"},
    "785":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber I", "path": "gellius/gellius1.txt"},
    "786":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber X", "path": "gellius/gellius10.txt"},
    "787":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber XI", "path": "gellius/gellius11.txt"},
    "788":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber XIII", "path": "gellius/gellius13.txt"},
    "789":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber II", "path": "gellius/gellius2.txt"},
    "790":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber XX", "path": "gellius/gellius20.txt"},
    "791":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber III", "path": "gellius/gellius3.txt"},
    "792":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber IV", "path": "gellius/gellius4.txt"},
    "793":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber V", "path": "gellius/gellius5.txt"},
    "794":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber VI", "path": "gellius/gellius6.txt"},
    "795":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber VII", "path": "gellius/gellius7.txt"},
    "796":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber VIII", "path": "gellius/gellius8.txt"},
    "797":     {"author": "Auli Gellii Noctes Atticae", "title": "Liber IX", "path": "gellius/gellius9.txt"},
    "798":     {"author": "Auli Gellii Noctes Atticae", "title": "Capitula", "path": "gellius/gelliuscapitula.txt"},
    "799":     {"author": "Auli Gellii Noctes Atticae", "title": "Praefatio", "path": "gellius/gelliuspraef.txt"},
    "800":     {"author": "Germanicus", "title": "Aratea", "path": "germanicus.txt"},
    "801":     {"author": None, "title": "Gesta Francorum I", "path": "gestafrancorum/gestafrancorum1.txt"},
    "802":     {"author": None, "title": "Gesta Francorum X", "path": "gestafrancorum/gestafrancorum10.txt"},
    "803":     {"author": None, "title": "Gesta Francorum II", "path": "gestafrancorum/gestafrancorum2.txt"},
    "804":     {"author": None, "title": "Gesta Francorum III", "path": "gestafrancorum/gestafrancorum3.txt"},
    "805":     {"author": None, "title": "Gesta Francorum IIII", "path": "gestafrancorum/gestafrancorum4.txt"},
    "806":     {"author": None, "title": "Gesta Francorum V", "path": "gestafrancorum/gestafrancorum5.txt"},
    "807":     {"author": None, "title": "Gesta Francorum VI", "path": "gestafrancorum/gestafrancorum6.txt"},
    "808":     {"author": None, "title": "Gesta Francorum VII", "path": "gestafrancorum/gestafrancorum7.txt"},
    "809":     {"author": None, "title": "Gesta Francorum VIII", "path": "gestafrancorum/gestafrancorum8.txt"},
    "810":     {"author": None, "title": "Gesta Francorum IX", "path": "gestafrancorum/gestafrancorum9.txt"},
    "811":     {"author": None, "title": "Gesta Romanorum", "path": "gestarom.txt"},
    "812":     {"author": "Gioacchino da Fiore", "title": "Adversus Iudeos", "path": "gioacchino.txt"},
    "813":     {"author": "Godfrey of Winchester", "title": "Epigrammata", "path": "godfrey.epigrammata.txt"}, "814": {
        "author": "Godfrey of Winchester", "title": "Epigrammata Historica", "path": "godfrey.epigrammatahist.txt"
    }, "815":  {"author": "Grattius", "title": "Cynegetica", "path": "grattius.txt"},
    "816":     {"author": None, "title": "Inter Gravissimas ", "path": "gravissimas.txt"},
    "817":     {"author": None, "title": "Letter of Gregory the Great", "path": "greg.txt"},
    "818":     {"author": "Gregory IX", "title": "Decretals I", "path": "gregdecretals1.txt"},
    "819":     {"author": "Gregory IX", "title": "Decretals II", "path": "gregdecretals2.txt"},
    "820":     {"author": "Gregory IX", "title": "Decretals III", "path": "gregdecretals3.txt"},
    "821":     {"author": "Gregory IX", "title": "Decretals IV", "path": "gregdecretals4.txt"},
    "822":     {"author": "Gregory IX", "title": "Decretals IV", "path": "gregdecretals5.txt"},
    "823":     {"author": "Gregory VII", "title": "Epistolae Vagantes", "path": "gregory7.txt"},
    "824":     {"author": None, "title": "Gregory of Tours I", "path": "gregorytours/gregorytours1.txt"},
    "825":     {"author": None, "title": "Gregory of Tours X", "path": "gregorytours/gregorytours10.txt"},
    "826":     {"author": None, "title": "Gregory of Tours II", "path": "gregorytours/gregorytours2.txt"},
    "827":     {"author": None, "title": "Gregory of Tours III", "path": "gregorytours/gregorytours3.txt"},
    "828":     {"author": None, "title": "Gregory of Tours IV", "path": "gregorytours/gregorytours4.txt"},
    "829":     {"author": None, "title": "Gregory of Tours V", "path": "gregorytours/gregorytours5.txt"},
    "830":     {"author": None, "title": "Gregory of Tours VI", "path": "gregorytours/gregorytours6.txt"},
    "831":     {"author": None, "title": "Gregory of Tours VII", "path": "gregorytours/gregorytours7.txt"},
    "832":     {"author": None, "title": "Gregory of Tours VIII", "path": "gregorytours/gregorytours8.txt"},
    "833":     {"author": None, "title": "Gregory of Tours IX", "path": "gregorytours/gregorytours9.txt"},
    "834":     {"author": "Nero", "title": "Act I  ", "path": "gwinne1.txt"},
    "835":     {"author": "Nero", "title": "Act II  ", "path": "gwinne2.txt"},
    "836":     {"author": "Nero", "title": "Act III ", "path": "gwinne3.txt"},
    "837":     {"author": "Nero", "title": "Act IV ", "path": "gwinne4.txt"},
    "838":     {"author": "Nero", "title": "Act V.1 ", "path": "gwinne5.1.txt"},
    "839":     {"author": "Nero", "title": "Act V.2 ", "path": "gwinne5.2.txt"},
    "840":     {"author": "Nero", "title": "Act V.3 ", "path": "gwinne5.3.txt"},
    "841":     {"author": "Nero", "title": "Act V.4 ", "path": "gwinne5.4.txt"},
    "842":     {"author": None, "title": "Edmond Halley (1656\u20131742)", "path": "halley.txt"},
    "843":     {"author": None, "title": "Hebet Sidus Leti Visus", "path": "hebet.txt"},
    "844":     {"author": None, "title": "Correspondence of Henry VII", "path": "henry1.txt"},
    "845":     {"author": None, "title": "Correspondence of Henry VII", "path": "henry2.txt"},
    "846":     {"author": None, "title": "Correspondence of Henry VII", "path": "henry3.txt"},
    "847":     {"author": "Henry of Settimello", "title": "Elegia", "path": "henrysettimello.txt"},
    "848":     {"author": None, "title": "Pseudo-Plato ", "path": "hipp.txt"},
    "849":     {"author": None, "title": "Historia Apollonii regis Tyri", "path": "histapoll.txt"},
    "850":     {"author": None, "title": "Historia Brittonum", "path": "histbrit.txt"},
    "851":     {"author": None, "title": "Augustin T\u00fcnger", "path": "holberg.txt"},
    "852":     {"author": "Horace", "title": "Ars Poetica", "path": "horace/arspoet.txt"},
    "853":     {"author": "Horace", "title": "Odes I", "path": "horace/carm1.txt"},
    "854":     {"author": "Horace", "title": "Odes II", "path": "horace/carm2.txt"},
    "855":     {"author": "Horace", "title": "Odes III", "path": "horace/carm3.txt"},
    "856":     {"author": "Horace", "title": "Odes IV", "path": "horace/carm4.txt"},
    "857":     {"author": "Horace", "title": "Carmen Saeculare", "path": "horace/carmsaec.txt"},
    "858":     {"author": "Horace", "title": "Epodes", "path": "horace/ep.txt"},
    "859":     {"author": "Horace", "title": "Epistulae I", "path": "horace/epist1.txt"},
    "860":     {"author": "Horace", "title": "Epistulae II", "path": "horace/epist2.txt"},
    "861":     {"author": "Horace", "title": "Sermonum Liber I", "path": "horace/serm1.txt"},
    "862":     {"author": "Horace", "title": "Sermonum Liber II", "path": "horace/serm2.txt"},
    "863":     {"author": None, "title": "Hrabanus Maurus ", "path": "hrabanus.txt"},
    "864":     {"author": None, "title": "Hugo of Saint Victor", "path": "hugo/hugo.solo.txt"},
    "865":     {"author": "Hugo of St. Victor", "title": "Didascalicon I", "path": "hugo/hugo1.txt"},
    "866":     {"author": "Hugo of St. Victor", "title": "Didascalicon II", "path": "hugo/hugo2.txt"},
    "867":     {"author": "Hugo of St. Victor", "title": "Didascalicon III", "path": "hugo/hugo3.txt"},
    "868":     {"author": "Hugo of St. Victor", "title": "Didascalicon IV", "path": "hugo/hugo4.txt"},
    "869":     {"author": "Hugo of St. Victor", "title": "Didascalicon V", "path": "hugo/hugo5.txt"},
    "870":     {"author": "Hugo of St. Victor", "title": "Didascalicon VI", "path": "hugo/hugo6.txt"},
    "871":     {"author": "Hydatius", "title": "Chronicon", "path": "hydatiuschronicon.txt"},
    "872":     {"author": "Hydatius", "title": "Fasti", "path": "hydatiusfasti.txt"},
    "873":     {"author": "Hyginus", "title": "de Astronomia I", "path": "hyginus/hyginus1.txt"},
    "874":     {"author": "Hyginus", "title": "de Astronomia II", "path": "hyginus/hyginus2.txt"},
    "875":     {"author": "Hyginus", "title": "de Astronomia III", "path": "hyginus/hyginus3.txt"},
    "876":     {"author": "Hyginus", "title": "de Astronomia IV", "path": "hyginus/hyginus4.txt"},
    "877":     {"author": "Hyginus", "title": "Fabulae", "path": "hyginus/hyginus5.txt"},
    "878":     {"author": "Pseudo-Hyginus", "title": "de Munitionibus Castrorum", "path": "hyginus/hyginus6.txt"},
    "879":     {"author": None, "title": "", "path": "hymni.txt"},
    "880":     {"author": "Lewis Carroll", "title": "Jabberwocky ", "path": "iabervocius.txt"},
    "881":     {"author": "Anonymous", "title": "Iam, dulcis amica ", "path": "iamdulcis.txt"},
    "882":     {"author": None, "title": "", "path": "ilias.txt"},
    "883":     {"author": None, "title": "", "path": "index.txt"},
    "884":     {"author": None, "title": "INDEX AUCTORUM", "path": "indices.txt"},
    "885":     {"author": "Lotario dei Segni", "title": "De Miseria Condicionis Humane", "path": "innocent1.txt"},
    "886":     {"author": "Lotario dei Segni", "title": "Dialogus inter Deum et Peccatorem", "path": "innocent2.txt"},
    "887":     {"author": None, "title": "Inquisitio", "path": "inquisitio.txt"},
    "888":     {"author": None, "title": "Inscriptiones", "path": "inscriptions.txt"},
    "889":     {"author": None, "title": "Iordanis de Origine Actibusque Getarum", "path": "iordanes1.txt"}, "890": {
        "author": "Iordanes", "title": "De summa temporum vel origine actibusque gentis Romanorum",
        "path":   "iordanes2.txt"
    }, "891":  {"author": "Anonymous", "title": "Ipsa vivere mihi reddidit! ", "path": "ipsavivere.txt"},
    "892":     {"author": "Isidore", "title": "Etymologiae I", "path": "isidore/1.txt"},
    "893":     {"author": "Isidore", "title": "Etymologiae X", "path": "isidore/10.txt"},
    "894":     {"author": "Isidore", "title": "Etymologiae XI", "path": "isidore/11.txt"},
    "895":     {"author": "Isidore", "title": "Etymologiae XII", "path": "isidore/12.txt"},
    "896":     {"author": "Isidore", "title": "Etymologiae XIII", "path": "isidore/13.txt"},
    "897":     {"author": "Isidore", "title": "Etymologiae XIV", "path": "isidore/14.txt"},
    "898":     {"author": "Isidore", "title": "Etymologiae XV", "path": "isidore/15.txt"},
    "899":     {"author": "Isidore", "title": "Etymologiae XVI", "path": "isidore/16.txt"},
    "900":     {"author": "Isidore", "title": "Etymologiae XVII ", "path": "isidore/17.txt"},
    "901":     {"author": "Isidore", "title": "Etymologiae XVIII ", "path": "isidore/18.txt"},
    "902":     {"author": "Isidore", "title": "Etymologiae XIX ", "path": "isidore/19.txt"},
    "903":     {"author": "Isidore", "title": "Etymologiae II", "path": "isidore/2.txt"},
    "904":     {"author": "Isidore", "title": "Etymologiae XX ", "path": "isidore/20.txt"},
    "905":     {"author": "Isidore", "title": "Etymologiae III", "path": "isidore/3.txt"},
    "906":     {"author": "Isidore", "title": "Etymologiae IV", "path": "isidore/4.txt"},
    "907":     {"author": "Isidore", "title": "Etymologiae V", "path": "isidore/5.txt"},
    "908":     {"author": "Isidore", "title": "Etymologiae VI", "path": "isidore/6.txt"},
    "909":     {"author": "Isidore", "title": "Etymologiae VII", "path": "isidore/7.txt"},
    "910":     {"author": "Isidore", "title": "Etymologiae VIII", "path": "isidore/8.txt"},
    "911":     {"author": "Isidore", "title": "Etymologiae IX", "path": "isidore/9.txt"}, "912": {
        "author": "Isidorus Hispalensis", "title": "Historia de regibus Gothorum, Vandalorum et Suevorum",
        "path":   "isidore/historia.txt"
    }, "913":  {"author": "Isidore", "title": "Sentientiae I", "path": "isidore/sententiae1.txt"},
    "914":     {"author": "Isidore", "title": "Sentientiae II", "path": "isidore/sententiae2.txt"},
    "915":     {"author": "Isidore", "title": "Sentientiae III", "path": "isidore/sententiae3.txt"},
    "916":     {"author": None, "title": "Janus Secundus", "path": "janus1.txt"},
    "917":     {"author": None, "title": "Janus Secundus", "path": "janus2.txt"},
    "918":     {"author": "St. Jerome", "title": "Contra Ioannem", "path": "jerome/contraioannem.txt"},
    "919":     {"author": "Sancti Hieronymi Epistulae", "title": "1-10 ", "path": "jerome/epistulae.txt"},
    "920":     {"author": "Jerome", "title": "Life of Malchus", "path": "jerome/vitamalchus.txt"},
    "921":     {"author": "Jerome", "title": "Life of Paul", "path": "jerome/vitapauli.txt"}, "922": {
        "author": None, "title": "Honores Academici Praesidi J. F. Kennedy Berolini Tributi", "path": "jfkhonor.txt"
    }, "923":  {"author": None, "title": "Johannes de Plano Carpini", "path": "johannes.txt"},
    "924":     {"author": None, "title": "Junillus", "path": "junillus.txt"},
    "925":     {"author": None, "title": "Justin I", "path": "justin/1.txt"},
    "926":     {"author": None, "title": "Justin X", "path": "justin/10.txt"},
    "927":     {"author": None, "title": "Justin XI", "path": "justin/11.txt"},
    "928":     {"author": None, "title": "Justin XII", "path": "justin/12.txt"},
    "929":     {"author": None, "title": "Justin XIII", "path": "justin/13.txt"},
    "930":     {"author": None, "title": "Justin XIV", "path": "justin/14.txt"},
    "931":     {"author": None, "title": "Justin XV", "path": "justin/15.txt"},
    "932":     {"author": None, "title": "Justin XVI", "path": "justin/16.txt"},
    "933":     {"author": None, "title": "Justin XVII", "path": "justin/17.txt"},
    "934":     {"author": None, "title": "Justin XVIII", "path": "justin/18.txt"},
    "935":     {"author": None, "title": "Justin XIX", "path": "justin/19.txt"},
    "936":     {"author": None, "title": "Justin II", "path": "justin/2.txt"},
    "937":     {"author": None, "title": "Justin XX", "path": "justin/20.txt"},
    "938":     {"author": None, "title": "Justin XXI", "path": "justin/21.txt"},
    "939":     {"author": None, "title": "Justin XXII", "path": "justin/22.txt"},
    "940":     {"author": None, "title": "Justin XXIII", "path": "justin/23.txt"},
    "941":     {"author": None, "title": "Justin XXIV", "path": "justin/24.txt"},
    "942":     {"author": None, "title": "Justin XXV", "path": "justin/25.txt"},
    "943":     {"author": None, "title": "Justin XXVI", "path": "justin/26.txt"},
    "944":     {"author": None, "title": "Justin XXVII", "path": "justin/27.txt"},
    "945":     {"author": None, "title": "Justin XXVIII", "path": "justin/28.txt"},
    "946":     {"author": None, "title": "Justin XXIX", "path": "justin/29.txt"},
    "947":     {"author": None, "title": "Justin III", "path": "justin/3.txt"},
    "948":     {"author": None, "title": "Justin XXX", "path": "justin/30.txt"},
    "949":     {"author": None, "title": "Justin XXXI", "path": "justin/31.txt"},
    "950":     {"author": None, "title": "Justin XXXII", "path": "justin/32.txt"},
    "951":     {"author": None, "title": "Justin XXXIII", "path": "justin/33.txt"},
    "952":     {"author": None, "title": "Justin XXXIV", "path": "justin/34.txt"},
    "953":     {"author": None, "title": "Justin XXXV", "path": "justin/35.txt"},
    "954":     {"author": None, "title": "Justin XXXVI", "path": "justin/36.txt"},
    "955":     {"author": None, "title": "Justin XXXVII", "path": "justin/37.txt"},
    "956":     {"author": None, "title": "Justin XXXVIII", "path": "justin/38.txt"},
    "957":     {"author": None, "title": "Justin XXXIX", "path": "justin/39.txt"},
    "958":     {"author": None, "title": "Justin IV", "path": "justin/4.txt"},
    "959":     {"author": None, "title": "Justin XL", "path": "justin/40.txt"},
    "960":     {"author": None, "title": "Justin XLI", "path": "justin/41.txt"},
    "961":     {"author": None, "title": "Justin XLII", "path": "justin/42.txt"},
    "962":     {"author": None, "title": "Justin XLIII", "path": "justin/43.txt"},
    "963":     {"author": None, "title": "Justin XIVL", "path": "justin/44.txt"},
    "964":     {"author": None, "title": "Justin V", "path": "justin/5.txt"},
    "965":     {"author": None, "title": "Justin VI", "path": "justin/6.txt"},
    "966":     {"author": None, "title": "Justin VII", "path": "justin/7.txt"},
    "967":     {"author": None, "title": "Justin VIII", "path": "justin/8.txt"},
    "968":     {"author": None, "title": "Justin IX", "path": "justin/9.txt"},
    "969":     {"author": "Justin", "title": "Praefatio", "path": "justin/praefatio.txt"},
    "970":     {"author": "Justin", "title": "Prologues", "path": "justin/prologi.txt"},
    "971":     {"author": "Codex of Justinian", "title": "Liber I", "path": "justinian/codex1.txt"},
    "972":     {"author": "Codex of Justinian", "title": "Liber X", "path": "justinian/codex10.txt"},
    "973":     {"author": "Codex of Justinian", "title": "Liber XI", "path": "justinian/codex11.txt"},
    "974":     {"author": "Codex of Justinian", "title": "Liber XII", "path": "justinian/codex12.txt"},
    "975":     {"author": "Codex of Justinian", "title": "Liber II", "path": "justinian/codex2.txt"},
    "976":     {"author": "Codex of Justinian", "title": "Liber III", "path": "justinian/codex3.txt"},
    "977":     {"author": "Codex of Justinian", "title": "Liber IV", "path": "justinian/codex4.txt"},
    "978":     {"author": "Codex of Justinian", "title": "Liber V", "path": "justinian/codex5.txt"},
    "979":     {"author": "Codex of Justinian", "title": "Liber Vi", "path": "justinian/codex6.txt"},
    "980":     {"author": "Codex of Justinian", "title": "Liber VII", "path": "justinian/codex7.txt"},
    "981":     {"author": "Codex of Justinian", "title": "Liber VIII", "path": "justinian/codex8.txt"},
    "982":     {"author": "Codex of Justinian", "title": "Liber IX", "path": "justinian/codex9.txt"},
    "983":     {"author": "Digest of Justinian", "title": "Liber I", "path": "justinian/digest1.txt"},
    "984":     {"author": "Digest of Justinian", "title": "Liber X", "path": "justinian/digest10.txt"},
    "985":     {"author": "Digest of Justinian", "title": "Liber XI", "path": "justinian/digest11.txt"},
    "986":     {"author": "Digest of Justinian", "title": "Liber XI", "path": "justinian/digest12.txt"},
    "987":     {"author": "Digest of Justinian", "title": "Liber XIII", "path": "justinian/digest13.txt"},
    "988":     {"author": "Digest of Justinian", "title": "Liber XIV", "path": "justinian/digest14.txt"},
    "989":     {"author": "Digest of Justinian", "title": "Liber XV", "path": "justinian/digest15.txt"},
    "990":     {"author": "Digest of Justinian", "title": "Liber XVI", "path": "justinian/digest16.txt"},
    "991":     {"author": "Digest of Justinian", "title": "Liber XVII", "path": "justinian/digest17.txt"},
    "992":     {"author": "Digest of Justinian", "title": "Liber XVIII", "path": "justinian/digest18.txt"},
    "993":     {"author": "Digest of Justinian", "title": "Liber XIX", "path": "justinian/digest19.txt"},
    "994":     {"author": "Digest of Justinian", "title": "Liber II", "path": "justinian/digest2.txt"},
    "995":     {"author": "Digest of Justinian", "title": "Liber XXX", "path": "justinian/digest20.txt"},
    "996":     {"author": "Digest of Justinian", "title": "Liber XXI", "path": "justinian/digest21.txt"},
    "997":     {"author": "Digest of Justinian", "title": "Liber XXII", "path": "justinian/digest22.txt"},
    "998":     {"author": "Digest of Justinian", "title": "Liber XXIII", "path": "justinian/digest23.txt"},
    "999":     {"author": "Digest of Justinian", "title": "Liber XXIV", "path": "justinian/digest24.txt"},
    "1000":    {"author": "Digest of Justinian", "title": "Liber XXV", "path": "justinian/digest25.txt"},
    "1001":    {"author": "Digest of Justinian", "title": "Liber XXVI", "path": "justinian/digest26.txt"},
    "1002":    {"author": "Digest of Justinian", "title": "Liber XXVII", "path": "justinian/digest27.txt"},
    "1003":    {"author": "Digest of Justinian", "title": "Liber XXVIII", "path": "justinian/digest28.txt"},
    "1004":    {"author": "Digest of Justinian", "title": "Liber XXIX", "path": "justinian/digest29.txt"},
    "1005":    {"author": "Digest of Justinian", "title": "Liber IIII", "path": "justinian/digest3.txt"},
    "1006":    {"author": "Digest of Justinian", "title": "Liber XXX", "path": "justinian/digest30.txt"},
    "1007":    {"author": "Digest of Justinian", "title": "Liber XXXI", "path": "justinian/digest31.txt"},
    "1008":    {"author": "Digest of Justinian", "title": "Liber XXXII", "path": "justinian/digest32.txt"},
    "1009":    {"author": "Digest of Justinian", "title": "Liber XXXIII", "path": "justinian/digest33.txt"},
    "1010":    {"author": "Digest of Justinian", "title": "Liber XXXIV", "path": "justinian/digest34.txt"},
    "1011":    {"author": "Digest of Justinian", "title": "Liber XXXV", "path": "justinian/digest35.txt"},
    "1012":    {"author": "Digest of Justinian", "title": "Liber XXXVI", "path": "justinian/digest36.txt"},
    "1013":    {"author": "Digest of Justinian", "title": "Liber XXXVII", "path": "justinian/digest37.txt"},
    "1014":    {"author": "Digest of Justinian", "title": "Liber XXXVIII", "path": "justinian/digest38.txt"},
    "1015":    {"author": "Digest of Justinian", "title": "Liber XXXIX", "path": "justinian/digest39.txt"},
    "1016":    {"author": "Digest of Justinian", "title": "Liber IV", "path": "justinian/digest4.txt"},
    "1017":    {"author": "Digest of Justinian", "title": "Liber LX", "path": "justinian/digest40.txt"},
    "1018":    {"author": "Digest of Justinian", "title": "Liber LXI", "path": "justinian/digest41.txt"},
    "1019":    {"author": "Digest of Justinian", "title": "Liber LXII", "path": "justinian/digest42.txt"},
    "1020":    {"author": "Digest of Justinian", "title": "Liber LXIII", "path": "justinian/digest43.txt"},
    "1021":    {"author": "Digest of Justinian", "title": "Liber LXIV", "path": "justinian/digest44.txt"},
    "1022":    {"author": "Digest of Justinian", "title": "Liber XLV", "path": "justinian/digest45.txt"},
    "1023":    {"author": "Digest of Justinian", "title": "Liber LXVI", "path": "justinian/digest46.txt"},
    "1024":    {"author": "Digest of Justinian", "title": "Liber XLVII", "path": "justinian/digest47.txt"},
    "1025":    {"author": "Digest of Justinian", "title": "Liber XLVIII", "path": "justinian/digest48.txt"},
    "1026":    {"author": "Digest of Justinian", "title": "Liber XLI", "path": "justinian/digest49.txt"},
    "1027":    {"author": "Digest of Justinian", "title": "Liber V", "path": "justinian/digest5.txt"},
    "1028":    {"author": "Digest of Justinian", "title": "Liber L", "path": "justinian/digest50.txt"},
    "1029":    {"author": "Digest of Justinian", "title": "Liber VI", "path": "justinian/digest6.txt"},
    "1030":    {"author": "Digest of Justinian", "title": "Liber VII", "path": "justinian/digest7.txt"},
    "1031":    {"author": "Digest of Justinian", "title": "Liber VIII", "path": "justinian/digest8.txt"},
    "1032":    {"author": "Digest of Justinian", "title": "Liber IX", "path": "justinian/digest9.txt"}, "1033": {
        "author": "The Institutes of Justinian", "title": "Introduction", "path": "justinian/institutes.proem.txt"
    }, "1034": {"author": "The Institutes of Justinian", "title": "Book 1", "path": "justinian/institutes1.txt"},
    "1035":    {"author": "The Institutes of Justinian", "title": "Book 1", "path": "justinian/institutes2.txt"},
    "1036":    {"author": "The Institutes of Justinian", "title": "Book 3", "path": "justinian/institutes3.txt"},
    "1037":    {"author": "The Institutes of Justinian", "title": "Book 4", "path": "justinian/institutes4.txt"},
    "1038":    {"author": "Juvenal", "title": "Satires I", "path": "juvenal/1.txt"},
    "1039":    {"author": "Juvenal", "title": "Satires X", "path": "juvenal/10.txt"},
    "1040":    {"author": "Juvenal", "title": "Satires XI", "path": "juvenal/11.txt"},
    "1041":    {"author": "Juvenal", "title": "Satires XII", "path": "juvenal/12.txt"},
    "1042":    {"author": "Juvenal", "title": "Satires XIII", "path": "juvenal/13.txt"},
    "1043":    {"author": "Juvenal", "title": "Satires XIV", "path": "juvenal/14.txt"},
    "1044":    {"author": "Juvenal", "title": "Satires XV", "path": "juvenal/15.txt"},
    "1045":    {"author": "Juvenal", "title": "Satires XVI", "path": "juvenal/16.txt"},
    "1046":    {"author": "Juvenal", "title": "Satires II", "path": "juvenal/2.txt"},
    "1047":    {"author": "Juvenal", "title": "Satires III", "path": "juvenal/3.txt"},
    "1048":    {"author": "Juvenal", "title": "Satires IV", "path": "juvenal/4.txt"},
    "1049":    {"author": "Juvenal", "title": "Satires V", "path": "juvenal/5.txt"},
    "1050":    {"author": "Juvenal", "title": "Satires VI", "path": "juvenal/6.txt"},
    "1051":    {"author": "Juvenal", "title": "Satires VII", "path": "juvenal/7.txt"},
    "1052":    {"author": "Juvenal", "title": "Satires VIII", "path": "juvenal/8.txt"},
    "1053":    {"author": "Juvenal", "title": "Satires IX", "path": "juvenal/9.txt"},
    "1054":    {"author": None, "title": "Liber Kalilae et Dimnae", "path": "kalila.txt"}, "1055": {
        "author": "THOMAS \u00c0 KEMPIS", "title": "DE IMITATIONE CHRISTI LIBER PRIMUS", "path": "kempis/kempis1.txt"
    }, "1056": {
        "author": "THOMAS \u00c0 KEMPIS", "title": "DE IMITATIONE CHRISTI LIBER SECUNDUS", "path": "kempis/kempis2.txt"
    }, "1057": {
        "author": "THOMAS \u00c0 KEMPIS", "title": "DE IMITATIONE CHRISTI LIBER TERTIUS", "path": "kempis/kempis3.txt"
    }, "1058": {
        "author": "THOMAS \u00c0 KEMPIS", "title": "DE IMITATIONE CHRISTI LIBER QUARTUS", "path": "kempis/kempis4.txt"
    }, "1059": {"author": "JOANNIS KEPLERI", "title": "STRENA SEU DE NIVE SEXANGULA", "path": "kepler/strena.txt"},
    "1060":    {"author": "Lactantius", "title": "de Mortibus Persecutorum", "path": "lactantius/demort.txt"},
    "1061":    {"author": "Lactantius", "title": "Divinarum Institutionum Liber I", "path": "lactantius/divinst1.txt"},
    "1062":    {"author": "Dry Sticks Fagoted", "title": "1858 ", "path": "landor.1858.txt"},
    "1063":    {"author": None, "title": "", "path": "landor1795.txt"},
    "1064":    {"author": "Simonidea", "title": "1806 ", "path": "landor1806.txt"},
    "1065":    {"author": "Landor", "title": "Simonidea, 1806 ", "path": "landor1810.txt"},
    "1066":    {"author": None, "title": "Legenda Maior Sancti Regis Stephani", "path": "legenda.stephani.txt"},
    "1067":    {"author": "Leo of Naples", "title": "Historia de preliis Alexandri Magni", "path": "leo1.txt"},
    "1068":    {"author": "Leo of Naples", "title": "Historia de preliis Alexandri Magni", "path": "leo2.txt"},
    "1069":    {"author": "Leo of Naples", "title": "Historia de preliis Alexandri Magni", "path": "leo3.txt"},
    "1070":    {"author": None, "title": "Leo the Great ", "path": "leothegreat/quadragesima1.txt"},
    "1071":    {"author": None, "title": "Leo the Great ", "path": "leothegreat/quadragesima2.txt"},
    "1072":    {"author": "Anonymous", "title": "Letabundus rediit ", "path": "letabundus.txt"},
    "1073":    {"author": None, "title": "", "path": "levis.txt"},
    "1074":    {"author": "Lhomond", "title": "Epitome historiae sacrae", "path": "lhomond.historiae.txt"},
    "1075":    {"author": "Lhomond", "title": "de viris illustribus", "path": "lhomond.viris.txt"},
    "1076":    {"author": None, "title": "Liber Pontificalis", "path": "liberpontificalis1.txt"},
    "1077":    {"author": "Livy", "title": "Book I", "path": "livy/liv.1.txt"},
    "1078":    {"author": "Livy", "title": "Book X", "path": "livy/liv.10.txt"},
    "1079":    {"author": "Livy", "title": "Book II", "path": "livy/liv.2.txt"},
    "1080":    {"author": "Livy", "title": "Book XXI", "path": "livy/liv.21.txt"},
    "1081":    {"author": "Livy", "title": "Book XXII", "path": "livy/liv.22.txt"},
    "1082":    {"author": "Livy", "title": "Book XXIII", "path": "livy/liv.23.txt"},
    "1083":    {"author": "Livy", "title": "Book XXIV", "path": "livy/liv.24.txt"},
    "1084":    {"author": "Livy", "title": "Book XXV", "path": "livy/liv.25.txt"},
    "1085":    {"author": "Livy", "title": "Book XXVI", "path": "livy/liv.26.txt"},
    "1086":    {"author": "Livy", "title": "Book XXVII", "path": "livy/liv.27.txt"},
    "1087":    {"author": "Livy", "title": "Book XXVIII", "path": "livy/liv.28.txt"},
    "1088":    {"author": "Livy", "title": "Book XXIX", "path": "livy/liv.29.txt"},
    "1089":    {"author": "Livy", "title": "Book III", "path": "livy/liv.3.txt"},
    "1090":    {"author": "Livy", "title": "Book XXX", "path": "livy/liv.30.txt"},
    "1091":    {"author": "Livy", "title": "Book XXXI", "path": "livy/liv.31.txt"},
    "1092":    {"author": "Livy", "title": "Book XXXII", "path": "livy/liv.32.txt"},
    "1093":    {"author": "Livy", "title": "Book XXXIII", "path": "livy/liv.33.txt"},
    "1094":    {"author": "Livy", "title": "Book XXXIV", "path": "livy/liv.34.txt"},
    "1095":    {"author": "Livy", "title": "Book XXXV", "path": "livy/liv.35.txt"},
    "1096":    {"author": "Livy", "title": "Book XXXVI", "path": "livy/liv.36.txt"},
    "1097":    {"author": "Livy", "title": "Book XXXVII", "path": "livy/liv.37.txt"},
    "1098":    {"author": "Livy", "title": "Book XXXVIII", "path": "livy/liv.38.txt"},
    "1099":    {"author": "Livy", "title": "Book XXXIX", "path": "livy/liv.39.txt"},
    "1100":    {"author": "Livy", "title": "Book IV", "path": "livy/liv.4.txt"},
    "1101":    {"author": "Livy", "title": "Book XL", "path": "livy/liv.40.txt"},
    "1102":    {"author": "Livy", "title": "Book XLI", "path": "livy/liv.41.txt"},
    "1103":    {"author": "Livy", "title": "Book XLII", "path": "livy/liv.42.txt"},
    "1104":    {"author": "Livy", "title": "Book XLIII", "path": "livy/liv.43.txt"},
    "1105":    {"author": "Livy", "title": "Book XLIV", "path": "livy/liv.44.txt"},
    "1106":    {"author": "Livy", "title": "Book XLV", "path": "livy/liv.45.txt"},
    "1107":    {"author": "Livy", "title": "Book V", "path": "livy/liv.5.txt"},
    "1108":    {"author": "Livy", "title": "Book VI", "path": "livy/liv.6.txt"},
    "1109":    {"author": "Livy", "title": "Book VII", "path": "livy/liv.7.txt"},
    "1110":    {"author": "Livy", "title": "Book VIII", "path": "livy/liv.8.txt"},
    "1111":    {"author": "Livy", "title": "Book IX", "path": "livy/liv.9.txt"},
    "1112":    {"author": "Livy", "title": "Periochae", "path": "livy/liv.per.txt"},
    "1113":    {"author": "Livy", "title": "Periocha I", "path": "livy/liv.per1.txt"},
    "1114":    {"author": "Livy", "title": "Periocha X", "path": "livy/liv.per10.txt"},
    "1115":    {"author": "Livy", "title": "Periocha C", "path": "livy/liv.per100.txt"},
    "1116":    {"author": "Livy", "title": "Periocha CI", "path": "livy/liv.per101.txt"},
    "1117":    {"author": "Livy", "title": "Periocha CII", "path": "livy/liv.per102.txt"},
    "1118":    {"author": "Livy", "title": "Periocha CIII", "path": "livy/liv.per103.txt"},
    "1119":    {"author": "Livy", "title": "Periocha CIV", "path": "livy/liv.per104.txt"},
    "1120":    {"author": "Livy", "title": "Periocha CV", "path": "livy/liv.per105.txt"},
    "1121":    {"author": "Livy", "title": "Periocha CVI", "path": "livy/liv.per106.txt"},
    "1122":    {"author": "Livy", "title": "Periocha CVII", "path": "livy/liv.per107.txt"},
    "1123":    {"author": "Livy", "title": "Periocha CVIII", "path": "livy/liv.per108.txt"},
    "1124":    {"author": "Livy", "title": "Periocha CIX", "path": "livy/liv.per109.txt"},
    "1125":    {"author": "Livy", "title": "Periocha XI", "path": "livy/liv.per11.txt"},
    "1126":    {"author": "Livy", "title": "Periocha CX", "path": "livy/liv.per110.txt"},
    "1127":    {"author": "Livy", "title": "Periocha CXI", "path": "livy/liv.per111.txt"},
    "1128":    {"author": "Livy", "title": "Periocha CXII", "path": "livy/liv.per112.txt"},
    "1129":    {"author": "Livy", "title": "Periocha CXIII", "path": "livy/liv.per113.txt"},
    "1130":    {"author": "Livy", "title": "Periocha CXIV", "path": "livy/liv.per114.txt"},
    "1131":    {"author": "Livy", "title": "Periocha CXV", "path": "livy/liv.per115.txt"},
    "1132":    {"author": "Livy", "title": "Periocha CXVI", "path": "livy/liv.per116.txt"},
    "1133":    {"author": "Livy", "title": "Periocha CXVII", "path": "livy/liv.per117.txt"},
    "1134":    {"author": "Livy", "title": "Periocha CXVIII", "path": "livy/liv.per118.txt"},
    "1135":    {"author": "Livy", "title": "Periocha CXIX", "path": "livy/liv.per119.txt"},
    "1136":    {"author": "Livy", "title": "Periocha XII", "path": "livy/liv.per12.txt"},
    "1137":    {"author": "Livy", "title": "Periocha CXX", "path": "livy/liv.per120.txt"},
    "1138":    {"author": "Livy", "title": "Periocha CXXI", "path": "livy/liv.per121.txt"},
    "1139":    {"author": "Livy", "title": "Periocha CXXII", "path": "livy/liv.per122.txt"},
    "1140":    {"author": "Livy", "title": "Periocha CXXIII", "path": "livy/liv.per123.txt"},
    "1141":    {"author": "Livy", "title": "Periocha CXXIV", "path": "livy/liv.per124.txt"},
    "1142":    {"author": "Livy", "title": "Periocha CXXV", "path": "livy/liv.per125.txt"},
    "1143":    {"author": "Livy", "title": "Periocha CXXVI", "path": "livy/liv.per126.txt"},
    "1144":    {"author": "Livy", "title": "Periocha CXXVII", "path": "livy/liv.per127.txt"},
    "1145":    {"author": "Livy", "title": "Periocha CXXVIII", "path": "livy/liv.per128.txt"},
    "1146":    {"author": "Livy", "title": "Periocha CXXIX", "path": "livy/liv.per129.txt"},
    "1147":    {"author": "Livy", "title": "Periocha XIII", "path": "livy/liv.per13.txt"},
    "1148":    {"author": "Livy", "title": "Periocha CXXX", "path": "livy/liv.per130.txt"},
    "1149":    {"author": "Livy", "title": "Periocha CXXXI", "path": "livy/liv.per131.txt"},
    "1150":    {"author": "Livy", "title": "Periocha CXXXII", "path": "livy/liv.per132.txt"},
    "1151":    {"author": "Livy", "title": "Periocha CXXXIII", "path": "livy/liv.per133.txt"},
    "1152":    {"author": "Livy", "title": "Periocha CXXXIV", "path": "livy/liv.per134.txt"},
    "1153":    {"author": "Livy", "title": "Periocha CXXXV", "path": "livy/liv.per135.txt"},
    "1154":    {"author": "Livy", "title": "Periocha CXXXVI et CXXXVII", "path": "livy/liv.per136-7.txt"},
    "1155":    {"author": "Livy", "title": "Periocha CXXXVIII", "path": "livy/liv.per138.txt"},
    "1156":    {"author": "Livy", "title": "Periocha CXXXIX", "path": "livy/liv.per139.txt"},
    "1157":    {"author": "Livy", "title": "Periocha XIV", "path": "livy/liv.per14.txt"},
    "1158":    {"author": "Livy", "title": "Periocha CXL", "path": "livy/liv.per140.txt"},
    "1159":    {"author": "Livy", "title": "Periocha CXLI", "path": "livy/liv.per141.txt"},
    "1160":    {"author": "Livy", "title": "Periocha CXLII", "path": "livy/liv.per142.txt"},
    "1161":    {"author": "Livy", "title": "Periocha XV", "path": "livy/liv.per15.txt"},
    "1162":    {"author": "Livy", "title": "Periocha XVI", "path": "livy/liv.per16.txt"},
    "1163":    {"author": "Livy", "title": "Periocha XVI", "path": "livy/liv.per17.txt"},
    "1164":    {"author": "Livy", "title": "Periocha XVIII", "path": "livy/liv.per18.txt"},
    "1165":    {"author": "Livy", "title": "Periocha XIX", "path": "livy/liv.per19.txt"},
    "1166":    {"author": "Livy", "title": "Periocha II", "path": "livy/liv.per2.txt"},
    "1167":    {"author": "Livy", "title": "Periocha XX", "path": "livy/liv.per20.txt"},
    "1168":    {"author": "Livy", "title": "Periocha XXI", "path": "livy/liv.per21.txt"},
    "1169":    {"author": "Livy", "title": "Periocha XXII", "path": "livy/liv.per22.txt"},
    "1170":    {"author": "Livy", "title": "Periocha XXIII", "path": "livy/liv.per23.txt"},
    "1171":    {"author": "Livy", "title": "Periocha XXIV", "path": "livy/liv.per24.txt"},
    "1172":    {"author": "Livy", "title": "Periocha XXV", "path": "livy/liv.per25.txt"},
    "1173":    {"author": "Livy", "title": "Periocha XXVI", "path": "livy/liv.per26.txt"},
    "1174":    {"author": "Livy", "title": "Periocha XXVII", "path": "livy/liv.per27.txt"},
    "1175":    {"author": "Livy", "title": "Periocha XXVIII", "path": "livy/liv.per28.txt"},
    "1176":    {"author": "Livy", "title": "Periocha XXIX", "path": "livy/liv.per29.txt"},
    "1177":    {"author": "Livy", "title": "Periocha III", "path": "livy/liv.per3.txt"},
    "1178":    {"author": "Livy", "title": "Periocha XXX", "path": "livy/liv.per30.txt"},
    "1179":    {"author": "Livy", "title": "Periocha XXXI", "path": "livy/liv.per31.txt"},
    "1180":    {"author": "Livy", "title": "Periocha XXXII", "path": "livy/liv.per32.txt"},
    "1181":    {"author": "Livy", "title": "Periocha XXXIII", "path": "livy/liv.per33.txt"},
    "1182":    {"author": "Livy", "title": "Periocha XXXIV", "path": "livy/liv.per34.txt"},
    "1183":    {"author": "Livy", "title": "Periocha XXXV", "path": "livy/liv.per35.txt"},
    "1184":    {"author": "Livy", "title": "Periocha XXXVI", "path": "livy/liv.per36.txt"},
    "1185":    {"author": "Livy", "title": "Periocha XXXVII", "path": "livy/liv.per37.txt"},
    "1186":    {"author": "Livy", "title": "Periocha XXXVIII", "path": "livy/liv.per38.txt"},
    "1187":    {"author": "Livy", "title": "Periocha XXXIX", "path": "livy/liv.per39.txt"},
    "1188":    {"author": "Livy", "title": "Periocha IV", "path": "livy/liv.per4.txt"},
    "1189":    {"author": "Livy", "title": "Periocha XL", "path": "livy/liv.per40.txt"},
    "1190":    {"author": "Livy", "title": "Periocha XLI", "path": "livy/liv.per41.txt"},
    "1191":    {"author": "Livy", "title": "Periocha XLII", "path": "livy/liv.per42.txt"},
    "1192":    {"author": "Livy", "title": "Periocha XLIII", "path": "livy/liv.per43.txt"},
    "1193":    {"author": "Livy", "title": "Periocha XLIV", "path": "livy/liv.per44.txt"},
    "1194":    {"author": "Livy", "title": "Periocha XLV", "path": "livy/liv.per45.txt"},
    "1195":    {"author": "Livy", "title": "Periocha XLVI", "path": "livy/liv.per46.txt"},
    "1196":    {"author": "Livy", "title": "Periocha XLVII", "path": "livy/liv.per47.txt"},
    "1197":    {"author": "Livy", "title": "Periocha XLVIII", "path": "livy/liv.per48.txt"},
    "1198":    {"author": "Livy", "title": "Periocha XLIX", "path": "livy/liv.per49.txt"},
    "1199":    {"author": "Livy", "title": "Periocha V", "path": "livy/liv.per5.txt"},
    "1200":    {"author": "Livy", "title": "Periocha L", "path": "livy/liv.per50.txt"},
    "1201":    {"author": "Livy", "title": "Periocha LI", "path": "livy/liv.per51.txt"},
    "1202":    {"author": "Livy", "title": "Periocha LII", "path": "livy/liv.per52.txt"},
    "1203":    {"author": "Livy", "title": "Periocha LIII", "path": "livy/liv.per53.txt"},
    "1204":    {"author": "Livy", "title": "Periocha LIV", "path": "livy/liv.per54.txt"},
    "1205":    {"author": "Livy", "title": "Periocha LV", "path": "livy/liv.per55.txt"},
    "1206":    {"author": "Livy", "title": "Periocha LVI", "path": "livy/liv.per56.txt"},
    "1207":    {"author": "Livy", "title": "Periocha LVII", "path": "livy/liv.per57.txt"},
    "1208":    {"author": "Livy", "title": "Periocha LVIII", "path": "livy/liv.per58.txt"},
    "1209":    {"author": "Livy", "title": "Periocha LIX", "path": "livy/liv.per59.txt"},
    "1210":    {"author": "Livy", "title": "Periocha VI", "path": "livy/liv.per6.txt"},
    "1211":    {"author": "Livy", "title": "Periocha LX", "path": "livy/liv.per60.txt"},
    "1212":    {"author": "Livy", "title": "Periocha LXI", "path": "livy/liv.per61.txt"},
    "1213":    {"author": "Livy", "title": "Periocha LXII", "path": "livy/liv.per62.txt"},
    "1214":    {"author": "Livy", "title": "Periocha LXIII", "path": "livy/liv.per63.txt"},
    "1215":    {"author": "Livy", "title": "Periocha LXIV", "path": "livy/liv.per64.txt"},
    "1216":    {"author": "Livy", "title": "Periocha LXV", "path": "livy/liv.per65.txt"},
    "1217":    {"author": "Livy", "title": "Periocha LXVI", "path": "livy/liv.per66.txt"},
    "1218":    {"author": "Livy", "title": "Periocha LXVII", "path": "livy/liv.per67.txt"},
    "1219":    {"author": "Livy", "title": "Periocha LXVIII", "path": "livy/liv.per68.txt"},
    "1220":    {"author": "Livy", "title": "Periocha LXIX", "path": "livy/liv.per69.txt"},
    "1221":    {"author": "Livy", "title": "Periocha VII", "path": "livy/liv.per7.txt"},
    "1222":    {"author": "Livy", "title": "Periocha LXX", "path": "livy/liv.per70.txt"},
    "1223":    {"author": "Livy", "title": "Periocha LXXI", "path": "livy/liv.per71.txt"},
    "1224":    {"author": "Livy", "title": "Periocha LXXII", "path": "livy/liv.per72.txt"},
    "1225":    {"author": "Livy", "title": "Periocha LXXIII", "path": "livy/liv.per73.txt"},
    "1226":    {"author": "Livy", "title": "Periocha LXXIV", "path": "livy/liv.per74.txt"},
    "1227":    {"author": "Livy", "title": "Periocha LXXV", "path": "livy/liv.per75.txt"},
    "1228":    {"author": "Livy", "title": "Periocha LXXVI", "path": "livy/liv.per76.txt"},
    "1229":    {"author": "Livy", "title": "Periocha LXXVII", "path": "livy/liv.per77.txt"},
    "1230":    {"author": "Livy", "title": "Periocha LXXVIII", "path": "livy/liv.per78.txt"},
    "1231":    {"author": "Livy", "title": "Periocha LXXIX", "path": "livy/liv.per79.txt"},
    "1232":    {"author": "Livy", "title": "Periocha VIII", "path": "livy/liv.per8.txt"},
    "1233":    {"author": "Livy", "title": "Periocha LXXX", "path": "livy/liv.per80.txt"},
    "1234":    {"author": "Livy", "title": "Periocha LXXXI", "path": "livy/liv.per81.txt"},
    "1235":    {"author": "Livy", "title": "Periocha LXXXII", "path": "livy/liv.per82.txt"},
    "1236":    {"author": "Livy", "title": "Periocha LXXXIII", "path": "livy/liv.per83.txt"},
    "1237":    {"author": "Livy", "title": "Periocha LXXXIV", "path": "livy/liv.per84.txt"},
    "1238":    {"author": "Livy", "title": "Periocha LXXXV", "path": "livy/liv.per85.txt"},
    "1239":    {"author": "Livy", "title": "Periocha LXXXVI", "path": "livy/liv.per86.txt"},
    "1240":    {"author": "Livy", "title": "Periocha LXXXVII", "path": "livy/liv.per87.txt"},
    "1241":    {"author": "Livy", "title": "Periocha LXXXVIII", "path": "livy/liv.per88.txt"},
    "1242":    {"author": "Livy", "title": "Periocha LXXXIX", "path": "livy/liv.per89.txt"},
    "1243":    {"author": "Livy", "title": "Periocha IX", "path": "livy/liv.per9.txt"},
    "1244":    {"author": "Livy", "title": "Periocha XC", "path": "livy/liv.per90.txt"},
    "1245":    {"author": "Livy", "title": "Periocha XCI", "path": "livy/liv.per91.txt"},
    "1246":    {"author": "Livy", "title": "Periocha XCII", "path": "livy/liv.per92.txt"},
    "1247":    {"author": "Livy", "title": "Periocha XCIII", "path": "livy/liv.per93.txt"},
    "1248":    {"author": "Livy", "title": "Periocha XCIV", "path": "livy/liv.per94.txt"},
    "1249":    {"author": "Livy", "title": "Periocha XCV", "path": "livy/liv.per95.txt"},
    "1250":    {"author": "Livy", "title": "Periocha XCVI", "path": "livy/liv.per96.txt"},
    "1251":    {"author": "Livy", "title": "Periocha XCVII", "path": "livy/liv.per97.txt"},
    "1252":    {"author": "Livy", "title": "Periocha XCVIII", "path": "livy/liv.per98.txt"},
    "1253":    {"author": "Livy", "title": "Periocha XCIX", "path": "livy/liv.per99.txt"},
    "1254":    {"author": "Livy", "title": "Preface", "path": "livy/liv.pr.txt"},
    "1255":    {"author": "Lotichius", "title": "De puella infelici", "path": "lotichius.txt"},
    "1256":    {"author": "Lucan", "title": "Liber I", "path": "lucan/lucan1.txt"},
    "1257":    {"author": "Lucan", "title": "Liber X", "path": "lucan/lucan10.txt"},
    "1258":    {"author": "Lucan", "title": "Liber II", "path": "lucan/lucan2.txt"},
    "1259":    {"author": "Lucan", "title": "Liber III", "path": "lucan/lucan3.txt"},
    "1260":    {"author": "Lucan", "title": "Liber IV", "path": "lucan/lucan4.txt"},
    "1261":    {"author": "Lucan", "title": "Liber V", "path": "lucan/lucan5.txt"},
    "1262":    {"author": "Lucan", "title": "Liber VI", "path": "lucan/lucan6.txt"},
    "1263":    {"author": "Lucan", "title": "Liber VII", "path": "lucan/lucan7.txt"},
    "1264":    {"author": "Lucan", "title": "Liber VIII", "path": "lucan/lucan8.txt"},
    "1265":    {"author": "Lucan", "title": "Liber IX", "path": "lucan/lucan9.txt"},
    "1266":    {"author": None, "title": "Ad Lucernarium ", "path": "lucernarium.txt"},
    "1267":    {"author": "Lucretius", "title": "De Rerum Natura I", "path": "lucretius/lucretius1.txt"},
    "1268":    {"author": "Lucretius", "title": "De Rerum Natura II", "path": "lucretius/lucretius2.txt"},
    "1269":    {"author": "Lucretius", "title": "De Rerum Natura III", "path": "lucretius/lucretius3.txt"},
    "1270":    {"author": "Lucretius", "title": "De Rerum Natura IV", "path": "lucretius/lucretius4.txt"},
    "1271":    {"author": "Lucretius", "title": "De Rerum Natura V", "path": "lucretius/lucretius5.txt"},
    "1272":    {"author": "Lucretius", "title": "De Rerum Natura VI", "path": "lucretius/lucretius6.txt"},
    "1273":    {"author": "Luther", "title": "95 Theses ", "path": "luther.95.txt"},
    "1274":    {"author": "Luther", "title": "Letter to Erasmus ", "path": "luther.lteramus.txt"},
    "1275":    {"author": None, "title": "", "path": "luther.praef.txt"},
    "1276":    {"author": None, "title": "Macarius of Alexandria", "path": "macarius.txt"},
    "1277":    {"author": "Marcarius the Great", "title": "Apophthegmata", "path": "macarius1.txt"},
    "1278":    {"author": None, "title": "Magna Carta", "path": "magnacarta.txt"},
    "1279":    {"author": None, "title": "Martyrium Ricardi Archiepiscopi", "path": "maidstone.txt"}, "1280": {
        "author": "Gaufredo Malaterra",
        "title":  "De rebus gestis Rogerii Calabriae et Siciliae Comitis et Roberti Guiscardi Ducis fratris eius",
        "path":   "malaterra1.txt"
    }, "1281": {
        "author": "Gaufredo Malaterra",
        "title":  "De rebus gestis Rogerii Calabriae et Siciliae Comitis et Roberti Guiscardi Ducis fratris eius",
        "path":   "malaterra2.txt"
    }, "1282": {
        "author": "Gaufredo Malaterra",
        "title":  "De rebus gestis Rogerii Calabriae et Siciliae Comitis et Roberti Guiscardi Ducis fratris eius",
        "path":   "malaterra3.txt"
    }, "1283": {
        "author": "Gaufredo Malaterra",
        "title":  "De rebus gestis Rogerii Calabriae et Siciliae Comitis et Roberti Guiscardi Ducis fratris eius",
        "path":   "malaterra4.txt"
    }, "1284": {"author": "Manilius", "title": "Liber I", "path": "manilius1.txt"},
    "1285":    {"author": "Manilius", "title": "Liber II", "path": "manilius2.txt"},
    "1286":    {"author": "Manilius", "title": "Liber IIi", "path": "manilius3.txt"},
    "1287":    {"author": "Manilius", "title": "Liber IV", "path": "manilius4.txt"},
    "1288":    {"author": "Manilius", "title": "Liber V", "path": "manilius5.txt"},
    "1289":    {"author": "Walter Mapps", "title": "de Mauro et Zoilo", "path": "mapps1.txt"},
    "1290":    {"author": "Walter Mapps", "title": "de Phillide et Flora", "path": "mapps2.txt"},
    "1291":    {"author": "Marbodus", "title": "Libellus de ornamentis verborum", "path": "marbodus.txt"},
    "1292":    {"author": None, "title": "Marcellinus Comes", "path": "marcellinus1.txt"},
    "1293":    {"author": None, "title": "Marcellinus Comes", "path": "marcellinus2.txt"},
    "1294":    {"author": "Martial", "title": "Liber de Spectaculis", "path": "martial/mart.spec.txt"},
    "1295":    {"author": None, "title": "Martial I", "path": "martial/mart1.txt"},
    "1296":    {"author": None, "title": "Martial X", "path": "martial/mart10.txt"},
    "1297":    {"author": None, "title": "Martial XI", "path": "martial/mart11.txt"},
    "1298":    {"author": None, "title": "Martial XII", "path": "martial/mart12.txt"},
    "1299":    {"author": None, "title": "Martial XIII", "path": "martial/mart13.txt"},
    "1300":    {"author": "Martial", "title": "Apophoreta", "path": "martial/mart14.txt"},
    "1301":    {"author": None, "title": "Martial II", "path": "martial/mart2.txt"},
    "1302":    {"author": None, "title": "Martial III", "path": "martial/mart3.txt"},
    "1303":    {"author": None, "title": "Martial IV", "path": "martial/mart4.txt"},
    "1304":    {"author": None, "title": "Martial V", "path": "martial/mart5.txt"},
    "1305":    {"author": None, "title": "Martial VI", "path": "martial/mart6.txt"},
    "1306":    {"author": None, "title": "Martial VII", "path": "martial/mart7.txt"},
    "1307":    {"author": None, "title": "Martial VIII", "path": "martial/mart8.txt"},
    "1308":    {"author": None, "title": "Martial IX", "path": "martial/mart9.txt"}, "1309": {
        "author": "Martin of Braga", "title": "Capitula ex orientalium patrum synodis",
        "path":   "martinbraga/capitula.txt"
    }, "1310": {
        "author": "Martin of Braga", "title": "Concilium Bracarense Primum", "path": "martinbraga/concilium1.txt"
    }, "1311": {
        "author": "Martin of Braga", "title": "Concilium Bracarense Secundum", "path": "martinbraga/concilium2.txt"
    }, "1312": {"author": "Martin of Braga", "title": "Exhortatio Humilitatis", "path": "martinbraga/exhortatio.txt"},
    "1313":    {"author": "Martin of Braga", "title": "Formula Vitae Honestae", "path": "martinbraga/formula.txt"},
    "1314":    {"author": "Martin of Braga", "title": "de Trina Mersione", "path": "martinbraga/ira.txt"},
    "1315":    {"author": "Martin of Braga", "title": "de Pascha", "path": "martinbraga/pascha.txt"},
    "1316":    {"author": "Martin of Braga", "title": "Versus", "path": "martinbraga/poems.txt"},
    "1317":    {"author": "Martin of Braga", "title": "pro Repellenda Iactantia", "path": "martinbraga/repellenda.txt"},
    "1318":    {"author": "Martin of Braga", "title": "de Correctione Rusticorum", "path": "martinbraga/rusticus.txt"},
    "1319":    {
        "author": "Martin of Braga", "title": "Sententiae Patrum Aegyptiorum", "path": "martinbraga/sententiae.txt"
    }, "1320": {"author": "Martin of Braga", "title": "Item de Superbia", "path": "martinbraga/superbia.txt"},
    "1321":    {"author": "Martin of Braga", "title": "de Trina Mersione", "path": "martinbraga/trina.txt"},
    "1322":    {"author": None, "title": "Michele Marullo", "path": "marullo.txt"},
    "1323":    {"author": None, "title": "Karl Marx", "path": "marx.txt"},
    "1324":    {"author": "Maximianus", "title": "Elegies", "path": "maximianus.txt"},
    "1325":    {"author": "May", "title": "Liber I", "path": "may/may1.txt"},
    "1326":    {"author": "May", "title": "Liber II", "path": "may/may2.txt"},
    "1327":    {"author": "May", "title": "Liber III", "path": "may/may3.txt"},
    "1328":    {"author": "May", "title": "Liber IV", "path": "may/may4.txt"},
    "1329":    {"author": "May", "title": "Liber V", "path": "may/may5.txt"},
    "1330":    {"author": "May", "title": "Liber VI", "path": "may/may6.txt"},
    "1331":    {"author": "May", "title": "Liber VII", "path": "may/may7.txt"},
    "1332":    {"author": "May", "title": "Title Page", "path": "may/maytitle.txt"},
    "1333":    {"author": "Melanchthon", "title": "The Augsburg Confession", "path": "melanchthon/conf.txt"},
    "1334":    {"author": "Melanchthon", "title": "Life of Luther", "path": "melanchthon/hist.txt"}, "1335": {
        "author": "Melanchthon", "title": "De Laude Vitae Scholasticae Oratio", "path": "melanchthon/laude.txt"
    }, "1336": {"author": "Melanchthon", "title": "De Obitu Martini Lutheri", "path": "melanchthon/obitu.txt"},
    "1337":    {"author": "John Milton", "title": "In Quintum Novembris", "path": "milton.quintnov.txt"},
    "1338":    {"author": "M. Minucius Felix", "title": "Octavius", "path": "minucius.txt"},
    "1339":    {"author": None, "title": "Mirabilia Urbis Romae", "path": "mirabilia.txt"},
    "1340":    {"author": "Gregorius", "title": "Narratio de Mirabilibus Urbis Romae", "path": "mirabilia1.txt"},
    "1341":    {"author": None, "title": "Carmina Ioannis Pici Mirandulae", "path": "mirandola/mir1.txt"},
    "1342":    {"author": None, "title": "Carmina Ioannis Pici Mirandulae", "path": "mirandola/mir2.txt"},
    "1343":    {"author": None, "title": "Carmina Ioannis Pici Mirandulae", "path": "mirandola/mir3.txt"},
    "1344":    {"author": None, "title": "Carmina Ioannis Pici Mirandulae", "path": "mirandola/mir4.txt"},
    "1345":    {"author": None, "title": "Carmina Ioannis Pici Mirandulae", "path": "mirandola/mir5.txt"},
    "1346":    {"author": None, "title": "Carmina Ioannis Pici Mirandulae", "path": "mirandola/mir6.txt"},
    "1347":    {"author": None, "title": "Carmina Ioannis Pici Mirandulae", "path": "mirandola/mir7.txt"},
    "1348":    {"author": None, "title": "Carmina Ioannis Pici Mirandulae", "path": "mirandola/mir8.txt"},
    "1349":    {"author": None, "title": "Carmina Ioannis Pici Mirandulae", "path": "mirandola/mir9.txt"}, "1350": {
        "author": "Pico della Mirandola", "title": "Oratio de hominis dignitate", "path": "mirandola/oratio.txt"
    }, "1351": {"author": "Fabricius Montanus", "title": "De Wilhelmo Thellio elegia", "path": "montanus.txt"},
    "1352":    {"author": None, "title": "Thomas More", "path": "more.txt"},
    "1353":    {"author": None, "title": "Musa venit carmine ", "path": "musavenit.txt"},
    "1354":    {"author": None, "title": "Naevius", "path": "naevius.txt"},
    "1355":    {"author": None, "title": "Naugerius", "path": "navagero.txt"},
    "1356":    {"author": "Nemesianus", "title": "Ecloga I", "path": "nemesianus1.txt"},
    "1357":    {"author": "Nemesianus", "title": "Ecloga II", "path": "nemesianus2.txt"},
    "1358":    {"author": "Nemesianus", "title": "Ecloga III", "path": "nemesianus3.txt"},
    "1359":    {"author": "Nemesianus", "title": "Ecloga IV", "path": "nemesianus4.txt"},
    "1360":    {"author": "Nepos", "title": "Life of Agesilaus", "path": "nepos/nepos.age.txt"},
    "1361":    {"author": "Nepos", "title": "Life of Alcibiades", "path": "nepos/nepos.alc.txt"},
    "1362":    {"author": "Nepos", "title": "Life of Aristides", "path": "nepos/nepos.aris.txt"},
    "1363":    {"author": "Nepos", "title": "Life of Atticus", "path": "nepos/nepos.att.txt"},
    "1364":    {"author": "Nepos", "title": "Life of Cato", "path": "nepos/nepos.cat.txt"},
    "1365":    {"author": "Nepos", "title": "Life of Chabrias", "path": "nepos/nepos.cha.txt"},
    "1366":    {"author": "Nepos", "title": "Life of Cimon", "path": "nepos/nepos.cim.txt"},
    "1367":    {"author": "Nepos", "title": "Life of Conon", "path": "nepos/nepos.con.txt"},
    "1368":    {"author": "Nepos", "title": "Life of Datames", "path": "nepos/nepos.dat.txt"},
    "1369":    {"author": "Nepos", "title": "Life of Dion", "path": "nepos/nepos.dion.txt"},
    "1370":    {"author": "Nepos", "title": "Life of Epaminondas", "path": "nepos/nepos.epam.txt"},
    "1371":    {"author": "Nepos", "title": "Life of Eumenes", "path": "nepos/nepos.eum.txt"},
    "1372":    {"author": "Nepos", "title": "Fragments", "path": "nepos/nepos.fragmenta.txt"},
    "1373":    {"author": "Nepos", "title": "Life of Hamilcar", "path": "nepos/nepos.ham.txt"},
    "1374":    {"author": "Nepos", "title": "Life of Hannibal", "path": "nepos/nepos.han.txt"},
    "1375":    {"author": "Nepos", "title": "Life of Iphicrates", "path": "nepos/nepos.iph.txt"},
    "1376":    {"author": "Nepos", "title": "On Kings", "path": "nepos/nepos.kings.txt"},
    "1377":    {"author": "Nepos", "title": "Life of Lysander", "path": "nepos/nepos.lys.txt"},
    "1378":    {"author": "Nepos", "title": "Life of Miltiades", "path": "nepos/nepos.mil.txt"},
    "1379":    {"author": "Nepos", "title": "Life of Pausanias", "path": "nepos/nepos.paus.txt"},
    "1380":    {"author": "Nepos", "title": "Life of Pelopidas", "path": "nepos/nepos.pel.txt"},
    "1381":    {"author": "Nepos", "title": "Life of Phocion", "path": "nepos/nepos.phoc.txt"},
    "1382":    {"author": "Nepos", "title": "Praefatio", "path": "nepos/nepos.pr.txt"},
    "1383":    {"author": "Nepos", "title": "Life of Themistocles", "path": "nepos/nepos.them.txt"},
    "1384":    {"author": "Nepos", "title": "Life of Thrasybulus", "path": "nepos/nepos.thras.txt"},
    "1385":    {"author": "Nepos", "title": "Life of Timoleon", "path": "nepos/nepos.tim.txt"},
    "1386":    {"author": "Nepos", "title": "Life of Timotheus", "path": "nepos/nepos.timo.txt"},
    "1387":    {"author": "Newton", "title": "Index Capitum from the Principia ", "path": "newton.capita.txt"},
    "1388":    {"author": "Newton", "title": "Leges Motus from the Principia ", "path": "newton.leges.txt"},
    "1389":    {"author": "Newton", "title": "Regulae Philosophandi from the Principia ", "path": "newton.regulae.txt"},
    "1390":    {"author": "Newton", "title": "Scholium Generale from the Principia ", "path": "newton.scholium.txt"},
    "1391":    {"author": "Nithardus", "title": "Historiae I ", "path": "nithardus1.txt"},
    "1392":    {"author": "Nithardus", "title": "Historiae II ", "path": "nithardus2.txt"},
    "1393":    {"author": "Nithardus", "title": "Historiae III ", "path": "nithardus3.txt"},
    "1394":    {"author": "Nithardus", "title": "Historiae IV ", "path": "nithardus4.txt"},
    "1395":    {"author": None, "title": "", "path": "nivis.txt"},
    "1396":    {"author": "Nobilis", "title": "me ", "path": "nobilis.txt"},
    "1397":    {"author": None, "title": "Notitia Dignitatum", "path": "notitia1.txt"},
    "1398":    {"author": None, "title": "Notitia Dignitatum", "path": "notitia2.txt"},
    "1399":    {"author": None, "title": "Novatian", "path": "novatian.txt"},
    "1400":    {"author": None, "title": "Julius Obsequens", "path": "obsequens.txt"},
    "1401":    {"author": None, "title": "Omne genus demoniorum ", "path": "omnegenus.txt"},
    "1402":    {"author": None, "title": "Oratio Stephani de Varda", "path": "oratio.stephani.txt"},
    "1403":    {"author": None, "title": "Oresimius", "path": "oresmius.txt"},
    "1404":    {"author": None, "title": "Origo gentis Langobardorum", "path": "origo.txt"},
    "1405":    {"author": None, "title": "Orosius I", "path": "orosius/orosius1.txt"},
    "1406":    {"author": None, "title": "Orosius II", "path": "orosius/orosius2.txt"},
    "1407":    {"author": None, "title": "Orosius III", "path": "orosius/orosius3.txt"},
    "1408":    {"author": None, "title": "Orosius IV", "path": "orosius/orosius4.txt"},
    "1409":    {"author": None, "title": "Orosius V", "path": "orosius/orosius5.txt"},
    "1410":    {"author": None, "title": "Orosius VI", "path": "orosius/orosius6.txt"},
    "1411":    {"author": None, "title": "Orosius VII", "path": "orosius/orosius7.txt"},
    "1412":    {"author": "Otto of Freising", "title": "Liber I", "path": "ottofreising/1.txt"},
    "1413":    {"author": "Otto of Freising", "title": "Liber II", "path": "ottofreising/2.txt"},
    "1414":    {"author": "Otto of Freising", "title": "Liber III", "path": "ottofreising/3.txt"},
    "1415":    {"author": "Otto of Freising", "title": "Liber IV", "path": "ottofreising/4.txt"},
    "1416":    {"author": "Otto of Freising", "title": "Epistola", "path": "ottofreising/epistola.txt"},
    "1417":    {"author": "Ovid", "title": "Amores I", "path": "ovid/ovid.amor1.txt"},
    "1418":    {"author": "Ovid", "title": "Amores II", "path": "ovid/ovid.amor2.txt"},
    "1419":    {"author": "Ovid", "title": "Amores III", "path": "ovid/ovid.amor3.txt"},
    "1420":    {"author": "Ovid", "title": "Ars Amatoria I", "path": "ovid/ovid.artis1.txt"},
    "1421":    {"author": "Ovid", "title": "Ars Amatoria II", "path": "ovid/ovid.artis2.txt"},
    "1422":    {"author": "Ovid", "title": "Ars Amatoria III", "path": "ovid/ovid.artis3.txt"},
    "1423":    {"author": "Ovid", "title": "Fasti I", "path": "ovid/ovid.fasti1.txt"},
    "1424":    {"author": "Ovid", "title": "Fasti II", "path": "ovid/ovid.fasti2.txt"},
    "1425":    {"author": "Ovid", "title": "Fasti III", "path": "ovid/ovid.fasti3.txt"},
    "1426":    {"author": "Ovid", "title": "Fasti IV", "path": "ovid/ovid.fasti4.txt"},
    "1427":    {"author": "Ovid", "title": "Fasti V", "path": "ovid/ovid.fasti5.txt"},
    "1428":    {"author": "Ovid", "title": "Fasti VI", "path": "ovid/ovid.fasti6.txt"},
    "1429":    {"author": "Ovid", "title": "Heroides I", "path": "ovid/ovid.her1.txt"},
    "1430":    {"author": "Ovid", "title": "Heroides X", "path": "ovid/ovid.her10.txt"},
    "1431":    {"author": "Ovid", "title": "Heroides XI", "path": "ovid/ovid.her11.txt"},
    "1432":    {"author": "Ovid", "title": "Heroides XII", "path": "ovid/ovid.her12.txt"},
    "1433":    {"author": "Ovid", "title": "Heroides XIII", "path": "ovid/ovid.her13.txt"},
    "1434":    {"author": "Ovid", "title": "Heroides XIV", "path": "ovid/ovid.her14.txt"},
    "1435":    {"author": "Ovid", "title": "Heroides XV", "path": "ovid/ovid.her15.txt"},
    "1436":    {"author": "Ovid", "title": "Heroides XVI", "path": "ovid/ovid.her16.txt"},
    "1437":    {"author": "Ovid", "title": "Heroides XVII", "path": "ovid/ovid.her17.txt"},
    "1438":    {"author": "Ovid", "title": "Heroides XVIII", "path": "ovid/ovid.her18.txt"},
    "1439":    {"author": "Ovid", "title": "Heroides XIX", "path": "ovid/ovid.her19.txt"},
    "1440":    {"author": "Ovid", "title": "Heroides II", "path": "ovid/ovid.her2.txt"},
    "1441":    {"author": "Ovid", "title": "Heroides XX", "path": "ovid/ovid.her20.txt"},
    "1442":    {"author": "Ovid", "title": "Heroides XXI", "path": "ovid/ovid.her21.txt"},
    "1443":    {"author": "Ovid", "title": "Heroides III", "path": "ovid/ovid.her3.txt"},
    "1444":    {"author": "Ovid", "title": "Heroides IV", "path": "ovid/ovid.her4.txt"},
    "1445":    {"author": "Ovid", "title": "Heroides V", "path": "ovid/ovid.her5.txt"},
    "1446":    {"author": "Ovid", "title": "Heroides VI", "path": "ovid/ovid.her6.txt"},
    "1447":    {"author": "Ovid", "title": "Heroides VII", "path": "ovid/ovid.her7.txt"},
    "1448":    {"author": "Ovid", "title": "Heroides VIII", "path": "ovid/ovid.her8.txt"},
    "1449":    {"author": "Ovid", "title": "Heroides IX", "path": "ovid/ovid.her9.txt"},
    "1450":    {"author": "Ovid", "title": "Ibis", "path": "ovid/ovid.ibis.txt"},
    "1451":    {"author": "Ovid", "title": "Metamorphoses I", "path": "ovid/ovid.met1.txt"},
    "1452":    {"author": "Ovid", "title": "Metamorphoses X", "path": "ovid/ovid.met10.txt"},
    "1453":    {"author": "Ovid", "title": "Metamorphoses XI", "path": "ovid/ovid.met11.txt"},
    "1454":    {"author": "Ovid", "title": "Metamorphoses XII", "path": "ovid/ovid.met12.txt"},
    "1455":    {"author": "Ovid", "title": "Metamorphoses XIII", "path": "ovid/ovid.met13.txt"},
    "1456":    {"author": "Ovid", "title": "Metamorphoses XIV", "path": "ovid/ovid.met14.txt"},
    "1457":    {"author": "Ovid", "title": "Metamorphoses XV", "path": "ovid/ovid.met15.txt"},
    "1458":    {"author": "Ovid", "title": "Metamorphoses II", "path": "ovid/ovid.met2.txt"},
    "1459":    {"author": "Ovid", "title": "Metamorphoses III", "path": "ovid/ovid.met3.txt"},
    "1460":    {"author": "Ovid", "title": "Metamorphoses IV", "path": "ovid/ovid.met4.txt"},
    "1461":    {"author": "Ovid", "title": "Metamorphoses V", "path": "ovid/ovid.met5.txt"},
    "1462":    {"author": "Ovid", "title": "Metamorphoses VI", "path": "ovid/ovid.met6.txt"},
    "1463":    {"author": "Ovid", "title": "Metamorphoses VII", "path": "ovid/ovid.met7.txt"},
    "1464":    {"author": "Ovid", "title": "Metamorphoses VIII", "path": "ovid/ovid.met8.txt"},
    "1465":    {"author": "Ovid", "title": "Metamorphoses IX", "path": "ovid/ovid.met9.txt"},
    "1466":    {"author": "Ovid", "title": "Ex Ponto I", "path": "ovid/ovid.ponto1.txt"},
    "1467":    {"author": "Ovid", "title": "Ex Ponto II", "path": "ovid/ovid.ponto2.txt"},
    "1468":    {"author": "Ovid", "title": "Ex Ponto III", "path": "ovid/ovid.ponto3.txt"},
    "1469":    {"author": "Ovid", "title": "Ex Ponto IV", "path": "ovid/ovid.ponto4.txt"},
    "1470":    {"author": "Ovid", "title": "Remedia Amoris", "path": "ovid/ovid.rem.txt"},
    "1471":    {"author": "Ovid", "title": "Tristia I", "path": "ovid/ovid.tristia1.txt"},
    "1472":    {"author": "Ovid", "title": "Tristia II", "path": "ovid/ovid.tristia2.txt"},
    "1473":    {"author": "Ovid", "title": "Ovid: Tristia III", "path": "ovid/ovid.tristia3.txt"},
    "1474":    {"author": "Ovid", "title": "Ovid: Tristia IV", "path": "ovid/ovid.tristia4.txt"},
    "1475":    {"author": "Ovid", "title": "Ovid: Tristia V", "path": "ovid/ovid.tristia5.txt"},
    "1476":    {"author": None, "title": "John Owen ", "path": "owen.txt"},
    "1477":    {"author": "Julius Paris", "title": "de Nominibus Epitome", "path": "paris.txt"},
    "1478":    {"author": None, "title": "Catullocalvos-Satura ", "path": "pascoli.catull.txt"},
    "1479":    {"author": None, "title": "Iugurtha ", "path": "pascoli.iug.txt"},
    "1480":    {"author": None, "title": "Laureolo ", "path": "pascoli.laur.txt"},
    "1481":    {"author": None, "title": "Senex Corycius ", "path": "pascoli.sen.txt"},
    "1482":    {"author": None, "title": "Veianius ", "path": "pascoli.veianius.txt"},
    "1483":    {"author": None, "title": "Jean Passerat", "path": "passerat.txt"},
    "1484":    {"author": "Franciscus Patricius", "title": "Panaugiae I ", "path": "patricius1.txt"},
    "1485":    {"author": "Franciscus Patricius", "title": "Panaugiae II ", "path": "patricius2.txt"},
    "1486":    {"author": "Paulus Diaconus", "title": "Carmina", "path": "pauldeacon/carmina.txt"},
    "1487":    {"author": "Paulus Diaconus", "title": "Fabulae", "path": "pauldeacon/fabulae.txt"},
    "1488":    {"author": "Paulus Diaconus", "title": "Historia Langobardorum Liber I", "path": "pauldeacon/hist1.txt"},
    "1489":    {
        "author": "Paulus Diaconus", "title": "Historia Langobardorum Liber II", "path": "pauldeacon/hist2.txt"
    }, "1490": {
        "author": "Paulus Diaconus", "title": "Historia Langobardorum Liber III", "path": "pauldeacon/hist3.txt"
    }, "1491": {
        "author": "Paulus Diaconus", "title": "Historia Langobardorum Liber IV", "path": "pauldeacon/hist4.txt"
    }, "1492": {"author": "Paulus Diaconus", "title": "Historia Langobardorum Liber V", "path": "pauldeacon/hist5.txt"},
    "1493":    {
        "author": "Paulus Diaconus", "title": "Historia Langobardorum Liber VI", "path": "pauldeacon/hist6.txt"
    }, "1494": {"author": "Paulus Diaconus", "title": "Historia Romana Liber I", "path": "pauldeacon/histrom1.txt"},
    "1495":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber X", "path": "pauldeacon/histrom10.txt"},
    "1496":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber XI", "path": "pauldeacon/histrom11.txt"},
    "1497":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber XII", "path": "pauldeacon/histrom12.txt"},
    "1498":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber XIII", "path": "pauldeacon/histrom13.txt"},
    "1499":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber XIV", "path": "pauldeacon/histrom14.txt"},
    "1500":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber XV", "path": "pauldeacon/histrom15.txt"},
    "1501":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber XVI", "path": "pauldeacon/histrom16.txt"},
    "1502":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber II", "path": "pauldeacon/histrom2.txt"},
    "1503":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber III", "path": "pauldeacon/histrom3.txt"},
    "1504":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber IV", "path": "pauldeacon/histrom4.txt"},
    "1505":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber II", "path": "pauldeacon/histrom5.txt"},
    "1506":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber VI", "path": "pauldeacon/histrom6.txt"},
    "1507":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber VII", "path": "pauldeacon/histrom7.txt"},
    "1508":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber VIII", "path": "pauldeacon/histrom8.txt"},
    "1509":    {"author": "Paulus Diaconus", "title": "Historia Romana Liber IX", "path": "pauldeacon/histrom9.txt"},
    "1510":    {"author": None, "title": "O Comes ", "path": "paulinus.ausonium.txt"},
    "1511":    {"author": "Paulinus of Nola", "title": "Poems", "path": "paulinus.poemata.txt"},
    "1512":    {"author": None, "title": "Perpetua et Felicitatis", "path": "perp.txt"},
    "1513":    {"author": None, "title": "Persius", "path": "persius.txt"},
    "1514":    {"author": None, "title": "Pervigilium Veneris", "path": "pervig.txt"},
    "1515":    {"author": "Petrarch", "title": "Epistula M. Tullio Ciceroni", "path": "petrarch.ep1.txt"},
    "1516":    {"author": "Petrarch", "title": "Numa Pompilius", "path": "petrarch.numa.txt"},
    "1517":    {"author": "Petrarch", "title": "Romulus", "path": "petrarch.rom.txt"},
    "1518":    {"author": "Petrarca", "title": "Contra Medicum Quendam", "path": "petrarchmedicus.txt"},
    "1519":    {"author": "Petronius", "title": "Satiricon", "path": "petronius1.txt"},
    "1520":    {"author": None, "title": "Fragmenta Petroniana", "path": "petroniusfrag.txt"},
    "1521":    {"author": None, "title": "Phaedrus I", "path": "phaedr1.txt"},
    "1522":    {"author": None, "title": "Phaedrus II", "path": "phaedr2.txt"},
    "1523":    {"author": None, "title": "Phaedrus III", "path": "phaedr3.txt"},
    "1524":    {"author": None, "title": "Phaedrus IV", "path": "phaedr4.txt"},
    "1525":    {"author": None, "title": "Phaedrus V", "path": "phaedr5.txt"},
    "1526":    {"author": None, "title": "Phaedrus Appendix", "path": "phaedrapp.txt"}, "1527": {
        "author": "Enea Silvio Piccolomini (1405-1464", "title": "Pope Pius II from 1458) ",
        "path":   "piccolomini.carmen.txt"
    }, "1528": {"author": "Piccolomini", "title": "Letter to Johann Lauterbach ", "path": "piccolomini.ep1.txt"},
    "1529":    {"author": "Piccolomini", "title": "Letter to His Father ", "path": "piccolomini.ep2.txt"},
    "1530":    {"author": "Piccolomini", "title": "Letter to Wilhelm von Stein ", "path": "piccolomini.ep3.txt"},
    "1531":    {"author": "Piccolomini", "title": "Letter to Procop van Rabenstein ", "path": "piccolomini.ep4.txt"},
    "1532":    {"author": "Piccolomini", "title": "Letter to Prince Sigismund ", "path": "piccolomini.ep5.txt"},
    "1533":    {"author": "Piccolomini", "title": "Letter to Caspar Schlick ", "path": "piccolomini.ep6.txt"},
    "1534":    {"author": "Piccolomini", "title": "Oratio contra Turcos ", "path": "piccolomini.turcos.txt"},
    "1535":    {"author": None, "title": "Anonymous", "path": "planctus.txt"},
    "1536":    {"author": "Plautus", "title": "Amphitruo", "path": "plautus/amphitruo.txt"},
    "1537":    {"author": "Plautus", "title": "Asinaria", "path": "plautus/asinaria.txt"},
    "1538":    {"author": "Plautus", "title": "Aulularia", "path": "plautus/aulularia.txt"},
    "1539":    {"author": "Plautus", "title": "Bacchides", "path": "plautus/bacchides.txt"},
    "1540":    {"author": "Plautus", "title": "Captivi", "path": "plautus/captivi.txt"},
    "1541":    {"author": "Plautus", "title": "Casina", "path": "plautus/cas.txt"},
    "1542":    {"author": "Plautus", "title": "Cistellaria", "path": "plautus/cistellaria.txt"},
    "1543":    {"author": "Plautus", "title": "Curculio", "path": "plautus/curculio.txt"},
    "1544":    {"author": "Plautus", "title": "Epidicus", "path": "plautus/epidicus.txt"},
    "1545":    {"author": "Plautus", "title": "Menaechmi", "path": "plautus/menaechmi.txt"},
    "1546":    {"author": "Plautus", "title": "Mercator", "path": "plautus/mercator.txt"},
    "1547":    {"author": "Plautus", "title": "Miles Gloriosus", "path": "plautus/miles.txt"},
    "1548":    {"author": "Plautus", "title": "Mostellaria", "path": "plautus/mostellaria.txt"},
    "1549":    {"author": "Plautus", "title": "Persa", "path": "plautus/persa.txt"},
    "1550":    {"author": "Plautus", "title": "Poenulus", "path": "plautus/poenulus.txt"},
    "1551":    {"author": "Plautus", "title": "Pseudolus", "path": "plautus/pseudolus.txt"},
    "1552":    {"author": "Plautus", "title": "Rudens", "path": "plautus/rudens.txt"},
    "1553":    {"author": "Plautus", "title": "Stichus", "path": "plautus/stichus.txt"},
    "1554":    {"author": "Plautus", "title": "Trinummus", "path": "plautus/trinummus.txt"},
    "1555":    {"author": "Plautus", "title": "Truculentus", "path": "plautus/truculentus.txt"},
    "1556":    {"author": "Plautus", "title": "Vidularia", "path": "plautus/vidularia.txt"},
    "1557":    {"author": None, "title": "Pliny the Younger", "path": "pliny.ep1.txt"},
    "1558":    {"author": None, "title": "Pliny the Younger", "path": "pliny.ep10.txt"},
    "1559":    {"author": None, "title": "Pliny the Younger", "path": "pliny.ep2.txt"},
    "1560":    {"author": None, "title": "Pliny the Younger", "path": "pliny.ep3.txt"},
    "1561":    {"author": None, "title": "Pliny the Younger", "path": "pliny.ep4.txt"},
    "1562":    {"author": None, "title": "Pliny the Younger", "path": "pliny.ep5.txt"},
    "1563":    {"author": None, "title": "Pliny the Younger", "path": "pliny.ep6.txt"},
    "1564":    {"author": None, "title": "Pliny the Younger", "path": "pliny.ep7.txt"},
    "1565":    {"author": None, "title": "Pliny the Younger", "path": "pliny.ep8.txt"},
    "1566":    {"author": None, "title": "Pliny the Younger", "path": "pliny.ep9.txt"},
    "1567":    {"author": "Pliny the Elder", "title": "Natural History, Book I", "path": "pliny.nh1.txt"},
    "1568":    {"author": None, "title": "Pliny the Elder", "path": "pliny.nh2.txt"},
    "1569":    {"author": "Pliny the Elder", "title": "Natural History, Book III", "path": "pliny.nh3.txt"},
    "1570":    {"author": "Pliny the Elder", "title": "Natural History, Book IV", "path": "pliny.nh4.txt"},
    "1571":    {"author": "Pliny the Elder", "title": "Natural History, Book V", "path": "pliny.nh5.txt"},
    "1572":    {"author": "Pliny the Elder", "title": "Natural History, Preface", "path": "pliny.nhpr.txt"},
    "1573":    {"author": None, "title": "Pliny the Younger", "path": "pliny.panegyricus.txt"},
    "1574":    {"author": None, "title": "Poggii Facetiae (1-120)", "path": "poggio.txt"},
    "1575":    {"author": "Pomponius Mela", "title": "de Chorographia I ", "path": "pomponius1.txt"},
    "1576":    {"author": "Pomponius Mela", "title": "de Chorographia II", "path": "pomponius2.txt"},
    "1577":    {"author": "Pomponius Mela", "title": "de Chorographia III", "path": "pomponius3.txt"},
    "1578":    {"author": None, "title": "Giovanni Pontano (1429-1503)", "path": "pontano.txt"},
    "1579":    {"author": "Charles Poree", "title": "Caecus Amor ", "path": "poree.txt"},
    "1580":    {"author": "Porphyrius", "title": "Carmina", "path": "porphyrius.txt"},
    "1581":    {"author": None, "title": "Potatores exquisiti", "path": "potatores.txt"},
    "1582":    {"author": None, "title": "Prata iam rident omnia ", "path": "prataiam.txt"},
    "1583":    {"author": None, "title": "Precatio Terrae", "path": "prec.terr.txt"},
    "1584":    {"author": None, "title": "Precatio Omnium Herbarum ", "path": "precatio.txt"},
    "1585":    {"author": None, "title": "Priapea", "path": "priapea.txt"},
    "1586":    {"author": None, "title": "Professio contra Sectam Priscilliani", "path": "professio.txt"},
    "1587":    {"author": None, "title": "Propertius Book II", "path": "prop2.txt"},
    "1588":    {"author": None, "title": "Propertius Book III", "path": "prop3.txt"},
    "1589":    {"author": None, "title": "SEXTI PROPERTI ELEGIARVM LIBER QVARTVS", "path": "prop4.txt"},
    "1590":    {"author": None, "title": "SEXTI PROPERTI ELEGIARVM LIBER PRIMVS", "path": "propertius1.txt"}, "1591": {
        "author": "St. Prosperus of Aquitaine", "title": "Epistola ad Augustinum", "path": "prosperus.epistola.txt"
    }, "1592": {
        "author": "St. Prosperus of Aquitaine", "title": "Epistola ad Rufinum", "path": "prosperus.rufinum.txt"
    }, "1593": {
        "author": "St. Prosperus of Aquitaine", "title": "Liber Sententiarum", "path": "prosperus.sententiae.txt"
    }, "1594": {"author": "Protospatariu", "title": "Breve Chronicon", "path": "protospatarius.txt"},
    "1595":    {"author": "Prudentius", "title": "Psychomachia", "path": "prudentius/prud.psycho.txt"},
    "1596":    {"author": None, "title": "Prudentius I", "path": "prudentius/prud1.txt"},
    "1597":    {"author": None, "title": "Prudentius X", "path": "prudentius/prud10.txt"},
    "1598":    {"author": None, "title": "Prudentius XI", "path": "prudentius/prud11.txt"},
    "1599":    {"author": None, "title": "Prudentius XII", "path": "prudentius/prud12.txt"},
    "1600":    {"author": None, "title": "Prudentius XIII", "path": "prudentius/prud13.txt"},
    "1601":    {"author": None, "title": "Prudentius XIV", "path": "prudentius/prud14.txt"},
    "1602":    {"author": None, "title": "Prudentius II", "path": "prudentius/prud2.txt"},
    "1603":    {"author": None, "title": "Prudentius III", "path": "prudentius/prud3.txt"},
    "1604":    {"author": None, "title": "Prudentius IIII", "path": "prudentius/prud4.txt"},
    "1605":    {"author": None, "title": "Prudentius V", "path": "prudentius/prud5.txt"},
    "1606":    {"author": None, "title": "Prudentius VI", "path": "prudentius/prud6.txt"},
    "1607":    {"author": None, "title": "Prudentius VII", "path": "prudentius/prud7.txt"},
    "1608":    {"author": None, "title": "Prudentius VIII", "path": "prudentius/prud8.txt"},
    "1609":    {"author": None, "title": "Prudentius IX", "path": "prudentius/prud9.txt"},
    "1610":    {"author": None, "title": "Pseudo-Plato - De Virtute ", "path": "psplato.amatores.txt"},
    "1611":    {"author": "Pseudo-Plato", "title": "Demodocus ", "path": "psplato.demodocus.txt"},
    "1612":    {"author": None, "title": "Pseudo-Plato - Eryxias ", "path": "psplato.eryxias.txt"},
    "1613":    {"author": "Pseudo-Plato/Pseudo-Lucian", "title": "Halcyon ", "path": "psplato.halcyon.txt"},
    "1614":    {"author": None, "title": "Pseudo-Plato - De Iusto ", "path": "psplato.iusto.txt"},
    "1615":    {"author": "Pseudo-Plato", "title": "Minos ", "path": "psplato.minos.txt"},
    "1616":    {"author": None, "title": "Pseudo-Plato - Sisyphus ", "path": "psplato.sisyphus.txt"},
    "1617":    {"author": None, "title": "Pseudo-Plato - De Virtute ", "path": "psplato.virtu.txt"},
    "1618":    {"author": None, "title": "Pulchra comis ", "path": "pulchracomis.txt"},
    "1619":    {"author": "Quintilian", "title": "Declamatio Maior I", "path": "quintilian/quintilian.decl.mai1.txt"},
    "1620":    {"author": "Quintilian", "title": "Declamatio Maior X", "path": "quintilian/quintilian.decl.mai10.txt"},
    "1621":    {"author": "Quintilian", "title": "Declamatio Maior XI", "path": "quintilian/quintilian.decl.mai11.txt"},
    "1622":    {
        "author": "Quintilian", "title": "Declamatio Maior XII", "path": "quintilian/quintilian.decl.mai12.txt"
    }, "1623": {
        "author": "Quintilian", "title": "Declamatio Maior XIII", "path": "quintilian/quintilian.decl.mai13.txt"
    }, "1624": {
        "author": "Quintilian", "title": "Declamatio Maior XIV", "path": "quintilian/quintilian.decl.mai14.txt"
    }, "1625": {"author": "Quintilian", "title": "Declamatio Maior XV", "path": "quintilian/quintilian.decl.mai15.txt"},
    "1626":    {
        "author": "Quintilian", "title": "Declamatio Maior XVI", "path": "quintilian/quintilian.decl.mai16.txt"
    }, "1627": {
        "author": "Quintilian", "title": "Declamatio Maior XVII", "path": "quintilian/quintilian.decl.mai17.txt"
    }, "1628": {
        "author": "Quintilian", "title": "Declamatio Maior XVIII", "path": "quintilian/quintilian.decl.mai18.txt"
    }, "1629": {"author": "Quintilian", "title": "Declamatio Maior I", "path": "quintilian/quintilian.decl.mai19.txt"},
    "1630":    {"author": "Quintilian", "title": "Declamatio Maior II", "path": "quintilian/quintilian.decl.mai2.txt"},
    "1631":    {"author": "Quintilian", "title": "Declamatio Maior IV", "path": "quintilian/quintilian.decl.mai4.txt"},
    "1632":    {"author": "Quintilian", "title": "Declamatio Maior V", "path": "quintilian/quintilian.decl.mai5.txt"},
    "1633":    {"author": "Quintilian", "title": "Declamatio Maior VI", "path": "quintilian/quintilian.decl.mai6.txt"},
    "1634":    {"author": "Quintilian", "title": "Declamatio Maior VII", "path": "quintilian/quintilian.decl.mai7.txt"},
    "1635":    {
        "author": "Quintilian", "title": "Declamatio Maior VIII", "path": "quintilian/quintilian.decl.mai8.txt"
    }, "1636": {"author": "Quintilian", "title": "Declamatio Maior IX", "path": "quintilian/quintilian.decl.mai9.txt"},
    "1637":    {
        "author": "Quintilian", "title": "Institutio Oratoria I", "path": "quintilian/quintilian.institutio1.txt"
    }, "1638": {
        "author": "Quintilian", "title": "Institutio Oratoria X", "path": "quintilian/quintilian.institutio10.txt"
    }, "1639": {
        "author": "Quintilian", "title": "Institutio Oratoria XI", "path": "quintilian/quintilian.institutio11.txt"
    }, "1640": {
        "author": "Quintilian", "title": "Institutio Oratoria XII", "path": "quintilian/quintilian.institutio12.txt"
    }, "1641": {
        "author": "Quintilian", "title": "Institutio Oratoria II", "path": "quintilian/quintilian.institutio2.txt"
    }, "1642": {
        "author": "Quintilian", "title": "Institutio Oratoria III", "path": "quintilian/quintilian.institutio3.txt"
    }, "1643": {
        "author": "Quintilian", "title": "Institutio Oratoria IV", "path": "quintilian/quintilian.institutio4.txt"
    }, "1644": {
        "author": "Quintilian", "title": "Institutio Oratoria V", "path": "quintilian/quintilian.institutio5.txt"
    }, "1645": {
        "author": "Quintilian", "title": "Institutio Oratoria VI", "path": "quintilian/quintilian.institutio6.txt"
    }, "1646": {
        "author": "Quintilian", "title": "Institutio Oratoria VII", "path": "quintilian/quintilian.institutio7.txt"
    }, "1647": {
        "author": "Quintilian", "title": "Institutio Oratoria VIII", "path": "quintilian/quintilian.institutio8.txt"
    }, "1648": {
        "author": "Quintilian", "title": "Institutio Oratoria IX", "path": "quintilian/quintilian.institutio9.txt"
    }, "1649": {"author": None, "title": "Quum inter nonNoneos ", "path": "quum.txt"}, "1650": {
        "author": "Raoul of Caen", "title": "Gesta Tancredi in expeditione Hierosolymitana", "path": "raoul.txt"
    }, "1651": {"author": None, "title": "Regula ad Monachos", "path": "regula.txt"},
    "1652":    {"author": "Reposianus", "title": "De concubitu Martis et Veneris ", "path": "reposianus.txt"},
    "1653":    {"author": "AUGUSTUS", "title": "RES GESTAE I", "path": "resgestae.txt"},
    "1654":    {"author": "AUGUSTUS", "title": "RES GESTAE", "path": "resgestae1.txt"},
    "1655":    {"author": None, "title": "EDICTUM ADVERSUS LATINOS RHETORES", "path": "rhetores.txt"},
    "1656":    {"author": "Richerus", "title": "Liber I", "path": "richerus1.txt"},
    "1657":    {"author": "Richerus", "title": "Liber II", "path": "richerus2.txt"},
    "1658":    {"author": "Richerus", "title": "Liber III", "path": "richerus3.txt"},
    "1659":    {"author": "Richerus", "title": "Liber IV", "path": "richerus4.txt"},
    "1660":    {"author": None, "title": "Arthur Rimbaud", "path": "rimbaud.txt"},
    "1661":    {"author": None, "title": "Ruaeus' Prose Summary of Virgil's Aeneid", "path": "ruaeus.txt"},
    "1662":    {"author": None, "title": "", "path": "rumor.txt"},
    "1663":    {"author": "Rutilius Namatianus", "title": "De Reditu Suo", "path": "rutilius.txt"}, "1664": {
        "author": "P. Rutilius Lupus", "title": "de Figuris Sententiarum et Elocutionis", "path": "rutiliuslupus.txt"
    }, "1665": {"author": None, "title": "Sabinus", "path": "sabinus1.txt"},
    "1666":    {"author": None, "title": "Sabinus", "path": "sabinus2.txt"},
    "1667":    {"author": None, "title": "Sabinus", "path": "sabinus3.txt"},
    "1668":    {"author": "Sallust", "title": "Bellum Catilinae", "path": "sall.1.txt"},
    "1669":    {"author": "Sallust", "title": "Bellum Iugurthinum", "path": "sall.2.txt"},
    "1670":    {"author": "Sallust", "title": "Speech of Cotta", "path": "sall.cotta.txt"},
    "1671":    {"author": "Sallust", "title": "Letter to Caesar I", "path": "sall.ep1.txt"},
    "1672":    {"author": "Sallust", "title": "Letter to Caesar II", "path": "sall.ep2.txt"},
    "1673":    {"author": "Sallust", "title": "Fragmenta", "path": "sall.frag.txt"},
    "1674":    {"author": "Sallust", "title": "Invective Against Cicero", "path": "sall.invectiva.txt"},
    "1675":    {"author": "Sallust", "title": "Speech of Lepidus", "path": "sall.lep.txt"},
    "1676":    {"author": "Sallust", "title": "Speech of Macer", "path": "sall.macer.txt"},
    "1677":    {"author": "Sallust", "title": "Speech of Mithridates", "path": "sall.mithr.txt"},
    "1678":    {"author": "Sallust", "title": "Speech of Philippus", "path": "sall.phil.txt"},
    "1679":    {"author": "Sallust", "title": "Speech of Pompey", "path": "sall.pomp.txt"},
    "1680":    {"author": "Sannazaro", "title": "de Partu Virginis", "path": "sannazaro1.txt"},
    "1681":    {"author": "Sannazaro", "title": "Lamentatio de morte Christi", "path": "sannazaro2.txt"},
    "1682":    {"author": None, "title": "Scaliger", "path": "scaliger.txt"},
    "1683":    {"author": None, "title": "SENATUS CONSULTUM DE BACCHANALIBUS", "path": "scbaccanalibus.txt"},
    "1684":    {"author": None, "title": "Sedulius Scottus ", "path": "scottus.txt"},
    "1685":    {"author": "Sedulius", "title": "A solis ortus cardine", "path": "sedulius.solis.txt"},
    "1686":    {"author": "Sedulius", "title": "Carmen Paschale I", "path": "sedulius1.txt"},
    "1687":    {"author": "Sedulius", "title": "Carmen Paschale II", "path": "sedulius2.txt"},
    "1688":    {"author": "Sedulius", "title": "Carmen Paschale III", "path": "sedulius3.txt"},
    "1689":    {"author": "Sedulius", "title": "Carmen Paschale IV", "path": "sedulius4.txt"},
    "1690":    {"author": "Sedulius", "title": "Carmen Paschale I", "path": "sedulius5.txt"},
    "1691":    {"author": "Seneca", "title": "On Benefits I ", "path": "sen/ben1.txt"},
    "1692":    {"author": "Seneca", "title": "On Benefits II ", "path": "sen/ben2.txt"},
    "1693":    {"author": "Seneca", "title": "On Benefits III ", "path": "sen/ben3.txt"},
    "1694":    {"author": "Seneca", "title": "Octavia", "path": "sen/octavia.txt"},
    "1695":    {"author": "Seneca", "title": "Agamemnon", "path": "sen/sen.agamemnon.txt"},
    "1696":    {"author": "Seneca", "title": "Apocolocyntosis", "path": "sen/sen.apoc.txt"},
    "1697":    {"author": "Seneca", "title": "On the Brevity of Life", "path": "sen/sen.brevita.txt"},
    "1698":    {"author": "Seneca", "title": "On Clemency", "path": "sen/sen.clem.txt"},
    "1699":    {"author": "Seneca", "title": "On Consolation (ad Polybium)", "path": "sen/sen.consolatione1.txt"},
    "1700":    {"author": "Seneca", "title": "On Consolation (ad Marciam)", "path": "sen/sen.consolatione2.txt"},
    "1701":    {"author": "Seneca", "title": "On Consolatio", "path": "sen/sen.consolatione3.txt"},
    "1702":    {"author": "Seneca", "title": "de Constantia", "path": "sen/sen.constantia.txt"},
    "1703":    {"author": "Seneca", "title": "Hercules", "path": "sen/sen.hercules.txt"},
    "1704":    {"author": "Seneca", "title": "On Anger I", "path": "sen/sen.ira1.txt"},
    "1705":    {"author": "Seneca", "title": "On Anger II", "path": "sen/sen.ira2.txt"},
    "1706":    {"author": "Seneca", "title": "On Anger III", "path": "sen/sen.ira3.txt"},
    "1707":    {"author": "Seneca", "title": "Medea", "path": "sen/sen.medea.txt"},
    "1708":    {"author": "Seneca", "title": "Oedipus", "path": "sen/sen.oedipus.txt"},
    "1709":    {"author": "Seneca", "title": "On Leisure", "path": "sen/sen.otio.txt"},
    "1710":    {"author": "Seneca", "title": "Phaedra", "path": "sen/sen.phaedra.txt"},
    "1711":    {"author": "Seneca", "title": "Phoenissae", "path": "sen/sen.phoen.txt"},
    "1712":    {"author": "Seneca", "title": "On Providence", "path": "sen/sen.prov.txt"},
    "1713":    {"author": None, "title": "Proverbia Senecae", "path": "sen/sen.proverbs.txt"},
    "1714":    {"author": "Seneca", "title": "Quaestiones Naturales I", "path": "sen/sen.qn1.txt"},
    "1715":    {"author": "Seneca", "title": "Quaestiones Naturales II", "path": "sen/sen.qn2.txt"},
    "1716":    {"author": "Seneca", "title": "Quaestiones Naturales III", "path": "sen/sen.qn3.txt"},
    "1717":    {"author": "Seneca", "title": "Quaestiones Naturales IV", "path": "sen/sen.qn4.txt"},
    "1718":    {"author": "Seneca", "title": "Quaestiones Naturales V", "path": "sen/sen.qn5.txt"},
    "1719":    {"author": "Seneca", "title": "Quaestiones Naturales VI", "path": "sen/sen.qn6.txt"},
    "1720":    {"author": "Seneca", "title": "Quaestiones Naturales VII", "path": "sen/sen.qn7.txt"},
    "1721":    {"author": "Seneca", "title": "Thyestes", "path": "sen/sen.thyestes.txt"},
    "1722":    {"author": "Seneca", "title": "On Tranquility of the Mind", "path": "sen/sen.tranq.txt"},
    "1723":    {"author": "Seneca", "title": "On the Good Life", "path": "sen/sen.vita.txt"},
    "1724":    {"author": "Seneca", "title": "Epistulae Morales, Liber I", "path": "sen/seneca.ep1.txt"},
    "1725":    {"author": "Seneca", "title": "Epistulae Morales, Liber X", "path": "sen/seneca.ep10.txt"},
    "1726":    {"author": "Seneca", "title": "Epistulae Morales, Liber XI-XIII", "path": "sen/seneca.ep11-13.txt"},
    "1727":    {"author": "Seneca", "title": "Epistulae Morales, Liber XIV & XV", "path": "sen/seneca.ep14-15.txt"},
    "1728":    {"author": "Seneca", "title": "Epistulae Morales, Liber XVI", "path": "sen/seneca.ep16.txt"},
    "1729":    {"author": "Seneca", "title": "Epistulae Morales, Liber XVII & XVIII", "path": "sen/seneca.ep17-18.txt"},
    "1730":    {"author": "Seneca", "title": "Epistulae Morales, Liber XIX", "path": "sen/seneca.ep19.txt"},
    "1731":    {"author": "Seneca", "title": "Epistulae Morales, Liber II", "path": "sen/seneca.ep2.txt"},
    "1732":    {"author": "Seneca", "title": "Epistulae Morales, Liber XX", "path": "sen/seneca.ep20.txt"}, "1733": {
        "author": "Seneca", "title": "Epistulae Morales, Liber XXII (Fragmenta)", "path": "sen/seneca.ep22.txt"
    }, "1734": {"author": "Seneca", "title": "Epistulae Morales, Liber IIII", "path": "sen/seneca.ep3.txt"},
    "1735":    {"author": "Seneca", "title": "Epistulae Morales, Liber IV", "path": "sen/seneca.ep4.txt"},
    "1736":    {"author": "Seneca", "title": "Epistulae Morales, Liber V", "path": "sen/seneca.ep5.txt"},
    "1737":    {"author": "Seneca", "title": "Epistulae Morales, Liber VI", "path": "sen/seneca.ep6.txt"},
    "1738":    {"author": "Seneca", "title": "Epistulae Morales, Liber VII", "path": "sen/seneca.ep7.txt"},
    "1739":    {"author": "Seneca", "title": "Epistulae Morales, Liber VIII", "path": "sen/seneca.ep8.txt"},
    "1740":    {"author": "Seneca", "title": "Epistulae Morales, Liber IX", "path": "sen/seneca.ep9.txt"},
    "1741":    {"author": None, "title": "Seneca the Elder", "path": "seneca.contr1.txt"},
    "1742":    {"author": None, "title": "Seneca the Elder", "path": "seneca.contr10.txt"},
    "1743":    {"author": None, "title": "Seneca the Elder", "path": "seneca.contr2.txt"},
    "1744":    {"author": None, "title": "Seneca the Elder", "path": "seneca.contr3.txt"},
    "1745":    {"author": None, "title": "Seneca the Elder", "path": "seneca.contr4.txt"},
    "1746":    {"author": None, "title": "Seneca the Elder", "path": "seneca.contr5.txt"},
    "1747":    {"author": None, "title": "Seneca the Elder", "path": "seneca.contr6.txt"},
    "1748":    {"author": None, "title": "Seneca the Elder", "path": "seneca.contr7.txt"},
    "1749":    {"author": None, "title": "Seneca the Elder", "path": "seneca.contr8.txt"},
    "1750":    {"author": None, "title": "Seneca the Elder", "path": "seneca.contr9.txt"},
    "1751":    {"author": None, "title": "Seneca the Elder", "path": "seneca.fragmenta.txt"},
    "1752":    {"author": None, "title": "Seneca the Elder", "path": "seneca.suasoriae.txt"},
    "1753":    {"author": None, "title": "The Story of the Seven Wise Men", "path": "septsap.txt"},
    "1754":    {"author": None, "title": "The Thirty Tyrants", "path": "sha/30.txt"},
    "1755":    {"author": None, "title": "Aelius", "path": "sha/aelii.txt"},
    "1756":    {"author": None, "title": "Alexander Severus", "path": "sha/alexsev.txt"},
    "1757":    {"author": None, "title": "Antoninus Pius", "path": "sha/ant.txt"},
    "1758":    {"author": None, "title": "Aurelian", "path": "sha/aurel.txt"},
    "1759":    {"author": None, "title": "Avidius Cassius", "path": "sha/avid.txt"},
    "1760":    {"author": None, "title": "Caracalla", "path": "sha/car.txt"},
    "1761":    {"author": "Carus", "title": "Carinus, Numerianus", "path": "sha/carus.txt"},
    "1762":    {"author": None, "title": "Claudius", "path": "sha/claud.txt"},
    "1763":    {"author": None, "title": "Clodius Albinus", "path": "sha/clod.txt"},
    "1764":    {"author": None, "title": "Commodus", "path": "sha/com.txt"},
    "1765":    {"author": None, "title": "Diadumenus", "path": "sha/diad.txt"},
    "1766":    {"author": None, "title": "Didius Iulianus", "path": "sha/didiul.txt"},
    "1767":    {"author": None, "title": "Tyrants", "path": "sha/firmus.txt"},
    "1768":    {"author": None, "title": "The Two Gallieni", "path": "sha/gall.txt"},
    "1769":    {"author": None, "title": "Geta", "path": "sha/geta.txt"},
    "1770":    {"author": None, "title": "The Three Gordians", "path": "sha/gord.txt"},
    "1771":    {"author": None, "title": "Hadrian", "path": "sha/hadr.txt"},
    "1772":    {"author": None, "title": "Elagabalus", "path": "sha/helio.txt"},
    "1773":    {"author": None, "title": "Macrinus", "path": "sha/mac.txt"},
    "1774":    {"author": None, "title": "Marcus Aurelius", "path": "sha/marcant.txt"},
    "1775":    {"author": None, "title": "Maximini", "path": "sha/max.txt"},
    "1776":    {"author": None, "title": "Maximus et Balbinus", "path": "sha/maxbal.txt"},
    "1777":    {"author": None, "title": "Pertinax", "path": "sha/pert.txt"},
    "1778":    {"author": None, "title": "Pescenius Niger", "path": "sha/pesc.txt"},
    "1779":    {"author": None, "title": "Probus", "path": "sha/probus.txt"},
    "1780":    {"author": None, "title": "Septimus Severus", "path": "sha/sepsev.txt"},
    "1781":    {"author": None, "title": "Tacitus", "path": "sha/tacitus.txt"},
    "1782":    {"author": None, "title": "The Two Valerians", "path": "sha/val.txt"},
    "1783":    {"author": None, "title": "L. Verus", "path": "sha/verus.txt"},
    "1784":    {"author": None, "title": "Sic mea fata canendo solor ", "path": "sicmeafata.txt"},
    "1785":    {"author": "Sidonius", "title": "Epistularum Liber I", "path": "sidonius1.txt"},
    "1786":    {"author": "Sidonius", "title": "Epistularum Liber II", "path": "sidonius2.txt"},
    "1787":    {"author": "Sidonius", "title": "Epistularum Liber III", "path": "sidonius3.txt"},
    "1788":    {"author": "Sidonius", "title": "Epistularum Liber IV", "path": "sidonius4.txt"},
    "1789":    {"author": "Sidonius", "title": "Epistularum Liber V", "path": "sidonius5.txt"},
    "1790":    {"author": "Sidonius", "title": "Epistularum Liber VI", "path": "sidonius6.txt"},
    "1791":    {"author": "Sidonius", "title": "Epistularum Liber VII", "path": "sidonius7.txt"},
    "1792":    {"author": "Sidonius", "title": "Epistularum Liber VIII", "path": "sidonius8.txt"},
    "1793":    {"author": "Sidonius", "title": "Epistularum Liber IX", "path": "sidonius9.txt"},
    "1794":    {"author": None, "title": "Sigebert of Gembloux", "path": "sigebert.script.txt"},
    "1795":    {"author": None, "title": "Sigebert of Gembloux", "path": "sigebert.virgin.txt"},
    "1796":    {"author": None, "title": "Sigebert of Gembloux", "path": "sigebert.vitabrevior.txt"},
    "1797":    {"author": "Silius", "title": "Liber I", "path": "silius/silius1.txt"},
    "1798":    {"author": "Silius", "title": "Liber X", "path": "silius/silius10.txt"},
    "1799":    {"author": "Silius", "title": "Liber XI", "path": "silius/silius11.txt"},
    "1800":    {"author": "Silius", "title": "Liber XII", "path": "silius/silius12.txt"},
    "1801":    {"author": "Silius", "title": "Liber XIII", "path": "silius/silius13.txt"},
    "1802":    {"author": "Silius", "title": "Liber XIV", "path": "silius/silius14.txt"},
    "1803":    {"author": "Silius", "title": "Liber XV", "path": "silius/silius15.txt"},
    "1804":    {"author": "Silius", "title": "Liber XVI", "path": "silius/silius16.txt"},
    "1805":    {"author": "Silius", "title": "Liber XVII", "path": "silius/silius17.txt"},
    "1806":    {"author": "Silius", "title": "Liber II", "path": "silius/silius2.txt"},
    "1807":    {"author": "Silius", "title": "Liber IIII", "path": "silius/silius3.txt"},
    "1808":    {"author": "Silius", "title": "Liber IV", "path": "silius/silius4.txt"},
    "1809":    {"author": "Silius", "title": "Liber V", "path": "silius/silius5.txt"},
    "1810":    {"author": "Silius", "title": "Liber VI", "path": "silius/silius6.txt"},
    "1811":    {"author": "Silius", "title": "Liber VII", "path": "silius/silius7.txt"},
    "1812":    {"author": "Silius", "title": "Liber VIII", "path": "silius/silius8.txt"},
    "1813":    {"author": "Silius", "title": "Liber IX", "path": "silius/silius9.txt"},
    "1814":    {"author": None, "title": "Si me dignetur quam desidero ", "path": "simedignetur.txt"},
    "1815":    {"author": None, "title": "Alexander Smarius", "path": "smarius.txt"},
    "1816":    {"author": None, "title": "Solet annuere ", "path": "solet.txt"},
    "1817":    {"author": None, "title": "Solinus", "path": "solinus1.txt"},
    "1818":    {"author": None, "title": "Solinus", "path": "solinus1a.txt"},
    "1819":    {"author": None, "title": "Solinus", "path": "solinus2.txt"},
    "1820":    {"author": None, "title": "Solinus", "path": "solinus2a.txt"},
    "1821":    {"author": None, "title": "Solinus", "path": "solinus3.txt"},
    "1822":    {"author": None, "title": "Solinus", "path": "solinus3a.txt"},
    "1823":    {"author": None, "title": "Solinus", "path": "solinus4.txt"},
    "1824":    {"author": None, "title": "Solinus", "path": "solinus4a.txt"},
    "1825":    {"author": None, "title": "Solinus", "path": "solinus5.txt"},
    "1826":    {"author": "Spinoza", "title": "Ethica I", "path": "spinoza.ethica1.txt"},
    "1827":    {"author": "Spinoza", "title": "Ethica I ", "path": "spinoza.ethica2.txt"},
    "1828":    {"author": "Spinoza", "title": "Ethica III ", "path": "spinoza.ethica3.txt"},
    "1829":    {"author": "Spinoza", "title": "Ethica IV ", "path": "spinoza.ethica4.txt"},
    "1830":    {"author": "Spinoza", "title": "Ethica V ", "path": "spinoza.ethica5.txt"},
    "1831":    {"author": "Statius", "title": "Achilleid I", "path": "statius/achilleid1.txt"},
    "1832":    {"author": "Statius", "title": "Achilleid II", "path": "statius/achilleid2.txt"},
    "1833":    {"author": "Statius", "title": "Silvae I", "path": "statius/silvae1.txt"},
    "1834":    {"author": "Statius", "title": "Silvae II", "path": "statius/silvae2.txt"},
    "1835":    {"author": "Statius", "title": "Silvae III", "path": "statius/silvae3.txt"},
    "1836":    {"author": "Statius", "title": "Silvae IV", "path": "statius/silvae4.txt"},
    "1837":    {"author": "Statius", "title": "Silvae V", "path": "statius/silvae5.txt"},
    "1838":    {"author": "Statius", "title": "Thebaid I", "path": "statius/theb1.txt"},
    "1839":    {"author": "Statius", "title": "Thebaid X", "path": "statius/theb10.txt"},
    "1840":    {"author": "Statius", "title": "Thebaid XI", "path": "statius/theb11.txt"},
    "1841":    {"author": "Statius", "title": "Thebaid XII", "path": "statius/theb12.txt"},
    "1842":    {"author": "Statius", "title": "Thebaid II", "path": "statius/theb2.txt"},
    "1843":    {"author": "Statius", "title": "Thebaid III", "path": "statius/theb3.txt"},
    "1844":    {"author": "Statius", "title": "Thebaid IV", "path": "statius/theb4.txt"},
    "1845":    {"author": "Statius", "title": "Thebaid V", "path": "statius/theb5.txt"},
    "1846":    {"author": "Statius", "title": "Thebaid VI", "path": "statius/theb6.txt"},
    "1847":    {"author": "Statius", "title": "Thebaid VII", "path": "statius/theb7.txt"},
    "1848":    {"author": "Statius", "title": "Thebaid VIII", "path": "statius/theb8.txt"},
    "1849":    {"author": "Statius", "title": "Thebaid IX", "path": "statius/theb9.txt"},
    "1850":    {"author": "Suetonius", "title": "Divus Augustus", "path": "suetonius/suet.aug.txt"},
    "1851":    {"author": "Suetonius", "title": "Divus Iulius", "path": "suetonius/suet.caesar.txt"},
    "1852":    {"author": None, "title": "\u0007 ", "path": "suetonius/suet.cal.txt"},
    "1853":    {"author": "Suetonius", "title": "Divus Claudius", "path": "suetonius/suet.claudius.txt"},
    "1854":    {"author": "Suetonius", "title": "Life of Crispus", "path": "suetonius/suet.crispus.txt"},
    "1855":    {"author": "Suetonius", "title": "Domitian", "path": "suetonius/suet.dom.txt"},
    "1856":    {"author": "Suetonius", "title": "Life of Galba", "path": "suetonius/suet.galba.txt"},
    "1857":    {"author": "Suetonius", "title": "de Grammaticis", "path": "suetonius/suet.gram.txt"},
    "1858":    {"author": "Suetonius", "title": "Life of Horace", "path": "suetonius/suet.horace.txt"},
    "1859":    {"author": "Suetonius", "title": "Life of Lucan", "path": "suetonius/suet.lucan.txt"},
    "1860":    {"author": "Suetonius", "title": "Life of Nero", "path": "suetonius/suet.nero.txt"},
    "1861":    {"author": "Suetonius", "title": "Life of Otho", "path": "suetonius/suet.otho.txt"},
    "1862":    {"author": "Suetonius", "title": "Life of Persius", "path": "suetonius/suet.persius.txt"},
    "1863":    {"author": "Suetonius", "title": "Life of Pliny", "path": "suetonius/suet.pliny.txt"},
    "1864":    {"author": "Suetonius", "title": "de Rhetoribus", "path": "suetonius/suet.rhet.txt"},
    "1865":    {"author": "Suetonius", "title": "Life of Terence", "path": "suetonius/suet.terence.txt"},
    "1866":    {"author": "Suetonius", "title": "Life of Tiberius", "path": "suetonius/suet.tib.txt"},
    "1867":    {"author": "Suetonius", "title": "Life of Tibullus", "path": "suetonius/suet.tibullus.txt"},
    "1868":    {"author": "Suetonius", "title": "Life of Titus", "path": "suetonius/suet.titus.txt"},
    "1869":    {"author": "Suetonius", "title": "Life of Vespasian", "path": "suetonius/suet.vesp.txt"},
    "1870":    {"author": "Suetonius", "title": "Life of Vergil", "path": "suetonius/suet.virgil.txt"},
    "1871":    {"author": "Suetonius", "title": "Life of Vitellius", "path": "suetonius/suet.vit.txt"},
    "1872":    {"author": None, "title": "Sulpicia", "path": "sulpicia.txt"},
    "1873":    {"author": "Sulpicius Severus", "title": "Chronicles I", "path": "sulpiciusseveruschron1.txt"},
    "1874":    {"author": "Sulpicius Severus", "title": "Chronicles II", "path": "sulpiciusseveruschron2.txt"},
    "1875":    {"author": "Sulpicius Severus", "title": "Life of St. Martin", "path": "sulpiciusseverusmartin.txt"},
    "1876":    {"author": None, "title": "Suscipe Flos ", "path": "suscipeflos.txt"},
    "1877":    {"author": None, "title": "Publilius Syrus", "path": "syrus.txt"},
    "1878":    {"author": "Tacitus", "title": "Agricola", "path": "tacitus/tac.agri.txt"},
    "1879":    {"author": "Tacitus", "title": "Annales I", "path": "tacitus/tac.ann1.txt"},
    "1880":    {"author": "Tacitus", "title": "Annales XI", "path": "tacitus/tac.ann11.txt"},
    "1881":    {"author": "Tacitus", "title": "Annales XII", "path": "tacitus/tac.ann12.txt"},
    "1882":    {"author": "Tacitus", "title": "Annales XIII", "path": "tacitus/tac.ann13.txt"},
    "1883":    {"author": "Tacitus", "title": "Annales XIV", "path": "tacitus/tac.ann14.txt"},
    "1884":    {"author": "Tacitus", "title": "Annales XV", "path": "tacitus/tac.ann15.txt"},
    "1885":    {"author": "Tacitus", "title": "Annales XVI", "path": "tacitus/tac.ann16.txt"},
    "1886":    {"author": "Tacitus", "title": "Annales II", "path": "tacitus/tac.ann2.txt"},
    "1887":    {"author": "Tacitus", "title": "Annales III", "path": "tacitus/tac.ann3.txt"},
    "1888":    {"author": "Tacitus", "title": "Annales IV", "path": "tacitus/tac.ann4.txt"},
    "1889":    {"author": "Tacitus", "title": "Annales V", "path": "tacitus/tac.ann5.txt"},
    "1890":    {"author": "Tacitus", "title": "Annales VI", "path": "tacitus/tac.ann6.txt"},
    "1891":    {"author": "Tacitus", "title": "Dialogus de Oratoribus", "path": "tacitus/tac.dialogus.txt"},
    "1892":    {"author": "Tacitus", "title": "Germania", "path": "tacitus/tac.ger.txt"},
    "1893":    {"author": "Tacitus", "title": "Histories I", "path": "tacitus/tac.hist1.txt"},
    "1894":    {"author": "Tacitus", "title": "Histories II", "path": "tacitus/tac.hist2.txt"},
    "1895":    {"author": "Tacitus", "title": "Histories III", "path": "tacitus/tac.hist3.txt"},
    "1896":    {"author": "Tacitus", "title": "Histories IV", "path": "tacitus/tac.hist4.txt"},
    "1897":    {"author": "Tacitus", "title": "Histories V", "path": "tacitus/tac.hist5.txt"},
    "1898":    {"author": None, "title": "Tempus est iocundum ", "path": "tempusest.txt"},
    "1899":    {"author": "Terence", "title": "Adelphoe", "path": "ter.adel.txt"},
    "1900":    {"author": "Terence", "title": "Andria", "path": "ter.andria.txt"},
    "1901":    {"author": "Terence", "title": "Eunuchus", "path": "ter.eunuchus.txt"},
    "1902":    {"author": "Terence", "title": "Heauton Timorumenos", "path": "ter.heauton.txt"},
    "1903":    {"author": "Terence", "title": "Hecyra", "path": "ter.hecyra.txt"},
    "1904":    {"author": "Terence", "title": "Phormio", "path": "ter.phormio.txt"},
    "1905":    {"author": None, "title": "Terra iam pandit gremium ", "path": "terraiam.txt"}, "1906": {
        "author": None, "title": "[Tertulliani] ad Senatorem ", "path": "tertullian/tertullian.adsenatorem.txt"
    }, "1907": {"author": "Tertullian", "title": "De Anima ", "path": "tertullian/tertullian.anima.txt"},
    "1908":    {"author": "Tertullian", "title": "Apology", "path": "tertullian/tertullian.apol.txt"},
    "1909":    {"author": "Tertullian", "title": "de Baptismo ", "path": "tertullian/tertullian.baptismo.txt"},
    "1910":    {"author": "Tertullian", "title": "de Carne Christi ", "path": "tertullian/tertullian.carne.txt"},
    "1911":    {
        "author": "Tertullian", "title": "De Exhortatione Castitatis ", "path": "tertullian/tertullian.castitatis.txt"
    }, "1912": {
        "author": "Tertullian", "title": "Liber De Corona Militis ", "path": "tertullian/tertullian.corona.txt"
    }, "1913": {
        "author": "Tertullian", "title": "Tertulliani De Cultu Feminarum Libri Duo : Liber I ",
        "path":   "tertullian/tertullian.cultu1.txt"
    }, "1914": {
        "author": "Tertullian", "title": "Tertulliani De Cultu Feminarum Libri Duo : Liber II ",
        "path":   "tertullian/tertullian.cultu2.txt"
    }, "1915": {
        "author": None, "title": "[Tertulliani] Carmen de Iudicio Domini ",
        "path":   "tertullian/tertullian.deiudicio.txt"
    }, "1916": {"author": "Tertullian", "title": "De Fuga in Persecutione ", "path": "tertullian/tertullian.fuga.txt"},
    "1917":    {"author": "Tertullian", "title": "Carmen Genesis ", "path": "tertullian/tertullian.genesis.txt"},
    "1918":    {
        "author": "Tertullian", "title": "De Execrandis Gentium Diis ", "path": "tertullian/tertullian.gentium.txt"
    }, "1919": {
        "author": "Tertullian", "title": "Adversus Omnes Haereses ", "path": "tertullian/tertullian.haereses.txt"
    }, "1920": {
        "author": "Tertullian", "title": "Liber adversus Hermogenem ", "path": "tertullian/tertullian.herm.txt"
    }, "1921": {"author": "Tertullian", "title": "De Idololatria", "path": "tertullian/tertullian.idololatria.txt"},
    "1922":    {"author": "Tertullian", "title": "de Ieiunio", "path": "tertullian/tertullian.ieiunio.txt"},
    "1923":    {"author": "Tertullian", "title": "Adversus Iudaeos ", "path": "tertullian/tertullian.iudaeos.txt"},
    "1924":    {
        "author": "Tertullian", "title": "Adversus Marcionem I ", "path": "tertullian/tertullian.marcionem1.txt"
    }, "1925": {
        "author": "Tertullian", "title": "Adversus Marcionem II ", "path": "tertullian/tertullian.marcionem2.txt"
    }, "1926": {
        "author": "Tertullian", "title": "Adversus Marcionem III ", "path": "tertullian/tertullian.marcionem3.txt"
    }, "1927": {
        "author": "Tertullian", "title": "Adversus Marcionem IV ", "path": "tertullian/tertullian.marcionem4.txt"
    }, "1928": {
        "author": "Tertullian", "title": "Adversus Marcionem V ", "path": "tertullian/tertullian.marcionem5.txt"
    }, "1929": {"author": "Tertullian", "title": "Ad Martyres ", "path": "tertullian/tertullian.martyres.txt"},
    "1930":    {"author": "Tertullian", "title": "Liber de Monogamia ", "path": "tertullian/tertullian.monog.txt"},
    "1931":    {"author": "Tertullian", "title": "ad Nationes I ", "path": "tertullian/tertullian.nationes1.txt"},
    "1932":    {"author": "Tertullian", "title": "ad Nationes II ", "path": "tertullian/tertullian.nationes2.txt"},
    "1933":    {"author": "Tertullian", "title": "de Oratione ", "path": "tertullian/tertullian.oratione.txt"},
    "1934":    {"author": "Tertullian", "title": "De Paenitentia ", "path": "tertullian/tertullian.paen.txt"},
    "1935":    {"author": "Tertullian", "title": "de Pallio ", "path": "tertullian/tertullian.pallio.txt"},
    "1936":    {"author": "Tertullian", "title": "De Patientia ", "path": "tertullian/tertullian.patientia.txt"},
    "1937":    {
        "author": "Tertullian", "title": "De Praescriptione Haereticorum ",
        "path":   "tertullian/tertullian.praescrip.txt"
    }, "1938": {"author": "Tertullian", "title": "Adversus Praexean ", "path": "tertullian/tertullian.praxean.txt"},
    "1939":    {
        "author": "Tertullian", "title": "Carmen de Iona propheta ", "path": "tertullian/tertullian.propheta.txt"
    }, "1940": {"author": "Tertullian", "title": "de Oratione ", "path": "tertullian/tertullian.pudicitia.txt"},
    "1941":    {
        "author": "Tertullian ", "title": "De Resurrectione Carnis ", "path": "tertullian/tertullian.resurrectione.txt"
    }, "1942": {"author": "Tertullian", "title": "ad Scapulam ", "path": "tertullian/tertullian.scapulam.txt"},
    "1943":    {"author": "Tertullian ", "title": "Scorpiace ", "path": "tertullian/tertullian.scorpiace.txt"},
    "1944":    {"author": "Tertullian", "title": "de Spectaculis ", "path": "tertullian/tertullian.spect.txt"},
    "1945":    {
        "author": "Tertullian", "title": "de Testimonio Animae ", "path": "tertullian/tertullian.testimonia.txt"
    }, "1946": {"author": "Tertullian", "title": "ad Uxorem I ", "path": "tertullian/tertullian.uxor1.txt"},
    "1947":    {"author": "Tertullian", "title": "ad Uxorem II ", "path": "tertullian/tertullian.uxor2.txt"}, "1948": {
        "author": "Tertullian", "title": "Adversus Valentinianos ", "path": "tertullian/tertullian.valentinianos.txt"
    }, "1949": {
        "author": "Tertullian", "title": "de Virginibus Velandis", "path": "tertullian/tertullian.virginibus.txt"
    }, "1950": {"author": None, "title": "Testamentum Porcelli", "path": "testamentum.txt"},
    "1951":    {"author": None, "title": "", "path": "tevigilans.txt"},
    "1952":    {"author": "Theganus", "title": "Vita Hludowici Imperatoris", "path": "theganus.txt"},
    "1953":    {"author": None, "title": "Theodulus", "path": "theodolus.txt"},
    "1954":    {"author": "Theodosiani Codex", "title": "Liber I", "path": "theodosius/theod01.txt"},
    "1955":    {"author": "Theodosiani Codex", "title": "Liber II", "path": "theodosius/theod02.txt"},
    "1956":    {"author": "Theodosiani Codex", "title": "Liber III", "path": "theodosius/theod03.txt"},
    "1957":    {"author": "Theodosiani Codex", "title": "Liber IV", "path": "theodosius/theod04.txt"},
    "1958":    {"author": "Theodosiani Codex", "title": "Liber V", "path": "theodosius/theod05.txt"},
    "1959":    {"author": "Theodosiani Codex", "title": "Liber VI", "path": "theodosius/theod06.txt"},
    "1960":    {"author": "Theodosiani Codex", "title": "Liber VII", "path": "theodosius/theod07.txt"},
    "1961":    {"author": "Theodosiani Codex", "title": "Liber VIII", "path": "theodosius/theod08.txt"},
    "1962":    {"author": "Theodosiani Codex", "title": "Liber IX", "path": "theodosius/theod09.txt"},
    "1963":    {"author": "Theodosiani Codex", "title": "Liber X", "path": "theodosius/theod10.txt"},
    "1964":    {"author": "Theodosiani Codex", "title": "Liber XI", "path": "theodosius/theod11.txt"},
    "1965":    {"author": "Theodosiani Codex", "title": "Liber XII", "path": "theodosius/theod12.txt"},
    "1966":    {"author": "Theodosiani Codex", "title": "Liber XIII", "path": "theodosius/theod13.txt"},
    "1967":    {"author": "Theodosiani Codex", "title": "Liber XIV", "path": "theodosius/theod14.txt"},
    "1968":    {"author": "Theodosiani Codex", "title": "Liber XV", "path": "theodosius/theod15.txt"},
    "1969":    {"author": "Theodosiani Codex", "title": "Liber XVI", "path": "theodosius/theod16.txt"},
    "1970":    {"author": "Theophanes Prokopovic", "title": "Epigrammata", "path": "theophanes.txt"},
    "1971":    {"author": "Johannes de Alta Silva", "title": "de Thesauro et Fure Astuto", "path": "thesauro.txt"},
    "1972":    {"author": None, "title": "Thomas of Edessa (Carr)", "path": "thomasedessa.txt"},
    "1973":    {"author": None, "title": "Tibullus Book I", "path": "tibullus1.txt"},
    "1974":    {"author": None, "title": "Tibullus Book II", "path": "tibullus2.txt"},
    "1975":    {"author": None, "title": "Tibullus Book III", "path": "tibullus3.txt"},
    "1976":    {"author": None, "title": "Augustin T\u00fcnger", "path": "tunger.txt"},
    "1977":    {"author": "Valerius Flaccus", "title": "Liber I", "path": "valeriusflaccus1.txt"},
    "1978":    {"author": "Valerius Flaccus", "title": "Liber II", "path": "valeriusflaccus2.txt"},
    "1979":    {"author": "Valerius Flaccus", "title": "Liber III", "path": "valeriusflaccus3.txt"},
    "1980":    {"author": "Valerius Flaccus", "title": "Liber IV", "path": "valeriusflaccus4.txt"},
    "1981":    {"author": "Valerius Flaccus", "title": "Liber V", "path": "valeriusflaccus5.txt"},
    "1982":    {"author": "Valerius Flaccus", "title": "Liber VI", "path": "valeriusflaccus6.txt"},
    "1983":    {"author": "Valerius Flaccus", "title": "Liber VII", "path": "valeriusflaccus7.txt"},
    "1984":    {"author": "Valerius Flaccus", "title": "Liber VIII", "path": "valeriusflaccus8.txt"},
    "1985":    {"author": None, "title": "Anonymus Valesianus", "path": "valesianus.txt"},
    "1986":    {"author": "Anonymus Valesianus", "title": "Origo Constantini Imperatoris", "path": "valesianus1.txt"},
    "1987":    {"author": "Anonymus Valesianus", "title": "Chronica Theodericiana", "path": "valesianus2.txt"},
    "1988":    {"author": None, "title": "Valerius Maximus I", "path": "valmax1.txt"},
    "1989":    {"author": None, "title": "Valerius Maximus II", "path": "valmax2.txt"},
    "1990":    {"author": None, "title": "Valerius Maximus III", "path": "valmax3.txt"},
    "1991":    {"author": None, "title": "Valerius Maximus IV", "path": "valmax4.txt"},
    "1992":    {"author": None, "title": "Valerius Maximus V", "path": "valmax5.txt"},
    "1993":    {"author": None, "title": "Valerius Maximus VI", "path": "valmax6.txt"},
    "1994":    {"author": None, "title": "Valerius Maximus VII", "path": "valmax7.txt"},
    "1995":    {"author": None, "title": "Valerius Maximus VIII", "path": "valmax8.txt"},
    "1996":    {"author": None, "title": "Valerius Maximus I", "path": "valmax9.txt"},
    "1997":    {"author": None, "title": "", "path": "varro.frag.txt"},
    "1998":    {"author": None, "title": "", "path": "varro.ll10.txt"},
    "1999":    {"author": None, "title": "", "path": "varro.ll5.txt"},
    "2000":    {"author": None, "title": "", "path": "varro.ll6.txt"},
    "2001":    {"author": None, "title": "", "path": "varro.ll7.txt"},
    "2002":    {"author": None, "title": "", "path": "varro.ll8.txt"},
    "2003":    {"author": None, "title": "", "path": "varro.ll9.txt"},
    "2004":    {"author": "Varro", "title": "De Agri Cultura I", "path": "varro.rr1.txt"},
    "2005":    {"author": "Varro", "title": "De Agri Cultura II", "path": "varro.rr2.txt"},
    "2006":    {"author": "Varro", "title": "De Agri Cultura III", "path": "varro.rr3.txt"},
    "2007":    {"author": "Vegetius", "title": "Liber I", "path": "vegetius1.txt"},
    "2008":    {"author": "Vegetius", "title": "Liber II", "path": "vegetius2.txt"},
    "2009":    {"author": "Vegetius", "title": "Liber III", "path": "vegetius3.txt"},
    "2010":    {"author": "Vegetius", "title": "Liber IV", "path": "vegetius4.txt"},
    "2011":    {"author": "Vegius", "title": "Aeneidos Supplementum", "path": "vegius.txt"},
    "2012":    {"author": None, "title": "Velleius Paterculus", "path": "vell1.txt"},
    "2013":    {"author": None, "title": "Velleius Paterculus", "path": "vell2.txt"},
    "2014":    {"author": None, "title": "Venantius Fortunatus", "path": "venantius.txt"},
    "2015":    {"author": "Vergil", "title": "Aeneid I", "path": "vergil/aen1.txt"},
    "2016":    {"author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER DECIMVS", "path": "vergil/aen10.txt"},
    "2017":    {"author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER VNDECIMVS", "path": "vergil/aen11.txt"},
    "2018":    {"author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER PRIMVS", "path": "vergil/aen12.txt"},
    "2019":    {"author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER SECVNDVS", "path": "vergil/aen2.txt"},
    "2020":    {"author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER TERTIVS", "path": "vergil/aen3.txt"},
    "2021":    {"author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER QVARTVS", "path": "vergil/aen4.txt"},
    "2022":    {"author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER QVINTVS", "path": "vergil/aen5.txt"},
    "2023":    {"author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER SEXTVS", "path": "vergil/aen6.txt"},
    "2024":    {"author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER SEPTIMVS", "path": "vergil/aen7.txt"},
    "2025":    {"author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER OCTAVVS", "path": "vergil/aen8.txt"},
    "2026":    {"author": "P. VERGILI MARONIS", "title": "AENEIDOS LIBER NONVS", "path": "vergil/aen9.txt"},
    "2027":    {"author": "P. VERGILI MARONIS", "title": "ECLOGA PRIMA", "path": "vergil/ec1.txt"},
    "2028":    {"author": "P. VERGILI MARONIS", "title": "ECLOGA DECIMA", "path": "vergil/ec10.txt"},
    "2029":    {"author": "P. VERGILI MARONIS", "title": "ECLOGA SECVNDA", "path": "vergil/ec2.txt"},
    "2030":    {"author": "P. VERGILI MARONIS", "title": "ECLOGA TERTIA", "path": "vergil/ec3.txt"},
    "2031":    {"author": "P. VERGILI MARONIS", "title": "ECLOGA QVARTA", "path": "vergil/ec4.txt"},
    "2032":    {"author": "P. VERGILI MARONIS", "title": "ECLOGA QVINTA", "path": "vergil/ec5.txt"},
    "2033":    {"author": "P. VERGILI MARONIS", "title": "ECLOGA SEXTA", "path": "vergil/ec6.txt"},
    "2034":    {"author": "P. VERGILI MARONIS", "title": "ECLOGA SEPTIMA", "path": "vergil/ec7.txt"},
    "2035":    {"author": "P. VERGILI MARONIS", "title": "ECLOGA OCTAVA", "path": "vergil/ec8.txt"},
    "2036":    {"author": "P. VERGILI MARONIS", "title": "ECLOGA NONA", "path": "vergil/ec9.txt"},
    "2037":    {"author": "P. VERGILI MARONIS", "title": "GEORGICON LIBER PRIMVS", "path": "vergil/geo1.txt"},
    "2038":    {"author": "P. VERGILI MARONIS", "title": "GEORGICON LIBER SECVNDVS", "path": "vergil/geo2.txt"},
    "2039":    {"author": "P. VERGILI MARONIS", "title": "GEORGICON LIBER TERTIVS", "path": "vergil/geo3.txt"},
    "2040":    {"author": "P. VERGILI MARONIS", "title": "GEORGICON LIBER QVARTVS", "path": "vergil/geo4.txt"},
    "2041":    {"author": None, "title": "", "path": "vestiunt.txt"},
    "2042":    {"author": "Vicentius Lerinensis", "title": "Commonitorium", "path": "vicentius.txt"},
    "2043":    {"author": "Vico", "title": "Oratio VI", "path": "vico.orat6.txt"},
    "2044":    {"author": None, "title": "LIBER DE CAESARIBUS", "path": "victor.caes.txt"},
    "2045":    {"author": None, "title": "EPITOME DE CAESARIBUS", "path": "victor.caes2.txt"},
    "2046":    {"author": None, "title": "DE VIRIS ILLVSTRIBVS", "path": "victor.ill.txt"},
    "2047":    {"author": None, "title": "EPITOME DE CAESARIBUS", "path": "victor.origio.txt"},
    "2048":    {"author": "Vida", "title": "Scacchia, Ludus", "path": "vida.txt"},
    "2049":    {"author": None, "title": "Vita Caroli IV", "path": "vitacaroli.txt"},
    "2050":    {"author": None, "title": "De Architectura Liber I", "path": "vitruvius1.txt"},
    "2051":    {"author": None, "title": "De Architectura Liber X", "path": "vitruvius10.txt"},
    "2052":    {"author": None, "title": "De Architectura Liber II", "path": "vitruvius2.txt"},
    "2053":    {"author": None, "title": "De Architectura Liber III", "path": "vitruvius3.txt"},
    "2054":    {"author": None, "title": "De Architectura Liber IV", "path": "vitruvius4.txt"},
    "2055":    {"author": None, "title": "De Architectura Liber V", "path": "vitruvius5.txt"},
    "2056":    {"author": None, "title": "De Architectura Liber VI", "path": "vitruvius6.txt"},
    "2057":    {"author": None, "title": "De Architectura Liber VII", "path": "vitruvius7.txt"},
    "2058":    {"author": None, "title": "De Architectura Liber VIII", "path": "vitruvius8.txt"},
    "2059":    {"author": None, "title": "De Architectura Liber IX", "path": "vitruvius9.txt"},
    "2060":    {"author": None, "title": "Volo virum vivere viriliter ", "path": "volovirum.txt"},
    "2061":    {"author": "Iacobus de Voragine", "title": "de Sancto Alexio", "path": "voragine/alexio.txt"},
    "2062":    {"author": "Iacobus de Voragine", "title": "Historia de Sancto Ambrosio", "path": "voragine/ambro.txt"},
    "2063":    {"author": "Iacobus de Voragine", "title": "Historia de Sancta Anastasia", "path": "voragine/anast.txt"},
    "2064":    {"author": "Iacobus de Voragine", "title": "De Sancto Andrea Apostolo", "path": "voragine/andrea.txt"},
    "2065":    {"author": "Iacobus de Voragine", "title": "Historia de Sancto Antonio", "path": "voragine/ant.txt"},
    "2066":    {"author": "Iacobus de Voragine", "title": "Historia de Sancto Blasio", "path": "voragine/blas.txt"},
    "2067":    {
        "author": "Iacobus de Voragine", "title": "Historia de Sancto Christophoro", "path": "voragine/chris.txt"
    }, "2068": {"author": "Iacobus de Voragine", "title": "Historia de Sancto Francisco", "path": "voragine/fran.txt"},
    "2069":    {"author": "Iacobus de Voragine", "title": "Historia de Sancto Georgio", "path": "voragine/georgio.txt"},
    "2070":    {
        "author": "Iacobus de Voragine", "title": "Historia de Sancto Iacobo Maiore", "path": "voragine/iacob.txt"
    }, "2071": {"author": "Iacobus de Voragine", "title": "Historia de Sancto Iuliano", "path": "voragine/iul.txt"},
    "2072":    {"author": "Iacobus de Voragine", "title": "Historia de Juda Ischariota", "path": "voragine/jud.txt"},
    "2073":    {"author": "Iacobus de Voragine", "title": "Historia Sanctae Luciae", "path": "voragine/luc.txt"},
    "2074":    {"author": "Iacobus de Voragine", "title": "Historia de Sancto Macario", "path": "voragine/marc.txt"},
    "2075":    {"author": "Iacobus de Voragine", "title": "Historia de Sancta Maria Magdalena", "path": "voragine/mariamag.txt"},
    "2076":    {
        "author": "Iacobus de Voragine", "title": "Historia de sancta Marina virgine", "path": "voragine/marina.txt"
    }, "2077": {"author": "Iacobus de Voragine", "title": "Historia Sancti Nicolai", "path": "voragine/nic.txt"},
    "2078":    {
        "author": "Iacobus de Voragine", "title": "Historia de Sancto Paulo Eremita", "path": "voragine/paulo.txt"
    }, "2079": {"author": "Iacobus de Voragine", "title": "Historia de Sancto Sebastiano", "path": "voragine/seb.txt"},
    "2080":    {
        "author": "Iacobus de Voragine", "title": "Historia de Septem Dormientibus", "path": "voragine/septem.txt"
    }, "2081": {"author": "Iacobus de Voragine", "title": "Historia de Sancto Silvestro", "path": "voragine/silv.txt"},
    "2082":    {
        "author": "Iacobus de Voragine", "title": "Historia de Sancto Thoma apostolo", "path": "voragine/thom.txt"
    }, "2083": {"author": "Iacobus de Voragine", "title": "Historia de Sancto Vincentio", "path": "voragine/vin.txt"},
    "2084":    {
        "author": "Iacobus de Voragine", "title": "Historia de Virgine Quadam Antiochena", "path": "voragine/vir.txt"
    }, "2085": {"author": None, "title": "Carmina Henrici Waardenburg", "path": "waardenburg.txt"},
    "2086":    {"author": None, "title": "Waltharius I", "path": "waltarius1.txt"},
    "2087":    {"author": None, "title": "Waltharius II", "path": "waltarius2.txt"},
    "2088":    {"author": None, "title": "Waltharius III", "path": "waltarius3.txt"},
    "2089":    {"author": None, "title": "Walter of Ch\u00e2tillon", "path": "walter/pastourelles.txt"},
    "2090":    {"author": None, "title": "Walter of Ch\u00e2tillon", "path": "walter/walter1.txt"},
    "2091":    {"author": None, "title": "Walter of Ch\u00e2tillon", "path": "walter/walter2.txt"},
    "2092":    {"author": None, "title": "Walter of Ch\u00e2tillon", "path": "walter/walter3.txt"},
    "2093":    {"author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon", "path": "walter10.txt"},
    "2094":    {"author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon", "path": "walter11.txt"},
    "2095":    {"author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon", "path": "walter12.txt"},
    "2096":    {"author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon", "path": "walter4.txt"},
    "2097":    {"author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon", "path": "walter5.txt"},
    "2098":    {"author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon", "path": "walter6.txt"},
    "2099":    {"author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon", "path": "walter7.txt"},
    "2100":    {"author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon", "path": "walter8.txt"},
    "2101":    {"author": None, "title": "Walter of Ch\u00e2tillon  Walter of Ch\u00e2tillon", "path": "walter9.txt"},
    "2102":    {"author": None, "title": "Brad Walton", "path": "walton.txt"},
    "2103":    {"author": "William of Apulia", "title": "Gesta Roberti Wiscardi", "path": "williamapulia.txt"},
    "2104":    {"author": "William of Tyre", "title": "Liber I", "path": "williamtyre/1.txt"},
    "2105":    {"author": "William of Tyre", "title": "Liber X", "path": "williamtyre/10.txt"},
    "2106":    {"author": "William of Tyre", "title": "Liber XI", "path": "williamtyre/11.txt"},
    "2107":    {"author": "William of Tyre", "title": "Liber XII", "path": "williamtyre/12.txt"},
    "2108":    {"author": "William of Tyre", "title": "Liber XIII", "path": "williamtyre/13.txt"},
    "2109":    {"author": "William of Tyre", "title": "Liber XIV", "path": "williamtyre/14.txt"},
    "2110":    {"author": "William of Tyre", "title": "Liber XV", "path": "williamtyre/15.txt"},
    "2111":    {"author": "William of Tyre", "title": "Liber XVI", "path": "williamtyre/16.txt"},
    "2112":    {"author": "William of Tyre", "title": "Liber XVII", "path": "williamtyre/17.txt"},
    "2113":    {"author": "William of Tyre", "title": "Liber XVIII", "path": "williamtyre/18.txt"},
    "2114":    {"author": "William of Tyre", "title": "Liber XIX", "path": "williamtyre/19.txt"},
    "2115":    {"author": "William of Tyre", "title": "Liber II", "path": "williamtyre/2.txt"},
    "2116":    {"author": "William of Tyre", "title": "Liber XX", "path": "williamtyre/20.txt"},
    "2117":    {"author": "William of Tyre", "title": "Liber XXI", "path": "williamtyre/21.txt"},
    "2118":    {"author": "William of Tyre", "title": "Liber XXII", "path": "williamtyre/22.txt"},
    "2119":    {"author": "William of Tyre", "title": "Liber XXIII", "path": "williamtyre/23.txt"},
    "2120":    {"author": "William of Tyre", "title": "Liber III", "path": "williamtyre/3.txt"},
    "2121":    {"author": "William of Tyre", "title": "Liber IV", "path": "williamtyre/4.txt"},
    "2122":    {"author": "William of Tyre", "title": "Liber V", "path": "williamtyre/5.txt"},
    "2123":    {"author": "William of Tyre", "title": "Liber VI", "path": "williamtyre/6.txt"},
    "2124":    {"author": "William of Tyre", "title": "Liber VII", "path": "williamtyre/7.txt"},
    "2125":    {"author": "William of Tyre", "title": "Liber VIII", "path": "williamtyre/8.txt"},
    "2126":    {"author": "William of Tyre", "title": "Liber IX", "path": "williamtyre/9.txt"},
    "2127":    {"author": "William of Tyre", "title": "Prologus", "path": "williamtyre/prologus.txt"},
    "2128":    {"author": "Johann Hildebrand Withof", "title": None, "path": "withof.txt"},
    "2129":    {"author": "Johann Hildebrand Withof", "title": None, "path": "withof1.txt"},
    "2130":    {"author": "Johann Hildebrand Withof", "title": None, "path": "withof2.txt"},
    "2131":    {"author": "Johann Hildebrand Withof", "title": None, "path": "withof3.txt"},
    "2132":    {"author": "Johann Hildebrand Withof", "title": None, "path": "withof4.txt"},
    "2133":    {"author": "Johann Hildebrand Withof", "title": None, "path": "withof5.txt"},
    "2134":    {"author": "Johann Hildebrand Withof", "title": None, "path": "withof6.txt"},
    "2135":    {"author": "Johann Hildebrand Withof", "title": None, "path": "withof7.txt"}, "2136": {
        "author": "[William of Conches]", "title": "Moralium dogma philosophorum", "path": "wmconchesdogma.txt"
    }, "2137": {"author": None, "title": "William of Conches", "path": "wmconchesphil.txt"},
    "2138":    {"author": None, "title": "Annales qui dicuntur Xantenses", "path": "xanten.txt"},
    "2139":    {"author": "Xylander", "title": "Vita Caesaris", "path": "xylander/caesar.txt"},
    "2140":    {"author": "Zonaras", "title": "Excerpta", "path": "zonaras.txt"}
}
