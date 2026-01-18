"""Exceptions for droid-agent-sdk."""


class DroidSDKError(Exception):
    """Base exception for all SDK errors."""


class SessionError(DroidSDKError):
    """Session-related errors."""


class SessionNotFoundError(SessionError):
    """Session not found or not initialized."""


class SessionNotAliveError(SessionError):
    """Session process is not running."""


class TransportError(DroidSDKError):
    """Transport layer errors."""


class FIFOError(TransportError):
    """FIFO communication errors."""


class ProtocolError(DroidSDKError):
    """JSON-RPC protocol errors."""


class StateError(DroidSDKError):
    """State backend errors."""
