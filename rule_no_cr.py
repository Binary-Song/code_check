from code_check import Rule, Check, Line, RawDiff

class NoCRRule(Rule):
    def check(self, chk: Check) -> bool:
        return self.no_adding_word(chk, b'\r', "Line ending CR(\\r) not allowed. Use LF(\\n) instead.")
    