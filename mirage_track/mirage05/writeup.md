```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   mirage track · phile 0x05 · "trust the client"
 ========================================================================

   target ..: mirage-05  "Trust the Client"
   class ...: web · privesc · unsigned session cookie
   tools ...: devtools · base64
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> "trust the client" — errore. il cookie di sessione è un JSON in chiaro
> non firmato: `"role":"member"` → `"role":"admin"`, ricodifica, reload.
> benvenuto in area admin.

## ----[ 0x00 · intel ]----

"Trayl", dashboard di habit-tracking, ha una voce di menu "Admin" marcata
come ristretta (lucchetto). Obiettivo: entrare in quell'area per la
credenziale dell'ambiente successivo.

## ----[ 0x01 · recon ]----

La dashboard `/` è libera e mostra un utente demo "Member". L'unico link
che punta fuori è l'area admin nella sidebar, marcata come riservata.
Visitandola da member si ottiene un "Access restricted" generico, niente
indizi nell'HTML; `robots.txt` non aiuta.

L'indizio vero è nella richiesta HTTP stessa (via "copy as curl" dai
devtools): c'è un header `authorization: Basic <base64>`, un cookie di
sessione applicativo anch'esso Base64, un cookie di clearance del CDN e un
session id opaco.

## ----[ 0x02 · il difetto ]----

Decodificando il Basic Auth si ottiene `utente:password` in cui l'username
è il nome dell'ambiente corrente — la credenziale già in uso, non quella
del livello dopo. La privesc ovvia (username → `admin`, stessa password,
ricodifica) non funziona: il Basic Auth autentica l'accesso
all'host/ambiente a livello infra, non il ruolo applicativo.

La vera superficie è il cookie di sessione applicativo: decodificato da
Base64 è un JSON in chiaro, **non firmato** (niente JWT, niente HMAC):

```json
{"uid": "<REDACTED>", "role": "member"}
```

Nessuna integrità verificata → basta cambiare `role` da `"member"` a
`"admin"`, ricodificare in Base64 e sostituire il cookie per essere
trattati da admin. Privesc classica per manomissione di un token di
sessione non protetto.

Nota pratica: replicare la richiesta via `fetch()` impostando a mano
l'header `Cookie` non funziona — i browser bloccano la scrittura di
`Cookie` da JS ("forbidden header name"). Si modifica il cookie reale dai
devtools (Application/Storage) e si ricarica.

## ----[ 0x03 · exploit ]----

1. Decodifica del Basic Auth (Base64 → `utente:password`); tentativo
   `admin` + stessa password: non funziona, non controlla il ruolo.

2. Decodifica del cookie di sessione → JSON in chiaro con campo `role`.

3. Manomissione `role` (`member` → `admin`) e ricodifica Base64.

4. Primo tentativo via `fetch()` con header `cookie` nel payload:
   fallisce, il browser blocca la scrittura di `Cookie` da script.

5. Sostituzione del cookie nel browser (DevTools → Application → Cookies)
   col valore `role: admin`, poi reload dell'area admin: passa.

6. La pagina admin mostra le credenziali per l'ambiente dopo (HTTP Basic:
   utente e chiave, valori omessi).

## ----[ 0x04 · loot ]----

Sfruttata la mancanza di integrità del cookie di sessione (Base64 di un
JSON in chiaro, non firmato) per passare da `member` ad `admin` e prendere
la credenziale HTTP Basic dell'ambiente successivo (valori omessi).
Lezione: un token di sessione senza firma è un modulo che l'utente
compila da sé.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · mirage track
```
