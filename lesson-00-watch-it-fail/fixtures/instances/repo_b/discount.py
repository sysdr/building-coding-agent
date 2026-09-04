def apply_discount(price, pct):
    # bug: pct is a whole number like 10 for 10%, but this treats it as a
    # fraction already, so a 10% discount only takes off 0.1 currency units
    return price - pct
