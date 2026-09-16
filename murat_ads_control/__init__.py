"""Murat Ads Control — minimal read-only diagnostics core."""

from .diagnostics import diagnose
from .google_ads import GoogleAdsProvider
from .normalize import normalize
from .provider import FixtureAdsProvider, ReadOnlyAdsProvider, load_fixture

__all__ = [
    "FixtureAdsProvider",
    "GoogleAdsProvider",
    "ReadOnlyAdsProvider",
    "diagnose",
    "load_fixture",
    "normalize",
]
