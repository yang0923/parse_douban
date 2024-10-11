import re
import requests
from parsel import Selector
from loguru import logger
import utils.helpers as helpers
from concurrent.futures import ThreadPoolExecutor


class SpiderDouban:

    def __init__(self, DoubanId):
        self.DoubanId = DoubanId
        self.BASE_URL = f"https://movie.douban.com/subject/{DoubanId}/"
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        self.session = requests.Session()  # 创建一个会话对象
        self.session.headers.update(self.headers)  # 更新会话对象的请求头
        self.selector = None  # Selector 对象

    @logger.catch  # 使用装饰器捕获所有未处理的异常# 页面 HTML 内容
    def fetch_page(self):
        """ 获取页面 HTML 内容 """
        response = self.session.get(self.BASE_URL)
        response.raise_for_status()  # 如果响应状态码不是200，则抛出异常
        self.selector = Selector(text=response.text)  # 使用 Selector 解析 HTML
        logger.info(f"获取页面 HTML 内容成功: {self.BASE_URL}")
        return self.selector

    @logger.catch
    def parse_name(self):
        """
        解析电影名称
        Args:
            None:
        Returns: 
            dict<{name: str, name_en: str|None}> : 返回电影名称和英文名称
        """
        content = self.selector.css('meta[name="keywords"]::attr(content)').get()
        name = content.split(',')[0]
        nane_en = content.split(',')[1]
        if not helpers.contains_only_english(nane_en) or '影评' in nane_en:
            nane_en = None
        result_data = {"name": name, "name_en": nane_en}
        return result_data

    @logger.catch
    def parse_year(self):
        """ 解析电影年份 """
        year = self.selector.xpath('//*[@id="content"]/h1/span[@class="year"]/text()').get()
        if year:
            try:
                year = int(year.replace('(', '').replace(')', ''))
                return year
            except ValueError:
                ...
        return None

    @logger.catch
    def parse_score(self):
        """ 解析电影评分 """
        score = self.selector.css(".rating_num::text")
        if score:
            try:
                score = float(score.get())
                return score
            except ValueError:
                pass
        return None

    @logger.catch
    def parse_director(self):
        """ 解析电影导演  
        returns:
            list[str]: 返回电影导演列表
        """
        director = self.selector.css(
            'meta[property="video:director"]::attr(content)').getall()
        if director:
            return director
        return None

    @logger.catch
    def parse_actor(self):
        """ 解析电影演员
        returns:
            list[str]: 返回电影演员列表
        """
        actor = self.selector.css('meta[property="video:actor"]::attr(content)').getall()
        return actor if actor else None

    @logger.catch
    def parse_type(self):
        """ 解析电影类型标签 """
        type = self.selector.css('span[property="v:genre"]::text').getall()
        return type if type else None

    @logger.catch
    def parse_summary(self):
        """ 解析电影简介 """
        summary_elements = self.selector.css(
            'span.all.hidden *::text').getall()  # 获取 span 内所有子元素的文本

        if not summary_elements:
            summary_elements = self.selector.css('span[property="v:summary"] *::text').getall()  # 获取 span 内所有子元素的文本
        summary = ''.join(summary_elements)  # 将文本连接在一起
        # 使用正则表达式去除多余的空白字符（包括全角空格）
        summary = re.sub(r'\s+', ' ', summary)  # 将多个空格替换为单个空格

        return summary if summary else None

    @logger.catch
    def parse_image(self):
        """ 解析电影海报 """
        image_path = self.selector.css('meta[property="og:image"]::attr(content)').get()
        return image_path if image_path and 'tv_default_large' not in image_path  else None

    @logger.catch
    def parse_bg_image(self):
        """ 解析电影背景图片 """
        # 跳转 https://movie.douban.com/subject/{douban_id}/photos?type=S&start=0&sortby=size&size=a&subtype=a
        url = f"https://movie.douban.com/subject/{self.DoubanId}/photos?type=S&start=0&sortby=size&size=a&subtype=a"

        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()  # 如果响应状态码不是200，则抛出异常   
        selector = Selector(text=response.text)

        images = []
        # 获取所有图片项
        li_list = selector.css('ul.poster-col3.clearfix li')

        for li_item in li_list:
            cover = li_item.css('div.cover a img::attr(src)').get()
            prop = li_item.css('div.prop::text').get()
            if cover and prop:
                images.append({
                    "cover": cover.strip(),
                    "prop": prop.strip()
                })

        return images if images else None

    
    @logger.catch
    def parse_region(self):
        """ 解析电影地区 """

        info_div = self.selector.css("div#info").get()
        for line in info_div.split("<br>"):
            if "制片国家/地区:" in line:
                # 提取国家/地区信息并分割为列表
                regions = line.split("</span>")[-1].strip()
                return [region.strip() for region in regions.split("/") if region.strip()]
        return None

    @logger.catch
    def parse_language(self):
        """ 解析电影语言 """
        info_div = self.selector.css("div#info").get()
        for line in info_div.split("<br>"):
            if "语言:" in line:
                # 提取国家/地区信息并分割为列表
                regions = line.split("</span>")[-1].strip()
                return [region.strip() for region in regions.split("/") if region.strip()]
        return None

    @logger.catch
    def parse_alias(self):
        """ 解析又名 """
        info_div = self.selector.css("div#info").get()
        for line in info_div.split("<br>"):
            if "又名:" in line:
                # 提取国家/地区信息并分割为列表
                regions = line.split("</span>")[-1].strip()
                return [region.strip() for region in regions.split("/") if region.strip()]
        return None

    @logger.catch
    def parse_release_date(self):
        """ 解析电影上映日期 """
        release_dates  = self.selector.css("span[property='v:initialReleaseDate']::text").getall()
        # 去除空白字符并过滤掉空字符串
        release_dates = [date.strip() for date in release_dates if date.strip()]
        # 使用列表推导式提取日期和事件
        result_data = []
        for date in release_dates:
            match = re.match(r"(\d{4}-\d{2}-\d{2})(?:\s*\((.*?)\))?", date)
            if match:
                date_only = match.group(1)  # 提取日期
                event = match.group(2) or "Unknown Event"  # 提取事件或设置默认值
                result_data.append({"date": date_only, "event": event.strip()})
        return result_data if result_data else None  # 返回提取后的结果数据或 None

    @logger.catch
    def parse(self):
        """ 解析页面 """
        results = {"douban_id":self.DoubanId}  # 创建一个字典来存储所有解析结果
        with ThreadPoolExecutor() as executor: # 创建一个线程池执行器, 用于并发执行解析任务, 提高效率, 减少等待时间
            futures = {
                executor.submit(self.parse_name): "name",
                executor.submit(self.parse_year): "year",
                executor.submit(self.parse_score): "score",
                executor.submit(self.parse_director): "director",
                executor.submit(self.parse_actor): "actor",
                executor.submit(self.parse_type): "type",
                executor.submit(self.parse_summary): "summary",
                executor.submit(self.parse_release_date): "release_date",
                executor.submit(self.parse_image): "image",
                executor.submit(self.parse_region): "region",
                executor.submit(self.parse_language): "language",
                executor.submit(self.parse_alias): "alias",
                executor.submit(self.parse_bg_image):"bg_image"
            }
            for future in futures:
                try:
                    result = future.result()  # 获取任务结果
                    results[futures[future]] = result  # 存储结果
                    # logger.info(f"{futures[future]}: {result}") # 打印结果
                except Exception as e:
                    logger.error(f"解析 {futures[future]} 时发生错误: {e}") # 打印错误信息
        
        logger.info(f"页面解析完成......")
        return results if results else None  # 返回解析后的结果数据或 None
        

    @logger.catch
    def run(self):
        """ 运行爬虫 """
        self.fetch_page() # 获取页面内容
        vod_data =  self.parse()  # 解析页面内容
        return vod_data if vod_data else None  # 返回解析后的结果数据或 None
