# flake8: noqa
import datetime
from io import StringIO
from unittest import TestCase

from boox_annotation_parser import parser

EXAMPLE_FILE = """\
Reading Notes | <<陈海贤:自我发展心理学 (陈海贤 [陈海贤]) (Z-Library)>>陈海贤
11丨僵固型思维：为什么你会活在别人的评判中？
2023-08-13 06:47  |  Page No.: 134
夸孩子“努力”比“聪明”更重要
【Note】期望装修的时候还能保留原物，可能是想多了
-------------------
2023-08-08 21:06  |  Page No.: 137
  就算你知道一件事真的要结束了，你还是会想方设法地延迟结束，你会停留在一份已经不适合你的工作中，就因为这份工作曾经很适合你；
·  你会停留在一段不断给你带来伤害的关系中，也许这段关系曾经很甜蜜；
·  你无法学习用新的应对方式来处理新的事物，就因为旧的应对方式曾经很有效。
-------------------
12丨突破僵固型思维：如何“正确地”犯错？
2023-08-08 21:07  |  Page No.: 142
从这个角度，“聪明不聪明”，“能力强不强”所形容的不应该是孤立的个体，而是个体和环境的互动方式能否促进能力的成长。
【Note】期望装修的时候还能保留原物，可能是想多了
-------------------
"""


class TestBasic(TestCase):
    def test_parses_file(self):
        annotations = parser.get_annotations(StringIO(EXAMPLE_FILE))

        assert (
            annotations.name
            == "陈海贤:自我发展心理学 (陈海贤 [陈海贤]) (Z-Library)"
        )
        assert annotations.author == "陈海贤"
        assert len(annotations.annotations) == 3

        expected_annotations = [
            parser.Annotation(
                "11丨僵固型思维：为什么你会活在别人的评判中？",
                datetime.datetime(2023, 8, 13, 6, 47),
                134,
                "夸孩子“努力”比“聪明”更重要",
                "期望装修的时候还能保留原物，可能是想多了",
            ),
            parser.Annotation(
                "11丨僵固型思维：为什么你会活在别人的评判中？",
                datetime.datetime(2023, 8, 8, 21, 6),
                137,
                "就算你知道一件事真的要结束了，你还是会想方设法地延迟结束，你会停留在一份已经不适合你的工作中，就因为这份工作曾经很适合你；\n·  你会停留在一段不断给你带来伤害的关系中，也许这段关系曾经很甜蜜；\n·  你无法学习用新的应对方式来处理新的事物，就因为旧的应对方式曾经很有效。",
                "",
            ),
            parser.Annotation(
                "12丨突破僵固型思维：如何“正确地”犯错？",
                datetime.datetime(2023, 8, 8, 21, 7),
                142,
                "从这个角度，“聪明不聪明”，“能力强不强”所形容的不应该是孤立的个体，而是个体和环境的互动方式能否促进能力的成长。",
                "期望装修的时候还能保留原物，可能是想多了",
            ),
        ]

        assert annotations.annotations == expected_annotations
