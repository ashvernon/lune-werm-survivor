# Lune Werm: Survivor

<p align="center">
  <img src="game_poster.png" alt="Game Poster" width="400" />
</p>

## Overview

**Lune Werm: Survivor** is a desert-survival game built with Pygame. Guide your lone survivor through shifting dunes, collect scarce water, and avoid the subterranean Werms that stalk beneath the sands.

---

## Features

* **Procedurally placed** rocks, water caches, and villages
* **Dynamic Werm AI** that steers around obstacles to hunt you
* **Stamina bar**: collect water to replenish, rest in villages to slowly regenerate
* **Zooming camera**: mouse wheel to zoom in/out on the world

---

## Installation & Running

1. **Clone the repo**

   ```bash
   git clone https://github.com/ashvernon/lune-werm-survivor.git
   cd lune-werm-survivor
   ```
2. **(Optional) Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv

   # Activate the environment
   # Windows:
   venv\\Scripts\\activate
   # macOS / Linux:
   source venv/bin/activate

   pip install pygame
   ```
3. **Run the game**

   ```bash
   python main.py
   ```

---

## Controls

* **Arrow keys**: move your character
* **Mouse wheel**: zoom camera in/out
* **Collect** blue water caches to refill stamina
* **Visit** villages for passive stamina regeneration
* **Avoid** the Werms—collision means **Game Over**
* **Press** `R` when “Game Over” to restart

---

## License

This project is released under the MIT License. Feel free to fork and experiment!
