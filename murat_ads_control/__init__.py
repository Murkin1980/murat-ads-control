"""Murat Ads Control — minimal read-only diagnostics core."""

from .diagnostics import diagnose
from .normalize import normalize
from .provider import FixtureAdsProvider, ReadOnlyAdsProvider, load_fixture

__all__ = ["FixtureAdsProvider", "ReadOnlyAdsProvider", "diagnose", "load_fixture", "normalize"]
