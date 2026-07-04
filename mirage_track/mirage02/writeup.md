```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   mirage track · phile 0x02 · "peel the encoding"
 ========================================================================

   target ..: mirage-02  "Peel the Encoding"
   class ...: web · layered encoding · API contract
   tools ...: devtools · fetch() · base64 · hex
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> un "codice di verifica" avvolto due volte — base64 sopra hex — e una
> API che accetta solo JSON. sbucci gli strati, rispetti il contratto, e
> l'ambiente successivo si apre.

## ----[ 0x00 · intel ]----

"Nimbus AI — verify your workspace": la pagina mostra un codice di
verifica e dice che l'onboarding lo decodifica e sblocca da solo.
Obiettivo: completare a mano lo sblocco (endpoint `/unlock`) per accedere
all'ambiente successivo.

## ----[ 0x01 · recon ]----

La pagina mostra un codice apparentemente casuale e un hint visibile:
"the code is wrapped for transport. Peel the layers…". Ma l'indizio vero è
in un commento sviluppatore nel sorgente HTML: il codice è "double-wrapped
for transport — base64 over a hex layer" (hex, poi base64), da decodificare
client-side, e l'endpoint `POST /unlock` accetta solo un body JSON
`{ token: decodedCode }`. Il commento nota anche che una form-urlencoded
viene rifiutata con 415: API JSON-only.

## ----[ 0x02 · il difetto ]----

Non è una falla applicativa in senso stretto, ma lo sfruttamento di info
di debug lasciate nel sorgente pubblico, che spiegano formato e
trasformazioni di un endpoint altrimenti opaco. Due parti:

1. **decodifica a strati** — il codice mostrato è base64; decodificato dà
   una stringa hex; da hex a testo si ottiene il token reale.
2. **rispetto del contratto API** — `/unlock` vuole `POST` con
   `Content-Type: application/json` e body `{"token": "<valore>"}`; altri
   formati → 415. Il primo tentativo col codice ancora codificato dà 401,
   con un errore che conferma la sequenza base64 → hex → plaintext.

## ----[ 0x03 · exploit ]----

1. Il commento nel sorgente HTML:

```html
<!--
  verify widget (v0.2). The "verification code" below is what the
  onboarding flow shows the user. TODO(jordan): the code is double-wrapped for
  transport — base64 over a hex layer — decode it client-side before posting.
  The unlock call is POST /unlock and the backend ONLY accepts a JSON body:
      fetch("/unlock", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: decodedCode })
      })
  NOTE(infra): a form post (application/x-www-form-urlencoded) is rejected
  with 415 — the API is JSON-only.
-->
```

2. Primo tentativo col codice ancora codificato, dalla console:

```javascript
fetch("/unlock", {method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: "<CODICE_ANCORA_CODIFICATO>" })
        })
```

```text
401 Unauthorized — token does not match. Peel the verification code (base64 -> hex -> plaintext) and submit the decoded value.
```

L'errore conferma i due strati da togliere.

3. Decodifica manuale: base64 → stringa hex → testo. Risultato: il token
   reale (valore fuori dal writeup).

4. Nuova `fetch` verso `/unlock` col token decodificato:

```javascript
fetch("/unlock", {method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: "<REDACTED>" })
        })
```

5. Risposta positiva, con i dettagli dell'ambiente successivo:

```json
{
  "status": "activated",
  "message": "Workspace verified. Open your console at /console.",
  "next_environment": {
    "url": "https://mirage-l3.breachlab.org",
    "user": "l3",
    "key": "<REDACTED>"
  }
}
```

C'è anche un blocco `observed_activity` che segnala i POST rifiutati: anche
i tentativi falliti vengono loggati.

## ----[ 0x04 · loot ]----

Token sbucciato (base64 → hex → plaintext) e inviato a `/unlock`: accesso
HTTP Basic per l'ambiente dopo (valori fuori dal writeup). Lezione: leggi
i commenti degli sviluppatori e rispetta alla lettera il contratto di una
API — metodo, header, formato del body — prima di dedurre dal 500 di
turno.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · mirage track
```
