# Phantom Track - Phantom 14

## Sommario

- Track: Phantom Track
- Livello: Phantom 14 ("Shadow Mode")
- Fonte appunti: `phantom_track/phantom14/notes.md`

## Obiettivo

La flag si trova in un file di proprietà di root, leggibile in virtù dell'appartenenza a un gruppo che ne consente la lettura. La vera sfida non è ottenere l'accesso al file (già garantito), ma leggerlo in modo "silenzioso": ogni processo che apre il file viene osservato a livello kernel, e una lettura conta come silenziosa solo se è la shell stessa a leggere il file — un builtin di lettura non lascia traccia di un reader esterno nel log di audit. Qualunque tool esterno (`cat`, `head`, `less`, un interprete, persino una copia rinominata di un reader) viene invece registrato, indipendentemente da come viene invocato o mascherato.

## Nota di pubblicazione

Questa versione è pensata per GitHub e segue la dottrina BreachLab: spiega per intero la tecnica di lettura "silenziosa" tramite builtin di shell, ma omette il percorso esatto del file target e il valore della flag.

## Ricognizione

Il brief chiarisce esplicitamente il vincolo: bisogna riprodurre i byte della flag in un file temporaneo usando esclusivamente builtin della shell (non binari esterni), poi eseguire lo script di verifica fornito dal livello, che verifica due condizioni: che la copia corrisponda byte-per-byte all'originale, e che il file non sia mai stato aperto da un reader esterno durante la sessione.

Enumerazione dei builtin disponibili in bash con `compgen -b`, per identificare quali di essi permettono di leggere il contenuto di un file senza invocare un processo esterno:

```bash
compgen -b
...
mapfile
...
read
readarray
...
```

I candidati più promettenti sono `read`, `mapfile`/`readarray`, e la sostituzione di comando su file descriptor (`$(< file)`), che in bash è gestita internamente dalla shell senza fork/exec di un processo esterno per l'operazione di lettura in sé.

## Tecnica

Il builtin `read` da solo non è sufficiente per leggere un intero file in un colpo (è pensato per leggere una riga da uno stream), e tentativi ingenui come `read <percorso>` falliscono con errori di sintassi (il primo argomento di `read` è un nome di variabile, non un percorso).

La tecnica corretta sfrutta la sintassi speciale di bash `$(< file)`, una forma di command substitution ottimizzata: quando il "comando" dentro `$(...)` è semplicemente `< file`, bash apre e legge il file internamente (senza eseguire una subshell con `cat`), restituendone il contenuto come stringa. Combinando questo con `echo` e una redirezione verso un file temporaneo, si ottiene una copia byte-per-byte del contenuto del file, senza che nessun processo esterno lo abbia mai aperto direttamente.

## Sfruttamento

1. Enumerazione dei builtin disponibili, per identificare le primitive di lettura native della shell:

```bash
compgen -b
```

2. Primo tentativo, errato, di usare `read` direttamente su un percorso (fallisce, perché `read` si aspetta un nome di variabile):

```bash
read /path/to/file
bash: read: `/path/to/file': not a valid identifier
```

3. Consultazione della documentazione del builtin per capire l'uso corretto:

```bash
read --help
```

4. Lettura del file tramite command substitution `$(< file)` (gestita internamente da bash, nessun processo esterno coinvolto) e scrittura del risultato nel percorso richiesto dal verificatore:

```bash
echo $(<percorso_del_file_target) > /tmp/shadow_copy
```

5. Esecuzione dello script di verifica fornito dal livello, che conferma sia la corrispondenza byte-per-byte sia l'assenza di reader esterni sul file originale, rilasciando la flag:

```bash
/opt/verify-shadow.sh
[+] Proof of read: <REDACTED> matches <REDACTED>
[+] Technique: flag was read via your own pristine shell builtin

[*] FLAG: <REDACTED_FLAG>
```

## Risultato

Riprodotto il contenuto del file target in una copia temporanea usando esclusivamente la sostituzione di comando builtin `$(< file)` di bash, senza mai invocare un processo esterno per la lettura del file originale. Lo script di verifica ha confermato sia la corrispondenza byte-per-byte sia l'assenza di reader esterni registrati. Valore della flag omesso in questa versione pubblica. Il livello ha insegnato la distinzione tra I/O gestito internamente dalla shell e I/O che richiede fork/exec di un processo esterno — rilevante per capire cosa può o non può essere osservato da strumenti di auditing basati su syscall/processi (es. auditd, eBPF).

## Crediti

Lab: BreachLab. Pubblicare sempre con credito al progetto e senza spoiler risolutivi.
