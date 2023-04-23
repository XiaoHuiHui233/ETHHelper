.. _ethhelper_base:

ETHHelper API
=============

.. contents:: :local:

.. automodule:: ethhelper
.. currentmodule:: ethhelper

.. note::

    All interfaces in this repo rely on the asynchronous environment, so the
    asyncio environment is required when using the REPL for interactive coding.
    This can be done by running ``python -m asyncio`` directly on the command
    line or shell (instead of ``python``).

High-level API
~~~~~~~~~~~~~~

GethHttpConnector
-----------------

.. autoclass:: GethHttpConnector
    :members:
    :inherited-members:

GethNewBlockSubscriber
----------------------

.. autoclass:: GethNewBlockSubscriber
    :members:
    :inherited-members:

.. toctree::
    :maxdepth: 1
    :caption: Low-level API

    ethhelper.connectors.http
    ethhelper.connectors.ws
