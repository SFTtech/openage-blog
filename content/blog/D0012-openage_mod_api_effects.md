Title: Openage modding API - Effects
Date: 2019-01-27
Tags: nyan, modding, API
Authors: heinezen
Summary: A new way of interaction between game entities

A recent discussion on how the `Convert` ability should work brought up the question how we want to handle interaction between different game entities. In our previous drafts, every interaction had its own ability. This aproach works, but inevitably creates redundancy. We introduced a new mechanic in form of `Effect` objects to address these issues and hopefully make the engine even more extensible along the way.

Latest articles in the modding API series:

* [Restocking farms]({filename}/blog/D0010-openage_mod_api_farming.md)
* [Civilizations]({filename}/blog/D0009-openage_mod_api_civ.md)
* [Transform]({filename}/blog/D0008-openage_mod_api_transform.md)
* [Too many villagers!]({filename}/blog/D0007-openage_mod_api_villager.md)
* [Inventory System]({filename}/blog/D0006-openage_mod_api_inventory.md)

[View all articles]({filename}/blog/landing_page.md)

# Many abilities, many overlaps

![Old interactive abilities]({static}/images/D0012-old-abilities.png)

The main problem with our interaction abilities is the lack of consistency in their mechanics. Some -- like `Heal` or `Repair` -- are one-sided as the outcome is solely decided by the unit that executes the ability, while others such as `Attack` are two-sided with the final attack value depending on both the attacker and the defender. Also, there are specialized abilities for the purpose of activating a `ResourceSpot` like the `Hunt` ability. And of course there's `Convert` with [weird and ridiculous rules](https://www.aoezone.net/threads/how-monks-really-work-v-2-all-the-details.119879/#post-470767) (thanks go out to Jineapple who figured all of this out).

One major drawback of having different behaviors for every interaction is that they are not compatible with each other. It is not possible to have an `Attack` that does damage **and** has a chance to convert for example. The idea behind the reorganization of abilities into an effect-based system is to eliminate these incompatabilities and to make combinations of different effects possible.

# Effect and Resistance

The new system draws heavy inspiration from the old attack definition described in [blogpost No. 5]({filename}/blog/D0004-openage_mod_api_attack.md). It is recommended that you read the whole article if you haven't already.

![New effect system]({static}/images/D0012-effect-resistance.png)

Every interaction is now two-sided and modeled through a pair of `Effect` and `Resistance`. The `Effect`s are defined by the applicant of the effect, while the `Resistance` is always defined by the unit the effect is applied on. For convenience sake, we will call the two sides "effector" and "resistor" from now on.

The mechanics that were previously tied to abilities are now defined as generic effects and resistances, albeit with different names. For example, the `ArmorAttack` and `ArmorDefense` objects previously used for the `Attack` ability are now covered by `FlatAttributeChange` (on the left) and `FlatAttributeResistance` (on the right). Despite the bulky object names, attacking still works the same way as before. Newly added are `ChanceEffect`s, which can be used for conversion, and `MakeHarvestable` that makes `ResourceSpot`s accessible to villagers.

One important mechanic that was carried over from the attack system is that the application of an `Effect` by an effector always requires the corresponding `Resistance` on the resistor's side. For example, if a resistor has no `ConversionResistance` defined, it **cannot** be converted with the `Conversion` effect. This is slightly counterintuitive, but makes giving units immunities much easier. If you want a conversion with zero resistance, this can instead be done by assigning a `ConversionResistance` object with `chance_resist` set to 0 to the resistor.

The `Effect` and `Resistance` objects can usually be used both ways. Either for the benefit or for the disadvantage of the targeted game entity. For example, setting a positive value for `change_value` in `FlatAttributeChange` will damage a unit, while a negative value essentially be a heal. To prevent a heal from accidently damaging the resistor, modders can define minimum and maximum value limits for an `Effect`. This is entirely optional, so you can also choose not to and let everything go haywire.

Calculation examples can be found in the Addenndum section at the bottom of the article.

## Discrete vs. Continuous

The current effects can come in two forms, *discrete* and *continuous*. `DiscreteEffect`s are applied immediatly *at a specific point* in time. `ContinuousEffect`s on the other hand happen *over time* at a defined rate (e.g. reduction of attribute points per second). The differentiation is necessary because an ability using `DiscreteEffect` needs to define the application interval which is not necessary for `ContinuousEffect`. Examples for the application of a `ContinuousEffect` in Age of Empires include healing and repairing. 

## The new abilities

![New exciting abilities]({static}/images/D0012-effect-abilities.png)

With the introduction of effects, the interaction abilities are subject to a lot of changes, too. As we can cover most of them with an `Effect`, the `Convert`, `Heal` and `Repair` ability do not need to be part of the API anymore, indicated by their white color. Instead, they are from now on handled as derivatives of `ApplyDiscreteEffect` and `ApplyContinuousEffect` shown in the centre of the diagram. For example, implementing the old `Heal` ability would be realized by inheriting `ApplyContinuousEffect` and defining one or more continuous `FlatAttributeChange` effects. A dedicated `Heal` ability is unnecessary as the needed definitions are stored in the effect. The only specific ability remaining is `DiscreteAttack` because the API does not have a concept of diplomatic stances yet which is required for recognizing friendly fire (although this could change in a later API draft). Resistances are stored in the `Resistance` ability (shown in the upper right corner).

For every general application ability there also are two more specialized API abilities available: `AreaOfXXXEffect` and `RangedXXXEffect`. With `RangedXXXEffect` one can define the minimum distance to a unit for the application of effects. `AreaOfXXXEffect` applies the effects in an area around the effector. This was previously only modeled for attacking, but now it is available for all effects. This means that you can make super monks that convert everything around them. Neat! Because `effects` is a set member, all abilities are able to bundle and apply multiple effects at once. 

The greatest advantage of this system is that it has eliminated the incompatibilities mentioned in the beginning. Delegating the behavior to individual effects allows us to derive abilities that combine them freely without being restricted to a specific type of effect. Theoretically, an ability can even apply both continuous and discrete effects by inheriting from `ApplyContinuousEffect` and `ApplyDiscreteEffect` simultaneously.

## More to come..?

The next logical step to improve the effect system would obviously be the definition of even more effect and resistance types. Right now, the API only features 4 concrete effects and resistances and there is room for more. Extensions could be damage-over-time effects like Poison or Fire Damage as well as more creative effects like a Life Steal. Another addition would be allowing effects to attach modifiers to other units that give temporary buffs or debuffs, e.g. a Disease.

There is also the question remaining whether `Gather` and `Build` are supposed to be effects or if they should be left as separate abilities. Both of them are candidates as they define a form of interaction, but modeling them as effects might require further depature from the way they were implemented in AoE2. Therefore, we will postpone the decision to a later date.

# Questions?

*Hint*: You can suggest your own improvement ideas on Reddit. It's not forbidden to question the devs.

Do you still have questions? Then let us know and discuss them with us and the community by visiting [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net

## Addendum: Example Calculations

Defining and calculating the result of an effect-resistance pairing is very easy and straight forward. Look at the example below for a simple interaction effect involving `FlatAttributeChange`.

```python
# Effector's side
MeleeAttack(FlatAttributeChange):
    type = MeleeArmor
    min_change_value = 0
    max_change_value = None
    change_value = AttackAmount
    
    AttackAmount(AttributeAmount):
        type = Health
        amount = 4
    
    ignore_protection = {}

###################################
    
# Resistor's side
MeleeResistance(FlatAttributeResistance):
    type = MeleeArmor
    block_value = BlockAmount
    
    BlockAmount(AttributeAmount):
        type = Health
        amount = 1
```

The effector's attack does 4 health points of damage and the resistor blocks 1 damage, so the overall damage done is 3. Keep in mind that `Effect` and `Resistance` have to match up for this to work. For `FlatAttributeChange`, the match is defined by the `type` member of `FlatAttributeChange`/`FlatAttributeResistance` and the `type` member of `AttributeAmount`. An example where the pair doesn't match up can be seen below.

```python
# Effector's side
MeleeAttack(FlatAttributeChange):
    type = MeleeArmor
    min_change_value = 0
    max_change_value = None
    change_value = AttackAmount
    
    AttackAmount(AttributeAmount):
        type = Health
        amount = 4
    
    ignore_protection = {}

###################################
    
# Resistor's side
MeleeResistance(FlatAttributeResistance):
    type = MeleeArmor
    block_value = BlockAmount
    
    BlockAmount(AttributeAmount):
        type = Faith                   # <-- Not a match
        amount = 1
```

The `type` of `AttributeAmount` in the effect does not match the `type` of `AttributeAmount` in the resistance. In this case the resistor is immune to the `MeleeAttack` effect, but usually effector's apply more than one effect and resistor's have more than one resistance.


```python
# Effector's side
MeleeAttack(FlatAttributeChange):
    type = MeleeArmor
    min_change_value = 0
    max_change_value = None
    change_value = AttackAmount
    
    AttackAmount(AttributeAmount):
        type = Health
        amount = 4
    
    ignore_protection = {}

PierceAttack(FlatAttributeChange):
    type = PierceArmor
    min_change_value = 0
    max_change_value = None
    change_value = AttackAmount
    
    AttackAmount(AttributeAmount):
        type = Health
        amount = 2
    
    ignore_protection = {}

Convert(ChanceEffect):
    type = Conversion
    chance_success = 0.5
    cost_fail = None

###################################
    
# Resistor's side
MeleeResistance(FlatAttributeResistance):
    type = MeleeArmor
    block_value = BlockAmount
    
    BlockAmount(AttributeAmount):
        type = Faith # No match
        amount = 1

PierceResistance(FlatAttributeResistance):
    type = PierceArmor
    block_value = BlockAmount
    
    BlockAmount(AttributeAmount):
        type = Health
        amount = 5

ConversionResistance(ChanceResistance):
    type = Conversion
    chance_resist = 0.1
```

This time, multiple effects come into play. The effect `MeleeAttack` attack has no match on the resistor's side, so it is ignored. 

`PierceAttack` does match up with `PierceResistance`, so the damage can be calculated. With a damage value of 2 and a block value of 5, the overall change to the resistor's health would be `-3`, which is equivalent a heal of 3. Because the effector has initialized `min_change_value` with 0, the change is rounded up to that number. As a result 0 pierce damage is done.

`Convert` also has a match (by type) on the resistor's side in form of `ConversionResistance`. The chance is calculated by substracting `chance_resist` from `chance_success`, resulting in an overall chance of `0.4` (40%) for the effector to be successful.
