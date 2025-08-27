# zk web socket


## Start the server

Start the server via `python3 server.py` in one tab or process.


## Make a commitment

Open another tab and run the prover with a commitment of your secret.

```bash
python3 prover.py commit 25121984
```

Note that here `25121984` is the secret and it is not sent to the server, but instead a public key is sent.
The server stores the public key.

## Verify you know

Then when you're ready to prove that you know the secret without sharing the secret run the following:

```bash
python3 prover.py verify 25121984
```

Note that again the secret is not sent to the server and remains on the client only.


## Example

Start the server.

```bash
$ python3 server.py
```

Make a commitment.

```bash
$ python3 prover.py commit 738921739817238219
Prover >> h: 63256057
```

Try to verify with an incorrect value.

```bash
$ python3 prover.py verify 738921739817238218
Prover <<: 64535033
Prover >>: 47686338863522884105868151:854135080
Prover <<: You're lying
```

And then try again with the real value.

```bash
$ python3 prover.py verify 738921739817238219
Prover <<: 18948837
Prover >>: 14001707603553258651983367:1682093897
Prover <<: You know
```


## Dependencies

Note it requires `websockets`:

```bash
pip3 install websockets
```
