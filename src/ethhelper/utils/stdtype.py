# pyright: reportUnnecessaryIsInstance=false
from typing import Any

from hexbytes import HexBytes as W3HexBytes


class IntStr:
    def __init__(self, value: "str | int | IntStr") -> None:
        self.value: int
        if isinstance(value, IntStr):
            self.value = value.value
        elif isinstance(value, int):
            self.value = value
        elif isinstance(value, str):
            self.value = int(value, 0)
        else:
            raise TypeError(
                "The value type should be str or int or IntStr!"
            )

    def to_int_or_str(self) -> int | str:
        if self.value.bit_length() >= 64:
            return str(self.value)
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __lt__(self, __o: Any) -> bool:
        o = IntStr(__o)
        return self.value < o.value

    def __le__(self, __o: Any) -> bool:
        o = IntStr(__o)
        return self.value <= o.value

    def __eq__(self, __o: Any) -> bool:
        o = IntStr(__o)
        return self.value == o.value

    def __ne__(self, __o: Any) -> bool:
        o = IntStr(__o)
        return self.value != o.value

    def __ge__(self, __o: Any) -> bool:
        o = IntStr(__o)
        return self.value >= o.value

    def __gt__(self, __o: Any) -> bool:
        o = IntStr(__o)
        return self.value > o.value

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> Any:
        if isinstance(value, IntStr):
            return value
        if isinstance(value, int) or isinstance(value, str):
            return cls(value)
        return value


class HexBytes:
    def __init__(self, value: "str | bytes | HexBytes") -> None:
        self.value: bytes
        if isinstance(value, HexBytes):
            self.value = value.value
        elif isinstance(value, W3HexBytes):
            self.value = bytes(value)
        elif isinstance(value, bytes):
            self.value = value
        elif isinstance(value, str):
            if not value.startswith("0x"):
                raise ValueError("HexBytes should start with 0x.")
            hex_str = value[2:]
            if len(hex_str) % 2 == 1:
                hex_str = f"0{hex_str}"
            self.value = bytes.fromhex(hex_str)
        else:
            raise TypeError(
                "The value type should be str or bytes or HexBytes!"
            )

    def __hash__(self) -> int:
        return hash(self.value)

    def __lt__(self, __o: Any) -> bool:
        o = HexBytes(__o)
        return self.value < o.value

    def __le__(self, __o: Any) -> bool:
        o = HexBytes(__o)
        return self.value <= o.value

    def __eq__(self, __o: Any) -> bool:
        o = HexBytes(__o)
        return self.value == o.value

    def __ne__(self, __o: Any) -> bool:
        o = HexBytes(__o)
        return self.value != o.value

    def __ge__(self, __o: Any) -> bool:
        o = HexBytes(__o)
        return self.value >= o.value

    def __gt__(self, __o: Any) -> bool:
        o = HexBytes(__o)
        return self.value > o.value

    def __str__(self) -> str:
        return f"0x{self.value.hex()}"

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> Any:
        if isinstance(value, HexBytes):
            return value
        if isinstance(value, bytes) or \
                (isinstance(value, str) and value.startswith("0x")):
            return cls(value)
        return value
