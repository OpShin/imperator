Imperator
---------

A proof of concept imperative language for writing Plutus Smart Contracts.

> This project is [applying for Cardano Catalyst Funding](https://cardano.ideascale.com/c/idea/418458). Please give feedback/assess/vote on it if you like it!

#### Official partner with [MuesliSwapTeam](https://github.com/MuesliSwapTeam/)


### What is it?

This is a language (compiler) that transforms a lightweight imperative language into [pluto](https://github.com/Plutonomicon/pluto),
a language that more or less directly compiles into [Untyped Plutus Core (UPLC)](https://iohk.io/en/blog/posts/2021/02/02/plutus-tx-compiling-haskell-into-plutus-core/).

I have given a presentation on this project at the Catalyst Swarm Idea Fest. Check it out here: https://youtu.be/1n9ftsoCLas

I have also hosted an AMA on reddit: https://www.reddit.com/r/cardano/comments/u8t7t4/i_develop_a_new_imperative_prototype_sc_language



### Why is it interesting?

Unlike most programming language, Plutus does not compile down to assembly or any assembly like language.
Plutus/Untyped Plutus Core is a functional programming language, which still causes headache to many programmers [[citation needed]](https://en.wikipedia.org/wiki/Wikipedia:Citation_needed).
However, in order for the development of Smart Contracts and dApps on the Cardano blockchain to thrive, the development of applications should be as accessible as possible.
Imperator is a solution to this, translating an imperative language into the functional language UPLC. This direction is rather unusual
but well known to be possible among theoretical computer scientists.

This translation brings many useful features in being
 - a more familiar, intuitive way of writing SCs than Plutus
 - a more secure platform for SCs than Solidity (by i.e. eliminating side effects)
 - extensible by efficiently written libraries

### Is Cardano L1 now EVM compatible??

No. Cardano L1 still works based on Smart Contracts acting as validators rather than
actors. Moreover, the state of the contract is not stored in the blockchain.
However, this project may help at convincing more people to develop on Cardano
and enrich the ecosystem.

### How does it work?

First you write a small program in imperator.

```imperator
main := function (b) {
   b := int(b);
   foo := function(a){return a + 3};
   x := (1 + foo(b)) * 3;
   n := 3;
   while(0 <i n){
      x := x + 1;
      n := n - 1
   }
   return x
}
```

This compiles into the following (rather unwieldy) pluto code,
using the compiler provided in this repository.

```bash
$ python3 imperator.py compile examples/showcase.imp
(\s -> (\x -> if (x ==b 0x6d61696e) then ((\s -> (\p0 -> (\s -> s 0x78) ((\s -> (\s -> (\s -> (\s -> (\s -> let g = (\s f -> if ((\s -> (((\s -> 0) s) <i ((\s -> s 0x6e) s))) s) then f ((\s -> (\s -> (\x -> if (x ==b 0x6e) then ((\s -> (((\s -> s 0x6e) s) -i ((\s -> 1) s))) s) else (s x))) ((\s -> (\x -> if (x ==b 0x78) then ((\s -> (((\s -> s 0x78) s) +i ((\s -> 1) s))) s) else (s x))) s)) s) f else s) in (g s g)) ((\s -> (\x -> if (x ==b 0x6e) then ((\s -> 3) s) else (s x))) s)) ((\s -> (\x -> if (x ==b 0x78) then ((\s -> (((\s -> (((\s -> 1) s) +i ((\s -> (s 0x666f6f) ((\s -> s 0x62) s)) s))) s) *i ((\s -> 3) s))) s) else (s x))) s)) ((\s -> (\x -> if (x ==b 0x666f6f) then ((\s -> (\p0 -> (\s -> (((\s -> s 0x61) s) +i ((\s -> 3) s))) ((\s -> s) (\x -> if (x ==b 0x61) then p0 else ( (s x)))))) s) else (s x))) s)) ((\s -> (\x -> if (x ==b 0x62) then ((\s -> UnIData ((\s -> s 0x62) s)) s) else (s x))) s)) (\x -> if (x ==b 0x62) then p0 else ( (s x)))))) s) else (s x))) (\x -> (!Trace "VNI" (Error ()))) 0x6d61696e
```

And produces the following output
```bash
$ pluto run showcase.pluto 5

ExBudget
--------
ExBudget {exBudgetCPU = ExCPU 31725354, exBudgetMemory = ExMemory 84924}

Result
------
Constant () (Some (ValueOf integer 30))
```

You can check that this is the expected output by comparing it to the directly
evaluated program.

```bash
$ python3 imperator.py eval examples/showcase.imp 5
30
```


### How can I support this?

Of course contributions are a very welcome way of support, be it ideas or code. I also made this a Cardano Catalyst proposal, so voting for it to be funded would be the biggest help possible! Check it out:

https://cardano.ideascale.com/c/idea/418458

