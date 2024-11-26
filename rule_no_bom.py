from code_check import Rule, Check, Line, RawDiff

class NoBomRule(Rule):
    def check(self, chk: Check) -> bool:
        return self.no_adding_word(chk, b'\xef\xbb\xbf', "BOM not allowed. Use UTF-8 without BOM.")
    