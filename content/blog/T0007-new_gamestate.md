Title: New Gamestate 2020
Date: 2020-08-15
Tags: roadmap, gamestate
Authors: jj, heinezen
Summary: our next steps for integrating the new gamestate and gameplay

Over the past weeks and months, two more important engine components of the engine
have become ready to be merged. These components are the
[new gamestate](https://github.com/SFTtech/openage/pull/1066) and the
[new nyan converter](https://github.com/SFTtech/openage/pull/1151).

The integration of both components marks the beginning of a new development phase
as pretty much all major engine core parts will be set in place. We can now use
this foundation to build all gameplay-relevant features around them.


## What's the plan?

The first thing we will do is merge the new converter. In comparison to the
older code, which mainly just dumped the assets into open formats, the new converter
is able to create **modpacks** that use the **openage nyan API**. It also brings
(preliminary) **support for the other Genie games** Age of Empires 1 and Star Wars:
Galactic Battlegrounds.

Next up is the new gamestate PR. This replaces the lockstep implementation
we have used in the engine until now with an **event-driven system**. Furthermore,
it makes use of the **curve-based simulation model** that has been implemented for a
while now. Another core part that is coupled with the new gamestate is the new
**low-level renderer/presenter**.

With the integration of the new components, the old gamestate implementation will
no longer work. However, this means that the gameplay features that were implemented
along with it will no longer work! There might be a lot less visible features for
a while. We have debated about leaving the old gamestate intact, but ultimately decided
that having parallel structures in the engine is too much work and probably
confusing to outside contributors. The old gameplay logic will also not be lost,
but rather re-implemented using the paradigms of the new gamestate.


## What's the next step?

Once all the code merging, refactoring and documentation updating has been solved,
we will start to reimplement gameplay with the Entity-Component-System paradigm. With
this approach a lot of features can be added in parallel (although we can't promise
that it won't be complicated still). That also means that we do not have to
tell new contributors the phrase "you can work on anything, except gameplay"
anymore as implementing it is no longer blocked by missing egine core functionality.

For testing features, we will create a simple gameplay demo which will be
gradually expanded with new systems. It is supposed to act as a testing bed for the
implementation and will probably not model a fully-featured game at first. It's main
goal is to give players and contributors an idea of what we are doing... because
nobody wants to read long blogposts all the time, am I right? :D


## Questions

Do you have something to discuss? Visit [our subreddit /r/openage](https://reddit.com/r/openage) or pass by in **[our forum](https://openage.discourse.group/)**!

And you can reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net

