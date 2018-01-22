# -*- coding: utf-8 -*-

import re
import sys


# 注意：使用python的re时，\s是包括\n和\r的。

_blank_re = re.compile(u'[\s\0]+', re.U)


def tounicode(s, enc='utf8', errors='ignore'):
    """ 将s转成unicode，若s不是str（已经是unicode），直接返回。
    :type s: str | unicode
    """
    return s.decode(enc, errors) if isinstance(s, str) else s


def tobytes(s, enc='utf8', errors='ignore'):
    """ 若s为unicode，转成相应编码的str；若s不是unicode，强转成str。
    :type s: unicode | str
    """
    return s.encode(enc, errors) if isinstance(s, unicode) else bytes(s)


def strip(s, chars=None):
    """ 清掉字符串头尾的空白符和换行
    :type s: unicode
    :type chars: unicode
    :param chars: 需要清掉的字符，若为None或''则使用默认清除。
    :rtype: unicode
    :return: 已清掉头尾空白字符的字符串。
    """
    s = tounicode(s)
    return s.strip(chars)


def isblank(s, white_chars=None):
    """ 判断字符串是否为空白串（空白字符组成）
    :type s: unicode
    :type white_chars: unicode
    :param white_chars: 属于空白的字符，若为None或''则使用默认字符。
    """
    if s is None:
        return True

    if isempty(s):
        return True

    s = tounicode(s)
    return isempty(strip(s, white_chars))


def isempty(s):
    """ 判断字符串是否为空串（长度为0）
    :type s: unicode | str
    """
    if s is None:
        return True
    return len(s) == 0


def display_length(s):
    """
    获取文本的显示长度，ascii计为1，其它计为2。
    ps: 一个emoji字符占python两个字符，所以一个emoji这里会计为4。
    现用新方案：一个一个数！
    旧方案如下（为计算emoji，不采用）：
    cn_char_1 = len(tounicode(s))
    cn_char_3 = len(tobytes(s))
    return (cn_char_1 + cn_char_3) / 2
    :type s: unicode
    """
    s = tounicode(s)
    total = 0
    for c in s:
        o = ord(c)
        total += (1 if o < 128 else 2)
    return total


def char_count_ty(s):
    """
    计算文本中的字数（汤圆版）。
    空白符（空格、换行等）计为0，英文字符计为0.5，其它计为1，总数再向上取整。
    ps: 一个emoji字符占python两个字符，所以一个emoji这里会计为2。
    :type s: unicode
    """
    s = _blank_re.sub(u'', tounicode(s))
    return (display_length(s) + 1) / 2


def replace_blank(s, repl=u' '):
    """ 将字符串里的(连续)空白替换成指定字符串，换行不算空白。
    因为python的re库会把\n算进\s里，所以这里先分行处理，再拼接。
    注意：此函数会对换行造成影响（对换行进行规范化，并清掉尾空行）。
    :type s: unicode
    """
    lines = tounicode(s).splitlines()
    lines = [_blank_re.sub(repl, fi_line) for fi_line in lines]
    return u'\n'.join(lines)


def format_comment(s):
    """ 格式化评论。
    将连续空白替换成一个空格，清掉每行头尾空白，清掉空白行。
    :type s: unicode
    """
    lines = tounicode(s).splitlines()
    lines = filter(lambda x: not isblank(x),
                   map(lambda x: strip(x),
                       map(lambda x: replace_blank(x), lines)))
    return u'\n'.join(lines)


def join_lines(s, joiner=u''):
    """
    将字符串 s 按行拆分，并用 joiner 连接起来
    :rtype: unicode
    """
    return joiner.join(tounicode(s).splitlines())


def ellipsify(s, length, ellipsis=u'…'):
    """
    若字符串 s 超过指定长度 length，将把 s 进行截断并在末尾添加 ellipsis。
    :rtype: unicode
    """
    s = tounicode(s)
    if len(s) <= length:
        return s

    s = unicode_slice(s, 0, length)
    if ellipsis:
        s += ellipsis

    return s


"""
unicode 扩展字符集使用 2 个 16 位字符（即 2 个普通字符）来表示一个字符，
所以类似 emoji 之类的字符是用 2 个连续的字符来表示，叫做 surrogate（代替）。
而这两个字符分别叫“引导”代替和“尾随”代替（也会叫“高端”代替和“低端”代替）。
引导代替（高端代替）和尾随代替（低端代替）的值，分别在下面两个定义中。
"""
UNICODE_SURROGATE_BEGIN = re.compile(ur'[\uD800-\uDBFF]')
UNICODE_SURROGATE_END = re.compile(ur'[\uDC00-\uDFFF]')


def unicode_slice(s, start, end):
    """
    支持 unicode 扩展字符的 slice，至于 unicode 扩展字符，可以看上面的简要文档。
    若使用传统的 slice，可能会截断 emoji 等双字符形式的字符。
    本方法会通过检查 unicode surrogate 来对 slice 的结果进行校正。
    注意：本方法返回的字符串长度，有可能不会是 end - start（因为校正过嘛）
    :param start: start index (inclusive)
    :param end: end index (exclusive)
    :rtype: unicode
    """
    s = tounicode(s)

    result = s[start:end]
    if not result:
        return result

    should_re_slice = False

    # 若起始字符被截断，则向后移一字符
    if UNICODE_SURROGATE_END.match(result[0]):
        start += 1
        should_re_slice = True

    # 若结束字符被截断，也向后移一字符
    if UNICODE_SURROGATE_BEGIN.match(result[-1]):
        if end == -1:
            end = sys.maxint  # 与 python 的 [:] 一致
        else:
            end += 1
        should_re_slice = True

    if should_re_slice:
        result = s[start:end]
    return result


def pad(s, char=' ', multiple_of=16):
    """
    在 s 后填充 char，使其满足长度为 multiple_of 的倍数
    :type s: str | unicode
    :type char: str | unicode
    :rtype: str | unicode
    """
    s_size = len(s)
    mod = s_size % multiple_of
    if mod == 0:
        return s
    pad_size = multiple_of - mod
    pad_str = char * pad_size
    return s + pad_str
