```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   mirage track · phile 0x04 · "left in the open"
 ========================================================================

   target ..: mirage-04  "Left in the Open"
   class ...: web · info disclosure · robots + sitemap
   tools ...: curl · view-source
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> la pagina interna non è linkata da nessuna parte. peccato che
> `robots.txt` la elenchi per dire ai crawler di non indicizzarla, e la
> sitemap ti dia pure l'URL preciso.

## ----[ 0x00 · intel ]----

Landing marketing di "Nimbus AI". Come nei livelli precedenti, obiettivo:
partire dalla superficie pubblica e arrivare a un pannello interno che
espone le credenziali per l'ambiente successivo.

## ----[ 0x01 · recon ]----

Homepage statica con due CTA ("Start for free", "Read the docs"). Il link
docs porta a `/docs`, ma è solo un placeholder ("Documentation is on the
way"). Con la doc a vuoto, il passo successivo sono i file standard di
discovery lato server: `robots.txt` e la sitemap XML che referenzia.

## ----[ 0x02 · il difetto ]----

**Information disclosure via robots.txt e sitemap.xml.** `robots.txt`, che
dovrebbe dire ai crawler cosa *non* indicizzare, qui rivela un percorso
amministrativo non linkato da nessuna parte. La sitemap, referenziata
dallo stesso robots, ne elenca l'URL completo, rendendo banale
raggiungerlo. Arrivati lì, la pagina di stato interno espone in chiaro
(dietro il solito "Reveal" client-side) le credenziali HTTP Basic per
l'ambiente successivo.

## ----[ 0x03 · exploit ]----

1. Homepage e link pubblici (`/`, `/docs`) — solo il placeholder doc.

2. `robots.txt` rivela un percorso escluso e una sitemap:

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

3. `sitemap.xml` elenca l'URL completo della pagina interna, mai linkata:

```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>http://mirage-l4.breachlab.org/</loc></url>
<url><loc>http://mirage-l4.breachlab.org/pricing</loc></url>
<url><loc>http://mirage-l4.breachlab.org/docs</loc></url>
<url><loc>http://mirage-l4.breachlab.org/internal/status</loc></url>
</urlset>
```

4. Richiesta diretta al percorso interno: nessuna auth, dashboard
   operativa con build metadata, stato worker e un pannello
   "Environments" con la chiave HTTP Basic per l'ambiente dopo, dietro
   "Reveal" ma già nel markup come `data-secret`:

```html
<div class="env-row">
   <span class="env-k">Key</span>
   <span class="env-v">
     <code class="secret" data-secret="<REDACTED>">••••••••••••••••</code>
     <button type="button" class="reveal" data-reveal="">Reveal</button>
   </span>
</div>
```

## ----[ 0x04 · loot ]----

`robots.txt` → `sitemap.xml` → endpoint interno non autenticato → chiave
HTTP Basic per l'ambiente successivo (valore fuori dal writeup). Lezione:
`robots.txt` non nasconde niente, lo annuncia — e "Reveal" è markup, non
sicurezza.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · mirage track
```
