import firebase_admin
from firebase_admin import credentials, firestore
from collections import Counter

# Initialize Firebase
cred = credentials.Certificate("eternalReturnKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Load and Categorize Final Build Items ---
def load_final_build_items():
    docs = db.collection("Final Build").stream()
    categorized = {
        "weapon": [],
        "armor": [],
        "head": [],
        "arm": [],
        "leg": []
    }

    for doc in docs:
        data = doc.to_dict()
        item_type = data.get("type")
        if item_type in categorized:
            categorized[item_type].append(doc.id)
        else:
            print(f"Unknown type '{item_type}' for item '{doc.id}'")

    return categorized

# --- Prompt User to Select One Item per Category ---
def prompt_user_choice(categorized):
    selected = []
    for slot in ["weapon", "armor", "head", "arm", "leg"]:
        options = categorized.get(slot, [])
        print(f"\nSelect your {slot.capitalize()}:")

        for i, name in enumerate(options, 1):
            print(f"  {i}. {name}")

        while True:
            try:
                choice = int(input("Enter number: "))
                if 1 <= choice <= len(options):
                    selected.append(options[choice - 1])
                    break
                else:
                    print("Invalid number.")
            except ValueError:
                print("Please enter a valid number.")
    return selected

# --- Fetch Item Document ---
def fetch_item(item_name, cache):
    if item_name in cache:
        return cache[item_name]
    doc = db.collection('Items').document(item_name).get()
    data = doc.to_dict()
    if data:
        cache[item_name] = data
    return data

# --- Traverse Build Tree Recursively ---
def gather_required_items(targets, starting_items=None):
    cache = {}
    required = Counter()

    def dfs(item_name):
        if item_name in starting_items:
            return  # Skip items the player already starts with
        item = fetch_item(item_name, cache)
        if not item:
            print(f"Missing item: {item_name}")
            return
        if item['tier'] == 1 or not item['components']:
            required[item_name] += 1
        else:
            for comp in item['components']:
                dfs(comp)

    for name in targets:
        dfs(name)

    return required


# --- Load All Locations and Their Items ---
def load_locations():
    locations = {}
    docs = db.collection("Locations").stream()
    for doc in docs:
        data = doc.to_dict()
        locations[doc.id] = set(data.get("spawned_items", []))
    return locations

# --- Greedy Set-Cover to Compute Route ---
def compute_route(required_items, location_data):
    uncovered = set(required_items)
    route = []

    while uncovered:
        best_loc = None
        best_cover = set()

        for loc, items in location_data.items():
            cover = items & uncovered
            if len(cover) > len(best_cover):
                best_loc, best_cover = loc, cover

        if not best_loc:
            print("Unable to find location(s) for:", uncovered)
            break

        route.append((best_loc, best_cover))
        uncovered -= best_cover
        del location_data[best_loc]

    return route

# --- Main Execution ---
if __name__ == "__main__":
    print("Loading Final Build options...")
    categorized = load_final_build_items()

    print("Let's create your build! Choose one item for each slot.")
    target_items = prompt_user_choice(categorized)

    # Items the player starts with (e.g., William's Baseball)
    starting_items = {"Baseball"}

    print("\nGathering required base items...")
    required_counter = gather_required_items(target_items, starting_items)

    print(f"Total base items needed (excluding starting gear): {sum(required_counter.values())}")

    location_data = load_locations()

    # Build route based on counted items (multiset logic)
    route = []
    remaining = required_counter.copy()

    while remaining:
        best_loc = None
        best_items = Counter()

        for loc, items in location_data.items():
            cover = Counter()
            for itm in items:
                if itm in remaining:
                    cover[itm] = min(remaining[itm], 1)  # Grabbing one per visit

            if sum(cover.values()) > sum(best_items.values()):
                best_loc = loc
                best_items = cover

        if not best_loc:
            print("Unable to find enough resources for remaining items:", remaining)
            break

        route.append((best_loc, list(best_items.keys())))
        for itm in best_items:
            remaining[itm] -= best_items[itm]
            if remaining[itm] <= 0:
                del remaining[itm]
        del location_data[best_loc]

    print(f"\nYou need to visit {len(route)} location(s):")
    for loc, items in route:
        print(f"- {loc}: collect {', '.join(sorted(items))}")
