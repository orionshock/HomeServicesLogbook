(function () {
    "use strict";

    function buildPhoneHref(rawValue) {
        var digits = (rawValue || "").replace(/\D/g, "");

        if (digits.length === 7 || digits.length === 10) {
            return "tel:" + digits;
        }

        if (digits.length === 11) {
            return "tel:+" + digits;
        }

        return null;
    }

    function initPhoneLinks() {
        document.querySelectorAll(".js-phone-link[data-phone-number]").forEach(function (node) {
            var rawValue = node.getAttribute("data-phone-number") || "";
            var href = buildPhoneHref(rawValue);

            if (!href) {
                return;
            }

            var link = document.createElement("a");
            link.href = href;
            link.textContent = node.textContent;
            node.replaceWith(link);
        });
    }

    function initCollapseToggle() {
        var toggles = document.querySelectorAll(".vendor-collapse-toggle");

        toggles.forEach(function (toggle) {
            toggle.addEventListener("click", function (e) {
                e.preventDefault();

                var controlsId = toggle.getAttribute("aria-controls");
                if (!controlsId) {
                    return;
                }

                var body = document.getElementById(controlsId);
                if (!body) {
                    return;
                }

                var isCurrentlyExpanded = toggle.getAttribute("aria-expanded") === "true";
                var isCollapsed = body.classList.contains("is-collapsed");

                // Toggle the state
                if (isCurrentlyExpanded) {
                    toggle.setAttribute("aria-expanded", "false");
                    body.classList.add("is-collapsed");
                } else {
                    toggle.setAttribute("aria-expanded", "true");
                    body.classList.remove("is-collapsed");
                }
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        initPhoneLinks();
        initCollapseToggle();
    });
}());