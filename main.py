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
            skill.slot - 1] = f"<td><select autocomplete='off' id='slot{skill.slot}' selected='{skill.name}'>{dropdown_options}</select><input class='levelEdit' autocomplete='off' min='0' max='3' type='number' value='{skill.lvl}' id='level{skill.slot}'></input></td>"

    w = f"<tr><th colspan='2' class='player{editor.get_team(name) + 1}'>{name}</th></tr>"
    for i in range(4):
        w += f"<tr>{table[i * 2]}{table[i * 2 + 1]}</tr>"
    return w + f'<tr><td colspan="2"><button onclick="save_hero(\'{name}\')">save</button></td></tr>'


@app.route('/')
def index():
    if editor.PID is None:
        return render_template("start_editor.html")

    players = [editor.get_player(i) for i in range(8)]

    table = ""
    for i in players:
        table += f"<tr class='player{i.color + 1}'>"
        table += f"<th>{i.name}</th>"
        for j in i.heroes:
            table += f"<td><a class='player{i.color + 1}' href='/edit/{j}'>{j}</a></td>"

        table += "</tr>"

    return render_template("index.html", tabela=table)


@app.route('/edit/<hero>')
def edit(hero):
    return render_template("edit_hero.html", tab=skills_html(hero))


@app.route("/save", methods=['POST'])
def update_hero():
    skills = [Skill(consts.skill_ids[skill['id']], int(skill['lvl']), int(skill['slot'])) for skill in
              request.json['skills'] if skill['id']]
    editor.set_skills(request.json['name'], skills)
    return skills_html(request.json['name'])


def compare_skills(skills, slots):
    for j in range(len(skills)):
        if skills[j] * slots[j] == 0 and skills[j] + slots[j] != 0:
            return False
    return True


if __name__ == '__main__':
    editor = H3editor()

    app.run(port=80, host='0.0.0.0')
