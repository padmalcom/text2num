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


"""
Test the ``text_to_num`` library.
"""
from unittest import TestCase
from text_to_num import alpha2digit, text2num


class TestTextToNumDE(TestCase):
    def test_text2num(self):
        self.assertEqual(text2num("null", "de"), 0)

        test1 = "dreiundfünfzig Milliarden zweihundertdreiundvierzigtausendsiebenhundertvierundzwanzig"
        self.assertEqual(text2num(test1, "de"), 53_000_243_724)

        test2 = "einundfünfzig Millionen fünfhundertachtundsiebzigtausenddreihundertzwei"
        self.assertEqual(text2num(test2, "de"), 51_578_302)

        test3 = "fünfundachtzig"
        self.assertEqual(text2num(test3, "de"), 85)

        test4 = "einundachtzig"
        self.assertEqual(text2num(test4, "de"), 81)

        self.assertEqual(text2num("fünfzehn", "de"), 15)
        self.assertEqual(text2num("einhundertfünfzehn", "de"), 115)
        self.assertEqual(text2num("hundertfünfzehn", "de"), 115)
        self.assertEqual(text2num("fünfundsiebzigtausend", "de"), 75000)
        self.assertEqual(text2num("eintausendneunhundertzwanzig", "de"), 1920)

    def test_text2num_centuries(self):
        self.assertEqual(text2num("neunzehnhundertdreiundsiebzig", "de"), 1973)

    def test_text2num_exc(self):
        self.assertRaises(ValueError, text2num, "tausendtausendzweihundert", "de")
        self.assertRaises(ValueError, text2num, "sechzigfünfzehn", "de")
        self.assertRaises(ValueError, text2num, "sechzighundert", "de")

    def test_text2num_zeroes(self):
        self.assertEqual(text2num("null", "de"), 0)
        self.assertRaises(ValueError, text2num, "null acht", "de") # This is not allowed and should be solved with alpha2digit
        self.assertRaises(ValueError, text2num, "null null hundertfünfundzwanzig", "de") # This is not allowed and should be solved with alpha2digit
        self.assertRaises(ValueError, text2num, "fünf null", "de")
        self.assertRaises(ValueError, text2num, "fünfzignullzwei", "de")
        self.assertRaises(ValueError, text2num, "fünfzigdreinull", "de")

    def test_alpha2digit_integers(self):
        source = "fünfundzwanzig Kühe, zwölf Hühner und einhundertfünfundzwanzig kg Kartoffeln."
        expected = "25 Kühe, 12 Hühner und 125 kg Kartoffeln."
        self.assertEqual(alpha2digit(source, "de"), expected)
        
        source = "Eintausendzweihundertsechsundsechzig Dollar."
        expected = "1266 Dollar."
        self.assertEqual(alpha2digit(source, "de"), expected)

        source = "eins zwei drei vier zwanzig fünfzehn"
        expected = "1 2 3 4 20 15"
        self.assertEqual(alpha2digit(source, "de"), expected)
        
        source = "einundzwanzig, einunddreißig."
        expected = "21, 31."
        self.assertEqual(alpha2digit(source, "de"), expected)


    def test_relaxed(self):
        source = "eins zwei drei vier fünf und zwanzig."
        expected = "1 2 3 4 5 und 20."
        self.assertEqual(alpha2digit(source, "de", relaxed=True), expected)

        source = "eins zwei drei vier fünfundzwanzig."
        expected = "1 2 3 4 25."
        self.assertEqual(alpha2digit(source, "de", relaxed=True), expected)

        source = "eins zwei drei vier fünf zwanzig."
        expected = "1 2 3 4 5 20."
        self.assertEqual(alpha2digit(source, "de", relaxed=True), expected)

        source = "vierunddreißig = vierunddreißig"
        expected = "34 = 34"
        self.assertEqual(alpha2digit(source, "de", relaxed=True), expected)

    def test_alpha2digit_formal(self):
        source = "plus dreiunddreißig neun sechzig null sechs zwölf einundzwanzig"
        alpha2digit(source, "de")
        expected = "+33 9 60 0 6 12 21"
        self.assertEqual(alpha2digit(source, "de"), expected)
        source = "plus dreiunddreißig neun sechzig 0 sechs zwölf einundzwanzig"
        self.assertEqual(alpha2digit(source, "de"), expected)

        source = "null neun sechzig null sechs zwölf einundzwanzig"
        expected = "0 9 60 0 6 12 21"
        self.assertEqual(alpha2digit(source, "de"), expected)

    def test_and(self):
        source = "fünfzig sechzig dreißig und elf"
        expected = "50 60 30 und 11"
        self.assertEqual(alpha2digit(source, "de"), expected)
		

    def test_alpha2digit_zero(self):
        source = "dreizehntausend null neunzig"
        expected = "13000 0 90"
        self.assertEqual(alpha2digit(source, "de"), expected)

        result = alpha2digit("null", "de")
        self.assertEqual(result, "0")

    def test_alpha2digit_ordinals(self):
        # Not yet applicable to German language
        return
        source = (
            " Fünfter dritter zweiter einundzwanzigster hundertster eintausendzweihundertdreißigster fünfundzwanzigster achtunddreißigster neunundvierzigster."
        )
        expected = "5ter third second 21st 100th 1230th 25th 38th 49th."
        self.assertEqual(alpha2digit(source, "de"), expected)

        source = (
            "first, second, third, fourth, fifth, sixth, seventh, eighth, ninth, tenth."
        )
        expected = "first, second, third, 4th, 5th, 6th, 7th, 8th, 9th, 10th."
        self.assertEqual(alpha2digit(source, "de"), expected)

    def test_alpha2digit_decimals(self):
        # Not yet applicable to German language
        return
        source = (
            "zwölf komma neunundneunzig, einhundertzwanzig komma null fünf,"
            " eins komma zweihundertsechsunddreißig."
        )
        expected = "12.99, 120.05, 1.236."
        self.assertEqual(alpha2digit(source, "de"), expected)

        self.assertEqual(alpha2digit("null komma fünfzehn", "de"), "0.15")

    def test_alpha2digit_signed(self):
        source = "Es ist drinnen plus zwanzig Grad und draußen minus fünfzehn Grad."
        expected = "Es ist drinnen +20 Grad und draußen -15 Grad."
        self.assertEqual(alpha2digit(source, "de"), expected)

    def test_one_as_noun_or_article(self):
        # Not applicable to German language
        return
        #source = "Ich nehme eins. Eins passt nicht!"
        #expected = "Ich nehme eins. Eins passt nicht!"
        #self.assertEqual(alpha2digit(source, "de"), expected)
        #source = "No one is innocent. Another one bites the dust."
        #self.assertEqual(alpha2digit(source, "de"), source)
        # End of segment
        #source = "No one. Another one. One one. Twenty one"
        #expected = "No one. Another one. 1 1. 21"
        #self.assertEqual(alpha2digit(source, "de"), expected)
		
    def test_second_as_time_unit_vs_ordinal(self):
        # Not yet applicable to German language
        return
    #    source = "One second please! twenty second is parsed as twenty-second and is different from twenty seconds."
    #    expected = "One second please! 22nd is parsed as 22nd and is different from 20 seconds."
    #    self.assertEqual(alpha2digit(source, "de"), expected)

    def test_uppercase(self):
        source = "FÜNFZEHN EINS ZEHN EINS"
        expected = "15 1 10 1"
        self.assertEqual(alpha2digit(source, "de"), expected)
