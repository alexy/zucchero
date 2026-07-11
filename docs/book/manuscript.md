# Imparare l'italiano con Zucchero

## Learn Italian with Zucchero

*Learn Italian with Zucchero* non è un corso travestito da playlist. È un modo
di studiare una lingua dentro una voce, dentro una cadenza, dentro una memoria
che ritorna. La canzone non viene usata come decorazione: diventa il laboratorio.

Il metodo parte da una cosa semplice. Prima ascoltiamo. Poi costruiamo un
sottotitolo che rispetta la frase musicale: italiano sopra, inglese pulito sotto.
L'italiano resta il centro della pagina. L'inglese non prende il comando; serve
solo a togliere la nebbia dal significato.

Quando la frase è chiara, non la spezziamo in frammenti scolastici. Quando non
è chiara, rallentiamo. Whisper e Parakeet ci danno indizi di tempo, ma non
decidono il testo. Il testo autorevole resta la fonte locale fornita per lo
studio. La macchina ascolta, l'umano giudica, e il sottotitolo finale diventa una
piccola partitura di comprensione.

Questo cambia anche il modo di imparare parole nuove. Non si memorizza una lista
isolata; si ritrova una parola nel punto esatto in cui il cantante la appoggia.
Il verbo arriva con la respirazione, l'articolo con la melodia, il pronome con
il ritorno del ritornello. La grammatica smette di essere una tabella e diventa
un'abitudine dell'orecchio.

Il lavoro ha tre passaggi.

1. Trascrivere abbastanza per avere tempi affidabili.
2. Allineare quei tempi alle righe italiane fornite.
3. Scrivere una traduzione inglese sobria, utile, non invadente.

Quando la traduzione cambia ma i tempi sono buoni, non rifacciamo tutto. Si
ricostruisce il file finale dai tempi esistenti. Quando il prompt aiuta il
riconoscimento, contiene solo italiano: mai le traduzioni inglesi mischiate alla
voce italiana. Questa disciplina rende il processo ripetibile.

Il risultato non è un museo di testi. È una biblioteca di ascolti. Ogni canzone
porta con sé un piccolo circuito: media locale, trascrizione, tempi, file di
studio, costruttore riproducibile. Lo studente può tornare allo stesso punto,
riascoltare, correggere, capire meglio, e poi passare alla canzone successiva
con un orecchio più allenato.

La versione pubblica di questo libro mantiene un confine netto: descrive il
metodo, collega gli script, e registra quali fonti locali sono state lavorate.
Non ridistribuisce i testi integrali delle canzoni. Per studiare, i testi
restano nei file locali autorizzati e nei sottotitoli privati.

Il processo pratico per preparare quei file è semplice e ripetibile: cercare su
Google `Zucchero <titolo della canzone> lyrics`, leggere il risultato italiano,
premere il pulsante `Translate`, e salvare localmente la resa bilingue. Nel
repository pubblico resta solo la descrizione del processo; i file completi
rimangono nella cartella locale `lyrics/`.

## Materiali lavorati finora

L'indice seguente registra tutte le fonti liriche locali già lavorate nel
percorso. I conteggi non sono versi pubblicati: indicano quante unità di studio
sono presenti nei file locali.

<!-- LYRIC_INDEX -->

## Script e riproducibilità

Gli script vivono nel repository pubblico:
[github.com/alexy/zucchero](https://github.com/alexy/zucchero).

Il file principale di orientamento è `AGENTS.md`: lì sono documentati i comandi
per Whisper, Parakeet, i builder specifici per canzone, il formato italiano /
inglese, e il vincolo di usare solo righe italiane quando si costruisce un
prompt per il riconoscimento.

Il libro pubblico è pubblicato nella libreria First Pair:
[firstpair.org/#zucchero](https://firstpair.org/#zucchero).

Per una copia privata del libro con i testi bilingui locali inclusi, usare:

```sh
INCLUDE_LOCAL_LYRICS=1 python3 tools/build_book.py
```

Questo comando scrive in `docs/book/private/`, una cartella esclusa da Git e non
destinata alla pubblicazione.

<!-- PRIVATE_LYRICS -->

## Nota finale

Il punto non è "capire tutto subito". Il punto è creare una superficie onesta in
cui l'ascolto può migliorare. La canzone resta viva; lo studio smette di essere
freddo. E, poco alla volta, l'italiano comincia a suonare meno come una lingua
straniera e più come una stanza in cui si sa già tornare.
