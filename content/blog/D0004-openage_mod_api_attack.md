Title: D4: Openage modding API - Archers don't kill units, projectiles do!
Date: 2018-08-17
Tags: nyan, modding, API
Authors: heinezen
Summary: Attack with and without projectiles

In a list of essential features for strategy games, attacking would probably be sorted in first or second place. Of course something that important should not be missing from the openage API. This time we are going to look at how units damage each other with the `Attack` ability.

Other articles in the modding API series:

1. [Introduction]({filename}/blog/D0000-openage_mod_api_intro.md)
2. [Units, Buildings & more]({filename}/blog/D0001-openage_mod_api_game_entity.md)
3. [Abilities]({filename}/blog/D0002-openage_mod_api_ability.md)
4. [Patching]({filename}/blog/D0003-openage_mod_api_patching.md)
5. Attack (you're here)
6. [Bonus]({filename}/blog/D0005-openage_mod_api_bonus.md)
7. [Inventory System]({filename}/blog/D0006-openage_mod_api_inventory.md)
8. [Too many villagers!]({filename}/blog/D0007-openage_mod_api_villager.md)
9. [Transform]({filename}/blog/D0008-openage_mod_api_transform.md)
10. [Civilizations]({filename}/blog/D0009-openage_mod_api_civ.md)
11. [Restocking farms]({filename}/blog/D0010-openage_mod_api_farming.md)

[View all articles]({filename}/blog/landing_page.md)

# Damage calculation

![Attack]({static}/images/D0004-attack-defense.png)

In the current API design, damage is dealt as a flat amount and is always directed against a specific type of armor. A single `Attack` can damage several armor types at once through the definition of `ArmorAttack` objects in the `damage` member. Every `ArmorAttack` stores the damage done against a type of armor. On execution of the attack, each damage value from `ArmorAttack` the objects of the attacker is matched against a defender's `ArmorDefense` object with the same armor type. 

It's best if we look at a simple example before explaining the system further.

![Attack Example]({static}/images/D0004-attack-example.png)

**armor_type** | **damage** | **armor_value**
---------------|------------|----------------
Melee          | 3          | 0
Pierce         | 5          | 4
Crush          | 1          | 5
Fire           | 2          | N/A

The above diagram gives us very basic definitions of one unit's `Attack` and another unit's `Defense` abilities. For convenience, a table shows the comparisons between the corresponding damage and armor values of the armor types.

The calculation for the `Melee` and `Pierce` armor types is very straight forward. `armor_value` in `ArmorDefense` is subtracted from `damage` in `ArmorAttack` which yields the following results:

```
Damage against Melee armor: 3 - 0 = 3 
```

```
Damage against Pierce armor: 5 - 4 = 1
```

The situation for the `Crush` armor type is a bit more tricky because subtracting `armor_value` from `damage` would result in a negative value. This behavior is generally undesirable as negative damage can have weird effects. Therefore, the engine will always round negative damage against an armor type up to `0`.

```
Damage against Crush armor: 1 - 5 = -4 --> rounded up to 0
```

For the last armor type we are facing another special yet common case of the damage calculation. The attacking unit has an `ArmorAttack` object for the `Fire` armor type, but the defender does not have an `ArmorDefense` object with matching armor type. Intuitively one might assume that the amount of fire damage dealt is `2`, since the defender seems to have no armor against it. However, this is not true. The engine will only calculate damage when there is an armor type match between an `ArmorAttack` and an `ArmorDefense` object. If there is no match, the damage defaults to `0`. We've already seen the correct way to give a unit no defense against an armor type when we look at `MeleeDefense`. Here any attack against `Meelee` armor does full damage because the defender has the matching armor type and `armor_value` is set to `0`.

The behavior is a bit unintuitive because it inevitably means that an attack will deal no damage when a unit has no `ArmorDefense` objects defined in `armors`, which goes against the expectations of the majority of people. On the other hand, resistances against specific types of damage can be modelled much easier.

```
Damage against Fire armor: 0
```

In the end the individual damage values are summed up and then compared to `min_damage` of the `Attack` ability. The engine chooses the greater of the two values. In this example `min_damage` was `1` which is smaller than the calculated damage value `4`. The overall damage is therefore `4`.

```
Overall damage: max(1 , 3 + 1 + 0 + 0) = max(1 , 4) = 4
```

At runtime there can be situations where the damage is modified further, e.g. because of a height advantage. But that's a story for another time. It is also important to note that openage will likely support other attack systems that use a different damage calculation, like percentage based armor or attacks with a block chance, in the future.

# Other types of Attack

![Other Attack types]({static}/images/D0004-attack-special.png)

In addition to the normal `Attack` ability, the API supports three more special versions of attacking. `AreaAttack` does area of effect damage with an optional damage dropoff over distance. The `SelfDestruct` ability is an even more special `AreaAttack` where the unit kills itself during the attack. With `RangedAttack` the attacking unit can attack from a specified distance and does not have to stand right next to the target. `RangedAttack` must not be confused with `ProjectileAttack`, since the former does not require any projectile related data.

## Shooting projectiles

![ProjectileAttack]({static}/images/D0004-attack-projectile.png)

The first striking difference between `Attack` and `ProjectileAttack` is that they are not directly related (other than the previous "special" versions of `Attack`). This is rooted in the fact that `ProjectileAttack` merely enables a unit to fire one or more projectiles. Each projectile can have its own `Attack` ability that is executed on hit. In other words: The units with `ProjectileAttack` are not doing damage, it's the projectiles they shoot.

The data for attacking with projectiles is partioned between the `ProjectileAttack` ability and the `Projectile` objects. In the ability *attack range*, *number of projectiles per attack* and of course the *projectiles* themselves are defined. Inside the `Projectile` objects we store the actual `Attack` and other related properties such as *accuracy*, whether it is fired in an *arc* or not, whether it is allowed to pass through units. This is great because it allows for a lot of customization. A unit could fire 20 different projectiles, each with individual properties and `Attack` values.

# Questions?

Although behavior for abilities like `Attack` is hardcoded in an engine function, the execution outcome should be allowed to deviate slightly. Preferrably we would want a way to define behavior edge cases have an influence on the calculation, e.g. when we attack with a height advantage. How that is handled is discussed next week, when we take a look at `Bonus` objects.

Any more questions? Let us know and discuss those ideas by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on libera.chat
