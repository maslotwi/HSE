#!/usr/bin/python3
import consts
from h3editor import H3editor, Skill, Troop, Town
from flask import Flask, render_template, request, redirect, url_for, Response

app = Flask(__name__)


def skills_html(name):
    skills = editor.get_skills(name)
    dropdown_options = "<option value='' selected></option>"
    for i in sorted(consts.skill_ids):
        dropdown_options += f"<option value='{i}'>{i}</option>"

    table = [
        f"<td colspan='2'><select autocomplete='off' id='slot{i + 1}'>{dropdown_options}</select><input class='levelEdit' autocomplete='off' min='0' max='3' type='number' value='0' id='level{i + 1}'></input></td>"
        for i in range(8)]

    for skill in skills:
        dropdown_options = ""
        for i in sorted(consts.skill_ids):
            dropdown_options += f"<option value='{i}' {'selected' if i == skill.name else ''}>{i}</option>"
        table[
            skill.slot - 1] = f"<td colspan='2'><select autocomplete='off' id='slot{skill.slot}' selected='{skill.name}'>{dropdown_options}</select><input class='levelEdit' autocomplete='off' min='0' max='3' type='number' value='{skill.lvl}' id='level{skill.slot}'></input></td>"

    w = f"<tr><th colspan='4' class='player{editor.get_team(name) + 1}'>{name}</th></tr>"
    for i in range(4):
        w += f"<tr>{table[i * 2]}{table[i * 2 + 1]}</tr>"

    w += "<tr>"
    for i, level in enumerate(editor.get_primary_skills(name)):
        w += f"<td><input class='resource' autocomplete='off' min='0' type='number' value='{level}' id='primary{i}'></input></td>"
    # for no, i in enumerate(consts.hero_ids):
    #     msg = f"{no} {i} {list(editor.get_skills(i))}"
    #     print(msg.ljust(100), editor.dereference(editor.mem_locations[i].main + consts.secondary_skills, "b"*29),
    #           editor.dereference(editor.mem_locations[i].slots, "b"*29))
    return w + f'</tr><tr><td colspan="4"><button onclick="save_hero(\'{name}\')">save</button></td></tr>'


def players_html():
    players = [editor.get_player(i) for i in range(8)]
    table = ""
    for i in players:
        table += f"<tr class='player{i.color + 1}'>"
        table += f"<th>{i.name}</th>"
        for j in i.heroes:
            table += f"<td><a class='player{i.color + 1}' href='/edit/{j}'>{j}</a></td>"
        if len(i.heroes) < 8:
            table += f"<td colspan='{8 - len(i.heroes)}'></td>"
        for j, amnt in enumerate(i.resources[:-1]):
            table += f"<td><img src='/static/resources/res{j + 1}.png'><input autocomplete='off' id='r{i.color}{j}' value='{amnt}' class='resource' type='number' min='0'></input></td>"
        table += f"<td><img src='/static/resources/res{7}.png'><input autocomplete='off' id='r{i.color}6' value='{i.resources[-1]}' class='gold' type='number' min='0'></input></td>"
        table += f"<td><a class='player{i.color + 1}' href='/tavern/{i.color}'>Tavern</a></td>"
        table += "</tr>"
    return table


def army_html(name):
    army = editor.get_troops(name)

    w = f"<tr><th colspan='2' class='player{editor.get_team(name)+1}'>Army</th></tr>"
    for i, troop in enumerate(army):
        dropdown_options = f"<option value='' {'selected' if troop.id == -1 else ''}></option>"
        for j in sorted(consts.troop_ids):
            dropdown_options += f"<option value='{j}' {'selected' if j == troop.name else ''}>{j}</option>"
        w += f"<tr><td><select id='troop{i}' autocomplete='off'>{dropdown_options}</select></td><td><input autocomplete='off' id='army{i}' value='{troop.amount}' min='0' class='gold' type='number'></input></td></tr>"
    # dropdown_options = "<option value='' selected></option>"
    # for i in sorted(consts.troop_ids):
    #     dropdown_options += f"<option value='{i}'>{i}</option>"
    # for i in range(len(army), 8):
    #     w += f"<tr><td><select id='troop{i}' autocomplete='off'>{dropdown_options}</select></td><td><input autocomplete='off' id='army{i}' value='0' min='0' class='gold' type='number'></input></td></tr>"
    w += f"<tr><td colspan='2'><button onclick='save_army(\"{name}\")'>save</button></td></tr>"
    return w

def teleport_html(name):
    x, y, underground = editor.get_location(name)
    team = editor.get_team(name)
    w = (f"<tr><th colspan='3' class='player{team + 1}'>Position</th></tr>"
        "<tr><th>x</th><th>y</th><th>Underground</th></tr><tr>" 
        f"<td><input autocomplete='off' id='teleX' value='{x}' class='resource' type='number' min='0' max='{editor.map_size - 1}'></input></td>" 
        f"<td><input autocomplete='off' id='teleY' value='{y}' class='resource' type='number' min='0' max='{editor.map_size - 1}'></input></td>" 
        f"<td class='tickbox'><input autocomplete='off' id='teleUnderground' type='checkbox' {'checked' if underground else ''}></input></td></tr>"
        f"<tr><td colspan='3'><button onclick='teleport(\"{name}\")'>save</button></td></tr>")
    return w

def possession_html(name):
    team = editor.get_team(name)
    w = f"<tr><th class='player{team + 1}'>Move To</th></tr><tr><td><select id='possess' autocomplete='off'>"
    for color in range(8):
        w += f"<option value='{color}'>{consts.colors[color]}: {editor.get_player(color).name}</option>"
    w += f"</select></td></tr><tr><td colspan='3'><button onclick='possess(\"{name}\")'>save</button></td></tr>"
    return w

def tavern_html(color):
    w = f"<tr><th colspan='2' class='player{color + 1}'>Tavern</th></tr><tr>"
    used_heroes = []
    for i in range(8):
        used_heroes += editor.get_player(i).heroes
    for nr, hero in enumerate(editor.get_tavern(color)):
        hero = consts.hero_ids[hero]
        w += f"<td><select id='tavern{nr + 1}' autocomplete='off'>"
        for i in sorted(consts.hero_ids):
            if i not in used_heroes:
                w += f"<option value='{i}' {'selected' if i == hero else ''}>{i}</option>"
        w += "</select></td>"
    w += f"</tr><tr><td colspan='2'><button onclick='tavern({color})'>save</button></td></tr>"
    return w

@app.route('/')
def index():
    if editor.PID is None:
        return render_template("start_editor.html")

    table = players_html()

    return render_template("index.html", tabela=table)


@app.route('/edit/<hero>')
def edit(hero):
    if editor.PID is None:
        return redirect("/")
    return render_template("edit_hero.html", tab=skills_html(hero), army=army_html(hero),
                           teleport=teleport_html(hero), possess=possession_html(hero))

@app.route('/tavern/<color>', methods=["GET"])
def tavern(color):
    if editor.PID is None:
        return redirect("/")
    return render_template("tavern.html", tab=tavern_html(int(color)))

@app.route('/tavern', methods=["POST"])
def edit_tavern():
    if editor.PID is None:
        return Response(status=503)
    editor.set_tavern(int(request.json["color"]), consts.hero_ids.index(request.json["slot1"]), consts.hero_ids.index(request.json["slot2"]))
    return tavern_html(int(request.json["color"]))


@app.route("/save", methods=['POST'])
def update_hero():
    if editor.PID is None:
        return Response(status=503)
    skills = [Skill(consts.skill_ids[skill['id']], int(skill['lvl']), int(skill['slot'])) for skill in
              request.json['skills'] if skill['id']]
    editor.set_skills(request.json['name'], skills)
    primary = [int(i) for i in request.json['primary']]
    editor.set_primary_skills(request.json['name'], primary)
    return skills_html(request.json['name'])


@app.route("/save_res", methods=['POST'])
def update_resources():
    if editor.PID is None:
        return Response(status=503)
    for color, resources in enumerate(request.json['resources']):
        editor.set_resources(color, resources)
    return players_html()

@app.route("/save_army", methods=['POST'])
def update_army():
    if editor.PID is None:
        return Response(status=503)
    skills = [Troop(consts.troop_ids.get(troop["id"], -1), int(troop["amount"])) for troop in request.json['army']]
    editor.set_troops(request.json['name'], skills)
    return army_html(request.json['name'])

@app.route("/restart")
def restart():
    editor.reload()
    if editor.PID is None:
        return Response(status=503)
    return Response(status=200)

@app.route("/teleport", methods=['POST'])
def teleport():
    if editor.PID is None:
        return Response(status=503)
    editor.set_location(request.json['name'], int(request.json['x']), int(request.json['y']), request.json['underground'] == "true")
    return teleport_html(request.json['name'])

@app.route("/possess", methods=['POST'])
def possess():
    if editor.PID is None:
        return Response(status=503)

    team = editor.get_team(request.json["name"])
    player = editor.get_player(int(request.json["target"]))
    if player.selected_town is not None:
        town = player.selected_town
    else:
        town = player.towns[0]
    town = Town(*editor.dereference(editor.town_array + town * 360, consts.town_struct))
    editor.possess(request.json['name'], team, int(request.json['target']), town.x, town.y, town.underground)
    return possession_html(request.json['name'])


def compare_skills(skills, slots):
    for j in range(len(skills)):
        if skills[j] * slots[j] == 0 and skills[j] + slots[j] != 0:
            return False
    return True


if __name__ == '__main__':
    editor = H3editor()
    # print(editor.mem_locations['Orrin'])
    # editor.memory_file.seek(0x6992B8)
    # from array import array
    # x =array("i")
    # x.frombytes(editor.memory_file.read(4))
    # editor.memory_file.seek(x[0]+0x5c)
    # x.frombytes(editor.memory_file.read(4))
    # editor.memory_file.seek(x[1] + 0xD0)
    # x.frombytes(editor.memory_file.read(4))
    #
    # editor.memory_file.seek(0x699538)
    # x.frombytes(editor.memory_file.read(4))
    # editor.memory_file.seek(x[-1] + 0x21614)
    # x.frombytes(editor.memory_file.read(4))
    # print(hex(x[-1]), hex(editor.dereference(editor.dereference(0x699538)+0x21614))) #12 10 00 FF FF
    #                                                             #03 11 00 FF FF
    # print(x)
    #
    # # data = editor.memory_file.read(0x168*16)
    # # for i in range(0, len(data), 16*10):
    # #     for j in range(10):
    # #         print(*(f"{hex(i).upper()[2:]:0>2}" for i in data[j*16+i:j*16+i+16]), data[j*16+i:j*16+i+16])
    # #     print()
    # # print(x)
    # # print()
    # #print(data)
    # #print(sum(data))
    # import struct
    # print(hex(editor.town_array))
    # miasto = Town(*editor.dereference(editor.town_array, consts.town_struct))
    # print(miasto)
    # print(editor.get_location("Clancy"))
    # print(editor.get_location("Clancy"))

    app.run(port=80, host='0.0.0.0')

