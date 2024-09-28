<template>
  <div>
    <h1>Buscar Jugadores</h1>
    <form @submit.prevent="searchPlayers">
      <input v-model="search.name" type="text" placeholder="Nombre del jugador">
      <input v-model="search.position" type="text" placeholder="Posición">
      <input v-model="search.club" type="text" placeholder="Nombre del club">
      <button type="submit">Buscar</button>
    </form>

    <div v-if="players.length > 0">
      <h2>Resultados de la búsqueda</h2>
      <ul>
        <li v-for="player in players" :key="player.player_id">
          <img :src="player.image_url" :alt="player.name">
          <p>{{ player.name }} - {{ player.position }}</p>
          <p>{{ player.current_club_name }}</p>
          <p>Valor de mercado: €{{ player.market_value_in_eur }}</p>
        </li>
      </ul>
    </div>
    <div v-else>
      <p>No se encontraron jugadores.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      search: {
        name: '',
        position: '',
        club: ''
      },
      players: []
    };
  },
  methods: {
    async searchPlayers() {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/players', {
          params: this.search
        });
        this.players = response.data;
      } catch (error) {
        console.error('Error fetching players:', error);
      }
    }
  }
};
</script>
