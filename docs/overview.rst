.. _overview:

Overview
========

The purpose of this page is to give you a sense of everything ETHHelper can do
and to serve as a quick reference guide. You'll find a summary of each feature
with links to learn more.

Configuration
~~~~~~~~~~~~~

In order to use interfaces of ETHHelper, you need to provide a hostname
and port of your Geth Web Services(include HTTP and WebSocket) and make sure
`net/txpool/eth` namespaces are opened.

Third-party node services are available, but not all namespaces are guaranteed
to be available. Nor does it ensure that the parsing of the information is
legal.

Geth HTTP Connector
-------------------

To use the HTTP interface of GethHTTPConnector, you need to provide the
hostname and port of the HTTP service of your Geth node. If on the machine
where Geth is deployed, this should default to ``http://localhost:8545``.

.. note::
    Please pay attention to marking ``http/https`` headers correctly, which is
    especially important when using third-party node services.

Geth HTTP Connector Example
---------------------------

.. code-block:: python

    >>> from ethhelper import GethHttpConnector
    >>> connector = GethHttpConnector("http://localhost:8545/")
    >>> await connector.test_connection()
    True

.. note::

    All interfaces in this repo rely on the asynchronous environment, so the
    asyncio environment is required when using the REPL for interactive coding.
    This can be done by running `python -m asyncio` directly on the command
    line or shell (instead of `python`).

Geth New Block Subscriber
-------------------------

In order to use GethNewBlockSubscriber, you need to provide the hostname and
port of the websocket service of your Geth node. If on the machine where Geth
is deployed, you need to enable the Websocket service in the command lines of
the startup of the Geth node(or some kind of config file). In this case, the
hostname and port provided should default to ``ws://localhost:8546``.

.. note::
    Please pay attention to marking ``ws/wss`` headers correctly, which is
    especially important when using third-party node services.

Geth New Block Subscriber Example
---------------------------------

You can see an example of this feature
`here <https://github.com/XiaoHuiHui233/ETHHelper/blob/main/tests/connectors/ws/test_block.py>`_.

HTTP API
~~~~~~~~

GethHttpConnector of ETHHelper provides a series of HTTP APIs, including
repackaging of ``eth/net`` namespaces interfaces of `Web3.py`_ (based on the
data structure defined by using `pydantic`_). It also supported for native
``txpool`` namespace of Geth node. On those basis, a series of convenient and
fast asynchronous aggregation interfaces (named as ``custom`` space) is
provided.

.. note::
    GethHttpConnector does not use the same namespace naming method as
    `Web3.py`_ (ie, one submodule per namespace). On the contrary, for flat
    design and quick access, GethHttpConnector uses the first word of the
    function name to distinguish the namespace. The only exception is that the
    ``custom`` space ignores the first word directly.

Eth Namespace
-------------

- :meth:`GethHttpConnector.eth_accounts() <ethhelper.GethHttpConnector.eth_accounts>`
- :meth:`GethHttpConnector.eth_hashrate() <ethhelper.GethHttpConnector.eth_hashrate>`
- :meth:`GethHttpConnector.eth_block_number() <ethhelper.GethHttpConnector.eth_block_number>`
- :meth:`GethHttpConnector.eth_chain_id() <ethhelper.GethHttpConnector.eth_chain_id>`
- :meth:`GethHttpConnector.eth_gas_price() <ethhelper.GethHttpConnector.eth_gas_price>`
- :meth:`GethHttpConnector.eth_max_priority_fee_per_gas() <ethhelper.GethHttpConnector.eth_max_priority_fee_per_gas>`
- :meth:`GethHttpConnector.eth_mining() <ethhelper.GethHttpConnector.eth_mining>`
- :meth:`GethHttpConnector.eth_syncing() <ethhelper.GethHttpConnector.eth_syncing>`
- :meth:`GethHttpConnector.eth_fee_history() <ethhelper.GethHttpConnector.eth_fee_history>`
- :meth:`GethHttpConnector.eth_call() <ethhelper.GethHttpConnector.eth_call>`
- :meth:`GethHttpConnector.eth_estimate_gas() <ethhelper.GethHttpConnector.eth_estimate_gas>`
- :meth:`GethHttpConnector.eth_get_transaction() <ethhelper.GethHttpConnector.eth_get_transaction>`
- :meth:`GethHttpConnector.eth_get_raw_transaction() <ethhelper.GethHttpConnector.eth_get_raw_transaction>`
- :meth:`GethHttpConnector.eth_get_transaction_by_block() <ethhelper.GethHttpConnector.eth_get_transaction_by_block>`
- :meth:`GethHttpConnector.eth_get_raw_transaction_by_block() <ethhelper.GethHttpConnector.eth_get_raw_transaction_by_block>`
- :meth:`GethHttpConnector.eth_get_transaction_cnt_by_block() <ethhelper.GethHttpConnector.eth_get_transaction_cnt_by_block>`
- :meth:`GethHttpConnector.eth_get_balance() <ethhelper.GethHttpConnector.eth_get_balance>`
- :meth:`GethHttpConnector.eth_get_code() <ethhelper.GethHttpConnector.eth_get_code>`
- :meth:`GethHttpConnector.eth_get_account_nonce() <ethhelper.GethHttpConnector.eth_get_account_nonce>`
- :meth:`GethHttpConnector.eth_get_block() <ethhelper.GethHttpConnector.eth_get_block>`
- :meth:`GethHttpConnector.eth_get_storage_at() <ethhelper.GethHttpConnector.eth_get_storage_at>`
- :meth:`GethHttpConnector.eth_send_raw_transaction() <ethhelper.GethHttpConnector.eth_send_raw_transaction>`
- :meth:`GethHttpConnector.eth_wait_for_transaction_receipt() <ethhelper.GethHttpConnector.eth_wait_for_transaction_receipt>`
- :meth:`GethHttpConnector.eth_get_transaction_receipt() <ethhelper.GethHttpConnector.eth_get_transaction_receipt>`
- :meth:`GethHttpConnector.eth_sign() <ethhelper.GethHttpConnector.eth_sign>`
- :meth:`GethHttpConnector.eth_filter() <ethhelper.GethHttpConnector.eth_filter>`

Net Namespace
-------------

- :meth:`GethHttpConnector.net_listening() <ethhelper.GethHttpConnector.net_listening>`
- :meth:`GethHttpConnector.net_peer_count() <ethhelper.GethHttpConnector.net_peer_count>`
- :meth:`GethHttpConnector.net_version() <ethhelper.GethHttpConnector.net_version>`

Txpool Namespace
----------------

- :meth:`GethHttpConnector.txpool_status() <ethhelper.GethHttpConnector.txpool_status>`
- :meth:`GethHttpConnector.txpool_inspect() <ethhelper.GethHttpConnector.txpool_inspect>`
- :meth:`GethHttpConnector.txpool_content() <ethhelper.GethHttpConnector.txpool_content>`
- :meth:`GethHttpConnector.txpool_content_from() <ethhelper.GethHttpConnector.txpool_content_from>`

Custom Namespace
----------------

- :meth:`GethHttpConnector.test_connection() <ethhelper.GethHttpConnector.test_connection>`
- :meth:`GethHttpConnector.get_logs() <ethhelper.GethHttpConnector.get_logs>`
- :meth:`GethHttpConnector.get_logs_by_blocks() <ethhelper.GethHttpConnector.get_logs_by_blocks>`
- :meth:`GethHttpConnector.get_height_after_ts() <ethhelper.GethHttpConnector.get_height_after_ts>`
- :meth:`GethHttpConnector.get_blocks_by_numbers() <ethhelper.GethHttpConnector.get_blocks_by_numbers>`

WS API
~~~~~~

ETHHelper implements an abstract class GethSubscriber to maintain a complete
Geth Websocket connection life cycle. Starting from the function, a
GethNewBlockSubscriber is exported to subscribe to new block messages on the
basis of the Websocket connection.

GethNewBlockSubscriber
----------------------

- :meth:`GethNewBlockSubscriber.on_block() <ethhelper.GethNewBlockSubscriber.on_block>`
- :meth:`GethNewBlockSubscriber.on_other() <ethhelper.GethNewBlockSubscriber.on_other>`

.. _Web3.py: https://github.com/ethereum/web3.py
.. _pydantic: https://github.com/pydantic/pydantic