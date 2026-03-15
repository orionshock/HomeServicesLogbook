(function () {
    "use strict";

    var CATEGORY_STATE_KEY = "vendor-category-state";
    var FILTER_TEXT_KEY = "vendor-filter-text";

    function getCategoryState() {
        try {
            return JSON.parse(sessionStorage.getItem(CATEGORY_STATE_KEY) || "{}");
        } catch (_) {
            return {};
        }
    }

    function saveCategoryState(state) {
        try {
            sessionStorage.setItem(CATEGORY_STATE_KEY, JSON.stringify(state));
        } catch (_) {}
    }

    function getFilterText() {
        try {
            return sessionStorage.getItem(FILTER_TEXT_KEY) || "";
        } catch (_) {
            return "";
        }
    }

    function saveFilterText(value) {
        try {
            sessionStorage.setItem(FILTER_TEXT_KEY, value);
        } catch (_) {}
    }

    // Set a category section's collapsed state and update its toggle icon.
    function setCollapsed(section, collapsed) {
        if (collapsed) {
            section.classList.add("is-collapsed");
        } else {
            section.classList.remove("is-collapsed");
        }
        var icon = section.querySelector(".category-toggle-icon");
        if (icon) {
            icon.textContent = collapsed ? "\u25b8" : "\u25be"; // ▸ or ▾
        }
    }

    // Show or hide vendor items based on the filter query.
    // Hides entire category sections when none of their vendors match.
    function applyFilter(query) {
        var lower = query.toLowerCase().trim();
        var sections = document.querySelectorAll(".vendor-category-section");

        sections.forEach(function (section) {
            var items = section.querySelectorAll(".vendor-item");
            var visibleCount = 0;

            items.forEach(function (item) {
                var name = (item.dataset.name || "").toLowerCase();
                var category = (item.dataset.category || "").toLowerCase();
                var matches = !lower || name.includes(lower) || category.includes(lower);
                item.style.display = matches ? "" : "none";
                if (matches) {
                    visibleCount++;
                }
            });

            // Hide the whole section when no vendors match.
            section.style.display = visibleCount > 0 ? "" : "none";
        });
    }

    function init() {
        var searchInput = document.getElementById("vendorSearch");
        var sections = document.querySelectorAll(".vendor-category-section");
        var state = getCategoryState();

        // Restore each category's open/closed state. Default to open.
        sections.forEach(function (section) {
            var key = section.dataset.category;
            var isOpen = Object.prototype.hasOwnProperty.call(state, key) ? state[key] : true;
            setCollapsed(section, !isOpen);
        });

        // Wire up click handlers on category headers.
        document.querySelectorAll(".vendor-category-header").forEach(function (header) {
            header.addEventListener("click", function () {
                var section = header.closest(".vendor-category-section");
                if (!section) { return; }
                var collapsed = section.classList.contains("is-collapsed");
                var key = section.dataset.category;
                var currentState = getCategoryState();
                currentState[key] = collapsed; // true = open after toggle
                saveCategoryState(currentState);
                setCollapsed(section, !collapsed);
            });
        });

        // Restore saved filter text and wire up live filtering.
        if (searchInput) {
            var saved = getFilterText();
            if (saved) {
                searchInput.value = saved;
                applyFilter(saved);
            }
            searchInput.addEventListener("input", function () {
                saveFilterText(searchInput.value);
                applyFilter(searchInput.value);
            });
        }
    }

    document.addEventListener("DOMContentLoaded", init);
}());
