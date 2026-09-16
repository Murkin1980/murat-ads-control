"""Runtime configuration for the read-only Google Ads adapter.

Secret values are checked for presence at the adapter boundary and remain in
runtime environment storage. They are never put into the configuration object,
normalized state, logs, or reports.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


class ConfigurationError(ValueError):
    """Raised when required runtime configuration is incomplete."""


@dataclass(frozen=True)
class GoogleAdsRuntimeConfig:
    """Account selection plus names of runtime-injected secret variables.

    Secret values are intentionally not fields on this object. The official
    client loads them from the environment only after ``require_credentials``
    has passed.
    """

    customer_id: str
    login_customer_id: str | None
    developer_token_env: str = "GOOGLE_ADS_DEVELOPER_TOKEN"
    client_id_env: str = "GOOGLE_ADS_CLIENT_ID"
    client_secret_env: str = "GOOGLE_ADS_CLIENT_SECRET"
    refresh_token_env: str = "GOOGLE_ADS_REFRESH_TOKEN"

    @classmethod
    def from_environment(cls, environ: Mapping[str, str] | None = None) -> "GoogleAdsRuntimeConfig":
        """Read non-secret account selection and secret variable names only."""

        values = os.environ if environ is None else environ
        customer_id = values.get("GOOGLE_ADS_CUSTOMER_ID", "").strip()
        if not customer_id:
            raise ConfigurationError("Missing required Google Ads configuration: GOOGLE_ADS_CUSTOMER_ID")
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

    def require_credentials(self, environ: Mapping[str, str] | None = None) -> None:
        """Fail closed while reporting only names of missing configuration."""

        values = os.environ if environ is None else environ
        missing = [name for name in self.secret_environment_names if not values.get(name, "").strip()]
        if missing:
            joined = ", ".join(missing)
            raise ConfigurationError(f"Missing required Google Ads configuration: {joined}")
