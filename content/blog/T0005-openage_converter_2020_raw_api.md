Title: The openage Converter - Part III: Convert!
Date: 2020-06-16
Tags: nyan, converter, assets
Authors: heinezen
Summary: We describe how data in the API-like objects is transferred to nyan objects.

In our previous blogpost we introduced the idea of **API-like objects** which organize logical
entities from AoE2 in such a way that we can map their data to the concepts of the openage API.
With all preparation done, we can now take the final step and convert the data to our [nyan
data format](https://github.com/SFTtech/nyan).

![You are here]({static}/images/T0005-converter-structure.svg)

## Iterate!

The approach we take to create the nyan objects is very straightforward: We iterate through all
concept groups, check what properties they have and create the associated nyan objects. Since
we made sure during the preparation phase that every concept group has information to be processed
individually, the transformation to nyan is surprisingly simple. So let's do an example.

A very basic concept group conversion for a `GenieUnitLineGroup` would look like this:

1. We check for the properties the unit line could have one by one. A property (or *ability* as it is
called in openage) represents something the unit line **is** or **does**, e.g.
    * Can it attack?
    * Can it build/create other game entities?
    * Is it harvestable?
    * ...
2. If a property check is successful, the `GenieUnitLineGroup` instance is passed to a function in a subprocessor.
There, the converter creates the corresponding nyan objects and assigns their member values by
mapping the unit values from the .dat file to them. All created nyan objects are stored with the
`GenieUnitLineGroup` instance, so they can be exported to file later.
3. Repeat this process for every possible property a unit line can have.

The same principle is applied to concept groups for buildings, ambient objects or concept groups
that are not even game entities such as techs or civs. The only difference for the latter is that
techs check for effect types, not properties. However, the workflow is the same, with the tech
being passed to a subprocessor that creates the nyan objects for its effect types.

A subprocessor function in the AoE2 converter are designed to be reusable for the conversion
of other games running on the Genie Engine, if they implement the corresponding property in
the same way. For example, basic movement properties are the same across all games.
The reusability is a huge benefit as it drastically decreases code redundancy and makes implementing
converters for other Genie games much simpler.

## Request!

Something we didn't talk about so far is the conversion of media files.
In the old converter, data and media files (mainly sounds and graphics) were exported separately.
The converter would just take a media container format like `graphics.drs` and dump all its
contents into one folder, regardless of whether they were actually used in the game.

![Media export request]({static}/images/T0005-media-export.svg)

This process has been revised for the new converter. The biggest change is that it now only exports media
files that were explicitly requested during data conversion. As a result, we can be more
selective about the media we want to have. For example, the "main" AoE2 modpack will only contain data
relevant for skirmish and multiplayer maps which means scenario or beta units are not included. Since these
units are not in the modpack, we also do not generate export requests for their graphics. This
ultimately saves a lot of conversion time for players that are not interested in singleplayer.

Integrating the media conversion into the data conversion also enables us to automatically generate
context-specific filenames such as `idle_archer_animation.png` instead of `8.slp.png`. Sometimes this
doesn't work as well as intended - especially when a media file is shared between units - but it's
certainly better than finding volunteers to name 1000 files manually.

## Export!

The export step is even more simple than conversion step as we just dump all the data we created. Nyan
objects are transformed into their human-readable string representation and printed into files. Media
files are converted into open image and sound formats as well as having their metadata extracted into
text files. It doesn't get more complicated than that.

However, every modpack also gets a few extra meta formats for glueing the modpack together. One of these
is the **modpack definition file**. This file stores the load configuration data for the engine initialization,
e.g. the paths to the included data folders and referenced to other modpacks it may require. It also
contains basic descriptive information such as the modpack's human-readable name, a (translated) description
or the list of authors.

The other formats are a **manifest file** optionally accompanied by a **cryptographic signature**. Every manifest
stores a list of hash-filename pairs for every file in the modpack. This can be used to check the
integrity of the modpack during load time. Its main purpose is to ensure that all players in a multiplayer
game use the same files and thus operate on the same data. Signatures (generated by a trusted authority)
can be used to additionally verify that the signed modpack is *safe to use*, e.g. they don't contain
malware or mine bitcoins while you play. However, this is much more relevant for user-created modpacks that use
complex scripting than for the modpacks generated by the converter.

## To be continued...

There will be one final blogpost in this series where we talk about future plans and considerations for the converter.
Keep an eye out for that!

If you have any questions regarding this blogpost or you are eager to help developing openage make sure to pass by in **[our discussion board](https://github.com/SFTtech/openage/discussions)**. You can also check the weekly development news on [our subreddit](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on libera.chat
