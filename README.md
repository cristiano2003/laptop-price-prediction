---
title: laptop-price-prediction
app_file: app.py
sdk: gradio
sdk_version: 4.12.0
---

## Install Dependencies

```bash
pip install -e .
```

## Crawling Process

All the code for crawling process are located in [src/crawler](src/crawler) directory. In details:

- [base.py](src/crawler/base.py): Base class for all crawlers

- [anphat.py](src/crawler/anphat.py): Crawler for [An Phát](https://www.anphatpc.com.vn/)

- [tgdd.py](src/crawler/tgdd.py): Crawler for [Thegioididong](https://www.thegioididong.com/)

- [fpt.py](src/crawler/fpt.py): Crawler for [FPT Shop](https://fptshop.com.vn/)

In each crawler, we have 2 main functions:

- `get_all_product_links()`: Get all product links from the website

- `crawl_raw_htmls()`: Get product info from a product link. The htmls will be saved in `data/anphat/raw_htmls` or `data/tgdd/raw_htmls` or `data/fpt/raw_htmls` directory.

- `parse_specs()`: Parse the raw htmls and save the data in form of json

To run one of these functions, uncomment the corresponding line in each crawler file and run the file.

## Regex for parsing specs

Show more details in [notebook/regex.ipynb](notebook/regex.ipynb)

## EDA and Train Model

Show EDA in [notebook/EDA.ipynb](notebook/EDA.ipynb)

Show Model in [notebook/train.ipynb](notebook/train.ipynb)

## Demo

```bash
python demo/app.py
```

## Workload of each member

- Duong Minh Quan (20210710):

  - Crawl data from An Phát, FPT Shop, Thegioididong in [src/crawler](src/crawler) directory (100%)

- Nguyen Huu Nam (20210630):

  - Preprocessing to extract feature from raw data(html) (100%)

- Vo Dinh Dat (20214890):

  - Perform EDA and Feature Engineering (50%)
  - Build Model and Evaluation Metrics (50%)

- Pham Quang Nguyen Hoang:

  - Build Model and Evaluation Metrics (50%)

- Nguyen Trung Truc:
  - Perform EDA and Feature Engineering (50%)
