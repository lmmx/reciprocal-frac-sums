from math import log, log10, log2
import numpy as np
from decimal import Decimal as d, getcontext
from sys import stderr

override_decimal = False

if override_decimal:
    d = lambda v: v

log_two = d(log(2))

def get_ln2_differences(offset=10, base=1, pc=5, pd=getcontext().prec,
        check_rep=False, v=True):
    """
    List the `{offset}` last values in the sequence of `10**({pc} + 1)`.

    `pc` and `pd` relate to the exponents ("powers") of `c` and `d` respectively,
    and these may be non-integer (i.e. floats).
    """
    base = d(base) # exponents and subtrahends do not need to be Decimal type
    c = d(10) ** d(pc + 1) # value beyond which to "continue" the sequence
    frac_list = []
    sum_list = []
    assert offset < c, ValueError("Decrease offset or increase pc")
    vals = []
    x_range = range(int(c) - offset, int(c))
    for x in x_range:
        sign = [-1, 1][x % 2]
        frac = base * sign / x
        frac_list.append(frac)
        frac_sum = sum(frac_list)
        sum_list.append(frac_sum)
        #print(frac, "--->", frac_sum)
        val = d(10)**pd * abs(log_two - sum(sum_list[-2:]) / 2)
        if v:
            print(f"{x}:", val, file=stderr)
        vals.append(val)
    arr = np.array([x_range, vals]).T
    if check_rep:
        diffs_consec = np.ediff1d(arr[:,1])
        diffs_even = np.ediff1d(arr[:,1][::2])
        diffs_odd = np.ediff1d(arr[1:,1][::2])
        checked = 0 in np.hstack([diffs_consec, diffs_even, diffs_odd])
        if v:
            result_check_message(check_bool=checked)
        return checked
    else:
        return arr

def result_check_message(check_bool, final_range=None):
    if final_range is None:
        range_str = ""
    else:
        range_str = "between " + " and ".join(map(repr,final_range))
    if check_bool:
        msg = f"Sequence becomes indistinguishable {range_str}"
    else:
        msg = f"Sequence remained distinguishable {range_str}, increase range"
    print(msg, file=stderr)
    return

def check_range(n, start=1, pc_step=1, offset=10, verbose=False):
    dp = getcontext().prec # decimal precision (in global context)
    if verbose:
        print(f"Checking from {start} to {n} in {pc_step} steps from {start}", file=stderr)
    round_prec = int(-log10(pc_step) + 1) # rounding precision
    start = round(start, round_prec)
    pc_ii = np.arange(start, round(n+pc_step, round_prec), pc_step).tolist()
    pc_ii = list(map(lambda x: round(x, round_prec), pc_ii))
    if verbose:
        print(f"--> pc_ii: {pc_ii}")
    for pc_i in pc_ii:
        if verbose:
            print(f"--> Checking {pc_i}", file=stderr)
        b = get_ln2_differences(offset=offset, pc=pc_i, pd=dp, check_rep=True, v=False)
        if b:
            success_range = (round(pc_i - pc_step, round_prec), pc_i)
            if verbose:
                result_check_message(check_bool=b, final_range=success_range)
            a = get_ln2_differences(offset=offset, pc=pc_i, pd=dp, v=verbose)
            return a, b, success_range
    failure_range = (start, n)
    if verbose:
        result_check_message(check_bool=False, final_range=failure_range)
    a = get_ln2_differences(offset=10, pc=pc_i, pd=getcontext().prec, v=verbose)
    return a, b, failure_range

def recursively_check_range(n, max_depth=8, start=1, pc_step=1, offset=10, verbose=False):
    a, b, r = check_range(n, start=start, pc_step=pc_step, offset=offset, verbose=verbose)
    if b:
        new_d = max_depth - 1
        if new_d < 1:
            if verbose:
                print(f"Reached depth {new_d}")
            return a, b, r
        else:
            if verbose:
                print(f"Current depth is {new_d}")
            new_start, new_n = r
            new_step = pc_step / 10
            return recursively_check_range(n=new_n, max_depth=new_d, start=new_start,
                                    pc_step = new_step, offset=offset, verbose=verbose)

def get_max_ps_elems(dec_prec=getcontext().prec, depth=8):
    getcontext().prec = dec_prec
    a, b, r = recursively_check_range(10+dec_prec, max_depth=depth, verbose=False)
    if b:
        lower_bound = 10**(r[0] + 1)
        max_ps_indexable_n_elems = log2(lower_bound)
        return max_ps_indexable_n_elems
    else:
        result_check_message(check_bool=b, final_range=r)
        return
