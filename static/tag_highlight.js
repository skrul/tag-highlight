(function() {
  "use strict";
})();

// Generic table widget controller with selectable rows.
var statsTable = (function() {
  var tbody = $("#stats-table > tbody");
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
  };

  var selectedRowData = function() {
    if (selectedRow < 0) {
      return null;
    } else {
      return rows[selectedRow];
    }
  };
  
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
  };
})();

// HTML source view controller that can highlight tags.
var sourceView = (function() {
  var root = $("#source-view");
  var selectedTag = null;

  var setSource = function(html) {
    root.html(html);
    highlightTag(null);
  };

  var highlightTag = function(tagName) {
    if (selectedTag) {
      root.find(".tag-" + selectedTag).css("background-color", "transparent");
    }
    if (tagName) {
      root.find(".tag-" + tagName).css("background-color", "yellow");
    }
    selectedTag = tagName;
  };
  
  return {
    setSource: setSource,
    highlightTag: highlightTag
  };
})();

function setState(state, errorMessage) {
  if (state == "start") {
    $("#spinner").hide();
    $("#results-container").hide();
    $("#error").hide();
  } else if (state == "loading") {
    // Need to unhide the spinner with inline-block for the
    // animation to work correctly.
    $("#spinner").css("display", "inline-block");
    $("#results-container").hide();
    $("#error").hide();
  } else if (state == "done") {
    $("#spinner").hide();
    $("#results-container").show();
  } else if (state == "error") {
    $("#spinner").hide();
    $("#error").text(errorMessage);
    $("#error").show();
  }
}

$(function() {
  $("#form").submit(function (e) {
    e.preventDefault();
    setState("loading");
    $.ajax({
      url: "/api/v1/describe-page",
      data: {url: $("#url").val()},
      type: "GET",
      dataType: "json",
      success: function(json) {
        if (!json.success) {
          setState("error", "Server request failed: " + json.message);
          return;
        }

        sourceView.setSource(json.highlighted_html);
        
        var rows = [];
        for (var name in json.tag_counts) {
          rows.push([name, json.tag_counts[name]]);
        }
        rows.sort(function(a, b) { return b[1] - a[1]; });
        statsTable.setData(rows);
        setState("done");
      },
      error: function(xhr, status, error) {
        setState("error", "Server request failed: " + status);
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

  setState("start");
});
