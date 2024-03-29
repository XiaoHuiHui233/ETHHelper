# ETHHelper

[![Build Status](https://img.shields.io/github/actions/workflow/status/XiaoHuiHui233/ETHHelper/publish.yml)](https://github.com/XiaoHuiHui233/ETHHelper/actions)
[![Documentation Status](https://readthedocs.org/projects/ethhelper/badge/?version=latest)](https://ethhelper.readthedocs.io/en/latest/?badge=latest)
![Python Version](https://img.shields.io/pypi/pyversions/ethhelper)
![Wheel Status](https://img.shields.io/pypi/wheel/ethhelper)
[![Latest Version](https://img.shields.io/github/v/release/XiaoHuiHui233/ETHHelper)](https://github.com/XiaoHuiHui233/ETHHelper/releases)
[![License](https://img.shields.io/github/license/XiaoHuiHui233/ETHHelper)](https://github.com/XiaoHuiHui233/ETHHelper/blob/main/LICENSE)

基于httpx、websockets以及web3.py的异步Geth节点连接封装。基于pydantic的Geth节点和以太坊类型扩展。

快速开始见[此](https://ethhelper.readthedocs.io/en/latest/quickstart.html)。

中文 | [English](README.md)

## 用法

### pypi

您可以使用pypi直接安装本包：

```bash
pip install ethhelper
```

### git

项目使用poetry进行管理，如果您喜欢基于git的安装，可以使用poetry直接通过git添加对本项目构建包的引用。

指令如下：

```bash
poetry add git+ssh://git@github.com:XiaoHuiHui233/ETHHelper.git
```

## 构建

你可以使用poetry的工具生成项目（纯Python）的构建。

指令如下：

```bash
poetry build
```

## 作者和版权

ETHHelper由[XiaoHuiHui233](https://github.com/XiaoHuiHui233/)开发，使用Apache2.0开源协议。
