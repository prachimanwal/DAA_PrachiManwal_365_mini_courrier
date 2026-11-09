"""
Unit & Integration Test Suite for Mini-Courier Planner.
Submitted by: Prachi Manwal (Roll No: 2501730365)
"""

from pathlib import Path
import unittest

from src.models import (
    load_parcels_from_csv,
    load_nodes_from_csv,
    load_edges_from_csv,
)
from src.sorting import (
    merge_sort_parcels,
    quick_sort_parcels,
    heap_sort_parcels,
    insertion_sort_parcels,
)
from src.knapsack_dp import (
    solve_knapsack_01_dp,
    solve_knapsack_1d_optimized,
    solve_knapsack_greedy_heuristic,
)
from src.graph_routing import (
    CustomerGraph,
    plan_route_nearest_neighbor,
    plan_route_two_opt,
    plan_route_held_karp_exact,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"


class TestMiniCourierPlannerPrachi(unittest.TestCase):
    def setUp(self) -> None:
        self.parcels = load_parcels_from_csv(DATASETS_DIR / "parcels_sample.csv")
        self.nodes = load_nodes_from_csv(DATASETS_DIR / "graph_nodes.csv")
        self.edges = load_edges_from_csv(DATASETS_DIR / "graph_edges.csv")
        self.graph = CustomerGraph(nodes=self.nodes, edges=self.edges)

    def test_phase1_data_loading(self) -> None:
        self.assertEqual(len(self.parcels), 16)
        self.assertEqual(len(self.nodes), 12)
        self.assertEqual(len(self.edges), 24)
        self.assertIn("HUB", self.nodes)

    def test_phase2a_sorting_algorithms_consistency(self) -> None:
        ms = merge_sort_parcels(self.parcels)
        qs = quick_sort_parcels(self.parcels)
        hs = heap_sort_parcels(self.parcels)
        ins = insertion_sort_parcels(self.parcels)

        expected_ids = [p.parcel_id for p in ms.sorted_parcels]
        self.assertEqual([p.parcel_id for p in qs.sorted_parcels], expected_ids)
        self.assertEqual([p.parcel_id for p in hs.sorted_parcels], expected_ids)
        self.assertEqual([p.parcel_id for p in ins.sorted_parcels], expected_ids)

    def test_phase2b_knapsack_dp_optimality(self) -> None:
        sorted_parcels = merge_sort_parcels(self.parcels).sorted_parcels
        dp2d = solve_knapsack_01_dp(sorted_parcels, capacity_kg=35, store_table=True)
        dp1d = solve_knapsack_1d_optimized(sorted_parcels, capacity_kg=35)
        greedy = solve_knapsack_greedy_heuristic(sorted_parcels, capacity_kg=35)

        self.assertEqual(dp2d.total_value_score, 990)
        self.assertEqual(dp2d.total_weight_kg, 35)
        self.assertEqual(dp1d.total_value_score, dp2d.total_value_score)
        self.assertGreater(dp2d.total_value_score, greedy.total_value_score)

    def test_phase3_dijkstra_and_tsp_routing(self) -> None:
        sorted_parcels = merge_sort_parcels(self.parcels).sorted_parcels
        dp2d = solve_knapsack_01_dp(sorted_parcels, capacity_kg=35)

        nn_route = plan_route_nearest_neighbor(self.graph, dp2d.selected_parcels)
        two_opt_route = plan_route_two_opt(self.graph, dp2d.selected_parcels)
        exact_route = plan_route_held_karp_exact(self.graph, dp2d.selected_parcels)

        self.assertEqual(nn_route.stop_sequence[0], "HUB")
        self.assertEqual(nn_route.stop_sequence[-1], "HUB")
        self.assertEqual(set(nn_route.stop_sequence[1:-1]), set(dp2d.unique_destinations))
        self.assertLessEqual(two_opt_route.total_distance_km, nn_route.total_distance_km)
        self.assertAlmostEqual(two_opt_route.total_distance_km, exact_route.total_distance_km, places=2)


if __name__ == "__main__":
    unittest.main()
