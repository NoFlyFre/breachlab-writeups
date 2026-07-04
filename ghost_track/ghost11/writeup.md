# Ghost Track - Ghost 11

[← Torna all'indice](../../README.md)

## Sommario

- **Track:** Ghost Track
- **Livello:** Ghost 11 → 12 ("Unwrap the Stage")
- **Fonte appunti:** `ghost_track/ghost11/notes.md`

## Obiettivo

Nella home di `ghost11` è presente un file `stage.bin` (leggibile solo dal proprietario). Il livello avverte che si tratta di un bundle "avvolto tre volte" in formati diversi, pensato per confondere controlli DLP superficiali che si basano solo sull'estensione del file. Obiettivo: identificare correttamente ogni formato (senza fidarsi del nome/estensione) e scartare i livelli di compressione uno alla volta, fino a recuperare la credenziale per il livello successivo.

## Ricognizione

Un primo `ll` nella home mostra un solo file rilevante, `stage.bin`, da 10240 byte. Il nome suggerisce un blob binario generico, ma è proprio questo il punto: bisogna verificare il tipo reale del file invece di fidarsi dell'estensione. Il comando `file` viene usato sistematicamente prima di ogni tentativo di estrazione, ed è questo approccio — identifica, poi decomprimi — che guida tutta la sequenza.

## Tecnica

Si tratta di un caso di **compressione/archiviazione a più livelli con estensioni fuorvianti** (mismatch tra nome del file e magic number reale). La tecnica corretta non è indovinare il formato dal nome, ma interrogare i primi byte del file con `file` (che legge i magic number) e agire di conseguenza:

- Un `tar` archive va estratto con `tar -xf` (non semplicemente `tar -x`, che senza `-f` si aspetta input da terminale).
- Un file XZ va decompresso con `xz --decompress` (attenzione: il comando `xz` senza `--decompress` tenta di comprimere ulteriormente e, se il nome ha già suffisso `.xz`, si rifiuta).
- Un file gzip va decompresso con `gunzip` (anche qui, `gzip` sul file già col suffisso `.gz` si rifiuta, serve l'operazione di decompressione esplicita).

Il bundle nasconde tre livelli annidati: tar → xz → gzip, ciascuno rilevabile solo controllando il magic number reale, non l'estensione superficiale del file.

## Sfruttamento

1. Enumerazione della home directory e identificazione del file target:

```bash
ll
total 64
...
-rw-r----- 1 ghost11 ghost11 10240 Jun 22 13:41 stage.bin
```

2. Verifica del tipo reale del file con `file`, che rivela un archivio tar nonostante il nome generico `.bin`:

```bash
file stage.bin 
stage.bin: POSIX tar archive (GNU)
```

3. Tentativo di estrazione senza `-f` fallisce (tar si aspetta input da stdin/terminale); si corregge con `-f` per indicare il file esplicitamente:

```bash
tar -x stage.bin
tar: Refusing to read archive contents from terminal (missing -f option?)
tar -xf stage.bin
```

L'estrazione produce un secondo file, prossimo livello del bundle, con estensione combinata `.gz.xz`.

4. Anche qui, non ci si fida del nome: si verifica il tipo reale, che conferma dati XZ compressi:

```bash
file payload.txt.gz.xz 
payload.txt.gz.xz: XZ compressed data, checksum CRC64
xz --decompress payload.txt.gz.xz
```

Questo produce il file successivo con estensione `.gz`.

5. Ultimo livello, decompressione gzip con `gunzip` (il comando `gzip` diretto si rifiuta perché il file ha già suffisso `.gz`):

```bash
gunzip payload.txt.gz
```

Il risultato finale è un file di testo di pochi byte.

6. Lettura del contenuto in chiaro, che rivela la credenziale per il livello successivo:

```bash
cat payload.txt 
<REDACTED>
```

## Risultato

La sequenza di identificazione (`file`) + decompressione mirata (`tar -xf` → `xz --decompress` → `gunzip`) porta al recupero della credenziale per l'utente successivo della catena, non riportata qui per rispetto della dottrina "no spoilers" di BreachLab.

## Nota di pubblicazione

Questo writeup è la versione pubblicabile su GitHub secondo la dottrina BreachLab (`RULES · OPS DOCTRINE`): insegna il metodo (identificazione di formati file tramite magic number e decompressione a più livelli) senza rivelare la password/flag letterale del livello, in modo che chi legge debba comunque eseguire l'esercizio.

---

## Crediti

Livello e sfida a cura di **BreachLab** (https://breachlab.org) — Ghost Track.
