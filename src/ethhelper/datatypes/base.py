# pyright: reportUnnecessaryIsInstance=false
from typing import Any, NewType

from eth_typing import Address as Web3Address
from eth_typing import BlockNumber
from eth_typing import Hash32 as EthHash32
from hexbytes import HexBytes as Web3HexBytes
from web3.types import BlockParams
from web3.types import Wei as Web3Wei


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
        elif isinstance(value, Web3HexBytes):
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


class Hash32(HexBytes):
    def to_web3(self) -> EthHash32:
        return EthHash32(self.value)


class Address(HexBytes):
    def to_web3(self) -> Web3Address:
        return Web3Address(self.value)


BlockIdentifier = BlockParams | BlockNumber | Hash32
Gas = NewType("Gas", int)


class Wei(IntStr):
    def to_web3(self) -> Web3Wei:
        return Web3Wei(self.value)
