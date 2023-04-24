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
      url: `/delete-keyword?keyword=${keywordToDelete}`,
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({foo: "bar"}),
      success: function(response) {
        row.parentNode.removeChild(row);
      }
    });
  };

  var buttons = document.querySelectorAll("button");
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function() {
      var keywordToDelete = this.id;
      console.log(`keyword to delete: ${keywordToDelete}`);
      deleteKeyword(keywordToDelete);
    });
  }
});
