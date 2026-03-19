(function () {
    "use strict";

    var VIEW_MODE_KEY = "vendors-view-mode";

    function getSavedViewMode() {
        try {
            return localStorage.getItem(VIEW_MODE_KEY) || "az";
        } catch (_) {
            return "az";
        }
    }

    function saveViewMode(viewMode) {
        try {
            localStorage.setItem(VIEW_MODE_KEY, viewMode);
        } catch (_) {}
    }

    function getActiveView() {
        return document.querySelector(".vendor-listing-view.is-active");
    }

    function updateViewButtons(buttons, activeViewMode) {
        buttons.forEach(function (button) {
            var isActive = button.dataset.viewMode === activeViewMode;
            button.classList.toggle("is-active", isActive);
            button.setAttribute("aria-pressed", isActive ? "true" : "false");
        });
    }

    function applyFilter(query) {
        var activeView = getActiveView();
        var lowerQuery = (query || "").toLowerCase().trim();

        if (!activeView) {
            return;
        }

        activeView.querySelectorAll("[data-vendor-section]").forEach(function (section) {
            var visibleCount = 0;

            section.querySelectorAll("[data-vendor-item]").forEach(function (item) {
                var searchText = (item.dataset.search || item.dataset.name || "").toLowerCase();
                var matches = !lowerQuery || searchText.includes(lowerQuery);
                item.hidden = !matches;
                if (matches) {
                    visibleCount += 1;
                }
            });

            section.hidden = visibleCount === 0;
        });
    }

    function setActiveView(viewMode, views, buttons, searchInput) {
        var normalizedViewMode = viewMode === "category" ? "category" : "az";

        views.forEach(function (view) {
            var isActive = view.dataset.vendorView === normalizedViewMode;
            view.hidden = !isActive;
            view.classList.toggle("is-active", isActive);
        });

        updateViewButtons(buttons, normalizedViewMode);
        saveViewMode(normalizedViewMode);
        applyFilter(searchInput ? searchInput.value : "");
    }

    function init() {
        var searchInput = document.getElementById("vendorSearch");
        var views = Array.prototype.slice.call(document.querySelectorAll(".vendor-listing-view"));
        var viewButtons = Array.prototype.slice.call(document.querySelectorAll(".vendor-view-toggle"));

        if (!views.length) {
            return;
        }

        viewButtons.forEach(function (button) {
            button.addEventListener("click", function () {
                setActiveView(button.dataset.viewMode, views, viewButtons, searchInput);
            });
        });

        if (searchInput) {
            searchInput.addEventListener("input", function () {
                applyFilter(searchInput.value);
            });
        }

        setActiveView(getSavedViewMode(), views, viewButtons, searchInput);
    }

    document.addEventListener("DOMContentLoaded", init);
}());
