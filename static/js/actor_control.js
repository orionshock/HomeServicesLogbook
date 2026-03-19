(function () {
    var controls = document.querySelectorAll("[data-actor-control]");
    if (!controls.length) {
        return;
    }

    controls.forEach(function (control) {
        var menu = control.querySelector("[data-actor-menu]");
        var dialog = control.querySelector("[data-actor-dialog]");
        var openButton = control.querySelector("[data-open-actor-dialog]");
        var closeButton = control.querySelector("[data-close-actor-dialog]");
        var actorInput = control.querySelector("input[name='actor_id']");
        var actorDisplay = control.querySelector("[data-current-actor-display]");
        var setForm = control.querySelector("[data-actor-set-form]");
        var resetInlineForm = control.querySelector("[data-actor-reset-inline]");
        var menuResetForm = control.querySelector("[data-actor-reset-form]");
        var errorMessage = control.querySelector("[data-actor-error]");

        if (!dialog || !openButton || !setForm) {
            return;
        }

        function showError(message) {
            if (errorMessage) {
                errorMessage.textContent = message;
                errorMessage.hidden = false;
            }
            console.error("Actor update failed:", message);
        }

        function clearError() {
            if (errorMessage) {
                errorMessage.textContent = "";
                errorMessage.hidden = true;
            }
        }

        function updateActorUI(currentActor) {
            if (!currentActor) {
                return;
            }

            if (actorDisplay && currentActor.display_name) {
                actorDisplay.textContent = currentActor.display_name;
            }

            var isOverride = currentActor.source === "override";
            if (resetInlineForm) {
                resetInlineForm.hidden = !isOverride;
            }
        }

        function postFormAsJson(form) {
            return fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "fetch",
                    "Accept": "application/json"
                }
            }).then(function (response) {
                if (!response.ok) {
                    throw new Error("Request failed with status " + response.status);
                }
                return response.json();
            }).then(function (data) {
                if (!data || data.ok !== true || !data.current_actor) {
                    throw new Error("Invalid actor response payload.");
                }
                return data.current_actor;
            });
        }

        function closeDialog() {
            if (dialog.open) {
                dialog.close();
            }
        }

        openButton.addEventListener("click", function () {
            if (menu && menu.open) {
                menu.open = false;
            }
            if (typeof dialog.showModal === "function") {
                clearError();
                dialog.showModal();
                if (actorInput) {
                    actorInput.focus();
                    actorInput.select();
                }
            }
        });

        if (closeButton) {
            closeButton.addEventListener("click", function () {
                closeDialog();
            });
        }

        setForm.addEventListener("submit", function (event) {
            event.preventDefault();
            clearError();

            postFormAsJson(setForm)
                .then(function (currentActor) {
                    updateActorUI(currentActor);
                    closeDialog();
                })
                .catch(function (error) {
                    showError("Could not change user right now.");
                    console.error(error);
                });
        });

        if (resetInlineForm) {
            resetInlineForm.addEventListener("submit", function (event) {
                event.preventDefault();
                clearError();

                postFormAsJson(resetInlineForm)
                    .then(function (currentActor) {
                        updateActorUI(currentActor);
                        closeDialog();
                    })
                    .catch(function (error) {
                        showError("Could not reset to upstream proxy.");
                        console.error(error);
                    });
            });
        }

        if (menuResetForm) {
            menuResetForm.addEventListener("submit", function (event) {
                event.preventDefault();

                postFormAsJson(menuResetForm)
                    .then(function (currentActor) {
                        updateActorUI(currentActor);
                        if (menu && menu.open) {
                            menu.open = false;
                        }
                    })
                    .catch(function (error) {
                        console.error("Could not reset to upstream proxy:", error);
                    });
            });
        }
    });
})();
