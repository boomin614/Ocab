# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 13:31:40 2017
参考にした元ネタ
https://foolean.net/p/576
https://github.com/neologd/mecab-ipadic-neologd/wiki/Regexp.ja
http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt
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
      # 書き換え規則の定義
      # 基本的には単純なディクショナリ型(キー:書き換える品詞, 値:書き換え後の単語)
      # 書き換える品詞は入れ子状に記述可能(品詞→品詞細分類1→品詞細分類2→品詞細分類3の順で入れ子にしていく)
      # Default 	1) "名詞"でかつ品詞細分類1が"数"ならば"[数値]"に単語を置き換えて出力
      #	      		2) "名詞"でかつ品詞細分類1が"固有名詞"でかつ品詞細分類2が"組織"ならば"[固有名詞_組織]"に単語を置き換えて出力
      self.replace_rule = {
      	 '名詞': {
          '非自立': "",
          '固有名詞': {
            '人名': ""
		       }
        }
      }
    self.mecab     = MeCab.Tagger(self.opO + dOps)
    self.mecab.parse('')				# MeCab上の不具合で一度空で解析すると解消される
    
  def removeStoplist(self, documents, stoplist):
    #ストップワード対象文字列は、以下から取得
    #http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt
    if not isinstance(documents,str):
      return documents
    if len(stoplist)<1:
      stoplist = ["あそこ", "あたり", "あちら", "あっち", "あと", "あな", "あなた", "あれ", "いくつ", "いつ", "いま", "いや", "いろいろ", "うち", "おおまか", "おまえ", "おれ", "がい", "かく", "かたち", "かやの", "から", "がら", "きた", "くせ", "ここ", "こっち", "こと", "ごと", "こちら", "ごっちゃ", "これ", "これら", "ごろ", "さまざま", "さらい", "さん", "しかた", "しよう", "すか", "ずつ", "すね", "すべて", "ぜんぶ", "そう", "そこ", "そちら", "そっち", "そで", "それ", "それぞれ", "それなり", "たくさん", "たち", "たび", "ため", "だめ", "ちゃ", "ちゃん", "てん", "とおり", "とき", "どこ", "どこか", "ところ", "どちら", "どっか", "どっち", "どれ", "なか", "なかば", "なに", "など", "なん", "はじめ", "はず", "はるか", "ひと", "ひとつ", "ふく", "ぶり", "べつ", "へん", "ぺん", "ほう", "ほか", "まさ", "まし", "まとも", "まま", "みたい", "みつ", "みなさん", "みんな", "もと", "もの", "もん", "やつ", "よう", "よそ", "わけ", "わたし", "ハイ", "上", "中", "下", "字", "年", "月", "日", "時", "分", "秒", "週", "火", "水", "木", "金", "土", "国", "都", "道", "府", "県", "市", "区", "町", "村", "各", "第", "方", "何", "的", "度", "文", "者", "性", "体", "人", "他", "今", "部", "課", "係", "外", "類", "達", "気", "室", "口", "誰", "用", "界", "会", "首", "男", "女", "別", "話", "私", "屋", "店", "家", "場", "等", "見", "際", "観", "段", "略", "例", "系", "論", "形", "間", "地", "員", "線", "点", "書", "品", "力", "法", "感", "作", "元", "手", "数", "彼", "彼女", "子", "内", "楽", "喜", "怒", "哀", "輪", "頃", "化", "境", "俺", "奴", "高", "校", "婦", "伸", "紀", "誌", "レ", "行", "列", "事", "士", "台", "集", "様", "所", "歴", "器", "名", "情", "連", "毎", "式", "簿", "回", "匹", "個", "席", "束", "歳", "目", "通", "面", "円", "玉", "枚", "前", "後", "左", "右", "次", "先", "春", "夏", "秋", "冬", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "百", "千", "万", "億", "兆", "下記", "上記", "時間", "今回", "前回", "場合", "一つ", "年生", "自分", "ヶ所", "ヵ所", "カ所", "箇所", "ヶ月", "ヵ月", "カ月", "箇月", "名前", "本当", "確か", "時点", "全部", "関係", "近く", "方法", "我々", "違い", "多く", "扱い", "新た", "その後", "半ば", "結局", "様々", "以前", "以後", "以降", "未満", "以上", "以下", "幾つ", "毎日", "自体", "向こう", "何人", "手段", "同じ", "感じ", "てる", "いる", "なる", "れる", "する", "ある", "こと", "これ", "さん", "して", "くれる", "やる", "くださる", "そう", "せる", "した", "思う", "できる", "くる", "みる", "しまう", "それ", "ここ", "ちゃん", "くん", "て", "に", "を", "は", "の", "が", "と", "た", "し", "で", "ない", "も", "な", "い", "か", "ので", "よう"]
    removed = ""
    for doc in  documents.split():
      if not doc in stoplist:
        removed += doc + " "
    #print(removed)
    return removed.strip()
  

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
  regexp = c.normalize(args.target)
  print("preprosess: {}".format(regexp))
  wakati = m.wakati(regexp)
  print("wakati    : {}".format(wakati))
  print("rmv st wds: {}".format(m.removeStoplist(wakati,[])))
  
