# Mirage Track - Mirage 6

## Sommario

- Track: Mirage Track
- Livello: Mirage 6
- Fonte appunti: `mirage_track/mirage6/notes.md`

## Obiettivo

L'applicazione "Parcelo" (un portale di gestione spedizioni per operatori) identifica l'operatore loggato tramite un cookie applicativo che contiene un identificativo numerico. L'obiettivo è capire se questo identificativo può essere manipolato per accedere ai dati di altri operatori (IDOR — Insecure Direct Object Reference) e, tramite quello, raggiungere un pannello con la credenziale per l'ambiente successivo.

## Nota di pubblicazione

Questa versione è pensata per GitHub e segue la dottrina BreachLab: spiega per intero la tecnica di enumerazione IDOR, ma omette credenziali, cookie di sessione e la chiave finale ottenuta.

## Ricognizione

La pagina principale mostra le spedizioni assegnate all'operatore corrente. Ispezionando la richiesta HTTP si nota un cookie applicativo con un identificativo numerico dell'operatore, passato lato client senza alcuna firma o token che leghi quel valore all'utente autenticato (l'unica altra credenziale è l'header `Authorization: Basic`, che autentica l'accesso all'ambiente, non l'identità dell'operatore specifico).

## Tecnica

Poiché l'identificativo dell'operatore è un valore numerico sequenziale interamente controllato dal client, e nessun controllo sembra legarlo alla sessione autenticata, è un candidato naturale per un IDOR: sostituendo il numero si potrebbe accedere ai dati di altri operatori. Per verificarlo sistematicamente è stato scritto uno script che itera un intervallo di valori (di default 0-100) mantenendo invariati gli altri header di autenticazione/sessione, confrontando la dimensione della risposta con quella "vuota" tipica per isolare rapidamente gli operatori con contenuto diverso dal default, senza dover ispezionare manualmente ogni risposta.

Questa è un'enumerazione mirata di un difetto di controllo degli accessi (IDOR) sul target di training stesso — non un tentativo di indovinare password, flag o accesso SSH, che sono le uniche categorie escluse dalla regola "no brute force" della dottrina BreachLab.

Uno degli operatori enumerati espone, nella colonna "Notes" di una spedizione, un appunto operativo interno lasciato per errore in produzione: un controllo di ruolo mancante su un endpoint di amministrazione, accessibile quindi da qualunque operatore autenticato, non solo dagli admin.

## Sfruttamento

1. Osservazione della richiesta autenticata di base, con il cookie dell'operatore identificato dal proprio numero.

2. Scrittura di uno script di enumerazione che ripete la stessa richiesta variando solo l'identificativo dell'operatore nel cookie, confrontando la dimensione della risposta con la dimensione "vuota" nota per individuare rapidamente operatori con contenuto anomalo:

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

3. Esecuzione dello script sull'intervallo di default, individuazione di un operatore con risposta anomala (dimensione diversa dal "vuoto").

4. Ispezione della pagina di quell'operatore, che mostra una spedizione con una nota interna anomala:

```text
Internal escalation: role check absent on /admin/console — any authenticated operator can invoke. Authz patch pending ops review.
```

5. Accesso diretto all'endpoint di amministrazione indicato dalla nota (mantenendo la stessa sessione autenticata come operatore qualsiasi), che espone un pannello "Admin console" con overview operativa e un pannello con le credenziali per l'ambiente successivo (valori omessi in questa versione pubblica).

## Risultato

Sfruttato un IDOR sul cookie applicativo dell'operatore per enumerare gli account e scoprire, tramite una nota lasciata in un record di un altro operatore, un controllo di autorizzazione mancante sull'endpoint di amministrazione (nessun controllo di ruolo, accessibile da qualunque operatore autenticato). Ottenuta la credenziale HTTP Basic per l'ambiente successivo della catena Mirage. Valori letterali omessi in questa versione pubblica.

## Crediti

Lab: BreachLab. Pubblicare sempre con credito al progetto e senza spoiler risolutivi.
