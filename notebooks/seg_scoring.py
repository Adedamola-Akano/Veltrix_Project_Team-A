"""Frozen scoring for the Veltrix segmentation model (seg-v1.0).

WHY THIS EXISTS
A segmentation is only useful if "Young renters" means the same thing next month. So new customers are
NOT re-clustered. They are scored with settings frozen at the time the model was built: the same scaling,
the same fill values, the same category lists, and the cluster centres (centroids). A customer is assigned
to the nearest centroid inside their own intent group (Rent or Buy), exactly as the model was built.

HOW IT IS USED
    params = seg_scoring.fit_params(raw_features, mixed_matrix, labels)   # once, when the model is built
    labels = seg_scoring.score(raw_features_new, params)                  # every month
    seg_scoring.drift_table(labels, params["baseline_share"])             # segment-size drift (20% rule)
    seg_scoring.quality_report(raw_features_new, params)                  # data quality checks

`raw_features` is the table written by notebook 04 (`customer_features.parquet`), indexed by customer_id.
`mixed_matrix` is `customer_features_mixed.parquet` (used only to learn WHICH columns the model uses).
"""
import re
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

LOG_COLS = ["n_sessions", "n_views", "n_leads", "n_interactions",
            "n_viewings", "mean_pages", "mean_duration_min"]
FLAGS = ["has_sessions", "has_views", "budget_missing",
         "consent_marketing", "is_overseas"]
SHARE_RE = re.compile(r"(share_|src_|vt_|vr_|ch_|evt_)")
BROWSING_COUNTS = ["n_sessions", "mean_pages", "mean_duration_min"]
VIEW_COUNTS = ["n_views"]
# weight of each one-hot category variable (see notebook 06)
W_CAT = 0.7071
KNOWN_CATS = ["customer_type", "gender", "occupation_sector", "buyer_position", "finance_type",
              "preferred_currency", "primary_lead_source", "uk_region_of_residence", "country_iso"]


# ----------------------------------------------------------------------------------------------- transforms
def _numeric_pre(raw, p):
    """Numeric model features before z-scoring (same steps as notebook 04)."""
    X = pd.DataFrame(index=raw.index)
    for c in p["share_cols"]:
        X[c] = raw[c].fillna(p["share_median"][c])
    for c in p["log_cols"]:
        X[c] = np.log1p(raw[c].fillna(0))
    mu = raw["primary_intent"].map(p["lb_mean"])
    sd = raw["primary_intent"].map(p["lb_std"])
    X["budget_z"] = (raw["log_budget"] - mu) / sd
    ordinal = raw["age_band"].map(p["age_map"])
    X["age_missing"] = ordinal.isna().astype(int)
    X["age_ord"] = ordinal.fillna(p["age_median"])
    for c in p["flag_cols"]:
        X[c] = raw[c].astype(int)
    return X[p["numeric_order"]]


def _numeric_scaled(raw, p):
    X = _numeric_pre(raw, p)
    cont = p["cont_cols"]
    X[cont] = (X[cont] - pd.Series(p["z_mean"])) / pd.Series(p["z_std"])
    return X


def _cats(raw, p):
    c = pd.DataFrame(index=raw.index)
    c["customer_type"] = raw["customer_type"].fillna("Unknown")
    c["gender"] = raw["gender"].fillna("Unknown")
    c["occupation_sector"] = raw["occupation_sector"].fillna("Unknown")
    c["country_group"] = raw["country_iso"].where(
        raw["country_iso"].isin(p["top_countries"]), "Other").fillna("Unknown")
    c["uk_region"] = raw["uk_region_of_residence"].fillna(pd.Series(
        np.where(raw["is_overseas"], "Overseas", "Unknown"), index=raw.index))
    c["buyer_position"] = raw["buyer_position"].fillna("Unknown")
    c["finance_type"] = raw["finance_type"].fillna("Unknown")
    c["primary_intent"] = raw["primary_intent"].fillna("Unknown")
    c["preferred_currency"] = raw["preferred_currency"].where(
        raw["preferred_currency"].isin(p["top_currencies"]), "Other").fillna("Unknown")
    c["primary_lead_source"] = raw["primary_lead_source"].fillna("No lead")
    return c


def model_matrix(raw, p):
    """The matrix the clusters live in (notebook 06 / 07): corrected browsing fill, weighted categories."""
    Xs = _numeric_scaled(raw, p)
    no_sess, no_view = raw["has_sessions"].eq(0), raw["has_views"].eq(0)
    Xn = Xs.drop(columns=["has_sessions", "has_views"], errors="ignore").copy()
    for c in BROWSING_COUNTS:
        if c in Xn:
            Xn.loc[no_sess, c] = p["fill_sessions"][c]
    for c in VIEW_COUNTS:
        if c in Xn:
            Xn.loc[no_view, c] = p["fill_views"][c]
    Xc = pd.get_dummies(_cats(raw, p), dtype=float).reindex(
        columns=p["dummy_cols"], fill_value=0.0) * W_CAT
    return pd.concat([Xn, Xc], axis=1)


# ----------------------------------------------------------------------------------------------- fitting
def fit_params(raw, mixed, labels):
    """Learn and freeze everything needed to score new customers. Call once, on the training population."""
    p = {}
    num_cols = [c for c in mixed.columns if is_numeric_dtype(mixed[c])]
    p["numeric_order"] = num_cols
    p["share_cols"] = [c for c in num_cols if SHARE_RE.match(c)]
    p["log_cols"] = [c for c in num_cols if c in LOG_COLS]
    p["flag_cols"] = [c for c in num_cols if c in FLAGS]
    covered = set(p["share_cols"]) | set(p["log_cols"]) | set(
        p["flag_cols"]) | {"budget_z", "age_ord", "age_missing"}
    unknown = [c for c in num_cols if c not in covered]
    assert not unknown, f"Model columns this module does not know how to rebuild: {unknown}"

    p["share_median"] = {c: float(raw[c].median()) for c in p["share_cols"]}
    order = sorted(raw["age_band"].dropna().unique(),
                   key=lambda s: int(re.search(r"\d+", s).group()))
    p["age_map"] = {a: i for i, a in enumerate(order)}
    p["age_median"] = float(raw["age_band"].map(p["age_map"]).median())
    g = raw.groupby("primary_intent")["log_budget"]
    p["lb_mean"], p["lb_std"] = g.mean().to_dict(), g.std().to_dict()

    pre = _numeric_pre(raw, p)
    binary = [c for c in pre.columns if set(
        pre[c].dropna().unique()) <= {0, 1}]
    p["cont_cols"] = [c for c in pre.columns if c not in binary]
    p["z_mean"], p["z_std"] = pre[p["cont_cols"]].mean(
    ).to_dict(), pre[p["cont_cols"]].std().to_dict()

    Xs = _numeric_scaled(raw, p)
    has_s, has_v = raw["has_sessions"].ne(0), raw["has_views"].ne(0)
    p["fill_sessions"] = {c: float(Xs.loc[has_s, c].median())
                          for c in BROWSING_COUNTS if c in Xs}
    p["fill_views"] = {c: float(Xs.loc[has_v, c].median())
                       for c in VIEW_COUNTS if c in Xs}

    p["top_countries"] = list(raw["country_iso"].value_counts().head(8).index)
    p["top_currencies"] = list(
        raw["preferred_currency"].value_counts().head(4).index)
    p["dummy_cols"] = list(pd.get_dummies(_cats(raw, p), dtype=float).columns)

    M = model_matrix(raw, p)
    labels = labels.loc[raw.index].astype(str)
    p["centroids"], p["labels_by_intent"] = {}, {}
    for lab in sorted(labels.unique()):
        members = labels.index[labels == lab]
        intents = raw.loc[members, "primary_intent"].unique()
        assert len(
            intents) == 1, f"Cluster {lab} mixes intents {list(intents)}: the scorer assumes the two-stage model"
        p["centroids"][lab] = M.loc[members].mean().to_numpy()
        p["labels_by_intent"].setdefault(intents[0], []).append(lab)
    p["M_columns"] = list(M.columns)
    p["baseline_share"] = labels.value_counts(normalize=True).to_dict()
    p["n_training"] = int(len(raw))

    p["known_categories"] = {c: sorted(raw[c].dropna().astype(
        str).unique()) for c in KNOWN_CATS if c in raw}
    p["quality_baseline"] = {
        "age_band missing %": raw["age_band"].isna().mean() * 100,
        "occupation_sector missing %": raw["occupation_sector"].isna().mean() * 100,
        "gender missing %": raw["gender"].isna().mean() * 100,
        "no web sessions %": (raw["has_sessions"] == 0).mean() * 100,
        "no property views %": (raw["has_views"] == 0).mean() * 100,
        "budget missing %": raw["budget_missing"].mean() * 100,
        "no lead %": (raw["n_leads"] == 0).mean() * 100,
        "overseas %": raw["is_overseas"].astype(float).mean() * 100,
    }
    return p


# ----------------------------------------------------------------------------------------------- scoring
def score(raw, p):
    """Assign each customer to the nearest centroid inside their intent group. Returns segment ids."""
    M = model_matrix(raw, p)[p["M_columns"]]
    out = pd.Series("UNASSIGNED", index=raw.index, dtype=object)
    for intent, labs in p["labels_by_intent"].items():
        idx = raw.index[raw["primary_intent"].eq(intent).to_numpy()]
        if not len(idx):
            continue
        C = np.vstack([p["centroids"][lab] for lab in labs])
        X = M.loc[idx].to_numpy()
        d = (X ** 2).sum(1)[:, None] - 2 * X @ C.T + (C ** 2).sum(1)[None, :]
        out.loc[idx] = np.array(labs, dtype=object)[d.argmin(1)]
    return out


# ----------------------------------------------------------------------------------------------- monitoring
def drift_table(labels, baseline_share, threshold=0.20):
    """Segment-size drift against the baseline (the DA plan's 20% rule).

    relative_change_% compares each segment's SHARE of customers with its share at model build, so growth in
    the total number of customers does not cause an alert by itself. noise_% is the sampling error to expect
    for a batch of this size: small batches wobble, so an alert needs to exceed both 20% and the noise.
    """
    n = len(labels)
    share = labels.value_counts(normalize=True)
    base = pd.Series(baseline_share)
    t = pd.DataFrame({"baseline_share_%": base * 100,
                     "share_%": share * 100}).fillna(0.0)
    t["customers"] = labels.value_counts().reindex(
        t.index).fillna(0).astype(int)
    t["relative_change_%"] = (t["share_%"] / t["baseline_share_%"] - 1) * 100
    b = t["baseline_share_%"] / 100
    t["noise_%"] = 1.96 * np.sqrt((1 - b) / (b * max(n, 1))) * 100
    t["alert"] = t["relative_change_%"].abs() > np.maximum(
        threshold * 100, t["noise_%"])
    return t.round(2)


def quality_report(raw, p, tolerance_points=5.0):
    """Data quality checks on a batch of features. FAIL means stop and investigate before publishing."""
    rows = []

    def add(check, value, baseline, ok, note=""):
        rows.append({"check": check, "value": value, "baseline": baseline,
                    "status": "PASS" if ok else "FAIL", "note": note})

    add("customer_id is unique", int(raw.index.is_unique), 1, raw.index.is_unique)
    missing_cols = [c for c in set(p["numeric_order"]) | {"primary_intent", "age_band", "log_budget", "primary_lead_source",
                                                          "country_iso"} if c not in raw.columns and c not in ("budget_z", "age_ord", "age_missing")]
    add("all columns the model needs are present", len(missing_cols),
        0, not missing_cols, ", ".join(sorted(missing_cols)))
    add("every customer has intent Buy or Rent", int((~raw["primary_intent"].isin(p["labels_by_intent"])).sum()), 0,
        raw["primary_intent"].isin(p["labels_by_intent"]).all(), "customers with another intent cannot be scored")
    add("log_budget is a finite number for every customer", int(
        (~np.isfinite(raw["log_budget"])).sum()), 0, np.isfinite(raw["log_budget"]).all())

    current = {
        "age_band missing %": raw["age_band"].isna().mean() * 100,
        "occupation_sector missing %": raw["occupation_sector"].isna().mean() * 100,
        "gender missing %": raw["gender"].isna().mean() * 100,
        "no web sessions %": (raw["has_sessions"] == 0).mean() * 100,
        "no property views %": (raw["has_views"] == 0).mean() * 100,
        "budget missing %": raw["budget_missing"].mean() * 100,
        "no lead %": (raw["n_leads"] == 0).mean() * 100,
        "overseas %": raw["is_overseas"].astype(float).mean() * 100,
    }
    for k, v in current.items():
        b = p["quality_baseline"][k]
        add(f"{k} within {tolerance_points:.0f} points of the build",
            round(v, 2), round(b, 2), abs(v - b) <= tolerance_points)

    for col, known in p["known_categories"].items():
        if col in raw:
            new = sorted(set(raw[col].dropna().astype(str)) - set(known))
            add(f"no new values in {col}", len(new),
                0, not new, ", ".join(new[:5]))
    return pd.DataFrame(rows)
