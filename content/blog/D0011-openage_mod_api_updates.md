Title: D11: Openage modding API - Additions and Updates
Date: 2018-12-24
Tags: nyan, modding, API
Authors: heinezen
Summary: An update on the previous blogposts

Throughout the last months we made several corrections and additions affecting the modding API that were too small to discuss in one blogpost. Since quite a few changes accumulated though, we decided to bundle them and wrap up the year with a collection of mini blogposts.

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
11. [Restocking farms]({filename}/blog/D0010-openage_mod_api_farming.md)

# Game entity

![Game Enitity (new)]({static}/images/D0011-game-entity-new.png)

From all of our API objects `GameEntity` saw the most drastic changes. Firstly, the members for hitbox and language data were moved to abilities, while the `icon` is now part of the nyan UI modding API (which is [under construction](https://github.com/SFTtech/openage/pull/1077) at the moment). `Building` also had unique members which were moved to the five new abilities `Constructable`, `DamageableBuilbing`, `TileRequirement`, `Foundation` and `TerrainRequirement`. We hope that by outsourcing these members to abilities, game entities will become even more versatile and less restrictive in their definition.

Secondly, we introduced `GameEntityType` referenced by the member `types` which is a new object that can be used for a broader classification of game entities. A game entity can be of several `GameEntityType`s like `Infantry` or `Archer` or both. In comparison to the classes in AoE2, `GameEntityType` is **not** tied to armor and acts as an independent mechanism.

Last but not least, we want to welcome `Projectile` as the fifth `GameEntity` category. In the [2. blogpost](https://blog.openage.sft.mx/d1-openage-modding-api-units-buildings-more.html) we declared that `Projectile` should not be a `GameEntity` because it does not operate independently and always needs a *host unit* that shoots it. Howerever, we came to the conclusion that just because projectiles are dependent on their host in AoE2, this doesn't necessarily have to be the case in openage. Hence, the `Projectile` object has emancipated itself and can now be used for other things than attacking, e.g. converting, resource gathering, repairing and more.

# Resource Contingents

![Resource Contingents]({static}/images/D0011-resource-contingent.png)

Another addition specifically designed for population space is `ResourceContingent`. Contingents are resources with the additional feature that they can be used and provided *temporarily*. In context of population space, this means that units use 1 `PopulationSpace` resource while they are alive and free it again when they have died. Similarly, houses provide 5 `PopulationSpace` once they are built which is available as long as they are not destroyed.

Because `ResourceContingent` is of type `Resource`, contingents can potentially be gathered and thus *permanently* added to the resource pool, too. This could lead to some interesting dual-use mechanics where a resource contingent is gathered first and then temporarily used. For example, one could define a resource contingent `Grain` which has to be collected from farms, while the amount of grain is also used as the population limit. The player can then choose between

1. Keep the `Grain` for additional population space, thus being able to field more units
2. Sell `Grain` for `Gold` and therefore lose room for population, but gain the potential to buy better upgrades for their units.

# Attributes

![Attributes]({static}/images/D0011-attribute.png)

Age of Empires 2 is not known for giving its units many attributes except HP, yet many other RTS games are more generous in that regard. Examples are mana, stamina (Battle Realms), "special" power (AoM, EE), shield (SWGB) and so on and so forth. So, instead of creating an ability for every single attribute RTS designers thought of, we generalize them with the `Attribute` API object. The definition of attributes is very similar to that of `Resource` which makes sense as attributes technically are resources, although only available in the scope of the unit. Abilities that cost attribute points reference `AttributeAmount` which is an attribute's counterpart to `ResourceAmount`.

For AoE2, two attributes are needed in total: `Health` and `Faith`. `Health` should be self-explanatory, `Faith` is used by monks to convert units. `Faith` is also a `RegeneratingAttribute` that is refilled at a defined `rate`. In preparation for SWGB support, we also added `ProtectingAttribute` which shields another attribute from damage. For example, if `Shield` protects `Health`, then the attribute points of the shield will be substracted first in case of an attack. Once the attribute points of `Shield` reach 0, the `Health` points of the unit start to get subtracted. Of course, we can also build longer protection chains with 3 or more attributes.

![Attack (new)]({static}/images/D0011-attack-new.png)

Introducing the attribute system required reworking attacks and armor. Now `ArmorDefense` is always connected to a specific attribute through `AttributeAmount`. `ArmorAttack` had a similar change so that every attack value is targeted at one specfic attribute. Optionally, `ArmorAttack` is allowed to ignore protections from the `ignore_protections` set. As a result, we can now have attacks in SWGB that only affect shields or ignore the shield entirely and damage the HP directly.

# Training and building

![Creatable]({static}/images/D0011-game-entity-creatable.png)

At last, we have made a small change to how the cost and creation time of units and buildings were managed. Before, cost and creation time were decided by the *created* unit through the `Creatable` ability. In our newest API draft, we delegated the decision to the *creating* unit or more precisely, to the `Train` and `Build` abilities. These reference a `CreatableGameEntity` object which stores cost, creation time, requirements and the unit/building that is created. This slight alteration should give more freedom to pricing when the same unit is produced in several different buildings.

# Questions?

That's it for this time, but there will probably be more to add, change or discuss about soon.

Did we leave something out or are we forgetting something important in our API? Shout at us (and discuss your ideas) by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on libera.chat
