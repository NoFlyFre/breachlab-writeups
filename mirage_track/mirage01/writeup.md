```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   mirage track · phile 0x01 · "the wire"
 ========================================================================

   target ..: mirage-01  "The Wire"
   class ...: web · hidden endpoint · forged HTTP request
   tools ...: devtools · fetch()
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> una pagina dove niente è cliccabile davvero. il badge di stato resta
> grigio perché il browser non sa parlare all'endpoint interno. glielo
> insegniamo noi, dalla console.

## ----[ 0x00 · intel ]----

Landing page statica ("Nimbus AI"): nessun elemento visibile è davvero
interattivo, il CTA punta a un link vuoto. Obiettivo: trovare superfici di
attacco non evidenti — una risorsa JavaScript e un endpoint API interno —
per accedere al livello Mirage successivo.

## ----[ 0x01 · recon ]----

La pagina ha un widget di stato ("systems operational") alimentato da uno
script esterno caricato in modo differito. Nel sorgente dello script ci
sono commenti degli sviluppatori che descrivono, senza volerlo,
l'endpoint interno che il widget interroga: accetta solo POST e richiede
un header custom di service-mesh che un browser non può impostare da solo
su una GET. Per questo, sulla pagina pubblica, il badge resta sempre
grigio.

## ----[ 0x02 · il difetto ]----

Analisi del codice client-side per scoprire endpoint e comportamenti
"interni" che gli sviluppatori credevano protetti dalla sola assenza di un
link (security through obscurity). Noto l'endpoint, si forgiano richieste
HTTP a mano dalla console (`fetch`), cambiando metodo e header rispetto al
widget, per soddisfare i controlli server letti negli errori progressivi:
405 → 403 → 200. Enumerazione guidata dagli errori: ogni risposta dice
cosa mancava nella precedente.

## ----[ 0x03 · exploit ]----

1. Sorgente HTML → riferimento allo script di stato come risorsa statica.

2. Lettura dello script: i commenti espongono l'endpoint dell'health
   probe interno e i vincoli su metodo/header.

3. Prima chiamata con GET semplice (default del browser) → errore di
   metodo (405, verbo non supportato).

4. Ricostruzione come `fetch` POST dalla console DevTools → fallisce
   ancora per l'header di marcatura del service-mesh mancante (403, header
   indicato esplicitamente nell'errore).

5. Aggiunta manuale dell'header alla POST e reinvio → accettata: il server
   risponde "ok" e restituisce, nel campo dell'ambiente successivo, URL,
   utente e chiave per il livello Mirage dopo.

## ----[ 0x04 · loot ]----

Con metodo e header corretti l'endpoint interno risponde con un JSON che
include le credenziali del livello dopo e un blocco "observed activity"
che riepiloga i tentativi falliti — segno che l'infra del livello traccia
il solutore durante la recon. Valori fuori dal writeup:
`<REDACTED_SECRET>`. Lezione: leggi il JS client-side, leggi gli errori
HTTP, e costruisci la richiesta che il server vuole.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · mirage track
```
