from div_frac import get_max_ps_elems, recursively_check_range, getcontext
import argparse

#a, b, r = recursively_check_range(10, max_depth=8, verbose=True)
parser = argparse.ArgumentParser()
parser.add_argument("fixed_point_precision", nargs='?', default=getcontext().prec,
    type=int, help="Fixed point precision to use (default: `decimal.getcontext().prec`)")
parser.add_argument("--depth", "-d", type=int, default=8, help="Max. decimal places to recurse (default: 8)")
args = parser.parse_args()
fpp, d = args.fixed_point_precision, args.depth

result = get_max_ps_elems(dec_prec=fpp, depth=d)
print(f"{int(result)} items ({fpp} fixed point decimals, searched to a depth {d})")
