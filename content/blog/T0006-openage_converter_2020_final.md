Title: The openage Converter - Part IV: Conclusions
Date: 2020-06-24
Tags: nyan, converter, assets
Authors: heinezen
Summary: Now that the technical aspects of the converter are explained, we take some time to review its performance and talk about features that should be implemented in the future.

With the general converter pipeline explained, there are not that many technical questions left
to be answered except the most important ones: *Does it work?* and *How well does it work?*.
You should be able to guess the answer to the first question yourself if you have read the
previous bloposts (Hint: It's "Yes"). The second question is what we want to answer
in this blogpost. To do that, we will take a look at the overall performance of
the converter, the file size of the created modpacks it generates and how well it is equipped for
future improvements.


## Performance

![Structure]({static}/images/T0003-converter-structure.svg)

The most time-consuming operations in the conversion process are parsing the `.dat` file
in the **Reader** stage and writing media files during the **Export** stage. Parsing
the AoC 1.0c `.dat` file will usually take 1-5 minutes, depending on how old your
processor is. Media export for AoC is in the same range. In comparison to that,
the Genie to nyan format conversion in the **Processor** is really fast and took a maximum
of 3 seconds in my tests. Its impact on the runtime is almost negligeble. All
in all, the conversion from AoC to an openage modpack should not take longer than 10 minutes.

It should be noted that the conversion time does not increase linearly with the size
of the original game. AoE2: Definitive Edition, which is more than 100x bigger than
the AoC 1.0c, will therefore hopefully not take 100x as long to convert. Since the converter
does not fully support all media formats of the Definitive Editions yet, we cannot directly compare the
runtime right now. However, we estimate that total necessary conversion time will be between 30 minutes
and 2 hours.

One remaining challenge is the reduction of the converter's memory consumption. Currently
the in-memory storage of the `.dat` file values consumes a huge amount of space (~360MB for AoC). The reason for
this is that we store these values in Python objects along with contextual information
necessary for the conversion process (see the [first blogpost]({filename}/blog/T0003-openage_converter_2020_read.md)
in the series). In a worst-case
scenario, a boolean that has a length 1 Byte in the `.dat` file will use up to 100 Bytes in
its Python object form, even when we employ memory optimizations like the usage of `__slots__`. This only becomes a
real problem with the large dataset of the AoE2: Definitive Edition (~3,800MB), but it's a problem nevertheless.

The solution to the memory problem will be to offload some of the larger structures to
temporary files during the **Reader** stage and load them on-demand during the nyan conversion.
This will increase conversion time, but will be less demanding for devices with low
memory.


## Modpack size

Modpack size is mostly determined by the size of media files, especially the graphics. Most graphics
in Genie games use palette-indexed sprites with a color depth of either 8 Bit (AoE1, AoC, SWGB)
or 10 Bit (AoE2: Definitive Edition). In comparison to that, openage sprites are stored in PNG files
using the 32 Bit RGBA format.

To prevent the increase in color depth from blowing up the file size, we also compress the spritesheets
with standard PNG compression. Funnily enough, this can lead to situations where an openage 32 Bit
spritesheet has a *smaller* file size than the uncompressed 8 Bit media file it was converted from.
In the end, the openage modpack size will be about even with the size of the original games and
could potentially be slightly smaller.

Of course, compression always comes with a price: The time to decompress the spritesheet
at runtime before rendering. Unless your PC is from 1999, decompression time is so small
that it should not have an impact for the spritesheets of AoC. For the
Definitive Editions, which have sprites with higher resolution and frame rates, we will
have to see how much decompression affects texture load times. If it is an issue, we are probably
able to solve it by implementing predicted asset pre-loading or utilizing block-wise parallel
decompression methods.


## Mod support

Future releases of the converter should also be able to transform a mod for the
original `.dat` file into a valid mod for the converted AoE2 openage modpack. The challenge here is
that mods often not only change existing data; they can also add, remove or rearrange
logical entities in the dataset. Thus converting mods will need more than just diffing values
from the `.dat` files, since we have to figure out how the change fits into the openage data model.
This could be more or less tricky depending on the features of the mod, but adding mod conversion
to the converter will make transitioning to openage much easier for modders used to AoC.


## What about the other games?

AoC 1.0c is only one of the games running on the Genie Engine, so what about all the other games?
Over the years, there have been 6 different releases that use the engine.

1. Age of Empires 1 + Rise of Rome (**RoR**)
2. Age of Empires 1: Definitive Edition (**DE1**)
3. Age of Empires 2 + The Conqueror's (**AoC**)
4. Age of Empires 2: HD Edition (**HD**)
5. Age of Empires 2: Definitive Edition (**DE2**)
6. Star Wars: Galactic Battlegrounds + Clone Campaigns (**SWGB**)

At the time that this blogpost is published, we have already implemented partial support for
4 of these versions. The code for the **AoC** processor is also the converter core. The conversion
processors for the other supported releases (**RoR**, **DE2** and **SWGB**) reuse most
of the core functionality of the **AoC** processor. Functions only need to be reimplemented
for abilities where behaviour between **AoC** and the other games is different. This is where
our modular approach pays off.

Release            | Unique code lines
-------------------|-------------
**AoC** (core)     | 38,000
**RoR**            | 4,000
**DE2** (partial)  | 3,000 (est.)
**SWGB** (partial) | 8,000 (est.)

(only data conversion)

The **DE2** and **SWGB** conversion processors do not convert all features of the games
so far, but already produce functional modpacks. **DE2's** processor is only missing some
of the newer tech effects. **SWGB** deviates the most from **AoC** and has its own
unique features, e.g. shields and stealth units, that are not supported yet;
This is partially the cause of me not being that knowledgable about the game.
So if you do know more about **SWGB's** inner workings, feel free to
come by in our [chat](https://riot.im/app/#/room/#sfttech:matrix.org).
We appreciate the extra help :-)

## Contact

If you have any questions regarding this blogpost or you are eager to help developing openage make sure to pass by in **[our forum](https://openage.discourse.group/)**. You can also check the weekly development news on [our subreddit](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
