# Phantom Track - Phantom 8

[← Torna all'indice](../../README.md)

## Sommario

- Track: Phantom Track
- Livello: Phantom 8 — "Live Injection"
- Fonte appunti: `phantom_track/phantom8/notes.md`

## Obiettivo

Il brief (`cat ~/BRIEFING`) descrive la missione così:

> A long-running process holds a secret in memory and never writes it to disk. You can see the process via /proc and, with the right capability, you can read what it is doing from the outside. Memory is more honest than the filesystem. Read it.
>
> The daemon runs as your own UID (phantom8) — /proc access is same-uid, no root required.

L'obiettivo è recuperare un segreto che un processo demone tiene esclusivamente in RAM (mai scritto su disco), sfruttando il fatto che il demone gira con lo stesso UID dell'utente (`phantom8`), condizione che rende teoricamente possibile l'introspezione via `/proc` e `ptrace` senza bisogno di root.

## Ricognizione

Con `ps aux | grep phantom8` si individuano due processi rilevanti:

- Un processo root (`runuser -u phantom8 -- python3 -c "..."`) — il wrapper che avvia il demone come `phantom8`.
- Un processo `phantom8` figlio: il demone vero e proprio, un one-liner Python.

Il comando completo del demone, ricostruito dall'output di `ps aux`, è:

```python
import sys
import time
import ctypes

# yama ptrace_scope=1 on Ubuntu blocks same-uid ptrace attach unless the
# tracee explicitly opts in via PR_SET_PTRACER (or scope=0 globally). The
# container inherits the host's read-only /proc/sys/kernel/yama, so we
# can't set scope=0 from the entrypoint. Opt in from inside the daemon:
# PR_SET_PTRACER = 0x59616d61, PR_SET_PTRACER_ANY = (unsigned long)-1.
libc = ctypes.CDLL(None)
libc.prctl(0x59616d61, ctypes.c_ulong(-1).value, 0, 0, 0)

secret = sys.stdin.readline().strip()
sys.stdin.close()

while True:
    time.sleep(60)
```

Il codice stesso, lasciato visibile negli argomenti di `ps aux`, spiega già la configurazione di sicurezza dell'host: `yama.ptrace_scope=1` normalmente impedirebbe a un processo di attaccarsi con `ptrace` a un altro processo con lo stesso UID, a meno che il processo "tracciato" non acconsenta esplicitamente tramite `prctl(PR_SET_PTRACER, ...)`. Il demone chiama proprio questa funzione con `PR_SET_PTRACER_ANY` (`-1`), aprendo la porta a *qualunque* processo dello stesso utente che voglia allegarsi con GDB/ptrace.

Enumerando `/proc/<pid>/` del demone con `ll` si osserva la struttura standard di procfs: `maps`, `mem`, `environ`, `status`, ecc. La maggior parte dei file ha dimensione 0 (procfs) ma permessi diversi: `maps` e `status` sono leggibili (`r--r--r--`), mentre `mem` è `rw-------` (accessibile solo al proprietario, coerente con l'UID condiviso) e `environ` è `r--------`.

Con `cat /proc/<pid>/maps` si ottiene la mappa completa delle region di memoria del processo: il binario `python3.10`, le librerie condivise (`libc`, `libffi`, `libexpat`, `libm`, `ld-linux`), l'`[heap]` e lo `[stack]`. L'heap è il candidato più promettente per contenere la stringa letta da `stdin.readline()`.

## Tecnica

La tecnica combina due elementi:

1. **`PR_SET_PTRACER` opt-in same-UID**: su Ubuntu con `yama.ptrace_scope=1`, un processo può normalmente essere tracciato solo dal proprio genitore diretto. Il demone, chiamando `prctl(PR_SET_PTRACER, -1)`, dichiara esplicitamente "qualsiasi processo dello stesso UID può allegarsi a me con ptrace/gdb". Questo è ciò che rende possibile l'attach con `gdb -p <pid>` da una shell qualunque con lo stesso UID, senza root e senza dover abbassare `ptrace_scope` a livello di sistema (impossibile qui, dato che `/proc/sys/kernel/yama` è montato read-only nel container).
2. **Lettura della memoria di processo via GDB / `/proc/<pid>/mem`**: una volta agganciati al processo, si può leggere la memoria del processo target come farebbe un debugger. GDB offre diversi comandi per farlo (`x` per esaminare indirizzi, `find` per cercare pattern di byte), ma soprattutto `/proc/<pid>/mem` è un file "finestra" sulla memoria virtuale del processo che, con i permessi giusti (stesso UID + ptrace consentito), può essere letto direttamente come un file binario con `dd`, `cat` o qualsiasi tool che sappia fare seek+read. Combinando `dd` (per estrarre un range di byte a partire da un offset dell'heap) con `strings` (per isolare le sequenze di caratteri stampabili) si trasforma un dump binario di centinaia di KB in testo leggibile, dentro cui cercare la stringa che il demone ha letto da stdin e non ha mai scritto su disco.

## Sfruttamento

1. **Attach fallito senza contesto.** I primi tentativi di attach, fatti passando il PID come se fosse il nome di un eseguibile (es. `gdb <qualcosa che non è un'opzione valida>`), falliscono con `No such file or directory`, perché GDB in quella forma interpreta l'argomento come un binario da caricare, non come un PID a cui allegarsi.

2. **Attach corretto con `-p`.**

   ```bash
   gdb -p <PID>
   ...
   Attaching to process <PID>
   warning: "target:/usr/bin/python3.10": could not open as an executable file: Operation not permitted.
   warning: `target:/usr/bin/python3.10': can't open to read symbols: Operation not permitted.
   0x00007bc26823261d in ?? ()
   (gdb) info registers
   ...
   ```

   L'attach riesce (grazie al `PR_SET_PTRACER_ANY` impostato dal demone). I warning su `target:/usr/bin/python3.10` sono attesi: GDB non può leggere l'eseguibile stesso per risolvere i simboli (niente permesso di lettura sul binario), quindi il processo resta "senza simboli" — niente nomi di variabili o funzioni, solo registri e memoria grezza. `info registers` conferma comunque l'attach riuscito mostrando lo stato della CPU nel punto in cui il processo era fermo.

3. **Ricerca diretta della stringa con `find` — fallita.**

   ```bash
   (gdb) find <start_heap>, <end_heap>, "secret"
   warning: Unable to access N bytes of target memory at ..., halting search.
   Pattern not found.
   ```

   Cercare letteralmente la parola `"secret"` (il nome della variabile Python, non il suo contenuto) nell'heap e nello stack non produce risultati: ovviamente il nome della variabile non esiste come stringa in memoria, solo il suo valore — che non è ancora noto.

4. **Scansione manuale dell'heap con `x/2000s`.** Per farsi un'idea di cosa contenga davvero l'heap, si esamina un blocco ampio come sequenza di stringhe (`x/<N>s <indirizzo_inizio_heap>`). L'output — migliaia di righe, in gran parte stringhe vuote o frammenti binari non stampabili — conferma che l'heap è pieno di strutture interne dell'interprete Python (buffer, riferimenti, piccoli frammenti di encoding) ma esaminarlo byte per byte con `x/s` non è pratico: serve un dump massivo e un filtro per il testo leggibile.

5. **Tentativo di dump raw da dentro GDB — fallito.**

   ```bash
   (gdb) dd if=/proc/<pid>/mem bs=1 skip=$(printf '%d' <offset_heap>) count=<N> 2>/dev/null | strings > ~/heap_dump.txt
   Undefined command: "dd".  Try "help".
   ```

   `dd` non è un comando GDB (è un errore di contesto: si sta scrivendo un comando di shell dentro il prompt `(gdb)`). Bisogna uscire da GDB e lanciare `dd` direttamente nella shell, puntandolo su `/proc/<pid>/mem` con l'offset dell'heap ricavato da `maps`.

6. **`dd` + `strings` sul file di memoria del processo, dalla shell.** Una volta fuori da GDB, `dd` legge un intervallo di byte a partire dall'offset dell'heap direttamente da `/proc/<pid>/mem` (permesso perché stesso UID e ptrace consentito), e la pipe verso `strings` isola le sequenze di testo stampabile. Il risultato è un dump di migliaia di righe: per la maggior parte si tratta di stringhe interne dell'interprete Python (nomi di moduli, docstring di `encodings`, `abc`, `signal`, `io`, frammenti di bytecode) mescolate a rumore binario. In mezzo a questo rumore compare anche il codice sorgente del demone stesso (l'interprete Python tiene il testo del proprio `-c` in memoria).

7. **Individuazione del valore.** Scorrendo il dump di `strings` fino in fondo, tra frammenti di bytecode e stringhe binarie residue, compare — isolato e ben formato, ripetuto due volte verso la coda dell'output — il segreto cercato: il pattern tipico di una stringa "reale" scritta dal setup del livello in mezzo a rumore di memoria.

## Risultato

Il segreto tenuto in memoria dal demone e mai scritto su disco è stato recuperato con successo:

```
<REDACTED_FLAG>
```

Recuperato leggendo la memoria di processo (heap) del demone tramite `/proc/<pid>/mem`, senza privilegi di root, sfruttando l'opt-in esplicito del demone a `PR_SET_PTRACER_ANY` e un dump `dd` + `strings` mirato sull'offset dell'heap ricavato da `/proc/<pid>/maps`.

## Nota di pubblicazione

Questa versione è pensata per la pubblicazione su GitHub secondo la dottrina operativa di BreachLab: il metodo (opt-in `PR_SET_PTRACER`, attach GDB same-UID, lettura di `/proc/<pid>/maps` e `/proc/<pid>/mem`, estrazione con `dd` + `strings`) è descritto per intero, perché lo scopo di un writeup è insegnare la tecnica. Il valore letterale del segreto recuperato è invece sostituito da `<REDACTED_FLAG>`, così come i PID e gli offset di memoria specifici della sessione (che sarebbero comunque diversi a ogni run e non aggiungono valore didattico) sono stati generalizzati in placeholder (`<PID>`, `<offset_heap>`). Nessuna password, flag o hint letterale viene condivisa: chi legge deve rifare il ragionamento e l'estrazione sulla propria istanza del livello.

---

## Crediti

Livello e piattaforma: BreachLab (Phantom Track, "Live Injection") — breachlab.org.
