/* ClimateAI · efecto «lupa» del mapa (tarea 3.1).
   Al pasar el mouse sobre un punto, ese punto crece y sus vecinos crecen menos según la
   distancia. Corre solo en el navegador (sin ir al servidor) para seguir al cursor sin retraso.
   Dash carga este archivo solo; el Dashboard lo activa con un clientside_callback. */
(function () {
  var TAMANO = 5;        // px, igual que TAMANO_PUNTO en app/componentes/mapa.py
  var MAXIMO = 13;       // px del punto bajo el mouse
  var RADIO = 7;         // grados: hasta dónde llega la lupa
  var ESPERA_SALIDA = 80; // ms antes de soltar la lupa (evita parpadeo al pasar de un punto a otro)

  var estado = { gd: null, actual: -1, pendiente: null, cuadro: 0, salida: 0 };

  // Plotly (Python) envía los números en binario: {dtype, bdata, _inputArray}. Esto devuelve el arreglo real.
  function arreglo(x) { return x && x._inputArray ? x._inputArray : x; }

  function cantidad(gd) { return arreglo(gd.data[0].lat).length; }

  function tamanos(gd, centro) {
    var t = gd.data[0], lat = arreglo(t.lat), lon = arreglo(t.lon), n = lat.length, s = new Array(n);
    var lat0 = lat[centro], lon0 = lon[centro], c = Math.cos(lat0 * Math.PI / 180);
    for (var i = 0; i < n; i++) {
      var dlat = lat[i] - lat0, dlon = (lon[i] - lon0) * c;
      var d = Math.sqrt(dlat * dlat + dlon * dlon);
      s[i] = d < RADIO ? TAMANO + (MAXIMO - TAMANO) * (1 - d / RADIO) : TAMANO;
    }
    return s;
  }

  function aplicar(gd, centro) {
    var s = centro < 0 ? new Array(cantidad(gd)).fill(TAMANO) : tamanos(gd, centro);
    window.Plotly.restyle(gd, { 'marker.size': [s] }, [0]);
  }

  function programar(gd, centro) {
    estado.pendiente = centro;
    if (estado.cuadro) return;
    estado.cuadro = window.requestAnimationFrame(function () {
      estado.cuadro = 0;
      if (estado.pendiente !== estado.actual) {
        estado.actual = estado.pendiente;
        aplicar(gd, estado.actual);
      }
    });
  }

  function alPasar(e) {
    var p = e && e.points && e.points[0];
    if (!p || p.curveNumber !== 0 || !estado.gd.data[0].lat) return;   // el coroplético no usa lupa
    window.clearTimeout(estado.salida);
    programar(estado.gd, p.pointNumber);
  }

  function alSalir() {
    window.clearTimeout(estado.salida);
    estado.salida = window.setTimeout(function () { programar(estado.gd, -1); }, ESPERA_SALIDA);
  }

  function enganchar(intento) {
    var gd = document.querySelector('#mapa .js-plotly-plot');
    if (!gd || typeof gd.on !== 'function' || !gd.data) {
      if (intento < 50) window.setTimeout(function () { enganchar(intento + 1); }, 100);
      return;
    }
    // Plotly puede reconstruir el gráfico al cambiar de año: se quitan y se vuelven a poner los eventos
    if (gd.removeListener) {
      gd.removeListener('plotly_hover', alPasar);
      gd.removeListener('plotly_unhover', alSalir);
    }
    gd.on('plotly_hover', alPasar);
    gd.on('plotly_unhover', alSalir);
    estado.gd = gd;
    estado.actual = -1;
  }

  window.dash_clientside = Object.assign({}, window.dash_clientside, {
    climateai: Object.assign({}, (window.dash_clientside || {}).climateai, {
      activarLupa: function () {
        window.setTimeout(function () { enganchar(0); }, 0);
        return window.dash_clientside.no_update;
      }
    })
  });
})();
