# Phantom Track - Phantom 4

## Sommario

- Track: Phantom Track
- Livello: Phantom 4 ("Misplaced Power")
- Fonte appunti: `phantom_track/phantom4/notes.md`

## Obiettivo

Il briefing chiarisce l'obiettivo: sul sistema esiste un interprete general-purpose con bit SUID impostato, cosa che non dovrebbe mai accadere. Non è di proprietà di root, ma di un utente che può leggere più dati dell'utente corrente. Bisogna enumerare i binari SUID, capire quale è fuori posto, e usarlo per leggere la flag posseduta da quell'utente.

## Ricognizione

Un primo tentativo diretto di eseguire l'interprete sospetto come modulo Python fallisce in modo rivelatore, con un errore di sintassi che indica byte non validi come sorgente Python. Questo suggerisce che il binario non è uno script testuale, ma un eseguibile compilato (l'header ELF inizia con byte non validi come sorgente Python).

La successiva enumerazione dei binari SUID sul sistema conferma il sospetto: tra i binari con bit SUID attivo (`-rwsr-x---`), uno risulta posseduto da un account non di sistema e appartenente a un gruppo che coincide con l'utente della sessione corrente — un'anomalia rispetto agli altri binari SUID standard di sistema (tutti posseduti da `root`).

Un controllo con `file` conferma che si tratta di un vero eseguibile ELF con SUID, non di uno script.

Eseguendolo direttamente si apre una vera REPL Python 3, ma in esecuzione con l'identità effettiva del proprietario del binario, non dell'utente che lo lancia.

## Tecnica

Questo è un classico caso di **SUID su interprete general-purpose**: un binario che incapsula un interprete Python completo viene marcato SUID e reso eseguibile da un gruppo di utenti. Poiché Python è un linguaggio interpretato general-purpose con accesso completo a syscall tramite i moduli `os` e simili, qualunque utente in grado di lanciare questo binario ottiene di fatto una shell con i privilegi effettivi del proprietario del binario, bypassando qualsiasi restrizione di accesso ai file di quell'utente.

Il principio generale (documentato anche in GTFOBins per `python`/`python3`) è che qualsiasi interprete general-purpose con SUID equivale a privilege escalation completa verso l'utente proprietario, perché l'interprete permette di eseguire codice arbitrario (lettura file, `os.system`, spawn di shell) con l'UID effettivo ereditato dal bit SUID.

## Sfruttamento

1. Tentativo iniziale fallito di eseguire il binario come modulo Python, che rivela trattarsi di un ELF e non di uno script:

```bash
python3 /usr/local/bin/<nome_binario_suid>
```

2. Enumerazione sistematica di tutti i binari SUID sul filesystem per individuare l'anomalia (proprietario non-root, eseguibile da un gruppo utente):

```bash
find / -type f -perm -4000 -ls 2>/dev/null
```

3. Verifica del tipo di file per confermare che è un vero binario ELF con SUID e non uno script interpretato:

```bash
file /usr/local/bin/<nome_binario_suid>
```

4. Esecuzione diretta del binario, che apre una REPL Python con i privilegi effettivi del proprietario del file:

```bash
/usr/local/bin/<nome_binario_suid>
```

5. All'interno della REPL, uso dei privilegi ereditati per esplorare il filesystem dell'utente target e localizzare la flag:

```python
>>> import os
>>> os.system("find / -user <utente_target> -ls 2>/dev/null")
```

L'output rivela il percorso di un file protetto (`-rw-------`) posseduto dall'utente target.

6. Un tentativo di leggerlo tramite `os.system("cat ...")` fallisce con permesso negato, perché la subshell lanciata da `os.system` non mantiene lo stesso comportamento privilegiato per l'accesso a quel file in quel contesto.

7. La lettura diretta tramite le funzioni native dell'interprete Python (`open()`), che opera con l'EUID del processo Python stesso (quello ereditato dal SUID), invece riesce:

```python
>>> print(open("<percorso_file_flag>").read())
```

## Risultato

La flag è stata letta direttamente dall'interprete Python SUID, sfruttando il fatto che `open()` chiamato dall'interno del processo con l'EUID del proprietario del binario bypassa i permessi restrittivi del file, mentre chiamare una subshell esterna con `os.system()` in questo caso non manteneva lo stesso comportamento privilegiato per l'accesso al file. Il valore letterale della flag non viene riportato in questa versione.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub, in conformità con la dottrina BreachLab: insegna il metodo (identificazione di un interprete general-purpose con SUID anomalo, differenza tra `os.system()` e `open()` nativo rispetto all'EUID effettivo) senza riportare nomi di file/utenti specifici del lab né il valore della flag.

## Crediti

Livello e piattaforma: BreachLab (breachlab.org) — Phantom Track. Se questo writeup genera revenue, parte del ricavato va devoluta secondo la dottrina "if it earns, give back" di BreachLab.
