#!/usr/bin/python3
import consts
from h3editor import H3editor, Skill
from flask import Flask, render_template, request, redirect, url_for, Response

app = Flask(__name__)


def skills_html(name):
    skills = editor.get_skills(name)

    dropdown_options = "<option value='' selected></option>"
    for i in sorted(consts.skill_ids):
        dropdown_options += f"<option value='{i}'>{i}</option>"

    table = [
        f"<td><select autocomplete='off' id='slot{i + 1}'>{dropdown_options}</select><input class='levelEdit' autocomplete='off' min='0' max='3' type='number' value='0' id='level{i + 1}'></input></td>"
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
        table += "</tr>"
    return table


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
    return render_template("edit_hero.html", tab=skills_html(hero))


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


@app.route("/restart")
def restart():
    editor.reload()
    if editor.PID is None:
        return Response(status=503)
    return Response(status=200)



def compare_skills(skills, slots):
    for j in range(len(skills)):
        if skills[j] * slots[j] == 0 and skills[j] + slots[j] != 0:
            return False
    return True


if __name__ == '__main__':
    editor = H3editor()

    app.run(port=80, host='0.0.0.0')
