"""Read-only provider boundary and fixture implementation.

The provider exposes exactly one operation: reading a snapshot. A future Google
Ads adapter can implement the same protocol without exposing provider write
operations to the diagnostic capability.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol


class ProviderInputError(ValueError):
    """Raised when a fixture does not have the minimal provider shape."""


@dataclass(frozen=True)
class RawAdsSnapshot:
    """The narrow raw contract consumed by normalization.

    ``account`` and each campaign retain provider-shaped fields because that is
    the adapter boundary. Only account state, campaigns, delivery settings,
    entities, targeting, conversions, and recent performance belong here.
    """

    account: Mapping[str, Any]
    campaigns: tuple[Mapping[str, Any], ...]
    source: str = "provider"

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any], *, source: str = "fixture") -> "RawAdsSnapshot":
        if not isinstance(payload, Mapping):
            raise ProviderInputError("provider snapshot must be a JSON object")
        account = payload.get("account")
        campaigns = payload.get("campaigns")
        if not isinstance(account, Mapping):
            raise ProviderInputError("provider snapshot requires an account object")
        if not isinstance(campaigns, list):
            raise ProviderInputError("provider snapshot requires a campaigns array")
        if not all(isinstance(campaign, Mapping) for campaign in campaigns):
            raise ProviderInputError("every campaign must be an object")
        return cls(
            account=copy.deepcopy(dict(account)),
            campaigns=tuple(copy.deepcopy(dict(campaign)) for campaign in campaigns),
            source=source,
        )


class ReadOnlyAdsProvider(Protocol):
    """Minimal adapter contract for the diagnostic capability."""

    def read_state(self) -> RawAdsSnapshot:
        """Return the fields needed for diagnostics, without side effects."""


@dataclass
class FixtureAdsProvider:
    """Provider backed by a local, sanitized JSON fixture."""

    snapshot: RawAdsSnapshot

    @classmethod
    def from_path(cls, path: str | Path) -> "FixtureAdsProvider":
        fixture_path = Path(path)
        with fixture_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return cls(RawAdsSnapshot.from_mapping(payload, source=f"fixture:{fixture_path.name}"))

    def read_state(self) -> RawAdsSnapshot:
        # Return a fresh snapshot so a capability cannot accidentally alter the
        # provider's stored fixture state while processing it.
        return RawAdsSnapshot(
            account=copy.deepcopy(dict(self.snapshot.account)),
            campaigns=tuple(copy.deepcopy(dict(campaign)) for campaign in self.snapshot.campaigns),
            source=self.snapshot.source,
        )


def load_fixture(path: str | Path) -> ReadOnlyAdsProvider:
    """Load a fixture through the same provider contract used by adapters."""

    return FixtureAdsProvider.from_path(path)
