Release Notes
=============

v0.3.4 (2023-04-24)
-------------------

Bugfixes
~~~~~~~~

- Fixed typo in README

v0.3.3 (2023-04-24)
-------------------

Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Added Build Status to README
- Added Python Version to README
- Added Wheel Status to README
- Added Latest Version to README

v0.3.2 (2023-04-24)
-------------------

Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- Added auto publish to github workflow

Release Notes
=============

v0.3.1 (2023-04-24)
-------------------

Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Added pypi install guide to README
- Added Documentation Status to README

Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- Added pypi release

v0.3.0 (2023-04-23)
-------------------

Bugfixes
~~~~~~~~

- Fixed typo ``ethhelper.connnectors`` to ``ethhelper.connectors``

Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Added full read-the-docs style documentation

v0.2.2 (2023-03-27)
-------------------

Breaking changes
~~~~~~~~~~~~~~~~

- Used timestamp instead of ``datetime`` for time calculation

v0.2.1 (2023-03-27)
-------------------

Features
~~~~~~~~

- Added ability to aggregate requests
- Added ability to get a series of consecutive blocks

Internal Changes
~~~~~~~~~~~~~~~~

- Migrated the direct query interface of logs from ``eth`` to ``custom``

v0.2.0 (2023-03-22)
-------------------

Breaking changes
~~~~~~~~~~~~~~~~

- Removed properties in ``SyncStatus`` that Geth has determined not to provide

Bugfixes
~~~~~~~~

- Fixed the bug that ``topics`` in ``FilterParams`` provided to web3 use hex
  ``str`` instead of ``bytes``
- Fixed the bug that the type of ``block_hash`` in ``FilterParams`` should be
  ``Hash32`` instead of ``HexBytes``
- Fixed typo in name of WS interface

Features
~~~~~~~~

- Added judgment on conflict between ``block_hash`` and ``from_block`` /
  ``to_block`` in ``FilterParams``
- Added ``GethCustomHttp`` to provide some additional common capability
  interfaces
- Added waiting for the node to synchronize to WS, now the node will not
  push the new block to be synchronized when the node is synchronizing

v0.1.18 (2023-03-16)
--------------------

Internal Changes
~~~~~~~~~~~~~~~~

- Updated ``web3`` to 6.0.0

v0.1.17 (2023-03-11)
--------------------

Internal Changes
~~~~~~~~~~~~~~~~

- Updated ``eth-typing`` to 3.3.0
- Updated ``pydantic`` to 1.10.6
- Updated ``mypy`` to 1.1.1
- Updated ``pytest`` to 7.2.2

v0.1.16 (2023-03-02)
--------------------

Bugfixes
~~~~~~~~

- Fixed missing type configuration

Features
~~~~~~~~

- Added conversion of GWei and ETH to Wei
- Made ``FilterParam`` mutable

v0.1.15 (2023-03-02)
--------------------

Internal Changes
~~~~~~~~~~~~~~~~

- Updated code style
- Added more config items for linting tools
- Used ``black`` instead of ``yapf``
- Used ``ruff`` instead of ``flake8``

v0.1.14 (2023-03-01)
--------------------

Breaking changes
~~~~~~~~~~~~~~~~

- Exported all types and tools

Internal Changes
~~~~~~~~~~~~~~~~

- Converted multi-level relative imports to absolute imports
- Standardized the format of ``isort``

v0.1.13 (2023-03-01)
--------------------

Features
~~~~~~~~

- Implemented full HTTP interfaces for the ``eth`` namespace (100%)

Internal Changes
~~~~~~~~~~~~~~~~

- Updated ``orjson`` from 3.8.6 to 3.8.7

v0.1.12 (2023-02-28)
--------------------

Features
~~~~~~~~

- Exposed the asynchronous task of websocket

v0.1.11 (2023-02-27)
--------------------

Features
~~~~~~~~

- Added comparison and hash functions for common standard types

v0.1.10 (2023-02-27)
--------------------

Features
~~~~~~~~

- Implemented more HTTP interfaces for the ``eth`` namespace (80%)
- Modified test cases to cover more information
- Added more test cases

Internal Changes
~~~~~~~~~~~~~~~~

- Updated ``web3`` to 6.0.0b11

v0.1.9 (2023-02-24)
-------------------

Features
~~~~~~~~

- Made ``TxParams`` mutable

v0.1.8 (2023-02-24)
-------------------

Breaking changes
~~~~~~~~~~~~~~~~

- Changed all host and port to url

v0.1.7
------

* Added ``__str__`` for ``HexBytes`` and ``IntStr``

v0.1.6
------

* Allowed ``HexBytes`` and ``IntStr`` be inited by duper

v0.1.5
------

* Removed log utils
* Changed the way to get logger
* Made all test infomation show in logs
* Fixed a bug when websocket is close the task is not safely closed

v0.1.4
------

* Added Websocket new block subscribe

v0.1.3
------

* Added ``py.typed`` to export type infomation and support PEP561

v0.1.2
------

* Modified the link in ``README``
* Added ``LICENSE``

v0.1.1
------

* Added auto release using github workflow
* Modified the project description

v0.1.0
------

* First commit
* Implemented the HTTP interfaces of the ``txpool`` and ``net`` namespaces of
  Geth node
* Partially implements the HTTP interface of the ``eth`` namespace (50%)
