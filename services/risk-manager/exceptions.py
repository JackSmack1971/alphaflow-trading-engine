"""Custom exceptions for risk manager."""

class RiskError(Exception):
    """Base class for risk-related errors."""


class RiskLimitBreached(RiskError):
    """Raised when a risk limit is violated."""


class CircuitBreakerTripped(RiskError):
    """Raised when a circuit breaker is triggered."""


class ValidationError(RiskError):
    """Raised when order validation fails."""
