from typing import Any

from eth_typing import Address as Web3Address
from pydantic import validator
from web3.types import ENS
from web3.types import BlockIdentifier as Web3BlockIdentifier

from ethhelper.datatypes.base import Address, BlockIdentifier, Hash32

Validator = Any


def parse_hex_or_strint(v: Any) -> Any:
    if not isinstance(v, str):
        return v
    return int(v, 0)


def block_id_transfer(
    block_identifier: BlockIdentifier
) -> Web3BlockIdentifier:
    if isinstance(block_identifier, Hash32):
        return block_identifier.to_web3()
    return block_identifier


def address_transfer(address: Address | ENS) -> Web3Address | ENS:
    if isinstance(address, Address):
        return address.to_web3()
    return address


def int_validator(*fields: str) -> Validator:
    return validator(*fields, pre=True, allow_reuse=True)(
        parse_hex_or_strint
    )
