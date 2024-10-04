<template>
  <div>
    <h1>Buscar Jugadores</h1>

    <!-- Formulario de búsqueda -->
    <form @submit.prevent="searchPlayers" class="search-form">
      <input v-model="search.name" type="text" placeholder="Nombre del jugador">

      <!-- Desplegable de posiciones -->
      <select v-model="search.position">
        <option value="">Selecciona una posición</option>
        <option v-for="(spanishPosition,englishPosition) in positionsMap" 
                :key="englishPosition" 
                :value="englishPosition">
          {{ spanishPosition }}
        </option>
      </select>

      <input v-model="search.current_club_name" type="text" placeholder="Nombre del club">
      <input v-model="search.country_of_citizenship" type="text" placeholder="Nacionalidad">
      <button type="submit">Buscar</button>
    </form>

    <!-- Resultados de jugadores en formato de tarjetas -->
    <div v-if="players.length > 0">
      <h2>Resultados de la búsqueda</h2>
      <div class="player-grid">
        <div 
          v-for="player in players" 
          :key="player.player_id" 
          @click="goToPlayerDetail(player.player_id)"
          class="player-card"
        >
          <img :src="player.image_url" :alt="player.name">
          <div class="player-info">
            <p class="player-name">{{ player.name }}</p>
            <p class="player-position">{{ player.position }}</p>
            <p class="player-club">{{ player.current_club_name }}</p>
            <p class="player-market-value">€{{ player.market_value_in_eur }}</p>
          </div>
        </div>
      </div>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="previousPage" :disabled="page === 1">Anterior</button>
        <button @click="nextPage" :disabled="!hasMorePlayers">Siguiente</button>
      </div>
    </div>
    <div v-else>
      <p>No se encontraron jugadores.</p>
    </div>
  </div>
</template>

<script>
import { getPlayers } from '../services/api';

export default {
  data() {
    return {
      search: {
        name: '',
        position: '',
        current_club_name: '',
        country_of_citizenship: ''
      },
      // Mapeo de posiciones en inglés y sus traducciones al español
      positionsMap: {
        "Attack": "Delantero",
        "Goalkeeper": "Portero",
        "Defender": "Defensa",
        "Midfield": "Centrocampista",
        "Missing": "Desconocido"
      },
      players: [],
      page: 1,
      perPage: 10, // Paginación con 10 jugadores por página (2 filas de 5 jugadores)
      hasMorePlayers: false
    };
  },
  methods: {
    async searchPlayers() {
      // Limpiar los resultados antes de realizar la nueva búsqueda
      this.players = [];
      
      try {
        const data = await getPlayers(this.search, this.page, this.perPage);
        this.players = data.players;
        this.hasMorePlayers = data.total > this.page * this.perPage;
      } catch (error) {
        console.error('Error fetching players:', error);
      }
    },
    goToPlayerDetail(playerId) {
      this.$router.push({ name: 'JugadorDetails', params: { playerId } });
    },
    async nextPage() {
      if (this.hasMorePlayers) {
        this.page++;
        await this.searchPlayers(); // Asegúrate de que se llama correctamente la función con la página actualizada
      }
    },
    async previousPage() {
      if (this.page > 1) {
        this.page--;
        await this.searchPlayers(); // Asegúrate de que se llama correctamente la función con la página actualizada
      }
    }
  }
};
</script>

<style scoped>
/* Estilos del formulario de búsqueda */
.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.search-form input, .search-form select {
  padding: 10px;
  font-size: 1em;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.search-form button {
  padding: 10px 20px;
  font-size: 1em;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

.search-form button:hover {
  background-color: #0056b3;
}

/* Estilos para la cuadrícula de tarjetas de jugadores */
.player-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr); /* Mostrar 5 jugadores por fila */
  gap: 20px;
  justify-items: center;
}

.player-card {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 200px;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.player-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.player-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.player-info {
  padding: 10px;
  text-align: center;
}

.player-name {
  font-weight: bold;
  font-size: 1.1em;
}

.player-position, .player-club, .player-market-value {
  margin: 5px 0;
  color: #555;
}

/* Paginación */
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.pagination button {
  padding: 10px 20px;
  font-size: 1em;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

.pagination button:disabled {
  background-color: #ccc;
}

.pagination button:hover:enabled {
  background-color: #0056b3;
}
</style>
