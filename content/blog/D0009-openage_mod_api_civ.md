Title: D9: Openage modding API - Civilizations and Uniqueness
Date: 2018-09-20
Tags: nyan, modding, API
Authors: heinezen
Summary: Civilizations bring variety into games and add asymmetry

Civilizations (also called *Factions* or *Races* in other games) are a concept as old as Dune 2. Their purpose is to add strategic complexity by inserting a layer of asymmetry to a game, thus enabling a variety of unique play styles and increasing replayability. How we are handling this and how much complexity we can add with the openage modding API is our topic for today.

Other articles in the modding API series:

1. [Introduction]({filename}/blog/D0000-openage_mod_api_intro.md)
2. [Units, Buildings & more]({filename}/blog/D0001-openage_mod_api_game_entity.md)
3. [Abilities]({filename}/blog/D0002-openage_mod_api_ability.md)
4. [Patching]({filename}/blog/D0003-openage_mod_api_patching.md)
5. [Attack]({filename}/blog/D0004-openage_mod_api_attack.md)
6. [Bonus]({filename}/blog/D0005-openage_mod_api_bonus.md)
7. [Inventory System]({filename}/blog/D0006-openage_mod_api_inventory.md)
8. [Too many villagers!]({filename}/blog/D0007-openage_mod_api_villager.md)
9. [Transform]({filename}/blog/D0008-openage_mod_api_transform.md)
10. Civilizations (you're here)
11. [Restocking farms]({filename}/blog/D0010-openage_mod_api_farming.md)

# Initial requirements

Throughout the history of strategy games, a lot of different ways to implement civilizations have evolved. In some games factions distinguish themselves only by a difference in unit stats, e.g. in *Empire Earth*, while others make them entirely unique (*Starcraft* being a prime example) with individual units, techs and strategies built around them. The *Age of Empires* series occupies some kind of middle ground in which each civilization uses a subset of a shared tech tree in addition to a few economic and military boni for each civ. Of course, other strategy games introduced many related flavors for their faction systems that come with their own quirks.

To support all these levels of uniqueness, we need a system that is flexible and easy to adjust. We would also like it to still be easily moddable, so that graphical and balance changes can be made by the community. Fortuately for us, nyan makes both of these requirements really easy to fulfill.

# Upgrades and unlocks in openage

Before we begin explaining how civilizations are implemented, we should do a quick recap on how upgrades and unlocks are realized in openage. On a technical level every upgrade in a game is defined as a bundle of [patches]({filename}/blog/D0003-openage_mod_api_patching.md) which modify the game entities that are currently available. In turn most upgrades are unlocked by other upgrades and were therefore also patched in at some point. This basically means that any uprade is the result of a series of patch bundles which can be traced back to one starting configuration. For example, the upgrade from spearman to pikeman is a result of these events:

1. Starting configuration: *Dark Age* buildings, units, techs are available
2. Researching `FeudalAgeTech` patches `CastleAgeTech` into `Research` ability of town center
3. Researching `CastleAgeTech` patches `PikemanTech` into `Research` ability of barracks
4. Researching `PikemanTech` patches graphics, name and attributes (HP (+10), attack damage (+1), etc.) of `Spearman`

The way we unlock `PikemanTech` is implicitely defined through the previous techs and the starting configuration. It is also important to stress that the upgrade path is not fixed and could just as well look like this:

1. Starting configuration: *Dark Age* buildings, units, techs are available
2. Researching `FeudalAgeTech` patches `WoodenStaffTech` into `Research` ability of blacksmith
3. Researching `WoodenStaffTech` patches `PointyStickTech` into `Research` ability of blacksmith
4. Researching `PointyStickTech` patches `PikemanTech` into `Research` ability of barracks
5. Researching `PikemanTech` patches graphics, name and attributes (HP (+10), attack damage (+1), etc.) of `Spearman`

This is benefical for two major reasons. For one it allows techs or units to be unlocked in different ways, which is always cool. But more importantly it shows that a tech's functionality is independent from its unlock path. Sure, `PikemanTech` has to be unlocked at some point, but it doesn't matter if `CastleAgeTech` or `PointyStickTech` did it. In consequence, this means that any of these five steps on the unlock path -- including the starting configuration -- can be altered individually without breaking the engine logic.

## Civilizations

But what does this have to do with the uniqueness of civilizations? It turns out that any unique property of a civilization is just a change of a step on the unlock path. And because we are able to alter every individual step without dangerous consequences, we can change pretty much anything we want. The civilization setup is practically a 0th step that comes with its own changes which again are introduced by patching.

Let's say we want to have a civilization that grants every pikeman of this civ 5 more HP than the "standard" pikemans have. We do so by patching the patch from `PikemanTech` that upgrades HP to give another 5 points of health.

```python
# The tech holds all the necessary patches for the upgrade
# from spearman to pikeman, including the patch for HP.
PikemanTech(engine.Tech):
    updates = o{HPforPikeman, ...}

# This is the standard HP increase for pikeman that
# patches the Live ability of Spearman units to gain
# 10 more HP.
HPforPikeman<engine.Live>(engine.Patch):
    hp += 10

# With this addition, we patch the standard HP increase patch
# to give an additional 5 HP.
CivAdditionalHP<HPforPikeman>(engine.Patch):
    hp += 5
```

In the series of events that leads to the research of `PikemanTech`, the application of `CivAdditionalHP` is part of the 0th step we talked about earlier.

0. Civ setup: `CivAdditionalHP` patches `HPforPikeman` from `PikemanTech` to grant an additional 5 points of health
1. Starting configuration: *Dark Age* buildings, units, techs are available
2. Researching `FeudalAgeTech` patches `CastleAgeTech` into `Research` ability of town center
3. Researching `CastleAgeTech` patches `PikemanTech` into `Research` ability of barracks
4. Researching `PikemanTech` patches graphics, name and attributes (**HP (+15)**, attack damage (+1), etc.) of `Spearman`

Of course, as the unlock path of `PikemanTech` itself consists of patches we are able to change them, too. For example, we can have `PikemanTech` unlocked in Feudal instead of Castle Age.

```python
# The standard Feudal upgrade which unlocks the tech for Castle Age
FeudalAgeTech(engine.Tech):
    updates = o{CastleAgeUnlock, ...}

# On the standard unlock path CasteAgeTech enables PikemanTech
CastleAgeTech(engine.Tech):
    updates = o{PikemanTechUnlock, ...}

# A new patch puts the unlock for pikeman into Feudal..
CivMovePikeToFeudal<FeudalAgeTech>(engine.Patch):
    updates += {PikemanTechUnlock}

# ..and removes it from Castle
CivRemovePikeFromCastle<CastleAgeTech>(engine.Patch):
    updates -= {PikemanTechUnlock}
```

We essentially removed one intermediate step on the unlock path.

0. Civ setup: `CivMovePikeToFeudal` patches `PikemanTechUnlock` into `FeudalAgeTech`
1. Starting configuration: *Dark Age* buildings, units, techs are available
2. Researching `FeudalAgeTech` patches `PikemanTech` into `Research` ability of barracks
3. Researching `PikemanTech` patches graphics, name and attributes (HP (+10), attack damage (+1), etc.) of `Spearman`

When we handle things this way, we end up with a very flexible system that allows us to uniquely define how a game is played with a civilization. One faction might unlock the pikeman by researching Feudal Age, another one by researching Imperial Age. Keep in mind that we don't even need age upgrades for unlocks, `PikemanTech` might as well be unlocked by Forging or another not so important tech. The starting configuration can also be changed easily because it just represents the game data before any patches have been applied. The civilization setup can alter it the same way we did with the other steps.

The question that remains is whether this system still allows for easy modding. When we look at any unlock path, we see that the 0th step is nothing special and essentially the same as the others: The use of patching to alter attributes. Similar to how we added the 0th step for "Civ Setup", we can introduce another step that comes even before the 0th step. This step would be able to change all subsequent steps, including "Civ Setup". Such a preliminary step would be exactly what a data mod is. And because mods are also a bundle of patches, we can have a step before each mod, which would also be a mod that allows a preliminary step that would again be a mod... (repeat indefinitely)

## API description

![Civilization API]({static}/images/D0009-civ-api.png)

All of a civilization's individual properties are handled by the `Civilization` API object. `Civilization` defines various attributes for its name and ingame help, the names of civilization leaders and its starting resources. `boni` is meant for civilization specific `Bonus` objects that are not bound to game entities or techs, such as the vietnamese bonus that reveals the starting positions of enemy players on the map. Everything concerning uniqueness of the civilization is handled by three patch bundles `civ_setup`, `graphics_set` and `team_setup`. They will be applied in the "0th step" we mentioned previously.

* **civ_setup**: Contains all patches for civ specific data changes, excluding graphical setup
* **graphics_set**: Contains all graphical changes for game entities
* **team_setup**: These patches are applied to the player of the civilization **and** their allies

All patches together define the unique properties of the civilization.

# Questions?

Any more questions? Let us know and discuss those ideas by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
