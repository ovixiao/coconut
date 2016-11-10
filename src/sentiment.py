#!/usr/bin/env python
# -*- coding: utf-8 -*-
# xiaorixin@2016-11-09T17:58:13
"""
通过调用 HanLP 的句法分析，来获取情感倾向的对象以及情感倾向
"""
import sys
import gzip
from pyhanlp import HanLP
from collections import defaultdict
from itertools import product

# 全局对象
hanlp = HanLP()


class SAS(object):
    """Sentiment Analysis System
    """

    # 大连理工大学 -> ICTPOS 3.0
    POS_MAP = {
        'noun': 'n',
        'verb': 'v',
        'adj': 'a',
        'adv': 'd',
        'nw': 'al',  # 网络用语
        'idiom': 'al',
        'prep': 'p',
    }

    # 否定词
    NOT_DICT = set(['不', '没', '无', '非', '莫', '弗', '毋',
                    '勿', '未', '否', '别', '無', '休'])

    def __init__(self, sentiment_dict_path, degree_dict_path):
        self.sentiment_dict = self.load_sentiment_dict(sentiment_dict_path)
        self.degree_dict = self.load_degree_dict(degree_dict_path)

    def load_degree_dict(self, dict_path):
        """读取程度副词词典

        Args:
            dict_path: 程度副词词典路径. 格式为 word\tdegree
                       所有的词可以分为6个级别，分别对应极其, 很, 较, 稍, 欠, 超

        Returns:
            返回 dict = {word: degree}
        """
        degree_dict = {}
        with gzip.open(dict_path) as f:
            for line in f:
                line = line.strip()
                word, degree = line.split('\t')
                degree = float(degree)
                degree_dict[word] = degree
        return degree_dict

    def load_sentiment_dict(self, dict_path):
        """读取情感词词典

        Args:
            dict_path: 情感词词典路径. 格式请看 README.md

        Returns:
            返回 dict = {(word, postag): 极性}
        """
        sentiment_dict = {}
        with gzip.open(dict_path) as f:
            for index, line in enumerate(f):
                if index == 0:  # title
                    continue

                items = line.split('\t')
                word = items[0]
                pos = items[1]
                intensity = items[5]
                polar = items[6]
                # 将词性转为 ICTPOS 词性体系
                pos = self.__class__.POS_MAP[pos]
                intensity = int(intensity)
                polar = int(polar)

                # 转换情感倾向的表现形式, 负数为消极, 0 为中性, 正数为积极
                # 数值绝对值大小表示极性的强度
                value = None
                if polar == 0:  # neutral
                    value = 0
                elif polar == 1:  # positive
                    value = intensity
                elif polar == 2:  # negtive
                    value = -1 * intensity
                else:  # invalid
                    continue

                key = (word, pos)
                sentiment_dict[key] = value

        return sentiment_dict

    def invert_dependency(self, words):
        """倒排依赖关系. 依赖 -> 被依赖. 方便依据情感词查找

        Args:
            words: 包含依赖关系的词单元

        Return:
            返回一个倒排后的依赖关系词典
            dict = {(word, postag): [word_id_1, word_id_2, ...]}
        """
        invert_dependency_dict = defaultdict(list)
        for word in words.values():
            headid = word.headid
            if headid == 0:  # root 节点, 不依赖其他
                continue

            head_key = (words[headid].lemma, words[headid].cpostag)
            invert_dependency_dict[head_key].append(word.id)

        return invert_dependency_dict

    def parse(self, text):
        """文本处理的入口函数, 分析情感关系.
        可以分析出情感倾向的对象, 情感极性和程度

        Args:
            text: UTF-8 编码的待分析文本

        Returns:
            返回分析出的案例
        """
        words = hanlp.parse_dependency(text)
        #for word in words.values():
        #    print ' >  ', word.id, word.lemma, word.cpostag, word.headid, word.deprel
        invert_dependency_dict = self.invert_dependency(words)
        for word in words.values():
            key = (word.lemma, word.cpostag)
            try:
                polar = self.sentiment_dict[key]
            except KeyError:
                continue

            #print '   #', word.lemma, word.cpostag, polar
            ori_polar = polar
            dependency_list = invert_dependency_dict.get(key, [])
            zhu_wei_words = []
            zhuang_zhong_words = []
            for _id in dependency_list:
                w = words[_id]
                key = (w.lemma, w.cpostag)
                if w.deprel == '主谓关系':
                    zhu_wei_words.append(key)
                elif w.deprel == '状中结构' and w.cpostag == 'd':
                    if w.lemma in self.degree_dict:
                        degree = self.degree_dict[w.lemma]
                        polar = polar + degree if polar > 0 else polar - degree
                    elif w.lemma in self.__class__.NOT_DICT:
                        polar *= -1
                    zhuang_zhong_words.append(key)

            if len(zhu_wei_words) <= 0:  # 不存在主语, 添加一个未知主语
                zhu_wei_words.append(('N', 'N'))

            for zw_lemma, zw_cpostag in zhu_wei_words:
                if polar != 0:
                    print '{}\t{}|{}\t{}|{}|{}\t{}'.format(
                        polar,
                        zw_lemma, zw_cpostag,
                        word.lemma, word.cpostag, ori_polar,
                        ' '.join(map(lambda x: '{}|{}'.format(*x), zhuang_zhong_words))
                    )


def _test():
    sas = SAS(sys.argv[1], sys.argv[2])
    while 1:
        text = raw_input('Please input your text for parsing:')
        sas.parse(text)


if __name__ == '__main__':
    _test()
