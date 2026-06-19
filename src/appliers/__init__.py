"""Appliers package — Auto-postulación con Playwright."""
from .base_applier import BaseApplier, ApplyResult
from .multitrabajos_applier import MultitrabajosApplier

__all__ = ["BaseApplier", "ApplyResult", "MultitrabajosApplier"]
