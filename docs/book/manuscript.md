# Imparare l'italiano con Zucchero

## Learn Italian with Zucchero

*Learn Italian with Zucchero* non è un corso travestito da playlist.\
_Learn Italian with Zucchero is not a course disguised as a playlist._

È un modo di studiare una lingua dentro una voce, dentro una cadenza, dentro una
memoria che ritorna.\
_It is a way to study a language inside a voice, inside a cadence, inside a
memory that comes back._

La canzone non viene usata come decorazione: diventa il laboratorio.\
_The song is not used as decoration: it becomes the laboratory._

Il metodo parte da una cosa semplice.\
_The method begins with something simple._

Prima ascoltiamo.\
_First we listen._

Poi costruiamo un sottotitolo che rispetta la frase musicale: italiano sopra,
inglese pulito sotto.\
_Then we build a subtitle that respects the musical phrase: Italian above, clear
English below._

L'italiano resta il centro della pagina.\
_Italian remains the center of the page._

L'inglese non prende il comando; serve solo a togliere la nebbia dal significato.\
_English does not take command; it only serves to lift the fog from the meaning._

Quando la frase è chiara, non la spezziamo in frammenti scolastici.\
_When the phrase is clear, we do not break it into schoolbook fragments._

Quando non è chiara, rallentiamo.\
_When it is not clear, we slow down._

Whisper e Parakeet ci danno indizi di tempo, ma non decidono il testo.\
_Whisper and Parakeet give us timing clues, but they do not decide the text._

Il testo autorevole resta la fonte locale fornita per lo studio.\
_The authoritative text remains the local source supplied for study._

La macchina ascolta, l'umano giudica, e il sottotitolo finale diventa una piccola
partitura di comprensione.\
_The machine listens, the human judges, and the final subtitle becomes a small
score for understanding._

Questo cambia anche il modo di imparare parole nuove.\
_This also changes the way we learn new words._

Non si memorizza una lista isolata; si ritrova una parola nel punto esatto in cui
il cantante la appoggia.\
_You do not memorize an isolated list; you meet a word again at the exact point
where the singer places it._

Il verbo arriva con la respirazione, l'articolo con la melodia, il pronome con il
ritorno del ritornello.\
_The verb arrives with the breath, the article with the melody, the pronoun with
the return of the refrain._

La grammatica smette di essere una tabella e diventa un'abitudine dell'orecchio.\
_Grammar stops being a table and becomes a habit of the ear._

Il lavoro ha tre passaggi.\
_The work has three steps._

1. Trascrivere abbastanza per avere tempi affidabili.\
   _Transcribe enough to have reliable timings._
2. Allineare quei tempi alle righe italiane fornite.\
   _Align those timings to the supplied Italian lines._
3. Scrivere una traduzione inglese sobria, utile, non invadente.\
   _Write an English translation that is restrained, useful, and unobtrusive._

Quando la traduzione cambia ma i tempi sono buoni, non rifacciamo tutto.\
_When the translation changes but the timings are good, we do not redo
everything._

Si ricostruisce il file finale dai tempi esistenti.\
_The final file is rebuilt from the existing timings._

Quando il prompt aiuta il riconoscimento, contiene solo italiano: mai le
traduzioni inglesi mischiate alla voce italiana.\
_When the prompt helps recognition, it contains only Italian: never English
translations mixed into the Italian voice._

Questa disciplina rende il processo ripetibile.\
_This discipline makes the process repeatable._

Il risultato non è un museo di testi.\
_The result is not a museum of texts._

È una biblioteca di ascolti.\
_It is a library of listenings._

Ogni canzone porta con sé un piccolo circuito: media locale, trascrizione, tempi,
file di studio, costruttore riproducibile.\
_Each song carries a small circuit with it: local media, transcription, timings,
study file, reproducible builder._

Lo studente può tornare allo stesso punto, riascoltare, correggere, capire
meglio, e poi passare alla canzone successiva con un orecchio più allenato.\
_The student can return to the same point, listen again, correct, understand
better, and then move to the next song with a better-trained ear._

La versione pubblica di questo libro mantiene un confine netto: descrive il
metodo, collega gli script, e registra quali fonti locali sono state lavorate.\
_The public version of this book keeps a clear boundary: it describes the method,
links the scripts, and records which local sources have been worked through._

Non ridistribuisce i testi integrali delle canzoni.\
_It does not redistribute the complete song lyrics._

Per studiare, i testi restano nei file locali autorizzati e nei sottotitoli
privati.\
_For study, the texts remain in the authorized local files and private subtitles._

Il processo pratico per preparare quei file è semplice e ripetibile: cercare su
Google `Zucchero <titolo della canzone> lyrics`, leggere il risultato italiano,
premere il pulsante `Translate`, e salvare localmente la resa bilingue.\
_The practical process for preparing those files is simple and repeatable: search
Google for `Zucchero <song title> lyrics`, read the Italian result, press the
`Translate` button, and save the bilingual rendering locally._

Nel repository pubblico resta solo la descrizione del processo; i file completi
rimangono nella cartella locale `lyrics/`.\
_In the public repository, only the description of the process remains; the
complete files stay in the local `lyrics/` folder._

## Materiali lavorati finora

L'indice seguente registra tutte le fonti liriche locali già lavorate nel
percorso.\
_The following index records all the local lyric sources already worked through
in the path._

I conteggi non sono versi pubblicati: indicano quante unità di studio sono
presenti nei file locali.\
_The counts are not published lines: they indicate how many study units are
present in the local files._

<!-- LYRIC_INDEX -->

## Script e riproducibilità

Gli script vivono nel repository pubblico:
[github.com/alexy/zucchero](https://github.com/alexy/zucchero).\
_The scripts live in the public repository:
[github.com/alexy/zucchero](https://github.com/alexy/zucchero)._

Il file principale di orientamento è `AGENTS.md`: lì sono documentati i comandi
per Whisper, Parakeet, i builder specifici per canzone, il formato italiano /
inglese, e il vincolo di usare solo righe italiane quando si costruisce un
prompt per il riconoscimento.\
_The main orientation file is `AGENTS.md`: it documents the commands for Whisper,
Parakeet, the song-specific builders, the Italian / English format, and the rule
that only Italian lines are used when building a recognition prompt._

Il libro pubblico è pubblicato nella libreria First Pair:
[firstpair.org/#zucchero](https://firstpair.org/#zucchero).\
_The public book is published in the First Pair library:
[firstpair.org/#zucchero](https://firstpair.org/#zucchero)._

Per una copia privata del libro con i testi bilingui locali inclusi, usare:\
_For a private copy of the book with the local bilingual lyrics included, use:_

```sh
INCLUDE_LOCAL_LYRICS=1 python3 tools/build_book.py
```

Questo comando scrive in `docs/book/private/`, una cartella esclusa da Git e non
destinata alla pubblicazione.\
_This command writes to `docs/book/private/`, a folder excluded from Git and not
intended for publication._

<!-- PRIVATE_LYRICS -->

## Nota finale

Il punto non è "capire tutto subito".\
_The point is not "to understand everything immediately."_

Il punto è creare una superficie onesta in cui l'ascolto può migliorare.\
_The point is to create an honest surface where listening can improve._

La canzone resta viva; lo studio smette di essere freddo.\
_The song remains alive; study stops being cold._

E, poco alla volta, l'italiano comincia a suonare meno come una lingua straniera
e più come una stanza in cui si sa già tornare.\
_And, little by little, Italian begins to sound less like a foreign language and
more like a room you already know how to return to._
