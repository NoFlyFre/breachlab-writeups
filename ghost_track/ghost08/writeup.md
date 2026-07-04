```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x08 · "something's running"
 ========================================================================

   target ..: ghost-08  "Something's Running"
   class ...: process inspection · /proc environ
   tools ...: ps · cat /proc · tr
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> file cancellati, log puliti, argomenti dei processi rimossi. però
> `/proc` ricorda quello che la shell dimentica: finché il processo è
> vivo, il suo ambiente è lì da leggere.

## ----[ 0x00 · intel ]----

Recuperare la password del livello dopo. Il banner dice che un operatore
ha ripulito file, log e persino gli argomenti dei suoi processi — quindi
`ps aux` non basta. La strada è il filesystem virtuale `/proc`.

## ----[ 0x01 · recon ]----

La home non ha nulla oltre ai dotfile standard. L'indizio è nel banner:
argomenti dei processi ripuliti, quindi niente segreti da riga di
comando in `ps`. Frugando `/proc` a mano (`cmdline`, `keys`,
`timer_list`, la gerarchia `sys/`) non emerge niente di utile. Ma
enumerando i processi dell'utente compaiono più istanze dello stesso
demone di livello, lanciate da root e poi declassate all'utente target.

## ----[ 0x02 · il difetto ]----

`/proc/<pid>/environ` espone le variabili d'ambiente con cui un processo
è partito, a prescindere dal fatto che i suoi argomenti siano stati
ripuliti. Le variabili sono separate da byte NUL (`\0`), quindi vanno
convertite con `tr '\0' '\n'` per leggerle. Se un segreto è stato passato
come env var (pratica comune per tenerlo fuori da `ps aux`, ma non
sicura), resta visibile qui finché il processo vive — log e history
cancellati o meno.

## ----[ 0x03 · exploit ]----

1. Enumerazione dei processi dell'utente per trovare i PID del demone:

```bash
ps aux | grep <utente>
```

Più istanze dello stesso processo, lanciate da root ed eseguite come
l'utente target.

2. Lettura dell'ambiente di ciascun processo, NUL → newline:

```bash
cat /proc/<PID>/environ | tr '\0' '\n'
```

3. Una delle istanze espone, tra le variabili di sistema, una env var non
   standard col segreto del livello (valore omesso). Non fa parte
   dell'ambiente shell tipico (HOSTNAME, PWD, HOME, SHLVL, PATH…): è stata
   iniettata nel processo lanciato da root.

## ----[ 0x04 · loot ]----

Password del livello successivo letta dall'ambiente di uno dei processi
via `/proc/<pid>/environ` (valore omesso). Lezione: un segreto passato
come variabile d'ambiente non è nascosto — è solo fuori da `ps`, ma resta
in `/proc`.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
