<!-- CURRENT_EXECUTION_TABLE_POINTER -->
Biezaca tabela wykonania: [ETAPY_WYKONANIE_AKTUALNE_20261101.md](ETAPY_WYKONANIE_AKTUALNE_20261101.md). Ponizej zachowany historyczny checkpoint przygotowan.

# A i B — pełna kolejka i postęp

Stan 2026-11-01, aktualizacja po materializacji pakietu A/r0 FIT; przed jego niezależnym odbiorem/uruchomieniem. To odczyt stanu, nie automatyczny panel live.

Root przygotowuje protokoły/metody i nadzoruje. Sol implementuje, testuje, uruchamia i zapisuje wyniki. Osobny recenzent odbiera rzeczywiste pakiety. Praca przechodzi do kolejnego gotowego etapu bez oczekiwania na użytkownika.

## Jak liczymy

Przygotowanie: cztery punkty po25% — (1) określony zakres/recepta etapu, (2) kod i wymagane dane/pakiet, (3) wymagane sprawdzenia offline, (4) niezależny odbiór konkretnego pakietu. 25% oznacza ustalony kierunek i zakres, NIE kompletny protokół liczbowy. Sam draft nie daje gotowości do uruchomienia. Dla zakończonych przygotowań dokumentacyjnych stosujemy odpowiednie dowody/odtworzenie zamiast modelowego kodu. Wykonanie: rzeczywisty licznik operacji lub zakończonych zadań. Wynik negatywny może być100% wykonany i niezaliczony naukowo.

Nie uśredniać poniższych wierszy jako procentu czasu: etapy mają różne koszty, a niektóre dzielą dane. Dotychczasowy gruby licznik A2/6,B2/6=33% dotyczył odebranych kamieni milowych; tabela daje dokładniejszy podział, nie nowy pomiar całkowitego nakładu pracy.

| Etap | Co dokładnie obejmuje | Przygotowanie | Wykonanie | Status / co pozostało |
|---|---|---:|---:|---|
| Wspólne: inwentaryzacja | Modele, artefakty, adaptery i historyczna ekspozycja danych |100%|100%|6692 źródła; tożsamości lokalnych modeli/TC zapisane.|
| Wspólne: korpus | Nowe bloki, rozłączność, donory, tokenizacja |100%|100%|14848 dokumentów,1376 bloków; niezależny odbiór leksykalny v3.|
| A: pierwszy pomiar techniczny | Jedna naturalna aktywacja Gemmy1B, kontrola hooków/cache |100%|100% (1/1)|Odebrany i dostarczony do osobnego A; nie test hipotezy.|
| Statystyka: kalibracja v1 | Pierwotna procedura,16 scenariuszy marginalnych |75%|75% (12/16)|5 zaliczonych,7 niezaliczonych bramek; zachować także porażki. Nie gotowość TEST.|
| Statystyka: kalibracja v2 | Konserwatywne p, całe rodziny, częściowe H0 |75%|19% (34/180)|33 zaliczone,1 niezaliczona bramka; proces trwa. Brak zaliczenia bramki nie zawsze dowodzi nadmiernego rzeczywistego błędu.|
| Statystyka: dobór N/moc/precyzja | Moc całej rodziny≥80%, wspólna precyzja B≥90%, stabilność FIT |25%|0%|Root dopracowuje regułę; Sol wdroży i skalibruje. Cele i liczebność muszą przejść odbiór przed PILOT.|
| A: główny FIT r0 | P oraz U0/Uctrl/U2/U5;448 dokumentów,48 bloków |75%|0% nowych operacji|Pakiet i7 testów gotowe, protokół roota zapisany; następnie recenzja/start.477 nowych pełnych forwardów+5 lokalnych odczytów;1 wcześniejszy import osobno.|
| A: PILOT | Nowe32 bloki; kontrole i rozrzut do zamrożonej reguły N |50%|0%|Kod ścieżki testowany na małym losowym modelu; konkretny kontrakt, reguła N i odbiór jeszcze potrzebne.|
| A: zamrożenie TEST | N, recepta analizy, P/U, prognozy i harmonogram |25%|0%|Zależy od odebranego FIT/PILOT i kalibracji.|
| A: główny TEST | A1 transfer U2 vs Uctrl naT6/T7; A2 przeciwny ranking wektor/odczyt U5/U2 naT5; A3 szkoda U0 vs P naT5 |50%|0%|Jedna wspólna kampania,3 hipotezy/Holm; nie trzy niezależne zbiory. Kod ogólny istnieje, finalny pakiet TEST niegotowy.|
| A: stabilność FIT |15 dodatkowych niezależnych FIT,16 razem z r0; wspólny TEST |25%|0%|Korpus przygotowany; wymagane kryterium precyzji, kalibracja zależności FIT×TEST i osobny odbiór.|
| A: analiza i odbiór | Efekty, niepewność, wszystkie ramiona, koszty, recenzja |25%|0%|Po rzeczywistych wynikach; hipotezy pozostają zamrożone.|
| B: FIT i techniczne kontrole | Kierunek projekcji z FIT, zgodność TC/native, suffix i numeryka |25%|0%|Moduły native/TC i testy jednostkowe istnieją; pełnego workera B/harmonogramu jeszcze brak.|
| B: PILOT | Nowe32 pary imion, rozrzut/koszt/precyzja |25%|0%|Po FIT oraz odebraniu reguły N i konkretnych kontroli.|
| B: zamrożenie TEST | N,kierunek,bazy,procedura analizy,prognozy i harmonogram |25%|0%|Zależy od FIT/PILOT i kalibracji; świeży odbiór.|
| B: główny TEST | B1 full c1 vszero/Taylor; B2 relativeRMS c1 vsc.05; B3 projected c1 vszero/Taylor |25%|0%|Jedna kampania,3 hipotezy; Gemma270M/L15,so/when,6 dawek.|
| B: transfer | Dodatkowy wcześniej wybrany szablon, te same zasady |25%|0%|Moduł dodatkowy; nie zamienia się w główną hipotezę po wynikach.|
| B: proste uczone bazy | Średnia natywnej delty i ridge, nadzór tylko FIT |25%|0%|Potrzebne dokładne reguły komórek/skali/kosztu oraz implementacja i odbiór.|
| B: diagnoza błędu | e0/e1, delta, energie/cross-term, bias/kowariancja; odczyt osobno |25%|0%|Tożsamość endpointów ma test jednostkowy; pełny zapis/analityka i odbiór jeszcze potrzebne.|
| B: analiza i odbiór | Błędy absolutne/względne/sygnał, transfer,bazy,koszt,recenzja |25%|0%|Po pomiarach; dodatnie i ujemne wyniki razem.|
| A+B: nowe wersje artykułów i dostawy | Aktualizacja na podstawie nowych odebranych wyników, osobne foldery i manifesty |25%|0% nowych wyników naukowych|Artykuły v4 już istnieją; techniczny pakiet A już dostarczony, nie oznacza zakończenia tej aktualizacji.|

## Dowody i ograniczenia

- Bieżące `STATUS.json`, `HANDOFF.md`, `A_fit_primary_v1/`, `single_capture_v1/`, `lexical_review/review_v3.json`.
- Liczniki kalibracji pochodzą z zachowanych wyników i raportu wykonawcy; postęp procesu może być nowszy od tej tabeli.
- Główne nowe pomiary hipotez A1–A3/B1–B3:0. Nie mylić starych wyników opisanych w artykułach z nową kampanią.
- Przygotowanie50% ścieżki A oznacza istniejący kod/dane ogólne, nie gotowy kontrakt PILOT/TEST. Tylko100% z właściwym niezależnym odbiorem umożliwia uruchomienie danego pakietu.
- Plan przyszłego artykułu o CLT między modelami jest odrębnym zapisanym kierunkiem, poza tą autoryzowaną kolejką pomiarów A/B.
