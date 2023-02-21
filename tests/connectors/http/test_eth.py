import os

import dotenv
# import orjson
import pytest
from eth_typing import ChecksumAddress
from web3 import Web3
from web3.types import Nonce
# from web3.contract import utils

from ethhelper.connnectors.http import GethHttpConnector
from ethhelper.datatypes.base import Address, Wei
from ethhelper.datatypes.eth import TxParams
from ethhelper.datatypes.geth import CallOverrideParams
from ethhelper.utils.stdtype import HexBytes

dotenv.load_dotenv()


connector = GethHttpConnector(
    os.getenv("HOST", "localhost"), int(os.getenv("PORT", "8545"))
)


@pytest.mark.asyncio
class TestHttpEth:
    async def test_case1(self) -> None:
        print("account", await connector.eth_accounts())
        print("hashrate", await connector.eth_hashrate())
        print("block number", await connector.eth_block_number())
        print("chain id", await connector.eth_chain_id())
        print("gas price", (await connector.eth_gas_price()).value)
        print(
            "max priority fee per gas",
            (await connector.eth_max_priority_fee_per_gas()).value
        )
        print("mining", await connector.eth_mining())
        print("syncing", await connector.eth_syncing())

    async def test_case2(self) -> None:
        fee_history = await connector.eth_fee_history(100, "latest")
        print(
            "fee_history",
            fee_history.oldest_block,
            fee_history.reward,
            len(fee_history.base_fee_per_gas),
            len(fee_history.gas_used_ratio)
        )
        fee_history = await connector.eth_fee_history(
            100, fee_history.oldest_block
        )
        print(
            "fee_history",
            fee_history.oldest_block,
            fee_history.reward,
            len(fee_history.base_fee_per_gas),
            len(fee_history.gas_used_ratio)
        )

    async def test_case3(self) -> None:
        addr = Address("0x6C09Fe6aDfCb42002617683D1deAeD7536167575")
        balance = await connector.eth_get_balance(addr)
        nonce = await connector.eth_get_account_nonce(addr)
        print("balance", balance.value)
        print("nonce", nonce)

    async def test_case4(self) -> None:
        code = await connector.eth_get_code(
            Address("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8")
        )
        print("code", len(code.value))

    async def test_case5(self) -> None:
        txn = TxParams(  # type: ignore
            to=Address("0x6C09Fe6aDfCb42002617683D1deAeD7536167575")
        )
        over: dict[ChecksumAddress, CallOverrideParams] = {
            Web3.to_checksum_address(
                "0x6C09Fe6aDfCb42002617683D1deAeD7536167575"
            ):
            CallOverrideParams(balance=Wei(0), nonce=Nonce(0))  # type: ignore
        }
        result = await connector.eth_call(txn, state_override=over)
        print(result.value, result.to_str())

    async def test_case6(self) -> None:
        txn = TxParams(  # type: ignore
            from_=Address(  # type: ignore
                "0x6C09Fe6aDfCb42002617683D1deAeD7536167575"
            ),
            to=Address("0x6C09Fe6aDfCb42002617683D1deAeD7536167575"),
            value=Wei(1000),
            nonce=Nonce(1)
        )
        over: dict[ChecksumAddress, CallOverrideParams] = {
            Web3.to_checksum_address(
                "0x6C09Fe6aDfCb42002617683D1deAeD7536167575"
            ):
            CallOverrideParams(  # type: ignore
                balance=Wei(1000), nonce=Nonce(0)
            )
        }
        result = await connector.eth_call(txn, state_override=over)
        print(result.value, result.to_str())

    async def test_case7(self) -> None:
        # with open("./tmp/UniswapV3Pool.json", "r") as rf:
        #     ABI = orjson.loads("".join(rf.readlines()))["abi"]
        # contract = connector.w3.eth.contract(
        #     Web3.to_checksum_address(
        #         "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
        #     ),
        #     abi=ABI
        # )
        # txn = utils.prepare_transaction(
        #     Web3.to_checksum_address(
        #         "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
        #     ),
        #     connector.w3,
        #     fn_identifier=contract.functions.slot0().function_identifier,
        #     contract_abi=contract.functions.slot0().contract_abi,
        #     fn_abi=contract.functions.slot0().abi,
        #     transaction={
        #         "to": Web3.to_checksum_address(
        #             "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
        #         )
        #     }
        # )
        # print(txn)
        # call get uniswap slot0
        txn = TxParams(  # type: ignore
            data=HexBytes("0x3850c7bd"),
            to=Address("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"),
        )
        print((await connector.eth_call(txn)).to_str())
