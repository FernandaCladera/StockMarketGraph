import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "image"
OUT.mkdir(exist_ok=True)

THRESHOLD = 0.6

# Plot Settings
SURFACE   = "#fcfcfb"
INK       = "#0b0b0b"
INK_2     = "#52514e"
INK_MUTED = "#8a8984"
GRID      = "#e8e7e3"
BLUE      = "#2a78d6"   
ORANGE    = "#eb6834"   
OTHER     = "#bfbeb9"   

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "text.color": INK,
    "axes.labelcolor": INK_2,
    "axes.edgecolor": GRID,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")

# Load data and build graph
stocks = pd.read_csv(ROOT / "data" / "stocks.csv")
corr   = pd.read_csv(ROOT / "data" / "correlation.csv")
sector = dict(zip(stocks.Symbol, stocks.Sector))

corr["pair"] = [tuple(sorted(p)) for p in zip(corr.stock_a, corr.stock_b)]
pairs = corr.drop_duplicates("pair")
edges = pairs[pairs.correlation > THRESHOLD]

G = nx.Graph()
G.add_nodes_from(stocks.Symbol)
G.add_weighted_edges_from(edges[["stock_a", "stock_b", "correlation"]].values)

components = sorted(nx.connected_components(G), key=len, reverse=True)
largest = G.subgraph(components[0])
isolated = [n for n, d in G.degree if d == 0]
connected = G.subgraph([n for n, d in G.degree if d > 0])

print(f"{G.number_of_nodes()} nodes | {G.number_of_edges()} unique pairs "
      f"({G.number_of_edges()*2} directed) | {len(components)} components | "
      f"largest {largest.number_of_nodes()} nodes | {len(isolated)} isolated")

def colour(sym):
    s = sector.get(sym, "")
    if s == "Financials":
        return BLUE
    if s == "Industrials":
        return ORANGE
    return OTHER

# Distribution of distance correlations
fig, ax = plt.subplots(figsize=(8, 4.2))
bins = np.linspace(pairs.correlation.min(), pairs.correlation.max(), 71)
below = pairs.correlation[pairs.correlation <= THRESHOLD]
above = pairs.correlation[pairs.correlation > THRESHOLD]
ax.hist(below, bins=bins, color="#cfceca", edgecolor=SURFACE, linewidth=0.4,
        label="discarded")
ax.hist(above, bins=bins, color=BLUE, edgecolor=SURFACE, linewidth=0.4,
        label="kept as edges")
ax.axvline(THRESHOLD, color=INK, linewidth=1.6)
ax.annotate(f"threshold {THRESHOLD}\n{len(above)} pairs kept of {len(pairs):,}",
            xy=(THRESHOLD + 0.012, ax.get_ylim()[1] * 0.74),
            color=INK, fontsize=9.5, va="center")
ax.legend(frameon=False, fontsize=9, labelcolor=INK_2, loc="upper left")
ax.set_xlabel("Distance correlation between daily log returns")
ax.set_ylabel("Stock pairs")
kept_pct= len(above)/len(pairs) *100

ax.set_title(f"{kept_pct:.1f}% of pairs exceed the correlation threshold", color=INK,
             fontsize=12, loc="left", pad=12)
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
save(fig, "01_correlation_distribution.png")

# Compare sector and Louvain community assigments
COMMUNITY_12 = ["AIG", "AXP", "BAC", "BK", "BLK", "BRK-B", "C", "COF",
                "GS", "JPM", "MS", "SCHW", "USB", "WFC"]
COMMUNITY_9  = ["CAT", "DE", "DOW", "EMR", "HON", "MET", "MMM"]
assert set(COMMUNITY_12) | set(COMMUNITY_9) == set(largest.nodes)

btw = {n: v * 2 for n, v in nx.betweenness_centrality(largest, normalized=False).items()}
POS = nx.spring_layout(largest, seed=11, k=0.9, iterations=800)

def component_figure(colours, legend, title, subtitle, highlight_met, name):
    fig, ax = plt.subplots(figsize=(8.2, 6.0))
    nx.draw_networkx_edges(largest, POS, ax=ax, edge_color="#dedcd7", width=1.1)
    nx.draw_networkx_nodes(
        largest, POS, ax=ax,
        node_color=[colours[n] for n in largest.nodes],
        node_size=[210 + 6.5 * btw[n] for n in largest.nodes],
        edgecolors=SURFACE, linewidths=2.2,
    )
    if highlight_met:
        nx.draw_networkx_nodes(largest, POS, ax=ax, nodelist=["MET"],
                               node_color="none",
                               node_size=210 + 6.5 * btw["MET"] + 900,
                               edgecolors=INK, linewidths=1.5)
    nx.draw_networkx_labels(largest, POS, ax=ax, font_size=7.8, font_color=INK)
    ax.legend(handles=[
        plt.Line2D([], [], marker="o", linestyle="", markersize=9,
                   markerfacecolor=c, markeredgecolor=SURFACE, label=l)
        for c, l in legend],
        loc="upper left", frameon=False, fontsize=9, labelcolor=INK_2)
    ax.set_title(title, color=INK, fontsize=12, loc="left", pad=10)
    ax.text(0, -0.03, subtitle, transform=ax.transAxes,
            color=INK_MUTED, fontsize=8.5, va="top")
    ax.axis("off")
    save(fig, name)

component_figure(
    colours={n: colour(n) for n in largest.nodes},
    legend=[(BLUE, "Financials (15)"), (ORANGE, "Industrials (5)"),
            (OTHER, "Materials (1)")],
    title="Coloured by GICS sector",
    subtitle=("Largest connected component: 21 stocks, "
              f"{largest.number_of_edges()} pairs \u00b7 node size = betweenness"),
    highlight_met=False, name="02_component_by_sector.png")

community_colour = {**{n: BLUE for n in COMMUNITY_12},
                    **{n: ORANGE for n in COMMUNITY_9}}
component_figure(
    colours=community_colour,
    legend=[(BLUE, "Community 12 \u2014 banking & capital markets (14)"),
            (ORANGE, "Community 9 \u2014 industrials (7)")],
    title="Largest component by Louvain Community",
    subtitle=("Communities computed in 2_graph.ipynb \u00b7 "
              "MetLife highlighted for comparison with its GICS sector"),
    highlight_met=True, name="03_component_by_community.png")

# Compare eigenvector and betweenness centrality
# Eigenvector values are taken from the saved output of 2_graph.ipynb
EIGEN = [("JPM", 0.2837), ("MET", 0.2828), ("BK", 0.2767), ("MS", 0.2767),
         ("BAC", 0.2767), ("BRK-B", 0.2764), ("USB", 0.2672), ("WFC", 0.2672),
         ("GS", 0.2656), ("AXP", 0.2631)]
btw_all = {n: v * 2 for n, v in nx.betweenness_centrality(G, normalized=False).items()}
BTW = sorted(btw_all.items(), key=lambda kv: -kv[1])[:10]

fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.4))
for ax, data, label, note in (
    (axes[0], EIGEN, "Eigenvector centrality", "Top 10 Stocks"),
    (axes[1], BTW,   "Betweenness centrality", "Top 10 Stocks"),
):
    names = [n for n, _ in data][::-1]
    vals  = [v for _, v in data][::-1]
    ax.barh(names, vals, color=[colour(n) for n in names],
            height=0.62, edgecolor=SURFACE, linewidth=1.2)
    for y, (n, v) in enumerate(zip(names, vals)):
        ax.text(v + max(vals) * 0.02, y, f"{v:,.3f}".rstrip("0").rstrip(".") if v < 1 else f"{v:,.1f}".rstrip("0").rstrip("."),
                va="center", fontsize=8.5, color=INK_2)
    ax.set_xlim(0, max(vals) * 1.22)
    ax.set_title(label, color=INK, fontsize=11.5, loc="left", pad=16)
    ax.text(0, 1.02, note, transform=ax.transAxes,
            color=INK_MUTED, fontsize=9, va="bottom")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, labelsize=9)
fig.suptitle("Top stocks by centrality measure",
             color=INK, fontsize=12.5, x=0.005, ha="left", y=1.06)
fig.tight_layout()
save(fig, "04_centrality_comparison.png")

print("completed :)")

