class AppError(Exception):
    """Base exception for expected application failures."""


class ValidationError(AppError):
    pass


class PromptNotFoundError(AppError):
    pass


class AIProviderError(AppError):
    pass
