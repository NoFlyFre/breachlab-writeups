```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x16 · CLASSIFIED · "graduation"
 ========================================================================

   target ..: ghost-22  "Graduation"  [final]
   class ...: capstone · strings + base64 + SUID
   tools ...: file · strings · base64 · find · nc
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> l'esame di maturità del Ghost Track. un file classificato spezzato in
> tre shard, ognuno chiuso con una tecnica diversa dei 22 livelli
> precedenti. si recuperano tutti e tre e si consegnano al gatekeeper.

## ----[ 0x00 · intel ]----

Livello finale del Ghost Track: un file classificato è stato spezzato in
tre shard, ognuno protetto con una tecnica già vista (dati in un blob
binario, dati codificati per il trasporto, dati dietro un helper SUID).
Vanno recuperati tutti e tre e inviati a un gatekeeper su TCP `:31339`,
nel formato esatto `SHARD1:<val>|SHARD2:<val>|SHARD3:<val>`.

## ----[ 0x01 · recon ]----

Nella home tre file utili: `BRIEFING` (UTF-8, istruzioni), `relic.bin`
(8215 byte, `file` lo dà come `data`, binario senza struttura) e
`scroll.b64` (25 byte, ASCII). Il `BRIEFING` conferma la missione: tre
shard, tre tecniche, un gatekeeper di rete che valida il formato
combinato.

## ----[ 0x02 · il difetto ]----

Capstone: un riepilogo delle tecniche del track applicate in fila.

- **Shard 1 — "buried in a binary blob":** stringhe leggibili da un
  binario con `strings`, per isolare ASCII annegato in un blob.
- **Shard 2 — "encoded for transport":** decodifica Base64 di un file di
  testo, la stessa codifica vista altrove nel track.
- **Shard 3 — "guarded by a SUID helper":** recupero via un binario SUID,
  la privesc/accesso controllato tipica del track.

## ----[ 0x03 · exploit ]----

1. Enumerazione e tre file utili:

```bash
ll
...
-rw-r----- 1 ghost22 ghost22  343 Jun 22 13:41 BRIEFING
-rw-r----- 1 ghost22 ghost22 8215 Jun 22 13:41 relic.bin
-rw-r----- 1 ghost22 ghost22   25 Jun 22 13:41 scroll.b64
```

2. Tipo reale di ciascuno:

```bash
file BRIEFING relic.bin scroll.b64
BRIEFING:   Unicode text, UTF-8 text
relic.bin:  data
scroll.b64: ASCII text
```

3. Briefing operativo, che conferma missione e formato:

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

4. Stringhe da `relic.bin`: tra il rumore, un marcatore delimita lo
   Shard 1:

```bash
strings relic.bin
...
::SHARD1:<REDACTED>::
...
```

5. `scroll.b64`, payload Base64 → Shard 2:

```bash
cat scroll.b64
<REDACTED_BASE64>
```

6. Shard 3 dall'helper SUID sul sistema (`find / -perm -4000` per
   individuarlo, poi esecuzione secondo il comportamento previsto).

7. Composizione finale e invio al gatekeeper su TCP `:31339`:

```text
SHARD1:<REDACTED>|SHARD2:<REDACTED>|SHARD3:<REDACTED>
```

## ----[ 0x04 · loot ]----

Tre shard, tre tecniche — `strings`, Base64, helper SUID — combinati nel
formato richiesto e consegnati al gatekeeper: Ghost Track completato
(valori fuori dal writeup). Diploma in tasca.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
