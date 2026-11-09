"""
Phase 3: Route Maker and Graph Processing Module.
Submitted by: Prachi Manwal (Roll No: 2501730365)

Implements CustomerGraph (Adjacency List), Dijkstra's Shortest-Path Algorithm,
Nearest-Neighbor TSP Approximation, 2-Opt Refinement, and Held-Karp Exact TSP DP.
"""

import heapq
import time
from typing import Dict, List, Optional, Tuple
from src.models import DeliveryNode, Parcel, RoadEdge, RouteLeg, RouteResult


class CustomerGraph:
    """
    Weighted undirected graph representing the MetroSwift city road network.
    Uses an Adjacency List representation: node_id -> List[(neighbor_id, distance_km, road_name)].
    """

    def __init__(
        self,
        nodes: Optional[Dict[str, DeliveryNode]] = None,
        edges: Optional[List[RoadEdge]] = None,
    ) -> None:
        self.nodes: Dict[str, DeliveryNode] = nodes or {}
        self.edges: List[RoadEdge] = edges or []
        self.adj: Dict[str, List[Tuple[str, float, str]]] = {
            node_id: [] for node_id in self.nodes
        }
        self.edge_lookup: Dict[Tuple[str, str], RoadEdge] = {}

        for edge in self.edges:
            self.add_edge(edge)

    def add_node(self, node: DeliveryNode) -> None:
        self.nodes[node.node_id] = node
        if node.node_id not in self.adj:
            self.adj[node.node_id] = []

    def add_edge(self, edge: RoadEdge) -> None:
        if edge.source not in self.adj:
            self.adj[edge.source] = []
        if edge.target not in self.adj:
            self.adj[edge.target] = []

        self.adj[edge.source].append((edge.target, edge.distance_km, edge.road_name))
        self.adj[edge.target].append((edge.source, edge.distance_km, edge.road_name))
        self.edge_lookup[(edge.source, edge.target)] = edge
        self.edge_lookup[(edge.target, edge.source)] = edge

    def get_road_name(self, u: str, v: str) -> str:
        edge = self.edge_lookup.get((u, v))
        return edge.road_name if edge and edge.road_name else f"{u}<->{v}"

    def format_adjacency_list(self) -> str:
        """Returns a formatted representation of the graph's adjacency list."""
        lines = [
            f"MetroSwift Customer Graph: |V| = {len(self.nodes)} nodes, |E| = {len(self.edges)} undirected road segments",
            "-" * 86,
            f"{'Node ID':<8} | {'Zone Name':<25} | {'Neighbors (Node: Distance km)'}",
            "-" * 86,
        ]
        for node_id, neighbors in self.adj.items():
            zone_name = self.nodes[node_id].node_name if node_id in self.nodes else node_id
            nbr_str = ", ".join(f"{nbr} ({dist:.1f}km)" for nbr, dist, _ in sorted(neighbors))
            lines.append(f"{node_id:<8} | {zone_name:<25} | {nbr_str}")
        return "\n".join(lines)

    def dijkstra_single_source(
        self, source: str
    ) -> Tuple[Dict[str, float], Dict[str, Optional[str]], Dict[str, List[str]]]:
        """
        Computes shortest paths from `source` to all reachable vertices using
        Dijkstra's Algorithm with a binary min-heap priority queue (O((V + E) log V)).
        """
        distances: Dict[str, float] = {v: float("inf") for v in self.adj}
        predecessors: Dict[str, Optional[str]] = {v: None for v in self.adj}
        distances[source] = 0.0

        pq: List[Tuple[float, str]] = [(0.0, source)]

        while pq:
            curr_dist, u = heapq.heappop(pq)
            if curr_dist > distances[u]:
                continue

            for neighbor, weight, _ in self.adj[u]:
                candidate_dist = curr_dist + weight
                if candidate_dist < distances[neighbor]:
                    distances[neighbor] = round(candidate_dist, 6)
                    predecessors[neighbor] = u
                    heapq.heappush(pq, (distances[neighbor], neighbor))

        paths: Dict[str, List[str]] = {}
        for target in self.adj:
            if distances[target] == float("inf"):
                paths[target] = []
                continue
            path = []
            curr: Optional[str] = target
            while curr is not None:
                path.append(curr)
                curr = predecessors[curr]
            path.reverse()
            paths[target] = path

        return distances, predecessors, paths

    def compute_metric_closure(
        self, active_nodes: List[str]
    ) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, List[str]]], float]:
        """Runs Dijkstra from each active node to build the pairwise shortest-path distance matrix."""
        t0 = time.perf_counter()
        dist_matrix: Dict[str, Dict[str, float]] = {}
        path_matrix: Dict[str, Dict[str, List[str]]] = {}

        for u in active_nodes:
            dists, _, paths = self.dijkstra_single_source(u)
            dist_matrix[u] = {v: round(dists[v], 2) for v in active_nodes}
            path_matrix[u] = {v: paths[v] for v in active_nodes}

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return dist_matrix, path_matrix, elapsed_ms


def _build_route_result(
    graph: CustomerGraph,
    algorithm_name: str,
    hub_id: str,
    tour_stops: List[str],
    selected_parcels: List[Parcel],
    dist_matrix: Dict[str, Dict[str, float]],
    path_matrix: Dict[str, Dict[str, List[str]]],
    dijkstra_time_ms: float,
    tsp_time_ms: float,
) -> RouteResult:
    """Constructs a detailed RouteResult from an ordered stop sequence."""
    parcels_by_dest: Dict[str, List[str]] = {}
    for p in selected_parcels:
        parcels_by_dest.setdefault(p.destination_id, []).append(
            f"{p.parcel_id} ({p.weight_kg}kg)"
        )

    legs: List[RouteLeg] = []
    expanded_road_path: List[str] = []
    total_distance = 0.0

    for idx in range(len(tour_stops) - 1):
        u = tour_stops[idx]
        v = tour_stops[idx + 1]
        leg_dist = dist_matrix[u][v]
        sub_path = path_matrix[u][v]
        roads = [
            graph.get_road_name(sub_path[i], sub_path[i + 1])
            for i in range(len(sub_path) - 1)
        ]
        delivered = parcels_by_dest.get(v, []) if v != hub_id else ["Return to MetroSwift Hub"]

        legs.append(
            RouteLeg(
                leg_index=idx + 1,
                from_node=u,
                to_node=v,
                shortest_distance_km=round(leg_dist, 2),
                intermediate_path=sub_path,
                roads_taken=roads,
                parcels_delivered=delivered,
            )
        )
        total_distance += leg_dist
        if idx == 0:
            expanded_road_path.extend(sub_path)
        else:
            expanded_road_path.extend(sub_path[1:])

    return RouteResult(
        algorithm_name=algorithm_name,
        hub_id=hub_id,
        stop_sequence=tour_stops,
        expanded_road_path=expanded_road_path,
        legs=legs,
        total_distance_km=round(total_distance, 2),
        dijkstra_time_ms=round(dijkstra_time_ms, 4),
        tsp_time_ms=round(tsp_time_ms, 4),
        distance_matrix=dist_matrix,
        path_matrix=path_matrix,
    )


def plan_route_nearest_neighbor(
    graph: CustomerGraph,
    selected_parcels: List[Parcel],
    hub_id: str = "HUB",
) -> RouteResult:
    """
    Phase 3 Core Algorithm:
    Computes all-pairs shortest paths via Dijkstra and applies the Nearest-Neighbor
    TSP Approximation heuristic (O(k^2)) starting and ending at `hub_id`.
    """
    unique_stops = []
    seen = {hub_id}
    for p in selected_parcels:
        if p.destination_id not in seen:
            seen.add(p.destination_id)
            unique_stops.append(p.destination_id)

    active_nodes = [hub_id] + unique_stops
    dist_matrix, path_matrix, dijkstra_ms = graph.compute_metric_closure(active_nodes)

    t0 = time.perf_counter()
    unvisited = set(unique_stops)
    current = hub_id
    tour = [hub_id]

    while unvisited:
        next_stop = min(
            unvisited,
            key=lambda candidate: (dist_matrix[current][candidate], candidate),
        )
        tour.append(next_stop)
        unvisited.remove(next_stop)
        current = next_stop

    tour.append(hub_id)
    tsp_ms = (time.perf_counter() - t0) * 1000.0

    return _build_route_result(
        graph=graph,
        algorithm_name="Dijkstra + Nearest-Neighbor TSP",
        hub_id=hub_id,
        tour_stops=tour,
        selected_parcels=selected_parcels,
        dist_matrix=dist_matrix,
        path_matrix=path_matrix,
        dijkstra_time_ms=dijkstra_ms,
        tsp_time_ms=tsp_ms,
    )


def plan_route_two_opt(
    graph: CustomerGraph,
    selected_parcels: List[Parcel],
    hub_id: str = "HUB",
) -> RouteResult:
    """Nearest-Neighbor initialization followed by 2-Opt Local Search refinement."""
    nn_result = plan_route_nearest_neighbor(graph, selected_parcels, hub_id=hub_id)
    dist_matrix = nn_result.distance_matrix
    path_matrix = nn_result.path_matrix

    t0 = time.perf_counter()
    tour = list(nn_result.stop_sequence)
    n = len(tour)

    improved = True
    while improved:
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                if j - i == 1:
                    continue
                old_cost = dist_matrix[tour[i - 1]][tour[i]] + dist_matrix[tour[j]][tour[j + 1]]
                new_cost = dist_matrix[tour[i - 1]][tour[j]] + dist_matrix[tour[i]][tour[j + 1]]
                if new_cost + 1e-9 < old_cost:
                    tour[i : j + 1] = reversed(tour[i : j + 1])
                    improved = True

    two_opt_ms = nn_result.tsp_time_ms + (time.perf_counter() - t0) * 1000.0

    return _build_route_result(
        graph=graph,
        algorithm_name="Dijkstra + Nearest-Neighbor + 2-Opt TSP",
        hub_id=hub_id,
        tour_stops=tour,
        selected_parcels=selected_parcels,
        dist_matrix=dist_matrix,
        path_matrix=path_matrix,
        dijkstra_time_ms=nn_result.dijkstra_time_ms,
        tsp_time_ms=two_opt_ms,
    )


def plan_route_held_karp_exact(
    graph: CustomerGraph,
    selected_parcels: List[Parcel],
    hub_id: str = "HUB",
) -> RouteResult:
    """Exact Held-Karp Dynamic Programming TSP solver (O(k^2 * 2^k))."""
    unique_stops = []
    seen = {hub_id}
    for p in selected_parcels:
        if p.destination_id not in seen:
            seen.add(p.destination_id)
            unique_stops.append(p.destination_id)

    active_nodes = [hub_id] + unique_stops
    dist_matrix, path_matrix, dijkstra_ms = graph.compute_metric_closure(active_nodes)

    t0 = time.perf_counter()
    k = len(unique_stops)
    if k == 0:
        return _build_route_result(
            graph, "Held-Karp Exact TSP DP", hub_id, [hub_id, hub_id],
            selected_parcels, dist_matrix, path_matrix, dijkstra_ms, 0.0
        )

    dp: Dict[Tuple[int, int], Tuple[float, int]] = {}
    for i in range(k):
        stop = unique_stops[i]
        dp[(1 << i, i)] = (dist_matrix[hub_id][stop], -1)

    for mask in range(1, 1 << k):
        for last in range(k):
            if not (mask & (1 << last)):
                continue
            state = (mask, last)
            if state not in dp:
                continue
            curr_cost, _ = dp[state]
            u = unique_stops[last]
            for nxt in range(k):
                if mask & (1 << nxt):
                    continue
                nxt_mask = mask | (1 << nxt)
                v = unique_stops[nxt]
                cand_cost = curr_cost + dist_matrix[u][v]
                nxt_state = (nxt_mask, nxt)
                if nxt_state not in dp or cand_cost < dp[nxt_state][0]:
                    dp[nxt_state] = (cand_cost, last)

    full_mask = (1 << k) - 1
    best_cost = float("inf")
    best_last = -1
    for last in range(k):
        cost, _ = dp[(full_mask, last)]
        total = cost + dist_matrix[unique_stops[last]][hub_id]
        if total < best_cost:
            best_cost = total
            best_last = last

    order_indices = []
    curr_mask = full_mask
    curr_last = best_last
    while curr_last != -1:
        order_indices.append(curr_last)
        _, prev_last = dp[(curr_mask, curr_last)]
        curr_mask ^= (1 << curr_last)
        curr_last = prev_last
    order_indices.reverse()

    tour = [hub_id] + [unique_stops[i] for i in order_indices] + [hub_id]
    tsp_ms = (time.perf_counter() - t0) * 1000.0

    return _build_route_result(
        graph=graph,
        algorithm_name="Dijkstra + Held-Karp Exact TSP (O(k^2 2^k))",
        hub_id=hub_id,
        tour_stops=tour,
        selected_parcels=selected_parcels,
        dist_matrix=dist_matrix,
        path_matrix=path_matrix,
        dijkstra_time_ms=dijkstra_ms,
        tsp_time_ms=tsp_ms,
    )
