#!/usr/bin/env python
# -*- coding: utf-8 -*-
# xiaorixin@2016-11-04T22:08:38
"""
使用 Py4j 调用 Java 项目 HanLP

请先安装py4j
"""
import os
import subprocess
import time
import py4j.java_gateway
from collections import namedtuple


# 依赖关系中的词单元
CoNLLWord = namedtuple('CoNLLWord', [
    'id',  # 词的 ID, 从 1 开始
    'lemma',  # 当前词语（或标点）的原型或词干，此处可理解为词条
    'cpostag',  # 粗粒度的词性
    'postag',  # 词性
    'headid',  # 当前词的中心词 (可理解为依赖的词) ID
    'deprel',  # 当前词语与中心词的依存关系, 例如: 主谓关系
])


class HanLP(object):

    def __init__(self, hanlp_jar_path=None, py4j_jar_path=None):
        # 获取文件的绝对路径
        abs_cwd = os.path.split(os.path.abspath(__file__))[0]
        self.src_path = os.path.join(abs_cwd, 'src')
        if hanlp_jar_path is None:
            self.hanlp_jar_path = os.path.join(abs_cwd, 'lib',
                                               'hanlp-1.3.1.jar')
        else:
            self.hanlp_jar_path = hanlp_jar_path
        if py4j_jar_path is None:
            self.py4j_jar_path = '/usr/local/share/py4j/py4j0.10.4.jar'
        else:
            self.py4j_jar_path = py4j_jar_path

        self.py4j_process = self._init_py4j_server()
        self.app = self._init_py4j_client()

    def __del__(self):
        """析构时释放子进程资源
        """
        if self.py4j_process:
            self.py4j_process.kill()
            self.py4j_process = None

    def _init_py4j_server(self):
        """启动使用 Py4j 启动的 Java 项目服务

        Returns:
            返回服务的进程 ID
        """
        cmd = 'java -cp {src}:{hanlp_jar_path}:{py4j_jar_path} Hanlp'.format(
            src=self.src_path,
            hanlp_jar_path=self.hanlp_jar_path,
            py4j_jar_path=self.py4j_jar_path,
        )
        # 使用子进程的方式启动
        py4j_process = subprocess.Popen(cmd, shell=True)
        # 不知道需要多久服务能正式启动，设定一个 sleep 5秒
        # 不这么做会在调用时显示服务还没启动
        # TODO: 应该还有更好的方法
        time.sleep(5)
        return py4j_process

    def _init_py4j_client(self):
        """启动使用 Py4j 启动的 Python 客户端服务

        Returns:
            返回 Java 对象的 Python 镜像
        """
        gateway = py4j.java_gateway.JavaGateway()
        app = gateway.entry_point
        return app

    def segment(self, text):
        """分词函数

        Args:
            text: 待分词的文本, UTF-8 编码

        Returns:
            返回一个生成器. 每个元素为 (word, postag), 均使用 UTF-8 编码
        """
        terms = self.app.segment(text)
        for term in terms:
            yield term[0].encode('utf-8'), term[1].encode('utf-8')

    def parse_dependency(self, text):
        """句法分析. 调用 HanLP 的最大熵依存句法分析

        Args:
            text: 待分析的文本, UTF-8 编码

        Returns:
            返回分析后的词典. dict = {ID: CoNLLWord}
        """
        items = self.app.parse_dependency(text)
        words = {}
        for item in items:
            _id, lemma, cpostag, postag, headid, deprel = item
            _id = int(_id)
            word = CoNLLWord(id=_id,
                             lemma=lemma.encode('utf-8'),
                             cpostag=cpostag.encode('utf-8'),
                             postag=postag.encode('utf-8'),
                             headid=int(headid),
                             deprel=deprel.encode('utf-8'))
            words[_id] = word
        return words


if __name__ == '__main__':
    hanlp = HanLP()

    terms = hanlp.parse_dependency('吃了几天 感觉皮肤开始亮了')
    for word in terms.values():
        print word

    terms = hanlp.segment('我最帅')
    for word, pos in terms:
        print word, pos
