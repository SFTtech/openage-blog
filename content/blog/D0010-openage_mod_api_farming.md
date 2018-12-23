Title: D10: Openage modding API - Restocking farms
Date: 2018-11-25
Tags: nyan, modding, API
Authors: heinezen
Summary: Renewable resources in openage with farming as an example

Food takes quite an unusual role in the AoE economy as its main harvesting source from the mid-game onwards - the farm - is a *renewable* resource spot. Other than the natural resources that are generated with the map, the farming economy relies on the constant reconstruction of the production building by the player. In this blogpost we will explain how resource spots can be restocked in openage and also how we implement the process of queueing farms in the mill.

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
10. [Civilizations]({filename}/blog/D0009-openage_mod_api_civ.md)
11. Restocking farms (you're here)

# Preliminary analysis

Before go into detail about the concrete API implementation, we should make clear how the farming economy from AoE2 works on an abstract level. For that purpose we prepared a simple diagram.

![Farming BPMN]({static}/images/D0010-farm-bpmn.svg)

Note that we leave out unimportant aspects such as delivering food to a drop site or deleting the building. We focus solely on the standard life cycle of the farm. A stylized hand indicates that the task is initiated by the player through the GUI, while tasks with a stylized person are automatically executed by a villager.

As seen above, the process of harvesting a farm can be divided into these steps:

* A farm's life cycle starts with the player placing and constructing it (needs 60 wood) with a villager.
* One villager (more are not allowed) gathers food from the farm until it is depleted.
* Then one of three scenarios can happen:
    1. There is a farm queued in the mill at the moment the farm depletes. In this case, the villager automatically rebuilds it and 1 farm is removed from the queue. They automatically resume gathering. This is a feature introduced in the first expansion *The Conqueror's*.
    2. The player rebuilds the farm manually by right-clicking on it with a villager. This will cost them 60 wood. They automatically resume gathering.
    3. If 3 minutes of ingame time passed, no farm was queued and the player did not manually rebuild the farm, the depleted farm is deleted.

# Streamlining the process

One problem that remains is that the process described in the previous section is still very specific to farms. As we are writing an API, we would like to generalize it as much as possible. Particularly, we would like to fulfill these requirements:

1. Restocking resources should be possible for every `ResourceSpot`, not just farms. Trees and berry bushes are candidates where renewability would make sense.
2. Similar to what we said in previous blogposts, the game entity containing the `ResourceSpot` should not be replaced when we restock it. The action should only refill the resources.
3. Queuing restocks should also be very easy to control through the API. Modders should have the option to enable and disable automatic restocks.

With this in mind, we can now look at the API implementation.

## Restock

![Restock API object]({static}/images/D0010-restock-api.png)

There are two abilities involved in the restocking process. On the left side we have the ability `Harvestable` of the farm, which contains the `ResourceSpot` that villagers can gather from. Villagers get the `Restock` ability with which they can fill up the resources again.

`Restock` targets a specilization of `ResourceSpot` which is called `RestockableResourceSpot`. A restockable resource spot works like a normal resource spot, except that it is not immediatly destructed after the resources are harvested. Instead, it will be *depleted* until it is either restocked or the time set in `destruction_time_limit` has run out. We can also decide with `auto_restock` whether queued/automatic restocks are allowed. The two sets of `Progress` objects contain graphics that are used when a certain percentage of restocking is complete. It is important to stress that normal `ResourceSpot`s can be turned into `RestockableResourceSpot`s through patching.

The `Restock` ability can be used on a restockable resource spot after its contents are depleted. Though its attributes look very similar to those of `Build`, the two abilities operate completely independent from each other. `Restock` is only concerned about the resource spot it is supposed to refill (`target`) and will not reconstruct the whole building. The necessary time to restock is stored in `restock_time`. We can also set the `amount` of resources that should be restocked. The costs for a restock action is split into two options: `manual_cost` is used when the player initiates the restock (like right-clicking on a depleted farm), while `auto_cost` is used when villagers automatically execute the restock, provided the resource spot allows this. Both costs can be the same, but it can be handy to set them to different values as we will see now.

## Queuing farms

When we implement our `Restock` ability for the resource spot of AoE2 farms, we have to initialize `manual_cost` and `auto_cost`. The naïve approach would be to interpret both cases as "build farm" actions and set both values to 60 wood. But this would not suffice. As we can see in our first diagram, the automatic restock does not really cost 60 wood, it costs one farm from the queue in the mill. That begs the question of how we actually queue farms. Fortunately for us, it turns out to be quite trivial. 

First of all, the farm queue does not exactly represent buildings. It is probably closer to a "I can rebuild my farm"-ticket for the villager. Secondly, these tickets are available to all villagers and are not tied to a specific mill. They can be used from everywhere on the map on a first-come, first-serve basis. If you think about it, these tickets work like the other four resources in the game, with the exception that they cannot be gathered by the villagers. Thus, we are going to interpret the elements in the queue as actual resources. We will introduce a fifth `Resource` called `FarmRestockResource` which will work exactly like `Food`, `Wood`, `Gold` and `Stone`.

![TradeResource API]({static}/images/D0010-trade-resource-api.png)

Since `FarmRestock` will probably not be gatherable on the map (although that is possible), we have to find another way to acquire it. For that purpose, we can use the `TradeResource` ability which is also used for selling and buying with the market. In the context of farming, the mill will get a `TradeResource` ability which sells 60 units of `Wood` for 1 unit of `FarmRestockResource`. We can then set `auto_cost` in the villager's `Restock` ability to 1 unit of `FarmRestockResource` which is therfore consumed whenever a villager automatically restocks a farm.

# Questions?

Any more questions? Let us know and discuss those ideas by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
