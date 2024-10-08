<template>
  <div>
    <h1>Buscar Jugadores</h1>

    <!-- Input de búsqueda -->
    <form @submit.prevent="searchPlayers" class="search-form">
      <!-- Inputs de búsqueda en la misma fila -->
      <input v-model="search.name" type="text" placeholder="Nombre del jugador">
      <select v-model="search.position">
        <option value="">Selecciona una posición</option>
        <option v-for="(spanishPosition, englishPosition) in positionsMap" 
                :key="englishPosition" 
                :value="englishPosition">
          {{ spanishPosition }}
        </option>
      </select>
      <input v-model="search.current_club_name" type="text" placeholder="Nombre del club">
      <input v-model="search.country_of_citizenship" type="text" placeholder="Nacionalidad">

      

    <!-- Label y rango de precios en una fila separada -->
    <div class="range-label">Valor de mercado:</div>
      <div class="range-slider-container">
        <div id="range-slider"></div>
        <div class="range-values">
          <span>Min: {{ rangeMin }} M€</span> <!-- Mostrar en millones -->
          <span>Max: {{ rangeMax }} M€</span> <!-- Mostrar en millones -->
        </div>
      </div>


      <button type="submit">Buscar</button>
    </form>

    <!-- Resultados de jugadores -->
    <div v-if="players.length > 0">
      <h2>Resultados de la búsqueda</h2>
      <div class="player-grid">
        <div v-for="player in players" 
             :key="player.player_id" 
             @click="goToPlayerDetail(player.player_id)" 
             class="player-card">
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
import noUiSlider from 'nouislider';
import 'nouislider/dist/nouislider.css';
import { getPlayers } from '../services/api';

export default {
  data() {
    return {
      search: {
        name: '',
        position: '',
        current_club_name: '',
        country_of_citizenship: '',
        min_market_value: '',
        max_market_value: ''
      },
      rangeMin: 0, // Valor mínimo inicial
      rangeMax: 250, // Valor máximo inicial
      positionsMap: {
        "Attack": "Delantero",
        "Goalkeeper": "Portero",
        "Defender": "Defensa",
        "Midfield": "Centrocampista",
        "Missing": "Desconocido"
      },
      players: [],
      page: 1,
      perPage: 10,
      hasMorePlayers: false
    };
  },
  mounted() {
    this.initSlider();
  },
  methods: {
    initSlider() {
      const slider = document.getElementById('range-slider');
      noUiSlider.create(slider, {
        start: [this.rangeMin, this.rangeMax],
        connect: true,
        range: {
          'min': 0,
          'max': 250
        },
        step: 1, // Permitir incrementos de 1
      });

      slider.noUiSlider.on('update', (values) => {
        this.rangeMin = Math.round(values[0]); // Actualiza el valor mínimo
        this.rangeMax = Math.round(values[1]); // Actualiza el valor máximo
      });
    },
    async searchPlayers() {
      const minPrice = this.rangeMin * 1000000; 
      const maxPrice = this.rangeMax * 1000000; 
      // Limpiar los resultados antes de realizar la nueva búsqueda
      this.players = [];
      try {
        const data = await getPlayers({ ...this.search, minPrice, maxPrice }, this.page, this.perPage);
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
        await this.searchPlayers();
      }
    },
    async previousPage() {
      if (this.page > 1) {
        this.page--;
        await this.searchPlayers();
      }
    }
  }
};
</script>


<style scoped>
/* Estilos del formulario de búsqueda */
.search-form {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 4 columnas para los filtros */
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
  grid-column: span 1; /* El botón ocupa una sola columna */
}

.search-form button:hover {
  background-color: #0056b3;
}

.player-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  justify-items: center;
}

.player-card {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 100%;
  max-width: 200px;
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

/* Estilos para el rango */
.range-values {
  display: flex;
  justify-content: space-between;
  margin-top: 10px; /* Espacio entre el slider y los valores */
  font-size: 1em; /* Ajusta el tamaño de la fuente según necesites */
  color: #555; /* Color del texto */
}

.range-slider-container {
  width: 23%; /* Ajusta este valor según tus necesidades */
  margin: 20px 0; /* Margen para separar del resto del formulario */
  grid-column: 1 / -1; /* Mantiene el contenedor en una fila completa */
}

#range-slider {
  margin-top: 5px; /* Separación superior para el slider */
  margin-bottom: 10px;
  margin-left: 20px;
}

.slider {
  width: 100%; /* Asegúrate de que el slider ocupe el ancho completo de su contenedor */
}
</style>

