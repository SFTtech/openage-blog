Title: T1: Curves logic
Date: 2017-08-22
Category: technical
Tags: curves, API
Authors: jw
Summary: curves are simulation environment independent of discretisation

The most important component of most games is the core gamestate. It contains all information relevant for the internal game logic, which the other components take into account and use for example for rendering or network transmission.

## Gamestate Interpolation

The naive approach to this problem would be having a list of objects, every object has a position and hitpoints. If a object receives a move command, we can calculate a path, and move it along this path, frame by frame with deterministic lockstepping, whereby with the knowledge of how much time `dt` has passed since the last frame, the current `position` and the current `speed` of a unit, we can integrate the position like

``` python
o.position = o.position + speed * dt
```

This approach has the major benefit of being really simple, and there is not much fancyness involved.
This is the most simple, the [Euler integration](https://en.wikipedia.org/wiki/Euler_method) method.
There are many more, more accurate and more calculation-heavy interpolations, but they all have the same drawbacks.

1. It is really hard to go back in time without keeping a store of old values.
2. You diverge from your optimal path just because of numerical effects.
3. You have to lay hand on every single object to update their position on each tick, even if they are not rendered at the moment.

## Curves - the answer of your dreams?

And so we came up with another idea - the Curves, [inspired](https://blog.forrestthewoods.com/the-tech-of-planetary-annihilation-chronocam-292e3d6b169a#.lmxbu3vld) by Planetary Annihilation.

A curve is a collection of

``` python
#  time    value
0: (0,     (50, 50)),
1: (150,   (75, 0)),
2: (450,   (0, 30)),
3: (750,   (75, 30)),
...
```

The curve is visualized in the below image, whereby tha ball is flying in different directions.

![Curve Graph]({filename}/images/T0001-timeline.png)

containing for example the path of an object on the map over the time from 0 to 750ms.
What we see there is the list of keyframes to describe the position of an object, going from middle to right to left and back playing ping-pong.

To access for example the position of the object at `now=100ms` we can calulate between two keyframes: `(t0, k0)` and `(t1, k1)`. We hereby use element-wise addition and substraction of vectors and multiplication of a vector with a scalar.

``` python
o.position['100ms'] = k0 + (k0 - k1) * (now - t0) / (t1 - t0)
= (50, 50) +  ((75, 0) - (50, 50)) * (100 - 0) / (150 - 0)
= (50, 50) + (25, -50) * 100/150
= (50 + 25 * 0.66, 50 - 50 * 0.66)
= (66.5, 17)
```

Which is right between the two key-frames - the red dot in the above image.

## It is awesome!

Now to move from a ball playing ping pong to units.
As you see - it is slightly more expensive to calulate the exact position of one unit, but this does not need to happen every frame for every unit, but instead only for those that are currently on screen. So huge armies, that are larger than a screen do not have to be interpolated as whole all the time.

Another thing that comes free house is that it is very simple to go back to any point in time, since the old keyframes are not overwritten for new values.
And for RAM saving purposes, we can always remove keyframes that are not relevant anymore and lay some time in the past.

This approach also does not accumulate floating point errors as fast as frame-by-frame interpolation, since key-frames lay further appart, and are not calculated as often.
The constant floating point error that occurs within the interpolation is negligible, since it is not integrated over.

## Or maybe not?

Of course this approach has major drawbacks, especially if the future of a object is changing very often or is not predictable at all. This is the case for any user-controlled unit, because users are the major source of randomness, and curves do not like users.
But for command-driven genres like adventure-games, puzzle-games or realtime strategy games this comes in handy.
We only have to calculate the path of a unit once, and as long as we do not look, we do not care where the unit is - except if it collides with something else on the path. But that is a story for another time.

## So can everything be represented as a curve?

There is a short answer to that, and a long one. the short answer is: *Yes!*. And not can. Must!

The long answer is: to be able to fully integrate the curve logic into the game logic, it is not sufficient to only use positions of objects. it is neccessary to track the hitpoints as well - because the path of the unit depends on the hitpoints of the building the unit is currently avoiding.
And the hitpoints of the unit depend on how many enemies are currenytly attacking it. How many enemies are attacking it depends on when the unit was built in the barracks. When the unit was built in the barracks depends on how many ressources are there ... gathering ... villager producing ... existence of town center ... it would go on all night.
So every value in the gamestate has to be time-dependent - a curve.

The smallest common datatypes that can be used here are linear interpolated curves, as seen above, and discrete curves, that hold a value until the next keyframe.
Discrete curves do not need to be interpolated, and so they can contain data, that does not define "-" or "+", like strings and objects and nyan references.


## Integration

Now you might wonder how `curves` works together with the rest of the engine?
We've got many ideas there and are experimenting how the simulation could be done best,
but the overall structure boils down to this:

<pre>
client:
[nyan] <-> simulation playback/prediction with curves <-> [presenter: gui, renderer, audio]
           ^
           | network
server:    v
[nyan] <-> authoritative simulation with curves
</pre>

This architecture allows us to have one dedicated game server (which can be run by any player)
and users can still do client-side modding.

Once the plan is more clear we'll explain the inner workings of the simulation and prediction.

## Questions

Wanna discuss those ideas? Visit [our subreddit /r/openage](https://reddit.com/r/openage)!

As always, if you want to reach us directly in the dev chatroom:

* Matrix: `#sfttech:matrix.org`
* IRC: `#sfttech` on freenode.net
