const searchField = document.getElementById('searchField');
const tableOutput = document.querySelector('.table-out');
const appTable = document.querySelector('.app-table');
const paginationContainer = document.querySelector(".pagination-container");
const tbody = document.querySelector(".table-body");
const noResults = document.querySelector(".no-results");
tableOutput.style.display = "none";
searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;
    if (searchValue.trim().length > 0) {
        paginationContainer.style.display = "none";
        tbody.innerHTML = "";
        fetch('/income/search-income', {
                body: JSON.stringify({ searchText: searchValue }),
                method: "POST",
            })
            .then(res => res.json())
            .then(data => {
                appTable.style.display = "none";
                tableOutput.style.display = "block";
                console.log(data, data.length);
                if (data.length === 0) {
                    noResults.style.display = "block";
                    tableOutput.display.style = "none";
                } else {
                    noResults.style.display = "none";
                    data.forEach(item => {
                        tbody.innerHTML += `
                        <tr>
                            <td>${item.amount}</td>
                            <td>${item.source}</td>
                            <td>${item.description}</td>
                            <td>${item.date}</td>
                        </tr>
                    `
                    });
                }
            });
    } else {
        tableOutput.style.display = "none";
        appTable.style.display = "block";
        paginationContainer.style.display = "block";
    }
});