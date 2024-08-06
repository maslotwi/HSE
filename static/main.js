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

async function save_army(name) {
    let army = []
    for (let i = 0; i < 7; i++) {
        army[i] = {
            id: document.getElementById("troop" + i).value,
            amount: document.getElementById("army" + i).value,
        }
    }
    const response = await fetch("/save_army", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            name: name,
            army: army,
        }),
    });
    if (response.ok) {
        document.getElementById("armyTable").innerHTML = await response.text();
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

async function teleport(name) {
    let x = document.getElementById("teleX").value
    let y = document.getElementById("teleY").value
    let underground = document.getElementById("teleUnderground").checked

    const response = await fetch("/teleport", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            x: x,
            y: y,
            underground: underground,
            name: name,
        }),
    });
    if (response.ok) {
        document.getElementById("teleportTable").innerHTML = await response.text();
        alert("Hero updated successfully.");
        return
    }
    alert("Falied to update hero.")

}

async function possess(name) {
    let target = document.getElementById("possess").value

    const response = await fetch("/possess", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            target: target,
            name: name,
        }),
    });
    if (response.ok) {
        document.getElementById("possessTable").innerHTML = await response.text();
        alert("Hero updated successfully.");
        location.reload()
        return
    }
    alert("Falied to update hero.")

}
