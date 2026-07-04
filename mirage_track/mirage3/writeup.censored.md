# Mirage Track - Mirage 3

## Sommario

- **Track:** Mirage
- **Livello:** 3 (Nimbus AI — Dashboard)
- **Fonte appunti:** `mirage_track/mirage3/note.md`
- **Variante:** censored

## Obiettivo

Il livello espone una dashboard applicativa minimale ("Nimbus AI — Dashboard"). L'obiettivo è risalire, partendo dal solo bundle JavaScript servito al client, fino a un pannello operativo interno ("ops console") e da lì recuperare le credenziali per l'ambiente successivo della catena Mirage.

## Ricognizione

La pagina principale è statica e non offre superficie di attacco diretta: un `<h1>Dashboard</h1>` e uno stato "Workspace ready". Lo script referenziato è `/static/app.min.js`, un bundle minificato ma comunque leggibile lato client. Analizzando il bundle si trova un oggetto globale `window.__NIMBUS_ENV__` con URL e chiave anonima di un backend-as-a-service esposti direttamente nel codice front-end, prassi comune ma che qui nasconde più di quanto sembri.

Accanto al bundle minificato è presente anche il sorgente pre-minify `src/app.js`, con commenti lasciati dagli sviluppatori: uno di questi rivela l'esistenza di una console operativa nascosta all'indirizzo `/internal`, protetta da una "build key", e la build key stessa è presente in chiaro nel sorgente non minificato.

## Tecnica

La tecnica combina più passaggi in una catena:

1. **Fuga di configurazione client-side** — le chiavi del backend e la build key delle ops sono incorporate nel codice JavaScript servito al browser, quindi accessibili a chiunque ispezioni i sorgenti pubblici, senza bisogno di autenticazione.
2. **Decodifica di un JWT** — la chiave "anon" del backend non è una stringa opaca ma un JSON Web Token. Decodificandone header e payload (senza bisogno di conoscerne il secret, dato che JWT è firmato ma non cifrato) si conferma che è una chiave sintetica associata al progetto, utile per capire il contesto ma non direttamente sfruttabile per l'escalation successiva.
3. **Uso della build key per autenticarsi alla ops console** — il commento nel sorgente indica esplicitamente che `/internal` accetta la build key come credenziale di accesso (form "Sign in with your build key").
4. **Pivot a catena tramite ops console** — una volta dentro, la console non è il traguardo finale ma espone un pannello "Environments" che rivela URL, utente e chiave HTTP Basic per l'ambiente di produzione successivo nella catena di deployment, replicando lo stesso pattern "ogni livello nasconde le credenziali del successivo" osservato altrove in Mirage.

## Sfruttamento

1. Ispezione della dashboard e individuazione del bundle applicativo:

```html
<script src="/static/app.min.js" defer=""></script>
```

2. Lettura del bundle minificato: espone la configurazione del backend direttamente in `window.__NIMBUS_ENV__`, incluso un JWT come chiave anonima.

```javascript
window.__NIMBUS_ENV__ = {
    SUPABASE_URL: "https://qx7r2mwktnzvpld9hsea.supabase.co",
    SUPABASE_ANON_KEY: "<REDACTED>"
};
```

3. Recupero del sorgente pre-minify `src/app.js`, più leggibile e con commenti degli sviluppatori che rivelano sia l'esistenza della ops console sia la variabile che contiene la build key necessaria per accedervi:

```javascript
// src/app.js (original, pre-minify)
// TODO(marco): pull the build key from env before launch
// FIXME(infra): move BaaS keys server-side before the Supabase cutover
// ops console lives at /internal — sign in with the build key below
const OPS_BUILD_KEY = "<REDACTED>";
```

4. Decodifica del JWT usato come chiave anonima (header + payload), per confermarne la natura e il contesto (ruolo "anon", progetto sintetico):

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

```json
{
  "role": "anon",
  "ref": "qx7r2mwktnzvpld9hsea",
  "synthetic": true
}
```

5. Accesso a `/internal`: la ops console richiede un "build key" tramite un semplice form POST. Inserendo la build key trovata nel sorgente, l'accesso viene concesso.

6. All'interno della ops console, il pannello "Environments" espone URL, utente HTTP Basic e chiave di accesso per l'ambiente successivo, nascosta dietro un pulsante "Reveal" puramente cosmetico — il valore è già presente nell'HTML in un attributo `data-secret`, quindi non è una vera protezione:

```html
<div class="env-row">
   <span class="env-k">Key</span>
   <span class="env-v">
     <code class="secret" data-secret="<REDACTED>">••••••••••••••••</code>
     <button type="button" class="reveal" data-reveal="">Reveal</button>
   </span>
 </div>
```

## Risultato

Seguendo la catena bundle minificato → sorgente pre-minify → build key → ops console `/internal` → pannello Environments, è stata ottenuta la credenziale HTTP Basic per l'ambiente successivo della catena Mirage: `<REDACTED>`.

## Nota di pubblicazione

Questa è la versione destinata alla pubblicazione su GitHub, in linea con la dottrina BreachLab (Writeups · Creators): l'intera catena di ragionamento — analisi del bundle minificato, recupero del sorgente non minificato, decodifica del JWT, uso della build key per autenticarsi alla ops console, e individuazione del pannello "Environments" come punto di leak delle credenziali per l'ambiente successivo — è spiegata per intero. Solo i valori letterali finali (JWT, build key, chiave HTTP Basic) sono stati rimossi per non fornire uno spoiler diretto ad altri operatori.

## Crediti

Livello e ambiente forniti da [BreachLab](https://breachlab.org) — Mirage Track.
