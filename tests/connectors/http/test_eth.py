import logging
import os
from logging import FileHandler, Formatter

import dotenv
# import orjson
import pytest
from eth_typing import ChecksumAddress
from web3 import Web3
from web3.types import Nonce

from ethhelper.connnectors.http import GethHttpConnector
from ethhelper.datatypes.base import Address, Wei
from ethhelper.datatypes.eth import TxParams
from ethhelper.datatypes.geth import CallOverrideParams
from ethhelper.utils.stdtype import HexBytes

# from web3.contract import utils


dotenv.load_dotenv()

logger = logging.getLogger(__name__)
fmt = Formatter("%(asctime)s [%(name)s][%(levelname)s] %(message)s")
fh = FileHandler(f"./logs/{__name__}", "w", encoding="utf-8")
fh.setFormatter(fmt)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

host = os.getenv("HOST", "localhost")
port = int(os.getenv("PORT", "8545"))
connector = GethHttpConnector(f"http://{host}:{port}/", logger)


@pytest.mark.asyncio
class TestHttpEth:
    async def test_case1(self) -> None:
        logger.info(f"account {await connector.eth_accounts()}")
        logger.info(f"hashrate {await connector.eth_hashrate()}")
        logger.info(f"block number {await connector.eth_block_number()}")
        logger.info(f"chain id {await connector.eth_chain_id()}")
        logger.info(f"gas price {(await connector.eth_gas_price()).value}")
        logger.info(
            "max priority fee per gas "
            f"{(await connector.eth_max_priority_fee_per_gas()).value}"
        )
        logger.info(f"mining {await connector.eth_mining()}")
        logger.info(f"syncing {await connector.eth_syncing()}")

    async def test_case2(self) -> None:
        fee_history = await connector.eth_fee_history(100, "latest")
        logger.info(
            "fee_history "
            f"{fee_history.oldest_block} "
            f"{fee_history.reward} "
            f"{len(fee_history.base_fee_per_gas)} "
            f"{len(fee_history.gas_used_ratio)}"
        )
        fee_history = await connector.eth_fee_history(
            100, fee_history.oldest_block
        )
        logger.info(
            "fee_history "
            f"{fee_history.oldest_block} "
            f"{fee_history.reward} "
            f"{len(fee_history.base_fee_per_gas)} "
            f"{len(fee_history.gas_used_ratio)}"
        )

    async def test_case3(self) -> None:
        addr = Address("0x6C09Fe6aDfCb42002617683D1deAeD7536167575")
        balance = await connector.eth_get_balance(addr)
        nonce = await connector.eth_get_account_nonce(addr)
        logger.info(f"balance {balance.value}")
        logger.info(f"nonce {nonce}")

    async def test_case4(self) -> None:
        code = await connector.eth_get_code(
            Address("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8")
        )
        logger.info(f"code length {len(code.value)}")

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
        logger.info(f"{result.value}, {result}")

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
        logger.info(f"{result.value}, {result}")

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
        logger.info(await connector.eth_call(txn))
