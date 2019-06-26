Title: D14: Openage modding API - Finale
Date: 2019-06-26
Tags: nyan, modding, API
Authors: heinezen
Summary: We look back at our API changes and summarize the new features

Over the last year, we have introduced a lot of features to our API and spent a lot of time polishing and improving its core concepts. But as an old Chinese saying goes: "You have to let go, otherwise you will never finish the converter and jj will be unhappy". So today, we finally present you the first release version of the *openage Modding API* tree and will talk a little bit about the features that come with it.

We present you the result of hours of thought and discussions **(Open picture in new tab to enlarge)**:

![modding API tree v0.2]({static}/images/D0014-API-tree-0.2.svg)

## Our Feature Set

As a baseline, everything that is and was possible in previous Genie Engine release versions will also be supported in the openage modding API. This includes all features from Age of Empires 1, Age of Empires 2 and Star Wars: Galactic Battlegrounds. Most of them have been reworked to provide better accessibility to modding, but the original behaviour can always be replicated.

**Additionally**, the API provides these new exciting possibilities:

**Modular ability and bonus system for units, buildings and other game objects**<br/>
Every ingame object, whether it is a unit, a building or part of the ambient scenery, is able to use any ability the API provides. This makes units much more flexible and enables modders to implement behaviour known from other games, e.g. Age of Mythology, such as mobile/movable dropoff points and military units constructing buildings. And of course other more crazy combinations are also possible:

* Trading with trees or birds
* Shooting houses as projectiles
* Let relics research special techs and fight in combat

**Nonlinear tech trees**<br/>
Techs can be unlocked through alternative paths and are not necessarily bound to Age Upgrades. The upgrade path can be different for every civilization or game mode. It also allows giving players the choice to select one out of two (or more) upgrades for a unit, e.g. a decision between more attack damage and faster reload speed.

**Proper inventories and item systems**<br/>
Relics will no longer replace the monk unit when picked up. Instead, the API unifies garrisoning, transporting and inventories with a new container system that give units the ability to store other game entities properly. Items and garrisoned units are allowed to grant new abilities or remove existing ones.

**Enable different abilities depending on the unit's state**<br/>
Like the trebuchet from AoE2, all game objects can have multiple states which activate other abilities and give different boni or mali. Modders will be able to define as many transformation states as they like. Additionally, construction, damage and harvest progress are able to change the state of the unit. For example, this can be used to make a building's armor weaker when it is not fully constructed.

**Combine effects such as damage, convert or heal**<br/>
Effects in the API are just as modular as our ability and modifier system. Any unit can apply any effect and is allowed to combine them freely. As an example, modders will be able to create attacks that do damage and also have a chance to convert the unit.

**Techs and civ bonuses affect more diplomatic stances**<br/>
In AoE, your civ choice grants bonuses to the whole team. But what if your enemies would profit too? In our API, civs are allowed to define modifiers for other players that have a different stance than "friendly". Additionally, techs can influence not only yourself, but also others on the same map. Abilities and effects are also allowed to be limited to specific diplomatic stances which enables more specialized diplomacy such as overlord-vassal relationships.

These are the most prominent features that we support. There are a lot of other helpful features that were either too small or too complex to mention. Be sure to check out our [previous blogposts]({filename}/blog/landing_page.md) if you are interested in more thorough explanations of the underlying mechanics.

## What happens next?

We will stop thinking about new features for a while and integrate the existing API into the engine. The core engine parts that need to be worked on are the *core gamestate* and the *converter*. The gamestate needs to be able to understand the API objects and implement the behavior for abilities and modifiers. Our converter can already read the `.dat` files of the original game and now needs to sort the old data into our nyan API tree.

Roadmap for integration:

* The converter will be changed to create nyan API objects and assemble them as a modpack
* In parallel, the engine will be extended to load API objects and implement their intended behavior
* Once everything works, write a modding guide and tutorials

Let's do it!

## Trivia

As a bonus, here is nice collection of fun and pointless facts about the API and its development.

* **The initial attempt at the API (April/May 2018):**

![API draft 1]({static}/images/D0014-API-draft-1.png)

* The API contains **282 individual objects** of which **58 are abilities**, **34 are modifiers** and **13 are effects**.
* There are **36 passive** and **22 active abilities** (considering their functionality).

Member type  | Amount
-------------|--------
bool         | 10
int          | 47
float        | 59
text         | 5
file         | 3
set          | 126
orderedset   | 9
nyan::Object | 130
**Total**    | 389

* The only ability from the first draft that survived until today is `Fly`. All other abilities have been reworked.
* `ShootProjectile` has the **most members** (18) of any API object.
* The object with the **longest name** is `RelativeProjectileAmountModifier` (32 characters). In contrast, the **shortest object name** is `Mod` (3 characters).
* The **maximum depth** of the API tree is 5 which is the longest inheritance distance between the root object `Entity` and the children of `FlatAttributeChangeModifier`.
* Even though nyan supports multiple inheritance, none of the API objects currently use it (this was not always the case). The small number of dependencies makes the API more robust to changes. However, mods using the API are expected to make extensive use of multi-inheritance.
* The lack of multiple inheritance means that the API is indeed a tree and not just a graph.
* The number of units from AoE2 will be reduced from 58 to 28 (excluding unique and cheat units) in the API. This is because we do not store upgraded units as separate ojects, but as patches to the original unit.

# Questions?

Questions? We probably know the answer! Ask us something about the blogpost by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
