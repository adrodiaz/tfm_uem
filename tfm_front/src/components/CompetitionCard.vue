<template>
  <div class="card" @mouseover="hover = true" @mouseleave="hover = false">
    <h2>{{ competition.name }}</h2>
    <p>{{ competition.country_name }} - {{ competition.type }}</p>
    
    <router-link :to="{ name: 'SelectSeason', params: { competitionId: competition.competition_id } }">
      <button>Ver Juegos</button>
    </router-link>
    
    <router-link :to="{ name: 'SelectResults', params: { competitionId: competition.competition_id } }">
      <button>Ver Resultados</button>
    </router-link>
    
    <br><br>
    <a :href="competition.url" target="_blank">Ver más en Transfermarkt</a>
  </div>
</template>

<script>
export default {
  name: 'CompetitionCard',
  props: {
    competition: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      hover: false
    };
  }
};
</script>

<style scoped>
.card {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 16px;
  margin: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  transition: transform 0.2s, box-shadow 0.2s; /* Añadir transición */
  cursor: pointer; /* Cambia el cursor al pasar por encima */
}

.card:hover {
  transform: scale(1.05); /* Aumentar tamaño de la tarjeta */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Aumentar sombra al pasar el ratón */
}

.card h2 {
  margin: 0 0 8px;
}

.card p {
  margin: 0 0 16px;
}

.card a {
  color: #d64040;
  text-decoration: none;
}

.card a:hover {
  text-decoration: underline;
}

.card button {
  padding: 10px 20px;
  background-color: #d64040;
  color: white;
  border: none; /* Cambiar a 'none' para quitar el borde */
  border-radius: 4px;
  cursor: pointer;
  margin: 5px 5px;
  text-align: center;
}
</style>
