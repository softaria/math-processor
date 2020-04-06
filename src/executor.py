from sympy import *
import json
import sys
from sympy.integrals.manualintegrate import integral_steps
from sympy.parsing.sympy_parser import parse_expr
from enum import Enum

class Equiv(str,Enum):
    identical = "identical"
    equiv = "equiv"
    equivCalc = "equivCalc"
    different = "different"

class Simpler(str,Enum):
    first = "first"
    second = "second"
    none = "none"
    unknown = "unknown"


class Executor:

    def __init__(self):
        self.runners = {
            "integral_steps": lambda args: srepr(integral_steps(args[0], args[1])),
            "equiv": lambda args: self.equivJson(args[0],args[1]),
            "mirror": lambda args: srepr(args[0]), 
        }    

    def equiv(self,a1,a2):
        if a1==a2:
            return (Equiv.identical,Simpler.none)
        s1 = simplify(a1,doit=False)
        if s1==a2:
            return (Equiv.equiv,Simpler.second)
        s2 = simplify(a2,doit=False)
        if s2==a1:
            return (Equiv.equiv,Simpler.first)

        if s1==s2:
            return (Equiv.equiv,Simpler.unknown)

        v1 = a1.doit()
        v2 = a2.doit()   

        dif1 = simplify(v1-a2,doit=False)
        dif2 = simplify(v2-a1,doit=False)
       
        if dif1==dif2 and dif1==0:
            if v1==a2:
                return (Equiv.equivCalc,Simpler.second)    
            if v2==a1:
                return (Equiv.equivCalc,Simpler.first)     

        if dif1==0:
            return (Equiv.equivCalc,Simpler.second)
        if dif2==0:
            return (Equiv.equivCalc,Simpler.first)
        if simplify(v1-v2)==0:
            return (Equiv.equivCalc,Simpler.unknown)

        return (Equiv.different,Simpler.unknown)

    def equivJson(self,a1,a2):
        t = self.equiv(a1,a2)
        return {"eq":t[0],"si":t[1]}


   

    def run_custom(self, method: str, args: []):
        if method in self.runners:
            runner = self.runners[method]
            parsed_args = []
            for arg in args:
                try:
                    parsed_args.append(parse_expr(arg,evaluate=False))
                except:
                    return {"ok": False, "error": "Can't parse argument "+arg + " because of "+str(sys.exc_info()[1]), "errorCode": "BAD_ARGUMENT"}
            try:
                ret = runner(parsed_args)
                return {"ok": True, "result": ret}
            except:
                return {"ok": False, "error": str(sys.exc_info()[1]), "errorCode": "METHOD_FAILURE"}
        else:
            return {"ok": False, "error": "unsupported method", "errorCode": "BAD_METHOD"}

    def run_method(self, obj_str: str, method: str, args: []):
        parsed_args = []
        for arg in args:
            try:
                parsed_args.append(parse_expr(arg))
            except:
                return {"ok": False, "error": "Can't parse argument "+arg + " because of "+str(sys.exc_info()[1]), "errorCode": "BAD_ARGUMENT"}
        try:
            obj = parse_expr(obj_str)
            func = getattr(obj, method)
            result = srepr(func(*parsed_args))
            return {"ok": True, "result": result}
        except:
            return {"ok": False, "error": str(sys.exc_info()[1]), "errorCode": "METHOD_FAILURE"}

    def run_function(self, method: str, args: [],params:dict):
        parsed_args = []
        for arg in args:
            try:
                parsed_args.append(parse_expr(arg))
            except:
                return {"ok": False, "error": "Can't parse argument "+arg + " because of "+str(sys.exc_info()[1]), "errorCode": "BAD_ARGUMENT"}
        try:
            func = getattr(sys.modules['sympy'], method)
            result = srepr(func(*parsed_args,**params))
            return {"ok": True, "result": result}
        except:
            return {"ok": False, "error": str(sys.exc_info()[1]), "errorCode": "METHOD_FAILURE"}
