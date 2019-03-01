Title: D13: Openage modding API - Diplomatic Stances (+ more updates)
Date: 2019-03-01
Tags: nyan, modding, API
Authors: heinezen
Summary: Introducing new features that concentrate on the diplomatic relationship between players

It's time for another update on the latest changes and this time, they primarily deal with the relationships between players. In previous blogposts, we always assumed that an ability already indirectly defines whether it can be used against friend or foe. However, this is often not as obvious as it seems, especially after the introduction of the `ApplyEffect` ability (see our [last blogpost]({filename}/blog/D0012-openage_mod_api_effects.md)) which can be used for friendly actions like healing or hostile actions such as attacking. Our solution to this problem is the addition of *diplomatic stances* which we will now discuss in detail.

Other interesting articles in the modding API series:

* [Introduction]({filename}/blog/D0000-openage_mod_api_intro.md)
* [Too many villagers!]({filename}/blog/D0007-openage_mod_api_villager.md)
* [Transform]({filename}/blog/D0008-openage_mod_api_transform.md)
* [Restocking farms]({filename}/blog/D0010-openage_mod_api_farming.md)
* [Effects]({filename}/blog/D0012-openage_mod_api_effects.md)

[View all articles]({filename}/blog/landing_page.md)

## Diplomacy and abilities

![DiplomaticAbility]({static}/images/D0013-diplo-ability.png)

The core concept behind diplomatic stances is that they decide what abilities can be used on another player's units. This is realised through the new `DiplomaticAbility` API object. Any ability that inherits from `DiplomaticAbility` can only be used with/against units of players with the corresponding diplomatic stances defined in the member `stances`. A really simple example is the `Attack` ability from the example above that can only be used against units from players where the stance is set to `Enemy`.

It is important to stress that the openage API only defines one built-in stance (`Self`). `Self` is a special stance that implies an abilitiy can be used on the player's own units, if added to the set of `stances` of a `DiplomaticAbility`. This can be used for active abilities like `Heal`, but also for more passive ones like `DropSite` which enables a `GameEntity` to be a resource dropoff point. All other stances have to be defined by the mod or game they are part of. In the case of AoE2 these stances would be `Ally`, `Neutral`, `Enemy` and possibly `Gaia` for the special relationship with wildlife.

Although players in AoE2 usually have the same stance towards each other, there is the potential to be more creative with diplomacy. For example, the stance system makes it possible to have vassal-overlord relationships where the overlord can use special abilities on its vassal, e.g. forcefully conscript the subject's units or collect tribute.

It should be noted that inheriting from `DiplomaticAbility` is entirely optional and by default, every ability works with all diplomatic stances.

## Diplomacy elsewhere

![DiplomaticEffect]({static}/images/D0013-diplo-effect.png)

Abilities are not the only useful application for diplomatic stances. Another use case are the `Effects` that we introduced last time. If you recall, effects define a form of interaction (damaging, healing, converting, etc.) between two or more game entities. In some situations, the effect should only apply to units of players with a specific stance. For example, the kamikaze attacks of the petard and the demolition ship only do damage to enemy units. Similarly, projectiles usually do not damage friendly units with the exception of onager shots.

The problem is solved by introducing a `DiplomaticEffect` that works in the same way as `DiplomaticAbility`. By making an `Effect` inherit from `DiplomaticEffect`, the effect will now only be applied to units of players that are covered by the diplomatic stances in the `stances` member. `Effect`s that do not inherit from `DiplomaticEffect` will be applied regardless of the stance of the target.

![DiplomaticPatch]({static}/images/D0013-diplo-patch.png)

On the side of smaller changes, there is the new `DiplomaticPatch` type. Before, patches in a `Tech` only upgraded the game entities of the player who researched the technology. `DiplomaticPatch` lets you define upgrades that can also apply to other players. These could be very fun to experiment with, as technologies are now able to influence enemies and allies alike.

![DiplomaticSetup]({static}/images/D0013-diplo-setup.png)

The `Civilization` object previously contained a `team_setup` member that stored the team boni that were applied to other team members in AoE2 games. Since the API now supports diplomatic stances directly, we have opted for a more fine-grained and flexible solution. `team_setup` is superseded by the `DiplomaticSetup` objects in `diplo_setup`. `diplo_setup` can store as many objects as necessary, so it is possible to define a setup for every existing stance, if required. As an interesting side effect, a civilization could also give boni/mali to its enemies.

## Side notes (Container ability)

![Storage ability]({static}/images/D0013-storage-ability.png)

Last but not least, there is something else to discuss which is somewhat related to diplomatic stances. In [blogpost No. 7]({filename}/blog/D0006-openage_mod_api_inventory.md) we introduced the `Inventory` ability to provide a way  for units to store items like the relic rather than merging with them. Back then, Reddit-user Kaligule [pointed out that transport ships, rams and siege towers](https://www.reddit.com/r/openage/comments/9blg1k/openage_modding_api_inventory_system/e554xpx/) (and garrisoning in general) could potentially be modelled the same way. However, at the time the API could not have supported this because `Inventory` relied on items being neutral game entities that did not belong to a specific player.

With the addition of diplomatic stances, there are no more excuses to keep `Inventory` and `Garrison` as separate abilities. Hence, they were merged into the `Storage` ability. `Storage` is essentially the same as `Inventory`, so there is nothing special to tell about it that was not discussed before. A side effect of `Storage` being a `DiplomaticAbility` is that you can put other player's units in inventories now, which will make creating Pokemon game modes for AoE2 a bit easier.

So as always: Do not hesitate to suggest improvement ideas on Reddit. It's encouraged to question the devs, it just takes long to implement :)

# Questions?

Do you still have questions? Then let us know and discuss them with us and the community by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
