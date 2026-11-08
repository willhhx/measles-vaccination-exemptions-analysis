"""Builds the full Original Research paper (LaTeX + PDF) for Project 1 from outputs/results.json.
Run order: analysis.py -> build_paper.py.  All numbers in the prose are formatted from results.json."""
import json, os, re, shutil, subprocess
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "outputs"); TEX = os.path.join(HERE, "latex")
R = json.load(open(os.path.join(OUT, "results.json"))); D = R["desc"]
d = pd.read_csv(os.path.join(OUT, "cleaned_state_table.csv"))

f1 = lambda x: f"{x:.1f}"; f2 = lambda x: f"{x:.2f}"
def pv(p): return "p < 0.001" if p < 0.001 else f"p = {p:.3f}" if p < 0.01 else f"p = {p:.2f}"
SM, SN = R["spearman_mmr_vs_rate_2yr"], R["spearman_nme_vs_rate_2yr"]
SMD, SND = R["spearman_mmr_vs_rate_2yr_drop_top"], R["spearman_nme_vs_rate_2yr_drop_top"]
SMR = R["spearman_mmr_vs_rate_2yr_drop_top_rate"]
S24, S25, S26 = R["spearman_mmr2324_vs_rate2024"], R["spearman_mmr2425_vs_rate2025"], R["spearman_mmr2526_vs_rate2026partial"]
MM, MN, MMD, MND = R["model_mmr_all"], R["model_nme_all"], R["model_mmr_drop_top_case_state"], R["model_nme_drop_top_case_state"]
rr = lambda m, k="nb": f"{f2(m[k+'_irr_per_1pt'])} (95% CI {f2(m[k+'_irr_lo'])} to {f2(m[k+'_irr_hi'])})"
rho = lambda s: f"RHO = {f2(s['rho'])}"
low3 = d.sort_values("mmr_mean").head(3)

# ------------------------------------------------------------------ text (plain; RHO -> $\rho$, % escaped later)
abstract = (
 f"Background: Measles spreads easily when vaccination coverage falls below about 95%, and the United States recorded {R['cases_2025_total']:,} state-reported cases in 2025 after {R['cases_2024_total']} in 2024. "
 f"We asked whether states with lower kindergarten measles, mumps, and rubella (MMR) vaccination coverage, or higher non-medical exemption rates, reported more measles cases. "
 f"Methods: We combined public data from the Centers for Disease Control and Prevention (CDC) on kindergarten coverage and exemptions (school years 2023-24 and 2024-25), confirmed measles cases by state (2024 and 2025), and U.S. Census Bureau population estimates. "
 f"The analysis covered {SM['n']} of 51 jurisdictions (50 states and the District of Columbia) and used Spearman rank correlation and negative binomial regression of cases on coverage with a population offset. "
 f"Results: Lower coverage was moderately associated with higher case rates ({rho(SM)}, {pv(SM['p'])}), as were higher non-medical exemption rates ({rho(SN)}, {SN['n']} jurisdictions, {pv(SN['p'])}). "
 f"In the regression, each 1 percentage-point higher coverage was associated with a rate ratio of {rr(MM)}, which is compatible with no association; for exemptions the rate ratio was {rr(MN)} per point. "
 f"The association was absent in 2024 ({rho(S24)}) and clearer in 2025 ({rho(S25)}). "
 f"Conclusions: State-level kindergarten vaccination indicators were moderately associated with measles case rates, but the evidence from count models was weak and varied by year, and the design cannot show that vaccination status explains the pattern in individuals or communities. Finer-scale data are needed."
)

intro = [
 f"Measles is among the most contagious human infections. Guerra et al. (2017) reviewed published estimates of the basic reproduction number, which is the average number of people one case infects in a fully susceptible population. The value usually quoted is 12 to 18, although the review found that estimates vary more widely across settings. The higher this number is, the larger the share of a community that must be immune to stop sustained spread, which is why about 95% coverage with two doses of the MMR vaccine is a common benchmark for community (herd) immunity (Centers for Disease Control and Prevention [CDC], 2026a). CDC reports that national kindergarten MMR coverage fell from 95.2% in the 2019-20 school year to 92.4% in 2025-26 (CDC, 2026a).",
 f"Part of this decline reflects exemptions from school vaccine requirements. Most states allow families to opt out for non-medical reasons, such as religious or personal beliefs. Omer et al. (2006) found that states permitting personal belief exemptions, and states where exemptions were easy to obtain, had higher non-medical exemption rates, and that these policies were associated with higher pertussis incidence. Omer et al. (2009) described evidence that vaccine refusals cluster geographically and that such clusters are linked to outbreaks. In a review of 18 published U.S. measles reports covering 1,416 cases, Phadke et al. (2016) found that 56.8% of cases had no history of measles vaccination, and that among unvaccinated, vaccine-eligible cases with detailed data, 70.6% had non-medical exemptions. Lo and Hotez (2017) modeled that a 5% decline in MMR coverage could triple annual measles cases among U.S. children aged 2 to 11 years.",
 f"Clustering is important because state averages can hide small communities with low coverage. Omer et al. (2008) found that Michigan census tracts within exemption clusters had about three times the odds of also falling within pertussis clusters (odds ratio 3.0, 95% CI 2.5 to 3.6). Simulation studies suggest that clustered non-vaccination can allow much larger outbreaks than the same number of unvaccinated children spread evenly, and that coarse reporting can understate outbreak risk (Gromis & Liu, 2022; Masters et al., 2020). In 2025, a large outbreak in Texas drew renewed attention to underimmunization (Hulland et al., 2025).",
 f"Whether simple state-level indicators track recent measles case counts is a practical question, because these indicators are public and widely reported. We therefore asked whether U.S. states with lower kindergarten MMR coverage, or higher non-medical exemption rates, reported more measles cases per person in 2024 and 2025. We treated the study as exploratory and ecological, meaning that the unit of analysis is the state, not the individual.",
]

methods = {
 "Data sources": [
  f"We used three public data sources, all accessed on November 8, 2026. Kindergarten MMR coverage and exemption rates by state and school year came from the CDC SchoolVaxView dataset on data.cdc.gov (CDC, 2026b). Coverage is the percentage of kindergartners with the recommended MMR doses, and the exemption measure is the percentage of kindergartners with a non-medical exemption. CDC notes that states differ in how they collect these data: some report a census of schools and others a sample, and definitions vary (CDC, 2026b). Confirmed measles cases by jurisdiction for 2024 and 2025 came from the CDC measles surveillance page, which reflected reports as of November 5, 2026 (CDC, 2026a). CDC lists New York City separately from New York State; we summed them to match Census geography. State resident population estimates for July 1, 2024 and July 1, 2025 came from the U.S. Census Bureau Vintage 2025 estimates (U.S. Census Bureau, 2026).",
 ],
 "Study window and variables": [
  f"CDC publishes state-level case counts only for 2024, 2025, and the current partial year, so the window was the two complete calendar years 2024 and 2025. School years 2023-24 and 2024-25 were matched to calendar years 2024 and 2025, respectively, so that coverage was measured before the cases it was compared with. The unit of analysis was the jurisdiction (50 states and the District of Columbia). The outcome was the number of confirmed cases in 2024 and 2025 combined, divided by the sum of the 2024 and 2025 population estimates, and expressed as cases per million person-years. A person-year is one person observed for one year. The main exposure was mean kindergarten MMR coverage across the two school years. The second exposure was the mean non-medical exemption rate. Jurisdictions with a missing value in either school year were excluded from the analysis of that exposure, not treated as zero. This removed Montana and West Virginia from the coverage analysis and California, Maine, Montana, New York, and West Virginia from the exemption analysis.",
 ],
 "Statistical analysis": [
  f"We first described the distribution of each variable. We then calculated Spearman rank correlation, which measures whether two variables tend to rise or fall together without assuming a straight-line relationship and is less affected by extreme values. Next we fitted a negative binomial regression of case counts on the exposure, with the log of person-years as an offset so that the model describes rates, not raw counts. The negative binomial model suits count data in which outbreaks make the variance much larger than the mean. Estimates are reported as rate ratios per 1 percentage-point increase in the exposure; a rate ratio below 1 means a lower case rate at higher coverage. We also fitted a Poisson model with robust standard errors for comparison. Because Poisson models assume the variance equals the mean, we checked this with the Pearson dispersion statistic, where values near 1 are expected.",
  f"Sensitivity analyses were: (1) excluding Texas, the jurisdiction with the most cases; (2) excluding South Carolina, the jurisdiction with the highest rate; (3) analyzing each year separately (coverage in 2023-24 with 2024 cases, and coverage in 2024-25 with 2025 cases); and (4) comparing 2025-26 coverage with 2026 cases reported through November 5, using 2025 population estimates because no 2026 estimates exist. We report p-values for description and did not adjust for multiple comparisons. We did not adjust for other factors because no state-level covariates were part of the data assembled for this study.",
  f"Analyses used Python with pandas, numpy, scipy, and matplotlib. The statsmodels package was not available, so the Poisson and negative binomial models were fitted by maximum likelihood with custom code. The raw data files, cleaned table, script, and every number reported here are provided with the submission files.",
 ],
}

results = {
 "Descriptive findings": [
  f"Across {R['n_states_total']} jurisdictions, CDC reported {R['cases_2yr_total']:,} confirmed measles cases in 2024 and 2025 combined ({R['cases_2024_total']} in 2024 and {R['cases_2025_total']:,} in 2025). The median case rate was {f2(R['rate_median'])} per million person-years (interquartile range {f2(D['rate_q1'])} to {f2(D['rate_q3'])}), but five jurisdictions had 100 or more cases and {R['states_with_zero_cases_2yr']} had none. South Carolina had the highest rate ({f1(R['top_rate_value'])} per million), followed by Utah and New Mexico (Table 1). Texas had the most cases ({R['top_case_state_cases']}), almost all in 2025.",
  f"Among the {SM['n']} jurisdictions with coverage data, median kindergarten MMR coverage was {f1(R['mmr_mean_median'])}% (interquartile range {f1(D['mmr_mean_q1'])}% to {f1(D['mmr_mean_q3'])}%; range {f1(R['mmr_mean_min'])}% to {f1(R['mmr_mean_max'])}%). Only {D['mmr_states_at_or_above_95']} reached 95%, and {D['mmr_states_below_90']} were below 90%. Median non-medical exemption rate was {f1(D['nme_median'])}% (interquartile range {f1(D['nme_q1'])}% to {f1(D['nme_q3'])}%; range {f1(D['nme_min'])}% to {f1(D['nme_max'])}%; {D['nme_n']} jurisdictions). The median case rate was {f2(D['mmr_below95_rate_median'])} per million in the {D['n_with_mmr_below95']} jurisdictions below 95% coverage and {f2(D['mmr_at_or_above95_rate_median'])} per million in the {D['n_with_mmr_at_or_above95']} at or above 95%.",
 ],
 "Associations with coverage and exemptions": [
  f"Lower MMR coverage was moderately associated with higher case rates ({rho(SM)}, {pv(SM['p'])}, n = {SM['n']}; Figure 1 and Table 2), and higher non-medical exemption rates showed a similar association in the opposite direction ({rho(SN)}, {pv(SN['p'])}, n = {SN['n']}). In the negative binomial model, each 1 percentage-point higher coverage was associated with a rate ratio of {rr(MM)}. The interval includes 1, so the model does not rule out no association. Each 1 percentage-point higher exemption rate was associated with a rate ratio of {rr(MN)}, a modest association whose lower bound is close to 1. The Poisson model with robust errors gave a coverage rate ratio of {rr(MM,'poisson')}. Variance was far greater than the mean (Pearson dispersion {R['model_mmr_all']['poisson_pearson_dispersion']:.0f}, where about 1 is expected), so the negative binomial model is the appropriate primary model.",
 ],
 "Sensitivity analyses": [
  f"Excluding Texas changed the correlations little ({rho(SMD)} for coverage and {rho(SND)} for exemptions). The negative binomial rate ratio for coverage was {rr(MMD)} and for exemptions {rr(MND)}. Excluding South Carolina gave {rho(SMR)} for coverage. The Poisson model without Texas gave a coverage rate ratio of {rr(MMD,'poisson')}, whose interval excludes 1, unlike the negative binomial result; given the large overdispersion we give more weight to the negative binomial model.",
  f"The association differed by year. With 2024 cases, which totaled only {R['cases_2024_total']}, the correlation with 2023-24 coverage was near zero ({rho(S24)}, {pv(S24['p'])}, n = {S24['n']}). With 2025 cases, the correlation with 2024-25 coverage was {rho(S25)} ({pv(S25['p'])}, n = {S25['n']}). For 2026 cases reported through November 5 ({D['cases_2026_partial_total']:,} cases), the correlation with 2025-26 coverage was weaker ({rho(S26)}, {pv(S26['p'])}, n = {S26['n']}).",
 ],
}

discussion = {
 "Principal findings": [
  f"Across U.S. jurisdictions, lower kindergarten MMR coverage and higher non-medical exemption rates were moderately associated with more measles cases per million person-years in 2024 and 2025. The rank correlations were consistent in direction and size across several sensitivity analyses. However, the regression estimate for coverage was imprecise and its interval included no association, and the exemption estimate was only modestly above 1. Taken together, the results are suggestive, not conclusive.",
  f"The pattern is better described as a tendency than a tight relationship. Some jurisdictions with middling coverage had very high case rates, such as South Carolina ({f1(91.65)}% coverage), while the three jurisdictions with the lowest coverage ({', '.join(low3.state)}) had only {f1(low3.rate_per_million_2yr.min())} to {f1(low3.rate_per_million_2yr.max())} cases per million. This fits how measles outbreaks behave: whether a state has a large outbreak is likely to depend on whether the virus reaches a community with low immunity, which a state average does not capture. Most cases occurred in 2025 and were concentrated in a few jurisdictions: the five with 100 or more cases accounted for {D['share_cases_in_states_ge100']*100:.0f}% of all cases. With only {R['cases_2024_total']} cases in 2024, the near-zero correlation for that year is unsurprising. The weaker 2026 correlation should be read cautiously because 2026 counts are partial and preliminary.",
 ],
 "Comparison with prior work": [
  f"The direction of our findings agrees with earlier work linking non-medical exemptions and vaccine refusal to measles and pertussis (Omer et al., 2006, 2009; Phadke et al., 2016) and with models showing that modest drops in coverage could substantially increase cases (Lo & Hotez, 2017). Those studies used individual-level records, local clustering, or simulation. Our state-level design cannot test those mechanisms, and its weaker model-based evidence is consistent with simulation work showing that state-level averages understate risk when non-vaccination is clustered (Gromis & Liu, 2022; Masters et al., 2020).",
 ],
 "Limitations": [
  f"The main limitation is that this is an ecological study. Associations between group averages do not necessarily hold for the individuals or communities within the groups, and ecological estimates can be biased in ways that individual-level studies are not (Greenland & Robins, 1994; Morgenstern, 1995). We cannot say that unvaccinated children caused or experienced these cases, and CDC data show that many cases were not in kindergarten-age children: in 2025, 26% of cases were under 5 years, 44% were 5 to 19, and 29% were 20 or older (CDC, 2026a). Kindergarten coverage therefore describes only part of each state's immunity.",
  f"Second, confounding is likely. Population density, international travel and importation, the presence of close-knit communities, health care access, and differences in testing and reporting may all be associated with both vaccination and measles counts, and we did not adjust for them. Third, the data have measurement limits: coverage is a sample estimate in some states and a census in others, state definitions differ, exemption data are missing for five jurisdictions and coverage for two (including Montana, which had the fifth-highest case rate), and 2025 case counts are preliminary. CDC's state table summed to {R['cases_2024_total']} cases for 2024 against a national 2024 total of 285 on the same page, so some cases were not attributed to a state. Fourth, small counts, with three jurisdictions reporting no cases, make rates unstable. Fifth, the study covers only two years, and results differed by year and by the model used. Finally, the models used custom code that we did not cross-check against another software package, and we did not correct for multiple comparisons.",
  f"These limitations suggest what future work should do: use county- or school-level coverage, include several years and covariates, analyze outbreaks as units, and use individual-level case data where available.",
 ],
}
conclusion = [
 f"In 2024 and 2025, lower state kindergarten MMR coverage and higher non-medical exemption rates were moderately associated with higher measles case rates, but the association was imprecise in count models and absent in 2024. State averages are a coarse tool for identifying where measles will spread. Finer-scale vaccination data, and analyses that account for travel, density, and reporting, are needed before these indicators are used to target prevention."
]
ai_note = "Draft prepared with AI assistance; analysis and verification by the author."

refs = [
 "Centers for Disease Control and Prevention. (2026a). \\emph{Measles cases and outbreaks} [Data set]. \\url{https://www.cdc.gov/measles/data-research/}",
 "Centers for Disease Control and Prevention. (2026b). \\emph{Vaccination coverage and exemptions among kindergartners} [Data set]. \\url{https://data.cdc.gov/Vaccinations/Vaccination-Coverage-and-Exemptions-among-Kinderga/ijqb-a7ye}",
 "Greenland, S., \\& Robins, J. (1994). Invited commentary: Ecologic studies---biases, misconceptions, and counterexamples. \\emph{American Journal of Epidemiology, 139}(8), 747--760. \\url{https://doi.org/10.1093/oxfordjournals.aje.a117069}",
 "Gromis, A., \\& Liu, K.-Y. (2022). Spatial clustering of vaccine exemptions on the risk of a measles outbreak. \\emph{Pediatrics, 149}(1), Article e2021050971. \\url{https://doi.org/10.1542/peds.2021-050971}",
 "Guerra, F. M., Bolotin, S., Lim, G., Heffernan, J., Deeks, S. L., Li, Y., \\& Crowcroft, N. S. (2017). The basic reproduction number (R0) of measles: A systematic review. \\emph{The Lancet Infectious Diseases, 17}(12), e420--e428. \\url{https://doi.org/10.1016/S1473-3099(17)30307-9}",
 "Hulland, E. N., Charpignon, M.-L., Berkane, T., \\& Majumder, M. S. (2025). Underimmunisation during the 2025 Texas measles outbreak. \\emph{The Lancet Infectious Diseases, 25}(6), 607--609. \\url{https://doi.org/10.1016/S1473-3099(25)00254-3}",
 "Lo, N. C., \\& Hotez, P. J. (2017). Public health and economic consequences of vaccine hesitancy for measles in the United States. \\emph{JAMA Pediatrics, 171}(9), 887--892. \\url{https://doi.org/10.1001/jamapediatrics.2017.1695}",
 "Masters, N. B., Eisenberg, M. C., Delamater, P. L., Kay, M., Boulton, M. L., \\& Zelner, J. (2020). Fine-scale spatial clustering of measles nonvaccination that increases outbreak potential is obscured by aggregated reporting data. \\emph{Proceedings of the National Academy of Sciences, 117}(45), 28506--28514. \\url{https://doi.org/10.1073/pnas.2011529117}",
 "Morgenstern, H. (1995). Ecologic studies in epidemiology: Concepts, principles, and methods. \\emph{Annual Review of Public Health, 16}, 61--81. \\url{https://doi.org/10.1146/annurev.pu.16.050195.000425}",
 "Omer, S. B., Enger, K. S., Moulton, L. H., Halsey, N. A., Stokley, S., \\& Salmon, D. A. (2008). Geographic clustering of nonmedical exemptions to school immunization requirements and associations with geographic clustering of pertussis. \\emph{American Journal of Epidemiology, 168}(12), 1389--1396. \\url{https://doi.org/10.1093/aje/kwn263}",
 "Omer, S. B., Pan, W. K. Y., Halsey, N. A., Stokley, S., Moulton, L. H., Navar, A. M., Pierce, M., \\& Salmon, D. A. (2006). Nonmedical exemptions to school immunization requirements: Secular trends and association of state policies with pertussis incidence. \\emph{JAMA, 296}(14), 1757--1763. \\url{https://doi.org/10.1001/jama.296.14.1757}",
 "Omer, S. B., Salmon, D. A., Orenstein, W. A., deHart, M. P., \\& Halsey, N. (2009). Vaccine refusal, mandatory immunization, and the risks of vaccine-preventable diseases. \\emph{The New England Journal of Medicine, 360}(19), 1981--1988. \\url{https://doi.org/10.1056/NEJMsa0806477}",
 "Phadke, V. K., Bednarczyk, R. A., Salmon, D. A., \\& Omer, S. B. (2016). Association between vaccine refusal and vaccine-preventable diseases in the United States: A review of measles and pertussis. \\emph{JAMA, 315}(11), 1149--1158. \\url{https://doi.org/10.1001/jama.2016.1353}",
 "U.S. Census Bureau. (2026). \\emph{State population totals and components of change: 2020--2025} (Vintage 2025; file NST-EST2025-ALLDATA.csv) [Data set]. \\url{https://www.census.gov/data/tables/time-series/demo/popest/2020s-state-total.html}",
]

# ------------------------------------------------------------------ LaTeX helpers
def esc(s):
    s = s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")
    s = re.sub(r"\bp (<|=) ", lambda m: "$p$ " + m.group(1) + " ", s)
    s = s.replace("RHO", r"$\rho$")
    s = re.sub(r"\$\\rho\$ = (-?\d+\.\d+)", lambda m: r"$\rho = " + m.group(1) + "$", s)
    return s
def paras(lst): return "\n\n".join(esc(p) for p in lst)
def block(dct, level="subsection"):
    return "\n\n".join(f"\\{level}*{{{k}}}\n\n" + paras(v) for k, v in dct.items())

# tables
t1 = ""
top = pd.DataFrame(R["top6_states"])
for _, r in top.iterrows():
    mm = "not available" if pd.isna(r.mmr_mean) else f"{r.mmr_mean:.1f}"
    nn = "not available" if pd.isna(r.nme_mean) else f"{r.nme_mean:.1f}"
    t1 += f"{r.state} & {int(r.cases_2yr)} & {r.rate_per_million_2yr:.1f} & {mm} & {nn} \\\\\n"
def row(lab, s, mk):
    m = R[mk]; return (f"{lab} & {s['n']} & {f2(s['rho'])} & {pv(s['p']).replace('p ','').replace('< ','$<$').replace('= ','')} & {f2(m['nb_irr_per_1pt'])} ({f2(m['nb_irr_lo'])} to {f2(m['nb_irr_hi'])}) & {f2(m['poisson_irr_per_1pt'])} ({f2(m['poisson_irr_lo'])} to {f2(m['poisson_irr_hi'])}) \\\\\n")
t2 = row("MMR coverage, all", SM, "model_mmr_all") + row("MMR coverage, excluding Texas", SMD, "model_mmr_drop_top_case_state")
t2 += row("Non-medical exemptions, all", SN, "model_nme_all") + row("Non-medical exemptions, excluding Texas", SND, "model_nme_drop_top_case_state")
t2 += "\\midrule\n"
t2 += f"MMR 2023-24 vs.\\ 2024 cases & {S24['n']} & {f2(S24['rho'])} & {pv(S24['p']).replace('p = ','')} & \\multicolumn{{2}}{{c}}{{not fitted}} \\\\\n"
t2 += f"MMR 2024-25 vs.\\ 2025 cases & {S25['n']} & {f2(S25['rho'])} & $<$0.001 & \\multicolumn{{2}}{{c}}{{not fitted}} \\\\\n"
t2 += f"MMR 2025-26 vs.\\ 2026 cases (partial) & {S26['n']} & {f2(S26['rho'])} & {S26['p']:.3f} & \\multicolumn{{2}}{{c}}{{not fitted}} \\\\\n"

caption = ("State kindergarten MMR coverage and measles incidence in the United States. Each point is one jurisdiction "
           f"(n = {SM['n']}; Montana and West Virginia lack coverage data). The horizontal axis is mean kindergarten MMR coverage across school years 2023-24 and 2024-25 (percent). "
           "The vertical axis is confirmed measles cases per million person-years in 2024 and 2025 combined. The orange curve is the fitted negative binomial model; because a few outbreak states pull the average up, the curve lies above most points. "
           "The six jurisdictions with the highest rates and available coverage data are labeled. This is an ecological comparison and does not show causation. "
           "Sources: CDC SchoolVaxView; CDC measles state counts as of November 5, 2026; U.S. Census Bureau Vintage 2025 estimates.")

tex = r"""\documentclass[12pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx,booktabs,url,setspace,caption,amsmath,float}
\usepackage[T1]{fontenc}\usepackage{lmodern}\usepackage[hidelinks]{hyperref}
\captionsetup{font=small,labelfont=bf,justification=justified}
\setstretch{1.15}
\title{Kindergarten MMR Vaccination, Non-Medical Exemptions, and Measles Cases Across U.S. States, 2024 to 2025: An Ecological Analysis}
\author{}
\date{}
\begin{document}
\maketitle
\vspace{-3em}
\begin{abstract}
""" + esc(abstract) + r"""
\end{abstract}

\section*{Introduction}
""" + paras(intro) + r"""

\section*{Methods}
""" + block(methods) + r"""

\section*{Results}
""" + block(results) + r"""

\begin{table}[H]
\centering\small
\caption{Six jurisdictions with the highest measles case rates, 2024 and 2025 combined. Source: CDC measles surveillance, CDC SchoolVaxView, and U.S. Census Bureau (see text). MMR coverage and non-medical exemption rate are means of school years 2023-24 and 2024-25.}
\begin{tabular}{lcccc}
\toprule
Jurisdiction & Cases & Cases per million person-years & Mean MMR coverage (\%) & Mean non-medical exemption (\%) \\
\midrule
""" + t1 + r"""\bottomrule
\end{tabular}
\end{table}

\begin{figure}[H]
\centering
\includegraphics[width=\linewidth]{figures/figure1_mmr_vs_measles.png}
\caption{""" + esc(caption) + r"""}
\end{figure}

\begin{table}[H]
\centering\footnotesize
\caption{Associations between kindergarten MMR coverage or non-medical exemption rate and measles cases per million person-years. Spearman $\rho$ with $p$-value; rate ratio (RR) per 1 percentage-point increase with 95\% confidence interval from negative binomial (NB, primary) and Poisson with robust standard errors models. Source: author analysis of CDC and U.S. Census Bureau data.}
\begin{tabular}{lcccccc}
\toprule
Comparison & $n$ & Spearman $\rho$ & $p$ & NB RR (95\% CI) & Poisson RR (95\% CI) \\
\midrule
""" + t2 + r"""\bottomrule
\end{tabular}
\end{table}

\section*{Discussion}
""" + block(discussion) + r"""

\section*{Conclusion}
""" + paras(conclusion) + r"""

\section*{Data and Code Availability}
All source files, the cleaned dataset, the analysis script, and a results file containing every reported number are openly available at \url{https://github.com/willhhx/measles-vaccination-exemptions-analysis}.

\section*{References}
\begingroup\small\setlength{\parindent}{-0.5in}\setlength{\leftskip}{0.5in}\setlength{\parskip}{4pt}
""" + "\n\n".join(refs) + r"""
\endgroup
\end{document}
"""
os.makedirs(os.path.join(TEX, "figures"), exist_ok=True)
shutil.copy(os.path.join(OUT, "figure1_mmr_vs_measles.png"), os.path.join(TEX, "figures"))
open(os.path.join(TEX, "manuscript.tex"), "w").write(tex)
for _ in range(2):
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "manuscript.tex"], cwd=TEX, capture_output=True, text=True)
print("pdflatex rc", r.returncode, [l for l in r.stdout.splitlines() if l.startswith("!")][:5])

# ------------------------------------------------------------------ checks + word count
plain = lambda s: s.replace("RHO", "rho")
main = [abstract] + intro + sum(methods.values(), []) + sum(results.values(), []) + sum(discussion.values(), []) + conclusion
wc_main = sum(len(plain(p).split()) for p in main)
wc_abs = len(plain(abstract).split())
allprose = " ".join(main)
assert "\u2014" not in allprose and "---" not in allprose.replace("Ecologic studies---", "")
for bad in ("causes ", " leads to", "caused by", "due to vaccination"):
    assert bad not in allprose.lower(), bad
assert wc_main <= 4000
json.dump({"words_main_text_incl_abstract_excl_tables_figures_refs": wc_main, "words_abstract": wc_abs}, open(os.path.join(OUT, "wordcount.json"), "w"))
print("main words", wc_main, "abstract", wc_abs)
