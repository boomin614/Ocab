# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 13:31:40 2017
元ネタ：https://foolean.net/p/576 と https://github.com/neologd/mecab-ipadic-neologd/wiki/Regexp.ja
@author: boomin
"""

from __future__ import unicode_literals
import MeCab
import re
import unicodedata

class Regexp:

  def __init__(self):
    self.c = self

  def unicode_normalize(self, cls, s):
    pt = re.compile('([{}]+)'.format(cls))

    def norm(c):
      return unicodedata.normalize('NFKC', c) if pt.match(c) else c

    s = ''.join(norm(x) for x in re.split(pt, s))
    s = re.sub('－', '-', s)
    return s

  def remove_extra_spaces(self, s):
    s = re.sub('[ 　]+', ' ', s)
    blocks = ''.join(('\u4E00-\u9FFF',  # CJK UNIFIED IDEOGRAPHS
            '\u3040-\u309F',  # HIRAGANA
            '\u30A0-\u30FF',  # KATAKANA
            '\u3000-\u303F',  # CJK SYMBOLS AND PUNCTUATION
            '\uFF00-\uFFEF'   # HALFWIDTH AND FULLWIDTH FORMS
            ))
    basic_latin = '\u0000-\u007F'

    def remove_space_between(cls1, cls2, s):
      p = re.compile('([{}]) ([{}])'.format(cls1, cls2))
      while p.search(s):
        s = p.sub(r'\1\2', s)
      return s

    s = remove_space_between(blocks, blocks, s)
    s = remove_space_between(blocks, basic_latin, s)
    s = remove_space_between(basic_latin, blocks, s)
    return s

  def separateSentence(self, s):
    return s.split(" ")

  def delspace(self, s):
    for i,t in enumerate(s):
      if len(t)<1:
        s.pop(i)
    return s

  def normalize(self, s):
    s = s.strip()
    s = self.unicode_normalize('０-９Ａ-Ｚａ-ｚ｡-ﾟ', s)

    def maketrans(f, t):
      return {ord(x): ord(y) for x, y in zip(f, t)}

    s = re.sub('[˗֊‐‑‒–⁃⁻₋−]+', '-', s)  # normalize hyphens
    s = re.sub('[﹣－ｰ—―─━ー]+', 'ー', s)  # normalize choonpus
    s = re.sub('[~∼∾〜〰～]', '', s)  # remove tildes
    s = s.translate(
      maketrans('!"#$%&\'()*+,-./:;<=>?@[¥]^_`{|}~｡､･｢｣',
        '！”＃＄％＆’（）＊＋，－．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜。、・「」'))

    s = self.remove_extra_spaces(s)
    s = self.unicode_normalize('！”＃＄％＆’（）＊＋，－．／：；＜＞？＠［￥］＾＿｀｛｜｝〜', s)  # keep ＝,・,「,」
    s = re.sub('[’]', '\'', s)
    s = re.sub('[”]', '"', s)
    return s

class Mecab2:
  def __init__(self, opO="-Ochasen", dicpath="",
               target=[], mode="genkei", form="han", splitchar=" ",
               replace_rule = "",
               exclusion=["記号","BOS/EOS"]):
    # ここでクラスのメンバーが定義されているのに注意
    self.opO       = opO
    self.dicpath   = dicpath
    self.target    = target
    self.mode      = mode
    self.form      = form
    self.splitchar = splitchar
    self.exclusion = exclusion
    if len(self.dicpath)>0:
      dOps = " -d "+ self.dicpath
    else:
      dOps = ""
    if len(replace_rule)>0:
      self.replace_rule = replace_rule
    else:
      self.replace_rule = {
      	 '名詞': {
          '非自立': "",
        }
      }
    self.mecab     = MeCab.Tagger(self.opO + dOps)
    self.mecab.parse('')				# MeCab上の不具合で一度空で解析すると解消される

  def wakati(self, line):
    text = ''
    node = self.mecab.parseToNode(line)

    # 一単語毎に解析
    while node:

      # 形態素のノードから形態素情報を取得
      # 得られる形態素情報は基本的に以下の順番のリストになっている
      # [品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音]
      word_surface = node.surface
      word_features = node.feature.split(',')

      # 単語の置き換え規則の確認及び実行
      local_replace_rule = self.replace_rule
      for x in range(3):
        if word_features[x] in local_replace_rule:
          if isinstance(local_replace_rule[word_features[x]], dict):
            local_replace_rule = local_replace_rule[word_features[x]]
          elif isinstance(local_replace_rule[word_features[x]], str):
            word_surface = local_replace_rule[word_features[x]]
            word_features = word_features[:5] + [word_surface, word_surface, word_surface]
            break

      # 解析対象の品詞か確認
      if (not len(self.target) or \
          word_features[0] in self.target) and \
          word_features[0] not in self.exclusion:

        # 指定された形式で出力に追加
        if self.mode == 'hyousou':
          word = word_surface
        elif self.mode == 'genkei':
          #word = word_features[6]
          if word_features[6] is '*':
            word = word_surface
          else:
            word = word_features[6]
          #print(word)
        elif self.mode == 'yomi':
          word = word_features[7]

        # 未定義(辞書内で"*"と表記される)の場合は出力しない
        if word is not '*':
          text += word + self.splitchar

      node = node.next

    # 解析した行に形態素があれば出力ファイルに記述
    if text is not '':
      text = re.sub(r'\s*$', "", text)
      return text

if __name__ == '__main__': #MeCab2.pyを実行すると以下が実行される（モジュールとして読み込んだ場合は実行されない）
  import argparse

  # 実行引数の受け取り
  parser = argparse.ArgumentParser(description="MeCabで分かち書きする前処理用コード")
  parser.add_argument('target', type=str, help="前処理対象となる文字列")
  args = parser.parse_args()

  c = Regexp()
  m = Mecab2()
  print("input     : {}".format(args.target))
  wakati = c.normalize(args.target)
  print("preprosess: {}".format(wakati))
  print("wakati    : {}".format(m.wakati(wakati)))
