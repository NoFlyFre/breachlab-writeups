# Ghost Track - Ghost 1

[← Torna all'indice](../../README.md)

## Sommario

- Track: Ghost
- Livello: Ghost 1
- Fonte appunti: `ghost_track/ghost1/notes.md`

## Obiettivo

La directory di partenza contiene alcuni file con nomi pensati per scoraggiare l'analista: un file `MANIFEST` che si presenta come una nota di testo "narrativa" e un secondo file dal nome insolito, con uno spazio letterale nel nome. L'obiettivo del livello è non fermarsi al primo ostacolo cosmetico ed enumerare per intero il contenuto della directory.

## Ricognizione

Un primo giro con `cat` sul file `MANIFEST` restituisce un messaggio in cui l'autore dichiara esplicitamente di aver scelto i nomi dei file apposta per far desistere gli analisti più frettolosi. È un chiaro indizio meta: il livello valuta la disciplina nell'enumerare tutto ciò che è presente in una directory, senza lasciarsi scoraggiare da nomi di file strani o da testo "narrativo" fuorviante.

## Tecnica

Non c'è una vulnerabilità software in senso stretto: la tecnica è procedurale ed è tipica della fase di ricognizione in un'intrusione reale — enumerare con cura tutti i file di una directory, inclusi quelli con nomi anomali (spazi, caratteri speciali, nomi civetta), invece di fermarsi al primo file che sembra irrilevante. Un nome file "scherzoso" può in realtà nascondere il dato utile.

## Sfruttamento

1. Lettura del primo file trovato nella home directory con `cat`, che restituisce un testo di "flavor" scritto in prima persona dall'autore del livello, confermando che si tratta di un test di pazienza/enumerazione più che di un exploit tecnico.

2. Prosecuzione dell'enumerazione della directory: viene individuato un secondo file il cui nome contiene uno spazio letterale. Per riferirlo correttamente in una shell POSIX occorre effettuare l'escape del carattere spazio (con backslash, oppure racchiudendo il nome fra virgolette).

3. Lettura del contenuto del secondo file con lo stesso comando usato al passo 1, applicando l'escaping corretto del nome.

## Risultato

Proseguendo l'enumerazione oltre il file "esca" iniziale si ottiene il valore conclusivo del livello, contenuto nel secondo file. Il valore letterale non viene riportato qui: `<REDACTED_FLAG>`. Il livello premia la costanza nel controllare ogni file presente nella directory, senza fermarsi al primo ostacolo psicologico.

## Nota di pubblicazione

Questo writeup è la versione pubblica (GitHub) delle note personali sul livello Ghost 1 di BreachLab. In conformità alla dottrina BreachLab (Writeups · Creators), il documento insegna il metodo di ricognizione/enumerazione usato per risolvere il livello, ma non riporta password, flag o hint letterali che permetterebbero di saltare il ragionamento. Chi vuole risolvere il livello deve comunque enumerare ed esplorare la directory in autonomia.

---

## Crediti

Livello svolto su BreachLab (breachlab.org), Ghost Track. Credit a BreachLab per la piattaforma e il design del livello.
