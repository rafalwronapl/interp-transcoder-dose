# A/B — aktualny stan wykonania
Stan: 2026-11-02, godzina aktualizacji jest zapisana w STATUS.json. Jest to zapis dowodów, nie pomiar procentu czasu.

Przygotowanie: cztery kryteria po 25% — zakres, kod/dane, sprawdzenia offline, niezależny odbiór literalnego pakietu. Wykonanie: licznik rzeczywistych zadań lub operacji. Wynik negatywny może być wykonany w 100%. Nie uśredniać nierównych wierszy; współdzielonych pomiarów nie liczyć ponownie.

| Etap | Przygotowanie | Wykonanie | Rzeczywisty wynik / ograniczenie |
|---|---:|---:|---|
| Inwentaryzacja i korpus |100%|100%|Tożsamości, ekspozycja, donory i tokenizacja odebrane; historia zachowana.|
| A: pojedynczy pomiar techniczny |100%|1/1|Odebrany; później zaimportowany bez ponownego pomiaru.|
| A: własny FIT r0 |100%|100%|448 dokumentów, 477 nowych pełnych forward +5 suffix; import1 osobno. Odbiór i aktualna adopcja infrastruktury PASS.|
| B: własny FIT i bazy |100%|100%|128 dokumentów, 36 dopasowanych komórek, obie kwalifikacje; odzyskano wszystkie poprawne cache po zachowanym błędzie. Odbiór PASS.|
| B: techniczna kwalifikacja tail |100%|160/160 operacji|152F+8B, cztery rekordy FIT, odebrana; nie wynik hipotezy.|
| Kalibracja rodzin v2 |100%|180/180 scenariuszy|A12835/36, A25636/36; B12846/54, B25652/54 PASS. Wszystkie porażki zachowane.|
| A: kwalifikacja N |100%|100%|N128 niekwalifikowane; N256 kwalifikowane. Nie jest to spełnienie celu mocy.|
| B: pierwotna kwalifikacja N |100%|100%|Oba N niekwalifikowane; niezależny odbiór i canonical PASS. Bramka nie dowodzi automatycznie empirycznego FWER>.05.|
| B: pierwotna precyzja |100%|8/8 scenariuszy|2 PASS,6 FAIL, odbiór PASS wyniku negatywnego.|
| B: prospektywna precyzja v6 |100%|8/8 scenariuszy|8 PASS,16000 syntetycznych zbiorów; nie zastępuje niezaliczonej rodziny B.|
| A: PILOT |100%|4480/4480F|32 bloki/640 dokumentów; odbiór i assembly PASS.|
| A: pierwotny selektor mocy |100%|100% zadania|720 zapisanych replikacji; dokładne reguły zatrzymania wykazały niemożność spełnienia celu. Odbiór negatywny PASS.|
| A: fixed256 TEST po poprawce zakresu |100%|35840/35840F|256 bloków/5120 dokumentów, odebrany. Po błędzie telemetrycznym501 cache wykorzystano bez powtórzeń. Brak zapewnienia80% mocy.|
| A: główne wyniki |100%|100%|A1 i A3:Holm.003; A2:IUT/Holm1, brak odwrócenia. A3 oznacza szkodę U0 dla badanego T5. Jedno r0,99% przedziały punktowe. Wyniki i surowe pomiary niezależnie sprawdzone.|
| A:30 komórek dodatkowych |100%|1/1 analiz|Zakończona i formalnie APPROVED b13f0013; 30 opisowych komórek/r0/86statystyk,0modeli. Bez15FIT i nowych hipotez.|
| A: kalibracja stabilności |100%|18/18 scenariuszy|14 PASS,4 lognormalne FAIL; pełna integralność72tys. artefaktów i odbiór negatywny PASS.|
| A: dodatkowe15 FIT |draft, niedopuszczony|0 pomiarów|Nie uruchamiać pod niezaliczoną kwalifikacją stabilności; osobny wynik jednego r0 pozostaje ważny w swoim zakresie.|
| B: PILOT opisowy |100%|19968/19968 operacji|192 dokumenty,19776F+192B; odbiór i assembly PASS. Bez awansu do pierwotnej inferencji.|
| B: pierwotny selektor/TEST rodziny |niedopuszczony|0 pomiarów|Oba N nie przeszły bramki; nie fabrykować dodatniej kwalifikacji.|
| B: fixed256 TEST opisowy |100%|159744/159744 operacji|1536 dokumentów,158208F+1536B, exit0 i niezależny odbiór3a247b07 APPROVED. Bez awansu do pierwotnej inferencji.|
| B: transfer, bazy, endpointy |100% pomiarów|100% pomiarów|Zawarte w tym samym TEST; bez dodatkowego naliczania. Wszystkie metody/dawki i negatywne komórki zachowane.|
| B: końcowa analiza opisowa |100%|1/1 analiz|288komórek/36endpointów/5kontrastów/12TCc1CI, formalnie APPROVED3df69e80. Cel szerokości niespełniony projected/when2.431pp>2pp; pierwotna rodzina nadal niekwalifikowana.|
| Qwen: FIT |100%|284/284F|Własne128MAP+128U, ridge.01/rank8; niezależny odbiór i canonical PASS.|
| Qwen: PILOT |100%|1024/1024F|256 dokumentów/32 bloki; niezależny odbiór i canonical PASS.|
| Qwen: fixed256 TEST |100%|8192/8192F|256 bloków/2048 dokumentów, exit0, wszystkie surowe rekordy i macierz kontrastów niezależnie odebrane.|
| Qwen: analiza końcowa |100%|100%|1999 losowań wykonanych raz. T5−.18191558,99%CI[−.24935525,−.11085584],Bonf2p1:brak replikacji szkody. T2+.25759566 opisowa. Focused i formalny odbiór APPROVED5713f19a.|
| Llama: FIT |100%|284/284F|Własny FIT, niezależny odbiór i canonical PASS.|
| Llama: PILOT |100%|1024/1024F|256 dokumentów/32bloki, exit0 i niezależny odbiór790ad64. Bez ponownego FIT.|
| Llama: fixed256 TEST |100%|8192/8192F|2048dokumentów/256bloków,exit0 i niezależny odbiór5f168083. Własny zamrożony FIT, brak retuningu po Qwenie.|
| Llama: analiza końcowa |100%|1/1 analiz|T5+.778263,99%CI[.669128,.890662],Bonf2p.002;T2−.406790 opisowa. Focused i formalny odbiór APPROVED0e734baf.|
| Osobne dostawy dowodów |częściowo zakończone|3 dostawy odebrane|A FIT, A PILOT/negatywny selektor i B FIT odebrane. B tail i nowe wyniki wymagają dalszego domknięcia/dostaw; bez wag i zbędnych pełnych cache.|
| Artykuły |osobne zadanie Roota|A roboczy dostarczony|A_v5 wybrane Gemma/Llama: reviewed working scope,nie public-ready. B artykuł/pakiet prowadzi Root z ukończonej analizy; nie deklarować dostawy przed rzeczywistymi plikami/review.|

| A_crossed diagnostyka |100%|320/320headF|32konteksty,0fullLLM/0B; focused+formal APPROVEDd5a34676,wszystkie przekątne PASS.|
| C zamiany P/U |100%|22720/22720NOWYCHheadF|2304konteksty/23040logicznych odczytów,320jawnychadopcji,0fullLLM/0B/refit/bootstrap. FocusedreviewAPPROVED; formalcompletionAPPROVEDe82f4c74.|

| C2 Qwen świeże FIT/holdout |100%|5020/5020F|896capture+28kontroli+4096head,3świeżeFIT,forecast przedfinitehead; formalnyodbiór APPROVEDab1c6583.|
| C2 Gemma świeże FIT/holdout |100%|8604/8604F|1280capture+28kontroli+7296head,3świeżeFIT,forecast przedfinitehead; formalnyodbiór APPROVED1474ff00.|
| C2 oracle-conditioned scoring |100%|2/2analiz|Oba formalnieAPPROVED:Qwen1146/1152znaków;Gemma2292/2304znaków+ranking1146/1152. Każde99.48%,N32wspólnebloki/zależnepary/oracleD. Brak gwarancji populacyjnej i wdrożenia bezD.|

C2 allauthorizedmeasurements/scorings complete and independentlyaccepted. No native/CPUjobs queued; priornegativecriteria preserved. No oldC/cache reruns. Root ownsarticle/deliveryfollowups.


Dowody: STATUS.json, HANDOFF.md, poszczególne pre_run/completion snapshoty i niezależne review. Żywy raport użytkownika: C:/Users/rafal/Downloads/Dorobek_programu_badawczego_2026-10-22.md. Stara tabela ETAPY_I_POSTEP.md jest zachowanym historycznym checkpointem przygotowań; bieżący stan jest tutaj.
