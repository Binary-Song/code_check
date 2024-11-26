from code_check import Rule, Check, Line, RawDiff

class NoTabRule(Rule):
    def check(self, chk: Check) -> bool:
        return self.no_adding_word(chk, b'\t', "Tabs not allowed. Use spaces for indentation.")
    