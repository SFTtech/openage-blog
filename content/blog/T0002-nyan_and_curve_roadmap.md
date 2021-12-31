Title: T2: Curve and nyan roadmap
Date: 2018-01-25
Tags: nyan, curves, API, roadmap
Authors: jj
Summary: our next steps for integrating the event driven gamesimulation configured by nyan into openage

After a very long planning and development phase,
two of our new core components are implemented:
[nyan](https://github.com/SFTtech/nyan) and
the [curves]({filename}/blog/T0001-curves_introduction.md).

Both are designed to work together:
`nyan` provides the configuration building blocks,
the `curves` enable our tickless, event-based game engine to work.
Now, we only have to combine them in order
to run [openage](https://github.com/SFTtech/openage).


## Replacement strategy

The current simulation, which is implemented with a classic time step loop,
will be replaced by the new event based game simulation system.

The replacement will be done in several steps:

* Design of the [game state structure](https://github.com/SFTtech/openage/issues/964)
* Design of the `nyan` model (i. e. API objects) for configuring the game state structure
* Creation of a [mod pack format](https://github.com/SFTtech/openage/issues/632)
* The convert script has to create a mod pack with assets and `nyan` files from the original game
* The engine has to load mod packs and start a basic game with a moving unit
* The [new renderer](https://github.com/SFTtech/openage/pull/850) has to be combined with the new simulation core

Those steps are tracked in a [github project board](https://github.com/SFTtech/openage/projects/14).

The first step is the cleanup and merge of the [eventsystem code](https://github.com/SFTtech/openage/pull/744).
Meanwhile we think about the `nyan` API and the modpack format.

Once the eventsystem is merged, we create a [demo](https://github.com/SFTtech/openage/blob/master/doc/code/testing.md#demos),
which basically is a new `main()`.
In this, we slowly add features so game entities are instanced by `nyan`
until we have a simple standing unit (militia, for simplicity).

In order to see this on-screen, the [new renderer](https://github.com/SFTtech/openage/pull/850) has to be able to display the terrain and units.

After that, we should add create the `Movement` ability, which allows walking around.
The pathfinding can remain very stupid (like our current implementation is),
but in the future should be far more sophisticated.
It should be quite easy to improve and extend.

Likewise, we have to add [many other abilities](https://github.com/SFTtech/openage/issues/816) to the new simulation.

Once the demo is nearly as good as the current game,
we just enable it as the new main function of the game.

Sounds easy, right? Then let's do it.


## Questions

Do you have something to discuss? Visit [our subreddit /r/openage](https://reddit.com/r/openage)!

And you can reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on libera.chat
