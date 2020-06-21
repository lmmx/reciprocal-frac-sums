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

This can be useful when we prefer to work with small numbers rather than large numbers (to achieve an
equivalent goal), and to work with them at a known level of precision (and no more than that).

- **Q**: What do I mean by "unable to distinguish"?

- **A**: When the mean absolute difference between the final two sequences' sums becomes a repeating sequence

The sequence above tends to a limit, and this limit is (𝒍𝒏2).

- `log(2)` = `0.6931471805599453`

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

If we try `recips(20)` we get the values it tends to for _n_ = 20

```py
[round(x, 3) for x in recips(20)]
```
⇣
```STDOUT
[1.0, 0.5, 0.833, 0.583, 0.783, 0.617, 0.76, 0.635, 0.746, 0.646, 0.737, 0.653, 0.73, 0.659, 0.725,
0.663, 0.722, 0.666, 0.719, 0.669]
```

You can see how the values approach the limit of `log(2)` = `0.6931`, alternating between being
above and below the limit for consecutive values in the sequence:

Going further, to _n_ = 100, we can then take the difference from the limit to show that the
difference is decreasing

```py
reciprocal_sums = [round(x, 5) for x in recips(100)][-6:]
print(reciprocal_sums)

ln2_differences = [log(2) - x for x in reciprocal_sums]
rounded_ln2_diffs = [round(x, 5) for x in ln2_differences]
print(rounded_ln2_diffs)
```
⇣
```STDOUT
[0.69838, 0.68797, 0.69828, 0.68807, 0.69817, 0.68817]
[-0.00523, 0.00518, -0.00513, 0.00508, -0.00502, 0.00498]
```

- The signs clearly alternate
- The final 3 digits are: `523, 518, 513, 508, 502, 498`

It's clear that taking the absolute difference gives a monotonically decreasing sequence.

- Because it tends to this limit, we could go to infinite decimal precision and always find some
  difference: it would just become a smaller and smaller difference.
- Because the sequence has terms of alternating sign, the final term decides the sign of the
  difference between the sum and the limit (if the final sign is negative then so too will be the
  sign of the difference).

**Q**: What happens when the computer representation of the decimal number "runs out of precision" to
represent the sum of reciprocals distinctly from the preceding sum of reciprocals?

**A**: The sums become the same: the sequence becomes repeating. With one caveat: because of the
nature of the convergence to the limit, alternating between above and below that limit, it's often
only visible when you compare next-but-one values in the sequence.

Two equivalent ways to check this are:

- Compare the next-but-one values in the sequence of sums of reciprocals
  - it's repeating when the values are the same
  - it's repeating when the differences contain 0

Note that the latter of these is _not_ the same as checking the difference between consecutive
values (which could show different values even if next-but-one are repeating).

In the function `get_ln2_differences`, I actually check all three: consecutive, odd, and even.
`numpy.ediff1d` gives the list of differences between consecutive values, which can be paired with
`[::2]` to refer to consecutive differences betweeen every next-but-one value:

```py
if check_rep:
    diffs_consec = np.ediff1d(arr[:,1])
    diffs_even = np.ediff1d(arr[:,1][::2])
    diffs_odd = np.ediff1d(arr[1:,1][::2])
    checked = 0 in np.hstack([diffs_consec, diffs_even, diffs_odd])
```

As its name suggests, the function `get_ln2_differences` returns these lists, and if passed
`check_rep=True` it will also perform the three checks above and return the boolean `True`
if the sequence becomes repeating or `False` if the sequence does not become repeating.

I built a range checking function on top of this, and then a recursive range checking function on
top of that, so you can specify a maximum _n_, check every integer up to that, then 'drill down'
recursively when you find the subrange containing the correct value.

Below are some examples I worked out manually to demonstrate the logic behind the calculations.

---

The numbers involved here get very large, many orders of magnitude must be tested. As such, the
parameter which controls the search is an exponent, the search is exponential. Since an exponent can
be a decimal we can narrow it down by recursively increasing the number of decimal places of the
result (i.e. the point at which the sequence stops being distinguishable, indicating max. _n_).

For floats, we find that the value of _n_ at which this happens is on the order of 10⁵, log₂ of which is
max. 19 (so can index a powerset of at most 19 items).

- A [powerset](https://en.wikipedia.org/wiki/Powerset) is the number of combinations of _i_
  items, and so if we know there are 10ⁿ items, then `log2(log10(10ⁿ))` is the order of the
  powerset of that size.
  - E.g. the powerset of 30 items is of order 2³⁰ = 1,073,741,824,
  - `log10(2**30)` is approx. 9
    - i.e. `10**9` is approx. 2³⁰
  - We can reverse this relationship by taking `log2(10**9)`
    - `log2(10**9)` = 29.897
    - Obviously to reverse it accurately we will need to use greater precision, and so
      I wrote the function `recursively_check_range`

As the previous example shows, accurately deriving the power of 10 which gives the maximum _n_ at
which you can distinguish this sequence in Python will let us denote by that exponent the index
of a powerset, and so discover how many items we can have in a powerset indexed at that level
of precision (which can't be changed for floating point, but can be set arbitrarily for fixed point
numbers, making its calculation important).

With this in mind, we can examine where that limit is in the two cases:

- Floating point using `override_decimal=False`
  - I'm not actually sure how much precision you can say floats have?

- Fixed point using `override_decimal=True`
  - Specifically here I will look at the default of 28 digit precision fixed point decimals
  - I originally thought this was the maximum, but in fact you can get arbitrarily many
    units of precision, all that's left to do is to find the associated maximum `n`

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

The examples above were done by hand, and then by manual calls to `get_ln2_differences`, but
obviously this is tiresome, so I wrote `check_range` to execute multiple calls to
`get_ln2_differences` with increasing exponent (`pc` is the name of the exponent), and then
`recursively_check_range` to 'drill down' to increasing decimal places (as shown in the example
above for `pc=8.35` to `pc=8.3501` etc).

- Note that the values searched are in the sequence up to `10**({pc} + 1)` so we must add 1 to
  whatever value we attain for `pc`

It's difficult to interpret the results of this 'drilling down' step to smaller decimal places
(but as the example above of 2³⁰ showed, this extra precision matters). I settled on a maximum
depth of 8, i.e. to add a further decimal place of precision to the exponent in searching for
the most precise value.

The following output is a little long, but in summary it shows that no greater precision can be
found at 8 decimal places of precision (in other words, 8.35 is a pretty solid approximate estimate
of the true value of `pc`, therefore 9.35 is a pretty good estimate for the exponent).

- `log2(10**9.35)` is a little above 31, so using 28 precision fixed point numbers lets us
  index the powerset of 31 items (as was calculated 'manually' with `get_ln2_differences` above)

```sh
python range_check_10.py 2>&1
```

```STDOUT
Checking from 1 to 10 in 1 steps from 1
--> Checking 1
--> Checking 2
--> Checking 3
--> Checking 4
--> Checking 5
--> Checking 6
--> Checking 7
--> Checking 8
--> Checking 9
Sequence becomes indistinguishable between 8 and 9
9999999990: 6931471806099452862767639830
9999999991: 6931471806099452862817639831
9999999992: 6931471806099452862767639830
9999999993: 6931471806099452862817639831
9999999994: 6931471806099452862767639830
9999999995: 6931471806099452862817639831
9999999996: 6931471806099452862767639830
9999999997: 6931471806099452862817639831
9999999998: 6931471806099452862767639830
9999999999: 6931471806099452862817639831
Checking from 8 to 9 in 0.1 steps from 8
--> Checking 8.0
--> Checking 8.1
--> Checking 8.2
--> Checking 8.3
--> Checking 8.4
Sequence becomes indistinguishable between 8.3 and 8.4
2511886421: 6931471803608917001171872554
2511886422: 6931471803608917000379425952
2511886423: 6931471803608917001171872554
2511886424: 6931471803608917000379425952
2511886425: 6931471803608917001171872553
2511886426: 6931471803608917000379425953
2511886427: 6931471803608917001171872553
2511886428: 6931471803608917000379425954
2511886429: 6931471803608917001171872552
2511886430: 6931471803608917000379425954
Checking from 8.3 to 8.4 in 0.01 steps from 8.3
--> Checking 8.3
--> Checking 8.31
--> Checking 8.32
--> Checking 8.33
--> Checking 8.34
--> Checking 8.35
--> Checking 8.36
Sequence becomes indistinguishable between 8.35 and 8.36
2290867642: 6931471807782032033727253995
2290867643: 6931471807782032034679984362
2290867644: 6931471807782032033727253996
2290867645: 6931471807782032034679984361
2290867646: 6931471807782032033727253996
2290867647: 6931471807782032034679984361
2290867648: 6931471807782032033727253997
2290867649: 6931471807782032034679984360
2290867650: 6931471807782032033727253998
2290867651: 6931471807782032034679984359
Checking from 8.35 to 8.36 in 0.001 steps from 8.35
--> Checking 8.35
--> Checking 8.351
Sequence becomes indistinguishable between 8.35 and 8.351
2243881913: 6931471803371171609572324753
2243881914: 6931471803371171608579277286
2243881915: 6931471803371171609572324753
2243881916: 6931471803371171608579277287
2243881917: 6931471803371171609572324752
2243881918: 6931471803371171608579277287
2243881919: 6931471803371171609572324751
2243881920: 6931471803371171608579277288
2243881921: 6931471803371171609572324750
2243881922: 6931471803371171608579277289
Checking from 8.35 to 8.351 in 0.0001 steps from 8.35
--> Checking 8.35
--> Checking 8.3501
Sequence becomes indistinguishable between 8.35 and 8.3501
2239236672: 6931471807832356629217022838
2239236673: 6931471807832356630214194684
2239236674: 6931471807832356629217022839
2239236675: 6931471807832356630214194683
2239236676: 6931471807832356629217022840
2239236677: 6931471807832356630214194683
2239236678: 6931471807832356629217022841
2239236679: 6931471807832356630214194682
2239236680: 6931471807832356629217022842
2239236681: 6931471807832356630214194681
Checking from 8.35 to 8.3501 in 1e-05 steps from 8.35
--> Checking 8.35
--> Checking 8.35001
Sequence becomes indistinguishable between 8.35 and 8.35001
2238772677: 6931471803366086316674408972
2238772678: 6931471803366086315676823747
2238772679: 6931471803366086316674408972
2238772680: 6931471803366086315676823748
2238772681: 6931471803366086316674408971
2238772682: 6931471803366086315676823749
2238772683: 6931471803366086316674408970
2238772684: 6931471803366086315676823750
2238772685: 6931471803366086316674408969
2238772686: 6931471803366086315676823751
Checking from 8.35 to 8.35001 in 1.0000000000000002e-06 steps from 8.35
--> Checking 8.35
--> Checking 8.350001
Sequence becomes indistinguishable between 8.35 and 8.350001
2238726283: 6931471803366040033746342660
2238726284: 6931471803366040032748716088
2238726285: 6931471803366040033746342659
2238726286: 6931471803366040032748716089
2238726287: 6931471803366040033746342658
2238726288: 6931471803366040032748716090
2238726289: 6931471803366040033746342657
2238726290: 6931471803366040032748716090
2238726291: 6931471803366040033746342656
2238726292: 6931471803366040032748716091
Checking from 8.35 to 8.350001 in 1.0000000000000002e-07 steps from 8.35
--> Checking 8.35
--> Checking 8.3500001
Sequence becomes indistinguishable between 8.35 and 8.3500001
2238721644: 6931471807832870318788196881
2238721645: 6931471807832870319785827587
2238721646: 6931471807832870318788196881
2238721647: 6931471807832870319785827586
2238721648: 6931471807832870318788196882
2238721649: 6931471807832870319785827585
2238721650: 6931471807832870318788196883
2238721651: 6931471807832870319785827584
2238721652: 6931471807832870318788196884
2238721653: 6931471807832870319785827584
Reached depth 0
```

To finish this off, I want to be able to find this correspondence between fixed point
decimal precision and the number of items whose powerset can be indexed by the arithmetic
progression of reciprocals.

This involves one final function, wrapping the call to `recursively_check_range` and
interpreting its output. In fact I made it its own program

```sh
python fixed_point_search.py -h
```
⇣
```STDOUT
usage: fixed_point_search.py [-h] [--depth DEPTH] [fixed_point_precision]

positional arguments:
  fixed_point_precision
                        Fixed point precision to use (default:
                        `decimal.getcontext().prec`)

optional arguments:
  --depth DEPTH, -d DEPTH
                        Max. decimal places to recurse (default: 8)
```

E.g. to recover the result above (the default will be 28 fixed point precision)

```sh
python fixed_point_search.py
```
⇣
```STDOUT
31 items (28 fixed point decimals, searched to a depth 8)
```

If you've got a known number of items you'd want to index, it can be useful
to search through the larger values, e.g. say I have 100 items, it seems to
be around the range of 10⁹¹.

```sh
python fixed_point_search.py 90
python fixed_point_search.py 91
python fixed_point_search.py 92
```
⇣
```STDOUT
99 items (90 fixed point decimals, searched to a depth 8)
100 items (91 fixed point decimals, searched to a depth 8)
101 items (92 fixed point decimals, searched to a depth 8)
```
