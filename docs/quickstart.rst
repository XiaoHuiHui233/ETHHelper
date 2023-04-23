.. _quickstart:

Quickstart
==========

.. contents:: :local:

.. NOTE:: All code starting with a ``$`` is meant to run on your terminal.
    All code starting with a ``>>>`` is meant to run in a python interpreter,
    like `ipython <https://pypi.org/project/ipython/>`_.

Installation
------------

ETHHelper can be installed using ``pip`` as follows:

.. code-block:: shell

    $ pip install ethhelper

Also, you can install with `poetry`_ as follows:

.. code-block:: shell

    $ poetry add git+ssh://git@github.com:XiaoHuiHui233/ETHHelper.git

Using ETHHelper
---------------

Geth HTTP Connector
*******************

Geth HTTP Connector is an encapsulation of all HTTP interfaces based on
Ethereum clients supported by this repo. You need to provide this connector
with a link to the Geth node's HTTP service. Of course, links to third-party
node services such as `Infura`_ are also acceptable, but some interfaces may
not be supported.

.. code-block:: python

    >>> from ethhelper import GethHttpConnector
    >>> connector = GethHttpConnector("http://localhost:8545/")
    >>> await connector.test_connection()
    True

.. note::

    All interfaces in this repo rely on the asynchronous environment, so the
    asyncio environment is required when using the REPL for interactive coding.
    This can be done by running ``python -m asyncio`` directly on the command
    line or shell (instead of ``python``).

For the HTTP interfaces of the node supported by Geth HTTP Connector, see
:class:`~ethhelper.GethHttpConnector` in the API docs.

Geth New Block Subscriber
*************************

Geth New Block Subscriber is an encapsulation of the websocket interface of
Geth nodes. It provides basic new block subscription capabilities. Whenever
the node finds that a new block is generated on the chain, it will get the
data of this block and call the callback function. It also supports the use of
third-party node services such as `Infura`_. It's an abstract class, users
need to inherit this class and implement the callback function
:meth:`~ethhelper.GethNewBlockSubscriber.on_block` to use it normally.

You can see an example of this feature
`here <https://github.com/XiaoHuiHui233/ETHHelper/blob/main/tests/connectors/
ws/test_block.py>`_.

.. _poetry: https://python-poetry.org/
.. _Infura: https://www.infura.io/