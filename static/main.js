async function save_hero(name) {
    let skills = Array()
    for (let i = 1; i <= 8; i++) {
        let skill = Object()
        skill.slot = i
        skill.id = document.getElementById("slot"+i).value
        skill.lvl = document.getElementById("level"+i).value
        skills[i-1]=skill
    }
    const response = await fetch("/save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            name: name,
            skills: skills
        }),
    });

    document.getElementById("mainTable").innerHTML = await response.text();

}