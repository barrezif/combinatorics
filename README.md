A jumbled mess of code I've written over the course of the past year and a half.

The gist of what I'm trying to do here is evaluate useful information about other
any other players' hand by taking the current state of the game and calculating
all combinations possible from the dominoes on board/which ones we know they don't have
if they've ever skipped.

With all of the combinations, we can determine which numbers they're most/least likely to have
and can sometimes even know which exact dominoes they have.

I first wrote combinations, then combinations3 (There was probably a combinations2 somewhere that I deleted), then
Dominoes.py was my first attempt at refactoring everything. It got a bit messy, so I tried to refactor again with
the ThreeEvent program.

I haven't touched it in a while. There's a lot I still want to fix with this and I don't think I ever finished
carrying all of the logic from Dominos to the ThreeEvent file. I've got the front end part of this on
Swift. It has a whole UI and working domino game and some very rudimentary tracking stuff like which
dominoes are in the boneyard, how much control you have over a specific number, highlighting of other dominoes
of the same numbers as what you pick. I can upload that later or show you during our call.
