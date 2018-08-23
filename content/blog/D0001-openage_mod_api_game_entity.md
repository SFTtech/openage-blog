Title: D1: Openage modding API - Units, Buildings & more
Date: 2018-07-26
Tags: nyan, modding, API
Authors: heinezen
Summary: About the representation of game world objects

Last week we explored the overall principles and design decision for our modding API. This time we will see how the definition of units, buildings and other visible objects in the game world will work.

Other articles in the modding API series:

* [Introduction]({filename}/blog/D0000-openage_mod_api_intro.md)
* Units, Buildings & more (you're here)
* [Abilities]({filename}/blog/D0002-openage_mod_api_ability.md)
* [Patching]({filename}/blog/D0003-openage_mod_api_patching.md)
* [Attack]({filename}/blog/D0004-openage_mod_api_attack.md)
* [Bonus]({filename}/blog/D0005-openage_mod_api_bonus.md)

# GameEntity

![GameEntity]({filename}/images/D0001-game-entity-overview.png)

Everything that *visibly exists* and *independently operates* in the simulated game world can be modelled with the `GameEntity` API object. This classification includes almost everything that moves, stands around or generally does things on the map. Projectiles are an exception because they need a `GameEntity`, e.g. a unit, to be spawned, thus violating the *independent* property. They also have some special features that differentiate them from `GameEntity`. These will be discussed in another blogpost dedicated to ranged attacks.

`GameEntity` requires very few attributes to be defined. Only name, description, helptext, an icon and some information about the hitbox (stored in the three `radius_` members) are strictly necessary. The other attributes of each game entity are defined through `Ability` objects which are stored in the `abilities` member. By adding abilities, game entities gain their main features, like animations, hp, attack damage and more. Two other set members `variants` and `boni` exist and are able to specialize a game entity even more. However, we will come back for them at a later date to not complicate this blogpost further.

Developers and modders should not let their objects inherit directly from `GameEntity` and instead choose one of the four child objects `Unit`, `Ambient`, `Item` or `Building`. With the exception of `Building` these objects are just for categorization and don't require additional attributes to be defined. An `Item` object could have the same abilities as a `Unit` object \*. However the categorization helps us, the engine developers, because we are able to design abilities that are aimed at a specific category. For example, the `PickupItem` will first and foremost be designed to handle game entities of type `Item`. We'll now explain what is expected from each category.

\* *Fun fact: Because nyan allows for multiple inheritance an object can be in more than one of the categories. So if you think that your units should also be items, you can go for it!*

## Unit

`Unit` is probably the most generic category. In general, all game entities that move, die, decay and have HP should be units. In the current API design, units are the only types of `GameEntity` that can be trained with the `Train` ability.

Examples: military, villagers, animals

## Ambient

`Ambient` objects usually lie or stand around on the map and look pretty. Typically, these objects never move, do not have HP and some of them are harvestable for resources. Flags and flag attachements would also be classified as `Ambient`. In AoE2 most of these objects would be owned by the neutral player *Gaia*.

Examples: cactus, tree, gold/stone pile, mountain

## Item

These are very similar to `Ambient` objects, but can be put in an inventory. openage features an inventory system through the `Inventory` ability. Items in there can have special effects on the inventory owner, provide boni or grant new abilities.

Example: relic

## Building

![Building]({filename}/images/D0001-building.png)

Buildings are more sophisticated than the othere three categories because they have to be constructed first and need space on the map grid. Each `Building` can have construction and damage stages that are defined in a `Progress` object. `Progress` objects allow buildings to display an alternative sprite after a certain percentage of *something* is complete. The number of stages is unlimited and theoretically a building could have 100 stages of construction that each have their own graphic.

It is also allowed to define more complex buildings that consist of multiple parts by using `MultiPartBuilding`. This type acts as a container that manages several subbuildings which are allowed to have individual properties, e.g. certain abilities and boni. `MultiPartBuildings` are also useful for modelling buildings that have passable parts like the Town Center in AoE2.


# Questions?

You've chosen the perfect category for your game entities - now what? Fear no more because next time, we are finally introducing the Ability system that gives them a purpose.

Any more questions? Let us know and discuss those ideas by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
