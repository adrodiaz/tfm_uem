<template>
    <div>
      <h1>Detalles del juego</h1>
      <!-- Mostrar detalles del juego aquí -->
    </div>
  </template>
  
  <script>
  export default {
    props: ['gameId'],
    created() {
      // Puedes hacer una llamada a la API aquí para obtener los detalles del juego
      console.log('Cargando detalles para el juego ID:', this.gameId);
    }
  };
  </script>