<template>
  <div id="app">
    <nav>
      <ul>
        <li><router-link to="/">Inicio</router-link></li>
        <li><router-link to="/competiciones">Competiciones</router-link></li>
        <li><router-link to="/equipos">Equipos</router-link></li>
        <li><router-link to="/jugadores">Jugadores</router-link></li>
      </ul>
    </nav>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>

<style>
nav {
  background-color: #d64040;
  padding: 2rem;
}

ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: 1rem;
}

li {
  display: inline;
}

a {
  color: rgb(248, 224, 224);
  text-decoration: solid;
  font-weight: bold;
  font: 1.5em sans-serif;
}

a:hover {
  text-decoration: underline;
}
</style>
