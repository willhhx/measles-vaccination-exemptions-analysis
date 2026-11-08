"""
Project 1: Kindergarten MMR coverage / non-medical exemptions vs. measles cases by U.S. state.
Reproducible script. Run:  python3 analysis.py
Needs only: pandas, numpy, scipy, matplotlib.  (statsmodels was unavailable, so the Poisson and
negative-binomial (NB2) models are fitted below with numpy/scipy; they are standard ML estimators.)

Inputs (data_raw/):
  schoolvaxview_kindergarten_ijqb-a7ye.csv   CDC SchoolVaxView, data.cdc.gov dataset ijqb-a7ye
  cdc_measles_cases_by_jurisdiction_2024_2026.csv   CDC "Measles Cases and Outbreaks" state table (as of Nov 5, 2026)
  NST-EST2025-ALLDATA.csv                    U.S. Census Bureau Vintage 2025 state population estimates
Outputs (outputs/): cleaned_state_table.csv, results.json, results.csv, figure1_mmr_vs_measles.png
"""
import json, os
import numpy as np, pandas as pd
from scipy import stats, optimize, special
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data_raw")
OUT = os.path.join(HERE, "outputs")
os.makedirs(OUT, exist_ok=True)
R = {}  # every number used in the text is stored here

# ---------------------------------------------------------------- load
v = pd.read_csv(os.path.join(RAW, "schoolvaxview_kindergarten_ijqb-a7ye.csv"))
v = v[v["Geography Type"] == "States"].copy()
v["est"] = pd.to_numeric(v["Estimate (%)"], errors="coerce")  # non-numeric/blank -> NaN (not zero)
mmr = v[v["Vaccine/Exemption"] == "MMR"].pivot_table(index="Geography", columns="School Year", values="est")
nme = v[v["Dose"] == "Non-Medical Exemption"].pivot_table(index="Geography", columns="School Year", values="est")

m = pd.read_csv(os.path.join(RAW, "cdc_measles_cases_by_jurisdiction_2024_2026.csv"))
m["Location"] = m["Location"].replace({"New York City": "New York"})  # Census counts NYC inside New York
m = m.groupby("Location")[["2024", "2025", "2026"]].sum()

p = pd.read_csv(os.path.join(RAW, "NST-EST2025-ALLDATA.csv"))
p = p[p["SUMLEV"] == 40].set_index("NAME")[["POPESTIMATE2024", "POPESTIMATE2025"]]  # states + DC (Puerto Rico not in file)

states = sorted(set(m.index) & set(p.index) & set(mmr.index))
assert len(states) == 51, len(states)

# ---------------------------------------------------------------- state-level table
# School year 2023-24 and 2024-25 kindergarten data are matched to calendar years 2024 and 2025
# (the two COMPLETE calendar years CDC reports by state). 2026 (to Nov 5) is used only as a sensitivity check.
d = pd.DataFrame(index=states)
d["cases_2024"] = m.loc[states, "2024"]; d["cases_2025"] = m.loc[states, "2025"]; d["cases_2026_partial"] = m.loc[states, "2026"]
d["pop_2024"] = p.loc[states, "POPESTIMATE2024"]; d["pop_2025"] = p.loc[states, "POPESTIMATE2025"]
d["mmr_2023_24"] = mmr.loc[states, "2023-24"]; d["mmr_2024_25"] = mmr.loc[states, "2024-25"]; d["mmr_2025_26"] = mmr.loc[states, "2025-26"]
d["nme_2023_24"] = nme.reindex(states)["2023-24"]; d["nme_2024_25"] = nme.reindex(states)["2024-25"]; d["nme_2025_26"] = nme.reindex(states)["2025-26"]
d["cases_2yr"] = d.cases_2024 + d.cases_2025
d["person_years_2yr"] = d.pop_2024 + d.pop_2025
d["rate_per_million_2yr"] = d.cases_2yr / d.person_years_2yr * 1e6   # cases per million person-years
d["mmr_mean"] = d[["mmr_2023_24", "mmr_2024_25"]].mean(axis=1, skipna=False)
d["nme_mean"] = d[["nme_2023_24", "nme_2024_25"]].mean(axis=1, skipna=False)
d["rate_2024"] = d.cases_2024 / d.pop_2024 * 1e6
d["rate_2025"] = d.cases_2025 / d.pop_2025 * 1e6
d["rate_2026_partial"] = d.cases_2026_partial / d.pop_2025 * 1e6  # 2025 population used (no 2026 estimate exists yet)
d.index.name = "state"
d.round(4).to_csv(os.path.join(OUT, "cleaned_state_table.csv"))

R["n_states_total"] = len(d)
R["cases_2024_total"] = int(d.cases_2024.sum()); R["cases_2025_total"] = int(d.cases_2025.sum())
R["cases_2yr_total"] = int(d.cases_2yr.sum())
R["states_with_zero_cases_2yr"] = int((d.cases_2yr == 0).sum())
R["mmr_missing_states_mean"] = d.index[d.mmr_mean.isna()].tolist()
R["nme_missing_states_mean"] = d.index[d.nme_mean.isna()].tolist()
R["mmr_mean_median"] = float(d.mmr_mean.median()); R["mmr_mean_min"] = float(d.mmr_mean.min()); R["mmr_mean_max"] = float(d.mmr_mean.max())
R["mmr_states_below_95_mean"] = int((d.mmr_mean < 95).sum())
R["rate_median"] = float(d.rate_per_million_2yr.median())

# ---------------------------------------------------------------- Spearman
def sp(x, y, tag, sub=None):
    ok = x.notna() & y.notna()
    if sub is not None: ok &= sub
    r, pv = stats.spearmanr(x[ok], y[ok])
    R[f"spearman_{tag}"] = {"rho": float(r), "p": float(pv), "n": int(ok.sum())}

sp(d.mmr_mean, d.rate_per_million_2yr, "mmr_vs_rate_2yr")
sp(d.nme_mean, d.rate_per_million_2yr, "nme_vs_rate_2yr")
sp(d.mmr_2023_24, d.rate_2024, "mmr2324_vs_rate2024")
sp(d.mmr_2024_25, d.rate_2025, "mmr2425_vs_rate2025")
sp(d.mmr_2025_26, d.rate_2026_partial, "mmr2526_vs_rate2026partial")
top_state = d.cases_2yr.idxmax(); R["top_case_state_2yr"] = top_state; R["top_case_state_cases"] = int(d.cases_2yr.max())
nontop = d.index != top_state
sp(d.mmr_mean, d.rate_per_million_2yr, "mmr_vs_rate_2yr_drop_top", pd.Series(nontop, d.index))
sp(d.nme_mean, d.rate_per_million_2yr, "nme_vs_rate_2yr_drop_top", pd.Series(nontop, d.index))
top_rate_state = d.rate_per_million_2yr.idxmax(); R["top_rate_state_2yr"] = top_rate_state
R["top_rate_value"] = float(d.rate_per_million_2yr.max())
sp(d.mmr_mean, d.rate_per_million_2yr, "mmr_vs_rate_2yr_drop_top_rate", pd.Series(d.index != top_rate_state, d.index))

# ---------------------------------------------------------------- count models (numpy/scipy)
def pois_fit(X, y, off):
    b = np.zeros(X.shape[1]); b[0] = np.log(y.sum() / np.exp(off).sum())
    for _ in range(100):
        mu = np.exp(X @ b + off); W = mu; z = X @ b + (y - mu) / mu
        bn = np.linalg.solve(X.T @ (W[:, None] * X), X.T @ (W * z))
        if np.max(abs(bn - b)) < 1e-10: b = bn; break
        b = bn
    mu = np.exp(X @ b + off)
    bread = np.linalg.inv(X.T @ (mu[:, None] * X)); meat = X.T @ (((y - mu) ** 2)[:, None] * X)
    se = np.sqrt(np.diag(bread @ meat @ bread))  # HC0 robust (sandwich) SE
    return b, se, mu

def nb_nll(th, X, y, off):
    b, a = th[:-1], np.exp(th[-1]); mu = np.exp(X @ b + off); r = 1 / a
    return -np.sum(special.gammaln(y + r) - special.gammaln(r) - special.gammaln(y + 1)
                   + r * np.log(r / (r + mu)) + y * np.log(mu / (r + mu)))

def num_hess(f, x, h=1e-4):
    n = len(x); H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            e_i = np.eye(n)[i] * h; e_j = np.eye(n)[j] * h
            H[i, j] = (f(x + e_i + e_j) - f(x + e_i - e_j) - f(x - e_i + e_j) + f(x - e_i - e_j)) / (4 * h * h)
    return H

def nb_fit(X, y, off):
    b0, _, mu0 = pois_fit(X, y, off)
    s0 = np.concatenate([b0, [0.0]])
    res = optimize.minimize(nb_nll, s0, args=(X, y, off), method="BFGS", options={"gtol": 1e-8, "maxiter": 2000})
    res2 = optimize.minimize(nb_nll, res.x, args=(X, y, off), method="Nelder-Mead", options={"xatol": 1e-9, "fatol": 1e-12, "maxiter": 20000})
    th = res2.x if res2.fun <= res.fun else res.x
    H = num_hess(lambda t: nb_nll(t, X, y, off), th); cov = np.linalg.inv(H)
    return th[:-1], np.sqrt(np.diag(cov))[:-1], float(np.exp(th[-1])), float(min(res.fun, res2.fun))

def run_models(df, xcol, tag):
    dd = df.dropna(subset=[xcol])
    y = dd.cases_2yr.values.astype(float); off = np.log(dd.person_years_2yr.values)
    X = np.column_stack([np.ones(len(dd)), dd[xcol].values])  # slope = per 1 percentage point
    b, se, mu = pois_fit(X, y, off)
    pear = float(np.sum((y - mu) ** 2 / mu) / (len(y) - 2))
    out = {"n": int(len(dd)), "poisson_irr_per_1pt": float(np.exp(b[1])),
           "poisson_irr_lo": float(np.exp(b[1] - 1.96 * se[1])), "poisson_irr_hi": float(np.exp(b[1] + 1.96 * se[1])),
           "poisson_p_robust": float(2 * stats.norm.sf(abs(b[1] / se[1]))), "poisson_pearson_dispersion": pear}
    bn, sen, alpha, nll = nb_fit(X, y, off)
    out.update({"nb_irr_per_1pt": float(np.exp(bn[1])), "nb_irr_lo": float(np.exp(bn[1] - 1.96 * sen[1])),
                "nb_irr_hi": float(np.exp(bn[1] + 1.96 * sen[1])), "nb_p": float(2 * stats.norm.sf(abs(bn[1] / sen[1]))),
                "nb_alpha": alpha, "nb_coef": float(bn[1]), "nb_intercept": float(bn[0])})
    R[f"model_{tag}"] = out
    return bn

bn_main = run_models(d, "mmr_mean", "mmr_all")
run_models(d[d.index != top_state], "mmr_mean", "mmr_drop_top_case_state")
run_models(d, "nme_mean", "nme_all")
run_models(d[d.index != top_state], "nme_mean", "nme_drop_top_case_state")

# ---------------------------------------------------------------- figure (Okabe-Ito, color-blind safe)
BL, OR, VR, GR = "#0072B2", "#D55E00", "#009E73", "#555555"
plt.rcParams.update({"font.size": 12, "font.family": "DejaVu Sans"})
fig, ax = plt.subplots(figsize=(9, 6.2))
ok = d.dropna(subset=["mmr_mean"])
ax.scatter(ok.mmr_mean, ok.rate_per_million_2yr, s=48, color=BL, alpha=.85, edgecolor="white", lw=.6, zorder=3)
xs = np.linspace(ok.mmr_mean.min() - .3, ok.mmr_mean.max() + .3, 200)
nb = R["model_mmr_all"]
ys = np.exp(nb["nb_intercept"] + nb["nb_coef"] * xs) * 1e6   # NB fitted rate (offset = person-years, per million)
ax.plot(xs, ys, color=OR, lw=2.4, label="Negative binomial fitted rate", zorder=2)
ax.axvline(95, color=GR, ls="--", lw=1.2); ax.text(95.1, ax.get_ylim()[1] * .93, "95% herd-immunity\nbenchmark", color=GR, fontsize=10, va="top")
lab = ok.sort_values("rate_per_million_2yr", ascending=False).head(6).index.tolist()
for s_ in lab:
    ax.annotate(s_, (ok.mmr_mean[s_], ok.rate_per_million_2yr[s_]), xytext=(6, 5), textcoords="offset points", fontsize=10)
ax.set_xlabel("Mean kindergarten MMR coverage, school years 2023-24 and 2024-25 (%)")
ax.set_ylabel("Confirmed measles cases per million\nperson-years, 2024-2025")
ax.set_title("State kindergarten MMR coverage and measles incidence", fontsize=13, loc="left")
ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.97)); ax.grid(alpha=.25, zorder=0)
for sp_ in ("top", "right"): ax.spines[sp_].set_visible(False)
fig.text(.01, .005, "Sources: CDC SchoolVaxView (data.cdc.gov, ijqb-a7ye); CDC measles state counts (as of Nov 5, 2026); U.S. Census Bureau Vintage 2025 estimates.",
         fontsize=7.5, color=GR)
fig.tight_layout(rect=(0, .03, 1, 1))
fig.savefig(os.path.join(OUT, "figure1_mmr_vs_measles.png"), dpi=300); plt.close(fig)
R["figure_labeled_states"] = lab

# ---------------------------------------------------------------- extra descriptives for the full paper
nm = d.nme_mean.dropna()
R["desc"] = {
    "mmr_mean_q1": float(d.mmr_mean.quantile(.25)), "mmr_mean_q3": float(d.mmr_mean.quantile(.75)),
    "mmr_states_below_90": int((d.mmr_mean < 90).sum()), "mmr_states_at_or_above_95": int((d.mmr_mean >= 95).sum()),
    "nme_n": int(len(nm)), "nme_median": float(nm.median()), "nme_min": float(nm.min()), "nme_max": float(nm.max()),
    "nme_q1": float(nm.quantile(.25)), "nme_q3": float(nm.quantile(.75)),
    "rate_q1": float(d.rate_per_million_2yr.quantile(.25)), "rate_q3": float(d.rate_per_million_2yr.quantile(.75)),
    "rate_max": float(d.rate_per_million_2yr.max()),
    "states_ge_1_case_2yr": int((d.cases_2yr > 0).sum()),
    "states_ge_100_cases_2yr": int((d.cases_2yr >= 100).sum()),
    "share_cases_in_states_ge100": float(d[d.cases_2yr >= 100].cases_2yr.sum() / d.cases_2yr.sum()),
    "cases_2026_partial_total": int(d.cases_2026_partial.sum()),
    "mmr_below95_rate_median": float(d[d.mmr_mean < 95].rate_per_million_2yr.median()),
    "mmr_at_or_above95_rate_median": float(d[d.mmr_mean >= 95].rate_per_million_2yr.median()),
    "n_with_mmr_below95": int((d.mmr_mean < 95).sum()), "n_with_mmr_at_or_above95": int((d.mmr_mean >= 95).sum()),
}
top = d.sort_values("rate_per_million_2yr", ascending=False).head(6)[["cases_2yr", "rate_per_million_2yr", "mmr_mean", "nme_mean"]].round(2)
top.to_csv(os.path.join(OUT, "top6_states_by_rate.csv"))
R["top6_states"] = top.reset_index().to_dict(orient="records")

# ---------------------------------------------------------------- save
json.dump(R, open(os.path.join(OUT, "results.json"), "w"), indent=2)
flat = []
def walk(k, o):
    if isinstance(o, dict):
        for kk, vv in o.items(): walk(f"{k}.{kk}" if k else kk, vv)
    else: flat.append((k, o))
walk("", R); pd.DataFrame(flat, columns=["quantity", "value"]).to_csv(os.path.join(OUT, "results.csv"), index=False)
print(json.dumps(R, indent=2))
