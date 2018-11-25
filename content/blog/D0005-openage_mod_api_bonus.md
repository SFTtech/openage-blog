Title: D5: Openage modding API - Bonus
Date: 2018-08-23
Tags: nyan, modding, API
Authors: heinezen
Summary: Boni are the second customization option for game entities

So far the only customization option we discussed were abilities. However, there's a second option that we brushed before: The `Bonus` API objects.

Other articles in the modding API series:

1. [Introduction]({filename}/blog/D0000-openage_mod_api_intro.md)
2. [Units, Buildings & more]({filename}/blog/D0001-openage_mod_api_game_entity.md)
3. [Abilities]({filename}/blog/D0002-openage_mod_api_ability.md)
4. [Patching]({filename}/blog/D0003-openage_mod_api_patching.md)
5. [Attack]({filename}/blog/D0004-openage_mod_api_attack.md)
6. Bonus (you're here)
7. [Inventory System]({filename}/blog/D0006-openage_mod_api_inventory.md)
8. [Too many villagers!]({filename}/blog/D0007-openage_mod_api_villager.md)
9. [Transform]({filename}/blog/D0008-openage_mod_api_transform.md)
10. [Civilizations]({filename}/blog/D0009-openage_mod_api_civ.md)
11. [Restocking farms]({filename}/blog/D0010-openage_mod_api_farming.md)

# Motivation

As establihed previously, each `Ability` in the API is linked to an engine function where its behavior is defined. On the one hand this is a benefit because we know exactly what a unit can do when we give it the ability. On the other hand there could be an ingame situation where we want the ability to do something slightly different, an *edge case* so to speak.

An example for this is the elevation factor in the damage calculation in AoE2. When two units are on the same elevation level the damage they do and receive is calculated normally. But when the elevation level different, the unit on a higher elevation level will suddenly do 25% more damage, while the opponent does 25% less. The elevation factor is examplary for an edge case behavior that we want to cover in our API with the `Bonus` object.

# Ability and Bonus relation

On an implementation level, `Ability` and `Bonus` are quite similar. Every `Bonus` provides a link to behavior hardcoded in the engine. The key difference however, is the purpose they are used for:

* Abilities define **general behavior** of a `GameEntity`.
* Boni apply under **certain conditions** or in **certain situations**. They are not limited to `GameEntity`.

So unlike abilities, which are usually always available to a unit, a bonus requires a condition to be fulfilled or a situation to occur. Then and only then do they have an impact on the game.

Taking the previous example about elevation the process for handling a bonus would roughly look like this: On execution of the `Attack` ability the engine checks if the units has any corresponding boni assigned. After that it checks whether the conditions of these boni apply. If they apply, the values in the engine function's calculation are modified accordingly.

![Bonus and objects that use it]({filename}/images/D0005-bonus.png)

Each `GameEntity` can have an unlimited number of boni assigned in the `boni` member. Other objects, like `Civilization` or `Cheat`, are also allowed to store boni.

Until now we've only talked about boni in the context of (damage) modifiers. In practice, a bonus can do much more, e.g. a map reveal (cheats) or providing a flow of resources (relics). A `Bonus` object does not necessarily have to alter an ability. This versatility is a requirement to a certin degree as `Bonus` objects should be able to cover a lot of different edge cases by definition.

While AoE2 has some applications for boni, it really are its successors Age of Mythology and Rise of Nations who make them an integral part of the game. In AoM relics can provide very unique boni, ranging from cheaper upgrades to automatically producing units for the player at the temple. RoN offers the player boni for building wonders and harvesting unique resources. These mechanics could act as a blueprint on what boni will be implemented into the API by us over time.

It is important to note that `Bonus` is **not** the same as what the Age of Empires community colloquially refers to as *attack bonus* or *civilization bonus*. Most of these are not conditional and only change data. For these cases of application, nyan patching is suited much better.

# Unconditional Bonus

We have established before that `Bonus` objects are conditional, but sometimes it might be beneficial when the mere presence of the bonus is condition enough for its application. This especially concerns boni that are percentage-based.

Consider a civilization that gives cavalry `10%` more health in Feudal Age, `15%` more in Castle Age and `20%` more in Imperial Age. We could do this through patching, but it does not look nice.

```python
FeudalHPUpgrade<engine.Live>(engine.Patch):
    # increase HP by 10% or 110/100
    # all is still fine
    hp *= 1.1
    
CastleHPUpgrade<engine.Live>(engine.Patch):
    # here the problems begin. To get
    # from 10% to 15%, we need to calculate
    # 115/110 which is
    hp *= 1.045454545

ImperialHPUpgrade<engine.Live>(engine.Patch):
    # Last but not least, to get from 10%
    # to 15%, we need to calculate 120/115
    hp *= 1.043478261
```

Not only is this very unreadable, it's also prone to rounding errors. We can improve it, if we model it with a `Bonus`.

```python
# We define bonus...
CavHPBonus(engine.Bonus):
    modifier = 1.1

# ... and add it in Feudal Age to get 10% more HP
FeudalHPUpgrade<engine.GameEntity>(engine.Patch):
    boni += {CavHPBonus}

# In Castle/Imperial Age, we increase the Bonus
CastleAndImperialHPUpgrade<CavHPBonus>(engine.Patch):
    modifier += 0.05
```

Much better to read for a human.

# Questions?

Next time we are going to investigate abilities again by taking a look at the `Inventory` ability.

Any more questions? Let us know and discuss those ideas by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
