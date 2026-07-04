# Ghost Track - Ghost 22

[← Torna all'indice](../../README.md)

## Sommario

- **Track:** Ghost Track
- **Livello:** Ghost 22 · CLASSIFIED ("Graduation")
- **Fonte appunti:** `ghost_track/ghost22/notes.md`

## Obiettivo

Livello finale del Ghost Track: un unico file "classificato" è stato spezzato in tre shard, ciascuno protetto con una tecnica diversa incontrata nei 22 livelli precedenti (dati nascosti in un blob binario, dati codificati per il trasporto, dati dietro un helper SUID). Bisogna recuperare tutti e tre gli shard e inviarli a un "gatekeeper" in ascolto su TCP `:31339`, nel formato esatto `SHARD1:<val>|SHARD2:<val>|SHARD3:<val>`.

## Ricognizione

Nella home sono presenti tre file rilevanti: `BRIEFING` (testo UTF-8 con le istruzioni), `relic.bin` (8215 byte, identificato da `file` come semplice `data`, cioè binario senza struttura riconoscibile) e `scroll.b64` (25 byte, testo ASCII). Il `BRIEFING` conferma la missione: tre shard, tre tecniche, un gatekeeper di rete che valida il formato combinato.

## Tecnica

Il livello è un riepilogo delle tecniche viste nel corso del Ghost Track, applicate in sequenza:

- **Shard 1 — "buried in a binary blob":** estrazione di stringhe leggibili da un file binario con `strings`, per isolare testo ASCII annegato in un blob altrimenti privo di struttura riconoscibile.
- **Shard 2 — "encoded for transport":** decodifica Base64 di un file di testo che contiene dati codificati per il trasporto, la stessa tecnica di codifica vista in altri livelli del track.
- **Shard 3 — "guarded by a SUID helper":** recupero tramite un binario con bit SUID impostato, tecnica di privilege escalation/accesso controllato tipica del track.

## Sfruttamento

1. Enumerazione della home e identificazione dei tre file rilevanti:

```bash
ll
total 76
...
-rw-r----- 1 ghost22 ghost22  343 Jun 22 13:41 BRIEFING
-rw-r----- 1 ghost22 ghost22 8215 Jun 22 13:41 relic.bin
-rw-r----- 1 ghost22 ghost22   25 Jun 22 13:41 scroll.b64
```

2. Identificazione del tipo reale di ciascun file:

```bash
file BRIEFING relic.bin scroll.b64 
BRIEFING:   Unicode text, UTF-8 text
relic.bin:  data
scroll.b64: ASCII text
```

3. Lettura del briefing operativo, che conferma la missione e il formato di invio al gatekeeper:

```bash
cat BRIEFING 
GRADUATION — OPERATIVE BRIEFING
================================

Three shards are scattered across this machine.
Each requires a different technique from the 22 levels behind you.

Recover all three. Combine them. Submit to the gatekeeper.

Gatekeeper: TCP localhost:31339
Format (exact): SHARD1:<val>|SHARD2:<val>|SHARD3:<val>

KAEL, out.
```

4. Estrazione delle stringhe leggibili dal blob binario `relic.bin` con `strings`: tra il rumore binario compare un marcatore chiaro che delimita lo Shard 1:

```bash
strings relic.bin 
...
::SHARD1:<REDACTED>::
...
```

5. Lettura e decodifica di `scroll.b64`, un payload Base64:

```bash
cat scroll.b64 
<REDACTED_BASE64>
```

Decodificando questa stringa si ottiene il secondo shard.

6. Recupero dello Shard 3 tramite l'helper SUID presente sul sistema (individuazione del binario SUID, es. con `find / -perm -4000`, ed esecuzione secondo il comportamento previsto dall'helper).

7. Composizione della stringa finale nel formato richiesto e invio al gatekeeper su TCP `:31339`:

```text
SHARD1:<REDACTED>|SHARD2:<REDACTED>|SHARD3:<REDACTED>
```

## Risultato

I tre shard vengono recuperati con tre tecniche distinte — estrazione di stringhe da binario (`strings`), decodifica Base64, e sfruttamento di un helper SUID — e combinati nel formato richiesto per essere inviati al gatekeeper TCP, completando la graduazione del Ghost Track. I valori letterali non sono riportati qui per rispetto della dottrina "no spoilers" di BreachLab.

## Nota di pubblicazione

Questo writeup è la versione pubblicabile su GitHub secondo la dottrina BreachLab (`RULES · OPS DOCTRINE`): insegna il metodo (estrazione di stringhe da binari, decodifica Base64, sfruttamento di helper SUID) senza rivelare i valori letterali degli shard o la flag finale, in modo che chi legge debba comunque eseguire l'esercizio.

---

## Crediti

Livello e sfida a cura di **BreachLab** (https://breachlab.org) — Ghost Track.
