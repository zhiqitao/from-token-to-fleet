"""CPU-only analytical checks. No accelerator, network, or collective benchmark.

Run: python3 independent_calculations.py
Outputs calculations.json beside this script. Decimal GB and binary MiB are explicit.
Ring model: equal blocks, no compression/offload, balanced point-to-point forwarding.
"""
from fractions import Fraction
import json
import struct
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
GB = 10**9
KiB = 2**10
MiB = 2**20


def ring_bytes(logical_bytes, ranks):
    if ranks < 1 or logical_bytes < 0:
        raise ValueError("positive rank count and nonnegative logical bytes required")
    sent = Fraction(2 * (ranks - 1), ranks) * logical_bytes
    return {"logical": Fraction(logical_bytes), "sent": sent,
            "received": sent, "endpoint_aggregate": 2 * sent,
            "all_rank_sent": ranks * sent}


def materialize():
    r = ring_bytes(140 * GB, 8)
    t = r["sent"] / (450 * GB)
    tp = ring_bytes(16 * 8192 * 2, 8)
    ep_routes = 256 * 2 * 8192 * 2
    ep_remote = Fraction(7, 8) * ep_routes
    n = 4
    inputs = [[rank + 1, 2 * (rank + 1), -(rank + 1), 0] for rank in range(n)]
    summed = [sum(row[col] for row in inputs) for col in range(4)]
    return {
        "status": "ANALYTICAL; CPU checks only; not a deployment measurement",
        "ring140GB_N8": {k: float(v / GB) for k, v in r.items()},
        "ring140GB_N8_units": "GB, decimal; aggregate sums send and receive",
        "ring140GB_seconds_at_450GBps_send": float(t),
        "ring140GB_seconds_at_900GBps_endpoint_aggregate": float(r["endpoint_aggregate"] / (900 * GB)),
        "incorrect_seconds_using_send_bytes_and_bidirectional_bandwidth": float(r["sent"] / (900 * GB)),
        "one_way140GB_seconds_at_450GBps": float(Fraction(140, 450)),
        "ring140GB_seconds_at_assumed40GBps_send": float(r["sent"] / (40 * GB)),
        "ring140GB_seconds_at_assumed2_5GBps_send": float(r["sent"] / (Fraction(5, 2) * GB)),
        "corrected_ratios_40GBps_and2_5GBps_vs450GBps": [float(Fraction(450, 40)), 180.0],
        "ring280GB_N8_seconds_at450GBps_send": float(ring_bytes(280 * GB, 8)["sent"] / (450 * GB)),
        "ring140GB_repeated100_full_tensor_calls_seconds": float(t * 100),
        "TP_assumptions": {"decode_sequences": 16, "tokens_per_sequence_this_step": 1,
                           "hidden": 8192, "bytes_per_element": 2, "TP_ranks": 8,
                           "blocks": 80, "allreduces_per_block": 2},
        "TP_per_allreduce_logical_bytes": int(tp["logical"]),
        "TP_per_allreduce_sent_bytes": int(tp["sent"]),
        "TP_per_allreduce_received_bytes": int(tp["received"]),
        "TP_per_decode_step_sent_bytes": int(tp["sent"] * 160),
        "TP_per_decode_step_received_bytes": int(tp["received"] * 160),
        "TP_per_decode_step_sent_MiB": float(tp["sent"] * 160 / MiB),
        "TP_per_decode_step_byte_only_ms_at450GBps_send": float(tp["sent"] * 160 / (450 * GB) * 1000),
        "TP_per_decode_step_byte_only_ms_at25GBps_send": float(tp["sent"] * 160 / (25 * GB) * 1000),
        "TP_flat_ring_serial_step_count": 160 * 2 * 7,
        "EP_assumptions": "256 local tokens/rank; top-2; hidden 8192; BF16; 8 ranks; uniform destinations; one full row per route; equal-size combine; no dedup/compression/metadata",
        "EP_per_rank_dispatch_sent_MiB": float(ep_remote / MiB),
        "EP_per_rank_dispatch_received_MiB": float(ep_remote / MiB),
        "EP_per_rank_dispatch_plus_combine_sent_MiB": float(2 * ep_remote / MiB),
        "EP_per_rank_dispatch_plus_combine_received_MiB": float(2 * ep_remote / MiB),
        "FSDP_64MiB_unit_N8_ring_allgather_sent_MiB": float(Fraction(7, 8) * 64),
        "FSDP_64MiB_unit_N8_ring_reduce_scatter_sent_MiB": float(Fraction(7, 8) * 64),
        "semantic_SUM_inputs": inputs,
        "semantic_SUM_output_on_every_rank": summed,
        "semantic_average_requires_division_by4": [x / 4 for x in summed],
        "floating_point_order_example_binary64": {
            "left_association": (1e16 + -1e16) + 1.0,
            "right_association": 1e16 + (-1e16 + 1.0),
            "scope": "Python binary64 example; not a library reproducibility test"},
        "memory_constraint": "140 GB logical input does not fit an 80 GB GPU; 160 GB model-only capacity does not establish training-state fit"
    }


class AnalyticalChecks(unittest.TestCase):
    def test_ring_direction_and_small_payload(self):
        r = ring_bytes(8, 4)
        self.assertEqual((r["sent"], r["received"], r["endpoint_aggregate"]), (12, 12, 24))
        self.assertEqual(ring_bytes(140 * GB, 8)["all_rank_sent"], 1960 * GB)

    def test_directional_denominator(self):
        r = ring_bytes(140 * GB, 8)
        self.assertEqual(r["sent"], 245 * GB)
        self.assertEqual(r["received"], 245 * GB)
        self.assertEqual(r["sent"] / (450 * GB), r["endpoint_aggregate"] / (900 * GB))
        self.assertEqual(r["sent"] / (450 * GB), Fraction(49, 90))

    def test_semantics_and_decomposition(self):
        inputs = [[r + 1, 2 * (r + 1), -(r + 1), 0] for r in range(4)]
        reduced = [sum(row[c] for row in inputs) for c in range(4)]
        self.assertEqual(reduced, [10, 20, -10, 0])
        scattered = [[v] for v in reduced]
        gathered = [v for part in scattered for v in part]
        self.assertEqual(gathered, reduced)  # reduce-scatter + all-gather
        self.assertNotEqual(gathered, [v for row in inputs for v in row])

    def test_llm_shapes(self):
        d = materialize()
        self.assertEqual(d["TP_per_allreduce_sent_bytes"], 448 * KiB)
        self.assertEqual(d["TP_per_decode_step_sent_bytes"], 70 * MiB)
        self.assertEqual(d["EP_per_rank_dispatch_plus_combine_sent_MiB"], 14)
        self.assertEqual(d["FSDP_64MiB_unit_N8_ring_allgather_sent_MiB"], 56)

    def test_figure_ring_rounds_and_fp16(self):
        # CPU simulation of the pictured clockwise R0->R1->R2->R3->R0 ring.
        # Snapshot each round so all sends consume the previous round's state.
        n = 4
        initial = [[r + 1, 2 * (r + 1), -(r + 1), 0] for r in range(n)]
        state = [row[:] for row in initial]
        sent = [0] * n
        received = [0] * n
        for step in range(n - 1):
            messages = [(r, (r + 1) % n, (r - step - 1) % n,
                         state[r][(r - step - 1) % n]) for r in range(n)]
            for source, target, chunk, value in messages:
                state[target][chunk] = initial[target][chunk] + value
                sent[source] += 2
                received[target] += 2
        reduced = [state[r][r] for r in range(n)]
        self.assertEqual(reduced, [10, 20, -10, 0])
        self.assertEqual(sent, [6] * n)
        self.assertEqual(received, [6] * n)
        for step in range(n - 1):
            messages = [(r, (r + 1) % n, (r - step) % n,
                         state[r][(r - step) % n]) for r in range(n)]
            for source, target, chunk, value in messages:
                state[target][chunk] = value
                sent[source] += 2
                received[target] += 2
        self.assertEqual(state, [reduced] * n)
        self.assertEqual(sent, [12] * n)
        self.assertEqual(received, [12] * n)
        for value in [v for row in initial + state for v in row]:
            self.assertEqual(struct.unpack('<e', struct.pack('<e', value))[0], value)

    def test_float_order(self):
        self.assertEqual((1e16 + -1e16) + 1.0, 1.0)
        self.assertEqual(1e16 + (-1e16 + 1.0), 0.0)

    def test_edge_cases(self):
        self.assertEqual(ring_bytes(19, 1)["sent"], 0)
        self.assertEqual(ring_bytes(0, 8)["sent"], 0)
        for size, n in [(-1, 8), (1, 0)]:
            with self.assertRaises(ValueError):
                ring_bytes(size, n)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AnalyticalChecks))
    if not result.wasSuccessful():
        raise SystemExit(1)
    output = materialize()
    (ROOT / "calculations.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(output, ensure_ascii=False, indent=2))
