(function () {
    var form = document.getElementById("entry-form");
    var fileInput = document.getElementById("attachment");
    var attachTrigger = document.getElementById("attach-trigger");
    var attachmentName = document.getElementById("attachment-name");
    if (!form || !fileInput) {
        return;
    }

    function setAttachmentName() {
        if (!attachmentName) {
            return;
        }

        if (fileInput.files && fileInput.files.length > 0) {
            attachmentName.textContent = "Selected: " + fileInput.files[0].name;
            return;
        }

        attachmentName.textContent = "No file selected";
    }

    function hasExtension(fileName) {
        var base = (fileName || "").split(/[\\/]/).pop();
        var lastDot = base.lastIndexOf(".");
        return lastDot > 0 && lastDot < base.length - 1;
    }

    function validateFileInput() {
        if (!fileInput.files || fileInput.files.length === 0) {
            fileInput.setCustomValidity("");
            return true;
        }

        var selectedName = fileInput.files[0].name;
        if (!hasExtension(selectedName)) {
            fileInput.setCustomValidity("Attached file must include an extension, such as .pdf or .jpg.");
            return false;
        }

        fileInput.setCustomValidity("");
        return true;
    }

    fileInput.addEventListener("change", function () {
        validateFileInput();
        setAttachmentName();
        fileInput.reportValidity();
    });

    if (attachTrigger) {
        attachTrigger.addEventListener("click", function () {
            fileInput.click();
        });
    }

    setAttachmentName();

    form.addEventListener("submit", function (event) {
        if (!validateFileInput()) {
            event.preventDefault();
            fileInput.reportValidity();
        }
    });
})();
