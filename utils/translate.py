import re
from translate import Translator
from loguru import logger  # 用于日志处理

class MyTranslator:
    def __init__(self, max_query_length=450):
        """
        初始化翻译器
        
        参数:
        max_query_length (int): 最大字符长度限制，默认为 450
        """
        self.MAX_QUERY_LENGTH = max_query_length
        # 编译正则表达式用于句子分割，提升性能
        self.sentence_endings = re.compile(r'([。！？?.!])')

    @logger.catch
    def split_text(self, text: str):
        """
        根据句子分割长文本并尽量合并相邻句子以减少分片
        
        参数:
        text (str): 需要分割的长文本

        返回:
        list: 分割后的句子列表
        """
        parts = self.sentence_endings.split(text)
        sentences = [''.join(parts[i:i+2]).strip() for i in range(0, len(parts)-1, 2)]
        
        if len(parts) % 2 != 0:
            sentences.append(parts[-1].strip())

        merged_sentences = []
        current_batch = ""

        for sentence in sentences:
            # 检查当前批次和即将添加的句子长度
            if len(current_batch) + len(sentence) + 1 > self.MAX_QUERY_LENGTH:  # +1 为空格
                if current_batch:  # 如果当前批次不为空，将其添加到合并结果中
                    merged_sentences.append(current_batch.strip())
                current_batch = sentence  # 开始新的批次
            else:
                current_batch += " " + sentence if current_batch else sentence
                
        # 添加最后一个批次
        if current_batch:
            merged_sentences.append(current_batch.strip())

        return merged_sentences

    @logger.catch
    def batch_translate(self, sentences, from_lang, to_lang):
        """
        对分割后的句子进行批量翻译，并合并翻译结果
        
        参数:
        sentences (list): 分割后的句子列表
        from_lang (str): 源语言
        to_lang (str): 目标语言

        返回:
        str: 翻译后的完整文本
        """
        translated_text = []
        batch = ""

        for sentence in sentences:
            if len(batch) + len(sentence) > self.MAX_QUERY_LENGTH:
                # 执行翻译并清空批次
                translated = self.perform_translation(batch, from_lang, to_lang)
                if translated:
                    translated_text.append(translated)
                batch = sentence
            else:
                batch += " " + sentence if batch else sentence

        if batch:
            translated = self.perform_translation(batch, from_lang, to_lang)
            if translated:
                translated_text.append(translated)

        if translated_text:
            return ' '.join(translated_text)
        else:
            return None

    @logger.catch
    def perform_translation(self, text: str, from_lang: str, to_lang: str):
        """
        执行单次文本翻译
        
        参数:
        text (str): 需要翻译的文本
        from_lang (str): 源语言
        to_lang (str): 目标语言

        返回:
        str: 翻译后的文本
        """
        try:
            translator = Translator(to_lang=to_lang, from_lang=from_lang)
            translation = translator.translate(text)

            # 判断 translation 是不是全是大写英文字符?? 出符号外
            if translation.isupper() and any(c.isalpha() for c in translation):
                return None  # 如果翻译结果全是大写英文字符，则认为翻译失败，返回 None
            
            return translation
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return None  # 出现错误时返回原文

    @logger.catch
    def run(self, text: str, from_lang: str = "zh", to_lang: str = "en"):
        """
        翻译入口方法，根据文本长度决定是否进行分句处理
        
        参数:
        text (str): 需要翻译的文本
        from_lang (str): 源语言，默认为中文 "zh"
        to_lang (str): 目标语言，默认为英文 "en"

        返回:
        str: 翻译后的文本
        """
        if not isinstance(text, str):
            raise ValueError("输入的文本必须是字符串")

        if len(text) > self.MAX_QUERY_LENGTH:
            sentences = self.split_text(text)
            return self.batch_translate(sentences, from_lang, to_lang)
        else:
            return self.perform_translation(text, from_lang, to_lang)


# 初始化翻译器实例
translator = MyTranslator()


