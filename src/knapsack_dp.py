"""
Phase 2B: Package Selection & Box Filling via 0/1 Knapsack Dynamic Programming.
Submitted by: Prachi Manwal (Roll No: 2501730365)

Determines the exact optimal subset of prioritized parcels for one courier van
delivery trip of capacity W = 35 kg using Bottom-Up 2D Dynamic Programming,
1D Bitmask Space-Optimized DP, and a Greedy Density Heuristic baseline.
"""

import time
from typing import List
from src.models import Parcel, PackingResult


def solve_knapsack_01_dp(
    parcels: List[Parcel],
    capacity_kg: int = 35,
    store_table: bool = True,
) -> PackingResult:
    """Solves the 0/1 Knapsack problem using Bottom-Up 2D Dynamic Programming."""
    n = len(parcels)
    W = int(capacity_kg)

    t0 = time.perf_counter()
    dp: List[List[int]] = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wt = parcels[i - 1].weight_kg
        val = parcels[i - 1].value_score
        prev_row = dp[i - 1]
        curr_row = dp[i]
        for w in range(W + 1):
            if wt <= w:
                candidate = val + prev_row[w - wt]
                curr_row[w] = candidate if candidate > prev_row[w] else prev_row[w]
            else:
                curr_row[w] = prev_row[w]

    selected_indices = set()
    rem_w = W
    for i in range(n, 0, -1):
        if dp[i][rem_w] != dp[i - 1][rem_w]:
            selected_indices.add(i - 1)
            rem_w -= parcels[i - 1].weight_kg

    selected_parcels = [parcels[idx] for idx in range(n) if idx in selected_indices]
    deferred_parcels = [parcels[idx] for idx in range(n) if idx not in selected_indices]

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    total_weight = sum(p.weight_kg for p in selected_parcels)
    total_value = dp[n][W]
    utilization = round((total_weight / W) * 100.0, 2) if W > 0 else 0.0

    return PackingResult(
        algorithm_name="0/1 Knapsack DP (2D Bottom-Up)",
        capacity_kg=W,
        selected_parcels=selected_parcels,
        deferred_parcels=deferred_parcels,
        total_weight_kg=total_weight,
        total_value_score=total_value,
        utilization_pct=utilization,
        execution_time_ms=round(elapsed_ms, 4),
        dp_table=dp if store_table else None,
    )


def solve_knapsack_1d_optimized(
    parcels: List[Parcel],
    capacity_kg: int = 35,
) -> PackingResult:
    """Space-Optimized 1D Dynamic Programming for 0/1 Knapsack (O(W) auxiliary space)."""
    n = len(parcels)
    W = int(capacity_kg)

    t0 = time.perf_counter()
    dp = [0] * (W + 1)
    chosen_mask = [0] * (W + 1)

    for i, parcel in enumerate(parcels):
        wt = parcel.weight_kg
        val = parcel.value_score
        bit = 1 << i
        for w in range(W, wt - 1, -1):
            candidate = dp[w - wt] + val
            if candidate > dp[w]:
                dp[w] = candidate
                chosen_mask[w] = chosen_mask[w - wt] | bit

    optimal_mask = chosen_mask[W]
    selected_parcels = [parcels[i] for i in range(n) if (optimal_mask & (1 << i))]
    deferred_parcels = [parcels[i] for i in range(n) if not (optimal_mask & (1 << i))]

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    total_weight = sum(p.weight_kg for p in selected_parcels)
    total_value = dp[W]
    utilization = round((total_weight / W) * 100.0, 2) if W > 0 else 0.0

    return PackingResult(
        algorithm_name="0/1 Knapsack DP (1D Bitmask Optimized)",
        capacity_kg=W,
        selected_parcels=selected_parcels,
        deferred_parcels=deferred_parcels,
        total_weight_kg=total_weight,
        total_value_score=total_value,
        utilization_pct=utilization,
        execution_time_ms=round(elapsed_ms, 4),
        dp_table=None,
    )


def solve_knapsack_greedy_heuristic(
    parcels: List[Parcel],
    capacity_kg: int = 35,
) -> PackingResult:
    """Greedy 0/1 Knapsack approximation sorted by Value-to-Weight Density (v_i / w_i)."""
    W = int(capacity_kg)
    t0 = time.perf_counter()

    ranked = sorted(
        enumerate(parcels),
        key=lambda item: (-item[1].value_density, item[1].priority_tier, item[1].deadline_hrs),
    )

    selected_indices = set()
    current_weight = 0
    current_value = 0

    for idx, parcel in ranked:
        if current_weight + parcel.weight_kg <= W:
            selected_indices.add(idx)
            current_weight += parcel.weight_kg
            current_value += parcel.value_score

    selected_parcels = [parcels[i] for i in range(len(parcels)) if i in selected_indices]
    deferred_parcels = [parcels[i] for i in range(len(parcels)) if i not in selected_indices]

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    utilization = round((current_weight / W) * 100.0, 2) if W > 0 else 0.0

    return PackingResult(
        algorithm_name="Greedy Density Heuristic (O(n log n))",
        capacity_kg=W,
        selected_parcels=selected_parcels,
        deferred_parcels=deferred_parcels,
        total_weight_kg=current_weight,
        total_value_score=current_value,
        utilization_pct=utilization,
        execution_time_ms=round(elapsed_ms, 4),
        dp_table=None,
    )


def format_dp_table_ascii(
    parcels: List[Parcel],
    dp_table: List[List[int]],
    step: int = 4,
) -> str:
    """Formats the 2D Knapsack DP table as an aligned ASCII grid."""
    if not dp_table:
        return "DP table not stored."

    max_w = len(dp_table[0]) - 1
    cols = list(range(0, max_w + 1, step))
    if cols[-1] != max_w:
        cols.append(max_w)

    header = f"{'Item (ID, Wt, Val)':<26} | " + " ".join(f"{w:>4}kg" for w in cols)
    sep = "-" * len(header)
    lines = [header, sep]

    row0_vals = " ".join(f"{dp_table[0][w]:>6}" for w in cols)
    lines.append(f"{'0: [Empty Base Case]':<26} | {row0_vals}")

    for i, p in enumerate(parcels, start=1):
        label = f"{i:>2}: {p.parcel_id} ({p.weight_kg}kg, v={p.value_score})"
        row_vals = " ".join(f"{dp_table[i][w]:>6}" for w in cols)
        lines.append(f"{label:<26} | {row_vals}")

    return "\n".join(lines)
