# PARSE_DOUBAN

## 简介

这是一个爬取豆瓣电影影片数据的项目，包括电影名称、导演、演员、评分、简介等。
本项目不做数据存储，只做数据爬取和展示。

## 功能

-   爬取豆瓣电影影片数据
-   展示爬取的数据

## 环境要求

-   Python 3.12+

## 使用方法

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 运行脚本

-   单影片数据爬取

```bash
python main.py -id 豆瓣ID
```

例如：`python main.py -id 35650754`

-   多影片数据爬取

```bash
python main.py -ids 豆瓣ID1 豆瓣ID2 豆瓣ID3 ...
```

例如：`python main.py -ids 35650754 1292052 1291546`

## 注意事项

-   请遵守豆瓣的使用协议，不要滥用爬虫。
-   本项目仅供学习和研究使用，请勿用于商业用途。
