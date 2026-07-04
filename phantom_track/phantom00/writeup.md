```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x00 · "recon gateway"
 ========================================================================

   target ..: phantom-00  "Recon Gateway"
   class ...: post-exploitation recon · situational awareness
   tools ...: uname · ps · ip · find -newermt
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> hai già la shell. prima di scalare qualunque cosa, serve
> consapevolezza: che OS, chi altro c'è, che servizi girano, che difese.
> e la flag la trovi non frugando a tappeto, ma isolando ciò che il lab ha
> "piantato" nella sua finestra di setup.

## ----[ 0x00 · intel ]----

Il brief è chiaro: shell su un host compromesso, e prima di ogni
escalation serve piena situational awareness. Domande guida: OS/kernel,
altri utenti, servizi attivi, difese presenti. La flag è dove solo una
recon fatta bene la trova.

## ----[ 0x01 · recon ]----

Metodo da checklist di privesc Linux (stile HackTricks), in sequenza:

- **OS/kernel** — `uname -a`, `/etc/os-release`: Ubuntu LTS, kernel
  recente.
- **utenti** — `/etc/passwd`: popolazione insolita, decine di utenti
  numerati (i livelli), account `flagkeeper`, alcuni account di servizio.
  Alcuni hanno come shell un binario custom invece di una shell
  interattiva: meccanismo di redirect/sandboxing del lab.
- **gruppi** — `/etc/group`: un utente è nel gruppo `shadow` (privilegio
  insolito, di norma legge `/etc/shadow`); un altro è membro secondario
  del gruppo di un altro livello.
- **processi** — oltre ai processi da container, due chicche: un
  emulatore dell'API Docker in ascolto su TCP e su socket Unix, e un
  processo con riferimento a `ptrace_scope`. Indizi sui livelli dopo
  (container escape, ptrace).
- **difese** — AppArmor installato, ASLR al default hardened.
- **rete** — due interfacce (Docker generale + rete dedicata al
  pivoting), IP forwarding abilitato: possibile ruolo di gateway.
- **cron** — tra le voci di sistema, un file dal nome legato alla
  rotazione delle flag.
- **superficie privesc** — enumerati sudo e SUID, propedeutici ai livelli
  dopo.

La ricerca decisiva: tutti i file leggibili modificati nella finestra
temporale del provisioning del lab.

## ----[ 0x02 · il difetto ]----

Recon sistematica + ricerca temporale mirata (`find -newermt`). Invece
dell'enumerazione a tappeto, si isolano i file toccati esattamente quando
il lab è stato provisionato: lo spazio di ricerca crolla e si va dritti
agli artefatti piantati dagli autori — flag inclusa — evitando il rumore
di pacchetti, cache e doc di sistema.

## ----[ 0x03 · exploit ]----

1. OS e kernel:

```bash
uname -a
cat /etc/os-release
```

2. Utenti e gruppi:

```bash
cat /etc/passwd
cat /etc/group
```

3. Processi attivi:

```bash
ps -aux
ps -ef
top -n 1
```

4. Difese (AppArmor, ASLR):

```bash
if [ `which aa-status 2>/dev/null` ]; then aa-status; elif [ `ls -d /etc/apparmor* 2>/dev/null` ]; then ls -d /etc/apparmor*; fi
cat /proc/sys/kernel/randomize_va_space
```

5. Rete:

```bash
(ifconfig || ip a)
ip route
sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding net.ipv4.conf.all.rp_filter
```

6. Cron di sistema, dove spunta il file legato alle flag:

```bash
cat /etc/cron* /etc/at* /etc/anacrontab /var/spool/cron/crontabs/root 2>/dev/null | grep -v "^#"
ls -al /etc/cron.d/
```

7. Superficie di privilegio:

```bash
sudo -l
find / -perm -4000 2>/dev/null
```

8. La ricerca decisiva: file leggibili toccati nella finestra di
   provisioning, filtrando il rumore:

```bash
find / \( -path /proc -o -path /sys -o -path /run \) -prune -o \
  -type f -newermt '<data_provisioning>' ! -newermt '<data_provisioning+1>' -readable -print 2>/dev/null \
  | grep -vE '^/(usr/lib|usr/share|var/lib/dpkg|etc/ssl)' | head -60
```

Escono gli script di verifica dei livelli successivi (pod escape,
persistence, clean exit, shadow…), un vault, un segreto legato al
namespace host, e il file della flag.

9. `cat` sul file flag individuato.

## ----[ 0x04 · loot ]----

La flag era in un file sotto `/opt/`, trovata non a tappeto ma isolando i
file modificati nella finestra di provisioning (valore fuori dal
writeup). In più la recon ha raccolto munizioni per dopo: socket Docker
emulato, `ptrace_scope`, gruppo `shadow` su un utente, script che
anticipano pod escape, persistence e namespace host. Lezione: `find
-newermt` trasforma un filesystem enorme in una lista corta.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
