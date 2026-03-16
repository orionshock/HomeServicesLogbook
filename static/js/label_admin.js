(function () {
    var list = document.querySelector(".label-management-list");
    var rows = document.querySelectorAll("[data-label-row]");
    var emptyState = document.querySelector("[data-label-empty-state]");

    if (!rows.length) {
        return;
    }

    function updateEmptyState() {
        if (!list || !emptyState) {
            return;
        }

        emptyState.hidden = list.querySelectorAll("[data-label-row]").length !== 0;
    }

    function parseResponse(response) {
        return response.json().catch(function () {
            return {};
        });
    }

    function setupRow(row) {
        var labelUid = row.dataset.labelUid || "";
        var currentName = row.dataset.labelName || "";
        var currentColor = row.dataset.labelColor || "#000000";

        var nameView = row.querySelector("[data-label-name-view]");
        var nameEdit = row.querySelector("[data-label-name-edit]");
        var nameText = row.querySelector("[data-label-name-text]");
        var editTrigger = row.querySelector("[data-label-edit-trigger]");
        var nameInput = row.querySelector("[data-label-name-input]");
        var nameSave = row.querySelector("[data-label-name-save]");
        var nameCancel = row.querySelector("[data-label-name-cancel]");
        var colorInput = row.querySelector("[data-label-color-input]");
        var colorValue = row.querySelector("[data-label-color-value]");
        var deleteButton = row.querySelector("[data-label-delete]");
        var rowError = row.querySelector("[data-label-row-error]");

        var isSavingName = false;
        var isSavingColor = false;
        var isDeleting = false;

        if (!labelUid || !nameView || !nameEdit || !nameText || !editTrigger || !nameInput || !nameSave || !nameCancel || !colorInput || !colorValue || !deleteButton || !rowError) {
            return;
        }

        function showError(message) {
            rowError.textContent = message || "An unexpected error occurred.";
            rowError.hidden = false;
        }

        function clearError() {
            rowError.textContent = "";
            rowError.hidden = true;
        }

        function refreshBusyState() {
            var isBusy = isSavingName || isSavingColor || isDeleting;
            row.classList.toggle("is-row-busy", isBusy);
            editTrigger.disabled = isBusy;
            nameSave.disabled = isBusy;
            nameCancel.disabled = isBusy;
            colorInput.disabled = isBusy;
            deleteButton.disabled = isBusy;
        }

        function setEditing(isEditing) {
            row.classList.toggle("is-editing", isEditing);

            if (isEditing) {
                nameInput.focus();
                nameInput.select();
            }
        }

        function syncColorValue() {
            colorValue.textContent = (colorInput.value || "#000000").toUpperCase();
        }

        function applyColor(color) {
            currentColor = color || "#000000";
            row.dataset.labelColor = currentColor;
            colorInput.value = currentColor;
            colorInput.defaultValue = currentColor;
            syncColorValue();
        }

        function applyName(name) {
            currentName = name;
            row.dataset.labelName = currentName;
            nameText.textContent = currentName;
            nameInput.value = currentName;
            nameInput.defaultValue = currentName;
        }

        async function renameLabel() {
            if (isSavingName || isDeleting) {
                return;
            }

            var submittedName = String(nameInput.value || "").trim();
            if (!submittedName) {
                showError("Label name is required");
                return;
            }

            if (submittedName === currentName) {
                clearError();
                setEditing(false);
                return;
            }

            clearError();
            isSavingName = true;
            refreshBusyState();

            try {
                var response = await fetch("/labels/" + encodeURIComponent(labelUid) + "/rename", {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    body: JSON.stringify({ name: submittedName }),
                });

                var payload = await parseResponse(response);
                if (!response.ok || !payload.ok) {
                    throw new Error(payload.error || "Unable to rename label.");
                }

                applyName(payload.name || submittedName);
                applyColor(payload.color || currentColor);
                setEditing(false);
            } catch (error) {
                showError(error.message || "Unable to rename label.");
            } finally {
                isSavingName = false;
                refreshBusyState();
            }
        }

        async function saveColorIfChanged() {
            if (isSavingColor || isSavingName || isDeleting) {
                return;
            }

            var submittedColor = String(colorInput.value || "").trim();
            if (!submittedColor || submittedColor.toUpperCase() === currentColor.toUpperCase()) {
                return;
            }

            clearError();
            isSavingColor = true;
            refreshBusyState();

            try {
                var response = await fetch("/labels/" + encodeURIComponent(labelUid) + "/color", {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    body: JSON.stringify({ color: submittedColor }),
                });

                var payload = await parseResponse(response);
                if (!response.ok || !payload.ok) {
                    throw new Error(payload.error || "Unable to save color.");
                }

                applyColor(payload.color || submittedColor);
            } catch (error) {
                applyColor(currentColor);
                showError(error.message || "Unable to save color.");
            } finally {
                isSavingColor = false;
                refreshBusyState();
            }
        }

        async function deleteLabel() {
            if (isDeleting || isSavingName || isSavingColor) {
                return;
            }

            if (!window.confirm("Delete this label?")) {
                return;
            }

            clearError();
            isDeleting = true;
            refreshBusyState();

            try {
                var response = await fetch("/labels/" + encodeURIComponent(labelUid) + "/delete", {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    body: JSON.stringify({}),
                });

                var payload = await parseResponse(response);
                if (!response.ok || !payload.ok) {
                    throw new Error(payload.error || "Unable to delete label.");
                }

                row.remove();
                updateEmptyState();
            } catch (error) {
                showError(error.message || "Unable to delete label.");
                isDeleting = false;
                refreshBusyState();
            }
        }

        editTrigger.addEventListener("click", function () {
            clearError();
            setEditing(true);
        });

        nameInput.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                renameLabel();
                return;
            }

            if (event.key === "Escape") {
                nameInput.value = currentName;
                clearError();
                setEditing(false);
            }
        });

        nameSave.addEventListener("click", function () {
            renameLabel();
        });

        nameCancel.addEventListener("click", function () {
            nameInput.value = currentName;
            clearError();
            setEditing(false);
        });

        colorInput.addEventListener("input", syncColorValue);
        colorInput.addEventListener("change", function () {
            syncColorValue();
            saveColorIfChanged();
        });
        colorInput.addEventListener("blur", function () {
            saveColorIfChanged();
        });

        deleteButton.addEventListener("click", function () {
            deleteLabel();
        });

        applyName(currentName);
        applyColor(currentColor);
        setEditing(false);
        refreshBusyState();
    }

    rows.forEach(setupRow);
    updateEmptyState();
})();