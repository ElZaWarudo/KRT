#!/usr/bin/env python3
"""Build one delivery-navigator fixture: a small repo with planning docs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REQUIREMENTS = """# Requirements: clinic online booking

Status: validated with client on 2026-10-01.

## Goal
Reduce no-shows and phone booking load for a 6-clinic dental chain.

## Actors
Patient, Receptionist, Clinic manager.

## In scope
- FR-1 Patients book an appointment online for a chosen clinic, dentist and slot.
- FR-2 Patients cancel or reschedule up to 24 h before the appointment.
- FR-3 Receptionists see the day schedule per clinic and move appointments.
- FR-4 The system sends an SMS reminder 24 h before each appointment.
- FR-5 Clinic managers see a weekly no-show report.

## Out of scope
- Integration with Dentrix (phase 2, not planned).
- Payments.

## Non-functional
- NFR-1 Patient data is stored in the EU and encrypted at rest.
- NFR-2 Booking page loads in under 2 s at p95 on 4G.
- NFR-3 Available 99.5% during clinic opening hours.

## Constraints
- Team: 2 full-stack developers, 1 part-time designer, client product owner available weekly.
- SMS provider not chosen yet; client prefers an EU provider.

## Acceptance criteria
- AC-1 A patient completes a booking in at most 3 screens and receives a confirmation.
- AC-2 A booking cancelled less than 24 h before is rejected with a message.
- AC-3 A reminder SMS is sent between 23 and 25 h before the slot.
- AC-4 The weekly report counts no-shows per clinic and dentist.

## Open questions
- Q-1 Does each clinic have its own opening hours and holidays?
"""

VISION = """# Product vision: Fleetly

Fleetly helps small logistics companies track vans and deliveries.

## Goals for this year
- Replace the spreadsheet dispatch board with a live board.
- Give drivers a mobile app for proof of delivery.
- Offer customers a tracking link.
"""

SPEC_BOARD = """# Spec: dispatch board

Dispatchers assign deliveries to vans on a live board. Needs van positions
from the telematics feed (see telematics.md). Status: approved.
"""

SPEC_TELEMATICS = """# Spec: telematics ingestion

Ingest GPS positions from the vendor webhook every 30 s per van. Vendor
contract signed; webhook docs pending from vendor. Status: approved.
"""

SPEC_POD = """# Spec: proof of delivery app

Drivers capture a photo and signature on delivery. Offline support is
required because rural routes lose signal. Status: draft, offline sync
approach undecided.
"""


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def setup(case: str, root: Path) -> None:
    origin, repo = root / "origin.git", root / "repo"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(repo)], check=True, capture_output=True)
    git(repo, "config", "user.name", "Eval Dev")
    git(repo, "config", "user.email", "dev@example.com")
    if case.startswith("fleet-roadmap"):
        write(repo, "README.md", "# fleetly\n\nSee docs/ for product docs.\n")
        write(repo, "docs/vision.md", VISION)
        write(repo, "docs/specs/dispatch-board.md", SPEC_BOARD)
        write(repo, "docs/specs/telematics.md", SPEC_TELEMATICS)
        write(repo, "docs/specs/proof-of-delivery.md", SPEC_POD)
    else:
        write(repo, "README.md", "# clinic-booking\n")
        write(repo, "docs/requirements/clinic-booking.md", REQUIREMENTS)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "docs: initial")
    git(repo, "push", "-q", "origin", "main")


if __name__ == "__main__":
    setup(sys.argv[1], Path(sys.argv[2]))
