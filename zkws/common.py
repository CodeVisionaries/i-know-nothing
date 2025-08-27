PUBLIC_GENERATOR = 5362171
PUBLIC_PRIME = 2000000579


def generate_value(x: int) -> int:
    h = pow(PUBLIC_GENERATOR, x, PUBLIC_PRIME)  # g**x mod P
    return h
