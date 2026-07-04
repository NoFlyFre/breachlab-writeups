# Mirage Track - Mirage 2

[← Torna all'indice](../../README.md)

## Sommario

- Track: Mirage Track
- Livello: Mirage 2 ("Peel the Encoding")
- Fonte appunti: `mirage_track/mirage02/notes.md`

## Obiettivo

Il livello presenta "Nimbus AI — verify your workspace", una pagina che mostra un "codice di verifica" e afferma che il flusso di onboarding lo decodifica e conferma automaticamente lo sblocco. L'obiettivo è completare manualmente questo sblocco (endpoint `/unlock`) per ottenere l'accesso all'ambiente successivo del track.

## Ricognizione

La pagina mostra un codice apparentemente casuale e un suggerimento nel testo visibile: "Stuck? The code is wrapped for transport. Peel the layers, then have the API verify the decoded token. (Engineers: see page source.)". Il vero indizio tecnico però è nel sorgente HTML, in un commento sviluppatore lasciato nel codice: spiega che il codice è "double-wrapped for transport — base64 over a hex layer" (cioè hex, poi il tutto codificato in base64), che va decodificato lato client prima dell'invio, e che l'endpoint `POST /unlock` accetta esclusivamente un body JSON con struttura `{ token: decodedCode }`. Il commento specifica anche che una richiesta form-urlencoded viene rifiutata con 415, perché l'API è JSON-only.

## Tecnica

Non è uno sfruttamento di una falla applicativa in senso stretto, ma lo sfruttamento di informazioni di debug/sviluppo lasciate nel sorgente pubblico (commento HTML) che spiegano esattamente formato e trasformazioni richieste da un endpoint altrimenti opaco. La tecnica si articola in due parti:

1. **Decodifica a strati**: il "codice di verifica" mostrato in pagina è una stringa base64 che, decodificata, produce a sua volta una stringa esadecimale; decodificando quest'ultima da hex a testo si ottiene il token reale in chiaro.
2. **Rispetto del contratto API**: l'endpoint `/unlock` richiede specificamente una richiesta `POST` con header `Content-Type: application/json` e body `{"token": "<valore>"}` — qualunque altro formato (es. form POST) viene respinto con HTTP 415. Il primo tentativo, inviando il codice ancora codificato, restituisce infatti 401 con un messaggio di errore che conferma esplicitamente la sequenza di decodifica richiesta (base64 → hex → plaintext), confermando l'ipotesi ricavata dal commento.

## Sfruttamento

1. Lettura del commento sviluppatore nel sorgente HTML della pagina, che rivela formato dell'endpoint e trasformazioni necessarie:

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

2. Primo tentativo, inviando il codice così com'è mostrato in pagina (ancora codificato), per verificare il comportamento dell'endpoint dalla console del browser:

```javascript
fetch("/unlock", {method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: "<CODICE_ANCORA_CODIFICATO>" })
        })
```

Risposta:

```text
401 Unauthorized — token does not match. Peel the verification code (base64 -> hex -> plaintext) and submit the decoded value.
```

Il messaggio d'errore conferma esplicitamente i due strati di codifica da rimuovere.

3. Decodifica manuale del codice: prima da base64 a stringa esadecimale, poi da esadecimale a testo semplice. Il risultato è il token reale (valore non riportato qui).

4. Nuova richiesta `fetch` verso `/unlock`, questa volta con il token decodificato:

```javascript
fetch("/unlock", {method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: "<REDACTED>" })
        })
```

5. Risposta positiva, con lo stato "activated" e i dettagli di accesso all'ambiente successivo:

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

La risposta include anche un blocco `observed_activity` che segnala i tentativi POST rifiutati registrati durante l'esplorazione — un promemoria che anche i tentativi falliti vengono loggati e possono alzare lo score di attività sospetta.

## Risultato

Token di sblocco decodificato correttamente (base64 → hex → plaintext) e inviato all'endpoint `/unlock`, ottenendo l'accesso HTTP Basic per l'ambiente successivo. Il valore letterale del token e della chiave non sono riportati qui secondo la dottrina BreachLab; il punto didattico è imparare a leggere i commenti degli sviluppatori nel sorgente e a rispettare rigorosamente il contratto di un'API (metodo, header, formato del body) prima di dedurne il comportamento da errori generici.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub secondo la dottrina BreachLab (Writeups · Creators): il metodo è spiegato per intero, ma il codice di verifica, il token decodificato e la chiave finale sono stati sostituiti con placeholder per non fornire scorciatoie a chi non ha ancora risolto il livello.

---

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Mirage Track. Credito al progetto BreachLab per la piattaforma di training.
