# coding: utf-8
from __future__ import unicode_literals
import re
from enum import IntEnum


class MergeResult(IntEnum):
    OLD_VALUE = 1
    NEW_VALUE = 2
    VALUES_ARE_SAME = 3
    MERGED = 4
    ERROR = 666


def replace_strategy(field_name, obj, new_value):
    """
    Replaces old value with a new one with no doubts
    """
    old_value = getattr(obj, field_name)

    if old_value == new_value:
        return MergeResult.VALUES_ARE_SAME

    setattr(obj, field_name, new_value)
    return MergeResult.NEW_VALUE


def replace_if_empty_strategy(field_name, obj, new_value):
    """
    Replaces old value with a new one only if
    old value is empty
    """

    old_value = getattr(obj, field_name)

    if old_value == new_value:
        return MergeResult.VALUES_ARE_SAME

    if not old_value:
        setattr(obj, field_name, new_value)
        return MergeResult.NEW_VALUE
    else:
        return MergeResult.OLD_VALUE


def replace_if_greater_strategy(field_name, obj, new_value):
    """
    Replaces old value with a new one only if
    new value is bigger than old one
    """
    old_value = getattr(obj, field_name)

    if old_value == new_value:
        return MergeResult.VALUES_ARE_SAME

    if new_value > old_value:
        setattr(obj, field_name, new_value)
        return MergeResult.NEW_VALUE
    else:
        return MergeResult.OLD_VALUE


def replace_if_len_is_greater_strategy(field_name, obj, new_value):
    """
    Replaces old value with a new one only if
    the length of the new value is bigger than old one
    """
    old_value = getattr(obj, field_name)

    if old_value == new_value:
        return MergeResult.VALUES_ARE_SAME

    if len(new_value or "") > len(old_value or ""):
        setattr(obj, field_name, new_value)
        return MergeResult.NEW_VALUE
    else:
        return MergeResult.OLD_VALUE


class Merger(object):
    def __init__(self, rules):
        """
        Rules is a list of tuples (re, merge_strategy_callable)
        """
        self.rules = rules

    def merge(self, obj, update_dict):
        res = {}
        for k, v in update_dict.items():
            for r, merger_func in self.rules:
                if re.search(r, k):
                    res[k] = merger_func(k, obj, v)
                    break

        return res
