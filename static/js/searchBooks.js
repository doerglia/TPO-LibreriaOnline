// Dentro de tu archivo apibooks.js
const apiUrl = 'https://www.googleapis.com/books/v1/volumes?q=';
const apiKey = 'AIzaSyAv_ZR8HS7tlObI9O3Mal3Jy4rq0PiG82w';  // Reemplaza con tu clave de API

function buscarLibro() {
    var nombreLibro = document.getElementById('nombreLibro').value;
    var url = apiUrl + '?nombreLibro=' + encodeURIComponent(nombreLibro);

    fetch(url)
        .then(response => response.json())
        .then(data => {
            mostrarResultados(data);
        })
        .catch(error => {
            console.error('Error al llamar a la API de Google Books:', error);
        });

    return false;
}

function mostrarResultados(data) {
    const resultadosDiv = document.getElementById('resultados');
    
    // Limpiar cualquier contenido existente en el div de resultados
    resultadosDiv.innerHTML = '';

    // Verificar si hay resultados
    if (data.items && data.items.length > 0) {
        // Iterar sobre los resultados y mostrar la información relevante
        data.items.forEach(item => {
            const titulo = item.volumeInfo.title;
            const descripcion = item.volumeInfo.description || 'No hay descripción disponible';

            // Crear elementos HTML para mostrar los resultados
            const resultadoDiv = document.createElement('div');
            resultadoDiv.innerHTML = `<h3>${titulo}</h3><p>${descripcion}</p>`;

            // Agregar el resultado al div de resultados
            resultadosDiv.appendChild(resultadoDiv);
        });
    } else {
        // Mostrar un mensaje si no hay resultados
        resultadosDiv.innerHTML = '<p>No se encontraron resultados.</p>';
    }
}
