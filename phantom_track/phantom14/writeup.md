```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x0e · "shadow mode"
 ========================================================================

   target ..: phantom-14  "Shadow Mode"
   class ...: anti-forensics · shell builtin read
   tools ...: compgen -b · $(< file)
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> puoi leggere la flag, ma ogni open del file è osservato dal kernel. una
> lettura conta come "silenziosa" solo se è la shell stessa a farla:
> `cat`, `head`, `less` — qualunque reader esterno finisce nel log.

## ----[ 0x00 · intel ]----

La flag è in un file di root, leggibile grazie all'appartenenza a un
gruppo. La sfida non è l'accesso (già garantito) ma leggerlo in modo
silenzioso: un builtin di lettura non lascia traccia di un reader esterno
nell'audit, mentre qualunque tool esterno (`cat`, `head`, `less`, un
interprete, persino una copia rinominata) viene registrato.

## ----[ 0x01 · recon ]----

Il vincolo: riprodurre i byte della flag in un file temporaneo usando solo
builtin della shell, poi lanciare lo script di verifica, che controlla due
cose: copia byte-per-byte identica all'originale, e file mai aperto da un
reader esterno.

Enumerazione dei builtin:

```bash
compgen -b
...
mapfile
...
read
readarray
...
```

Candidati: `read`, `mapfile`/`readarray`, e la command substitution su file
descriptor (`$(< file)`), gestita internamente da bash senza fork/exec.

## ----[ 0x02 · il difetto ]----

`read` da solo non legge un intero file (è pensato per una riga da stream),
e `read <percorso>` fallisce (il primo argomento è un nome di variabile).
La tecnica giusta è `$(< file)`, una command substitution ottimizzata:
quando dentro `$(...)` c'è solo `< file`, bash apre e legge il file
internamente, senza subshell con `cat`. Con `echo` e una redirezione verso
un temp file si ottiene una copia byte-per-byte senza che nessun processo
esterno abbia mai aperto il file.

## ----[ 0x03 · exploit ]----

1. Builtin disponibili:

```bash
compgen -b
```

2. Tentativo errato di `read` su un percorso:

```bash
read /path/to/file
bash: read: `/path/to/file': not a valid identifier
```

3. Doc del builtin:

```bash
read --help
```

4. Lettura via `$(< file)` (interna a bash) e scrittura nel percorso del
   verificatore:

```bash
echo $(<percorso_del_file_target) > /tmp/shadow_copy
```

5. Verifica:

```bash
/opt/verify-shadow.sh
[+] Proof of read: <REDACTED> matches <REDACTED>
[+] Technique: flag was read via your own pristine shell builtin

[*] FLAG: <REDACTED_FLAG>
```

## ----[ 0x04 · loot ]----

Contenuto riprodotto con la sola command substitution `$(< file)`, senza
reader esterni; il verifier conferma copia identica e zero tracce (flag
omessa). Lezione: I/O gestito dalla shell vs I/O che richiede fork/exec —
è la differenza tra invisibile e loggato per auditd/eBPF.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
