# Mirage Track - Mirage 5

[← Torna all'indice](../../README.md)

## Sommario

- Track: Mirage Track
- Livello: Mirage 5
- Fonte appunti: `mirage_track/mirage5/notes.md`

## Obiettivo

L'applicazione web "Trayl" (una dashboard di habit-tracking) espone una sezione "Workspace" con una voce di menu "Admin" marcata come ristretta (icona lucchetto). L'obiettivo è ottenere l'accesso a quell'area riservata per recuperare la credenziale dell'ambiente successivo della catena Mirage.

## Nota di pubblicazione

Questa versione è pensata per GitHub e segue la dottrina BreachLab: spiega il metodo per intero, ma rimuove credenziali, token di sessione e qualunque valore che permetterebbe di saltare il ragionamento o di riutilizzare un accesso non proprio.

## Ricognizione

La dashboard principale (`/`) è raggiungibile senza barriere e mostra un utente demo con piano "Member". L'unico elemento interattivo che punta fuori dalla home è un link verso un'area amministrativa nella sidebar, esplicitamente marcato come riservato agli admin del workspace.

Visitando direttamente quell'area da utente member si ottiene una pagina "Access restricted" generica, senza ulteriori indizi lato HTML. Un controllo di `robots.txt` non produce nulla di operativamente utile.

Il vero indizio emerge ispezionando la richiesta HTTP stessa verso l'area admin (via "copy as curl" dagli strumenti di sviluppo): sono presenti un header `authorization: Basic <base64>` e un cookie applicativo di sessione, anch'esso Base64, oltre a un cookie di clearance del CDN e a un identificativo di sessione opaco.

## Tecnica

Decodificando l'header Basic Auth si ottiene una coppia `utente:password` in cui l'username corrisponde al nome dell'ambiente corrente — la credenziale già in uso, non quella del livello successivo. Un primo tentativo di privilege escalation ovvio, sostituire l'username con `admin` mantenendo la stessa password e ricodificare in Base64, non funziona: l'header Basic Auth autentica probabilmente solo l'accesso all'host/ambiente a livello di infrastruttura, non il ruolo applicativo.

La vera superficie di attacco è il cookie di sessione applicativo: decodificato da Base64 rivela un oggetto JSON in chiaro, **non firmato** (nessun JWT, nessun HMAC):

```json
{"uid": "<REDACTED>", "role": "member"}
```

Poiché il token non ha integrità verificata, è sufficiente modificare il campo `role` da `"member"` ad `"admin"`, ricodificare in Base64, e sostituire il cookie nel browser per essere trattati come amministratori dall'applicazione — un classico caso di privilege escalation per manomissione di un token di sessione non protetto crittograficamente.

Un tentativo di replicare la richiesta modificata tramite `fetch()` dalla console del browser, impostando manualmente l'header `Cookie`, non ha funzionato: i browser moderni bloccano la scrittura diretta dell'header `Cookie` da JavaScript per motivi di sicurezza (è un "forbidden header name"). La soluzione corretta è stata modificare il cookie reale del browser tramite gli strumenti di sviluppo (tab Application/Storage) e poi semplicemente ricaricare la pagina, lasciando che sia il browser a inviare il cookie modificato in una normale navigazione.

## Sfruttamento

1. Decodifica dell'header Basic Auth osservato nella richiesta (Base64 → `utente:password`); tentativo di sostituire l'utente con `admin` mantenendo la stessa password: non funziona, l'header Basic Auth non controlla il ruolo applicativo.

2. Decodifica del cookie di sessione applicativo, che rivela un JSON in chiaro con un campo `role`.

3. Manomissione del campo `role` (`member` → `admin`) e ricodifica in Base64 del JSON risultante.

4. Primo tentativo, via `fetch()` dalla console con header `cookie` impostato manualmente nel payload della richiesta: fallisce silenziosamente, perché il browser ignora/blocca la scrittura diretta dell'header `Cookie` da script.

5. Sostituzione diretta del cookie di sessione nel browser (DevTools → Application → Cookies) col valore ricodificato con `role: admin`, seguita da un semplice reload della pagina dell'area admin: questa volta la richiesta va a buon fine.

6. La pagina admin restituita mostra un pannello con le credenziali per l'ambiente successivo (HTTP Basic: utente e chiave, valori non riportati in questa versione pubblica).

## Risultato

Sfruttata la mancanza di integrità del cookie di sessione applicativo (Base64 di un JSON in chiaro, senza firma) per elevare il proprio ruolo da `member` ad `admin` e accedere al pannello admin. Ottenuta la credenziale HTTP Basic per l'ambiente successivo della catena Mirage. Valori letterali (credenziali, cookie) omessi in questa versione pubblica.

---

## Crediti

Lab: BreachLab. Pubblicare sempre con credito al progetto e senza spoiler risolutivi.
