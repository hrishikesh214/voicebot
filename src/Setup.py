import datetime
import pyttsx3
import speech_recognition as sr
import json
import importlib as il
from colorama import Fore, Back, Style
import colorama

colorama.init(autoreset=True)

_debug = True
_log = True

if False and _debug:
    _log = False

_green = Back.GREEN
_red = Back.RED
_blue = Back.BLUE
_yellow = Back.YELLOW
_magenta = Back.MAGENTA


def debug(s, backcolor=None):
    if _debug:
        if backcolor is not None:
            print(backcolor + Fore.BLACK + s)
            print(Style.RESET_ALL)
        else:
            print(s)


def log(s, backcolor=None):
    if _log:
        if backcolor is not None:
            print(backcolor + Fore.BLACK + s)
            print(Style.RESET_ALL)
        else:
            print(s)

# format


def compareKeyword(str1, str2):
    str1 = str1.split('|')
    if str2 in str1:
        return True
    return False


def checkWord(words, query):
    words = words.split('||')
    found = False
    for word in words:
        for w in word.split('|'):
            if w in query:
                found = True
                break
        if found:
            break
    return found


def match_string(types, query):

    # make Flags
    next_turn = False
    is_match = True
    static_match = False

    can_survive = True
    static_match = False
    was_static = False

    # expect result
    result = {
        'matched': False,
        'variables': []
    }

    # check if nothing then return
    if query is not None and query == 'None':
        return result

    # initial configs
    var_types = ['?', '?*', '?-']
    types = [x.strip() for x in types.split('||')]
    s2 = query.split(' ')
    l2 = len(s2)
    variables = []
    # if True:
    try:

        for type in types:
            is_varry = False
            next_turn = False
            was_static = False
            debug(f"Taking = '{type}' as TYPE", _blue)
            log(f"Experimenting => '{type}' as TYPE", _blue)
            for x in var_types:
                if x in type:
                    is_varry = True
                    break
            if not is_varry:
                was_static = True
                debug('NON VARIABLE STRING FOUND', _yellow)
                debug(f'type = {type} query = {query}', _yellow)
                if type == query:
                    result['matched'] = True
                    static_match = True
                    break
                continue

            s1 = type.split(' ')
            l1 = len(s1)

            opt1, opt2 = 0, 0

            debug('Checking if not survive', _yellow)
            for x in s1:
                if x == '?-' or x == '?*':
                    opt1 += 1
                if x not in var_types:
                    debug(f"SURVIVE: checking '{x}'")
                    if not checkWord(x, query):
                        can_survive = False
                        debug(f"TYPE can't survive...", _yellow)
                        debug(f"'{x}' not found in query", _red)
                        break

            if not can_survive:
                can_survive = True
                log(f"SURVIVE: FAILED", _red)
                debug(f"THROWING TYPE | FOR SURVIVE: {can_survive}", _red)
                next_turn = True
                continue
            log(f"SURVIVE: PASSED", _green)
            debug(f"SURVIVE: PASSED", _green)
            if l2 < l1-opt1:
                debug(f"SIZE CHECK FAILED", _red)
                log(f"SIZE CHECK: FAILED", _red)
                is_match = False
                break
            debug(f"SIZE CHECK PASSED", _green)
            log(f"SIZE CHECK: PASSED", _green)
            variables = []
            j = 0
            for i in range(0, l1):

                debug(
                    f'i = {i} j = {j} l1 = {l1} l2 = {l2} s1[i] = {s1[i]} \t s2[j] = {s2[j]} \t compare = {compareKeyword(s1[i], s2[j])} ', _green)

                if s1[i] == '?':
                    debug(f"\tMatching = ?", _yellow)
                    variables.append(s2[j])
                    if (i+1 < l1 and not compareKeyword(s1[i+1], s2[j+1])) or ((i == l1-1) and (j+1 < l2)):
                        debug('thrown by ?', _red)
                        next_turn = True
                        is_match = False
                        break
                    else:
                        j += 1

                elif s1[i] == '?-':
                    debug(f"\tMatching = ?-", _yellow)
                    temp_vars = []
                    if i < l1-1:
                        next_match = s1[i+1]
                        if compareKeyword(next_match, s2[j]):
                            i += 1
                        else:
                            temp_vars.append(s2[j])
                            j += 1
                    else:
                        while j <= l2-1:
                            temp_vars.append(s2[j])
                            j += 1
                    temp_vars = " ".join(temp_vars)
                    debug(f"\tOptional Var = {temp_vars} PASSED", _yellow)
                    variables.append(temp_vars)

                elif s1[i] == '?*':
                    debug(f"\tMatching = ?*", _yellow)
                    temp_vars = []
                    if i < l1-1:
                        next_match = s1[i+1]
                        debug(f"\tnext_match = {next_match}", _blue)
                        while not compareKeyword(next_match, s2[j]):
                            temp_vars.append(s2[j])
                            if j+1 >= l2:
                                next_turn = True
                                break
                            j += 1
                    else:
                        while j <= l2-1:
                            temp_vars.append(s2[j])
                            j += 1
                    debug(f"\tnext_match = 'END'", _blue)
                    temp_vars = " ".join(temp_vars)
                    debug(f"\tOptional Var = {temp_vars} PASSED", _yellow)
                    variables.append(temp_vars)

                elif compareKeyword(s1[i], s2[j]):
                    debug(f'\tMatching static word = {s1[i]}', _yellow)
                    if j+1 >= l2:
                        continue
                    j += 1

                else:
                    debug(f'\tgot nothing trying to match next type', _red)
                    next_turn = True

                debug(f'\tStats:', _green)
                debug(f'\t\tVariables = {variables}', _blue)
                debug('\n')

                # check break tags
                if next_turn:
                    next_turn = False
                    continue
                if i == l1-1 and is_match:
                    result['matched'] = True
                    result['variables'] = variables
                    log(f"MATCH FOUND '{type}' AS TYPE", _green)
                    return result

        # check flags and return accordingly
        if not next_turn and ((not was_static) and is_match) or static_match:
            result['matched'] = ((not was_static) and is_match) or static_match
            result['variables'] = variables
            log(f"MATCH FOUND '{type}' AS TYPE", _green)
            return result
        else:
            log(f"MATCH NOT FOUND!", _red)
            return result
            # pass
    except Exception as e:
        debug(f"i got thrown exc = {e}", _red)
        return {"matched": False}
    return None


def match(alike=None):
    if alike is not None:
        def decorator(func):
            def inner_decorator(*args, **kwargs):
                _check = match_string(alike, kwargs['_query'])
                if not _check['matched']:
                    return
                del kwargs['_query']
                kwargs['vars'] = _check['variables']
                return func(*args, **kwargs)
            return inner_decorator
        return decorator
    return
