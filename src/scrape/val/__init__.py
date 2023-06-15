from enum import Enum


def splitat(s: str, p: str) -> (str, str):
    split_values = s.split(p, 1)
    lang, value = p.join(split_values[:-1]), split_values[-1]
    return (lang, value)


def currency(v: str) -> dict:
    return {"currency": v[-1:], "value": float(v[:-1].replace(",", "."))}


class Language(Enum):
    en_US = 1
    de_DE = 2
