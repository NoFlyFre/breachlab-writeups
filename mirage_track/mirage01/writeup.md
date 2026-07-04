# Mirage Track - Mirage 1

[← Torna all'indice](../../README.md)

## Sommario

- Track: Mirage
- Livello: Mirage 1 ("The Wire")
- Fonte appunti: `mirage_track/mirage01/notes.md`

## Obiettivo

Il livello presenta una landing page statica ("Nimbus AI") in cui nessun elemento visibile è realmente interattivo: il solo bottone CTA punta a un link vuoto. L'obiettivo, ricostruibile dal design del livello, è individuare superfici di attacco non evidenti nell'interfaccia utente — in questo caso una risorsa JavaScript e un endpoint API interno — per ottenere l'accesso al livello Mirage successivo.

## Ricognizione

La pagina HTML mostra un widget di stato ("systems operational") alimentato da uno script esterno, caricato in modo differito. Analizzando il sorgente di questo script emergono commenti degli sviluppatori che descrivono, involontariamente, i dettagli implementativi dell'endpoint interno che il widget interroga. I commenti rivelano due informazioni chiave: che l'endpoint accetta solo richieste POST, e che richiede un header custom di service-mesh che un browser non può impostare autonomamente su una richiesta GET standard — motivo per cui nella pagina pubblica il badge di stato resta sempre grigio.

## Tecnica

La tecnica sfruttata è l'analisi del codice client-side (JavaScript servito al browser) per scoprire endpoint e comportamenti "interni" che gli sviluppatori consideravano protetti dalla sola assenza di un link visibile ("security through obscurity"). Una volta noto l'endpoint, la tecnica prosegue con la forgiatura manuale di richieste HTTP dalla console del browser (tramite `fetch`), modificando metodo HTTP e header rispetto a quanto fa normalmente il widget, per soddisfare i controlli lato server osservati nei messaggi di errore progressivi (405 → 403 → 200). Questo è un classico esempio di enumerazione guidata dagli errori: ogni risposta del server indica esplicitamente cosa manca nella richiesta precedente.

## Sfruttamento

1. Ispezione del sorgente HTML della pagina principale, che rivela il riferimento a uno script di stato caricato come risorsa statica.

2. Lettura del contenuto dello script, che espone l'endpoint dell'health probe interno e i vincoli sul metodo/header richiesti, tramite i commenti lasciati dagli sviluppatori nel codice.

3. Prima chiamata diretta all'endpoint con una GET semplice (comportamento di default del browser), che restituisce un errore che indica il metodo sbagliato (405, verbo non supportato).

4. Ricostruzione della richiesta come `fetch` POST dalla console DevTools del browser, che però fallisce ancora per mancanza dell'header di marcatura interna del service-mesh (403 Forbidden, header mancante indicato esplicitamente nel messaggio di errore).

5. Aggiunta manuale dell'header richiesto alla richiesta POST e reinvio dalla console. Questa volta la richiesta viene accettata: il server risponde con stato "ok" e restituisce, dentro un campo dedicato all'ambiente successivo, l'URL, l'utente e la chiave di accesso per il livello Mirage successivo.

## Risultato

L'endpoint interno, una volta interrogato con il metodo e l'header corretti, risponde con un JSON che include le credenziali per il livello successivo e un blocco di "observed activity" che riepiloga in modo trasparente i tentativi falliti effettuati in precedenza — segno che l'infrastruttura del livello traccia il comportamento del solutore durante la ricognizione. I valori letterali (credenziali, chiavi, header di autorizzazione) non vengono riportati qui: `<REDACTED_SECRET>`. Il livello ha insegnato l'analisi del codice client-side per scoprire endpoint nascosti e la costruzione manuale di richieste HTTP con header custom.

## Nota di pubblicazione

Questo writeup è la versione pubblica (GitHub) delle note personali sul livello Mirage 1 di BreachLab. In conformità alla dottrina BreachLab (Writeups · Creators), il documento insegna il metodo — analisi del JavaScript client-side, lettura dei messaggi di errore HTTP per capire cosa manca in una richiesta, e forgiatura manuale di richieste con header custom — ma non riporta credenziali, chiavi di accesso o header di autorizzazione osservati durante la risoluzione, che il solutore deve ottenere in autonomia ripetendo l'analisi.

---

## Crediti

Livello svolto su BreachLab (breachlab.org), Mirage Track. Credit a BreachLab per la piattaforma e il design del livello.
