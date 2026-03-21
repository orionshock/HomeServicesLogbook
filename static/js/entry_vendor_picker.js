(function () {
    "use strict";

    function firstVisibleRow(rows) {
        for (var i = 0; i < rows.length; i += 1) {
            if (!rows[i].hidden) {
                return rows[i];
            }
        }
        return null;
    }

    function applyFilter(searchInput, rows, emptyState) {
        var query = (searchInput.value || "").trim().toLowerCase();
        var visibleCount = 0;

        rows.forEach(function (row) {
            var searchText = (row.dataset.search || "").toLowerCase();
            var isVisible = !query || searchText.indexOf(query) !== -1;
            row.hidden = !isVisible;
            if (isVisible) {
                visibleCount += 1;
            }
        });

        emptyState.classList.toggle("is-hidden", visibleCount > 0);
    }

    function init() {
        var searchInput = document.getElementById("entryVendorSearch");
        var rows = Array.prototype.slice.call(document.querySelectorAll("[data-entry-picker-row]"));
        var emptyState = document.querySelector("[data-entry-picker-empty]");

        if (!searchInput || !emptyState) {
            return;
        }

        searchInput.addEventListener("input", function () {
            applyFilter(searchInput, rows, emptyState);
        });

        searchInput.addEventListener("keydown", function (event) {
            if (event.key !== "Enter") {
                return;
            }

            var row = firstVisibleRow(rows);
            var link = row ? row.querySelector("a") : null;
            if (!link) {
                return;
            }

            event.preventDefault();
            window.location.href = link.href;
        });

        applyFilter(searchInput, rows, emptyState);
        searchInput.focus();
    }

    document.addEventListener("DOMContentLoaded", init);
}());
