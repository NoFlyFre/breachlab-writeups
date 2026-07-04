# Mirage Track - Mirage 4

## Sommario

- **Track:** Mirage
- **Livello:** 4 (Nimbus AI — "Build smarter, ship faster")
- **Fonte appunti:** `mirage_track/mirage4/note.md`
- **Variante:** censored

## Obiettivo

Il livello espone una landing page marketing dell'applicazione fittizia "Nimbus AI". L'obiettivo, come nei livelli precedenti della catena Mirage, è muoversi dalla superficie pubblica dell'applicazione fino a trovare un pannello interno che espone le credenziali per l'ambiente successivo.

## Ricognizione

La homepage è una landing page statica con due CTA: "Start for free" e "Read the docs". Seguendo il link alla documentazione si arriva a `/docs`, che però mostra solo un placeholder ("Documentation is on the way"), senza contenuto utile.

Con la documentazione a vuoto, il passo successivo è consultare i file standard di discovery lato server: `robots.txt` e la sitemap XML referenziata al suo interno.

## Tecnica

La tecnica sfruttata è **information disclosure tramite robots.txt e sitemap.xml**. Il file `robots.txt`, pensato per dire ai crawler quali percorsi *non* indicizzare, qui rivela involontariamente l'esistenza di un percorso amministrativo che non era linkato da nessuna parte nell'interfaccia pubblica. La sitemap, referenziata dallo stesso robots.txt, conferma ed elenca esplicitamente l'URL completo della pagina interna, rendendo triviale raggiungerla anche se non era mai stata esposta via link cliccabile. Una volta raggiunta, la pagina di stato interno espone in chiaro (dietro un pulsante "Reveal" lato client, quindi senza vera protezione server-side) le credenziali HTTP Basic per l'ambiente di produzione successivo nella catena di deployment.

## Sfruttamento

1. Analisi della homepage e dei link pubblici (`/`, `/docs`) — nessun contenuto utile oltre al placeholder di documentazione.

2. Richiesta di `robots.txt`, che rivela un percorso escluso esplicitamente dall'indicizzazione e la presenza di una sitemap:

```text
User-agent: *
Disallow: /
Allow: /$
Allow: /pricing
Allow: /docs
# internal tooling — do not index
Disallow: /internal/

Sitemap: /sitemap.xml
```

3. Consultazione di `sitemap.xml`, che elenca esplicitamente l'URL completo della pagina interna nascosta, non collegata da nessun link visibile nell'interfaccia pubblica:

```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>http://mirage-l4.breachlab.org/</loc></url>
<url><loc>http://mirage-l4.breachlab.org/pricing</loc></url>
<url><loc>http://mirage-l4.breachlab.org/docs</loc></url>
<url><loc>http://mirage-l4.breachlab.org/internal/status</loc></url>
</urlset>
```

4. Richiesta diretta del percorso interno indicato dalla sitemap: la pagina non richiede autenticazione e mostra una dashboard operativa interna con metadati di build, stato dei worker e, soprattutto, un pannello "Environments" con le credenziali HTTP Basic per l'ambiente successivo nella catena, protette solo da un pulsante "Reveal" lato client — il valore è già presente nell'HTML in un attributo `data-secret`, semplicemente nascosto via CSS/JS finché non si preme il pulsante (nessuna vera protezione, il segreto è nel markup fin dal caricamento della pagina):

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

Attraverso `robots.txt` → `sitemap.xml` → endpoint interno non autenticato è stata individuata una dashboard amministrativa che espone la chiave HTTP Basic dell'ambiente successivo nella catena Mirage: `<REDACTED>`.

## Nota di pubblicazione

Questa è la versione destinata alla pubblicazione su GitHub, in linea con la dottrina BreachLab (Writeups · Creators): il metodo — discovery via `robots.txt`/`sitemap.xml`, individuazione di un endpoint amministrativo non collegato pubblicamente, ed esfiltrazione di un secret esposto lato client dietro un semplice toggle "Reveal" — è spiegato per intero; il valore letterale della chiave d'accesso è stato rimosso per non fornire uno spoiler diretto ad altri operatori.

## Crediti

Livello e ambiente forniti da [BreachLab](https://breachlab.org) — Mirage Track.
