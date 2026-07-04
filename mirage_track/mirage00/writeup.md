```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   mirage track · phile 0x00 · "nothing is secret"
 ========================================================================

   target ..: mirage-00  "Nothing Is Secret"
   class ...: web · client-side auth · secret in DOM
   tools ...: view-source · devtools
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> "nothing is secret", e il livello lo prende alla lettera: la chiave che
> "verifica" il login è scritta nello script, e il segreto per l'ambiente
> dopo è già nell'HTML sotto una fila di pallini.

## ----[ 0x00 · intel ]----

"Nimbus AI", landing page fittizia con un link "Open admin console".
Obiettivo: entrare nella console di amministrazione e recuperare da lì le
credenziali per l'ambiente successivo.

## ----[ 0x01 · recon ]----

Il sorgente HTML ha un link diretto `/admin`. Porta a un login ("Workspace
owner sign-in") che chiede una "workspace access key" via form POST. A
video niente di sospetto, ma la pagina include uno script inline che dà
feedback mentre digiti.

## ----[ 0x02 · il difetto ]----

Validazione client-side di un secret: lo `<script>` di login contiene una
costante usata solo per il feedback immediato ("Access key verified.")
mentre l'utente digita, prima ancora dell'invio. Siccome il controllo è
tutto nel browser, la chiave è in chiaro nel sorgente — basta view-source
o devtools, nessun bruteforce, nessuna interazione col server. Un valore
nato "per UX" che finisce per essere il segreto di auth.

Nella console dopo il login lo stesso schema si ripete: la chiave HTTP
Basic per l'ambiente successivo è nel DOM come attributo `data-secret` di
un `<code>`, nascosta solo esteticamente con dei bullet e "rivelata" via
JS al click di "Reveal".

## ----[ 0x03 · exploit ]----

1. Sorgente della home, link all'area riservata:

```html
<a class="cta" href="/admin">Open admin console</a>
```

2. A `/admin`, nel sorgente del login, lo script di validazione:

```javascript
var WORKSPACE_OWNER_KEY = "<REDACTED>";
var input = document.getElementById("access_key");
var feedback = document.querySelector('[data-role="key-feedback"]');
if (input) {
  input.addEventListener("input", function () {
    feedback.textContent = input.value === WORKSPACE_OWNER_KEY ? "Access key verified." : "";
  });
}
```

La chiave è in chiaro nel JS servito al browser: basta leggerla.

3. Si incolla la chiave nel campo "Workspace access key", si invia,
   accesso concesso.

4. In console, sotto "Environments", l'accesso HTTP Basic per l'ambiente
   dopo, dietro "Reveal" ma già in chiaro nel markup:

```html
<code class="secret" data-secret="<REDACTED>">••••••••••••••••</code>
<button type="button" class="reveal" data-reveal="">Reveal</button>
```

Non serve nemmeno cliccare: `data-secret` contiene già il valore.

## ----[ 0x04 · loot ]----

Sia la workspace access key sia la chiave HTTP Basic recuperate dal solo
sorgente HTML/JS, zero attacco attivo (valori fuori dal writeup).
Lezione: qualunque auth o "nascondimento" fatto solo client-side —
validazione JS, testo mascherato via CSS/bullet — non protegge niente: il
browser riceve tutto in chiaro.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · mirage track
```
