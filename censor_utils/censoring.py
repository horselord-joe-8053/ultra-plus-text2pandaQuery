"""Data censoring utilities for reversible data anonymization.

This module provides reversible censoring for sensitive fields and text.
- Censoring: replaces originals with stable placeholders and records mapping
- Desensorizing: restores placeholders back to originals using recorded mapping
"""

import hashlib
from typing import Any, Dict


class CensoringService:
    """Provides reversible censoring for sensitive fields and text.

    - Censoring: replaces originals with stable placeholders and records mapping
    - Desensorizing: restores placeholders back to originals using recorded mapping
    """

    def __init__(self) -> None:
        self.placeholder_to_original: Dict[str, str] = {}

    def _store_mapping(self, placeholder: str, original: str) -> str:
        if original and placeholder:
            self.placeholder_to_original[placeholder] = original
        return placeholder

    def censor_vin(self, vin: Any) -> str:  # type: ignore[name-defined]
        if vin is None:
            return ""
        vin_str = str(vin).strip()
        if vin_str == "":
            return ""
        if len(vin_str) < 3:
            return vin_str
        hashed = hashlib.md5(vin_str.encode()).hexdigest()[:8].upper()
        placeholder = f"VIN_{hashed}"
        return self._store_mapping(placeholder, vin_str)

    def censor_dealer_code(self, dealer_code: Any) -> str:  # type: ignore[name-defined]
        if dealer_code is None:
            return ""
        dealer_str = str(dealer_code).strip()
        if dealer_str == "":
            return ""
        hashed = hashlib.md5(dealer_str.encode()).hexdigest()[:6].upper()
        placeholder = f"DEALER_{hashed}"
        return self._store_mapping(placeholder, dealer_str)

    def censor_sub_dealer_code(self, sub_dealer_code: Any) -> str:  # type: ignore[name-defined]
        if sub_dealer_code is None:
            return ""
        sub_dealer_str = str(sub_dealer_code).strip()
        if sub_dealer_str == "":
            return ""
        hashed = hashlib.md5(sub_dealer_str.encode()).hexdigest()[:6].upper()
        placeholder = f"SUB_DEALER_{hashed}"
        return self._store_mapping(placeholder, sub_dealer_str)

    def censor_text(self, text: str) -> str:
        if not isinstance(text, str):
            return str(text)
        result = text
        for placeholder, original in self.placeholder_to_original.items():
            result = result.replace(original, placeholder)
        return result

    def desensorize_text(self, text: str | None) -> str:
        if not isinstance(text, str):
            return str(text)
        result = text
        for placeholder, original in self.placeholder_to_original.items():
            result = result.replace(placeholder, original)
        return result

    def get_stats(self) -> Dict[str, int | Dict[str, str]]:
        return {
            'total_censored_fields': len(self.placeholder_to_original),
            'vin_mappings': len([k for k in self.placeholder_to_original if k.startswith('VIN_')]),
            'dealer_mappings': len([k for k in self.placeholder_to_original if k.startswith('DEALER_')]),
            'sub_dealer_mappings': len([k for k in self.placeholder_to_original if k.startswith('SUB_DEALER_')]),
            'sample_mappings': dict(list(self.placeholder_to_original.items())[:5]),
        }