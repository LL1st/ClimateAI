/* ClimateAI · tamaño de los puntos y efecto «lupa» del mapa (tarea 3.1).
   - Tamaño: los puntos miden la mitad de la separación entre ellos, según el ancho real
     del mapa, así quedan delgados y con aire entre sí (estilo «dot matrix»).
   - Lupa: al pasar el mouse, el punto crece y sus vecinos crecen menos según la distancia.
   Corre solo en el navegador (sin ir al servidor). Dash carga este archivo solo; el
   Dashboard lo activa con un clientside_callback cada vez que cambia la figura. */
(function () {
  var PROPORCION = 0.5;    // diámetro del punto / separación entre puntos
  var MIN_PX = 2.5, MAX_PX = 7;
  var CRECE = 2.3;         // el punto bajo el mouse crece a 2.3 veces su tamaño
  var RADIO_PASOS = 3.5;   // la lupa alcanza 3.5 separaciones a la redonda
  var ESPERA_SALIDA = 80;  // ms antes de soltar la lupa (evita parpadeo entre puntos)

  var estado = { gd: null, actual: -1, pendiente: null, cuadro: 0, salida: 0, base: 5 };

  // Plotly (Python) envía los números en binario: {dtype, bdata, _inputArray}. Esto devuelve el arreglo real.
  function arreglo(x) { return x && x._inputArray ? x._inputArray : x; }

  function meta(gd) { return (gd.layout && gd.layout.meta) || {}; }

  function factores(gd) {
    var f = meta(gd).factores, n = arreglo(gd.data[0].lat).length;
    return f && f.length === n ? f : new Array(n).fill(1);
  }

  // Tamaño base según el espacio real que ocupa el mapa (lon 360°, lat ~142°)
  function calcularBase(gd) {
    var t = gd._fullLayout && gd._fullLayout._size, paso = meta(gd).paso || 4;
    if (!t) return estado.base;
    var pxPorGrado = Math.min(t.w / 360, t.h / 142);
    return Math.max(MIN_PX, Math.min(MAX_PX, pxPorGrado * paso * PROPORCION));
  }

  function tamanos(gd, centro) {
    var t = gd.data[0], lat = arreglo(t.lat), lon = arreglo(t.lon), f = factores(gd);
    var n = lat.length, s = new Array(n), base = estado.base;
    for (var i = 0; i < n; i++) s[i] = base * f[i];
    if (centro < 0) return s;
    var radio = (meta(gd).paso || 4) * RADIO_PASOS;
    var lat0 = lat[centro], lon0 = lon[centro], c = Math.cos(lat0 * Math.PI / 180);
    for (var j = 0; j < n; j++) {
      var dlat = lat[j] - lat0, dlon = (lon[j] - lon0) * c;
      var d = Math.sqrt(dlat * dlat + dlon * dlon);
      if (d < radio) s[j] = s[j] * (1 + (CRECE - 1) * (1 - d / radio));
    }
    return s;
  }

  function aplicar(gd, centro) {
    window.Plotly.restyle(gd, { 'marker.size': [tamanos(gd, centro)] }, [0]);
  }

  function programar(gd, centro, forzar) {
    estado.pendiente = centro;
    if (forzar) estado.actual = null;
    if (estado.cuadro) return;
    estado.cuadro = window.requestAnimationFrame(function () {
      estado.cuadro = 0;
      if (estado.pendiente !== estado.actual) {
        estado.actual = estado.pendiente;
        aplicar(gd, estado.actual);
      }
    });
  }

  function esMapaDePuntos(gd) { return gd.data && gd.data[0] && gd.data[0].lat; }   // el coroplético no usa lupa

  function alPasar(e) {
    var p = e && e.points && e.points[0];
    if (!p || p.curveNumber !== 0 || !esMapaDePuntos(estado.gd)) return;
    window.clearTimeout(estado.salida);
    programar(estado.gd, p.pointNumber);
  }

  function alSalir() {
    window.clearTimeout(estado.salida);
    estado.salida = window.setTimeout(function () { programar(estado.gd, -1); }, ESPERA_SALIDA);
  }

  function ajustarTamano() {
    var gd = estado.gd;
    if (!gd || !esMapaDePuntos(gd)) return;
    estado.base = calcularBase(gd);
    programar(gd, -1, true);
  }

  function enganchar(intento) {
    var gd = document.querySelector('#mapa .js-plotly-plot');
    if (!gd || typeof gd.on !== 'function' || !gd._fullLayout || !gd._fullLayout._size) {
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
    // Plotly avisa cuando termina de redimensionar el mapa (por ejemplo, al cambiar el ancho de la ventana)
    if (gd.removeListener) gd.removeListener('plotly_relayout', alRedimensionar);
    gd.on('plotly_relayout', alRedimensionar);
    estado.gd = gd;
    ajustarTamano();
  }

  function alRedimensionar() {
    var gd = estado.gd;
    if (gd && Math.abs(calcularBase(gd) - estado.base) > 0.05) ajustarTamano();
  }

  var espera = 0;
  window.addEventListener('resize', function () {   // respaldo por si Plotly no emite el aviso
    window.clearTimeout(espera);
    espera = window.setTimeout(ajustarTamano, 400);
  });

  window.dash_clientside = Object.assign({}, window.dash_clientside, {
    climateai: Object.assign({}, (window.dash_clientside || {}).climateai, {
      activarLupa: function () {
        window.setTimeout(function () { enganchar(0); }, 0);
        return window.dash_clientside.no_update;
      }
    })
  });
})();
