Title: The openage Converter - Part II: Preparations for Conversion
Date: 2020-05-14
Tags: nyan, converter, assets
Authors: heinezen
Summary: We investigate how the Genie structures are organized into API-like objects.

Our last blogpost was all about parsing the AoE2 `.dat` file and structuring its content into objects that
represent the **logical entities** of the original format (like in Advanced Genie Editor). However, we cannot
start with the transition to nyan objects just yet. The reason for this is that the openage API has
a different structure than the objects we acquired from the `.dat` file so far. Thus, an additional
refinement is required to before we can do the transition to nyan. How this affects the converter is
our topic for today.

![You are here!]({static}/images/T0004-converter-structure.svg)

## Spotting the Differences

Attributes from the `.dat` file often do not have a direct 1-to-1 mapping to the nyan API. While openage
and AoE2 essentially do the same thing on the surface, the underlying structure of the openage API can differ quite
significantly from the structure of the logical entities in the Genie Engine. Some of the mechanics were
extended or streamlined by us, other had to be altered to fit the Entity-Component System model our API uses.
A few examples of different data models are listed below.

Game Mechanic         | Genie Engine                                 | openage
----------------------|----------------------------------------------|----------------------------------------------
Unit Upgrades         | Units are *replaced* with upgraded unit      | Unit *attributes* are upgraded (with patches)
Creation location     | Stored in connection or *created* unit object| Stored with *creating* unit object
Trebuchet (un)packing | Trebuchet is *replaced* with (un)packed unit | *State change* in state machine
HP                    | *Hardcoded* behaviour (damage, death, heal)  | HP is a *configurable attribute*

Unit upgrades are especially challenging because AoE2 replaces the whole unit object reference, while openage
upgrades only the attributes that actually change. In order to detect which attributes change we need to
know the upgrade order of units (also called a *unit line*) and create a diff between neighboring units
in that line. Replacement mechanics are also used in other ways, e.g. for the trebuchet, which requires its
own special treatment.

Other mechanics, such as the creation location of buildings or units, can sometimes be annoying to detect
when we process units one at a time. For example, there is no way to see which buildings a villager can
create by looking at the villager object alone.

## Concept Grouping

The first step we take to solve the described problems is to use **concept grouping**. The idea behind this
method is that even though the data model of the Genie Engine and openage can be very different, the gameplay
mechanics/concepts stay the same. One example of such a concept would be the aforementioned unit line, while
a concept group is a specific instance of the concept, e.g. the archer unit line in AoE2. Examples for other
concepts are age upgrades, civs or transform groups (trebuchets).

In the converter, the concepts are implemented as Python classes whose instances become the concept groups.
The classes usually implement methods that can figure out additional context about the groups, e.g. whether
a unit line is unique or what position every unit in the line has. To establish the concept groups, the
converter iterates through every logical entity, finds the related concept and adds the entity to its
corresponding group.

![GenieUnitLineGroup UML]({static}/images/T0004-group-object.svg)

(The above image shows an UML excerpt from the Python class `GenieUnitLineGroup` (for - you guessed it - the unit line concept)
on the left as well as an example instance in form of the archer line. The instance stores the units that are part of the line
as an ordered list of `GenieUnit` objects which you should be familiar with from the last blogpost.
Methods from the class are available for every instance and help us determine a line's properties.)

One big advantage of concept groups is that every concept does have a 1-to-1 mapping from AoE2 to openage;
something that a single logical entity did not necessarily provide. The groups' Python classes provide an
abstract view on the concepts in this case which translate the Genie data model to the openage data model.
Hence, you can also interpret the created concept groups as *API-like objects* that represent an openage API
concept using Genie Engine data. By operating on the groups during nyan conversion, the converter does not
have to worry about the context of individual logical entities anymore and can concentrate solely on
fetching the necessary data from the groups.

## Linking

The purpose of **linking** is to add information about the relation to other groups to a concept group. We mostly
do this for relations that would be hard to detect from just looking at one concept group because it is
not stored as a value in its logical entities. An example for this that we mentioned before are the buildings
a villager creates. The links in a concept group are technically just a bunch of concept-specific lists in
the Python classes. These lists are filled by iterating through all concept groups we created, each time looking
for a relation to another group and appending the group to the list asspociated with the relation type.

![GenieUnitLineGroup UML]({static}/images/T0004-group-object-linking.svg)

(This is the same `GenieUnitLineGroup` class as shown above, this time with linked information visible.
`creates` stores the building lines created by the villager, `garrison_locations` the places where it
can garrison.
Note that these links are also stored as lists, but in contrast to `line` which stores references to
`GenieUnit`s, links will usually reference group instances.)

Linking is not as important as grouping, but it saves us a lot of runtime when a relation is relavant more than
once. It also ensures that every concept group has all information it needs for conversion available in the
Python object instance and (theoretically) does not need to search the rest of the dataset for information.

Now that we have prepared the data for conversion, we can finally start to translate it to the nyan API.

## To be continued...

The series will continue soon with another blogpost about the converter. Next time we will start to look at
the most important step in the conversion process: the nyan object creation.

If you have any questions regarding this blogpost or you are eager to help developing openage make sure to pass by in **[our forum](https://openage.discourse.group/)**. You can also check the weekly development news on [our subreddit](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on libera.chat
