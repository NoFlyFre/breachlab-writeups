# Ghost Track - Ghost 7

## Sommario

- Track: Ghost Track
- Livello: Ghost 7 → Ghost 8 ("Lost in Translation")
- Fonte appunti: `ghost_track/ghost7/notes.md`
- Variante: censored (pubblicabile)

## Obiettivo

Il livello fornisce un file di "trasmissione" con un indizio esplicito: nulla di ciò che è stato inviato è "solo una cosa" — un suggerimento che il file richiede più di un livello di decodifica prima di rivelare la credenziale dell'account successivo.

## Ricognizione

Nella home dell'utente è presente un solo file rilevante, di dimensioni ridotte (poche centinaia di byte).

Ispezionandolo con `cat`, il terminale mostra un output che assomiglia a un dump esadecimale (offset, coppie di byte, colonna ASCII a destra). Questo formato — offset a 8 cifre esadecimali seguito da coppie di byte e rappresentazione ASCII — è la firma caratteristica dell'output di `xxd`, lo strumento standard per la visualizzazione/dump esadecimale di file binari su Linux.

## Tecnica

Si tratta di una **decodifica a strati**: il contenuto reale del file è stato prima codificato in base64, poi il risultato salvato/mostrato come dump esadecimale (`xxd`). Per risalire al contenuto originale occorre invertire i passaggi nell'ordine opposto:

1. Interpretare il dump esadecimale per ricostruire i byte ASCII originali (che sono già leggibili nella colonna di destra dell'output `xxd`, ma vanno letti come stringa base64).
2. Decodificare quella stringa da base64 a testo semplice.

La colonna ASCII destra del dump xxd è già la stringa base64 leggibile — non serve nemmeno reinvertire manualmente i byte esadecimali, xxd la mostra già decodificata a fianco. Il passo restante è un singolo `base64 -d`.

## Sfruttamento

1. Lettura del file, che restituisce output in formato dump esadecimale:

```bash
cat transmission.dat
```
```text
00000000: <REDACTED_HEX_DUMP>
00000010: <REDACTED_HEX_DUMP>
```

2. Riconoscimento del pattern: la colonna a destra del dump è già la rappresentazione testuale (ASCII) dei byte esadecimali a sinistra, e forma una stringa base64 (il carattere finale reso come punto da xxd corrisponde al newline non stampabile).

3. Decodifica base64 della stringa ricostruita:

```bash
echo "<stringa_base64_ricostruita>" | base64 -d
```

## Risultato

Il file "di trasmissione" nascondeva, dietro un doppio strato di codifica (base64 rappresentato come dump esadecimale), la credenziale in chiaro dell'account successivo. Il valore letterale non viene riportato in questa versione.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub, in conformità con la dottrina BreachLab: insegna il metodo (riconoscimento del formato xxd, decodifica base64 a catena) senza riportare il dump esadecimale completo né la password risultante, che permetterebbero di saltare direttamente alla soluzione.

## Crediti

Livello e piattaforma: BreachLab (breachlab.org) — Ghost Track. Se questo writeup genera revenue, parte del ricavato va devoluta secondo la dottrina "if it earns, give back" di BreachLab.
