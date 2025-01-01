import sys

import modal

app = modal.App("example-hello-world")

@app.function()
def hello_world():
    print("Hello, World!")

@app.local_entrypoint()
def main():
    hello_world.local()

