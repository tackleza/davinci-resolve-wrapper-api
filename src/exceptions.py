"""
exceptions.py — Custom exceptions for DaVinci Resolve Wrapper API
"""


class ResolveError(Exception):
    """Base exception for all Resolve wrapper errors."""

    def __init__(self, message: str, code: str = "RESOLVE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ResolveNotRunningError(ResolveError):
    """Raised when Resolve is not running or cannot be reached."""

    def __init__(self, message: str = "DaVinci Resolve is not running. Start Resolve first."):
        super().__init__(message, code="RESOLVE_NOT_RUNNING")


class ResolveFreeVersionError(ResolveError):
    """Raised when external scripting is attempted on the free version."""

    def __init__(self, message: str = "External scripting requires DaVinci Resolve Studio (paid version)."):
        super().__init__(message, code="FREE_VERSION")


class ResolveScriptingDisabledError(ResolveError):
    """Raised when external scripting is disabled in Resolve preferences."""

    def __init__(self, message: str = "External scripting is disabled. Enable it in: Preferences → General → External scripting using → Local"):
        super().__init__(message, code="SCRIPTING_DISABLED")


class ResolveConnectionError(ResolveError):
    """Raised when the API connection to Resolve fails."""

    def __init__(self, message: str = "Failed to connect to DaVinci Resolve API."):
        super().__init__(message, code="CONNECTION_FAILED")


class ProjectNotFoundError(ResolveError):
    """Raised when a project cannot be found."""

    def __init__(self, project_name: str):
        super().__init__(f"Project not found: '{project_name}'", code="PROJECT_NOT_FOUND")


class TimelineNotFoundError(ResolveError):
    """Raised when a timeline cannot be found."""

    def __init__(self, timeline_name: str | None = None, timeline_index: int | None = None):
        identifier = timeline_name or str(timeline_index)
        super().__init__(f"Timeline not found: '{identifier}'", code="TIMELINE_NOT_FOUND")


class ClipNotFoundError(ResolveError):
    """Raised when a clip cannot be found."""

    def __init__(self, clip_id: str):
        super().__init__(f"Clip not found: '{clip_id}'", code="CLIP_NOT_FOUND")


class TimelineItemNotFoundError(ResolveError):
    """Raised when a timeline item cannot be found by its position."""

    def __init__(self, detail: str = ""):
        super().__init__(f"Timeline item not found: {detail}", code="TIMELINE_ITEM_NOT_FOUND")


class InvalidPageError(ResolveError):
    """Raised when an invalid page name is provided."""

    VALID_PAGES = ["media", "cut", "edit", "fusion", "color", "fairlight", "deliver"]

    def __init__(self, page_name: str):
        valid = ", ".join(self.VALID_PAGES)
        super().__init__(
            f"Invalid page: '{page_name}'. Valid pages: {valid}",
            code="INVALID_PAGE"
        )


class RenderInProgressError(ResolveError):
    """Raised when an operation cannot proceed while rendering is active."""

    def __init__(self):
        super().__init__("Cannot perform this action while rendering is in progress.", code="RENDER_IN_PROGRESS")


class InvalidRenderSettingsError(ResolveError):
    """Raised when render settings are invalid or missing required fields."""

    def __init__(self, message: str):
        super().__init__(message, code="INVALID_RENDER_SETTINGS")


class APIError(ResolveError):
    """Raised when a Resolve API call fails."""

    def __init__(self, method: str, detail: str):
        super().__init__(f"API error in {method}: {detail}", code="API_ERROR")
