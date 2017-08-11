# What is this?
日本語解析ライブラリ[MeCab](http://taku910.github.io/mecab/)を使う際の、前処理を行うためのpython用ライブラリです。  
詳細は、[こちらを参照してください](http://boomin.yokohama/archives/634)

# How to use
## As a single program
単体で使うときは、以下のように使います。

```bash
$ python Mecab2.py 南アルプスの天然水-Ｓｐａｒｋｉｎｇ*Ｌｅｍｏｎ+レモン一絞り
input     : 南アルプスの天然水-Ｓｐａｒｋｉｎｇ*Ｌｅｍｏｎ+レモン一絞り
preprosess: 南アルプスの天然水-Sparking*Lemon+レモン一絞り
wakati    : 南アルプスの天然水 Sparking Lemon レモン 一 絞る
rmv st wds: 南アルプスの天然水 Sparking Lemon レモン 絞る
```

## As like Library in Python code
ライブラリとして使うときは、こんな感じです。

```python
$ python
from Mecab2 import Mecab2, Regexp
c = Regexp()
text1 = c.normalize("南アルプスの天然水-Ｓｐａｒｋｉｎｇ*Ｌｅｍｏｎ+レモン一絞り")
print(text1) # 南アルプスの天然水-Sparking*Lemon+レモン一絞り
m = Mecab2(target=["名詞","動詞","形容詞","副詞"])
text2 = m.wakati(text1)
print(text2) # 南アルプスの天然水 Sparking Lemon レモン 一 絞る
text3 = m.removeStoplist(text2, [])
print(text3) # 南アルプスの天然水 Sparking Lemon レモン 絞る
```

`m = Mecab2(target=["名詞","動詞","形容詞","副詞"])`の部分でもっといろいろ指定できたりしますが、  
そこはコード読んでください。

# Reference
1. [解析前に行うことが望ましい文字列の正規化処理](https://github.com/neologd/mecab-ipadic-neologd/wiki/Regexp.ja)
1. [MeCabとPythonで品詞を選びつつ分かち書きをしたよ](https://foolean.net/p/576)
