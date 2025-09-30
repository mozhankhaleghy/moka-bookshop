def to_persian_number(value):
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    safe_str = str(value)
    return ''.join(persian_digits[int(ch)] if ch in '0123456789' else ch for ch in safe_str)