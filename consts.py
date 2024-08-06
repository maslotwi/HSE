import struct

hero_names = ("Adela",
              "Adelaide",
              "Adrienne",
              "Aenain",
              "Aeris",
              "Agar",
              "Aine",
              "Aislinn",
              "Ajit",
              "Alagar",
              "Alamar",
              "Alkin",
              "Anabel",
              "Andal",
              "Andra",
              "Arlach",
              "Ash",
              "Astra",
              "Astral",
              "Axsis",
              "Ayden",
              "Beatrice",
              "Bertram",
              "Bidley",
              "Boragus",
              "Brissa",
              "Broghild",
              "Bron",
              "Caitlin",
              "Calh",
              "Calid",
              "Casmetra",
              "Cassiopeia",
              "Catherine",
              "Celestine",
              "Charna",
              "Christian",
              "Ciele",
              "Clancy",
              "Clavius",
              "Corkes",
              "Coronius",
              "Crag Hack",
              "Cuthbert",
              "Cyra",
              "Dace",
              "Damacon",
              "Daremyth",
              "Dargem",
              "Darkstorn",
              "Deemer",
              "Derek",
              "Dessa",
              "Dracon",
              "Drakon",
              "Dury",
              "Eanswythe",
              "Edric",
              "Elleshar",
              "Elmore",
              "Eovacius",
              "Erdamon",
              "Fafner",
              "Fiona",
              "Fiur",
              "Floribert",
              "Frederick",
              "Galthran",
              "Gelare",
              "Gelu",
              "Gem",
              "Geon",
              "Gerwulf",
              "Gird",
              "Giselle",
              "Gretchin",
              "Grindan",
              "Gundula",
              "Gunnar",
              "Gurnisson",
              "Haart Lich",
              "Halon",
              "Henrietta",
              "Ignatius",
              "Ignissa",
              "Illor",
              "Ingham",
              "Inteus",
              "Iona",
              "Isra",
              "Ivor",
              "Jabarkas",
              "Jaegar",
              "Jeddite",
              "Jenova",
              "Jeremy",
              "Josephine",
              "Kalt",
              "Kilgor",
              "Kinkeria",
              "Korbac",
              "Krellion",
              "Kyrre",
              "Labetha",
              "Lacus",
              "Leena",
              "Lord Haart",
              "Lorelei",
              "Loynis",
              "Luna",
              "Malcom",
              "Malekith",
              "Manfred",
              "Marius",
              "Melchior",
              "Melodia",
              "Mephala",
              "Merist",
              "Miriam",
              "Mirlanda",
              "Moandor",
              "Monere",
              "Morton",
              "Murdoch",
              "Mutare",
              "Mutare Drake",
              "Nagash",
              "Neela",
              "Nimbus",
              "Nymus",
              "Octavia",
              "Olema",
              "Oris",
              "Orrin",
              "Pasis",
              "Piquedram",
              "Pyre",
              "Ranloo",
              "Rashka",
              "Rion",
              "Rissa",
              "Roland",
              "Rosic",
              "Ryland",
              "Sam",
              "Sandro",
              "Sanya",
              "Saurug",
              "Sephinroth",
              "Septienna",
              "Serena",
              "Shakti",
              "Shiva",
              "Sir Mullich",
              "Solmyr",
              "Sorsha",
              "Spint",
              "Straker",
              "Styg",
              "Sylvia",
              "Synca",
              "Tamika",
              "Tancred",
              "Tark",
              "Tavin",
              "Tazar",
              "Terek",
              "Thane",
              "Thant",
              "Theodorus",
              "Thorgrim",
              "Thunar",
              "Tiva",
              "Todd",
              "Torosar",
              "Tyraxor",
              "Tyris",
              "Ufretin",
              "Uland",
              "Valeska",
              "Verdish",
              "Vey",
              "Victoria",
              "Vidomina",
              "Vokial",
              "Voy",
              "Wrathmont",
              "Wynona",
              "Wystan",
              "Xarfax",
              "Xeron",
              "Xsi",
              "Xyron",
              "Yog",
              "Zilare",
              "Ziph",
              "Zubin",
              "Zydar")
skill_ids = {
    'Air Magic': 15,
    'Archery': 1,
    'Armorer': 23,
    'Artillery': 20,
    'Ballistics': 10,
    'Diplomacy': 4,
    'Eagle Eye': 11,
    'Earth Magic': 17,
    'Estates': 13,
    'Fire Magic': 14,
    'First Aid': 27,
    'Intelligence': 24,
    'Interference': 28,
    'Leadership': 6,
    'Learning': 21,
    'Logistics': 2,
    'Luck': 9,
    'Mysticism': 8,
    'Navigation': 5,
    'Necromancy': 12,
    'Offense': 22,
    'Pathfinding': 0,
    'Resistance': 26,
    'Scholar': 18,
    'Scouting': 3,
    'Sorcery': 25,
    'Tactics': 19,
    'Water Magic': 16,
    'Wisdom': 7,
}

troop_ids = {
          'Pikeman': 0,
          'Halberdier': 1,
          'Archer': 2,
          'Marksman': 3,
          'Griffin': 4,
          'Royal griffin': 5,
          'Swordsman': 6,
          'Crusader': 7,
          'Monk': 8,
          'Zealot': 9,
          'Cavalier': 10,
          'Champion': 11,
          'Angel': 12,
          'Archangel': 13,
          'Centaur': 14,
          'Centaur capitan': 15,
          'Dwarf': 16,
          'Battle dwarf': 17,
          'Wood elf': 18,
          'Grand elf': 19,
          'Pegasus': 20,
          'Silver pegasus': 21,
          'Dendroid guard': 22,
          'Dendroid solider': 23,
          'Unicorn': 24,
          'War unicorn': 25,
          'Green dragon': 26,
          'Gold dragon': 27,
          'Gremlin': 28,
          'Master gremlin': 29,
          'Stone gargoyle': 30,
          'Obsidian gargoyle': 31,
          'Stone golem': 32,
          'Iron golem': 33,
          'Mage': 34,
          'Arch mage': 35,
          'Genie': 36,
          'Master genie': 37,
          'Naga': 38,
          'Naga queen': 39,
          'Giant': 40,
          'Titan': 41,
          'Imp': 42,
          'Familiar': 43,
          'Gog': 44,
          'Magog': 45,
          'Hell hound': 46,
          'Cerberus': 47,
          'Daemon': 48,
          'Horned daemon': 49,
          'Pit fiend': 50,
          'Pit lord': 51,
          'Efreet': 52,
          'Efreet sultan': 53,
          'Devil': 54,
          'Arch Devil': 55,
          'Skeleton': 56,
          'Skeleton Warrior': 57,
          'Walking dead': 58,
          'Zombie': 59,
          'Wight': 60,
          'Wraith': 61,
          'Vampire': 62,
          'Vampire lord': 63,
          'Lich': 64,
          'Power Lich': 65,
          'Black knight': 66,
          'Dead knight': 67,
          'Bone dragon': 68,
          'Ghost dragon': 69,
          'Troglodyte': 70,
          'Infernal troglodyte': 71,
          'Harpy': 72,
          'Harpy hag': 73,
          'Beholder': 74,
          'Evil eve': 75,
          'Medusa': 76,
          'Medusa queen': 77,
          'Minotaur': 78,
          'Minotaur king': 79,
          'Manticore': 80,
          'Scorpicore': 81,
          'Red dragon': 82,
          'Black dragon': 83,
          'Goblin': 84,
          'Hobgoblin': 85,
          'Wolf rider': 86,
          'Wolf raider': 87,
          'Orc': 88,
          'Orc chieftain': 89,
          'Ogre': 90,
          'Ogre mage': 91,
          'Roc': 92,
          'Thunderbird': 93,
          'Cyclops': 94,
          'Cyclops king': 95,
          'Behemoth': 96,
          'Ancient behemoth': 97,
          'Gnoll': 98,
          'Gnoll marauder': 99,
          'Lizardman': 100,
          'Lizard warrior': 101,
          'Serpent fly': 102,
          'Dragonfly': 103,
          'Basilisk': 104,
          'Greater Basilisk': 105,
          'Gorgon': 106,
          'Mighty gorgon': 107,
          'Wyvern': 108,
          'Wyvern Monarch': 109,
          'Hydra': 110,
          'Chaos hydra': 111,
          'Air elemental': 112,
          'Earth elemental': 113,
          'Fire elemental': 114,
          'Water elemental': 115,
          'Golem': 116,
          'Diamond golem': 117,
          'Pixies': 118,
          'Sprites': 119,
          'Psychic elemental': 120,
          'Magic elemental': 121,
          'Ice elemental': 123,
          'Magma elemental': 125,
          'Storm elemental': 127,
          'Energy elemental': 129,
          'Firebird': 130,
          'Phoenix': 131,
          'Azure dragons': 132,
          'Crystal dragons': 133,
          'Faerie dragons': 134,
          'Rust dragons': 135,
          'Enchanters': 136,
          'Sharpshooters': 137,
          'Halflings': 138,
          'Peasants': 139,
          'Boars': 140,
          'Mummies': 141,
          'Nomads': 142,
          'Rogues': 143,
          'Trolls': 144,
          'Catapult': 145,
          'Ballista': 146,
          "First Aid Tent": 147,
          "Ammo Cart": 148,
          "Arrow Tower": 149,  # Crashes the game on interactions
          "Cannon": 150,
          "Sea Dog": 151,
          "Electric Tower": 152,  # Crashes the game on interactions
          "Nymph": 153,
          "Oceanid": 154,
          "Crew Mate": 155,
          "Seaman": 156,
          "Pirate": 157,
          "Corsair": 158,
          "Stormbird": 159,
          "Ayssid": 160,
          "Sea Witch": 161,
          "Sorceress": 162,
          "Nix": 163,
          "Nix Warrior": 164,
          "Sea Serpent": 165,
          "Haspid": 166,
          "Satyr": 167,
          "Fangarm": 168,
          "Leprechaun": 169,
          "Steel Golem": 170,
          "Halfling Grenadier": 171,
          "Mechanic": 172,
          "Engineer": 173,
          "Armadillo": 174,
          "Bellwether Armadillo": 175,
          "Automaton": 176,
          "Sentinel Automaton": 177,
          "Sandworm": 178,
          "Olgoi-Khorkhoi": 179,
          "Gunslinger": 180,
          "Bounty Hunter": 181,
          "Couatl": 182,
          "Crimson Couatl": 183,
          "Dreadnought": 184,
          "Juggernaut": 185,
          }

hero_ids = (
    'Orrin', 'Valeska', 'Edric', 'Sylvia', 'Lord Haart', 'Sorsha', 'Christian', 'Tyris', 'Rion', 'Adela', 'Cuthbert',
    'Adelaide', 'Ingham', 'Sanya', 'Loynis', 'Caitlin', 'Mephala', 'Ufretin', 'Jenova', 'Ryland', 'Thorgrim', 'Ivor',
    'Clancy', 'Kyrre', 'Coronius', 'Uland', 'Elleshar', 'Gem', 'Malcom', 'Melodia', 'Alagar', 'Aeris', 'Piquedram',
    'Thane', 'Josephine', 'Neela', 'Torosar ', 'Fafner', 'Rissa', 'Iona', 'Astral', 'Halon', 'Serena', 'Daremyth',
    'Theodorus', 'Solmyr', 'Cyra', 'Aine', 'Fiona', 'Rashka', 'Marius', 'Ignatius', 'Octavia', 'Calh', 'Pyre', 'Nymus',
    'Ayden', 'Xyron', 'Axsis', 'Olema', 'Calid', 'Ash', 'Zydar', 'Xarfax', 'Straker', 'Vokial', 'Moandor', 'Charna',
    'Tamika', 'Isra', 'Clavius', 'Galthran', 'Septienna', 'Aislinn', 'Sandro', 'Nimbus', 'Thant', 'Xsi', 'Vidomina',
    'Nagash', 'Lorelei', 'Arlach', 'Dace', 'Ajit', 'Damacon', 'Gunnar', 'Synca', 'Shakti', 'Alamar', 'Jaegar',
    'Malekith', 'Jeddite', 'Geon', 'Deemer', 'Sephinroth', 'Darkstorn', 'Yog', 'Gurnisson', 'Jabarkas', 'Shiva',
    'Gretchin', 'Krellion', 'Crag Hack', 'Tyraxor', 'Gird', 'Vey', 'Dessa', 'Terek', 'Zubin', 'Gundula', 'Oris',
    'Saurug', 'Bron', 'Drakon', 'Wystan', 'Tazar', 'Alkin', 'Korbac', 'Gerwulf', 'Broghild', 'Mirlanda', 'Rosic', 'Voy',
    'Verdish', 'Merist', 'Styg', 'Andra', 'Tiva', 'Pasis', 'Thunar', 'Ignissa', 'Lacus', 'Monere', 'Erdamon', 'Fiur',
    'Kalt', 'Luna', 'Brissa', 'Ciele', 'Labetha', 'Inteus', 'Aenain', 'Gelare', 'Grindan', 'Sir Mullich', 'Adrienne',
    'Catherine', 'Dracon', 'Gelu', 'Kilgor', 'Haart Lich', 'Mutare', 'Roland', 'Mutare Drake', 'Boragus', 'Xeron',
    'Corkes', 'Jeremy', 'Illor', 'Derek', 'Leena', 'Anabel', 'Cassiopeia', 'Miriam', 'Casmetra', 'Eovacius', 'Spint',
    'Andal', 'Manfred', 'Zilare', 'Astra', 'Dargem', 'Bidley', 'Tark', 'Elmore', 'Beatrice', 'Kinkeria', 'Ranloo',
    'Giselle', 'Henrietta', 'Sam', 'Tancred', 'Melchior', 'Floribert', 'Wynona', 'Dury', 'Morton', 'Celestine', 'Todd',
    'Agar', 'Bertram', 'Wrathmont', 'Ziph', 'Victoria', 'Eanswythe', 'Frederick', 'Tavin', 'Murdoch')

colors = ("Red", "Blue", "Tan", "Green", "Orange", "Purple", "Teal", "Pink")

skill_names = {y: x for x, y in skill_ids.items()}
troop_names = {y: x for x, y in troop_ids.items()}

primary_skills = 1107
secondary_skill_count = 222
secondary_skills = 166
affiliation = -1
coordinates = -35

troop_id_array = 110
troop_count_array = 138

player_array = 0x20AD0
player_color = -204
player_hero_count = player_color + 1
player_heroes = player_color + 8
player_resources = -48
player_selected_town = -9*16+3

game_manager_address = 0x699538
adventure_manager_address = 0x6992B8

town_array = 0x21614
town_struct = "bb?xbBB?"

game_map = 92
map_size = 212
