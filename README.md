# Optimizare calcul matriceal

## Cuprins

- [Specificații hardware și software](#specificații-hardware-și-software)
- [Implementări](#implementări)
  - [solver_neopt.c](#solver_neoptc)
  - [solver_opt.c](#solver_optc)
  - [solver_blas.c](#solver_blasc)
- [Bonus — Zen 2 Renoir](#bonus--zen-2-renoir)
- [Rezultate și grafice](#rezultate-și-grafice)
- [Prompturi LLM utilizate](#prompturi-llm-utilizate)

---

## Specificații hardware și software

### Arhitectura primară — Intel Haswell (cluster)


| Specificație          | Valoare                          |
| --------------------- | -------------------------------- |
| **CPU**               | Intel Xeon E5-2640 v3            |
| **Arhitectură**       | Haswell                          |
| **Dimensiune proces** | 22 nm                            |
| **Frecvență**         | 2.6 GHz (base) → 3.5 GHz (boost) |
| **RAM**               | 64 GB DDR4 ~2133 MHz             |
| **Bandwidth memorie** | 59.7 GB/s                        |
| **Compilator**        | GCC 14.3.1                       |


**Cache-uri** (per nod NUMA, 8 core-uri):


| Nivel | Tip         | Dimensiune         | Asociativitate | Cache line |
| ----- | ----------- | ------------------ | -------------- | ---------- |
| L1d   | Data        | 32 KB × 8 = 256 KB | 8-way          | 64 B       |
| L1i   | Instruction | 32 KB × 8 = 256 KB | 8-way          | 64 B       |
| L2    | Unified     | 256 KB × 8 = 2 MB  | 8-way          | 64 B       |
| L3    | Unified     | 20 MB × 1          | 20-way         | 64 B       |


> **Notă:** clusterul conține două noduri NUMA (2 sockete). Datele de mai sus se referă la un singur nod.

---

## Implementări

### solver_neopt.c

Traducerea directă a formulei în cod C, fără nicio optimizare:

```
C = Aᵀ · B
D = C · Cᵀ         (D este simetrică — se calculează doar triunghiul superior)
y = Σᵢ D · linie(C, i) + x
```

Buclele triple standard cu indexare `arr[i*N+j]`, fără reordonare sau acumulatori.

---

### solver_opt.c

Pornind de la varianta neoptimizată, s-au aplicat succesiv următoarele optimizări:

#### 1. Reordonarea buclelor pentru `C = Aᵀ · B`

Ordinea originală `i, j, k` accesează `A[k*N+i]` cu stride `N` — complet non-secvențial.  
Schimbând în ordinea `k, i, j`, valoarea `A[k*N+i]` devine o constantă pentru toată bucla internă (`a_ki`), iar `B` și `C` sunt parcurse secvențial, maximizând reutilizarea cache line-urilor.

Pentru celelalte două operații (`D = C·Cᵀ` și bucla `y`), ordinea standard era deja optimă — ambele rânduri parcurse sunt contigue în memorie.

> **Câștig:** ~6 s pe matricea 1200×1200 față de `neopt`.

#### 2. Pointer increments

Indexarea `arr[i*N+j]` implică o înmulțire și o adunare la fiecare iterație pentru calculul adresei. Înlocuind cu `*p++`, adresa se avansează cu o singură adunare pe iterație. Aplicat în toate cele trei operații.

> **Câștig:** ~2 s suplimentar față de pasul anterior.

#### 3. Utilizarea registrelor

Cuvântul cheie `register` a fost folosit în trei contexte distincte:

1. **Pointeri de parcurgere** (`pA_k`, `pB`, `pC`, `pCi`, `pD_r` etc.) — pointerii sunt citiți și incrementați la fiecare iterație; `register` elimină load/store-ul repetat de pe stivă și îi menține în registre fizice.
2. **Constante hoistate** (`a_ki = pA_k[i]`) — valoare fixă pe durata buclei interne, calculată o singură dată și păstrată în registru în loc să fie recalculată la fiecare iterație.
3. **Acumulatori multipli** (`s0..s3`, `y0..y3`) — scrierile în memorie (`D[...]`, `y[r]`) sunt reduse la una singură per (i,j), după terminarea buclei interne. Combinat cu unrolling, permit exploatarea ILP.

#### 4. Loop unrolling ×4 cu ILP

Un singur acumulator creează un lanț serial de dependențe: iterația `n+1` nu poate începe până nu se termină adunarea FP din iterația `n`. Folosind **4 acumulatori independenți** (`s0..s3`), unitățile FP pot executa instrucțiunile în paralel.

S-a ales factorul 4 deoarece arhitectura oferă **16 registre YMM** (`YMM0–YMM15`). Buclele interne folosesc ~7–8 registre FP simultan, încadrându-se confortabil în limită și evitând register spilling.

#### De ce nu s-a aplicat cache blocking?

Analizând cu Cachegrind, LLd miss rate pentru N=1200 pe Haswell este **0.0%** — toate datele active intră în L3. Implementarea cache blocking-ului nu ar fi adus un câștig măsurabil pe această arhitectură.

---

### solver_blas.c

Apeluri către funcții BLAS optimizate pentru arhitectura țintă:


| Operație                 | Funcție BLAS  |
| ------------------------ | ------------- |
| `C = Aᵀ · B`             | `cblas_dgemm` |
| `D = C · Cᵀ` (simetric)  | `cblas_dsyrk` |
| `y = D · v` (D simetric) | `cblas_dsymv` |
| `y = y + x`              | `cblas_daxpy` |


---

## Bonus — Zen 2 Renoir

### Specificații


| Specificație          | Valoare                                 |
| --------------------- | --------------------------------------- |
| **CPU**               | AMD Ryzen 5 4600H (6 cores, 12 threads) |
| **Arhitectură**       | Zen 2 (Renoir)                          |
| **Dimensiune proces** | 7 nm                                    |
| **Frecvență**         | 3 GHz (base) → 4 GHz (boost)            |
| **RAM**               | 16 GB (2 × 8 GB) DDR4-3200 CL22         |
| **Bandwidth memorie** | 51.2 GB/s                               |
| **Compilator**        | GCC 15.2.1                              |


**Cache-uri** (per core unde nu e specificat altfel):


| Nivel | Tip         | Dimensiune      | Asociativitate | Cache line | Sharing          |
| ----- | ----------- | --------------- | -------------- | ---------- | ---------------- |
| L1d   | Data        | 32 KB           | 8-way          | 64 B       | per core         |
| L1i   | Instruction | 32 KB           | 8-way          | 64 B       | per core         |
| L2    | Unified     | 512 KB          | 8-way          | 64 B       | per core         |
| L3    | Unified     | 4 MB × 2 = 8 MB | 16-way         | 64 B       | shared (6 cores) |


### Comparație cu Haswell


| Caracteristică        | Haswell   | Zen 2 Renoir |
| --------------------- | --------- | ------------ |
| Frecvență boost       | 3.5 GHz   | 4.0 GHz      |
| L2 per core           | 256 KB    | 512 KB       |
| L3 total              | 20 MB     | 8 MB         |
| Fereastră de execuție | 192 µops  | 224 µops     |
| Memorie               | DDR4-2133 | DDR4-3200    |


### Problemă identificată

Varianta optimizată pentru Haswell, rulată pe Zen 2 cu N=1200, genera **LLd misses** semnificative în Cachegrind. Cauza: cele 3 matrice active (C, D, B) ocupă prea multă memorie pe Zen 2 (acesta este un APU — L3-ul a fost redus pentru a lăsa spațiu iGPU-ului).

### Soluție: cache blocking

S-au adăugat blocuri calibrate pe L2=512 KB (un rând = N×8 = 9.6 KB pentru N=1200):


| Operație     | Block size                 | Ocupare L2                        |
| ------------ | -------------------------- | --------------------------------- |
| `C = Aᵀ · B` | `BLOCK_1 = 40` rânduri     | 40 × 9.6 KB = 384 KB < 512 KB     |
| `D = C · Cᵀ` | `BLOCK_2 = 20` rânduri × 2 | 2 × 20 × 9.6 KB = 384 KB < 512 KB |
| Bucla `y`    | `BLOCK_1 = 40` rânduri     | 40 × 9.6 KB = 384 KB < 512 KB     |


Blocurile active rămân în L2 pe durata iterațiilor, evitând accesul la RAM.

> **Câștig:** ~1.2 s față de varianta fără blocking pe N=1200 pe Zen 2.

---

## Rezultate și grafice

Graficele "grafic_haswell.png" și "grafic_zen2.png" arată timpii de execuție pentru toate implementările pe matricele de dimensiuni 400, 600, 800, 1000 și 1200. Se observă că timpii de execuție pentru primele trei matrice sunt mai scăzuți pentru Zen 2, iar pentru matricele mai mari apar accese la memoria RAM, iar timpii încep să se egalizeze.

În schimb, pentru variantele optimizate se vede avantajul de cache L2 și frecvență pe care îl are Zen 2 față de Haswell.


**Analiza Cachegrind** (N=400, ambele arhitecturi):

- LL miss rate: **0%** — toate datele intră în cache la finalul execuției
- D1 miss rate: **~5.1%** — datele nu încap complet în L1, ceea ce este așteptat
- Valgrind confirmă absența memory leaks pentru toate implementările
