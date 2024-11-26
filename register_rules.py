from rule_no_bom import NoBomRule
from rule_no_cr import NoCRRule
from rule_cpp_no_log import CppNoLogRule
from rule_no_binary_outside_lfs import NoBinaryOutsideLFS

def register_rules():
    rules = [ NoBomRule(), NoCRRule(), CppNoLogRule(), NoBinaryOutsideLFS() ]

    return rules
