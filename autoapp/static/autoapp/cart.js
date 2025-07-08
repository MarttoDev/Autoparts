document.addEventListener('DOMContentLoaded', function () {
  const envioRadios = document.querySelectorAll('input[name="envio"]');
  const direccionFormSection = document.getElementById('direccion-form');
  const pagoRadios = document.querySelectorAll('input[name="pago"]');
  const btnPagar = document.getElementById('btnPagar');
  const pagoFinalForm = document.getElementById('pagoFinalForm');
  const envioSeleccionadoInput = document.getElementById('envioSeleccionado');
  const direccionForm = document.getElementById('direccionForm');

  function validarForm() {
    let envioSeleccionado = document.querySelector('input[name="envio"]:checked').value;
    envioSeleccionadoInput.value = envioSeleccionado;

    let pagoSeleccionado = document.querySelector('input[name="pago"]:checked');
    if (!pagoSeleccionado) {
      btnPagar.disabled = true;
      return;
    }

    if (envioSeleccionado === 'domicilio') {
      const inputs = direccionForm.querySelectorAll('input[required]');
      for (const input of inputs) {
        if (!input.value.trim()) {
          btnPagar.disabled = true;
          return;
        }
      }
    }
    btnPagar.disabled = false;
  }

  envioRadios.forEach(radio => {
    radio.addEventListener('change', function () {
      direccionFormSection.style.display = this.value === 'domicilio' ? 'block' : 'none';
      validarForm();
    });
  });

  pagoRadios.forEach(radio => {
    radio.addEventListener('change', validarForm);
  });

  direccionForm.querySelectorAll('input[required]').forEach(input => {
    input.addEventListener('input', validarForm);
  });

  if (document.querySelector('input[name="envio"]:checked').value === 'domicilio') {
    direccionFormSection.style.display = 'block';
  } else {
    direccionFormSection.style.display = 'none';
  }

  validarForm();

  pagoFinalForm.addEventListener('submit', function (event) {
    if (envioSeleccionadoInput.value === 'domicilio') {
      const inputsDireccion = direccionForm.querySelectorAll('input');
      inputsDireccion.forEach(function (input) {
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = input.name;
        hiddenInput.value = input.value;
        pagoFinalForm.appendChild(hiddenInput);
      });
    }
  });
});

