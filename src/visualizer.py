"""
Visualization & Evidence Generation Module for Mini-Courier Planner.
Submitted by: Prachi Manwal (Roll No: 2501730365)

Generates high-resolution charts and console execution screenshots in `images/`
covering all 5 Capstone Phases with student attribution.
"""

from pathlib import Path
from typing import Any, Dict, List
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from src.models import PackingResult, Parcel, RouteResult
from src.graph_routing import CustomerGraph

STUDENT_CREDIT = "Submitted by: Prachi Manwal | Roll No: 2501730365"


def plot_phase1_architecture(output_path: str | Path) -> None:
    """Renders Phase 1 System Architecture & Algorithmic Pipeline diagram."""
    fig, ax = plt.subplots(figsize=(13.2, 5.6), dpi=180)
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 5.6)
    ax.axis("off")
    fig.patch.set_facecolor("#FAF5FF")

    ax.text(
        6.6, 5.15,
        "Mini-Courier Planner: End-to-End Algorithmic Architecture (Phase 1 Design)",
        ha="center", va="center", fontsize=14.5, fontweight="bold", color="#1E1B4B"
    )
    ax.text(
        6.6, 4.73,
        f"{STUDENT_CREDIT}  •  Sorting (Merge Sort) + 0/1 Knapsack DP + Dijkstra + Nearest-Neighbor TSP",
        ha="center", va="center", fontsize=10, fontweight="bold", color="#6D28D9"
    )

    stages = [
        (0.45, 1.4, 2.45, 2.75, "#312E81", "#EEF2FF", "STAGE 1: INPUT DATA",
         "• MetroSwift Manifest CSV\n  (16 Parcels, Weight, SLA,\n   Priority, Value Score)\n• City Road Graph CSV\n  (|V|=12 Nodes, |E|=24)\n• Van Capacity W = 35 kg"),
        (3.4, 1.4, 2.65, 2.75, "#0F766E", "#CCFBF1", "STAGE 2A: SORTING",
         "• Algorithm: Merge Sort\n• Complexity: O(n log n)\n• Property: Stable Sort\n• Multi-Key Comparator:\n  1. Priority Tier (ASC)\n  2. SLA Deadline (ASC)\n  3. Value Score (DESC)"),
        (6.55, 1.4, 2.85, 2.75, "#B45309", "#FEF3C7", "STAGE 2B: 0/1 KNAPSACK DP",
         "• Algorithm: Bottom-Up DP\n• Complexity: O(n · W)\n• State: dp[i][w] Max Value\n• Backtracking selects\n  optimal parcel subset\n  fitting W <= 35 kg\n• Output: 9 Packed Items"),
        (9.9, 1.4, 2.85, 2.75, "#BE185D", "#FCE7F3", "STAGE 3: GRAPH & TSP",
         "• Dijkstra All-Pairs Shortest\n  Paths: O(k·(V+E) log V)\n• Nearest-Neighbor TSP\n  Approximation: O(k²)\n• 2-Opt Local Refinement\n• Output: Optimal Tour"),
    ]

    for x, y, w, h, hdr_col, body_col, title, body in stages:
        rect_body = mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
            facecolor=body_col, edgecolor=hdr_col, linewidth=2
        )
        ax.add_patch(rect_body)
        rect_hdr = mpatches.FancyBboxPatch(
            (x, y + h - 0.55), w, 0.55, boxstyle="round,pad=0.08,rounding_size=0.12",
            facecolor=hdr_col, edgecolor=hdr_col, linewidth=1
        )
        ax.add_patch(rect_hdr)
        ax.text(x + w / 2, y + h - 0.27, title, ha="center", va="center",
                fontsize=9.5, fontweight="bold", color="white")
        ax.text(x + 0.14, y + h - 0.80, body, ha="left", va="top",
                fontsize=8.6, color="#0F172A", linespacing=1.42, family="monospace")

    arrow_xs = [(2.98, 3.32), (6.13, 6.47), (9.48, 9.82)]
    for x0, x1 in arrow_xs:
        ax.annotate(
            "", xy=(x1, 2.77), xytext=(x0, 2.77),
            arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.35", lw=2.5, color="#312E81")
        )

    banner = mpatches.FancyBboxPatch(
        (0.45, 0.35), 12.3, 0.72, boxstyle="round,pad=0.06,rounding_size=0.12",
        facecolor="#EDE9FE", edgecolor="#6D28D9", linewidth=1.8
    )
    ax.add_patch(banner)
    ax.text(
        6.6, 0.71,
        "PHASE 4 & 5 EVALUATION: Empirical Scalability Benchmarks (Small N=25, Medium N=120, Large N=500) + Complexity Analysis + Visual Report",
        ha="center", va="center", fontsize=9.4, fontweight="bold", color="#4C1D95"
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_phase2_knapsack_and_prioritization(
    sorted_parcels: List[Parcel],
    packing_dp: PackingResult,
    packing_greedy: PackingResult,
    output_path: str | Path,
) -> None:
    """Renders Phase 2 visual evidence (Prioritized Parcels + 0/1 Knapsack DP Table Heatmap)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.8, 7.2), dpi=180, gridspec_kw={"width_ratios": [1.08, 1.32]})
    fig.patch.set_facecolor("#FFFFFF")
    fig.suptitle(
        f"Phase 2: Parcel Prioritization & 0/1 Knapsack Dynamic Programming — {STUDENT_CREDIT}",
        fontsize=12, fontweight="bold", color="#1E1B4B", y=0.99
    )

    selected_ids = {p.parcel_id for p in packing_dp.selected_parcels}

    labels = [
        f"#{idx+1:02d} {p.parcel_id} (T{p.priority_tier}, {p.deadline_hrs}h, {p.weight_kg}kg -> {p.destination_id})"
        for idx, p in enumerate(sorted_parcels)
    ]
    values = [p.value_score for p in sorted_parcels]
    colors = ["#0D9488" if p.parcel_id in selected_ids else "#CBD5E1" for p in sorted_parcels]

    y_pos = np.arange(len(sorted_parcels))
    bars = ax1.barh(y_pos, values, color=colors, edgecolor="#1E293B", height=0.72, linewidth=0.8)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(labels, fontsize=8.3, family="monospace")
    ax1.invert_yaxis()
    ax1.set_xlabel("Parcel Priority Value Score", fontsize=10, fontweight="bold")
    ax1.set_title(
        f"Merge-Sorted Parcels & Box Selection (W = {packing_dp.capacity_kg} kg)\n"
        f"0/1 DP Value = {packing_dp.total_value_score} ({packing_dp.total_weight_kg}/{packing_dp.capacity_kg} kg) vs. Greedy = {packing_greedy.total_value_score} ({packing_greedy.total_weight_kg}/{packing_dp.capacity_kg} kg)",
        fontsize=10.2, fontweight="bold", pad=8
    )
    ax1.set_xlim(0, max(values) * 1.38)
    ax1.set_ylim(len(sorted_parcels) + 1.2, -0.8)
    ax1.grid(axis="x", linestyle="--", alpha=0.4)

    for bar, p in zip(bars, sorted_parcels):
        status = "PACKED" if p.parcel_id in selected_ids else "DEFERRED"
        ax1.text(
            bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
            f"v={p.value_score} ({status})",
            va="center", ha="left", fontsize=7.7,
            fontweight="bold" if status == "PACKED" else "normal",
            color="#0F766E" if status == "PACKED" else "#64748B",
        )

    packed_patch = mpatches.Patch(color="#0D9488", label=f"Selected by 0/1 DP ({len(packing_dp.selected_parcels)} parcels, {packing_dp.total_weight_kg} kg)")
    deferred_patch = mpatches.Patch(color="#CBD5E1", label=f"Deferred to Next Trip ({len(packing_dp.deferred_parcels)} parcels)")
    ax1.legend(handles=[packed_patch, deferred_patch], loc="lower right", fontsize=8.3)

    # Panel B: 0/1 Knapsack DP Table Heatmap
    dp_matrix = np.array(packing_dp.dp_table, dtype=float)
    im = ax2.imshow(dp_matrix, aspect="auto", cmap="PuBuGn", origin="upper")
    cbar = fig.colorbar(im, ax=ax2, fraction=0.042, pad=0.03)
    cbar.set_label("Cumulative Optimal Value Score dp[i][w]", fontsize=9.5, fontweight="bold")

    n_items, max_w_plus_1 = dp_matrix.shape
    row_labels = ["0: Empty"] + [f"{i}: {p.parcel_id} ({p.weight_kg}kg)" for i, p in enumerate(sorted_parcels, 1)]
    ax2.set_yticks(np.arange(n_items))
    ax2.set_yticklabels(row_labels, fontsize=7.8, family="monospace")
    col_ticks = np.arange(0, max_w_plus_1, 3)
    ax2.set_xticks(col_ticks)
    ax2.set_xticklabels([f"{w}" for w in col_ticks], fontsize=8)
    ax2.set_xlabel("Van Capacity w (kg)", fontsize=10, fontweight="bold")
    ax2.set_title(
        f"0/1 Knapsack DP State Table dp[i][w] ({n_items-1} Parcels × {max_w_plus_1-1} kg)\n"
        f"Crimson Trajectory Shows Backtracking Path from dp[{n_items-1}][{max_w_plus_1-1}] = {int(dp_matrix[-1, -1])}",
        fontsize=10.2, fontweight="bold", pad=8
    )

    rem_w = max_w_plus_1 - 1
    path_w = [rem_w]
    path_i = [n_items - 1]
    for i in range(n_items - 1, 0, -1):
        if dp_matrix[i, rem_w] != dp_matrix[i - 1, rem_w]:
            ax2.scatter([rem_w], [i], color="#E11D48", s=65, zorder=6, edgecolors="white", linewidth=1.2)
            rem_w -= sorted_parcels[i - 1].weight_kg
        path_w.append(rem_w)
        path_i.append(i - 1)

    ax2.plot(path_w, path_i, color="#E11D48", linewidth=2.3, linestyle="-", label="DP Backtracking Trajectory", zorder=5)
    for i in range(n_items):
        for w in range(0, max_w_plus_1, 5):
            val = int(dp_matrix[i, w])
            txt_col = "white" if val > dp_matrix.max() * 0.56 else "#0F172A"
            ax2.text(w, i, f"{val}", ha="center", va="center", fontsize=6.4, color=txt_col)

    ax2.legend(loc="lower left", fontsize=8.3)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_phase3_delivery_route(
    graph: CustomerGraph,
    nn_route: RouteResult,
    two_opt_route: RouteResult,
    output_path: str | Path,
) -> None:
    """Renders Phase 3 visual evidence (MetroSwift Road Network + Dijkstra Matrix)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.8, 7.0), dpi=180, gridspec_kw={"width_ratios": [1.25, 1.0]})
    fig.patch.set_facecolor("#FFFFFF")
    fig.suptitle(
        f"Phase 3: Customer Road Graph, Dijkstra Shortest Paths & Nearest-Neighbor TSP — {STUDENT_CREDIT}",
        fontsize=12, fontweight="bold", color="#1E1B4B", y=0.99
    )

    active_stops = set(nn_route.stop_sequence)

    for edge in graph.edges:
        u_node = graph.nodes[edge.source]
        v_node = graph.nodes[edge.target]
        ax1.plot(
            [u_node.x_km, v_node.x_km],
            [u_node.y_km, v_node.y_km],
            color="#CBD5E1", linewidth=1.6, linestyle="--", zorder=1
        )
        mx = (u_node.x_km + v_node.x_km) / 2.0
        my = (u_node.y_km + v_node.y_km) / 2.0
        ax1.text(
            mx, my, f"{edge.distance_km:.1f}km",
            fontsize=6.8, color="#64748B", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="none", alpha=0.75),
            zorder=2
        )

    leg_colors = plt.cm.viridis(np.linspace(0.1, 0.85, len(nn_route.legs)))
    for leg, col in zip(nn_route.legs, leg_colors):
        path_nodes = leg.intermediate_path
        for idx in range(len(path_nodes) - 1):
            n1 = graph.nodes[path_nodes[idx]]
            n2 = graph.nodes[path_nodes[idx + 1]]
            ax1.annotate(
                "",
                xy=(n2.x_km, n2.y_km),
                xytext=(n1.x_km, n1.y_km),
                arrowprops=dict(
                    arrowstyle="-|>,head_width=0.38,head_length=0.55",
                    color=col, lw=3.0, shrinkA=10, shrinkB=10
                ),
                zorder=4,
            )

    stop_order_map: Dict[str, int] = {}
    for order_idx, node_id in enumerate(nn_route.stop_sequence[:-1]):
        stop_order_map[node_id] = order_idx

    for node_id, node in graph.nodes.items():
        if node_id == "HUB":
            ax1.scatter([node.x_km], [node.y_km], s=380, color="#E11D48", edgecolors="#1E293B", linewidth=2.0, marker="s", zorder=6)
            ax1.text(node.x_km, node.y_km - 1.05, f"HUB: {node.node_name}\n(Start / Return)",
                     ha="center", va="top", fontsize=8.3, fontweight="bold", color="#9F1239",
                     bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFF1F2", edgecolor="#E11D48", lw=1))
        elif node_id in active_stops:
            order_num = stop_order_map[node_id]
            ax1.scatter([node.x_km], [node.y_km], s=310, color="#4F46E5", edgecolors="#0F172A", linewidth=1.8, zorder=6)
            ax1.text(node.x_km, node.y_km, f"#{order_num}", ha="center", va="center",
                     fontsize=8.3, fontweight="bold", color="white", zorder=7)
            ax1.text(node.x_km, node.y_km + 0.85, f"{node_id}: {node.node_name[:18]}",
                     ha="center", va="bottom", fontsize=7.8, fontweight="bold", color="#1E1B4B",
                     bbox=dict(boxstyle="round,pad=0.15", facecolor="#EEF2FF", edgecolor="#4F46E5", lw=0.8))
        else:
            ax1.scatter([node.x_km], [node.y_km], s=175, color="#E2E8F0", edgecolors="#64748B", linewidth=1.2, zorder=5)
            ax1.text(node.x_km, node.y_km + 0.65, f"{node_id} (Inactive)",
                     ha="center", va="bottom", fontsize=7.2, color="#64748B")

    tour_str = " -> ".join(nn_route.stop_sequence)
    ax1.set_title(
        f"MetroSwift Network & Nearest-Neighbor TSP Delivery Route\n"
        f"Stop Sequence: {tour_str} (Total = {nn_route.total_distance_km:.2f} km)",
        fontsize=10.0, fontweight="bold", pad=8
    )
    ax1.set_xlabel("East-West Coordinate (km)", fontsize=9.5, fontweight="bold")
    ax1.set_ylabel("North-South Coordinate (km)", fontsize=9.5, fontweight="bold")
    ax1.set_xlim(1.0, 22.0)
    ax1.set_ylim(2.0, 20.0)
    ax1.grid(True, linestyle=":", alpha=0.45)

    nodes_ordered = nn_route.stop_sequence[:-1]
    k = len(nodes_ordered)
    mat = np.zeros((k, k))
    for i, u in enumerate(nodes_ordered):
        for j, v in enumerate(nodes_ordered):
            mat[i, j] = nn_route.distance_matrix[u][v]

    im2 = ax2.imshow(mat, cmap="BuPu", aspect="auto")
    cbar2 = fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
    cbar2.set_label("Shortest Path Distance (km)", fontsize=9, fontweight="bold")

    ax2.set_xticks(np.arange(k))
    ax2.set_yticks(np.arange(k))
    ax2.set_xticklabels(nodes_ordered, fontsize=9, fontweight="bold")
    ax2.set_yticklabels(nodes_ordered, fontsize=9, fontweight="bold")
    ax2.set_title(
        f"All-Pairs Dijkstra Shortest-Path Matrix (km)\n"
        f"NN Tour = {nn_route.total_distance_km:.2f} km vs. 2-Opt Refined = {two_opt_route.total_distance_km:.2f} km",
        fontsize=10.0, fontweight="bold", pad=8
    )

    for i in range(k):
        for j in range(k):
            is_tour_step = (j == (i + 1) % k)
            val = mat[i, j]
            col = "white" if val > mat.max() * 0.55 else "#0F172A"
            box = dict(boxstyle="round,pad=0.18", facecolor="none", edgecolor="#E11D48", lw=2.0) if is_tour_step else None
            ax2.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=8.3,
                     fontweight="bold" if is_tour_step else "normal", color=col, bbox=box)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_phase4_runtime_charts(
    sorting_records: List[Dict[str, Any]],
    knapsack_records: List[Dict[str, Any]],
    routing_records: List[Dict[str, Any]],
    e2e_records: List[Dict[str, Any]],
    output_path: str | Path,
) -> None:
    """Renders a 4-panel Phase 4 Scalability & Runtime Comparison Dashboard."""
    fig, axes = plt.subplots(2, 2, figsize=(15.5, 10.6), dpi=180)
    fig.patch.set_facecolor("#FFFFFF")
    fig.suptitle(
        f"Phase 4: Performance Testing, Scalability Analysis & Module Comparison — {STUDENT_CREDIT}",
        fontsize=12.5, fontweight="bold", color="#1E1B4B", y=0.99
    )
    ax1, ax2, ax3, ax4 = axes.flatten()

    ns = [r["n"] for r in sorting_records]
    ax1.plot(ns, [r["merge_sort_ms"] for r in sorting_records], "o-", lw=2.4, color="#4F46E5", label="Merge Sort O(n log n) [Selected]")
    ax1.plot(ns, [r["quick_sort_ms"] for r in sorting_records], "s--", lw=2.0, color="#0D9488", label="Quick Sort O(n log n) Avg")
    ax1.plot(ns, [r["heap_sort_ms"] for r in sorting_records], "^-.", lw=2.0, color="#D97706", label="Heap Sort O(n log n)")
    ax1.plot(ns, [r["insertion_sort_ms"] for r in sorting_records], "d:", lw=2.2, color="#E11D48", label="Insertion Sort O(n²) Baseline")
    ax1.set_title("Phase 4A: Sorting Algorithm Runtime vs. Parcel Count (N)", fontsize=10.8, fontweight="bold")
    ax1.set_xlabel("Number of Parcels (N)", fontsize=9.5, fontweight="bold")
    ax1.set_ylabel("Execution Time (ms, log scale)", fontsize=9.5, fontweight="bold")
    ax1.set_yscale("log")
    ax1.grid(True, which="both", linestyle="--", alpha=0.4)
    ax1.legend(fontsize=8.5)

    k_labels = [f"N={r['n']}\nW={r['capacity_kg']}" for r in knapsack_records]
    x_k = np.arange(len(k_labels))
    width = 0.26
    ax2.bar(x_k - width, [r["dp_2d_ms"] for r in knapsack_records], width, color="#4F46E5", label="2D 0/1 Knapsack DP O(n·W)")
    ax2.bar(x_k, [r["dp_1d_ms"] for r in knapsack_records], width, color="#0D9488", label="1D Space-Optimized DP O(n·W)")
    ax2.bar(x_k + width, [r["greedy_ms"] for r in knapsack_records], width, color="#D97706", label="Greedy Heuristic O(n log n)")
    ax2.set_xticks(x_k)
    ax2.set_xticklabels(k_labels, fontsize=8.5)
    ax2.set_yscale("log")
    ax2.set_title("Phase 4B: Knapsack Packing Runtime across Problem Sizes (N, W)", fontsize=10.8, fontweight="bold")
    ax2.set_xlabel("Problem Scale (Parcels N, Capacity W kg)", fontsize=9.5, fontweight="bold")
    ax2.set_ylabel("Execution Time (ms, log scale)", fontsize=9.5, fontweight="bold")
    ax2.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax2.legend(fontsize=8.5)

    stops = [r["num_stops"] for r in routing_records]
    ax3.plot(stops, [r["dijkstra_ms"] for r in routing_records], "o-", lw=2.2, color="#4F46E5", label="Dijkstra All-Pairs Shortest Paths")
    ax3.plot(stops, [r["nn_tsp_ms"] for r in routing_records], "s-", lw=2.2, color="#0D9488", label="Nearest-Neighbor TSP O(k²)")
    ax3.plot(stops, [r["two_opt_tsp_ms"] for r in routing_records], "^--", lw=2.0, color="#D97706", label="NN + 2-Opt Local Search")

    hk_stops = [r["num_stops"] for r in routing_records if r["held_karp_ms"] is not None]
    hk_times = [r["held_karp_ms"] for r in routing_records if r["held_karp_ms"] is not None]
    ax3.plot(hk_stops, hk_times, "d-", lw=2.4, color="#E11D48", label="Held-Karp Exact TSP O(k²·2^k)")
    ax3.set_yscale("log")
    ax3.set_title("Phase 4C: Graph & TSP Routing Runtime vs. Active Stops (k)", fontsize=10.8, fontweight="bold")
    ax3.set_xlabel("Number of Active Customer Delivery Stops (k)", fontsize=9.5, fontweight="bold")
    ax3.set_ylabel("Execution Time (ms, log scale)", fontsize=9.5, fontweight="bold")
    ax3.grid(True, which="both", linestyle="--", alpha=0.4)
    ax3.legend(fontsize=8.5)

    ds_labels = [r["dataset_label"].split("(")[0].strip() + f"\n(N={r['n_parcels']}, W={r['capacity_kg']}kg)" for r in e2e_records]
    x_e = np.arange(len(ds_labels))
    sort_t = np.array([r["sort_ms"] for r in e2e_records])
    dp_t = np.array([r["knapsack_dp_ms"] for r in e2e_records])
    dijk_t = np.array([r["dijkstra_ms"] for r in e2e_records])
    tsp_t = np.array([r["tsp_ms"] for r in e2e_records])

    ax4.bar(x_e, sort_t, width=0.48, color="#6366F1", label="Phase 2A: Merge Sort")
    ax4.bar(x_e, dp_t, width=0.48, bottom=sort_t, color="#0D9488", label="Phase 2B: 0/1 Knapsack DP")
    ax4.bar(x_e, dijk_t, width=0.48, bottom=sort_t + dp_t, color="#EC4899", label="Phase 3A: Dijkstra Shortest Paths")
    ax4.bar(x_e, tsp_t, width=0.48, bottom=sort_t + dp_t + dijk_t, color="#F59E0B", label="Phase 3B: Nearest-Neighbor TSP")

    totals = sort_t + dp_t + dijk_t + tsp_t
    for idx, tot in enumerate(totals):
        ax4.text(idx, tot + max(totals) * 0.025, f"Total: {tot:.2f} ms", ha="center", va="bottom",
                 fontsize=9, fontweight="bold", color="#0F172A")

    ax4.set_xticks(x_e)
    ax4.set_xticklabels(ds_labels, fontsize=9, fontweight="bold")
    ax4.set_ylim(0, max(totals) * 1.18)
    ax4.set_title("Phase 4D: End-to-End Pipeline Runtime Breakdown by Dataset Scale", fontsize=10.8, fontweight="bold")
    ax4.set_ylabel("Cumulative Execution Time (ms)", fontsize=9.5, fontweight="bold")
    ax4.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax4.legend(fontsize=8.5, loc="upper left")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=180)
    plt.close(fig)


def render_console_screenshot(console_text: str, output_path: str | Path) -> None:
    """Renders the terminal execution output trace with Prachi Manwal's attribution."""
    lines = console_text.strip("\n").splitlines()
    if len(lines) > 82:
        lines = lines[:82]

    fig_height = max(9.8, len(lines) * 0.19 + 1.2)
    fig, ax = plt.subplots(figsize=(14.6, fig_height), dpi=180)
    fig.patch.set_facecolor("#1E1B4B")
    ax.set_facecolor("#1E1B4B")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, len(lines) + 4)
    ax.axis("off")

    header_y = len(lines) + 2.3
    ax.add_patch(mpatches.Rectangle((0, header_y - 0.8), 100, 2.5, color="#312E81"))
    ax.scatter([2.2, 4.0, 5.8], [header_y + 0.35] * 3, s=95, color=["#F43F5E", "#F59E0B", "#10B981"], zorder=5)
    ax.text(
        50, header_y + 0.35,
        "zsh — python3 -m src.main — Prachi Manwal (2501730365) — Mini-Courier Planner Execution Trace",
        ha="center", va="center", fontsize=9.3, fontweight="bold", color="#E0E7FF", family="monospace"
    )

    for idx, line in enumerate(lines):
        y = len(lines) - idx + 0.5
        color = "#F1F5F9"
        weight = "normal"
        if line.startswith("===") or line.startswith("PHASE") or "STUDENT" in line:
            color = "#38BDF8"
            weight = "bold"
        elif "OPTIMAL" in line or "FINAL" in line or "SELECTED" in line or "Total Tour" in line:
            color = "#34D399"
            weight = "bold"
        elif line.startswith("---") or line.startswith("Item"):
            color = "#94A3B8"
        ax.text(1.5, y, line, ha="left", va="center", fontsize=7.9, color=color, fontweight=weight, family="monospace")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.savefig(output_path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
