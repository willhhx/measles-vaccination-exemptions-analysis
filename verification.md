# Verification: Project 1 (Original Research paper)

| Claim | Source | Check |
|---|---|---|
| Main text 2411 words (limit 4,000, excl. references/figures); abstract 247 words | outputs/wordcount.json | PASS |
| No em dashes or causal verbs (cause, leads to) in prose | assert in build_paper.py | PASS |
| 269 cases in 2024 and 2,263 in 2025 across jurisdictions (2,532 total) | results.json; CDC state table sums | PASS |
| CDC national totals: 2025 = 2,289 (2,263 reported by jurisdictions); 2024 = 285 (state table sums to 269) | CDC measles page (Nov 6, 2026 update), table sums in results.json | PASS |
| Median rate 1.24/million; IQR 0.47-3.33; max 30.2 (South Carolina) | results.json | PASS |
| Median MMR 91.7% (IQR 88.9-94.1); 8 at/above 95%; 15 below 90% | results.json desc | PASS |
| NME median 3.9% (IQR 2.5-5.5), range 0.1-14.5, n=46 | results.json desc | PASS |
| Median rate 1.41 (<95%, n=41) vs 0.23 (>=95%, n=8) | results.json desc | PASS |
| Spearman MMR rho -0.49 (n=49); NME rho 0.55 (n=46) | results.json | PASS |
| NB RR coverage 0.90 (0.78-1.04), CI includes 1; NB RR exemption 1.20 (1.01-1.42) | results.json | PASS |
| Poisson dispersion 149 (overdispersed) | results.json | PASS |
| Without Texas: rho -0.51/0.57; NB RR coverage 0.88; Poisson RR 0.89 (CI excludes 1, discrepancy disclosed) | results.json | PASS |
| Without South Carolina: rho -0.50 | results.json | PASS |
| Per-year: 2024 rho -0.05; 2025 rho -0.49; 2026 partial rho -0.29 (p=0.045) | results.json | PASS |
| Five jurisdictions with >=100 cases hold 65% of cases | results.json desc | PASS |
| Three lowest-coverage jurisdictions: Idaho, Alaska, Wisconsin; 2.7-3.5 cases per million | cleaned_state_table.csv | PASS |
| Montana has 5th-highest rate (15.8/million) but no coverage data | top6_states_by_rate.csv; results.json | PASS |
| CDC: kindergarten MMR 95.2% (2019-20) to 92.4% (2025-26); >95% community immunity; 2025 case ages 26%/44%/29% | CDC measles page text fetched Nov 8, 2026 (not peer reviewed) | PASS |
| Guerra 2017: R0 often cited 12-18, estimates vary more widely; R0 determines herd immunity threshold | Europe PMC PMID 28757186 abstract; DOI 10.1016/S1473-3099(17)30307-9 | PASS |
| Omer 2006: PBE and easy-exemption states had higher NME rates; associated with higher pertussis incidence (IRR 1.48, 1.53) | Europe PMC PMID 17032989; DOI 10.1001/jama.296.14.1757 | PASS |
| Omer 2008: Michigan exemption-cluster tracts more likely in pertussis clusters, OR 3.0 (2.5-3.6) | Europe PMC PMID 18922998; DOI 10.1093/aje/kwn263 | PASS |
| Omer 2009: refusal increasing; geographic clustering linked to outbreaks; exemptors at higher risk for measles/pertussis | Europe PMC PMID 19420367; DOI 10.1056/NEJMsa0806477 | PASS |
| Phadke 2016: 18 measles reports, 1,416 cases, 56.8% no vaccination history; 70.6% of 574 unvaccinated eligible cases had NME | Europe PMC PMID 26978210; DOI 10.1001/jama.2016.1353 | PASS |
| Lo & Hotez 2017: 5% MMR decline -> 3-fold increase in cases, ages 2-11 | Europe PMC PMID 28738137; DOI 10.1001/jamapediatrics.2017.1695 | PASS |
| Gromis & Liu 2022: clustered exemptions allow outbreaks with thousands more infections than random distribution | Crossref abstract; DOI 10.1542/peds.2021-050971 | PASS |
| Masters 2020: aggregated data can underestimate outbreak risk when non-vaccination clustered | Crossref abstract; DOI 10.1073/pnas.2011529117 | PASS |
| Morgenstern 1995 and Greenland & Robins 1994: ecologic studies vulnerable to bias/limits on causal inference | Europe PMC PMID 7639884 and 8178788 abstracts | PASS |
| Hulland 2025 exists (Lancet Infect Dis 25(6):607-609); cited only for the 2025 Texas outbreak drawing attention to underimmunization. No abstract was retrievable, so its findings are NOT described | Europe PMC PMID 40339584; title/authors/journal/year/pages verified; content NOT verified | PASS |

## Items for you to check manually
- Hulland et al. (2025): open the article and confirm it supports the one sentence citing it, or remove it.
- EUJPH rules on whether abstract, tables, and captions count toward the 4,000-word limit (current main text is under 2,500 either way).
- 2025 CDC case counts are preliminary; re-download the CDC table right before submission and re-run analysis.py.
- Custom Poisson/negative binomial code was not cross-checked against statsmodels; re-run in an environment that has it if possible.
- Peer-reviewed citations: 11 (Greenland & Robins; Gromis & Liu; Guerra; Hulland; Lo & Hotez; Masters; Morgenstern; Omer 2006, 2008, 2009; Phadke). Datasets/web pages: CDC x2, Census.
