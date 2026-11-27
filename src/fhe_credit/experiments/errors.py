"""Errors with safe, structured messages for the experiment executor."""


class ExperimentError(RuntimeError):
    """Base error for executor operations that must not expose sensitive input."""


class AdapterNotAllowedError(ExperimentError):
    """Raised for an absent or unapproved adapter identifier."""


class ExecutionAuthorizationError(ExperimentError):
    """Raised when processing was not explicitly authorized at the interface."""


class ArtifactIntegrityError(ExperimentError):
    """Raised when an input/output artifact is unavailable or altered."""


class ResumeNotSupportedError(ExperimentError):
    """Raised when an adapter has no declared computational resume capability."""


class ConcurrentRunError(ExperimentError):
    """Raised when another process holds the exclusive lock for the same run."""
