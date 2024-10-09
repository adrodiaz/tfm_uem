<template>
  <div class="home">
    <h1>Bienvenido a la Página de Competiciones de Fútbol</h1>
    <p>
      Este sitio web ofrece información detallada sobre diferentes competiciones de fútbol, 
      incluyendo competiciones nacionales e internacionales. Puedes explorar las diferentes 
      secciones para ver más detalles sobre competiciones, equipos y jugadores.
    </p><br><br>
    
    <h2>Top 3 Goleadores</h2>
    <div class="card-container">
      <div v-if="loading" class="loading">Cargando...</div>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-for="player in players" :key="player.player_id" class="card">
        <img :src="player.image_url" alt="Imagen del jugador" class="player-image" />
        <h3>{{ player.name }}</h3>
        <p>País: {{ player.country_of_birth }}</p>
        <p>Goles: {{ player.goals }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { getTopScorers } from '../services/api.js';

export default {
  name: 'InicioView',
  data() {
    return {
      players: [],
      loading: true,
      error: null,
    };
  },
  async created() {
    try {
      const data = await getTopScorers();
      this.players = data;
    } catch (err) {
      this.error = 'No se pudieron cargar los goleadores';
    } finally {
      this.loading = false;
    }
  },
};
</script>

<style scoped>
.home {
  text-align: center;
  padding: 40px;
}

.home h1 {
  font-size: 2.5rem;
  margin-bottom: 20px;
}

.home p {
  font-size: 1.2rem;
  line-height: 1.6;
}

.card-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.5rem; /* Aumenta el espacio entre las tarjetas */
}

.card {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 1rem;
  width: 200px; /* Ajusta el ancho según tus necesidades */
  text-align: center;
  background-color: #f9f9f9;
  transition: box-shadow 0.3s;
}

.card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.player-image {
  width: 80%; /* Ajusta el tamaño de la imagen a un 80% del ancho de la tarjeta */
  height: auto;
  max-width: 150px; /* Limita el tamaño máximo de la imagen */
  margin-bottom: 10px; /* Espacio entre la imagen y el texto */
}
</style>

