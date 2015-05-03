"use strict";

var statsTable = (function() {
  var tbody = $("#stats-table > tbody")
  var selectedRow = -1;
  var rows = [];
  var setData = function(rowData) {
    rows = rowData;
    tbody.empty();
    for (var i = 0; i < rows.length; i++) {
      var row = rows[i];
      var tr = $("<tr>");
      for  (var j = 0; j < row.length; j++) {
        tr.append("<td>" + row[j] + "</td>");
      }
      tbody.append(tr);
    }
    selectedRow = -1;
  }

  var selectedRowData = function() {
    if (selectedRow < 0) {
      return null;
    } else {
      return rows[selectedRow];
    }
  }
  
  tbody.click(function(e) {
    if (selectedRow >= 0) {
      tbody.children().eq(selectedRow).removeClass('info');
    }
    var tr = $(e.target).parent();
    if (tr.index() == selectedRow) {
      selectedRow = -1;
    } else {
      tr.addClass('info');
      selectedRow = tr.index();
    }
    $("#stats-table").trigger("row-selected");
  });

  return {
    selectedRowData: selectedRowData,
    setData: setData
  }
})();

var sourceView = (function() {
  var root = $("#source-view");
  var selectedTag = null;

  var setSource = function(html) {
    root.html(html);
    highlightTag(null);
  }

  var highlightTag = function(tagName) {
    if (selectedTag) {
      root.find(".tag-" + selectedTag).css("background-color", "transparent");
    }
    if (tagName) {
      root.find(".tag-" + tagName).css("background-color", "yellow");
    }
    selectedTag = tagName;
  }
  
  return {
    setSource: setSource,
    highlightTag: highlightTag
  }
})();

$(function() {
  $("#form").submit(function (e) {
    $("#results-container").hide();
    $("#spinner").show();
    $("#error").hide();
    e.preventDefault();
    $.ajax({
      url: "/api/v1/describe-page",
      data: {url: $("#url").val()},
      type: "GET",
      dataType: "json",
      success: function(json) {
        if (!json.success) {
          $("#error").text("Server request failed: " + json.message);
          $("#error").show();
          return;
        }

        sourceView.setSource(json.highlighted_html);
        
        var rows = []
        for (var name in json.tag_counts) {
          rows.push([name, json.tag_counts[name]]);
        }
        rows.sort(function(a, b) { return b[1] - a[1] });
        statsTable.setData(rows);
        $("#results-container").show();
      },
      error: function(xhr, status, error) {
        $("#error").text("Server request failed: " + status);
        $("#error").show();
      },
      complete: function(xhr, status) {
        $("#spinner").hide();
      }
    });
  });

  $("#stats-table").on("row-selected", function() {
    var data = statsTable.selectedRowData();
    if (data) {
      sourceView.highlightTag(data[0]);
    } else {
      sourceView.highlightTag(null);
    }
  });

  $("#spinner").hide();
  $("#results-container").hide();
  $("#error").hide();
});
