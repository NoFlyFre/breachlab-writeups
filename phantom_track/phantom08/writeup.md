```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x08 · "live injection"
 ========================================================================

   target ..: phantom-08  "Live Injection"
   class ...: process memory · ptrace · /proc/pid/mem
   tools ...: ps · gdb -p · dd · strings
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> un demone tiene un segreto in RAM e non lo scrive mai su disco. gira col
> tuo stesso UID e — colpo di scena — acconsente esplicitamente a farsi
> tracciare. la memoria è più onesta del filesystem: la si legge.

## ----[ 0x00 · intel ]----

Dal brief:

> A long-running process holds a secret in memory and never writes it to disk. You can see the process via /proc and, with the right capability, you can read what it is doing from the outside. Memory is more honest than the filesystem. Read it.
>
> The daemon runs as your own UID (phantom8) — /proc access is same-uid, no root required.

Obiettivo: recuperare un segreto che il demone tiene solo in RAM,
sfruttando il fatto che gira come `phantom8` — condizione che rende
possibile l'introspezione via `/proc` e `ptrace` senza root.

## ----[ 0x01 · recon ]----

`ps aux | grep phantom8` mostra due processi: un wrapper root
(`runuser -u phantom8 -- python3 -c "..."`) e il demone figlio come
`phantom8`, un one-liner Python. Il comando completo, visibile in `ps`:

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

Il codice spiega da solo la sicurezza dell'host: `yama.ptrace_scope=1`
bloccherebbe l'attach ptrace same-UID, ma il demone chiama
`prctl(PR_SET_PTRACER, -1)` (`PR_SET_PTRACER_ANY`), aprendo a *qualunque*
processo dello stesso utente. In `/proc/<pid>/`, `maps` e `status` sono
`r--r--r--`, `mem` è `rw-------` (stesso UID) ed `environ` `r--------`.
`cat /proc/<pid>/maps` dà le region: python3.10, librerie, `[heap]`,
`[stack]`. L'heap è il candidato per la stringa letta da
`stdin.readline()`.

## ----[ 0x02 · il difetto ]----

Due elementi:

1. **PR_SET_PTRACER opt-in same-UID** — con `ptrace_scope=1` un processo è
   tracciabile solo dal padre; il demone dichiara "chiunque col mio UID
   può agganciarmi", quindi `gdb -p <pid>` funziona senza root e senza
   toccare `ptrace_scope` (impossibile qui, `/proc/sys/kernel/yama` è
   read-only nel container).
2. **lettura memoria via `/proc/<pid>/mem`** — agganciati al processo, la
   sua memoria si legge come un debugger. `/proc/<pid>/mem` è una finestra
   sulla memoria virtuale: coi permessi giusti (stesso UID + ptrace
   consentito) la si legge come file binario con `dd`, e `strings` isola
   il testo leggibile da centinaia di KB di dump.

## ----[ 0x03 · exploit ]----

1. Attach fallito passando il PID come fosse un eseguibile → `No such file
   or directory` (GDB lo interpreta come binario, non come PID).

2. Attach corretto con `-p`:

```bash
gdb -p <PID>
...
Attaching to process <PID>
warning: "target:/usr/bin/python3.10": could not open as an executable file: Operation not permitted.
0x00007bc26823261d in ?? ()
(gdb) info registers
...
```

Riesce (grazie al `PR_SET_PTRACER_ANY`). I warning sui simboli sono
attesi: GDB non può leggere il binario, quindi niente simboli, solo
registri e memoria grezza.

3. `find` letterale della parola `"secret"` (nome della variabile, non il
   valore) → nulla, ovviamente.

4. Scansione dell'heap con `x/2000s <inizio_heap>`: migliaia di righe,
   per lo più strutture interne di Python. Esaminare a mano con `x/s` non
   è pratico: serve un dump massivo + filtro.

5. Tentativo di `dd` da dentro GDB → `Undefined command: "dd"` (è un
   comando di shell, non di GDB). Si esce e si lancia dalla shell.

6. `dd` + `strings` su `/proc/<pid>/mem` all'offset dell'heap (ricavato da
   `maps`): dump di migliaia di righe, per lo più stringhe interne di
   Python e il sorgente stesso del demone.

7. Scorrendo fino in fondo, isolato e ripetuto due volte verso la coda,
   compare il segreto — una stringa "reale" in mezzo al rumore di memoria.

## ----[ 0x04 · loot ]----

Segreto tenuto solo in RAM recuperato via `/proc/<pid>/mem`, senza root,
grazie all'opt-in `PR_SET_PTRACER_ANY` e a un `dd` + `strings` mirato
sull'offset dell'heap:

```
<REDACTED_FLAG>
```

Lezione: se un processo acconsente al ptrace same-UID, la sua memoria è un
file aperto — e la memoria non mente.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
