from config import settings  # 确保在其他代码之前导入 settings
import os
import argparse
from loguru import logger
from spiders.Douban import SpiderDouban
from concurrent.futures import ThreadPoolExecutor

def run_douban_spider(DoubanIds: list[int], threads: int = 4):
    """ 多页面爬取豆瓣电影数据，使用多线程爬取
        :param DoubanIds: 电影的豆瓣 ID 列表
        :param threads: 线程数, 默认为4
        :return:
    """
    with ThreadPoolExecutor(max_workers=threads) as executor:  # 使用指定数量的线程
        results = list(executor.map(run_douban_spider_by_id, DoubanIds))  # 提交任务

    logger.info(f"results: {results}")
    # logger.info(f"豆瓣电影数据已保存到 {os.path.join(settings.BASE_DIR, 'datas')}")

def run_douban_spider_by_id(DoubanId:int):
    """ 单页面爬取豆瓣电影数据
        :param DoubanId : 电影的豆瓣 ID
        :return:
    """
    try:
        spider = SpiderDouban(DoubanId=DoubanId)
        # 开始解析
        vod_data = spider.run()
        logger.info(f"影片名称: {vod_data.get("name").get('name')} 豆瓣ID: {DoubanId}, 数据解析完成")
        return vod_data
    except Exception as e:
        logger.error(f"处理豆瓣ID {DoubanId} 时发生错误: {e}")
        return None

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="解析输入参数以获取豆瓣电影数据。")

    # 添加命令行参数以及简写形式
    parser.add_argument('-id','--DoubanId',type=str,required=True,help="电影的豆瓣 ID。")

    # 解析命令行参数
    args = parser.parse_args()
    # 检查输入的ID是否为空
    if not args.DoubanId: 
        logger.error("请输入电影的豆瓣 ID。")
        exit(1)

    # 将输入的字符串按逗号分隔成列表
    douban_ids = args.DoubanId.split(',')
    
    if not douban_ids:
        logger.error("请输入有效的豆瓣 ID。")
        exit(1)

    # 确保函数参数名和变量名一致
    run_douban_spider(DoubanIds=douban_ids)
    # run_douban_spider_by_id(DoubanId=douban_ids[0])

if __name__ == '__main__':
    
    main()


