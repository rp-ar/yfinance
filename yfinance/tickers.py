#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Yahoo! Finance market data downloader (+fix for Pandas Datareader)
# https://github.com/ranaroussi/yfinance
#
# Copyright 2017-2019 Ran Aroussi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function

import re
import pandas as pd

from . import Ticker, multi
from collections import namedtuple as _namedtuple


def genTickers(tickers):
    tickers = tickers if isinstance(
        tickers, list) else tickers.replace(',', ' ').split()
    tickers = [ticker.upper() for ticker in tickers]
    ticker_objects = {}

    for ticker in tickers:
        ticker_objects[ticker] = Ticker(ticker)
    return _namedtuple("Tickers", ticker_objects.keys()
                       )(*ticker_objects.values())


class Tickers():

    def __repr__(self):
        return 'yfinance.Tickers object <%s>' % ",".join(self.symbols)

    def __init__(self, tickers):
        tickers = tickers if isinstance(
            tickers, list) else tickers.replace(',', ' ').split()
        self.symbols = [ticker.upper() for ticker in tickers]
        ticker_objects = {}

        for ticker in self.symbols:
            ticker_objects[ticker] = Ticker(ticker)

        self.tickers = _namedtuple(
            "Tickers", [self.ticker_to_attr(x) for x in ticker_objects.keys()], rename=True
        )(*ticker_objects.values())

    @staticmethod
    def ticker_to_attr(ticker: str):
        return re.sub("[^a-zA-Z0-9_]+", "_", re.sub("(^[0-9])", "YFIN__\\1", ticker.replace('.', '_').replace('-', '_')))

    def history(self, period="1mo", interval="1d",
                start=None, end=None, prepost=False,
                actions=True, auto_adjust=True, proxy=None,
                threads=True, group_by='column', progress=True,
                **kwargs):

        return self.download(
                period, interval,
                start, end, prepost,
                actions, auto_adjust, proxy,
                threads, group_by, progress,
                **kwargs)

    def download(self, period="1mo", interval="1d",
                 start=None, end=None, prepost=False,
                 actions=True, auto_adjust=True, proxy=None,
                 threads=True, group_by='column', progress=True,
                 **kwargs):

        data = multi.download(self.symbols,
                              start=start, end=end,
                              actions=actions,
                              auto_adjust=auto_adjust,
                              period=period,
                              interval=interval,
                              prepost=prepost,
                              proxy=proxy,
                              group_by='ticker',
                              threads=threads,
                              progress=progress,
                              **kwargs)

        for symbol in self.symbols:
            if symbol not in data:
                data.columns = pd.MultiIndex.from_product([[symbol], data.columns])
            try:
                getattr(self.tickers, self.ticker_to_attr(symbol))._history = data[symbol]
            except Exception:
                idx = self.symbols.index(symbol)
                self.tickers[idx]._history = data[symbol]

        if group_by == 'column':
            data.columns = data.columns.swaplevel(0, 1)
            data.sort_index(level=0, axis=1, inplace=True)

        return data
