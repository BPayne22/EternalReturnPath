# EternalReturnPath

**EternalReturnPath** is a Python-based tool designed to generate efficient item routes for the game *Eternal Return*. Players must navigate across 18+ unique locations to gather resources and craft powerful weapons and armor before engaging other competitors. Completing your build quickly provides a significant tactical advantage — and this program helps you do exactly that.

It prompts users to input their desired build, searches a Firebase database for item data and crafting components, then analyzes all available map zones to determine the fastest possible scavenging route — telling them exactly where to go and what items to collect.

---

## How It Works

This program connects to a Firebase backend containing three main collections: `Final Build`, `Items`, and `Locations`.

- **Final Build** — Contains all final build items (tier 4) for each gear slot. These are the high-priority items players aim to craft before fights begin.
- **Items** — Holds all tier 1 to tier 4 items, including their crafting components and spawn locations (for tier 1).
- **Locations** — Represents each map zone with a `spawned_items` field listing all items that can be found in that area.

Upon starting, the program prompts the user to choose one item for each gear slot:
1. Weapon  
2. Head  
3. Armor  
4. Arm  
5. Leg  

It then calculates the components required to build each item and generates the shortest optimal route for gathering everything needed — ensuring fast and efficient progression.

---

###Project Goal

One of my main goals in developing this tool was to strengthen my understanding of database architecture and clean backend design. In previous projects, I’ve often worked with cluttered or inconsistent frameworks set up by teammates, which made collaboration and scaling frustrating. This time, I focused on creating a well-organized and intuitive database structure that allows the program to pull data reliably and operate with precision — and I’m proud of how seamlessly it performs.
