```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   mirage track · phile 0x03 · "source maps talk"
 ========================================================================

   target ..: mirage-03  "Source Maps Talk"
   class ...: web · client-side leak → ops console pivot
   tools ...: browser devtools · jwt decode · un occhio ai commenti
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> una dashboard che non fa niente. un `<h1>`, uno "Workspace ready", e
> un bundle javascript. il front-end è muto in superficie ma chiacchiera
> parecchio se lo leggi: chiavi, commenti degli sviluppatori, una console
> interna. si tira il filo finché non viene giù la catena.

## ----[ 0x00 · intel ]----

Il livello espone "Nimbus AI — Dashboard", minimale. L'obiettivo è
risalire dal solo bundle JavaScript servito al client fino a un pannello
operativo interno (`/internal`) e, da lì, alle credenziali per
l'ambiente successivo della catena Mirage.

## ----[ 0x01 · recon ]----

La pagina è statica: `<h1>Dashboard</h1>`, stato "Workspace ready",
zero superficie diretta. Lo script referenziato è `/static/app.min.js`,
minificato ma leggibile:

```html
<script src="/static/app.min.js" defer=""></script>
```

Dentro il bundle c'è un oggetto globale `window.__NIMBUS_ENV__` con URL
e chiave "anon" di un backend-as-a-service, incollati nel front-end:

```javascript
window.__NIMBUS_ENV__ = {
    SUPABASE_URL: "https://qx7r2mwktnzvpld9hsea.supabase.co",
    SUPABASE_ANON_KEY: "<REDACTED>"
};
```

Ma il vero regalo è accanto: il sorgente pre-minify `src/app.js`, coi
commenti lasciati dagli sviluppatori. Uno rivela una ops console
nascosta a `/internal`, protetta da una "build key" — che è lì sotto, in
chiaro:

```javascript
// src/app.js (original, pre-minify)
// TODO(marco): pull the build key from env before launch
// FIXME(infra): move BaaS keys server-side before the Supabase cutover
// ops console lives at /internal — sign in with the build key below
const OPS_BUILD_KEY = "<REDACTED>";
```

## ----[ 0x02 · la catena ]----

Non è un singolo bug, è una catena di sviste che si concatenano:

1. **config leak client-side** — chiavi del backend e build key delle
   ops sono nel JavaScript servito al browser, leggibili da chiunque,
   senza autenticazione.
2. **jwt in chiaro** — la chiave "anon" non è una stringa opaca ma un
   JWT. Decodificando header e payload (JWT è firmato, non cifrato) si
   conferma che è una chiave sintetica legata al progetto: utile per il
   contesto, non per l'escalation.
3. **build key = pass per le ops** — il commento dice esplicitamente che
   `/internal` accetta la build key come credenziale ("Sign in with your
   build key").
4. **pivot a catena** — dentro la ops console c'è un pannello
   "Environments" che espone URL, utente e chiave HTTP Basic
   dell'ambiente di produzione successivo. Stesso pattern di tutto
   Mirage: ogni livello nasconde le credenziali del prossimo.

## ----[ 0x03 · exploit ]----

Decodifica del JWT usato come anon key (header + payload), giusto per
capire con cosa si ha a che fare:

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

Poi `/internal`: un form POST che chiede la build key. Si incolla quella
trovata nel sorgente e si entra. Dentro, il pannello "Environments"
espone la credenziale per l'ambiente successivo dietro un bottone
"Reveal" puramente cosmetico — il valore è già nell'HTML, in un attributo
`data-secret`:

```html
<div class="env-row">
   <span class="env-k">Key</span>
   <span class="env-v">
     <code class="secret" data-secret="<REDACTED>">••••••••••••••••</code>
     <button type="button" class="reveal" data-reveal="">Reveal</button>
   </span>
 </div>
```

Il "Reveal" non protegge niente: è markup che nasconde solo agli occhi,
non al sorgente.

## ----[ 0x04 · loot ]----

Filo tirato per intero: bundle minificato → sorgente pre-minify → build
key → ops console `/internal` → pannello Environments → credenziale HTTP
Basic dell'ambiente successivo. I valori letterali (JWT, build key,
chiave finale) restano fuori. La morale: tutto ciò che finisce nel bundle
servito al client è pubblico, "Reveal" o no.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · mirage track
```
