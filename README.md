# ETHHelper

[![license](https://img.shields.io/github/license/XiaoHuiHui233/ETHHelper)](https://github.com/XiaoHuiHui233/ETHHelper/blob/main/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/ethhelper/badge/?version=latest)](https://ethhelper.readthedocs.io/en/latest/?badge=latest)

Asynchronous Geth node connection encapsulation based on httpx, websockets and web3.py. Geth node and Ethereum type extension based on pydantic.

Quickstart see [this](https://ethhelper.readthedocs.io/en/latest/quickstart.html).

[中文](docs/README_cn.md) | English

## Usage

### pypi

If you prefer to use pypi to install this package, you can just run the following command:

```bash
pip install ethhelper
```

### git

The project is managed by poetry. If you prefer to use git to install this package, you can use poetry to directly add a reference to the project's build package through git.

The command is as follow:

```bash
poetry add git+ssh://git@github.com:XiaoHuiHui233/ETHHelper.git
```

## Build

You can use poetry's tools to generate a build of this project (pure Python).

The command is as follow:

```bash
poetry build
```

## Author and License

ETHHelper was written by [XiaoHuiHui233](https://github.com/XiaoHuiHui233/), licensed under the Apache 2.0.
