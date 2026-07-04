# Phantom Track - Phantom 6

[← Torna all'indice](../../README.md)

## Sommario

- Track: Phantom
- Livello: Phantom 6
- Fonte appunti: `phantom_track/phantom6/notes.md`

## Obiettivo

Il brief ("Scheduled Sins") indica che sulla macchina gira, ogni minuto, qualcosa di schedulato, non eseguito da root. L'obiettivo è identificare cosa sia, chi lo esegue, e se è possibile modificarlo per ottenere la flag, di proprietà dell'utente che possiede il job schedulato. Il brief avverte anche di una particolarità dell'ambiente: `/tmp` è poli-istanziato per sessione SSH, quindi un cron job eseguito in un contesto diverso scriverà nel `/tmp` reale dell'host, non visibile dalla shell interattiva del solutore — un dettaglio operativo cruciale per scegliere dove scrivere l'output.

## Ricognizione

L'enumerazione dei job cron di sistema rivela diversi file di configurazione. Oltre a job legittimi di manutenzione, sono presenti job particolari commentati esplicitamente come "sweep" anti-leak, pensati dagli operatori della piattaforma per ripulire periodicamente file lasciati in giro dai solutori. Tra questi job compare la riga chiave: un job che, ogni minuto, esegue uno script di manutenzione come un utente diverso da root — coerentemente con l'indizio del brief.

## Tecnica

La tecnica sfruttata è l'abuso di un cron job di manutenzione eseguito da un utente diverso da quello del solutore, il cui script risulta scrivibile dall'utente corrente grazie a permessi eccessivamente permissivi (bit setuid attivo, gruppo del solutore con permesso di scrittura). Modificando il contenuto dello script, che viene rieseguito automaticamente dal cron ogni minuto con i privilegi del proprietario originale, è possibile far eseguire comandi arbitrari con quella identità — in questo caso, comandi che rendono leggibile la flag altrimenti protetta, invece di limitarsi al semplice cleanup di file temporanei che lo script svolgeva in origine.

## Sfruttamento

1. Lettura del brief e ricognizione dei job pianificati di sistema in `/etc/cron.d/`. Tra le regole presenti spicca un job eseguito ogni minuto da un utente specifico (non root), che richiama uno script di manutenzione.

2. Ispezione dello script eseguito dal cron job: nella sua versione originale si limita a cancellare file temporanei più vecchi di un giorno.

3. Verifica dei permessi dello script, che risulta scrivibile dal gruppo dell'utente del solutore e con bit setuid attivo — una configurazione dei permessi eccessivamente permissiva rispetto a quanto lo script dovrebbe richiedere.

4. Modifica esplorativa dello script per verificare che le modifiche vengano effettivamente rieseguite dal cron.

5. Modifica finale, mirata: aggiunta di un comando che rende leggibile la flag altrimenti protetta, sfruttando il fatto che lo script viene rieseguito periodicamente con i privilegi del proprietario originale del job.

6. Attesa del prossimo tick del cron (il brief stesso suggerisce pazienza) e verifica ripetuta dei permessi del file target, che passano da inaccessibili a leggibili una volta eseguito lo script modificato.

7. Lettura della flag, ora accessibile in sola lettura.

## Risultato

Modificando lo script di manutenzione, eseguito periodicamente dal cron job con i privilegi di un utente diverso grazie a permessi di scrittura troppo permissivi, è stato possibile far eseguire un comando con i privilegi del proprietario del job, rendendo leggibile la flag del livello. Il valore letterale non viene riportato qui: `<REDACTED_FLAG>`. Il livello ha insegnato l'analisi dei job cron di sistema alla ricerca di script eseguiti da un utente diverso ma scrivibili dal solutore — un classico vettore di privilege escalation orizzontale/verticale.

## Nota di pubblicazione

Questo writeup è la versione pubblica (GitHub) delle note personali sul livello Phantom 6 di BreachLab. In conformità alla dottrina BreachLab (Writeups · Creators), il documento insegna il metodo — enumerazione dei cron job di sistema, individuazione di script con permessi eccessivi, e sfruttamento della riesecuzione periodica per eseguire comandi con privilegi altrui — ma non riporta il valore letterale della flag, che il solutore deve ottenere in autonomia ripetendo l'analisi.

---

## Crediti

Livello svolto su BreachLab (breachlab.org), Phantom Track. Credit a BreachLab per la piattaforma e il design del livello.
