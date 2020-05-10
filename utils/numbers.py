import math

millnames = ['',' K',' M',' B',' T', ' Qd', 'Qt', ' Sx', ' Sp', ' Oc', ' No']

def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    if n < 1000:
        return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
    return '{:.4f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
    