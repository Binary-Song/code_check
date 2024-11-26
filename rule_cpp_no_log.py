from code_check import Rule, Check, Line, RawDiff

class CppNoLogRule(Rule):
    def check(self, chk: Check) -> bool:
        return self.no_adding_word(chk, b'X1_LOG', "X1_LOG not allowed. Remove temporary logs before committing.")
    