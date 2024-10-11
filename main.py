from config import settings  # 确保在其他代码之前导入 settings
import os
import argparse
from loguru import logger
from spiders.Douban import SpiderDouban
from multiprocessing import Pool
import utils.helpers as helpers
from utils.translate import translator

def run_douban_spider(DoubanIds: list[int],processes:int=4):
    """ 多页面爬取豆瓣电影数据,使用多线程爬取
        :param DoubanIds: 电影的豆瓣 ID 列表
        :param processes: 进程数,默认为4
        :return:
    """
    with Pool(processes=processes) as pool:  # 使用4个进程
        pool.map(run_douban_spider_by_id, DoubanIds)

    logger.info(f"豆瓣电影数据已保存到 {os.path.join(settings.BASE_DIR,'datas')}")

def run_douban_spider_by_id(DoubanId:int):
    """ 单页面爬取豆瓣电影数据
        :param DoubanId : 电影的豆瓣 ID
        :return:
    """
    try:
        spider = SpiderDouban(DoubanId=DoubanId)
        # 开始解析
        vod_data = spider.run()

        if vod_data:
            summary = vod_data["summary"]
            vod_data["summary_tw"] = translator.run(text=summary,from_lang="zh", to_lang="zh-tw")
        helpers.save_json_to_file(vod_data, os.path.join(settings.BASE_DIR,"datas", f"{vod_data['name']['name']}-{DoubanId}.json"))
        logger.info(f"电影数据已保存到 {os.path.join(settings.BASE_DIR,'datas', f'{vod_data["name"]["name"]}-{DoubanId}.json')}")

    except Exception as e:
        logger.error(f"处理豆瓣ID {DoubanId} 时发生错误: {e}")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="解析输入参数以获取豆瓣电影数据。")

    # 创建互斥组
    group = parser.add_mutually_exclusive_group(required=True)

    # 添加命令行参数以及简写形式
    group.add_argument('-id','--DoubanId',type=int,help="电影的豆瓣 ID。")
    # 添加命令行参数以及简写形式
    group.add_argument('-ids','--DoubanIds',type=int,nargs='+',help="多个电影的豆瓣 ID。例: ")

    # # 解析命令行参数
    args = parser.parse_args()
    if args.DoubanId:
        run_douban_spider_by_id(DoubanId=args.DoubanId)

    if args.DoubanIds:
        run_douban_spider(DoubanIds=args.DoubanIds)


if __name__ == '__main__':
    
    main()


