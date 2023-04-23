from decimal import (
    Decimal,
)
from typing import (
    Any,
    NewType,
)

from eth_typing import (
    Address as Web3Address,
    BlockNumber,
    Hash32 as EthHash32,
)
from hexbytes import (
    HexBytes as Web3HexBytes,
)
from web3.types import (
    BlockParams,
    Wei as Web3Wei,
)


class IntStr:
    """A class that represents an integer value that can be initialized
    from a string or another ``IntStr`` instance.
    
    This class is designed to work with the ``orjson`` library, and provides a
    way to represent integer values that may be too large to be encoded using
    64 bits.
    
    By using an ``IntStr`` instance to represent such values, you can ensure
    that the integers are passed around as Python integers but still allow them
    to be encoded as strings if necessary.

    The ``value`` is the value to be initialized. If a string is provided, it
    will be converted to an integer.
    """
    def __init__(self, value: "str | int | IntStr") -> None:
        self.value: int
        """An integer value."""
        if isinstance(value, IntStr):
            self.value = value.value
        elif isinstance(value, int):
            self.value = value
        else:
            assert isinstance(value, str)
            self.value = int(value, 0)

    def to_int_or_str(self) -> int | str:
        """Returns the integer value as a string if it has 64 or more bits,
        otherwise it returns the integer value itself.

        Returns:
            The integer value as a string if it has 64 or more bits, otherwise
            the integer value itself.
        """
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
        """Validates and returns the value as an ``IntStr`` instance.

        Args:
            value: The value to be validated and returned.

        Returns:
            An ``IntStr`` instance that represents the validated value.

        Raises:
            TypeError: If the value is not an ``IntStr``, int, or str.
        """
        if isinstance(value, IntStr):
            return value
        if isinstance(value, int) or isinstance(value, str):
            return cls(value)
        return value


class HexBytes:
    """A class that represents a byte string that can be initialized from a
    string, bytes, ``hexbytes.HexBytes`` instance or another ``HexBytes``
    instance.
    """
    def __init__(self, value: "str | bytes | HexBytes") -> None:
        self.value: bytes
        if isinstance(value, HexBytes):
            self.value = value.value
        elif isinstance(value, Web3HexBytes):
            self.value = bytes(value)
        elif isinstance(value, bytes):
            self.value = value
        else:
            assert isinstance(value, str)
            if not value.startswith("0x"):
                raise ValueError("HexBytes should start with 0x.")
            hex_str = value[2:]
            if len(hex_str) % 2 == 1:
                hex_str = f"0{hex_str}"
            self.value = bytes.fromhex(hex_str)

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
        """Validates and converts a value to a ``HexBytes`` instance.

        Args:
            value: The value to be validated and converted.

        Returns:
            A ``HexBytes`` instance representing the input value.

        Raises:
            TypeError: If the input value is not a ``HexBytes``, bytes, or
                string starting with "0x".
        """
        if isinstance(value, HexBytes):
            return value
        if isinstance(value, bytes) or \
                (isinstance(value, str) and value.startswith("0x")):
            return cls(value)
        return value


class Hash32(HexBytes):
    """A subclass of ``HexBytes`` that represents a 32-byte hash value."""
    def to_web3(self) -> EthHash32:
        """Returns an ``eth_typing.Hash32`` instance that represents the hash
        value.

        Returns:
            An ``eth_typing.Hash32`` instance that represents the hash value.
        """
        return EthHash32(self.value)


class Address(HexBytes):
    """A subclass of HexBytes that represents an Ethereum address (20 bytes).
    """
    def to_web3(self) -> Web3Address:
        """Returns a ``eth_typing.Address`` instance that represents the
        address.

        Returns:
            A ``eth_typing.Address`` instance that represents the address.
        """
        return Web3Address(self.value)


BlockIdentifier = BlockParams | BlockNumber | Hash32
"""A union type that can represent a block number, a block hash, or the strings
"latest", "earliest", or "pending".
"""
Gas = NewType("Gas", int)
"""A new type that represents a gas value (an integer)."""


class Wei(IntStr):
    """A subclass of ``IntStr`` that represents a value in wei (the smallest
    unit of ether in Ethereum).
    """
    def to_web3(self) -> Web3Wei:
        """Returns a ``web3.types.Wei`` instance that represents the value in
        wei.

        Returns:
            A ``web3.types.Wei`` instance that represents the value in wei.
        """
        return Web3Wei(self.value)
    
    @classmethod
    def from_gwei(cls, value: int) -> "Wei":
        """Class method that converts a value in gigawei to wei.

        Args:
            value: An integer value in gigawei.

        Returns:
            A ``Wei`` instance that represents the converted value in wei.
        """
        return cls(value * 1_000_000_000)

    @classmethod
    def from_eth(cls, value: int | float | Decimal) -> "Wei":
        """Class method that converts a value in ether to wei.

        Args:
            value: A value in ether.

        Returns:
            Wei: A ``Wei`` instance that represents the converted value in wei.
        """
        return cls(int(value * 1_000_000_000_000_000_000))
