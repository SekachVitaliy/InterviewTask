class NotFound(Exception):
    """Requested entity does not exist."""


class Conflict(Exception):
    """Request conflicts with the current state."""


class InsufficientStock(Conflict):
    pass


class InvalidState(Conflict):
    pass
