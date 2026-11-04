# A i B — stan przygotowania wykonawczego

Aktualizacja: 2026-11-01, 12:47, Europe/Warsaw. Procenty dotyczą przygotowania programów, testów i recenzji, nie wykonania badań. Są przybliżeniem roboczym, a nie procentem czasu ani liczbą potwierdzonych hipotez. Artykuły aktualizujemy po zakończeniu badań.

| Etap przygotowania | Gotowość | Dowód / pozostała praca |
|---|---:|---|
| 1. Uruchamianie i pakiety kalibracji | 100% | Zmiana obsługi zerowego budżetu modelowego niezależnie odebrana; oba pakiety kalibracji zatwierdzone. Kalibracja precyzji B faktycznie działa. |
| 2. Krótki test techniczny B | 100% | Gotowy literalny pakiet152 forward/8 backward, testy integracyjne, pre-run APPROVED ba4c7f11…be21. W kolejce wykonawczej. |
| 3. Programy i pakiety A | 100% | APPROVED fb8a4124…dc364c; PILOT, TEST128/256,15FIT, współdzielony TEST do stabilności;5 testów. Rzeczywiste warunki dopuszczenia A odebrane:128 niedopuszczone,256 dopuszczone. |
| 4. Programy i pakiety B | 100% | APPROVED a0511313…38773; trzy literalne pakiety robocze, program rzeczywistego dopuszczenia i składania danych,6 testów. Rzeczywiste uruchomienie nadal wymaga wyników kalibracji i ukończenia testu technicznego. |
| 5. Integracja, dobór liczebności i końcowe analizy | 85% | Niezależny dobór A/B i składanie dopuszczenia zatwierdzone27caffb6…bb32b. Końcowe analizy główne i stabilności zatwierdzone470ef67a…9558f. Do końca: pakiety uruchomienia selektora oraz raportów dodatkowych, ich testy i recenzja. |

Nie utożsamiać gotowych programów z gotowymi wynikami. Przyszłe pakiety wykonawcze mają być składane z rzeczywistych zakończonych etapów i ich niezależnych recenzji; brak przyszłego wyniku nie jest zastępowany sztucznym potwierdzeniem.

## Wykonanie i kolejka

- A FIT i B FIT ukończone, niezależnie odebrane. Historia błędu odniesienia B, poprawki i kosztów zachowana.
- Działa kalibracja rodziny testów oraz kalibracja precyzji B. Dokładne liczniki sprawdzać w aktualnych plikach wynikowych; nie w tym raporcie przygotowań.
- Wspólna blokada `research_worker.lock` jest zajęta przez kalibrację precyzji B. Inny agent nie omija tej blokady.
- Rzeczywisty PILOT A ma pre-run APPROVED1c9b7204…f3931:640 pełnych przebiegów i3840 lokalnych odczytów,0 backward. Automatycznie czeka na wolny slot; jeszcze nie uruchomiony.
- Po zwolnieniu blokady najpierw zatwierdzony krótki test B, następnie zatwierdzony PILOT A; kolejne etapy według faktycznej gotowości i dopuszczenia. Kalibracja stabilności A nie powinna ponownie zablokować gotowego PILOT.
- A jest niezależne od wyniku krótkiego testu B: po zakończeniu jego procesu i zwolnieniu slotu A może ruszyć również przy negatywnym wyniku B, bez powtarzania B.
- Właściwy TEST wymaga wyników PILOT i zatwierdzonego doboru liczebności. Nie uruchamiać obu wariantów128 i256.
- Wynik negatywny lub brak dopuszczalnej liczebności pozostaje wynikiem; bez przeliczania do uzyskania pozytywnego rezultatu.

## Podział odpowiedzialności

Root: B i integracja. Astra przygotowująca: A, dobór liczebności i raporty dodatkowe. Osobna Astra: niezależna recenzja. Sol: wykonanie, rzeczywiste liczniki, przekazywanie wyników do odbioru i aktualizacja raportu użytkownika.

## Główne dowody

- `A_remaining_preparation/HANDOFF.md`, `astra_preparation_review/A_remaining_v2/review.json`.
- `B_remaining_preparation/HANDOFF.md`, `B_remaining_preparation/review_astra.json`.
- `B_tail_qualification_v1/pre_run_review_astra_v1.json`.
- `eligibility_synthesis_v5/A_actual_v1/review_astra.json`.
- `final_analysis_preparation_v5/review_astra_v2.json`.
- Stały raport użytkownika: `C:/Users/rafal/Downloads/Dorobek_programu_badawczego_2026-10-22.md`.
