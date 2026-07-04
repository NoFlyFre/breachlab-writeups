```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x0b · "unwrap the stage"
 ========================================================================

   target ..: ghost-11  "Unwrap the Stage"
   class ...: file formats · magic numbers · nested archives
   tools ...: file · tar · xz · gunzip
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> `stage.bin` è una cipolla: avvolta tre volte in formati diversi per
> fregare i controlli DLP che guardano solo l'estensione. non fidarti del
> nome — chiedi ai magic number.

## ----[ 0x00 · intel ]----

Nella home c'è `stage.bin` (leggibile solo dal proprietario), un bundle
"avvolto tre volte" pensato per confondere i controlli superficiali
basati sull'estensione. Obiettivo: identificare ogni formato reale e
scartare i livelli uno alla volta fino alla credenziale.

## ----[ 0x01 · recon ]----

`ll` mostra un solo file utile, `stage.bin`, 10240 byte. Il nome dice
"blob generico", ed è il punto: si verifica il tipo reale invece di
fidarsi. `file` va usato sistematicamente prima di ogni estrazione —
identifica, poi decomprimi.

## ----[ 0x02 · il difetto ]----

Archiviazione a più livelli con estensioni fuorvianti (mismatch tra nome
e magic number). Non si indovina dal nome, si interrogano i primi byte
con `file`:

- un archive `tar` → `tar -xf` (senza `-f` tar aspetta input dal
  terminale).
- un file XZ → `xz --decompress` (senza `--decompress`, con suffisso
  `.xz` già presente, si rifiuta).
- un file gzip → `gunzip` (idem: `gzip` sul file già `.gz` si rifiuta).

Tre strati annidati: tar → xz → gzip, ognuno rilevabile solo dal magic
number reale.

## ----[ 0x03 · exploit ]----

1. Enumerazione e target:

```bash
ll
...
-rw-r----- 1 ghost11 ghost11 10240 Jun 22 13:41 stage.bin
```

2. Tipo reale del file — è un tar, nonostante il `.bin`:

```bash
file stage.bin
stage.bin: POSIX tar archive (GNU)
```

3. Estrazione senza `-f` fallisce, si corregge:

```bash
tar -x stage.bin
tar: Refusing to read archive contents from terminal (missing -f option?)
tar -xf stage.bin
```

Ne esce un file `.gz.xz`.

4. Non ci si fida del nome, si verifica: dati XZ:

```bash
file payload.txt.gz.xz
payload.txt.gz.xz: XZ compressed data, checksum CRC64
xz --decompress payload.txt.gz.xz
```

Produce il `.gz`.

5. Ultimo strato con `gunzip` (`gzip` diretto si rifiuta col suffisso già
   presente):

```bash
gunzip payload.txt.gz
```

6. Lettura del testo finale:

```bash
cat payload.txt
<REDACTED>
```

## ----[ 0x04 · loot ]----

`file` per identificare + decompressione mirata (`tar -xf` →
`xz --decompress` → `gunzip`) porta alla credenziale per l'utente dopo
(valore fuori dal writeup). Lezione: l'estensione mente, il magic number
no.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
