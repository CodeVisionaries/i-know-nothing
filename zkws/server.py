import asyncio
import websockets
from random import SystemRandom

from common import PUBLIC_GENERATOR, PUBLIC_PRIME

# not in common because both parties want their own
# way to generate their random values
def _generate_random() -> int:
    return SystemRandom().randrange(PUBLIC_PRIME)


def verify(z: int, h: int, u: int, c: int) -> bool:
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

clients = set()

_h = 0

async def echo(websocket):
    global _h
    clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Recieved: {message}")
            if message.startswith("COMMIT:"):
                real_message = message.replace("COMMIT:", "")
                # Respond to the client that sent the verify message
                print(f"Verifier << h: {real_message}")
                _h = int(real_message)
                # we store the public key until they want to verify
            elif message.startswith("VERIFY"):

                c = _generate_random()
                print(f"Verifier >> c: {c}")
                await websocket.send(str(c))

                next_message = await websocket.recv()
                print(f"Verifier <<: {next_message}")
                z, u = next_message.split(':')

                do_they_know = verify(int(z), _h, int(u), c)
                response_message = "You know" if do_they_know else "You're lying"
                print(f"Verifier >>: {response_message}")
                await websocket.send(response_message)
            else:
                # Broadcast received message to all connected clients
                for client in clients:
                    if client != websocket:
                        await client.send(message)
    finally:
        # Unregister client on disconnect
        clients.remove(websocket)

async def main():
    async with websockets.serve(echo, "localhost", 6789) as server:
        print("Server started on ws://localhost:6789")
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
