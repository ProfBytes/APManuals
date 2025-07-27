import json
from itertools import combinations_with_replacement
import yaml


# Locations
# Build <Unit>
# Beat <n> player FFA AI at <difficulty>
# Beat <a> vs. <b> AI at <difficulty> (could do allies at one difficulty and enemies at another)
# Beat <n> team AI at <difficulty>

class Unit:

    def __init__(self, name):
        self.name = name


class Building:

    def __init__(self, name, units):
        self.name = name
        self.units = units


class Faction:

    def __init__(self, name, buildings):
        self.name = name
        self.buildings = buildings


def generateBalancedTeams(numTeams, maxPlayers, maxTeamSize):
    maps = []
    for alliedTeam in range(1, maxTeamSize + 1):
        if alliedTeam + alliedTeam * (numTeams - 1) <= maxPlayers and  numTeams * alliedTeam > numTeams:
            mapString = str(alliedTeam)
            for i in range(numTeams - 1):
                mapString += "v" + str(alliedTeam)
            maps.append(mapString)
    return maps

def generateUnbalancedTeams(numTeams, maxPlayers, maxTeamSize):
    maps = []
    for alliedTeam in range(1, maxTeamSize + 1):
        for enemyTeam in range(1, maxTeamSize + 1):
            if alliedTeam + enemyTeam * (numTeams - 1) <= maxPlayers and alliedTeam + (
                    numTeams - 1) * enemyTeam > numTeams and alliedTeam != enemyTeam:
                mapString = str(alliedTeam)
                for i in range(numTeams - 1):
                    mapString += "v" + str(enemyTeam)
                maps.append(mapString)
    return maps


def generateMaps(maxTeams, maxPlayers, maxTeamSize, maxFFASize):
    teamList = []
    unbalancedList = []
    for a in range(2, maxFFASize + 1):
        teamList.append(str(a) + " Player FFA")

    for a in range(2, maxTeams + 1):
        teamList += generateBalancedTeams(a, maxPlayers, maxTeamSize)
        unbalancedList += generateUnbalancedTeams(a, maxPlayers, maxTeamSize)

    return teamList, unbalancedList


def generateLocations(factions, difficultyList, teamsList):
    with open("locations.json", 'w') as f:
        data = []
        for faction in factions:
            numUnits = 0
            for building in faction.buildings:
                numUnits += len(building.units)
            data.append({
                "name": "Destroy " + faction.name + " worker",
                "category": ["Destroy "+faction.name],
                "requires": "|" + faction.name + "|"
            })
            data.append({
                "name": "Destroy " + faction.name + " command structure",
                "category": ["Destroy "+faction.name],
                "requires": "|" + faction.name + "|"
            })
            data.append({
                "name": "Destroy " + faction.name + " production structure",
                "category": ["Destroy "+faction.name],
                "requires": "|" + faction.name + "|"
            })
            data.append({
                "name": "Destroy " + faction.name + " tech structure",
                "category": ["Destroy "+faction.name],
                "requires": "|" + faction.name + "|"
            })
            for difficulty in difficultyList:
                for teams in teamsList:
                    index = difficultyList.index(difficulty)
                    numRequired = 1
                    if index != 0:
                        numRequired = max(1, int(numUnits * index / len(difficultyList)))
                    unbalanced = []
                    if len(teams.split("v")) > 1:
                        unbalanced = ["Unbalanced Teams"]
                    data.append({
                        "name": "Beat " + teams + " against " + difficulty + " as " + faction.name,
                        "region": "Win as " + faction.name,
                        "category": ["Destroy "+faction.name],
                        "categories": ["Win as "+faction.name, "Beat "+difficulty, "Clear "+teams+" match"] + unbalanced,
                        "requires": "|"+faction.name+"| AND |"+difficulty+"| AND |"+teams+"| AND |@"+faction.name+" Units:"+str(numRequired)+"|"
                    })
        data.append({
            "name": "Beat Hardest Maps",
            "requires": "|@Factions:all| AND |@Units:all| AND |@Maps:all| AND |@AI Difficulties:all|",
            "victory": True
        })
        json.dump(data, f, indent=2)

def generateCategories(factions):
    with open("categories.json", 'w') as f:
        data = {"Unbalanced Maps": {"yaml_option": ["UnbalancedMaps"]}}
        json.dump(data, f, indent=2)

def generateOptions(factions, difficultyList, teamsList):
    with open("options.json", 'w') as f:
        user = {}
        data = {"user": user}
        for faction in factions:
            user[faction.name+"_Starting_Unit"] = {
                "type": "Choice",
                "description": ["Choose your starting unit for "+faction.name],
                "values": {},
                "default": 0,
                "allow_custom_value": False,
                "group": "Starting Unit"
            }
            index = 0
            for building in faction.buildings:
                for unit in building.units:
                    user[faction.name+"_Starting_Unit"]["values"][faction.name+" - "+unit.name] = index
                    index += 1
        json.dump(data, f, indent=2)
def generateItems(factions, difficultyList, maps, unbalancedMaps):
    with open("items.json", 'w') as f:
        data = []
        for difficulty in difficultyList:
            data.append({
                "count": 1,
                "name": difficulty,
                "category": ["AI Difficulties"],
                "progression": True
            })
        for teams in maps:
            data.append({
                "count": 1,
                "name": teams,
                "category": ["Maps"],
                "progression": True
            })
        for teams in unbalancedMaps:
            data.append({
                "count": 1,
                "name": teams,
                "category": ["Maps", "UnbalancedMaps"],
                "progression": True
            })
        for faction in factions:
            data.append({
                "count": 1,
                "name": faction.name,
                "category": ["Factions"],
                "progression": True
            })
            for building in faction.buildings:
                for unit in building.units:
                    data.append({
                        "count": 1,
                        "name": faction.name+" - "+unit.name,
                        "category": [faction.name + " Units", "Units"],
                        "progression": True
                    })
        json.dump(data, f, indent=2)


def generateRegions(factions, maps):
    with open('regions.json', 'w') as file:
        data = {}
        for faction in factions:
            data["Win as "+faction.name] = {
                "starting": True,
                "connects_to": [],
                "requires": "|"+faction.name+"|"
            }
        json.dump(data, file, indent=2)

def generateGame(game, author, difficulty):
    with open("game.json", 'w') as file:
        data = {
            "$schema": "https://github.com/ManualForArchipelago/Manual/raw/main/schemas/Manual.game.schema.json",
            "game": game,
            "creator": author,
            "filler_item_name": "One supply",
            "death_link": False,
            "starting_index": 1,
            "starting_items": [
                {
                    "item_categories": [
                        "Maps"
                    ],
                    "random": 1
                },
                {
                    "items": [
                        difficulty
                    ]
                }
            ]
        }
        json.dump(data, file, indent=2)


if __name__ == '__main__':
    with open('definitions.yml', 'r') as file:
        data = yaml.safe_load(file)
        print(data)
        factions = []
        for faction in data['Factions']:
            factionData = Faction(faction, [])
            for building in data['Factions'][faction]:
                buildingData = Building(building, [])
                for unit in data['Factions'][faction][building]:
                    unitData = Unit(unit)
                    buildingData.units.append(unitData)
                factionData.buildings.append(buildingData)
            factions.append(factionData)

        maxTeams = int(data["Maps"]["MaxTeams"])
        maxPlayers = int(data["Maps"]["MaxPlayers"])
        maxTeamSize = int(data["Maps"]["MaxTeamSize"])
        maxFFASize = int(data["Maps"]["MaxFFASize"])
        difficultyList = data["Difficulties"]
        game = data["Game"]
        author = "RTSBuilder-ProfBytes"

        teamsList, unbalancedList = generateMaps(maxTeams, maxPlayers, maxTeamSize, maxFFASize)
        generateItems(factions, difficultyList, teamsList, unbalancedList)

        generateLocations(factions, difficultyList, teamsList)
        generateRegions(factions, teamsList)
        generateCategories(factions)
        generateOptions(factions, difficultyList, teamsList)

        generateGame(game, author, difficultyList[0])