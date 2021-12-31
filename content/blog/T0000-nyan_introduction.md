Title: T0: nyan API integration
Date: 2017-08-13 10:20
Tags: nyan, API
Authors: jj
Summary: nyan will be used for as content interface in openage


This is probably our zeroth technical information post,
it may be informative to you if you want to follow development more closely.
We'll post more things on an irregular basis :)


# What's nyan?

[nyan](https://github.com/SFTtech/nyan) is our new database for storing the game configuration:
It provides which units are available, what they can do, cultures, technologies,
i.e. everything that makes openage behave and look like age of empires.

`nyan` also functions as mod-API, as it is designed to be easily usable and extensible
for content creators and modders.
After some minor changes and improvements in `nyan`,
we start to integrate it into the engine and use it as data source.

For this, we need to create the "openage API", i.e. everything the engine can do.
The API is defined in `nyan`-files:

* The engine accesses content data by names and structures it defined in the API
* The game content is created and set up with this API

## API Example

For example this could be a simplified version of the openage API,
defined in valid `nyan` code:


``` python
Entity():
    name : text

Unit():
    hp : int
    abilities : set(Ability)
    # probably much more is missing here :)

Resource():
    name : text
    icon : file

DropSite():
    accepted_resources : set(Resource)

ResourceProvider():
    resource_type : Resource
    amount : int

ResourceSpot():
    provided_resources : set(ResourceProvider)

Animation():
    image : file
    frames : int = 1
    loop : bool = True
    speed : float = 15.0
    # ^ the above information could also be in
    #   some info file that accompanies the image

Ability():
    animation : Animation

Movement(Ability):
    speed : float
    instant : bool = False
    range : float = inf

HarvestResource(Movement):
    target : Resource
    harvest_animation : Animation
```


Using that API, we can now create content for a game that is running on the engine, e.g. our AoE2 implementation:

``` python
Wood(Resource):
    name = "chop chop"
    icon = "wood.svg"

Tree(Entity, ResourceSpot):
    name = "big ol' oak"

    TreeWood(ResourceProvider):
        resource_type = Wood
        amount = 150

    provided_resources = {TreeWood}


Villager(Unit):

    Walking(Movement):
        WalkingAnim(Animation):
            image = "walking_villager.png"
            frames = 18

        animation = WalkingAnim
        speed = 15.0

    HarvestWood(HarvestResource):
        Transport(Animation):
            image = "wood_transport.png"
            frames = 40

        Chop(Animation):
            image = "wood_cutting.png"
            frames = 20

        target = Wood
        animation = Transport
        harvest_animation = Chop
        speed = 12.0

    name = "Villager"
    hp = 25
    abilities += {Walking, HarvestWood}
```

If we now assume the engine properly implements the expected behavior of the API,
this could be an intuitive definition of a villager that can do wood cutting.

The content for AoE1 can be described just as easily.
Modders will have a great time because they can add any object and action on the fly, as long as it uses the API.

* You want to add a new resource? Define it, add resource spots and the harvesting action and it's in the game.
* You want "special moves" or hero units like in Warcraft 3 or AoM? Just define a new ability, add it to the units that shall have it and you're good to go.

You may now ask yourself "why the data is described this way and not another?"

* The majority of errors are checked at load-time through the `nyan` type system.
* `nyan` allows to change the data at run time with patches:
    * A patch object defines changes to member values of a target object.
    * This means that every possible change is already stored in the database.
    * When mods e.g. add new abilities to a unit, this is done by a patch activated when your mod is activated.
    * When you click a button for technology research, a patch is applied (villager now has +10 HP for example).

In essence: **all game modifications** are done only by patches.
Be it technology research, development testing, mods or total gameplay overhauls.


Here, have an overly-simplified example with the loom technology,
the first research usually available in the town center.

``` python
Loom<Villager>():
    hp += 15

TownCenter(Unit):
    researches = {Loom}
```

The openage engine implements the feature "research buttons", which will activate the patch if a user clicked on it.
Missing in the example is of course configuration of the button look, delay, cost for the research etc, but you get the point.


## Integration

Now you might wonder how `nyan` works together with the rest of the engine?
We've got many ideas there and are experimenting how the simulation could be done best,
but the overall structure boils down to this:

<pre>
client:
nyan <-> [simulation playback/prediction with curves] <-> [presenter: gui, renderer, audio]
           ^
           | network
server:    v
nyan <-> [authoritative simulation with curves]
</pre>

This architecture allows us to have one dedicated game server (which can be run by any player)
and users can still do client-side modding.

Once the plan is more clear we'll explain the inner workings of the simulation and prediction.


## Questions

Wanna discuss those ideas? Visit [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on libera.chat
