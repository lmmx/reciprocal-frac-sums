# reciprocal-frac-sums

I wrote this code to calculate the maximum _n_ for which Python can distinguish unique sums of fractions
with alternating sign:

> ## {¹/ₙ, ⁻¹/ₙ₊₁, ¹/ₙ₊₂, …}

Python stops being able to distinguish the new terms in this sequence (i.e. stops being able to
distinguish the sums of sequences of this form of increasing length) because of the limit of decimal
precision.

It turns out, you can actually adopt arbitrarily precise decimal precision in Python using
[fixed point](https://docs.python.org/3/library/decimal.html) arithmetic (the `decimal` library).

This means that the maximum _n_ for which Python can distinguish the above sequence is really only
the maximum _n_ at that particular fixed point decimal precision.

- **Q**: What do I mean by "unable to distinguish"?

- **A**: When the mean absolute difference between the final two sequences' sums becomes a repeating sequence

The sequence above tends to a limit, and this limit is (𝒍𝒏2).

```py
log(2)
```
⇣
```STDOUT
0.6931471805599453
```

Here's a simple version of part of `div_frac.py`'s function `get_ln2_difference`:

```py
def recips(n):
    sum_list = []
    frac_list = []
    x_range = range(1,n+1)
    for x in x_range:
        sign = [-1, 1][x % 2]
        frac = 1 * sign / x
        frac_list.append(frac)
        frac_sum = sum(frac_list)
        sum_list.append(frac_sum)
    return sum_list
```

If we try `recips(20)` (and `round` the result to 3 decimal places) we get:

```py
[round(x, 3) for x in recips(20)]
```
⇣
```STDOUT
[1.0, 0.5, 0.833, 0.583, 0.783, 0.617, 0.76, 0.635, 0.746, 0.646, 0.737, 0.653, 0.73, 0.659, 0.725,
0.663, 0.722, 0.666, 0.719, 0.669]
```

Going further,

```py
[round(x, 5) for x in recips(100)][-6:]
```
⇣
```STDOUT
[0.69838, 0.68797, 0.69828, 0.68807, 0.69817, 0.68817]
```

- Because it tends to this limit, we could go to infinite decimal precision and always find some
  difference: it would just become a smaller and smaller difference.
- Because the sequence has terms of alternating sign, the final term decides the sign of the sum.
  Therefore, to compare this smaller-and-smaller difference, we need to compare a positive and a
  negative value

is on the order of 10⁵, log₂ of which is max. 19 (so can index a powerset of at
most 19 items) 

```
1/n - 1/(n+2)
```

---

Results from further on (description TBC)

We know it's somewhere between 1 and 8 for floating points `(override_decimal = True)`

```py
for i in range(1,8):
    dec_init = i
    pc_dec_init = dec_init
    a = get_ln2_differences(offset=10, pc=pc_dec_init, pd=getcontext().prec, check_rep=True, v=False)
    if a:
        a = get_ln2_differences(offset=10, pc=pc_dec_init, pd=getcontext().prec, check_rep=True)
        break
```
⇣

value is 5

We know it's somewhere between 4 and 5 so check 4.01 to 4.99

```py
for j in range(1,100):
    hun = j / 100
    pc_dec_fl_two = pc_dec_init - 1 + hun
    b = get_ln2_differences(offset=10, pc=pc_dec_fl_two, pd=getcontext().prec, check_rep=True, v=False)
    if b:
        b = get_ln2_differences(offset=10, pc=pc_dec_fl_two, pd=getcontext().prec, check_rep=True)
        break
```
⇣

value is 4.32

We know it's somewhere between 4.31 and 4.32

`10**4.31` exactly is a bit above `2**14`

```py
>>> log2(10**4.31)
14.31751008896453
```

---

We know it's somewhere between 8 and 8.5 for 28 fixed point `(override_decimal = False)`

```py
for i in range(1,50):
    dec = i / 100
    pc_dec = 8 + dec
    a = get_ln2_differences(offset=10, pc=pc_dec, pd=getcontext().prec, check_rep=True, v=False)
    if a:
        a = get_ln2_differences(offset=10, pc=pc_dec, pd=getcontext().prec, check_rep=True)
        break
```

value is 8.36

We know it's somewhere between 8.35 and 8.36

```py
for j in range(1,100):
    thou = j / 10_000
    pc_dec_two = pc_dec - 0.01 + thou
    b = get_ln2_differences(offset=10, pc=pc_dec_two, pd=getcontext().prec, check_rep=True, v=False)
    if b:
        b = get_ln2_differences(offset=10, pc=pc_dec_two, pd=getcontext().prec, check_rep=True)
        break
```

```py
>>> pc_dec_two
8.3501
>>> get_ln2_differences(offset=10, pc=8.35, pd=getcontext().prec, check_rep=True, v=False)
False
>>> get_ln2_differences(offset=10, pc=8.3501, pd=getcontext().prec, check_rep=True, v=False)
True
>>> get_ln2_differences(offset=10, pc=8.35001, pd=getcontext().prec, check_rep=True, v=False)
True
>>> get_ln2_differences(offset=10, pc=8.350001, pd=getcontext().prec, check_rep=True, v=False)
True
>>> get_ln2_differences(offset=10, pc=8.3500001, pd=getcontext().prec, check_rep=True, v=False)
True
```

`10**9.35` exactly is a little above `2**31`

```py
>>> log2(10**9.35)
31.060027687196836
```
