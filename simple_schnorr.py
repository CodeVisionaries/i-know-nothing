import os
import argparse as ap
from random import SystemRandom


"""
Modular arthimatic is helpful here

We note that:
  (a + b) mod N = [(a mod N) + (b mod N)] mod N

therefore:
  (a*b) mod N = [(a mod N)*(b mod N)] mod N

also:
  (a mod N) mod N = a mod N

and:
  (a**b mod N) = (a mod N)**b mod N
"""


# TODO: we should generate these in a better way than hand crafted
# and for practical purposes they should be much, much bigger!
PUBLIC_GENERATOR = 5362171
PUBLIC_PRIME = 2000000579


def _generate_random() -> int:
    return SystemRandom().randrange(PUBLIC_PRIME)


def generate_public_key_from_private_key(secret: int) -> int:
    # we assume it is hard for them to find x given g**x (this is a large number)
    h = pow(PUBLIC_GENERATOR, secret, PUBLIC_PRIME)  # g**x mod P
    return h


def prover_for_verifier_step1() -> tuple[int, int]:
    random_value = _generate_random()
    u = pow(PUBLIC_GENERATOR, random_value, PUBLIC_PRIME)
    return random_value, u


def verifier_for_prover_step1() -> int:
    c = _generate_random()
    return c


def prover_for_verifier_step2(secret: int, r: int, c: int) -> int:
    # this is because of modulo congruency: https://en.wikipedia.org/wiki/Congruence_relation
    # a = b (mod p) -> a mod p == b mod p
    # so that if b mod p = b (as we require 1 < b < p)
    # a mod p = b, therefore a = p*n + b
    z = r + (c * secret)
    return z


def v_check_step3(z: int, h: int, u: int, c: int) -> bool:
    # z, h, u are from the prover
    # c is from the verifier
    # if we expand this using the identities at the top of this script
    # we can indeed see that they should be equal if all done correctly
    # as   z = r + c*secret
    # and  u = g**r mod p
    # and  h = g**secret mod p
    lhs = pow(PUBLIC_GENERATOR, z, PUBLIC_PRIME)
    rhs = (u * pow(h, c, PUBLIC_PRIME)) % PUBLIC_PRIME
    return lhs == rhs


def main():
    # params to show it works
    use_real_date = True

    # the secret - the birthday encoded via DDMMYYYY
    # in this case it can clearly be found by brute force but we ignore that here
    real_secret_date = 25121984
    fake_secret_date = 24091983

    # this should be in a commitment
    h = generate_public_key_from_private_key(real_secret_date)
    print(
        f"INFO: Generated {h} from secret_date, using public g: {PUBLIC_GENERATOR} and p: {PUBLIC_PRIME}"
    )

    # and prover sends to verifier u, which has a random value in it
    # NOTE: always generate a new p_random otherwise they can work out the secret!
    p_random, u = prover_for_verifier_step1()
    print(f"INFO: Prover generates u: {u} from random value: {p_random}")

    # verifier generates a random value and sends to prover
    c = verifier_for_prover_step1()
    print(f"INFO: Verifier generates random value c: {c} and sends to prover")

    # prover uses their private random number and c from verifier to generate z
    birthdate = real_secret_date if use_real_date else fake_secret_date
    z = prover_for_verifier_step2(birthdate, p_random, c)
    print(
        f"INFO: Prover uses random value generated in step 1: {p_random}, and combines c (from verifier): {c} with secret date, to generate z: {z}"
    )

    # verifier recieves z and checks
    print(
        f"INFO: Prover then sends z: {z}, h: {h}, u: {u} to verifier (they already know c)."
    )
    print(
        f"INFO: Note the prover should NOT send random value generated in step 1: {p_random}, otherwise they can figure out the secret via secret = (z-r)/c!"
    )
    not_lying = v_check_step3(z, h, u, c)

    print(
        "\n** They know the secret **"
        if not_lying
        else "\n** They're lying! They don't the secret **"
    )


if __name__ == "__main__":
    main()
