# -*- coding: utf-8 -*-
import codecs

from typing import Dict
from typing import List

import requests

from bs4 import BeautifulSoup

from batch.batch import SimpleJob
from batch.batch import Converter
from batch.batch import Task

from batch.batch import BatchError


class Stock:

    def __init__(self, name: str):
        self._name = name
        self._data = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def data(self) -> Dict:
        return self._data

    @data.setter
    def data(self, data: Dict):
        self._data = data


class ZozoItemFetchTask(Task[str, str]):

    def __init__(self):
        pass

    def execute(self, param: str) -> str:
        response = requests.get(param)
        response.encoding = response.apparent_encoding
        return response.text


class HtmlToStockConverter(Converter[str, Stock]):

    def convert(self, response: str) -> Stock:
        soup = BeautifulSoup(response)
        stock = Stock(self._get_item_name(soup))
        stock.data = self._get_item_stock_data(soup)

        return stock

    def _get_item_name(self, soup: BeautifulSoup) -> str:
        item_intro = soup.find(id='item-intro')
        return item_intro.find_all('h1')[0].text

    def _get_item_stock_data(self, soup: BeautifulSoup) -> dict:
        blockMain = soup.find('div', class_='blockMain')
        clearfixs = blockMain.find_all('dl', class_='clearfix')

        data = {}
        for clearfix in clearfixs:
            dt = clearfix.find_all('dt')[0]
            color = dt.find('span', class_='txt').text
            size_data = {}

            lis = clearfix.find_all('li')
            for li in lis:
                size = li['data-size']
                stock = li.find('div', class_='stock').find_all('span')[1].text
                size_data[size] = stock

            data[color] = size_data

        return data


class ItemStockConfirmJob(SimpleJob[List[str], List[Stock]]):

    def __init__(self, parameters: List[str], task: ZozoItemFetchTask, converter: HtmlToStockConverter):
        super().__init__('ItemStockConfirmJob', parameters, task, converter)


class UrlReader:

    def __init__(self, file_name: str):
        self._file_name = file_name

    def load(self):
        with codecs.open(self._file_name, 'r', 'utf-8') as f:
            return [row.strip() for row in f]


class StockWriter:

    def __init__(self, file_name: str):
        self._file_name = file_name

    def write(self, stocks: List[Stock]):
        with codecs.open(self._file_name, 'w', 'utf-8') as f:
            for stock in stocks:
                f.write(stock.name)
                f.write('\n')
                for color, d in stock.data.items():
                    f.write(color)
                    f.write('\n')
                    for size, exists in d.items():
                        f.write('{}, {}\n'.format(size, exists))
                f.write('\n')


def main():
    reader = UrlReader('items.txt')
    urls = reader.load()
    batch = ItemStockConfirmJob(urls, ZozoItemFetchTask(), HtmlToStockConverter())
    stocks = batch.run()
    writer = StockWriter('stocks.txt')
    writer.write(stocks)


if __name__ == '__main__':
    main()