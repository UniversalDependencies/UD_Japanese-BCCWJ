# Summary

This Universal Dependencies (UD) Japanese treebank is based on the definition of
UD Japanese convention described in the UD documentation.
The original sentences are from `Balanced Corpus of Contemporary Written Japanese'(BCCWJ).

# Introduction

The Japanese UD treebank contains the sentences from BCCWJ [1]
http://pj.ninjal.ac.jp/corpus_center/bccwj/en/
with BCCWJ-DepPara[2] annotation.

The word units is based on Short Unit Word in BCCWJ [1].
We prepared conversion rules from BCCWJ-DepPara to UD_Japanese v2.1 guidelines [3][4].

## Recovering data

The data is provided in the CoNLL format, but original texts are
stripped off due to the license issue.

The corpus is obtained by running the following command:

```
./merge/merge.sh -c BCCWJ_CORE_FILE
```

where `BCCWJ_CORE_FILE` denotes the file of BCCWJ core file (core_SUW.txt)

or

The BCCWJ DVD edition purchaser can download the data with the original text
from https://bccwj-data.ninjal.ac.jp/mdl/

## Spliting

Each data set contains UD annotations for the following parts in BCCWJ

training: annotation C, D, E subsets
development: annotation B subset
test: annotation A subset

See also https://github.com/masayu-a/BCCWJ-ANNOTATION-ORDER

## Citation

You are encouraged to cite the following paper when you refer to the
Universal Dependencies Japanese Treebank.

Asahara, M., Kanayama, H., Tanaka, T., Miyao, Y., Uematsu, S., Mori, S.,
Matsumoto, Y., Omura, M., & Murawaki, Y. (2018).
Universal Dependencies Version 2 for Japanese.
In LREC-2018.

# Acknowledgments

The original treebank was provided by:

- National Instutite for Japanese Language and Linguistics, Japan

The corpus was converted by:

- Mai Omura
- Masayuki Asahara

through discussion and validation with

- Hiroshi Kanayama
- Yusuke Miyao
- Takaaki Tanaka
- Yuji Matsumoto
- Shinsuke Mori
- Sumire Uematsu
- Yugo Murawaki

This work was supported by JSPS KAKENHI Grants Numbers JP17H00917
and is a project of the Center for Corpus Development, NINJAL.

# License

See file LICENSE.txt

# Reference

[1] Maekawa, K., Yamazaki, M., Ogiso, T., Maruyama, T., Ogura, H., Kashino, W.,
Koiso, H., Yamaguchi, M., Tanaka, M. & Den, Y. (2014). Balanced corpus of contemporary written Japanese. Language resources and evaluation, 48(2), 345-371.
[2] Asahara, M., & Matsumoto, Y. (2016). Bccwj-deppara: A syntactic annotation treebank on the ‘Balanced Corpus of Contemporary Written Japanese’. In Proceedings of the 12th Workshop on Asian Language Resources (ALR12) (pp. 49-58).
[3] Tanaka, T., Miyao, Y., Asahara, M., Uematsu, S., Kanayama, H., Mori, S., &
Matsumoto, Y. (2016). Universal Dependencies for Japanese. In LREC-2016.
[4] Asahara, M., Kanayama, H., Tanaka, T., Miyao, Y., Uematsu, S., Mori, S.,
Matsumoto, Y., Omura, M., & Murawaki, Y. (2018). Universal Dependencies Version 2 for Japanese. In LREC-2018.

Changelog

2018-11-01   v2.3
  * Update v2.2 to v2.3.
2018-03-28   v2.2
  * Initial release in Universal Dependencies.

=== Machine-readable metadata =================================================
Data available since: UD v2.2
License: CC BY-NC-SA 4.0 International
Includes text: no
Genre: news nonfiction fiction blog web
Lemmas: not available
UPOS: converted from manual
XPOS: not available
Features: not available
Relations: converted from manual
Contributors: Omura, Mai; Asahara, Masayuki; Miyao, Yusuke; Tanaka, Takaaki; Kanayama, Hiroshi; Matsumoto, Yuji; Mori, Shinsuke; Uematsu, Sumire; Murawaki, Yugo
Contributing: elsewhere
Contact: masayu-a@ninjal.ac.jp
===============================================================================
