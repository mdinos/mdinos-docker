document.addEventListener("DOMContentLoaded", function(e) {
    let pingAPIButton = document.getElementById('ping')
    pingAPIButton.addEventListener('click', showPingAPI)
})

let hostname = window.location.hostname

async function pingAPI() {
    let pingData = await fetch(`http://${hostname}/api/ping`)
    return pingData.json()
}

async function showPingAPI() {
    let dataZone = document.getElementById('data_zone')
    try {
        let pingData = await pingAPI()
        dataZone.innerHTML = `API IS OK?: ${pingData.ok}`
        dataZone.classList.remove('redify')
        dataZone.classList.add('greenify')
    } catch (err) {
        dataZone.innerHTML = err
        dataZone.classList.remove('greenify')
        dataZone.classList.add('redify')
    }
}