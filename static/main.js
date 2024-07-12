async function save_hero(name) {
    let skills = []
    for (let i = 1; i <= 8; i++) {
        let skill = Object()
        skill.slot = i
        skill.id = document.getElementById("slot"+i).value
        skill.lvl = document.getElementById("level"+i).value
        skills[i-1]=skill
    }
    let primary = []
    for (let i = 0; i < 4; i++) {
        primary[i] = document.getElementById("primary"+i).value
    }
    const response = await fetch("/save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            name: name,
            skills: skills,
            primary: primary,
        }),
    });
    if (response.ok) {
        document.getElementById("mainTable").innerHTML = await response.text();
        alert("Hero updated successfully.");
        return
    }
    alert("Falied to update hero.")
}

async function save_res() {
    let tab = []
    for (let i = 0; i < 7; i++) {
        let row = []
        for (let j = 0; j < 7; j++)
            row[j] = parseInt(document.getElementById('r'+i+j).value);
        tab[i]=row
    }
    let res = await fetch("/save_res", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            resources: tab,
        }),
    })
    if (res.ok) {
        location.reload()
        return
    }
    alert("Falied to update resources.")

}

async function reset_editor() {
    let loadbox = document.createElement("div")
    loadbox.classList.add("loadingBox")
    let div = document.createElement("div")
    div.classList.add("loading")
    loadbox.appendChild(div)
    document.body.appendChild(loadbox)

    let res = await fetch("/restart", {})
    if (res.status === 502) {
        alert("Heroes 3 process not found")
        return
    }
    location.reload()
}