.. ETHHelper documentation master file, created by
    sphinx-quickstart on Thu Mar 16 16:21:25 2023.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Welcome to ETHHelper's documentation!
=====================================

Introduction
============

ETHHelper is a Python library for asynchronously interacting with Ethereum Geth
node.

It wraps some asynchronous implementations of the HTTP interface of some
namespaces of `Geth`_ nodes.

It forwards the asynchronous Ethereum JSON-RPC HTTP interface implemented by
`Web3.py`_.

It implements websockets subscription of asynchronous `Geth`_ nodes and
encapsulates basic block subscription capabilities.

It provides more Ethereum types and uses `pydantic`_ for automatic
(de)serialization.

Getting Started
---------------

Your next steps depend on where you're standing:

- Unfamiliar with Ethereum? → `ethereum.org`_
- Looking for Ethereum Python tutorials? → `ethereum.org/python`_
- Ready to code? → :ref:`quickstart`
- Read the source? → `Github`_

Table of Contents
-----------------
.. toctree::
    :maxdepth: 1
    :caption: Intro

    quickstart
    overview
    releases

.. toctree::
    :maxdepth: 1
    :caption: API

    ethhelper.main
    ethhelper.types
    ethhelper.connectors.http
    ethhelper.connectors.ws

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _Geth: https://github.com/ethereum/go-ethereum
.. _Web3.py: https://github.com/ethereum/web3.py
.. _pydantic: https://github.com/pydantic/pydantic
.. _ethereum.org: https://ethereum.org/what-is-ethereum/
.. _ethereum.org/python: https://ethereum.org/python/
.. _Github: https://github.com/XiaoHuiHui233/ETHHelper