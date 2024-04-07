from .fireapp_exception import FireAppException


class EventNotFoundError(FireAppException):
    def __init__(self, event_id, *args):
        super().__init__(f"Event not found", *args)
        self.event_id = event_id

    def __str__(self):
        # Optionally customize the string representation for this specific error
        return f"{self.message}: Event ID {self.event_id} could not be located."


class InvalidArgumentError(FireAppException):
    def __init__(self, *args):
        super().__init__(f"Invalid argument(s)", *args)

    def __str__(self):
        # Optionally customize the string representation for this specific error
        return f"{self.message}: unexpected values in the payload"
