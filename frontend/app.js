document.getElementById("leadForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value
    };

    const res = await fetch("http://127.0.0.1:8000/leads/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await res.json();
    console.log("Lead enviado:", data);
});