# Coach Carter (2005): streaming viewership, Netflix first

Research date: 2026-11-10. Labels: **VERIFIED** means the primary source file was opened and read. **REPORTED** means a secondary source states it. **ESTIMATE** means derived, with the math shown.

Primary files downloaded and parsed (openpyxl, every row searched for "coach carter"):
- All 7 Netflix "What We Watched" workbooks, H1 2023 through H1 2026. The xlsx links come from each report page on about.netflix.com:
  - [H1 2023](https://about.netflix.com/en/news/what-we-watched-a-netflix-engagement-report)
  - [H2 2023](https://about.netflix.com/en/news/what-we-watched-the-second-half-of-2023)
  - [H1 2024](https://about.netflix.com/en/news/what-we-watched-the-first-half-of-2024)
  - [H2 2024](https://about.netflix.com/en/news/what-we-watched-the-second-half-of-2024)
  - [H1 2025](https://about.netflix.com/en/news/what-we-watched-the-first-half-of-2025)
  - [H2 2025](https://about.netflix.com/en/news/what-we-watched-the-second-half-of-2025)
  - [H1 2026](https://about.netflix.com/en/news/what-we-watched-the-first-half-of-2026)
- The official Netflix Top 10 TSVs: [all-weeks-global.tsv](https://www.netflix.com/tudum/top10/data/all-weeks-global.tsv) and [all-weeks-countries.tsv](https://www.netflix.com/tudum/top10/data/all-weeks-countries.tsv). They cover the weeks from 2021-07-04 to 2026-11-08 and 94 countries.

## Netflix engagement reports: hours and views per half-year, and the cumulative sum

### Takeaway
"Coach Carter" appears **once** in 6 of the 7 published reports, always marked "Available Globally? = No" (a regional licence). It is **missing from H1 2025**, which means it had fewer than 50k views that period, or none.
- Cumulative hours, H1 2023 to H1 2026: **73.1M (VERIFIED sum)**.
- Cumulative views: **22.8M VERIFIED** for H2 2023 onward. Adding an ESTIMATE of about 9.2M for H1 2023 (that report gave no views) brings it to about **32.0M**.
- More than half of all reported hours (38.5M) came in H2 2025, when the film ranked **#100 of all movies** on Netflix.

### Cited Findings

| Period | Workbook row (sheet) | Hours viewed | Views | Rank* | Label |
|---|---|---|---|---|---|
| H1 2023 (Jan–Jun) | row 1022 (Engagement) | 21,000,000 | *not published* (≈9,200,000) | #1,016 of ~18,214 titles (TV and film combined) | Hours VERIFIED; views ESTIMATE |
| H2 2023 (Jul–Dec) | row 1008 (Film) | 7,500,000 | 3,300,000 | #1,002 film | VERIFIED |
| H1 2024 | row 1942 (Film) | 3,300,000 | 1,400,000 | #1,936 film | VERIFIED |
| H2 2024 | row 5472 (Film) | 300,000 | 100,000 | #5,466 film | VERIFIED |
| H1 2025 | — absent from the Movies sheet | <50k views (≈ <0.11M hours) | <50,000 | — | VERIFIED absent |
| H2 2025 | row 106 (Movies) | 38,500,000 | 16,900,000 | #100 film | VERIFIED (matches the earlier row-106 note) |
| H1 2026 | row 2245 (Movies) | 2,500,000 | 1,100,000 | #2,239 film | VERIFIED |
| **TOTAL** | | **73,100,000** | **22,800,000 verified (H2'23 onward); ≈32,000,000 with the H1'23 estimate** | | Sum |

*Rank = row number − 6. The data starts at row 7 and is sorted by views (by hours in H1 2023).

- Sources for the table: the [H1 2023 report](https://about.netflix.com/en/news/what-we-watched-a-netflix-engagement-report), [H2 2023](https://about.netflix.com/en/news/what-we-watched-the-second-half-of-2023), [H1 2024](https://about.netflix.com/en/news/what-we-watched-the-first-half-of-2024), [H2 2024](https://about.netflix.com/en/news/what-we-watched-the-second-half-of-2024), [H1 2025](https://about.netflix.com/en/news/what-we-watched-the-first-half-of-2025), [H2 2025](https://about.netflix.com/en/news/what-we-watched-the-second-half-of-2025) and [H1 2026](https://about.netflix.com/en/news/what-we-watched-the-first-half-of-2026). All are VERIFIED from the downloaded xlsx files.
- Runtime is listed as 2:17 (2.2833 h) in every report that has runtimes. The release-date cell is blank, which is normal for licensed titles. — [H2 2025 workbook](https://about.netflix.com/en/news/what-we-watched-the-second-half-of-2025)
- No duplicate entries: there is only one "Coach Carter" row per report. Three similar titles are different films and must NOT be summed:
  - "Carter // 카터" (2022 Korean action film)
  - "Get Carter (2000)"
  - "Coach Snoop" (a series)
  - — all 7 workbooks (VERIFIED)
- The 2025 H2 and 2026 H1 workbooks carry this footnote: "'Other Movies' and 'Other Shows' rows in this report capture total viewing from titles with <50k views". So absence means fewer than 50k views. — [H1 2026 workbook](https://about.netflix.com/en/news/what-we-watched-the-first-half-of-2026)
- What's on Netflix's tracker shows the same six rows and ranks. For H1 2023 it gives 9,200,000 views, which matches the hours ÷ runtime estimate below; it is not a figure Netflix published. — [What's on Netflix title page](https://www.whats-on-netflix.com/top-10-title-search/?title=Coach+Carter) (REPORTED)

### Inferences
- **H1 2023 views (ESTIMATE):** 21,000,000 h ÷ 2.2833 h ≈ 9.20M views. This uses the same method Netflix uses for "views" (hours ÷ runtime).
- **Views total:** 22.8M + 9.2M = **≈32.0M views (ESTIMATE)**.
- **H1 2025 ceiling:** at most 50k views × 2.2833 h ≈ 0.11M hours could be missing. The true cumulative total is therefore 73.1M to 73.2M hours.
- "Views" are hours ÷ runtime, not unique viewers. Treat 32M as viewing-equivalents, not people.
- The film was licensed regionally throughout (never "available globally"). The rise and fall from period to period follows the licence windows opening and closing. Without the H2 2025 relicence spike, interest was declining: 21.0 → 7.5 → 3.3 → 0.3 → 0 million hours.

### Gaps
- Netflix does not publish which countries made up each half-year figure.
- Viewing before 2023 is not in any engagement report. Netflix did not disclose half-year totals before H1 2023.

## Netflix Top 10: weeks, countries, peak rank, weekly hours

### Takeaway
Two **global** Top 10 weeks (both #9–#10 in Films (English)), totalling **13.45M hours**. In the **country** lists, the title charted in **exactly 45 distinct countries** across 2021–2025, in 61 country-weeks. The "45 countries" claim is **VERIFIED**, but only as an all-time total; it was 40 countries in the 2025 run. The US charted only once (#7, week ending 2022-03-13).

### Cited Findings
- **Global week ending 2022-03-13 (Mar 7–13, 2022):** #10, Films (English), 5,450,000 hours. Views were not published then. — [Netflix all-weeks-global.tsv](https://www.netflix.com/tudum/top10/data/all-weeks-global.tsv) (VERIFIED)
- **Global week ending 2025-08-10 (Aug 4–10, 2025):** #9, Films (English), 8,000,000 hours and 3,500,000 views, listed as cumulative week 2. It ranked behind My Oxford Year, KPop Demon Hunters, Happy Gilmore 2 and others. It had more hours than #6–#8 but ranked lower because ranking is by views. — [Netflix all-weeks-global.tsv](https://www.netflix.com/tudum/top10/data/all-weeks-global.tsv) (VERIFIED)
- **Global Top 10 total:** 5.45M + 8.0M = 13.45M hours, 2 weeks. What's on Netflix gives 13.5M hours, 3.5M views. — [What's on Netflix](https://www.whats-on-netflix.com/top-10-title-search/?title=Coach+Carter) (REPORTED, consistent)
- **Country Top 10 (VERIFIED from [all-weeks-countries.tsv](https://www.netflix.com/tudum/top10/data/all-weeks-countries.tsv); 61 rows, 45 distinct countries):**
  - **Week ending 2021-09-26** (4 countries): Jordan #8, Saudi Arabia #8, Belgium #9, Bahrain #10.
  - **Week ending 2022-03-13** (1): United States #7.
  - **July 2022** (5 countries, 11 country-weeks): Bulgaria #6/#9; Slovenia #7/#9; Croatia #8/#8/#10; Serbia #8/#8/#10; Greece #10. These are the weeks ending 07-10, 07-17 and 07-24.
  - **Week ending 2025-08-10** (39 countries):
    - #5: Canada, Chile, Costa Rica, Ecuador, El Salvador, Guatemala, Honduras, Mexico, Nicaragua, Paraguay, Peru.
    - #6: Argentina, Dominican Republic, Panama, Uruguay.
    - #7: Bolivia, Greece, Israel, Italy, Martinique, Serbia, Trinidad and Tobago.
    - #8: Bulgaria, Colombia, Denmark, Finland, Guadeloupe, Iceland, Jamaica, Kenya, Poland, Portugal, South Africa, Venezuela.
    - #9: Spain.
    - #10: Brazil, Croatia, Cyprus, Slovenia.
  - **Week ending 2025-08-17** (6 countries): Guatemala #8, Nicaragua #9, Bulgaria #10, Canada #10, Iceland #10, Nigeria #10 (Nigeria's only week).
  - **Distinct countries:** 4 in 2021, 6 in 2022, 40 in 2025, **45 unique across all years**. There were no country chart entries in 2023, 2024 or 2026.
  - **Peak country rank:** #5 (11 countries, including Canada and Mexico). Most weeks: Bulgaria, Croatia and Serbia with 4 each, then Slovenia with 3.
- The **US did not chart** in the 2025 run.
- **Netflix US arrival:** the film was added around **March 1, 2022**. PopCulture (Apr 27, 2022) says it arrived "March 1" and has stayed in the Top 10 since. ComicBook (Mar 7, 2022) says it was #9 on Monday's Netflix Top 10 movies list. — [PopCulture](https://popculture.com/streaming/news/netflix-coach-carter-samuel-l-jackson/); [ComicBook](https://comicbook.com/movies/news/netflix-top-10-samuel-l-jackson-coach-carter-movie-streaming) (REPORTED)

### Inferences
- The 2025 surge was driven by Latin America, Canada and Europe. Its US-heavy period was March 2022.
- **ESTIMATE:** the 8.0M hours in the Aug 4–10 week are about 21% of H2 2025's 38.5M. The other ~30.5M hours (38.5 − 8.0) were spread across the rest of Jul–Dec 2025, below the global Top 10 threshold.
- What's on Netflix lists "Added to Netflix: Oct 1, 2025". That conflicts with the August 2025 chart data, so it probably reflects a later regional addition or a database artifact. Treat it as unreliable.

### Gaps
- Country lists give ranks only, not hours or views per country.
- The film may have charted on Netflix before July 2021, but Netflix's Top 10 data does not go back that far.
- FlixPatrol's daily charts could not be fetched (HTTP 403), so daily peaks were not verified.

## Streaming viewing before 2023, and non-Netflix figures

### Takeaway
The only official Netflix number before 2023 is the **5.45M-hour global week in March 2022**. All other Netflix viewing before H1 2023 is **undisclosed**. No Nielsen, Samba TV, Reelgood, Paramount+, Prime Video, Hulu, Pluto or Peacock viewership figures were found for the film.

### Cited Findings
- Week of Mar 7–13, 2022: 5,450,000 global hours (VERIFIED). Country Top 10 entries in Sept 2021 and Jul 2022 (VERIFIED, ranks only). — [Netflix Top 10 TSVs](https://www.netflix.com/tudum/top10/data/all-weeks-global.tsv)
- A search for Nielsen streaming Top 10 entries for "Coach Carter" turned up nothing. — web search, 2026-11-10 (no source found)
- Availability now (no viewership data):
  - JustWatch lists the film on Paramount+ / Showtime Apple TV channels in some regions and on Netflix in others. — [JustWatch ID](https://www.justwatch.com/id/movie/coach-carter); [JustWatch TH](https://www.justwatch.com/th/movie/coach-carter)
  - Peacock offers it as a STARZ add-on title. — [Peacock](https://www.peacocktv.com/watch-online/movies/coach-carter/9470de35-3f66-320f-928d-167e2a11ffb3)
  - Super Channel (Canada) lists it. — [Super Channel](https://superchannel.ca/movie/coach-carter)
- Reelgood has a "coach-carter" blog tag, but no viewership figure was found. — [Reelgood blog](https://blog.reelgood.com/tag/coach-carter)

### Inferences
- Paramount (the rights owner, through Paramount and MTV Films) does not publish per-title Paramount+ viewing. No other platform publishes figures comparable to Netflix's. Any cross-platform "total streaming" figure is therefore a Netflix-only floor: **≥73.1M hours / ≈32M views since 2023, plus a disclosed 5.45M hours in one 2022 week.**
- Do NOT add the 2022 week to the engagement-report total as if it completes the record. Netflix viewing from Mar 2022 to Dec 2022 (from the US launch onward) is mostly undisclosed.

### Gaps
- No viewership data exists in public sources for Paramount+, Prime Video, Hulu, Pluto, Peacock/STARZ, Showtime or TV.
- Samba TV and Nielsen data on this film were not found.
- FlixPatrol's "streaming" and "hours" pages returned 403 and could not be checked.
