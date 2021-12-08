Title: Engine Core Modules
Date: 2021-12-15
Tags: roadmap, gamestate, renderer, presenter, curves
Authors: jj, heinezen
Summary: our next steps for creating the engine core modules

- last year we talked about the gamestate implementation
- this year, we have to implement everything else
- how hard could that be, right?

## Current state

- Actual gamestate is a small part of the engine
- Other modules (see figure)
    - Eventsystem: Tracks events in the game that result in something happening
    - Renderer: Shows whats happening on the screen
    - Presenter: Receives user inputs and forwards/translates them to the engine
    - (Networking: Receives network inputs and forwards them to the engine)
- For creating a game, all of them have to be coupled

## Recap: Calculating the gamestate

- Those who followed our blogposts about the modding API already know how the several gamepay elements will be addressed
- Short summary as a refresher:
    - Ingame units have so-called abilities
    - Abilities are traits that define what a unit does (e.g. move, attack, gather), is (e.g. selectable) or has (e.g. attributes like HP)
    - In the game data, ability objects store the necessary data for using the ability, e.g. movement speed
    - In the engine, the ability is associated with a gameplay system that, when called, takes the data and does an action, e.g. move the unit from A to B

## From gameplay systems to gameplay mechanics

- This sounds easy enough until you realize that this does not yet suffice for the complex gameplay mechanics that you find in AoE2
- An action is very easy to model, but most gameplay mechanics are multi-stage activity
- Take the gathering mechanic in AoE2 for example
    - Let me break it down for you
    1. The player commands the villager to a resource (beginning of the task)
    2. the villager moves to the resource (Move ability)
    3. the villager starts gathering the resource (Gather ability)
        - the villager stops gathering on a specific breakout condition, i.e. its resource is full
    4. villager locates a resource dropsite (DropSite ability)
    5. villager moves to a resource dropsite (Move ability)
    6. start again at 2.
- this activity for a relatively "simple" mechanic can already get reasonably complex
- can even result in branching paths
- things also might happen in parallel

- these types of mechanics are common in RTS games
- typically all tasks that involve movement are like this
- "hardcode everything": not an option

- Solution: activity system using a node graph
- node graph described the flow for the activity
    - node can be any action (move, gather, attack)
    - path to next chosen based on event, e.g. resource storage is full
    - branching paths with nodes that check conditions
- node graph can be the same for every unit of a unit type, e.g. villager
    - activity flow is always the same
    - at runtime, the unit only needs to know the node that is currently active and the events that trigger the choosing of paths
    - behavior of unit is controlled by following the activity flow in the node graph

- since engine is event-based, this can be easibly modelled
- events are registered on curves
- entity manager calls activity system when a new activity event happens
- when a unit reaches a new node in the flow graph
    - starts the associated gameplay system
    - register events for advancing to next node
- this way, complete behavior can be encapsuled in a giant flow graph, but stays simple enough to be expandable

## Renderer

- Renderer is stuffed by gamestate with animations
- displays animation on screen

- challenges comes from the fact that rendered animations color pixels depending on game data
- example: player color depends on player ID (or a color blind setting)
- renderer needs to know how to handle these special pixels

- In the animation, these pixels are marked with a command bit
- pixel color RGBA => 32 Bit = 8R8G8G8A
- openage uses the last bit in the alpha channel as flag for a special draw command
- if bit is 0 (i.e. alpha value is even), use a custom shader
    - RGB channels (24 Bit) can be used as a command payload (e.g. a palette index)
- that leaves modders with 128 regular alpha values for normal draw commands and 128 potential commands

- In the engine, the renderer receives animation and all "associated data" from gamestate (usually by system that starts an animated action)
- associated data can be an anchr point for example (if the animated entity is a moving unit)
- but can be anything from the gamestate, e.g. player ID of the unit
- engine will have a lookup table that defines what data it sends the renderer

## Game Control

- input events from peripherals have to be translated to game events
- e.g. commands for units
- usually also follows a mapping (hotkeys etc.)
- separation of ingame and outgame events
    - ingame: units, player factions (as concepts in the game), the game world
    - outgame: command queue, input events from the player/person in front of the screen

- define what outgame players can do ingame via a "Controller"
    - what they have control over (which ingame faction)
    - how their inputs should be translated to ingame events (hotkeys)
- Controller is a gateway to the gamestate
    - basic access control: ensures that player can only control units that are assigned to them
    - translation of inputs to ingame events is separated from gameplay
    - can be changed at runtime without affecting game (exchange human player with AI player)
    - also: switching control of ingame factions is easy, whch is useful for debugging
- Controllers will not only be used for human players
    - AI, networking, scripting will communicate with gamestate using controllers
    - all theoretically will have the same capabilities as humans
    - gateway could be generic enough that all kinds of outgame input types can be modelled
    - potentially interesting for AI developers or scripters who like to have a lot of control over ingame events
