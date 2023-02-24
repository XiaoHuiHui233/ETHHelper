from typing import Any


class IntStr:
    def __init__(self, value: "str | int | IntStr") -> None:
        if isinstance(value, IntStr):
            self.value = value.value
            return
        self.value = int(value, 0) if isinstance(value, str) else value

    def to_int_or_str(self) -> int | str:
        if self.value.bit_length() >= 64:
            return str(self.value)
        return self.value

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
        if isinstance(value, HexBytes):
            self.value = value.value
            return
        if isinstance(value, str):
            if not value.startswith("0x"):
                raise ValueError("HexBytes should start with 0x.")
            hex_str = value[2:]
            if len(hex_str) % 2 == 1:
                hex_str = f"0{hex_str}"
            self.value = bytes.fromhex(hex_str)
        else:
            self.value = value

    def to_str(self) -> str:
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
