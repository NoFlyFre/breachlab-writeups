# Ghost Track - Ghost 6

[← Torna all'indice](../../README.md)

## Sommario

- **Track:** Ghost Track
- **Livello:** Ghost 6 → 7 ("Ghost in the Machine")
- **Fonte appunti:** `ghost_track/ghost06/notes.md`

## Obiettivo

Il livello suggerisce che KAEL, dopo la breach, ha smesso di scrivere segreti su disco convinto che la shell "dimentichi" ciò che le viene passato — ma non è così. L'obiettivo è dimostrare che le variabili d'ambiente (e la configurazione persistita in file come `.bashrc`) sono un luogo comune, e spesso trascurato, dove finiscono credenziali in chiaro o codificate. Bisogna trovare e decodificare la credenziale corretta per il livello successivo.

## Ricognizione

La home di `ghost6` non contiene file sospetti a prima vista: solo i dotfile standard (`.bash_logout`, `.bashrc`, `.profile`) e una cache vuota. Il punto debole è proprio `.bashrc`, che tra le variabili d'ambiente "di sistema" (build id, log level, region, ecc. — tutte plausibili e innocue) nasconde quattro variabili con valore codificato in Base64.

## Tecnica

Si tratta di un caso di **secret leakage tramite variabili d'ambiente persistite in un file di configurazione della shell**, combinato con **offuscamento debole via Base64** (non crittografia: Base64 è solo una codifica, reversibile senza chiave). La tecnica corretta è:

1. Riconoscere il pattern Base64 (charset alfanumerico + `+`, `/`, padding `=`).
2. Decodificare ogni candidato con `base64 -d` (o equivalente).
3. Valutare quale valore decodificato sia plausibile come credenziale reale, distinguendolo dai distrattori — nomi di variabile e valori palesemente etichettati come "non reali" sono indizio di depistaggio intenzionale.

## Sfruttamento

1. Enumerazione della home directory: nessun file anomalo, solo dotfile standard.

```bash
ll
total 48
drwx------ 1 ghost6 ghost6 4096 Jun 24 18:57 ./
...
-rw-r--r-- 1 ghost6 ghost6 4419 Jun 22 13:41 .bashrc
```

2. Ispezione della cache utente, che risulta vuota (nessuna evidenza utile):

```bash
ll .cache/
total 12
drwx------ 2 ghost6 ghost6 4096 Jun 22 19:11 ./
drwx------ 1 ghost6 ghost6 4096 Jun 24 18:57 ../
-rw-r--r-- 1 ghost6 ghost6    0 Jun 22 19:11 motd.legal-displayed
```

3. Lettura di `.bashrc`: dopo variabili "di sistema" ovviamente innocue, compaiono quattro `export` con valore Base64:

```bash
cat .bashrc 
...
export TRACE_SALT=<REDACTED_B64>
export API_DIGEST=<REDACTED_B64>
export RUNTIME_TOKEN=<REDACTED_B64>
export CACHE_SEED=<REDACTED_B64>
```

4. Decodifica di ciascun valore con `base64 -d`. Tre dei quattro valori decodificati risultano essere distrattori (nomi/etichette che dichiarano esplicitamente di non essere la credenziale reale, es. un valore il cui contenuto stesso include la dicitura "not a real credential"). Il valore restante, associato alla variabile `API_DIGEST`, è la credenziale reale per il livello successivo.

## Risultato

Decodificando sistematicamente le quattro variabili Base64 in `.bashrc` e scartando i distrattori si ottiene la credenziale per l'utente successivo della catena. Il valore non è riportato qui per rispetto della dottrina "no spoilers" di BreachLab.

## Nota di pubblicazione

Questo writeup è la versione pubblicabile su GitHub secondo la dottrina BreachLab (`RULES · OPS DOCTRINE`): insegna il metodo (individuazione e decodifica di segreti Base64 in variabili d'ambiente/file di configurazione della shell, e discriminazione dai distrattori) senza rivelare la password/flag letterale del livello.

---

## Crediti

Livello e sfida a cura di **BreachLab** (https://breachlab.org) — Ghost Track.
