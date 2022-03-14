Imperator
---------
A proof of concept imperative language for writing Plutus Smart Contracts.

### What is it?

This is a language (compiler) that transforms a lightweight imperative language into [pluto](https://github.com/Plutonomicon/pluto),
a language that more or less directly compiles into [Untyped Plutus Core (UPLC)](https://iohk.io/en/blog/posts/2021/02/02/plutus-tx-compiling-haskell-into-plutus-core/).

### Why is it interesting?

Unlike most programming language, Pluts does not compile down to assembly or any assembly like language.
Untyped Plutus Core is a functional programming language, which still causes headache to many programmers [[citation needed]](https://en.wikipedia.org/wiki/Wikipedia:Citation_needed).
Imperator is an attempt to compile an imperative language into a functional language, which is a rather unusual
direction but well known to be possible among theoretical computer scientist.

### Is Cardano L1 now EVM compatible??

No. Cardano L1 still works based on Smart Contracts acting as validators rather than
actors. Moreover, the state of the contract is not stored in the blockchain.
However, this project may help at convincing more people to develop on Cardano
and enrich the ecosystem.

### Show me a sample program!

Sure thing.

```imperator
function (input) {
   input = int input;
   foo = function(a){return a + 3};
   x = (1 + foo(input)) * 3;
   n = 3;
   while(0 < n){
      x = x + 1;
      n = n - 1
   }|
   return x
}
```

