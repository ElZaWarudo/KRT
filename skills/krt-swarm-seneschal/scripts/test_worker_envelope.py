#!/usr/bin/env python3
"""Tests for deterministic worker dispatch envelopes."""

from __future__ import annotations

import unittest

from render_worker_envelope import render_envelope
import test_worker_contract
from worker_contract import materialize_contract


class WorkerEnvelopeTest(unittest.TestCase):
    def test_envelope_is_contract_bound_and_terminal_only(self) -> None:
        helper = test_worker_contract.WorkerContractTest()
        contract = materialize_contract(helper.draft(required_certifications=[]))
        envelope = render_envelope(contract, contract_path="run/contract.json", terminal_path="run/terminal.json")

        self.assertEqual(envelope["contract_hash"], contract["contract_hash"])
        self.assertEqual(envelope["worker_profile"], "luna")
        self.assertIn("--contract run/contract.json --input run/terminal.json", envelope["terminal_validation_command"])
        self.assertIn("Return only that JSON object", envelope["prompt"])
        self.assertNotIn("commands_observed", envelope["prompt"])


if __name__ == "__main__":
    unittest.main()
