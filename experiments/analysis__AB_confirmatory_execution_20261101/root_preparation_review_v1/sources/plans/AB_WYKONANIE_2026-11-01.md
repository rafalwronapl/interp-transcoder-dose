# Zlecenie wykonawcze A/B — 1 listopada 2026

Użytkownik zlecił przygotowanie wszystkich opisanych eksperymentów A/B, następnie wykonanie przez agenta Sol. To nowe upoważnienie zastępuje dawny STOP w zakresie tych badań, nie innych kampanii. Wersja robocza wykonawcza, nie zgoda pre-run. Źródło naukowe: papers/AB_v4_20261101/PLAN_POTWIERDZEN_A_B.md oraz osobne plany A/B. Zachować dokładnie A1–A3 i B1–B3. Nie zmieniać historycznych źródeł, wyników, progów ani cache.

## Produkty i własność

Nowy katalog: analysis/AB_confirmatory_execution_20261101/. Kod wyłącznie ab_confirmatory_20261101/. Wszystkie źródła historyczne tylko do odczytu. Sol odpowiada za implementację, materializację i wykonanie; root za ten projekt i nadzór. Osobny agent recenzuje każdy rzeczywisty snapshot przed pomiarami i po wynikach. Autor nie wystawia własnego approval. Wspólny filesystem nie daje zaślepienia.

Wymagane pliki: PROTOCOL_A.md, PROTOCOL_A_FIT.md, PROTOCOL_B.md, PROTOCOL_B_CONTROLS.md, corpus/exposure_manifest.json, model_identity.json, sample_size_spec.json, statistical_validation.json, operation_schedule.json, cost_estimate.json, STATUS.json, HANDOFF.md oraz osobne kontrakty/snapshoty/recenzje etapów. Każde pole nieustalone ma jawny status, bez pozornej gotowości.

## A — minimum i stabilność

Gemma-3-1B, dokładny lokalny checkpoint, ostatnia gałąź MLP, końcowy token; operator/recepta ridge/SVD według dodatku A v4. Nowe, rozłączne bloki FIT_MAP/FIT_U/FIT_EXT/PILOT/TEST. Ranga8, lambda0.01, globalne RMS i centrowanie według zapisanej recepty. P wspólna w porównaniu U0/Uctrl/U2/U5; FIT_EXT wspólny między ramionami, ta sama liczba dokumentów. TEST T0/T2/T5/T6/T7, wszystkie strony/distractory. A1 transfer T6/T7 U2 vs Uctrl; A2 przeciwny ranking V i L dla U5/U2 na T5; A3 szkoda U0 względem P na T5. Jedna rodzina trzech hipotez, Holm; A2 intersection–union. Oracle dostęp do prawdziwej delty wyłącznie dla ramion naprawy.

Stabilność to oddzielny moduł, nie nowe główne sukcesy A. Zrealizować niezależne kohorty FIT i wspólny TEST dla oszczędności. Estymować każdy kontrast osobno dla każdej realizacji, średnią między realizacjami i rozrzut; zachować wszystkie realizacje. Wnioskowanie musi resamplować niezależne kohorty FIT oraz wspólne bloki TEST jako skrzyżowane jednostki. Nie sumować wierszy jako niezależnych. Liczbę realizacji i rozmiary FIT ustalić na podstawie jawnych symulacji/wykonalności przed pomiarami. Wielokrotne seedy deterministycznego fitu nie są replikacją.

## B — minimum i kontrole

Gemma-3-270M/L15, dokładny publiczny medium TC z dawnego PRON. Nowe lokalnie niewykorzystane pary imion, so/when z równymi wagami, dodatkowy jeden nowy literalny szablon transferu wybrany przed PILOT. Full/projected, c={0.05,0.1,0.25,0.5,1,2}, kierunek tylko z FIT. TC/frozen-mask/Taylor/zero na tych samych przypadkach. B1 full c1 lepszy od zero i Taylor; B2 pooled relative RMS c1 mniejszy niż c0.05; B3 projected c1 lepszy od obu baz. Trzy hipotezy/Holm, koniunkcje IUT. Raportować bezwzględny RMS, RMS sygnału oraz względny błąd osobno na szablon/operator; sama przewaga baz nie potwierdza dawnych5–8%.

Dodatkowe bazy: średnia natywnej delty w komórce FIT i centrowana regularizowana mapa różnicy wejścia do delty wektorowej, z odczytem przez ten sam natywny suffix. Ustalić dopasowanie/skalowanie/regularyzację przed PILOT; ewentualny SELECT rozłączny z TEST. Brak etykiet TEST w prognozie. Jawny dodatkowy nadzór i koszty względem publicznego TC; bez deklaracji wyrównania kosztu jego pretrainingu. Porównania dodatkowe raportować opisowo z niepewnością, bez awansu do B1–B3.

Zapisać e0=TC(x)−N(x), e1=TC(x+delta)−N(x+delta), deltę, energie i człon mieszany; osobno bias/kowariancję między kontekstami. Sprawdzić dokładną tożsamość e_delta=e1−e0. Suffix i margines mierzyć oddzielnie; rozkład wektora nie jest rozkładem błędu readout. Zachować kontrole projected i linear-readout. Nie zakładać z góry mechanizmu znoszenia.

## Kolejność wykonania i bramki

1. Bez modeli: odnaleźć istniejące adaptery i pełną tożsamość lokalnych artefaktów. Materializować literalne korpusy, rozłączność lematów/imion i hierarchię bloków wobec dawnych korpusów, tokenizację i test donorów. Nie powtarzać dawnych wyników jako nowych. Freeze danych/źródeł przed użyciem.
2. Bez modeli: zaimplementować statystykę sparowanych bloków, IUT/Holm, brakujące komórki/zera/NaN/Inf, politykę wznowień i corruption fail-closed. Nierozstrzygniętych testów nie usuwać z rodziny. Nie zastępować niekorzystnych bloków. Zdefiniować kryteria N i maksima kosztowe przed PILOT, z naukowym uzasadnieniem celów precyzji/mocy. Symulacje mają obejmować H0, częściowe H0, ciężkie ogony, heterogeniczność i współdzielenie FIT/TEST. Raportować błąd Monte Carlo. N nie wybierać ze znaku wyników ani z odległości starego efektu od progu. Jeśli wymagania są niewykonalne, zapisać to zamiast fałszować gotowość.
3. Niezależny odbiór przygotowania i ograniczonego PILOT: sham, niezerowe kontrole, hook/pozycja, osiągalność, parity pełnego forward vs suffix, precyzja małych delt, koszt i restart. PILOT rozłączny, jego rozrzut służy wyłącznie zamrożonej regule N. Techniczne poprawki wersjonować przed TEST.
4. Freeze wybranego N, P/U/kierunków/baz, prognoz, wszystkich warunków i harmonogramu; kolejny rzeczywisty pre-run review. Uruchamiać tylko przez research_checks launch. Jeden worker modelowy naraz; zachować Neuron Lab i cudze procesy. Długie procesy ukryte, osobne logi/PID/ledger, atomowy lock oraz wznawialny cache związany tożsamościami. Nie powtarzać durable pomiarów.
5. Wykonać A, B i przygotowane moduły dodatkowe sekwencyjnie w zakresie odebranych kontraktów; nie czekać na offline analizę, gdy kolejny etap jest niezależny i odebrany. Każdy etap ma niezależny końcowy audyt. Aktualizować stały raport Downloads/Dorobek_programu_badawczego_2026-10-22.md po każdym raportowanym etapie; zachować historię i negatywne wyniki. Artykuły zmieniać dopiero na podstawie ukończonych zrecenzowanych wyników.

Bez chmury i płatnych zewnętrznych dostawców. Upoważnienie użytkownika obejmuje przygotowanie oraz lokalne wykonanie po spełnieniu wymaganych recenzji, bez kolejnych pytań o tę samą zgodę. Sam ten dokument nie zastępuje kodu, liczbowej specyfikacji N, pilota lub niezależnej recenzji. Wszystkie pola potrzebne do konkretnego etapu muszą być wypełnione przed jego uruchomieniem.
