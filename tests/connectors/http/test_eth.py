import logging
import os
from logging import FileHandler, Formatter

import dotenv
import pytest
from eth_typing import BlockNumber, ChecksumAddress
from web3 import Web3
from web3.types import Nonce

from ethhelper import GethHttpConnector
from ethhelper.types import (
    Address,
    CallOverrideParams,
    FilterParams,
    Hash32,
    HexBytes,
    TxParams,
    Wei
)

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
        hash = Hash32(
            "0x19e59670614c583c2043517f3f39c03"
            "c3be788d7c402dd0c946e9d1dbafe56ee"
        )
        raw_txn = await connector.eth_get_raw_transaction(hash)
        txn = await connector.eth_get_transaction(hash)
        logger.info(raw_txn)
        logger.info(txn)

    async def test_case6(self) -> None:
        height = BlockNumber(16716880)
        txn_cnt = await connector.eth_get_transaction_cnt_by_block(height)
        for i in range(txn_cnt):
            raw_txn = \
                await connector.eth_get_raw_transaction_by_block(height, i)
            txn = await connector.eth_get_transaction_by_block(height, i)
            logger.info(raw_txn)
            logger.info(txn)
        logger.info(f"height: {height}, cnt: {txn_cnt}")

    async def test_case7(self) -> None:
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

    async def test_case8(self) -> None:
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

    async def test_case9(self) -> None:
        # call get uniswap slot0
        txn = TxParams(  # type: ignore
            data=HexBytes("0x3850c7bd"),
            to=Address("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"),
        )
        logger.info(await connector.eth_call(txn))
        logger.info(await connector.eth_estimate_gas(txn))

    async def test_case10(self) -> None:
        block_now = await connector.eth_get_block("latest", True)
        logger.info(block_now.number)
        block_before_the_merge = await connector.eth_get_block(
            BlockNumber(15537392)
        )
        logger.info(block_before_the_merge.number)
        block_before_eip_1559 = await connector.eth_get_block(
            BlockNumber(12964998)
        )
        logger.info(block_before_eip_1559.number)

    async def test_case11(self) -> None:
        receipt = await connector.eth_wait_for_transaction_receipt(
            Hash32(
                "0xc5831b6a76a694ba1bec2d88ca8e4a09"
                "7d8372187b03ca29cfb0a58bb527da7c"
            )
        )
        logger.info(receipt.transaction_hash)
        receipt = await connector.eth_get_transaction_receipt(
            Hash32(
                "0xc5831b6a76a694ba1bec2d88ca8e4a09"
                "7d8372187b03ca29cfb0a58bb527da7c"
            )
        )
        logger.info(receipt.transaction_hash)

    async def test_case12(self) -> None:
        height = await connector.eth_block_number()
        logs = await connector.get_logs(
            FilterParams(  # type: ignore
                address=Address("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"),
                fromBlock=height-1000,
                toBlock=height,
            )
        )
        for log in logs:
            logger.info(f"{log.block_number}, {log.log_index}")
