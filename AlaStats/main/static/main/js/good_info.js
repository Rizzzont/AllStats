document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("articleInput");
    const datalist = document.getElementById("articleSuggestions");
    let debounceTimer;

    input.addEventListener("input", function () {
        const query = this.value.trim();

        clearTimeout(debounceTimer);
        if (query.length < 2) return;

        debounceTimer = setTimeout(() => {
            fetch(`/api/autocomplete_goods/?term=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    datalist.innerHTML = "";
                    data.forEach(article => {
                        const option = document.createElement("option");
                        option.value = article;
                        datalist.appendChild(option);
                    });
                });
        }, 300);
    });
});
