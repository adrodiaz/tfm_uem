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
    <router-view />
    <footer>
      <p>Adrián Marcel Rodríguez Díaz | Tutor: Jorge Moratalla Collado</p>
      <p>Curso 2023-2024 | TFM: "El juego del Big Data"</p>
    </footer>
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

#app {
  min-height: 100vh; /* Asegura que el contenido ocupe al menos el 100% del alto de la ventana */
  display: flex;
  flex-direction: column;
  margin-bottom: 2%;
}

router-view {
  flex: 1; /* Ocupa el espacio disponible antes del footer */
  margin-bottom: 5rem; /* Asegura que haya espacio para el footer */
}

footer {
  background-color: #d64040;
  color: rgb(248, 224, 224);
  text-align: center;
  padding: 1rem;
  font-size: 1.0rem;
  position: fixed;
  width: 100%;
  bottom: 0;
  left: 0;
  height: 4rem; 
}
</style>
