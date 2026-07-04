# Phantom Track - Phantom 11

## Sommario

- Track: Phantom Track
- Livello: Phantom 11 ("Token Hunter")
- Fonte appunti: `phantom_track/phantom11/notes.md`

## Obiettivo

La missione chiede di cacciare token e credenziali moderne oltre alle semplici password: JWT, API key, credenziali cloud, service account token. La macchina si collega a servizi cloud e API interne; bisogna trovare ogni token possibile, decodificare quello che si può, e uno di questi token è il flag del livello.

## Ricognizione

Nella home dell'operatore è presente un repository git con permessi leggibili dall'utente. Il repository non è "pulito": ci sono file di stato residui di un merge/revert interrotto (file come `AUTO_MERGE`, `MERGE_MSG`, `REVERT_HEAD`, `COMMIT_EDITMSG`), segno che sono state eseguite operazioni git recenti (revert di un commit) lasciando tracce nella working area, oltre ovviamente a tutta la cronologia negli oggetti e nei riferimenti del repository.

Ispezionando i file di stato si scopre che è in corso (o appena avvenuto) il revert di un commit di configurazione iniziale, con un conflitto segnalato proprio su un file di variabili d'ambiente — un forte indizio che quel file, in una versione precedente della storia, conteneva segreti.

## Tecnica

La tecnica è "git history archaeology": anche quando un commit successivo rimuove o oscura un segreto da un file, il valore originale resta comunque recuperabile nella cronologia del repository, perché git conserva ogni versione di ogni file come oggetto immutabile finché non viene fatto un garbage collection aggressivo o una riscrittura della storia. Con `git log` si enumerano i commit; con `git show <hash>` si può visualizzare il diff introdotto da un commit specifico, inclusi i diff che *rimuovono* segreti — che mostrano sia il valore vecchio (rimosso, prefisso `-`) sia quello nuovo (prefisso `+`).

In questo caso il commit in testa al branch (con messaggio relativo alla rimozione di segreti) mostra proprio un diff sul file di variabili d'ambiente che sostituisce dei valori reali con placeholder — ma la riga con il prefisso `-` nel diff contiene ancora il valore originale in chiaro, perché è ciò che c'era *prima* della rimozione.

## Sfruttamento

1. Lettura del brief della missione per capire l'obiettivo:

```bash
cat BRIEFING
```

2. Ingresso nella directory `.git` del repository presente nella home ed enumerazione dei file di stato:

```bash
cd .git
ll
```

Si notano file di stato di operazioni git recenti oltre alla struttura standard del repository.

3. Lettura rapida dei file di stato per capire cosa fosse in corso:

```bash
cat *
```

Emerge che è stato fatto un revert di un commit di configurazione, con un conflitto segnalato su un file sensibile.

4. Enumerazione della cronologia dei commit:

```bash
git log
```

Si trovano due commit: uno di configurazione iniziale e uno più recente relativo alla rimozione di segreti, in testa al branch.

5. Visualizzazione del diff introdotto dal commit più recente per capire cosa è stato "rimosso":

```bash
git show
```

Il diff mostra chiaramente i valori originali (righe `-`) prima che venissero sostituiti con placeholder (righe `+`):

```text
diff --git a/.env b/.env
index 1db2a85..c935363 100644
--- a/.env
+++ b/.env
@@ -1,2 +1,2 @@
-APP_SECRET=<REDACTED_FLAG>
-DB_URL=<REDACTED>
+APP_SECRET=REDACTED
+DB_URL=REDACTED
```

## Risultato

La cronologia git ha rivelato, nel diff del commit di "pulizia", il valore originale del segreto applicativo che rappresenta il token/flag del livello, oltre a una connection string di database contenente credenziali (entrambi i valori sono stati omessi in questa versione pubblica). L'esercizio dimostra concretamente quanto sia pericoloso committare credenziali anche se "rimosse" in un commit successivo: la cronologia le conserva comunque.

## Nota di pubblicazione

Questa è la versione pubblicabile su GitHub secondo la dottrina BreachLab: spiega per intero il metodo (ispezione della cronologia git con `git log`/`git show` per recuperare segreti da commit che li "rimuovono" senza riscrivere la storia) ma omette i valori reali dei segreti recuperati, per non fornire una scorciatoia a chi non ha ancora risolto il livello.

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Phantom Track. Writeup pubblicato nel rispetto della dottrina "no spoilers" della piattaforma.
