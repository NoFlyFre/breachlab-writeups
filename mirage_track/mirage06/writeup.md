```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   mirage track · phile 0x06 · "other people's objects"
 ========================================================================

   target ..: mirage-06  "Other People's Objects"
   class ...: web · IDOR · missing authz
   tools ...: curl · bash loop
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> l'operatore ti identifica con un numerino nel cookie. numerino
> sequenziale, controllato dal client, niente firma. lo si enumera, e in
> un record altrui c'è la nota che apre l'admin console.

## ----[ 0x00 · intel ]----

"Parcelo", portale di gestione spedizioni, identifica l'operatore loggato
con un cookie che contiene un id numerico. Obiettivo: capire se quell'id
si può manipolare per accedere ai dati di altri operatori (IDOR) e da lì
raggiungere il pannello con la credenziale dell'ambiente successivo.

## ----[ 0x01 · recon ]----

La home mostra le spedizioni dell'operatore corrente. Nella richiesta HTTP
c'è un cookie con un id numerico dell'operatore, passato client-side senza
firma né token che lo leghi all'utente autenticato (l'unica altra
credenziale è `Authorization: Basic`, che autentica l'ambiente, non
l'identità del singolo operatore).

## ----[ 0x02 · il difetto ]----

L'id operatore è numerico, sequenziale e interamente controllato dal
client, e niente lo lega alla sessione: candidato naturale a **IDOR**.
Cambiando il numero si accede ai dati altrui. Per verificarlo in modo
sistematico, uno script itera un intervallo (default 0-100) tenendo fissi
gli altri header, confrontando la dimensione della risposta con quella
"vuota" tipica per isolare in fretta gli operatori con contenuto diverso.

Enumerazione mirata di un difetto di access control sul target di training
— non un tentativo di indovinare password/flag/SSH, le uniche categorie
escluse dalla regola "no brute force" della dottrina.

Uno degli operatori enumerati espone, nella colonna "Notes" di una
spedizione, un appunto interno lasciato in produzione: un role check
mancante su un endpoint admin, quindi invocabile da qualunque operatore
autenticato.

## ----[ 0x03 · exploit ]----

1. Osservazione della richiesta autenticata di base, col cookie
   dell'operatore identificato dal numero.

2. Script di enumerazione che ripete la richiesta variando solo l'id
   nell'cookie, confrontando la dimensione della risposta col "vuoto":

```bash
BASE_URL="https://mirage-l6.breachlab.org/"
EMPTY_SIZE=2700
TOLERANCE=200

for n in $(seq "$MIN" "$MAX"); do
  op="op_$n"
  curl -s -o "$body_file" -w '%{http_code} %{size_download}' \
    -H "authorization: <REDACTED>" \
    -H "cookie: ${COOKIE_BASE}; parcelo_op=${op}" \
    "$BASE_URL"
  # confronto con EMPTY_SIZE +/- TOLERANCE, salva solo le risposte "diverse"
done
```

3. Esecuzione sull'intervallo di default → un operatore con risposta
   anomala (dimensione diversa dal vuoto).

4. La sua pagina mostra una spedizione con una nota interna:

```text
Internal escalation: role check absent on /admin/console — any authenticated operator can invoke. Authz patch pending ops review.
```

5. Accesso diretto a `/admin/console` con la stessa sessione da operatore
   qualsiasi: "Admin console" con overview operativa e le credenziali per
   l'ambiente dopo (valori omessi).

## ----[ 0x04 · loot ]----

IDOR sul cookie operatore per enumerare gli account, e in un record altrui
la nota che rivela un authz mancante su `/admin/console`: da lì la
credenziale HTTP Basic dell'ambiente successivo (valori omessi). Lezione:
un id lato client senza controllo lega niente — e le note "interne"
finiscono in produzione.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · mirage track
```
