#!/usr/bin/env python

import html
import string
import re
from typing import List

import defopt
import jieba
import zhon.hanzi
from elasticsearch import Elasticsearch
from logzero import logger


# TODO: get someone to verify the output for zh and ko (english seems ok)
# TODO: rewerite this whole module to use Sentences class to do tokenization

# TODO: this should probably be in a config file somewhere
LANGS = ["en", "ko", "zh", "es", "fr"]


# string.punctuation, except for '
re_en = string.punctuation.replace("'", "")
# compile regular expression once (outside str_to_setnence) since we'll call
# them repeatedly

# TODO: someone verify these regular expressions
RE_PUNCTS = {
    # string.punctuation, minus '
    "en": re.compile(rf"[{re_en}]"),
    "zh": re.compile(rf"[{zhon.hanzi.punctuation + string.punctuation}]"),
    # TODO: are these all the punctuation characters in korean?
    "ko": re.compile(rf"[{zhon.hanzi.punctuation + string.punctuation}]"),
    "es": re.compile(rf"[{string.punctuation}]"),
    "fr": re.compile(rf"[{string.punctuation}]"),
}

# Elasticsearch segmentation
def create_elasticsearch_indices(
    langs: List[str] = ["en", "ko", "zh", "es", "fr"],
    host: str = "localhost",
    port: int = 9200,
    rebuild: bool = True,
) -> None:
    """
    Setup elasticsearch to do tokenization for sentences
    """
    # TODO: stopwords for ko and zh?
    indices = {
        "ko": {
            "settings": {
                "analysis": {
                    "tokenizer": {
                        "nori_tok": {
                            "type": "nori_tokenizer",
                            "decompound_mode": "none",
                        }
                    },
                    "analyzer": {
                        "ko": {
                            "tokenizer": "nori_tok",
                            "filter": [
                                "nori_readingform",
                                # "lowercase"
                            ],
                        }
                    },
                }
            }
        },
        "zh": {
            "settings": {
                "analysis": {"analyzer": {"zh": {"tokenizer": "smartcn_tokenizer"}}}
            }
        },
        "en": {
            "settings": {
                "analysis": {
                    "filter": {
                        "english_stop": {"type": "stop", "stopwords": "_english_"},
                        "english_stemmer": {"type": "stemmer", "language": "light_english"},
                        "english_possessive_stemmer": {
                            "type": "stemmer",
                            "language": "possessive_english",
                        },
                    },
                    "analyzer": {
                        "en": {
                            "tokenizer": "standard",
                            "filter": [
                                "english_possessive_stemmer",
                                "lowercase",
                                "english_stop",
                                "english_stemmer",
                            ],
                        }
                    },
                }
            }
        },
        "fr": {
            "settings": {
                "analysis": {
                    "filter": {
                        "french_elision": {
                            "type": "elision",
                            "articles_case": "true",
                            "articles": [
                                "l",
                                "m",
                                "t",
                                "qu",
                                "n",
                                "s",
                                "j",
                                "d",
                                "c",
                                "jusqu",
                                "quoiqu",
                                "lorsqu",
                                "puisqu",
                            ],
                        },
                        "french_stop": {"type": "stop", "stopwords": "_french_"},
                        "french_stemmer": {
                            "type": "stemmer",
                            "language": "light_french",
                        },
                    },
                    "analyzer": {
                        "fr": {
                            "tokenizer": "standard",
                            "filter": [
                                "french_elision",
                                # "lowercase",
                                # "french_stop",
                                # "french_stemmer",
                            ],
                        }
                    },
                }
            }
        },
        "es": {
            "settings": {
                "analysis": {
                    "filter": {
                        "spanish_stop": {"type": "stop", "stopwords": "_spanish_"},
                        "spanish_stemmer": {
                            "type": "stemmer",
                            "language": "light_spanish",
                        },
                    },
                    "analyzer": {
                        "es": {
                            "tokenizer": "standard",
                            # "filter": [
                            #     "lowercase",
                            #     "spanish_stop",
                            #     "spanish_stemmer"
                            # ],
                        }
                    },
                }
            }
        },
    }

    es = Elasticsearch([f"{host}:{port}"])
    for lang in indices:
        if es.indices.exists(index=lang):
            if rebuild:
                es.indices.delete(index=lang)
                es.indices.create(index=lang, body=indices[lang])
        else:
            es.indices.create(index=lang, body=indices[lang])


def tokenize(
    s: str,
    lang: str = "en",
    drop_punctuation: bool = True,
    tokenizer: str = "elasticsearch",
    es: Elasticsearch = None,
    host: str = "localhost",
    port: int = 9200,
) -> List[str]:
    """
    Return tokenized string from string, accoding to tokenizer

    NOTE if tokenizer=='elasticsearch', elasticsearch is assumed to be
    running and have apropriate indices already created. That is, you must
    explicitly call create_elasticsearch_indices before calling this function

    :param s: utf-8 string (a sentence)
    :param lang: 2-character language id
    :param drop_punctuation: If True, remove punctuation characters
    :param tokenizer: one of elasticsearch, jieba, pylucene, or None (which does
        naive splitting on whitespace)
    :param es: elasticsearch client to use
    :param host: elaticsearch hostname (only applies if
        tokenizer==`elasticsearch`, ignored if es is passed directly)
    :param port: elaticsearch port (only applies if tokenizer==`elasticsearch`,
        ignored if es is passed directly)
    """
    # TODO: rename mathod to tokenizer, either a str or Callable, and
    # propagate to all functions in the call stack

    # unescape html special characters, eg '%gt;' -> '>'
    s = html.unescape(s)

    if drop_punctuation:
        s = RE_PUNCTS[lang].sub("", s.replace("\\", ""))

    if tokenizer is None:
        # naive splitting on whitespace
        return " ".join([w.strip() for w in s.split()])

    elif tokenizer == "elasticsearch":
        if es is None:
            es = Elasticsearch([f"{host}:{port}"])

        # TODO: fail gracefully if elasticsearch isn't running?
        resp = es.indices.analyze(index=lang, body={"analyzer": lang, "text": s})

        # TODO: better error handling. Retrys, etc
        if not resp:
            return []

        tokens = resp["tokens"]
        return " ".join([t["token"] for t in tokens])

    elif tokenizer == "jieba":
        # cut_all False helps with accuracy
        # Hidden Markov Model to try to handle things
        # that jieba hasn't encountered before.
        tokens = jieba.cut(s, cut_all=False, HMM=True)
        return " ".join([t.strip() for t in tokens])

    elif tokenizer == "pylucene":
        # TODO: implement pylucene, or remove the tokenizer entirely
        raise NotImplementedError

    elif tokenizer == "moses":
        raise NotImplementedError
    else:
        raise ValueError(f"Unknown tokenizer: {tokenizer}")


if __name__ == "__main__":
    defopt.run([create_elasticsearch_indices])
