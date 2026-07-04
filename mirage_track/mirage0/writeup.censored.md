# Mirage Track - Mirage 0

## Sommario

- Track: Mirage Track
- Livello: Mirage 0
- Fonte appunti: `mirage_track/mirage0/note.md`
- Variante: censored

## Obiettivo

Il livello presenta "Nimbus AI", una landing page fittizia con un link "Open admin console". L'obiettivo è ottenere accesso alla console di amministrazione e recuperare da lì le credenziali per l'ambiente successivo del track.

## Ricognizione

Ispezionando il sorgente HTML della home page si nota un link diretto `/admin`. Seguendolo si arriva a una pagina di login ("Workspace owner sign-in") che richiede una "workspace access key" tramite un form POST verso `/admin`. Nulla di sospetto a prima vista nell'interfaccia, ma la pagina include uno script inline che gestisce il feedback visivo mentre l'utente digita.

## Tecnica

La vulnerabilità è una validazione client-side di un secret: la pagina di login include nel proprio `<script>` una costante usata solo per dare un feedback immediato ("Access key verified.") mentre l'utente digita, prima ancora dell'invio del form al server. Poiché questo controllo avviene interamente lato browser, la chiave è visibile in chiaro nel sorgente HTML della pagina — chiunque apra "view-source" o gli strumenti di sviluppo del browser può leggerla senza bisogno di alcun attacco, bruteforce o interazione col server. Si tratta di un classico errore di design: un valore che si voleva "solo per UX" finisce per essere anche il segreto di autenticazione reale.

Nella console di amministrazione raggiunta dopo il login, lo stesso pattern si ripete: la chiave di accesso HTTP Basic per l'ambiente successivo del deployment chain è presente nel DOM come attributo `data-secret` di un elemento `<code>`, semplicemente nascosta visivamente con dei bullet e rivelata via JavaScript al click del pulsante "Reveal" — di nuovo, il segreto è già presente in chiaro nell'HTML scaricato dal browser, la UI lo nasconde solo esteticamente.

## Sfruttamento

1. Ispezione del sorgente della home page e individuazione del link all'area riservata:

```html
<a class="cta" href="/admin">Open admin console</a>
```

2. Navigazione a `/admin`: la pagina richiede una "workspace access key" tramite un form. Ispezionando il sorgente della pagina di login si trova lo script di validazione client-side:

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

La chiave è scritta in chiaro nel codice JavaScript inviato al browser: basta leggere il sorgente della pagina per ottenerla, senza bisogno di eseguire nulla.

3. Inserimento della chiave trovata nel campo "Workspace access key" e invio del form: l'accesso alla console di amministrazione viene concesso.

4. Nella console, sotto "Environments", è presente l'accesso HTTP Basic per l'ambiente di produzione successivo. La chiave è nascosta dietro un pulsante "Reveal" ma è già presente in chiaro nell'HTML come attributo dati:

```html
<code class="secret" data-secret="<REDACTED>">••••••••••••••••</code>
<button type="button" class="reveal" data-reveal="">Reveal</button>
```

Non serve nemmeno cliccare il pulsante: l'attributo `data-secret` nel markup contiene già il valore in chiaro, leggibile da "view-source" o dagli strumenti di sviluppo senza eseguire lo script.

## Risultato

Sia la workspace access key sia la chiave HTTP Basic per l'ambiente successivo sono state recuperate direttamente dal sorgente HTML/JavaScript, senza alcun attacco attivo al server. I valori letterali non sono riportati qui secondo la dottrina BreachLab; il punto didattico è che qualunque controllo di autenticazione o "nascondimento" fatto solo lato client (validazione JS, testo mascherato via CSS/bullet) non protegge realmente un segreto: il browser riceve comunque tutto il contenuto in chiaro.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub secondo la dottrina BreachLab (Writeups · Creators): il metodo è spiegato per intero, ma le due chiavi/access key sono state sostituite con `<REDACTED>` per non fornire scorciatoie a chi non ha ancora risolto il livello.

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Mirage Track. Credito al progetto BreachLab per la piattaforma di training.
