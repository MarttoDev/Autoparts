document.addEventListener('DOMContentLoaded', function () {
  const input = document.getElementById('buscador');
  const productos = document.querySelectorAll('.producto');

  if (!input || productos.length === 0) return;

  // Función para normalizar texto (quita tildes y pasa a minúsculas)
  const normalizar = (str) =>
    str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

  input.addEventListener('input', function () {
    const filtro = normalizar(this.value);

    productos.forEach(function (producto) {
      const nombreElem = producto.querySelector('h3');
      if (!nombreElem) return;

      const nombre = normalizar(nombreElem.textContent);

      if (nombre.includes(filtro)) {
        producto.style.display = '';
      } else {
        producto.style.display = 'none';
      }
    });
  });
});
