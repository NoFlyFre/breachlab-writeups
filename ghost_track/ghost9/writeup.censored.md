# Ghost Track - Ghost 9

## Sommario

- Track: Ghost
- Livello: Ghost 9
- Fonte appunti: `ghost_track/ghost9/notes.md`
- Variante: censored (pubblica)

## Obiettivo

Il brief ("Core Dump") racconta che un processo agente è crashato lasciando un core dump su disco. I segreti che erano in memoria al momento del crash sono finiti "verbatim" (in chiaro) nel dump. L'obiettivo è estrarre il token corretto dal core dump — il brief avverte esplicitamente di non leggere i byte grezzi (`cat` sul binario), ma di usare uno strumento adatto a testo stampabile dentro un file binario — per ottenere la password dell'account del livello successivo.

## Ricognizione

Nella home directory è presente un file di core dump di alcuni KB, leggibile dal gruppo, oltre a un file secondario illeggibile che non è rilevante per la soluzione. Un tentativo di lettura diretta del core dump con `cat` restituisce solo dati binari illeggibili, confermando che serve uno strumento diverso per estrarne il contenuto testuale.

## Tecnica

La tecnica è l'estrazione di stringhe stampabili da un file binario (in questo caso un core dump di processo) con il comando `strings`, seguita dall'ispezione visiva dell'output alla ricerca di variabili d'ambiente o strutture dati riconoscibili. I core dump di processo contengono spesso, tra i tanti byte di memoria heap/stack non interpretabili, blocchi testuali chiari come le variabili d'ambiente del processo al momento del crash (tipicamente conservate in una regione contigua di memoria) — che possono includere segreti come token o credenziali se il processo li teneva in variabili d'ambiente anziché gestirli in modo più sicuro.

## Sfruttamento

1. Enumerazione della home directory, che rivela il file del core dump del processo agente.

2. Tentativo (fallito, come atteso dal brief) di leggere il file direttamente con `cat`, che mostra solo un blob binario non interpretabile.

3. Estrazione delle stringhe stampabili dal core dump con `strings`, che produce un lungo elenco di frammenti; la maggior parte sono sequenze binarie casuali non significative, ma tra queste emerge un blocco riconoscibile di variabili d'ambiente del processo agente al momento del crash, tra cui una variabile che contiene il token di autenticazione dell'agente, marcata visivamente nell'output.

## Risultato

Estraendo le stringhe dal core dump con `strings` si individua tra le variabili d'ambiente del processo il token dell'agente, da usare come password per l'accesso SSH al livello successivo. Il valore letterale non viene riportato qui: `<REDACTED_FLAG>`. Il livello ha insegnato la tecnica di analisi post-mortem di un core dump per il recupero di segreti rimasti in chiaro in memoria di processo.

## Nota di pubblicazione

Questo writeup è la versione pubblica (GitHub) delle note personali sul livello Ghost 9 di BreachLab. In conformità alla dottrina BreachLab (Writeups · Creators), il documento insegna il metodo — estrazione ed analisi di stringhe da un core dump con `strings` per individuare segreti in memoria — ma non riporta il valore letterale del token/password, che il solutore deve ottenere in autonomia ripetendo l'analisi sul proprio ambiente.

## Crediti

Livello svolto su BreachLab (breachlab.org), Ghost Track. Credit a BreachLab per la piattaforma e il design del livello.
