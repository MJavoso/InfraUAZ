const errorBoxes = {
    'global': document.getElementById("globalErrors"),
    'nombre': document.getElementById("nombreErrors"),
    'correo': document.getElementById("correoErrors"),
    'programaAcademico': document.getElementById("programaAcademicoErrors"),
    'contrasena': document.getElementById("contrasenaErrors")
};

function addErrors(errors) {
    if ('non_field_errors' in errors) {
        for (const error of errors.non_field_errors) {
            errorBoxes.global.classList.remove("hidden");
            const errorText = document.createElement("p");
            errorText.textContent = error;
            errorBoxes.global.appendChild(errorText);
        }
    }

    for (const clave in errorBoxes) {
        if (clave === 'global') {
            continue;
        }

        if (errors[clave] !== undefined) {
            for (const error of errors[clave]) {
                const errorText = document.createElement("p");
                errorText.textContent = error;
                errorBoxes[clave].appendChild(errorText);
            }
            errorBoxes[clave].classList.remove("hidden");
        }
    }
}

function clearErrors() {
    for (const clave in errorBoxes) {
        const box = errorBoxes[clave];
        box.innerHTML = '';
        box.classList.add("hidden");
    }
}

function loadAdminData(idAdmin) {
    let adminInfoUrl = getAdminUrl;
    adminInfoUrl = adminInfoUrl.substring(0, adminInfoUrl.lastIndexOf("/") + 1) + idAdmin;

    const modal = document.getElementById("updateAdminModal");
    const form = modal.querySelector("#updateAdminForm");

    const idAdminInput = form.querySelector("#id_id_admin");
    const nombreInput = form.querySelector("#id_nombre");
    const correoInput = form.querySelector("#id_correo");
    const programaAcademicoInput = form.querySelector("#id_programa_academico");
    const estadoCuentaInput = form.querySelector("#id_estado_cuenta");

    fetch(adminInfoUrl)
    .then((response) => {
        if (response.status == 404) {
            throw new Error("Administrador no encontrado");
        }

        return response.json();
    })
    .then((json) => {
        console.log(json);
        idAdminInput.value = json.id_admin;
        nombreInput.value = json.nombre;
        correoInput.value = json.correo;
        programaAcademicoInput.value = json.programa_academico;
        estadoCuentaInput.checked = json.estado_cuenta;

        const bootstrapModal = bootstrap.Modal.getInstance(modal) ?? new bootstrap.Modal(modal, {});
        bootstrapModal.show();
    })
    .catch((error) => {
        alert(error);
        console.error(error);
    });
}

function closeModalBtnClick() {
    const updateAdminForm = document.getElementById("updateAdminForm");
    updateAdminForm.reset();
}

document.addEventListener('DOMContentLoaded', function (event) {
    const updateAdminUrl = updateInfoUrl;

    const updateAdminForm = document.getElementById("updateAdminForm");
    const sendBtn = document.getElementById("sendBtn");
    sendBtn.addEventListener('click', function (event) {
        event.preventDefault();
        clearErrors();
        const formData = new FormData(updateAdminForm);

        fetch(updateAdminUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
            }
        })
            .then(async (response) => {
                return {
                    "code": response.status,
                    "body": await response.json()
                };
            })
            .then((body) => {
                if (body.code == 200) {
                    const modalDiv = document.getElementById("updateAdminModal");
                    const modal = bootstrap.Modal.getInstance(modalDiv);
                    modal.hide();
                    updateAdminForm.reset();
                } else if (body.code == 405) {
                    // Se usó otro método
                } else if (body.code == 400) {
                    const errors = body.body.errors;
                    addErrors(errors);
                }
            })
            .catch((error) => {
                alert(error);
            });
    });
});