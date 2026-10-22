from dataclasses import dataclass
from typing import Final

FORBIDDEN: Final[tuple[tuple[str, str], ...]] = (
    ("..", "host contains two consecutive dots"),
    ("://", "host contains a scheme"),
    ("/", "host contains a path"),
    ("?", "host contains a query"),
    ("#", "host contains a fragment"),
    ("@", "host contains userinfo"),
    (":", "host contains a port"),
)


class InvalidTargetError(ValueError):
    """Raised when a target is invalid."""

    def __init__(self, text: str, reason: str) -> None:
        super().__init__(f"{text!r}: {reason}")
        self.text = text
        self.reason = reason


@dataclass(frozen=True, slots=True)
class Target:
    host: str
    port: int = 443

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"

    def __post_init__(self) -> None:
        """
        Validate the host and port. Raises InvalidTargetError if invalid.
        """

        if not self.host:
            raise InvalidTargetError(self.host, "host is empty")
        if any(c.isspace() for c in self.host):
            raise InvalidTargetError(self.host, "host contains whitespace")
        if self.host.startswith(".") or self.host.endswith("."):
            raise InvalidTargetError(self.host, "host starts or ends with a dot")

        for token, description in FORBIDDEN:
            if token in self.host:
                raise InvalidTargetError(self.host, description)

        if type(self.port) is not int:
            raise InvalidTargetError(str(self.port), "port is not an integer")
        if not (1 <= self.port <= 65535):
            raise InvalidTargetError(str(self.port), "port is out of range [1, 65535]")

        # Normalize the host to lowercase, since DNS is case-insensitive.
        object.__setattr__(self, "host", self.host.lower())
