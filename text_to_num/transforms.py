# MIT License

# Copyright (c) 2018-2019 Groupe Allo-Media

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
from itertools import dropwhile
from typing import Any, Iterator, List, Sequence, Tuple

from .lang import LANG
from .parsers import WordStreamValueParser, WordToDigitParser, WordStreamValueParserGerman

import logging


def look_ahead(sequence: Sequence[Any]) -> Iterator[Tuple[Any, Any]]:
    """Look-ahead iterator.

    Iterate over a sequence by returning couples (current element, next element).
    The last couple returned before StopIteration is raised, is (last element, None).

    Example:

    >>> for elt, nxt_elt in look_ahead(sequence):
    ... # do something

    """
    maxi = len(sequence) - 1
    for i, val in enumerate(sequence):
        ahead = sequence[i + 1] if i < maxi else None
        yield val, ahead


def text2num(text: str, lang: str, relaxed: bool = False) -> int:
    """Convert the ``text`` string containing an integer number written in French
    into an integer value.

    Set ``relaxed`` to True if you want to accept "quatre vingt(s)" as "quatre-vingt".

    Raises an AssertionError if ``text`` does not describe a valid number.
    Return an int.
    """

    language = LANG[lang]
    
    # The German number writing rules do not apply to the order of number processing
    # in the commin WordStreamValueParser
    if lang == "de":
        # German numbers are frequently written without spaces. Split them.
        text = language.split_ger(text)
        num_parser = WordStreamValueParserGerman(language)
        num_parser.parse(text)
        return num_parser.value
    else:
        num_parser = WordStreamValueParser(language, relaxed=relaxed)
        
    tokens = list(dropwhile(lambda x: x in language.ZERO, text.split()))
    if not all(num_parser.push(word, ahead) for word, ahead in look_ahead(tokens)):
        raise ValueError("invalid literal for text2num: {}".format(repr(text)))
            
    return num_parser.value


def alpha2digit(
    text: str, lang: str, relaxed: bool = False, signed: bool = True
) -> str:
    """Return the text of ``text`` with all the French spelled numbers converted to digits.
    Takes care of punctuation.
	
	THIS IS STILL IN DEVELOOPMENT FOR GERMAN LANGUAGE
	
    Set ``relaxed`` to True if you want to accept some disjoint numbers as compounds.
    Set ``signed`` to False if you don't want to produce signed numbers, that is, for example,
    if you prefer to get « moins 2 » instead of « -2 ».
    """
    
    if lang == "de":
        language = LANG[lang]
        segments = re.split(r"\s*[\.,;\(\)…\[\]:!\?]+\s*", text)
        punct = re.findall(r"\s*[\.,;\(\)…\[\]:!\?]+\s*", text)
  
        if len(punct) < len(segments):
            punct.append("")

        out_segments: List[str] = []
        for segment, sep in zip(segments, punct):

            tokens = segment.split()
            sentence = []
            out_tokens: List[str] = []
            out_tokens_is_num: List[bool] = []
            old_num_result = None
            token_index = 0

            while token_index < len(tokens):
                t = tokens[token_index]
                sentence.append(t)
                                    
                try:
                    num_result = text2num(" ".join(sentence), lang)
                    old_num_result = num_result
                    token_index += 1
                except:
                    # " ".join(sentence) cannot be resolved to a number
                    
                    # last token has to be tested again in case there is sth like "eins eins eins"
                    # which is invalid in sum but separately allowed
                    if not old_num_result is None:
                        out_tokens.append(str(old_num_result))
                        out_tokens_is_num.append(True)
                        sentence.clear()
                    else:
                        out_tokens.append(t)
                        out_tokens_is_num.append(False)
                        sentence.clear()
                        token_index += 1
                    old_num_result = None
                    
            # any remaining tokens to add?
            if not old_num_result is None:
                out_tokens.append(str(old_num_result))
                out_tokens_is_num.append(True)
                
            # join all and keep track on signs
            out_segment = ""
            for index, ot in enumerate(out_tokens):
                if (ot in language.SIGN) and signed:
                    if index < len(out_tokens)-1:
                        if out_tokens_is_num[index+1] == True:
                            out_segment += language.SIGN[ot]
                else:
                    out_segment +=ot + " "
                        
            out_segments.append(out_segment.strip())
            out_segments.append(sep)
        
        
        return "".join(out_segments)
    else:
        language = LANG[lang]
        segments = re.split(r"\s*[\.,;\(\)…\[\]:!\?]+\s*", text)
        punct = re.findall(r"\s*[\.,;\(\)…\[\]:!\?]+\s*", text)
        if len(punct) < len(segments):
            punct.append("")
        out_segments: List[str] = []
        for segment, sep in zip(segments, punct):
            tokens = segment.split()
            num_builder = WordToDigitParser(language, relaxed=relaxed, signed=signed)
            in_number = False
            out_tokens: List[str] = []
            for word, ahead in look_ahead(tokens):
                if num_builder.push(word.lower(), ahead and ahead.lower()):
                    in_number = True
                elif in_number:
                    out_tokens.append(num_builder.value)
                    num_builder = WordToDigitParser(language, relaxed=relaxed)
                    in_number = num_builder.push(word.lower(), ahead and ahead.lower())
                if not in_number:
                    out_tokens.append(word)
            # End of segment
            num_builder.close()
            if num_builder.value:
                out_tokens.append(num_builder.value)
            out_segments.append(" ".join(out_tokens))
            out_segments.append(sep)
        return "".join(out_segments)
