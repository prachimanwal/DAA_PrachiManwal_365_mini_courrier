"""
Phase 2A: Parcel Prioritization & Sorting Module.
Submitted by: Prachi Manwal (Roll No: 2501730365)

Implements and compares multiple sorting algorithms for ranking parcels by:
1. Priority Tier (1 = Express/Critical, 2 = Standard, 3 = Economy)
2. Delivery Deadline (earliest SLA deadline first, in hours)
3. Value Score (highest value score tie-breaker)
4. Weight (lightest weight secondary tie-breaker)
"""

from dataclasses import dataclass
import time
from typing import Callable, List, Tuple
from src.models import Parcel


@dataclass
class SortResult:
    """Encapsulates sorted parcels along with performance metrics."""
    algorithm_name: str
    criterion_name: str
    sorted_parcels: List[Parcel]
    execution_time_ms: float
    comparisons_count: int


def get_sort_key(mode: str = "deadline_priority") -> Callable[[Parcel], Tuple]:
    """Returns a composite key extraction function for parcel prioritization."""
    if mode == "deadline_only":
        return lambda p: (p.deadline_hrs, p.priority_tier, -p.value_score, p.parcel_id)
    if mode == "value_density":
        return lambda p: (-p.value_density, p.deadline_hrs, p.priority_tier, p.parcel_id)
    return lambda p: (p.priority_tier, p.deadline_hrs, -p.value_score, p.weight_kg, p.parcel_id)


def merge_sort_parcels(
    parcels: List[Parcel],
    mode: str = "deadline_priority",
) -> SortResult:
    """
    Sorts parcels using Divide-and-Conquer Merge Sort (Stable, O(n log n) guaranteed).
    """
    key_fn = get_sort_key(mode)
    comparisons = 0

    def _merge(left: List[Parcel], right: List[Parcel]) -> List[Parcel]:
        nonlocal comparisons
        merged: List[Parcel] = []
        i = j = 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if key_fn(left[i]) <= key_fn(right[j]):
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        if i < len(left):
            merged.extend(left[i:])
        if j < len(right):
            merged.extend(right[j:])
        return merged

    def _merge_sort(items: List[Parcel]) -> List[Parcel]:
        if len(items) <= 1:
            return list(items)
        mid = len(items) // 2
        left_sorted = _merge_sort(items[:mid])
        right_sorted = _merge_sort(items[mid:])
        return _merge(left_sorted, right_sorted)

    t0 = time.perf_counter()
    sorted_list = _merge_sort(list(parcels))
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return SortResult(
        algorithm_name="Merge Sort (O(n log n) Stable)",
        criterion_name=mode,
        sorted_parcels=sorted_list,
        execution_time_ms=round(elapsed_ms, 4),
        comparisons_count=comparisons,
    )


def quick_sort_parcels(
    parcels: List[Parcel],
    mode: str = "deadline_priority",
) -> SortResult:
    """Sorts parcels using Median-of-Three Quick Sort (O(n log n) average)."""
    key_fn = get_sort_key(mode)
    comparisons = 0
    arr = list(parcels)

    def _quick_sort(items: List[Parcel], low: int, high: int) -> None:
        if low < high:
            pivot_idx = _partition(items, low, high)
            _quick_sort(items, low, pivot_idx - 1)
            _quick_sort(items, pivot_idx + 1, high)

    def _partition(items: List[Parcel], low: int, high: int) -> int:
        nonlocal comparisons
        mid = (low + high) // 2
        if key_fn(items[mid]) < key_fn(items[low]):
            items[low], items[mid] = items[mid], items[low]
        if key_fn(items[high]) < key_fn(items[low]):
            items[low], items[high] = items[high], items[low]
        if key_fn(items[mid]) < key_fn(items[high]):
            items[mid], items[high] = items[high], items[mid]

        pivot_key = key_fn(items[high])
        i = low - 1
        for j in range(low, high):
            comparisons += 1
            if key_fn(items[j]) <= pivot_key:
                i += 1
                items[i], items[j] = items[j], items[i]
        items[i + 1], items[high] = items[high], items[i + 1]
        return i + 1

    t0 = time.perf_counter()
    if len(arr) > 1:
        _quick_sort(arr, 0, len(arr) - 1)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return SortResult(
        algorithm_name="Quick Sort (Median-of-3)",
        criterion_name=mode,
        sorted_parcels=arr,
        execution_time_ms=round(elapsed_ms, 4),
        comparisons_count=comparisons,
    )


def heap_sort_parcels(
    parcels: List[Parcel],
    mode: str = "deadline_priority",
) -> SortResult:
    """Sorts parcels in-place using Binary Max-Heap Sort (O(n log n) time, O(1) aux space)."""
    key_fn = get_sort_key(mode)
    comparisons = 0
    arr = list(parcels)
    n = len(arr)

    def _sift_down(size: int, root: int) -> None:
        nonlocal comparisons
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2

        if left < size:
            comparisons += 1
            if key_fn(arr[left]) > key_fn(arr[largest]):
                largest = left
        if right < size:
            comparisons += 1
            if key_fn(arr[right]) > key_fn(arr[largest]):
                largest = right
        if largest != root:
            arr[root], arr[largest] = arr[largest], arr[root]
            _sift_down(size, largest)

    t0 = time.perf_counter()
    for start in range(n // 2 - 1, -1, -1):
        _sift_down(n, start)
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        _sift_down(end, 0)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return SortResult(
        algorithm_name="Heap Sort (O(n log n) In-Place)",
        criterion_name=mode,
        sorted_parcels=arr,
        execution_time_ms=round(elapsed_ms, 4),
        comparisons_count=comparisons,
    )


def insertion_sort_parcels(
    parcels: List[Parcel],
    mode: str = "deadline_priority",
) -> SortResult:
    """Sorts parcels using Insertion Sort (O(n^2) average/worst, stable baseline)."""
    key_fn = get_sort_key(mode)
    comparisons = 0
    arr = list(parcels)

    t0 = time.perf_counter()
    for i in range(1, len(arr)):
        current = arr[i]
        current_key = key_fn(current)
        j = i - 1
        while j >= 0:
            comparisons += 1
            if key_fn(arr[j]) > current_key:
                arr[j + 1] = arr[j]
                j -= 1
            else:
                break
        arr[j + 1] = current
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return SortResult(
        algorithm_name="Insertion Sort (O(n^2) Baseline)",
        criterion_name=mode,
        sorted_parcels=arr,
        execution_time_ms=round(elapsed_ms, 4),
        comparisons_count=comparisons,
    )
