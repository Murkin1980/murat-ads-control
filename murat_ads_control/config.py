"""Safe runtime configuration contract reserved for the later real adapter.

This checkpoint deliberately does not authenticate or instantiate a Google Ads
client. It only names values that a future adapter may receive from the
runtime environment; secret values are never stored in this repository.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


class ConfigurationError(ValueError):
    """Raised when a future runtime configuration is incomplete."""


@dataclass(frozen=True)
class GoogleAdsRuntimeConfig:
    """Non-secret account identifiers plus names of runtime secret variables."""

    customer_id: str
    login_customer_id: str | None
    developer_token_env: str = "GOOGLE_ADS_DEVELOPER_TOKEN"
    client_id_env: str = "GOOGLE_ADS_CLIENT_ID"
    client_secret_env: str = "GOOGLE_ADS_CLIENT_SECRET"
    refresh_token_env: str = "GOOGLE_ADS_REFRESH_TOKEN"

    @classmethod
    def from_environment(cls, environ: Mapping[str, str] | None = None) -> "GoogleAdsRuntimeConfig":
        """Read identifiers and secret *names* from runtime environment only.

        The secret values are intentionally not returned. CP-002 will decide
        how a real read-only adapter receives them.
        """

        values = os.environ if environ is None else environ
        customer_id = values.get("GOOGLE_ADS_CUSTOMER_ID", "").strip()
        if not customer_id:
            raise ConfigurationError("GOOGLE_ADS_CUSTOMER_ID is required at runtime")
        login_customer_id = values.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip() or None
        return cls(customer_id=customer_id, login_customer_id=login_customer_id)

    @property
    def secret_environment_names(self) -> tuple[str, ...]:
        return (
            self.developer_token_env,
            self.client_id_env,
            self.client_secret_env,
            self.refresh_token_env,
        )
