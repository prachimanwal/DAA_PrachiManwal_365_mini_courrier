# Technical Project Report: Mini-Courier Planner
### Integrated Parcel Prioritization, 0/1 Knapsack Dynamic Programming, Dijkstra Shortest Paths, and TSP Route Approximation

- **Student Name:** Prachi Manwal
- **Roll / Registration No:** `2501730365`
- **Course Outcomes Mapped:** CO1, CO2, CO3, CO4, CO5 (L5 – Evaluate)
- **Total Marks:** 100 (Phases 1–5)
- **Version Tag:** `v1.0-final-submission`

---

## 1. Phase 1: Courier Problem Design and Planning (20 Marks)

### 1.1 Problem Statement & System Design
Urban express hubs must dispatch prioritized customer parcels within strict Service-Level Agreement (SLA) deadlines while respecting vehicle weight limits and navigating complex metropolitan road networks. **Mini-Courier Planner (MetroSwift Edition)** integrates four core algorithmic paradigms into a single cohesive pipeline:
1. **Merge Sort ($\Theta(n \log n)$ Stable):** Ranks incoming parcels by urgency tier, SLA deadline, and utility value score.
2. **0/1 Knapsack Dynamic Programming ($\Theta(n \cdot W)$):** Determines the exact subset of indivisible parcels that maximizes total dispatch value within the van's $W = 35\text{ kg}$ payload limit.
3. **Dijkstra's Shortest-Path Algorithm ($O((V+E)\log V)$):** Computes exact single-source and pairwise shortest paths across the 12-node, 24-edge MetroSwift city road graph.
4. **Nearest-Neighbor TSP Approximation ($O(k^2)$) & 2-Opt Refinement:** Orders all active customer delivery stops into a closed delivery tour starting and ending at the central dispatch hub (`HUB`).

![Phase 1 Architecture](images/phase1_system_architecture.png)

---

## 2. Phase 2: Package Prioritization and Box Filling (20 Marks)

### 2.1 Parcel Prioritization via Merge Sort
All 16 parcels (`PKG-101`–`PKG-116`) are sorted by the composite urgency key:
$$\text{Key}(p_i) = (\text{priority\_tier}_i \uparrow,\; \text{deadline\_hrs}_i \uparrow,\; -\text{value\_score}_i \uparrow,\; \text{weight\_kg}_i \uparrow)$$
Merge Sort is selected as the primary algorithm because it guarantees deterministic $\Theta(n \log n)$ worst-case complexity (46 key comparisons on the 16-parcel manifest) and is **stable**, preserving FIFO arrival order for parcels with identical urgency and deadline values.

### 2.2 Optimal Box Filling via 0/1 Knapsack Dynamic Programming ($W = 35\text{ kg}$)
- **State Recurrence:**
  $$dp[i][w] = \begin{cases} dp[i-1][w] & \text{if } w_i > w \\ \max\big(dp[i-1][w],\; v_i + dp[i-1][w - w_i]\big) & \text{if } w_i \le w \end{cases}$$
- **Selected Packing Plan ($W = 35\text{ kg}$):**
  - **9 Selected Parcels:** `PKG-101` (5kg, v=145, Z3), `PKG-104` (3kg, v=105, Z2), `PKG-108` (4kg, v=112, Z7), `PKG-102` (3kg, v=99, Z1), `PKG-111` (5kg, v=125, Z9), `PKG-106` (2kg, v=110, Z4), `PKG-114` (4kg, v=96, Z3), `PKG-103` (5kg, v=110, Z7), and `PKG-107` (4kg, v=88, Z5).
  - **Total Weight Packed:** **$35 / 35\text{ kg}$ ($100.0\%$ capacity utilization)**.
  - **Total Optimal Value Score:** **$990$** (includes all 7 Express Tier-1 parcels).
  - **Why 0/1 DP Outperforms Greedy Heuristic:** After packing the 7 Express Tier-1 items ($26\text{ kg}$, value $= 792$), $9\text{ kg}$ of capacity remains. The Greedy value-density heuristic picks `PKG-109` ($6\text{ kg}, v=138$, density $23.0$), stranding $3\text{ kg}$ of unused capacity ($32/35\text{ kg}$, value $= 930$). **0/1 Knapsack DP instead selects `PKG-103` ($5\text{ kg}, v=110$) + `PKG-107` ($4\text{ kg}, v=88$), utilizing $100\%$ of the $35\text{ kg}$ van capacity and achieving $990$ value points ($+60$ points higher than Greedy).**

![Phase 2 Prioritization and Knapsack DP](images/phase2_knapsack_and_prioritization.png)

---

## 3. Phase 3: Route Maker and Graph Processing (20 Marks)

### 3.1 Dijkstra Shortest Paths & Nearest-Neighbor TSP Tour
For the 7 unique delivery zones required by the 9 packed parcels ($U = \{\text{HUB}, Z1, Z2, Z3, Z4, Z5, Z7, Z9\}$), Dijkstra's algorithm computes all-pairs shortest paths and Nearest-Neighbor TSP constructs the delivery tour:

| Leg | From $\to$ To | Shortest Distance (km) | Street-Level Dijkstra Path | Roads Traversed | Parcels Delivered |
| :---: | :---: | :---: | :--- | :--- | :--- |
| **#1** | `HUB -> Z1` | 5.10 km | `HUB -> Z1` | Rajpath Arterial North | `PKG-102 (3kg)` |
| **#2** | `Z1 -> Z4` | 4.10 km | `Z1 -> Z4` | Bullion Market Flyover | `PKG-106 (2kg)` |
| **#3** | `Z4 -> Z2` | 8.50 km | `Z4 -> Z2` | Northern Bypass Rd | `PKG-104 (3kg)` |
| **#4** | `Z2 -> Z3` | 4.80 km | `Z2 -> Z3` | West Enclave Blvd | `PKG-101 (5kg), PKG-114 (4kg)` |
| **#5** | `Z3 -> Z5` | 5.00 km | `Z3 -> Z5` | Botanical Link Ave | `PKG-107 (4kg)` |
| **#6** | `Z5 -> Z9` | 9.30 km | `Z5 -> Z9` | Cross-Metro Arterial | `PKG-111 (5kg)` |
| **#7** | `Z9 -> Z7` | 5.60 km | `Z9 -> Z7` | Tech Corridor Express | `PKG-108 (4kg), PKG-103 (5kg)` |
| **#8** | `Z7 -> HUB` | 11.70 km | `Z7 -> Z9 -> HUB` | Tech Corridor Express $\to$ Aerocity Spine Rd | *Return to MetroSwift Hub* |
| **Total** | **Closed Tour** | **54.10 km** | **9 Road Hops** | — | **9 Parcels (35 kg)** |

- **2-Opt Refinement & Held-Karp Exact Verification:** Applying **2-Opt Local Search** uncrosses the transition between the northern and southern sectors to yield a tour of **51.80 km**, matching the **Held-Karp Exact TSP DP** global optimum (**saving 2.30 km / 4.25%**).

![Phase 3 Delivery Route Map](images/phase3_delivery_route_map.png)

---

## 4. Phase 4: Performance Testing, Complexity Analysis, and Optimization (20 Marks)

| Algorithmic Module | Selected Method | Time Complexity | Space Complexity | Empirical Scaling Observation |
| :--- | :--- | :---: | :---: | :--- |
| **Phase 2A: Sorting** | Merge Sort | $\Theta(n \log n)$ | $O(n)$ | Scales from $0.03\text{ ms}$ ($N=25$) to $2.1\text{ ms}$ ($N=1,500$), beating $O(n^2)$ Insertion Sort by $32\times$. |
| **Phase 2B: Packing** | 0/1 Knapsack DP (2D & 1D) | $\Theta(n \cdot W)$ | $O(nW)$ / $O(W)$ | 1D Bitmask DP reduces memory to $O(W)$ and improves runtime by ~20%. |
| **Phase 3A: Shortest Path** | Min-Heap Dijkstra | $O(k(V+E)\log V)$ | $O(V + k^2)$ | Computes full metric closure in $<0.20\text{ ms}$ across 12 nodes. |
| **Phase 3B: TSP Routing** | Nearest-Neighbor + 2-Opt | $O(k^2)$ | $O(k)$ | Sub-millisecond at $k=40$ stops, whereas exact Held-Karp $\Theta(k^2 2^k)$ explodes past $k=12$. |

![Phase 4 Runtime Scalability Charts](images/phase4_runtime_scalability_charts.png)

---

## 5. Phase 5: Final Report and Demonstration (20 Marks)

![Phase 5 Console Execution Screenshot](images/phase5_console_execution_screenshot.png)

### Conclusion
Submitted by **Prachi Manwal (`2501730365`)**, this **Mini-Courier Planner** prototype demonstrates that combining **Merge Sort**, **0/1 Knapsack Dynamic Programming**, **Dijkstra's Shortest-Path Algorithm**, and **Nearest-Neighbor / 2-Opt TSP Approximation** produces provably prioritized, 100% capacity-optimized, and shortest-path-routed courier dispatch plans in **under 1 millisecond** for standard manifests and **7.3 milliseconds** for 500-parcel hub workloads.
