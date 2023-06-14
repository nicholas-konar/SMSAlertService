document.addEventListener("DOMContentLoaded", function() {

    // Dynamic Keyword Table
    var table = document.createElement("table");
    table.setAttribute("id", "keywordTable");

    // todo: get keywords from API
    var keywordsElement = document.getElementById("keywords");
    var keywordsAttribute = keywordsElement.getAttribute("data-keywords");
    var keywords = JSON.parse(keywordsAttribute);

    for (var i = keywords.length - 1; i >= 0; i--) {
        tableRow = makeTableRow(keywords[i])
        table.appendChild(tableRow);
    }
    document.getElementById("keywords").appendChild(table);

    function makeTableRow(keyword) {
        var keywordCell = document.createElement("td");
        keywordCell.innerText = keyword;

        var icon = document.createElement("i");
        icon.classList.add("fa", "fa-trash");

        var deleteKeywordButton = document.createElement("button");
        deleteKeywordButton.classList.add("delete-keyword-btn", "red");
        deleteKeywordButton.setAttribute("id", `${keyword}`)
        deleteKeywordButton.appendChild(icon);

        var deleteKeywordButtonCell = document.createElement("td");
        deleteKeywordButtonCell.appendChild(deleteKeywordButton);

        var tableRow = document.createElement("tr");
        tableRow.setAttribute("id", `row-${keyword}`)
        tableRow.appendChild(keywordCell);
        tableRow.appendChild(deleteKeywordButtonCell);

        return tableRow
    }

    // Add Keyword
    const addKeywordButton = document.getElementById("addKeywordButton");
    addKeywordButton.addEventListener("click", addKeyword);

    const addKeywordForm = document.getElementById("addKeywordForm");
    addKeywordForm.addEventListener("submit", function(event) {
        event.preventDefault();
        addKeyword();
    });

    function addKeyword() {
        const newKeyword = document.getElementById("newKeyword").value;
        fetch("/account/keyword/add", {
            method: "POST",
            body: JSON.stringify({keyword: newKeyword}),
            headers: {"Content-Type": "application/json"}
        })
        .then(response => response.json())
        .then(data => {
            var inputField = document.getElementById("newKeyword");
            inputField.value = "";
            if (data.Status == "SUCCESS") {
                tableRow = makeTableRow(newKeyword);
                table.insertBefore(tableRow, table.firstChild);
            } else {
                // Do nothing
            }
        })
        .catch(error => console.error(error));
    }

    // Delete Keyword
    var deleteKeywordButtons = table.querySelectorAll(".delete-keyword-btn");
    for (var i = 0; i < deleteKeywordButtons.length; i++) {
        deleteKeywordButtons[i].addEventListener("click", function() {
            var keywordToDelete = this.id;
            deleteKeyword(keywordToDelete);
        });
    }

    var deleteKeyword = function(keywordToDelete) {
        var rowId = `row-${keywordToDelete}`;
        var row = document.getElementById(`${rowId}`);
        $.ajax({
            url: "/account/keyword/delete",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({DeleteKeyword: keywordToDelete}),
            success: function(response) {
                if (response.Status == "SUCCESS") {
                    row.parentNode.removeChild(row);
                } else {
                    // Do nothing
                }
            }
        });
    };

    // Delete All Keywords
    var deleteAllKeywordsButton = document.getElementById("deleteAllKeywordsButton");
    deleteAllKeywordsButton.addEventListener("click", function() {
        deleteAllKeywords();
    });

    function deleteAllKeywords() {
        $.ajax({
            url: "/account/keyword/delete-all",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({DeleteAllKeywords: true}),
            success: function(response) {
                if (response.Status == "SUCCESS") {
                    while (table.rows.length > 0) {
                        table.deleteRow(0);
                    }
                } else {
                    // Do nothing
                }
            }
        })
    }

});




















