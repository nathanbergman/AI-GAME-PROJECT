# Project Report: AI Dungeon Master System

## Section 1: Supported Gameplay Scenarios


Room exploration is one of the core features, where rooms are procedurally generated based on themes, depth, and surrounding context. These rooms are enhanced with descriptions, items, NPCs, and multiple exits. 

Players can talk with memory-aware NPCs. This means that NPCs remember previous conversations with the player, adding to the immersion. Dialogue adapts to these past interactions, personality traits, and situational context.

AI-generated puzzles provide a challenge. Each puzzle includes a solution, progressive hints, and an item-based reward.

Quests are generated dynamically by NPCs based on their role and the player's level. Objectives are tracked and tied to rewards that help drive the narrative.

The combat system supports turn-based encounters using a behavior-driven AI that selects actions based on player/enemy health, tactics, and difficulty setting. The AI selects actions based on these variables.

Players manage items by equipping, using, and inspecting them. Items include tools, weapons, consumables, and valuable loot. There is generated loot in each rooms, allowing players to pick up and drop items as well.

The system supports saving and loading of the game, preserving player stats, room states, and interactions across sessions. This is a crucial part of the system, allowing the maintenance of immersion in longer games. 

Players can rest to heal and view dynamic stats, allowing strategic planning between encounters. 

The combination of these features ensures a fun experience for players, allowing them to replay the game multiple times without it getting boring and repetative.

---

## Section 2: Prompt Engineering and Parameter Tuning

The system leverages prompt engineering and model parameter settings for different gameplay needs. For NPC dialogue, prompts are customized with the player's name, personality traits, memory logs, and the immediate scenario. Room generation prompts include things such as the type of room, the overall dungeon theme, and the names of adjacent rooms. Prompts for quests and puzzles are enriched with background information. 

Parameter settings:
- `temperature`: 0.3 for deterministic logic (combat), 0.5–0.8 for creative outputs (dialogue, quests, rooms).
- `max_length`: 150 tokens to ensure relevant and concise outputs.
- `response_format`: JSON enforced for all structured generation tasks.

These configurations enable contextually appropriate and stylistically consistent AI behavior.

---

## Section 3: Tool Integration

The system integrates several tools and libraries to support core functionality. The `Ollama API` serves as the language model backend for generating dialogue, quests, rooms, and puzzles. The `FileManager` handles structured file I/O operations, such as saving and retrieving the game, retrieving dungeon layouts, NPC definitions, and the game state. The inverntory is managed by the `ItemSystem`, which defines item properties and tracks item states. Combat is handled by the `TacticalCombatAI` class. Some standard libraries that we used include `random`, `json`, and `os` to enable proceduaral logic and ensure proper data storage. 


---

## Section 4: Planning and Reasoning

The Dungeon Master system has multi-step planning and reasoning capabilities. In combat, the AI evaluates the player and enemys health levels, and selects the best move. NPCs remember previous conversations, which allows them to respond in a way that is consistent with past dialogue and their defined personality. Quest flow is logically constructed, which makes sure that quests are aligned with the narrative and the gameplay. Room generation also incorporates planning, as it factors in previously explored rooms to ensure that new areas maintain the theme and connectivity.

---

## Section 5: Retrieval-Augmented Generation (RAG)

We use retrival-augmented generation (RAG) techniques to maintain coherence and context. NPC memory is stored and used in subsequent promnpts. Past room descriptions are injected into prompts to avoid repitition. Past themes, locations and interaction history are embedded into prompts for immersion. These methods provide a grounded and persistent experience throughout the game.

---

## Section 6: Additional Tools and Innovation

The current architecture supports adding NPC portraits, room art, and audio output (e.g., text-to-speech).

---

## Section 7: Code Design and Quality

The project maintains high standards of software engineering, well-structured and modular. The codebase is divided into different components such as NPC handling, item managment, puzzle generation, and dungeon logic. Each module encapsulates specific functionality and can be extended and modified independently. Encapsulation is maintained through classes, and reusable components are used to support flexibility. Error handling, fallbacks, and logging are used to prevent crashes and errors. This ensures maintainability, testability, and scalability in future development.
