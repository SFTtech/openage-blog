Title: D0: Openage modding API - Introduction
Date: 2018-07-19
Tags: nyan, modding, API
Authors: heinezen
Summary: a first draft of the openage mod API

A while ago we [introduced]({filename}/blog/T0000-nyan_introduction.md) our game configuration database language nyan. Now we present our efforts to integrate nyan into openage and to create a powerful and extensible modding API.

Other articles in the modding API series:

1. Introduction (you're here)
2. [Units, Buildings & more]({filename}/blog/D0001-openage_mod_api_game_entity.md)
3. [Abilities]({filename}/blog/D0002-openage_mod_api_ability.md)
4. [Patching]({filename}/blog/D0003-openage_mod_api_patching.md)
5. [Attack]({filename}/blog/D0004-openage_mod_api_attack.md)
6. [Bonus]({filename}/blog/D0005-openage_mod_api_bonus.md)
7. [Inventory System]({filename}/blog/D0006-openage_mod_api_inventory.md)
8. [Too many villagers!]({filename}/blog/D0007-openage_mod_api_villager.md)
9. [Transform]({filename}/blog/D0008-openage_mod_api_transform.md)
10. [Civilizations]({filename}/blog/D0009-openage_mod_api_civ.md)

# What is an API?

As you probably all know, openage is not just one game. It is intended to be a fully functional game engine that provides a *framework* for multiple RTS games. Because any game developer can start working the engine and we cannot anticipate how they want to use it, it wouldn't be smart to have every tiny bit of game logic hardcoded. Instead, the engine should only implement general behavior and provide an *interface* for game developers. That's where the API comes into place.

An API, also known as an *application programming interface*, is a method of exposing an engine's functionality to its users (in our case: developers and modders). Engines can implement several APIs that give access to a variety of functionality, like scripting or adding GUI elements. This blogpost will solely focus on the *modding API* which is used for defining game data.

Developers usually take the API first and then use it to derive special cases they want for their game. You may wonder how this derivation process works exactly. We are going to look at a very simple example.

## API example

![API example 1]({filename}/images/D0001-API-example-1.png)

In this example the engine has defined a function that lets a unit run around on a map and displays their name and HP when it is selected. The function takes a very simple API object called `Unit` as input. `Unit` objects must have the attributes `name` (as a text value) and `hp` (as an integer value), but the exact value of these attributes is up to the developer. By setting the value, the special cases are derived.

![API example 2]({filename}/images/D0001-API-example-2.png)

The above diagram shows how units for a medieval game could be defined. A developer derived the three units `Swordsman`, `Spearman` and `Knight` from the generic API object `Unit` by assigning specific values to the attributes. The engine will handle all special cases like it will handle `Unit`, but takes their specific values into account. For example, if a `Knight` is selected, it will display *Knight* as the name and *120* as the HP.

A developer with a different game in mind can also utilize the API to define completely different special cases.

![API example 3]({filename}/images/D0001-API-example-3.png)

This would also be an viable use for the API when a developer wants to have a more modern setting in their game.

You might wonder if the derived objects from the two games could be used simultaneously. The answer is yes, they can!

![API example 4]({filename}/images/D0001-API-example-4.png)

In this API design the engine essentially does not care that the theme of the medieval and the modern units is vastly different. As long as they use the same API they can be used in any combination, even if it does not make much sense. For a modding community this kind of API design is a huge benefit because it is very easy to extend, replace and combine mods.

We will later see how the openage modding API handles things in a similar manner, albeit the design is much more complex.

# API Overview

The UML diagram below shows the latest draft of our API and should be very close to what will be implemented in the next months.

![API overview]({filename}/images/D0001-API-overview.png)

If you are familiar with Age of Empires 2, you most likely spotted some similarities between the game and our API objects. Although it draws inspiration from the game, modding in openage will be completely different from modding in AoE2. The openage modding API exposes much more features and should allow for very complex mods and a range of different styles of RTS gaming.

Over the next weeks, we will have a look at specific parts of the API and explain how it can be used.

# General design decisions

To support our goal of making modding easy and keeping the API extensible we made a few major design decisions.

**Single API tree**

The whole API is part of a single object tree (or graph to be more specific). All API objects inherit implicetely or explicitely from the root object `Entity`. This will keep the hierarchy of objects consistent, even if a lot of mods are activated at once. It also allows every object to be added to a `set` with type `Entity`.

**Define units through abilities**

Units are almost entirely defined through API objects of type `Ability`. Abilities describe what a unit can *do* (e.g. `Build`, `Move`, `Research`) or what it *is* (e.g. `Creatable`, `Selectable`). Most of a unit's attributes will reside in an ability. This goes so far that `Live` itself will be an ability that stores the member `hp` and its value. Each unit stores its abilities in a set, so that they can easily be added or removed (including through patching at runtime).

Because abilities are API objects themselves, their values can be uniquely defined for each unit. For example, two different units can derive their own version of the `Move` ability and each specify different values for `speed`.

Every object that is of type `GameEntity` (e.g. units, buildings, items, trees, gold spots & more) can posess any ability. The system is very powerful and allows for

* Trees training units
* Animals converting villagers
* Relics chopping wood

and other crazy stuff.

**All game modifications are done only by patches**

nyan allows us to dynamically change objects' members at runtime by applying Patches. Everything from upgrading stats to unlocking units will be done by patching the members of an object. Any value can be changed and adjusted by a patch. Also, individual units or game entities on the battlefield can be patched individually. This will allow developers and modders to create special units from generic units at runtime.

**No replacement of units within their life cycle**

In AoE and other strategy games objects are often replaced by a new object when they switch to a new state. This can for example be observed when unit lines are upgraded or when villagers are assigned to the various gather tasks.

We cannot use that strategy for openage as patching has the potential to severely alter the member values of the unit. By replacing a unit its changes would be lost. To avoid replacing objects we have implemented a variety of solutions which will enable the objects to switch states without losing their patch history.

# Questions?

[Next week]({filename}/blog/D0001-openage_mod_api_game_entity.md) we will explain how `GameEntity`s, the objects in the game world, are handled.

Any more questions? Let us know and discuss those ideas by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
