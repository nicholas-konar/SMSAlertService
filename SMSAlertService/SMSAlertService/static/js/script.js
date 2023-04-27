document.addEventListener("DOMContentLoaded", function() {
  var keywordsElement = document.getElementById("keywords");
  var keywordsAttribute = keywordsElement.getAttribute("data-keywords");
  var keywords = JSON.parse(keywordsAttribute);

  var table = document.createElement("table");
  table.setAttribute("id", "keywordTable");

  for (var i = 0; i < keywords.length; i++) {
    var keyword = keywords[i];

    var button = document.createElement("button");
    button.setAttribute("id", `${keyword}`)
    button.classList.add("btn", "btn-danger");

    var icon = document.createElement("i");
    icon.classList.add("fa", "fa-trash");
    button.appendChild(icon);

    var cell1 = document.createElement("td");
    var cell2 = document.createElement("td");
    cell1.innerText = keyword;
    cell2.appendChild(button);

    var row = document.createElement("tr");
    row.setAttribute("id", `row-${keyword}`)
    row.appendChild(cell1);
    row.appendChild(cell2);
    table.appendChild(row);
  }
  document.getElementById("keywords").appendChild(table);

  var deleteKeyword = function(keywordToDelete) {
    var rowId = `row-${keywordToDelete}`;
    var row = document.getElementById(`${rowId}`);
    $.ajax({
      url: "/delete-keyword",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({DeleteKeyword: keywordToDelete}),
      success: function(response) {
        row.parentNode.removeChild(row);
        console.log(response);
      }
    });
  };

  var buttons = table.querySelectorAll("button");
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function() {
      var keywordToDelete = this.id;
      deleteKeyword(keywordToDelete);
    });
  }

  function addKeyword() {
    const newKeyword = document.getElementById("newKeyword").value;
    fetch("/add-keyword", {
        method: "POST",
        body: JSON.stringify({keyword: newKeyword}),
        headers: {"Content-Type": "application/json"}
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        var newRow = table.insertRow(0);
        newRow.setAttribute("id", `row-${newKeyword}`)
        var newCell1 = newRow.insertCell(0);
        var newCell2 = newRow.insertCell(1)

        var button = document.createElement("button");
        button.setAttribute("id", `${newKeyword}`)
        button.classList.add("btn", "btn-danger");
        button.addEventListener("click", function() {
          var keywordToDelete = this.id;
          deleteKeyword(keywordToDelete);
        });

        var icon = document.createElement("i");
        icon.classList.add("fa", "fa-trash");
        button.appendChild(icon);

        newCell1.innerHTML = data.NewKeyword;
        newCell2.appendChild(button)

    })
    .catch(error => console.error(error));
    }
    const addButton = document.getElementById("addKeywordButton");
    addButton.addEventListener("click", addKeyword);

});




















