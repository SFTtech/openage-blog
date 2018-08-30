Title: D2: Openage modding API - Abilities
Date: 2018-08-02
Tags: nyan, modding, API
Authors: heinezen
Summary: Abilities give units something to do

[Last week]({filename}/blog/D0001-openage_mod_api_game_entity.md) we learned about the `GameEntity` API object and how it provides a skeleton for the objects present in the game world. This time we are going to enable units to interact with each other by giving them *abilities*.

Other articles in the modding API series:

* [Introduction]({filename}/blog/D0000-openage_mod_api_intro.md)
* [Units, Buildings & more]({filename}/blog/D0001-openage_mod_api_game_entity.md)
* Abilities (you're here)
* [Patching]({filename}/blog/D0003-openage_mod_api_patching.md)
* [Attack]({filename}/blog/D0004-openage_mod_api_attack.md)
* [Bonus]({filename}/blog/D0005-openage_mod_api_bonus.md)
* [Inventory System]({filename}/blog/D0006-openage_mod_api_inventory.md)

# The Ability API object

![Ability examples]({filename}/images/D0002-abilities-overview.png)

Each `Ability` API object has two main purposes.

First of all, an `Ability` is always linked to behavior that is defined by an engine function. By adding an `Ability` to a game entity, the engine knows that the unit is allowed to execute this behavior. For example, once the `Move` ability is added to a unit, it will automatically be able to move around. The exact behavior of an ability is always decided by the engine, hardcoded into a function.

Furthermore, an `Ability` object stores the attributes that are necessary for the execution of the ability. An example for `Move` would be the speed at which a unit moves or for `Build` the buildings that can be constructed. Keep in mind that nyan objects only store *definition data* which is different from the stats of a unit at runtime. For example, the `Live` ability only defines the **maximum HP**, while the **current HP** value is handled by the engine's runtime simulation system.

## Complexity

Because pretty much everything is an ability, the associated properties can range in complexity. Some abilities are purely passive and don't even define members, e.g. `Passable` which just tells the engine to turn the collision of a game entity off. Others define stats for units, like the `Live` ability does with `hp` and `line_of_sight` or the `Creatable` ability with `creation_time`.

The more sophisticated abilities allow units to interact with other entities in the game world, e.g. `Repair` or `Build`. Often these complex abilities are also animated and have an execution sound. This is signified by them inheriting from `SoundAbility` or `AnimatedAbility`. Abilities usually only store one animation (with rare exceptions), but can define several sounds, one of which is played randomly on execution.

## nyan example

Now (finally) we are going to have a look at how all the definition we talked about are written down in the nyan language.

``` python
Swordsman(engine.Unit):
    # Strings and translation data (not explained here)
    name = SwordsmanName
    description = SwordsmanDescription
    tech_tree_help = SwordsmanHelptext

    ...

    icon = "swordsman_icon.png"

    # Hitbox
    radius_x = 0.3
    radius_y = 0.3
    radius_z = 0.55

    variants = o{}
    abilities = {SwordsmanLive, SwordsmanMove, SwordsmanDie}
    boni = {}

    SwordsmanLive(engine.Live):
        hp = 40
        line_of_sight = 3
        pop_space = 1
        visible_in_fog = False

    SwordsmanMove(engine.Move):
        # Inherited member from AnimatedAbility
        animation = SwordsmanMoveAnimation

        SwordsmanMoveAnimation(engine.Animation):
            animation = "swordsman_move.sprite"

        # Inherited member from SoundAbility
        sounds = {SwordsmanMoveSound1, SwordsmanMoveSound2}

        SwordsmanMoveSound1(engine.Sound):
            play_delay = 0
            sounds = o{"swordsman_move.opus"}

        SwordsmanMoveSound2(engine.Sound):
            play_delay = 0
            sounds = o{"swordsman_move_alt.opus"}

        # Unique members of Move
        speed = 1.56
        turn_speed = inf # this means turns are instant


    SwordsmanDie(engine.Die):
        # Inherited member from AnimatedAbility
        animation = SwordsmanDieAnimation

        SwordsmanDieAnimation(engine.Animation):
            animation = "swordsman_die.sprite"

        # Inherited member from SoundAbility
        sounds = {SwordsmanDieSound}

        SwordsmanDieSound(engine.Sound):
            play_delay = 0
            sounds = o{"swordsman_die.opus"}
```

In this example we have created a simple unit `Swordsman`. Right from the start, we can see that `Swordsman` inherits from the `Unit` API object (referenced by `engine.Unit`). Aside from the values that were required for the members inherited from `GameEntity` there are three abilities defined: `SwordsmanLive`, `SwordsmanMove` and `SwordsmanDie`. As you probably already guessed, they use the API objects `Live`, `Move` and `Die`.

The three abilities are defined as *nested objects*. Nested objects work just like normal objects with the neat little benefit that we can keep the notation of the units, its abilities and other dependent objects together in one space. For the abilities we do what we always do: We assign values to the members that are required by the API. After filling everything in, we have completed the definition of `Swordsman`, a special case of `Unit`/`GameEntity`.

And that's really the gist of it. Using the API mostly evolves around "filling in the blanks" by assigning values to the required attributes. The above definition can be taken as is, placed as plaintext inside a `.nyan` file and will be understood by the engine. Of course, in a real life situation a modder would also have to create animations and sounds to be included. But we hope it was clear that these do not get magically created out of the blue.

# Questions?

We have now seen the initial definition of a unit in nyan, but in real-time strategy games the intial values are often changed by upgrades, techs and other modifiers. How these changes are handled in nyan and why it is awesome will be discussed next week when we talk about *Patches*.

Until then feel free to ask questions and discuss the blogpost in [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
