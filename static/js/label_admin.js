(function () {
    var rows = document.querySelectorAll("[data-label-row]");

    if (!rows.length) {
        return;
    }

    function setupRow(row) {
        var form = row.querySelector("[data-label-form]");
        var nameView = row.querySelector("[data-label-name-view]");
        var nameEdit = row.querySelector("[data-label-name-edit]");
        var editTrigger = row.querySelector("[data-label-edit-trigger]");
        var nameInput = row.querySelector("[data-label-name-input]");
        var nameHidden = row.querySelector("[data-label-name-hidden]");
        var nameSave = row.querySelector("[data-label-name-save]");
        var colorInput = row.querySelector("[data-label-color-input]");
        var colorValue = row.querySelector("[data-label-color-value]");

        if (!form || !nameView || !nameEdit || !editTrigger || !nameInput || !nameHidden || !nameSave || !colorInput || !colorValue) {
            return;
        }

        function setEditing(isEditing) {
            nameView.hidden = isEditing;
            nameEdit.hidden = !isEditing;
            row.classList.toggle("is-editing", isEditing);

            if (isEditing) {
                nameInput.focus();
                nameInput.select();
            }
        }

        function syncNameValue() {
            nameHidden.value = nameInput.value;
        }

        function syncColorValue() {
            colorValue.textContent = (colorInput.value || "#000000").toUpperCase();
        }

        editTrigger.addEventListener("click", function () {
            setEditing(true);
        });

        nameInput.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                syncNameValue();
                return;
            }

            if (event.key === "Escape") {
                nameInput.value = nameHidden.value;
                setEditing(false);
            }
        });

        nameSave.addEventListener("click", function () {
            syncNameValue();
        });

        colorInput.addEventListener("input", syncColorValue);
        colorInput.addEventListener("change", function () {
            syncColorValue();

            if (row.classList.contains("is-editing")) {
                return;
            }

            form.requestSubmit();
        });

        syncColorValue();
    }

    rows.forEach(setupRow);
})();