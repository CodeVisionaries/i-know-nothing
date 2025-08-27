import argparse
import asyncio
import websockets
from random import SystemRandom

from common import PUBLIC_GENERATOR, PUBLIC_PRIME, generate_value


# not in common because both parties want their own
# way to generate their random values
def _generate_random() -> int:
    return SystemRandom().randrange(PUBLIC_PRIME)

def _generate_z(secret: int, r: int, c: int) -> int:
    # this is because of modulo congruency: https://en.wikipedia.org/wiki/Congruence_relation
    # a = b (mod p) -> a mod p == b mod p
    # so that if b mod p = b (as we require 1 < b < p)
    # a mod p = b, therefore a = p*n + b
    z = r + (c * secret)
    return z


async def make_commitment(secret: int):
    async with websockets.connect("ws://localhost:6789") as websocket:
        # this should be a commitment sent earlier,
        # but for this example we ignore this massive problem
        h = generate_value(secret)
        print(f"Prover >> h: {h}")
        await websocket.send(f"COMMIT:{h}")


async def make_verify(secret: int):
    async with websockets.connect("ws://localhost:6789") as websocket:
        # many months later, we now prove we know the secret
        # via the earlier commitment ....
        await websocket.send("VERIFY")

        # wait for verifier to send their random value c
        response = await websocket.recv()
        print(f"Prover <<: {response}")
        c = int(response)

        random_value = _generate_random()
        u = generate_value(random_value)
        z = _generate_z(secret, random_value, c)
        print(f"Prover >>: {z}:{u}")
        await websocket.send(f"{z}:{u}")

        # do they believe us?
        response = await websocket.recv()
        print(f"Prover <<: {response}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("option")
    parser.add_argument("secret", type=int)
    args = parser.parse_args()

    if args.option == 'commit':
        asyncio.run(make_commitment(int(args.secret)))
    else:
        asyncio.run(make_verify(int(args.secret)))
