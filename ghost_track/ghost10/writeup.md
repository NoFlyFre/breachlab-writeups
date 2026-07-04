# Ghost Track - Ghost 10

[← Torna all'indice](../../README.md)

## Sommario

- Track: Ghost Track
- Livello: Ghost 10 ("Odd Token Out")
- Fonte appunti: `ghost_track/ghost10/notes.md`

## Obiettivo

Il livello fornisce un file di log (`session-tokens.log`) generato da due collector che scrivono ogni token di sessione due volte. A causa di un'interruzione (outage), uno dei collector ha registrato un solo token in modo anomalo: quel token compare **una sola volta** nel file, mentre tutti gli altri compaiono in coppia. L'obiettivo è identificare quel token univoco senza analisi visiva riga per riga, e usarlo come credenziale per il livello successivo.

## Ricognizione

Il file `session-tokens.log` contiene diverse centinaia di righe, ciascuna con un token alfanumerico di 14 caratteri. Il volume di righe è troppo elevato per un controllo manuale affidabile: serve uno strumento che deduplichi e isoli le occorrenze singole.

## Tecnica

La tecnica sfruttata è l'uso combinato di `sort` e `uniq` per l'analisi di frequenza su un dataset testuale:

- `sort` ordina alfabeticamente le righe del file, portando automaticamente vicine tutte le occorrenze duplicate dello stesso token — requisito necessario perché `uniq` funzioni correttamente, dato che `uniq` opera solo su righe adiacenti.
- `uniq -u` (flag "unique") stampa esclusivamente le righe che compaiono **una sola volta** nell'input, scartando sia i duplicati sia le righe ripetute. Questo isola in un solo comando l'elemento anomalo tra centinaia di righe, senza bisogno di contare manualmente le occorrenze.

Il comando `sort file | uniq -u` è lo strumento esatto per il problema "trova l'elemento dispari" in un set dove tutto il resto è duplicato esattamente due volte. È un pattern generale, applicabile a qualsiasi log/dataset in cui bisogna trovare una voce che rompe uno schema di duplicazione atteso.

## Sfruttamento

1. Ispezione del file di log fornito nella home del livello:

```bash
cat session-tokens.log
```

Il file contiene centinaia di token, ciascuno atteso in duplice copia salvo uno.

2. Verifica preliminare con semplice deduplicazione (`sort | uniq`, senza `-u`) per farsi un'idea della dimensione del set unico rispetto al totale delle righe — passaggio di controllo, non risolutivo da solo.

3. Estrazione dell'elemento che compare una sola volta, con `sort` per garantire l'adiacenza delle righe uguali e `uniq -u` per isolare le righe non duplicate:

```bash
sort session-tokens.log | uniq -u
<REDACTED>
```

L'unico output è il token anomalo, riconoscibile perché segue un pattern diverso dagli altri (generato manualmente durante l'outage, non dal collector automatico).

## Risultato

Il comando `sort | uniq -u` isola correttamente l'unica riga non duplicata nel dataset, che corrisponde alla credenziale richiesta per procedere al livello successivo. Il valore letterale non è incluso in questo writeup.

## Nota di pubblicazione

Questa è la versione pubblicabile su GitHub secondo la dottrina BreachLab: spiega per intero il metodo e il ragionamento (uso di `sort`/`uniq` per l'analisi di frequenza), ma non riporta la password/token risolutivo, in modo da preservare la sfida per gli altri operatori.

---

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Ghost Track — piattaforma di training autorizzato per pentest/CTF. Rispetta le Standing Orders: nessuno spoiler di password o flag letterali.
