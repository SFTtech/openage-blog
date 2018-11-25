Title: D7: Openage modding API - Too many villagers!
Date: 2018-09-06
Tags: nyan, modding, API
Authors: heinezen
Summary: Villagers and their gathering abilities, animations and gender

If we would ask AoE2 players how many villager units there are in the game files, most would probably answer one or two, depending on whether they consider female and male version as separate units. In reality, the AoE2 game data contains a total of 22 different villager units; enough for them to play their own football game. This seems a bit much, so maybe there is some redundancy that we can get rid of.

Other articles in the modding API series:

1. [Introduction]({filename}/blog/D0000-openage_mod_api_intro.md)
2. [Units, Buildings & more]({filename}/blog/D0001-openage_mod_api_game_entity.md)
3. [Abilities]({filename}/blog/D0002-openage_mod_api_ability.md)
4. [Patching]({filename}/blog/D0003-openage_mod_api_patching.md)
5. [Attack]({filename}/blog/D0004-openage_mod_api_attack.md)
6. [Bonus]({filename}/blog/D0005-openage_mod_api_bonus.md)
7. [Inventory System]({filename}/blog/D0006-openage_mod_api_inventory.md)
8. Too many villagers! (you're here)
9. [Transform]({filename}/blog/D0008-openage_mod_api_transform.md)
10. [Civilizations]({filename}/blog/D0009-openage_mod_api_civ.md)
11. [Restocking farms]({filename}/blog/D0010-openage_mod_api_farming.md)

# Divide..

Before we actually start working on the redundancy problem, we have to find out why the game data defines so many villagers. Obviously, Ensemble did not intend to make their units play football matches, [did they](https://www.youtube.com/watch?v=NHEFPENBV-s)\*? As it turns out, the game contains this many villagers because units in AoE2 are only able to have five animated abilities.

1. Action (for most units this is an attack)
2. Idle
3. Move
4. Die
5. Decay (this is not resource decay, but corpse decay)

This system works fine for military units, but creates trouble for villagers because they need more than one *Action* to support all the types of gathering they do. AoE2 supports 8 different forms of gathering resources which, together with attacking, building and repairing, amounts to 11 *Actions* a villager is required to support. So to solve this dilemma, Ensemble created a unique villager unit for every one of these *Actions* (twice, because villagers come in two genders) and makes the game switch between them at runtime depending on the *Action* that is currently needed. In addition to this, they also gave each of these villager units their own idle, move, die and decay animations that add a lot of visual variety.

When we look at the game data in more detail, we see that the villager is not the only unit that is handled like this. Monks and trade carts are also units that have more than one unit defined in the original game data to make them support more animations, although the villager is the most extreme example.

While this implementation certainly works for Age of Empires, there are several reasons why this design is not great. First of all, it adds a lot of redundancy just to change some of the animations. Values for HP, speed and other stats stay exactly the same for each unit, yet have to be redefined twenty-two times in the game data. Secondly, the ingame transitions between the villager types need to be hardcoded in the engine. This would likely mean that we would have to restrict modders that use the openage API to a specfific number of resources and gathering types, which is an unacceptable requirement for us. Finally, replacing different villager units at runtime "on-the-fly" is prone to consistency problems. In openage, units can be more individual than in the Genie Engine and it is very difficult to keep this individuality when replacing them. Ideally we would want the *Action*s and alternative animations to be part of a single villager unit.

# .. and Conquer

Our first advantage is that game entities in the openage API are not limited to five animated abilities. Therefore, we can assign all of the 11 villager-specific actions directly to one unit without much effort. However, we also need a way to include the related move, idle, die and decay animations that the individual villager units had for each type of *Action*. We can do so with the `CommonAnimationOverride` object.

![CAO object API]({filename}/images/D0007-cao-common.png)

`CommonAnimationOverride` is an API object that any `Abiliy` can inherit from. By doing this, the unit's default animations from the `Move`, `Idle`, `Die` and `Decay` abilities will be temporarily overriden with the ones from `CommonAnimationOverride` until:

* any animated ability other than `Move`, `Idle`, `Die` or `Decay` is executed **or**
* another ability inheriting from `CommonAnimationOverride` is used

In practice this means an ability can indicate it wants to temporarily replace the animations of the four "common" abilities mentioned above. The example below shows how this would look for the villager ability `Forage`.

![CAO Forage Example]({filename}/images/D0007-cao-common-example.png)

It is important to note that inheriting from `CommonAnimationOverride` is entirely optional and all abilities should generally work fine without being of this type. It is also not limited to typical villager abilities like `Gather`, `Build` or `Repair`. For example, another unit that can make use of it is the trade cart with its `Trade` ability. In fact, any ability is allowed to inherit `CommonAnimationOverride`, even though it doesn't make sense for all of them.

# More alternative animations

![Carry animations example]({filename}/images/D0007-cao-carry-villagers.png)

Having `CommonAnimationOverride` is still not enough because all gathering abilities have second alternative animations for `Move` and `Idle`. These are used as *carrying* animations and replace their default counterparts as soon as the amount of resources carried by the villager exceeds 20% of their resource capacity. The way we can handle this is very similar in its mechanics to `CommonAnimationOverride`: We just inherit from a second API override object called `CarryAnimationOverride`.

![Carry animation override]({filename}/images/D0007-cao-carry.png)

By inheriting from `CarryAnimationOverride`, an ability is able to provide alternative animations for `Move` and `Idle`. The alternative animations replace the default ones when the carried resource amount passes the `carry_threshold` which should be a floating point number between 0 and 1, indicating the percentage at which the threshold is reached. It only works with abilities that make a game entity carry something, so it is best suited to be used with `Gather`, `Transport`, `ProvideGarrison` and `Inventory`. Even though it is not an ability, `InventoryItem` is be allowed to inherit from it, too. This makes it possible for items like the relic to give a unit a unique carry animation.

`CarryAnimationOverride` can be used in combination with `CommonAnimationOverride`. In this case, if the carry threshold is reached, the move and idle animations from `CarryAnimationOverride` always take precedence over the definitions from `CommonAnimationOverride`.

# Variants add variety (and genders)

So far we've only seen how abilities activate alternative animations, but we haven't covered how animations change depending on a villager's gender. It turns out this actually sounds harder than it is because in AoE2 genders are decided at creation time and don't change after that. Well, at least they don't by gathering and building. This means we can simply patch in the animation set for each gender before the unit is created. We do so by utilizing a so called `Variant` of the unit.

![Variants]({filename}/images/D0007-variants.png)

A `Variant` object contains a number of patches that are applied to the unit on creation. Which variant is chosen depends on the type of the `Variant` objects. A `RandomVariant` has a chance to be chosen at random (which perfectly fits for our villagers), while `PerspectiveVariant` depends on the angle the game entity is viewed. The latter variants are particularly useful for walls which have to cover up to 8 different angles. Other variant types could be introduced by us later, if there's a demand.

Variants are not restricted to graphical changes and can patch pretty much every attribute of a game entity, e.g. add new abilities or change the attributes of existing ones. Therefore modders should be able to implement a lot more crazy ideas for unit variety than just alternative animations.

# Questions?

Next time we will discuss everyone's favorite siege unit and the implications it has for the API.

Any more questions? Let us know and discuss those ideas by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net

\* The sport depicted is obviously not **foot**ball because the monks never use their feet. It actually is a special form of [gridiron](https://en.wikipedia.org/wiki/Gridiron_football) which tries to make up for the lack of feet by making the rules more complicated and running more commercials.
