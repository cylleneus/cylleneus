def roman_to_arabic(n: str):
    """ Convert a Roman numeral to an Arabic integer. """

    if isinstance(n, str):
        n = n.upper()
        numerals = {'M': 1000,
                    'D': 500,
                    'C': 100,
                    'L': 50,
                    'X': 10,
                    'V': 5,
                    'I': 1
                    }
        sum = 0
        for i in range(len(n)):
            try:
                value = numerals[n[i]]
                if i+1 < len(n) and numerals[n[i+1]] > value:
                    sum -= value
                else:
                    sum += value
            except KeyError:
                return None
        return sum
