"""Automatic insight bullets from the current slice (no Streamlit)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def safe_pearson_r(x: object, y: object) -> float | None:
    """Pearson r or None if undefined (too few points or zero variance)."""
    xv = np.asarray(x, dtype=np.float64).ravel()
    yv = np.asarray(y, dtype=np.float64).ravel()
    mask = np.isfinite(xv) & np.isfinite(yv)
    if int(mask.sum()) < 2:
        return None
    xs = xv[mask]
    ys = yv[mask]
    if float(np.std(xs)) < 1e-15 or float(np.std(ys)) < 1e-15:
        return None
    try:
        r = float(np.corrcoef(xs, ys)[0, 1])
        return r if np.isfinite(r) else None
    except Exception:
        return None


def compute_insights(
    df: pd.DataFrame,
    df_y: pd.DataFrame,
    year: int,
    sel_countries: list[str],
    tw0: int,
    tw1: int,
    x_metric: str,
    x_label: str,
    lang: str = "en",
    *,
    include_cross_section: bool = True,
) -> list[str]:
    """Return 3–5 short markdown-safe lines.

    When ``include_cross_section`` is False, only trend-pick bullets are returned
    (requires non-empty ``sel_countries``); ``df_y`` / ``x_metric`` are unused.
    """
    out: list[str] = []
    if include_cross_section:
        if len(df_y) < 3:
            return out
    elif not sel_countries:
        return out

    if include_cross_section:
        r_val = safe_pearson_r(df_y[x_metric].values, df_y["Happiness"].values)
        if r_val is None:
            if lang == "es":
                out.append(
                    f"**{year}** · correlación de Pearson **no definida** (poca variación en X o Y en este corte)."
                )
            else:
                out.append(
                    f"**{year}** · Pearson **r** is **n/a** (little variation in X or Y in this slice)."
                )
        elif lang == "es":
            out.append(
                f"**{year}** · correlación Pearson **r ≈ {r_val:.2f}** entre **{x_label}** y evaluación de vida (solo asociación)."
            )
        else:
            out.append(
                f"**{year}** · Pearson **r ≈ {r_val:.2f}** between **{x_label}** and life evaluation (association only)."
            )

        top = df_y.nlargest(1, "Happiness")
        if len(top):
            row = top.iloc[0]
            if lang == "es":
                out.append(f"Máxima evaluación en **{year}**: **{row['Country']}** ({row['Happiness']:.2f}).")
            else:
                out.append(f"Highest life evaluation in **{year}**: **{row['Country']}** ({row['Happiness']:.2f}).")

    if sel_countries:
        best_c, best_d = None, -1e9
        worst_c, worst_d = None, 1e9
        for c in sel_countries:
            g = df[(df["Country"] == c) & (df["Year"] >= tw0) & (df["Year"] <= tw1)].sort_values("Year")
            if len(g) < 2:
                continue
            d = float(g["Happiness"].iloc[-1] - g["Happiness"].iloc[0])
            if d > best_d:
                best_d, best_c = d, c
            if d < worst_d:
                worst_d, worst_c = d, c
        if best_c is not None and lang == "en":
            out.append(
                f"Largest **improvement** in selected window ({tw0}–{tw1}) among picks: **{best_c}** (Δ ≈ {best_d:+.2f})."
            )
        elif best_c is not None:
            out.append(
                f"Mayor **mejora** en la ventana ({tw0}–{tw1}) entre los elegidos: **{best_c}** (Δ ≈ {best_d:+.2f})."
            )
        if worst_c is not None and worst_c != best_c:
            if lang == "en":
                out.append(f"Largest **decline** among picks: **{worst_c}** (Δ ≈ {worst_d:+.2f}).")
            else:
                out.append(f"Mayor **caída** entre los elegidos: **{worst_c}** (Δ ≈ {worst_d:+.2f}).")

    if include_cross_section:
        rng = float(df_y["Happiness"].max() - df_y["Happiness"].min())
        if lang == "es":
            out.append(f"Banda **{year}** (max − min entre países): **{rng:.2f}** puntos de escala.")
        else:
            out.append(f"Cross-country spread in **{year}** (max − min): **{rng:.2f}** ladder points.")

    return out[:5]
