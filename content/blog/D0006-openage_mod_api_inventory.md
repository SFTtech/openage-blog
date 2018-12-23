Title: D6: Openage modding API - Inventory System
Date: 2018-08-30
Tags: nyan, modding, API
Authors: heinezen
Summary: Ability for storing Item game entities

Our topic for today is the `Inventory` ability which allows units to store items. AoE2 only offers one item, the relic, but it is very popular in custom scenarios. Considering that other strategy games implement other and more various kinds of items, it makes sense to include a fully fledged inventory system in openage, too.

Other articles in the modding API series:

1. [Introduction]({filename}/blog/D0000-openage_mod_api_intro.md)
2. [Units, Buildings & more]({filename}/blog/D0001-openage_mod_api_game_entity.md)
3. [Abilities]({filename}/blog/D0002-openage_mod_api_ability.md)
4. [Patching]({filename}/blog/D0003-openage_mod_api_patching.md)
5. [Attack]({filename}/blog/D0004-openage_mod_api_attack.md)
6. [Bonus]({filename}/blog/D0005-openage_mod_api_bonus.md)
7. Inventory System (you're here)
8. [Too many villagers!]({filename}/blog/D0007-openage_mod_api_villager.md)
9. [Transform]({filename}/blog/D0008-openage_mod_api_transform.md)
10. [Civilizations]({filename}/blog/D0009-openage_mod_api_civ.md)
11. [Restocking farms]({filename}/blog/D0010-openage_mod_api_farming.md)

# Inventory

![Inventory ability]({static}/images/D0006-inventory.png)

The abilities for inventory management are `PickupItem`, `DropItem`, `TranferItem` and `Inventory`. The first three of these abilities interact with items in and out of the inventory, while the actual inventory is defined by an ability that is just called `Inventory`. An inventory's definition is determined by a list of `InventoryItem`s stored in the `allowed_items` attribute. Note that `InventoryItem` is different from `Item` and has a different purpose:

* `Item` is the (physical) *representation of the item in the game world*. It is a `GameEntity` and can therefore exist independently. This means it can also have its own abilities and boni.

* `InventoryItem` defines the effect of an `Item` *when it is stored in a unit's inventory*. In contrast to `Item` it cannot exist independently and all of its effects are applied to the inventory owner. `InventoryItem` always references the `Item` for which it stores the effect in its `item` member.

The benefit of modeling the inventory system like this is that the same item can have different effects for different units. We already know a situation where this is useful because a similar behavior can be observed in AoE2. When stored in a *monk's inventory*, a relic provides no boni (and even takes away some of their abilities). However, when inside a *monastery's inventory* it provides a continuous gold bonus to the player. Another more RPG-like example would be a health potion that provides 20HP when a villager consumes it, while a mighty and experienced warrior gets 100HP from using it.

By keeping `Item` and `InventoryItem` as separate API objects, we also have more options for items that are outside of an inventory and lie on the ground. Because an `Item` game entity can have its own abilities assigned, we could enable it to run away or hide from the player, summon units for its protection or just have it mind its own business by chopping trees in the woods.

# A closer look at InventoryItem

![InventoryItem examples]({static}/images/D0006-inventory-example.png)

The effects of `InventoryItem` that we briefly touched a few paragraphs before are the following: First of all, `InventoryItem` can grant a variable number of boni to the inventory owner through the `boni` set attribute. In addition to this, `InventoryItem` is allowed to take away units' abilities (through `disable_abilities`) and add entirely new ones (through `enable_abilities`). This means that a unit's abilities - like `Attack` - can potentially be swapped for better (or worse) versions of the ability.

`items_per_slot` determines how many items of the same type can be stacked in one inventory slot. In the diagram we see that `HealthPotion` can be stacked 5 times before a new slot is required. In consequence, the `ExampleInventory` can hold up to 30 health potions, while the maximum number of relics is 6. Of course, relics and health potions can be in the inventory at the same time, but every inventory slot can only be occupied by one type of item.

An interesting attribute is `conflicts`. While the `Item` specified in `item` resides in the inventory, items listed in `conflicts` cannot be there at the same time. This is useful when items are supposed to be incompatible with each other, for example a *holy relic* and a *satanic bible*. It can also be beneficial for a rudimentary equipment system where a unit is only allowed to wear one garment for each body part. Considering the complexity, an equipment system should probably have its own ability, but this is something for a future version of the API. After all, we are still making a real-time strategy engine and not an RPG\*.

Last but not least, we will show you a code example showing how storing relics from AoE2 would work with `Inventory` and `InventoryItem`.

```python
# Monk's inventory
MonkInventory(engine.Inventory):
    items = {MonkInventoryRelic}
    slots = 1

# Monk's inventory item
MonkInventoryRelic(engine.InventoryItem):
    item = Relic
    items_per_slot = 1
    conflicts = {}
    enable_abilities = {}
    disable_abilities = {Convert, Heal}
    boni = {}

# Monastery's inventory
MonasteryInventory(engine.Inventory):
    items = {MonasteryInventoryRelic}
    slots = 10

# Monastery's inventory item
MonasteryInventoryRelic(engine.InventoryItem):
    item = Relic
    items_per_slot = 1
    conflicts = {}
    enable_abilities = {}
    disable_abilities = {}
    boni = {RelicGoldBonus}
```

\* If you're interested in that though, check out [Flare](http://flarerpg.org/).

# Questions?

Our next blogpost will be about a very special and complicated unit from AoE2 - the villager, or rather the villager**s**. Tune in next week when we tame this beast and adapt its quirks to our modding API.

Any more questions? Let us know and discuss those ideas by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
