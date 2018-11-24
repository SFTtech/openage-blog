Title: D8: Openage modding API - The Transformers
Date: 2018-09-13
Tags: nyan, modding, API
Authors: heinezen
Summary: Transforming between states with certain abilities available

Anyone familiar with *The Transformers* franchise by Michael Bay probably knows how the Autobots work. For those who don't: The Autobots are sentient robots from outer space that come to Earth for robot business reasons, but more interesting is that they can switch between two forms. The first one, vehicle form (a.k.a. product placement form), disguises them as cars or trucks from Earth while also allowing them to drive around at a very fast pace. When transforming to robot form, they lose both disguise and the option to move fast, but are able to shoot, punch or slice their enemies effectively. You could say that each form gives the Autobots different *abilities*. In a sense, this concept is very similar to a unit from AoE2 that also possesses different abilities depending on its form. The trebuchet.

Other articles in the modding API series:

1. [Introduction]({filename}/blog/D0000-openage_mod_api_intro.md)
2. [Units, Buildings & more]({filename}/blog/D0001-openage_mod_api_game_entity.md)
3. [Abilities]({filename}/blog/D0002-openage_mod_api_ability.md)
4. [Patching]({filename}/blog/D0003-openage_mod_api_patching.md)
5. [Attack]({filename}/blog/D0004-openage_mod_api_attack.md)
6. [Bonus]({filename}/blog/D0005-openage_mod_api_bonus.md)
7. [Inventory System]({filename}/blog/D0006-openage_mod_api_inventory.md)
8. [Too many villagers!]({filename}/blog/D0007-openage_mod_api_villager.md)
9. Transform (you're here)
10. [Civilizations]({filename}/blog/D0009-openage_mod_api_civ.md)
11. [Restocking farms]({filename}/blog/D0010-openage_mod_api_farming.md)

# Generalizing the problem

What the little example from the Introduction shows us is that despite the uniqueness of the trebuchet in comparison to AoE2's units, the concept of units that have several forms, which give access to different abilities, is far from uncommon. This means there is a good chance that we can generalize the behavior of units that have multiple forms and use this generalization for the trebuchet, instead of having to hardcode specific behavior for just one unit.

The way AoE2 handles its precious stone thrower is by defining the two forms, *packed* and *unpacked*, as separate units in the game data. Transforming from either of those forms to the other is done by replacing the unit after the transformation is done. We've already discussed why replacement is a bad idea for villagers [in our last blogpost]({filename}/blog/D0007-openage_mod_api_villager.md) and the same problem also applies to the trebuchet. It requires the replaced and replacing units to be in a predictable state. In openage, this is not guaranteed (by design) as individual units can go through a substantial number of changes due to patching, so we need a different approach here. Instead of two units that are switched, we would like to have a single unit where **only** the active abilities change.

# Finite-state machines

Before we consider the openage API definition, we should discuss how we would want transformations to work in general. Fortunately, there are already existing models that we can use for that purpose in the form of *finite-state machines*. A finite-state machine is defined by a finite number of states, which are equal to what we have called forms until now, and the transitions - the equivalent of transformations - between them. Each state is further defined by the abilities and transitions that are available when the machine reaches it. Ideally, we would want our game entities to also be finite-state machines. We will go through an example to clarify what this means exactly. However, to explain the topic properly we need something more complex than an Autobot or a trebuchet: A vending machine.

![Vending machine 1]({filename}/images/D0008-automaton-1.png)

The vending machine that is shown here is defined by a finite-state machine with the three states `s_0`, `s_1`, `s_2` (depicted as nodes) and various transitions between them (depicted as arrows). `s_0` (marked with a double outline) is the starting state that we assume the machine is in when a customer would approach it. Abilities available in a specific state are visible next to the corresponding node in a blue colored font. The total number of abilities the machine has can be seen in the upper left. Only a subset of them is active in each state.

Some of the abilities are transitional, for example `InsertCoin`, which means they trigger a transition to another state when they are executed. A transition is denoted as an arrow with the name of the transitional ability next to it. Other abilities, like `ShowBeverages`, do not result in a transition.

Vending machines are a pretty good example case where finite-state machines are useful because we don't want to give the customer access to all of its abilities at once. For example, using `ShowSelection` makes no sense before `SelectBeverage` was executed. Giving access to the `EjectBeverage` ability before `InsertCoin` was used definitely requires a lot of goodwill, too. With state machines we can make sure that specific actions/transitions are taken before an ability is available to users.

Note that the depicted vending machine always allows us to go back to the starting state `s_0` from any other state. There are even multiple pathways of transitions that accomplish this. However, this is not necessarily the case for all finite-state machines. We can show this with a simple extension.

![Vending machine 2]({filename}/images/D0008-automaton-2.png)

This new version of the vending machine offers one new ability `Break` and a new state `s_e` (changes are colored red). `Break` is available in every state except `s_e`. The practical implications of this are that if our vending machine "breaks" in any of these states, the machine will transition to the error state `s_e` and is only able to execute `ShowError`. `s_e` is a dead-end as there is no transition that gets us back to a previous state anymore.

Dead-end states are not limited to errors in their use cases. They could just as well be defined for a situation where the vending machine runs out of drinks. The point is that it can sometimes be beneficial to transition to a state or even a branch of states, so that it is impossible to reach the starting state again.

So far we discussed finite-state machines where every state is reachable from `s_0` and the whole state graph is interconnected. This does not always have to be the case.

![Vending machine 3]({filename}/images/D0008-automaton-3.png)

We again introduced new states `s_3` and `s_4` and some new abilities which would qualify for some kind of "maintainance mode". In our example, it would make sense for these abilities to be completely unavailable from "customer mode" (especially `EjectMoney`) and therefore have the state machine offer no transition to any of these states. Only an authorized person should have access to them. But how would they be able to reach these states?

The obvious answer is to use *outside measures* which add a transition at runtime, but are not part of the actual machine. As you might remember, game entities in openage can change at runtime. As a result, a transitional ability could be added at a later date by a patch, an item, a script or a trigger in a custom scenario. Finite-state machines in openage are not fixed as they are just as alterable as the game entities that represent them.

Going back to our vending machine, an example for such an outside measure would be a keycard that is slotted into the machine. Similar to an `InventoryItem`, this keycard would enable two additional abilities `EnterMaint.` (for `s_0`) and `LeaveMaint.` (for `s_3`) that transition between `s_0` and `s_3` (depicted as dashed red arrows).

![Vending machine 4]({filename}/images/D0008-automaton-4.png)

# API definition

![Transform API]({filename}/images/D0008-transform-api.png)

Finally, we are going to look at the API definition of finite-state machines in openage. There are two core abilities that accomplish this, `Transform` and `TransformTo`. `Transform` is the ability that enables a `GameEntity` to be a state machine. It stores all the the possible states of the game entity and the startig state as `initial_state`. `TransformTo` on the other hand is meant as a transitional ability which can be used to get into another state. It does so by defining a `target_state` that must point to a state from `states` in `Transform`. It also defines the time the transition takes (`transition_time`) as well as the sprites used during the transition with `TransformProgress` objects. After the transition time has passed, the game entity will switch to the target state.

![Trebuchet API example]({filename}/images/D0008-transform-trebuchet-example.png)

If we would model the trebuchet in our API, we would need one `Transform` abilitiy and two transitional `TransformTo` abilities for our state machine. The transitional abilities change the current state to `Packed` or `Unpacked`. Both of the states are defined in the set `states` from `Transform` as instances of `TransformState`.

All of the abilities referenced in the defined states are also stored in the `abilities` attribute of the `Trebuchet` game entity. This allows them to be easily accessible when we want to patch them, even if they are not enabled in the unit's current state.

![Trebuchet API example]({filename}/images/D0008-transform-trebuchet-automaton.png)

## Improvements?

While modelling game entities with finite-state machines can be very powerful, the current API system does not explore their full potential (yet). For example, the `TransformTo` API ability does not do much except for transitioning between states. Furthermore, units will not be able to use any abilities during the transformation. There is a simple reason for that: We don't need so much complexity right now as the only real practical example is the trebuchet. The priority is making sure that the system works reliably for trebuchets first and then gradually improve it with ideas from modders and developers.

For example, we could add a cost for transformations, cooldowns for transitions, states that units can only be in temporary or states that force them to transform back after a time limit. There is a lot of potential for extending the system.

# Questions?

In our next iteration of the API blog series, civilizations will make an appearance. We will discuss how they work and how the openage modding API handles *uniqueness*.

Any more questions? Let us know and discuss those ideas by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
