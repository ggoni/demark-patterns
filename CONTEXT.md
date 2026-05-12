Los indicadores de DeMark son una familia de herramientas de análisis técnico desarrolladas por Tom DeMark desde los años 70. Lo que los distingue del análisis técnico tradicional es que están diseñados para **anticipar agotamientos de tendencia** (exhaustion) en lugar de confirmar tendencias ya en curso. La mayoría son no paramétricos: cuentan eventos discretos sobre la serie de precios en vez de aplicar promedios móviles o filtros lineales. Esto los hace conceptualmente cercanos a un detector de cambio de régimen basado en reglas.

Te describo los más representativos: TD Sequential, TD Combo, TD DeMarker, TD REI y TD Pressure.

## TD Sequential

Es el más conocido y consta de dos fases encadenadas: **Setup** (9 barras) y **Countdown** (13 barras). La idea es que una tendencia que se sostiene "demasiado" empieza a agotarse, y el conteo formaliza ese "demasiado".

El Buy Setup busca un posible piso de mercado, comparando cada cierre con el cierre cuatro barras atrás.

```python
def buy_setup(close):
    """
    Devuelve los índices donde se completa un Buy Setup (9 barras).
    Precondición: 'price flip' bajista — close[i-1] >= close[i-5] y close[i] < close[i-4].
    """
    completed = []
    count = 0
    for i in range(5, len(close)):
        price_flip = close[i-1] >= close[i-5] and count == 0
        if (count == 0 and price_flip and close[i] < close[i-4]) \
           or (count > 0 and close[i] < close[i-4]):
            count += 1
            if count == 9:
                # Setup completo. "Perfection" requiere:
                #   min(low[i], low[i-1]) <= min(low[i-2], low[i-3])
                # es decir, low de las barras 8 u 9 <= low de barras 6 y 7.
                completed.append(i)
                count = 0
        else:
            count = 0
    return completed
```

El Sell Setup es simétrico: se reemplaza `<` por `>` sobre `close` y, para la perfection, se trabaja con `high` en vez de `low`. Una vez completado un Setup, comienza el Countdown, que no exige consecutividad y compara contra el low (o high) dos barras atrás.

```python
def buy_countdown(start, close, low):
    """
    Empieza inmediatamente después de un Buy Setup completado.
    Cuenta hasta 13 barras (no necesariamente consecutivas) en que close[i] <= low[i-2].
    """
    count = 0
    bar8_close = None
    i = start + 1
    while i < len(close):
        if close[i] <= low[i-2]:
            count += 1
            if count == 8:
                bar8_close = close[i]
            if count == 13:
                # "Cualificación" estándar: la barra 13 debe cerrar
                # en o por debajo del cierre de la barra 8.
                if bar8_close is not None and close[i] <= bar8_close:
                    return i
                # Si no cualifica, se busca la siguiente barra que sí cumpla
                # (regla "+1"); el contador no se reinicia.
                count = 12
        i += 1
    return None
```

Hay además condiciones de **cancelación** del Countdown, principalmente los niveles TDST (TD Setup Trend), que son los extremos de la barra 1 del Setup previo: si el precio los rompe en dirección contraria al Setup, el Countdown queda invalidado.

## TD Combo

Es una variante más estricta del Sequential. La diferencia clave es que el Countdown de Combo empieza junto con el Setup (no después) y exige condiciones simultáneas en cada barra, en vez de solo la condición de close vs. low/high de dos barras atrás.

```python
def buy_combo_count(i, close, low, high):
    # Las cuatro condiciones de Combo (versión "original") para una barra de conteo:
    return (close[i] <= low[i-2]
            and low[i] < low[i-1]
            and high[i] < high[i-1]
            and close[i] < close[i-1])
```

Se acumulan 13 barras que cumplan todas las condiciones para un setup de compra; las versiones más nuevas relajan algunas condiciones después del conteo 10.

## TD DeMarker (DeM)

Es un oscilador acotado en [0, 1] que mide expansión asimétrica de máximos vs. mínimos en una ventana. Es probablemente el más simple de implementar.

```python
def td_demarker(high, low, n=14):
    de_max = [max(high[i] - high[i-1], 0) for i in range(1, len(high))]
    de_min = [max(low[i-1] - low[i], 0) for i in range(1, len(low))]
    dem = []
    for i in range(n, len(de_max)):
        sma_max = sum(de_max[i-n:i]) / n
        sma_min = sum(de_min[i-n:i]) / n
        denom = sma_max + sma_min
        dem.append(sma_max / denom if denom > 0 else 0.5)
    return dem
```

La interpretación habitual: lecturas bajo 0.3 sugieren sobreventa, sobre 0.7 sobrecompra. Funcionalmente es primo del RSI, pero usa solo extremos en vez de retornos.

## TD Range Expansion Index (REI)

Es un oscilador acotado en [-100, 100] que mide cuánto los máximos y mínimos actuales se han expandido respecto a dos barras atrás, filtrando barras "atrapadas" dentro del rango reciente.

```python
def td_rei(high, low, period=8):
    rei = []
    for i in range(period + 5, len(high)):
        num = 0.0
        denom = 0.0
        for j in range(period):
            k = i - j
            # Condición de "no consolidación": la barra debe haber
            # roto los rangos de hace 5 o 6 barras.
            cond_high = high[k] >= low[k-5] or high[k] >= low[k-6]
            cond_low  = low[k]  <= high[k-5] or low[k]  <= high[k-6]
            delta_h = high[k] - high[k-2]
            delta_l = low[k]  - low[k-2]
            if cond_high and cond_low:
                num += delta_h + delta_l
            denom += abs(delta_h) + abs(delta_l)
        rei.append(100.0 * num / denom if denom > 0 else 0.0)
    return rei
```

Las señales clásicas son lecturas extremas (>60 o <-60) sostenidas, seguidas de "duration analysis": una salida del nivel extremo en pocas barras señala continuación; si permanece muchas barras, señala posible reversión.

## TD Pressure

Mide cuánto del rango de la barra fue cubierto por la diferencia open-to-close, ponderado por volumen. Es una proxy de presión compradora vs. vendedora.

```python
def td_pressure(open_, close, high, low, volume, n=5):
    pressure = []
    for i in range(n, len(close)):
        num = 0.0
        denom = 0.0
        for k in range(i - n + 1, i + 1):
            rng = high[k] - low[k]
            if rng > 0:
                num += ((close[k] - open_[k]) / rng) * volume[k]
            denom += volume[k]
        pressure.append(100.0 * num / denom if denom > 0 else 0.0)
    return pressure
```

Valores positivos altos indican presión compradora dominante en la ventana, negativos lo contrario. Suele usarse como confirmador de señales de Sequential o REI más que de forma aislada.

---

Una observación práctica: si vas a backtestear estos indicadores, ten cuidado con dos cosas. Primero, las reglas de cancelación y "perfection" cambian materialmente las señales y muchas implementaciones open-source las omiten, lo que te dará resultados que no replican los del libro de DeMark. Segundo, Sequential es un indicador con muy baja frecuencia de señales (semanas o meses entre completaciones en intraday), así que las muestras estadísticas son chicas y los intervalos de confianza sobre métricas como Sharpe o hit ratio suelen ser amplios. Vale la pena hacer bootstrap antes de declarar edge.

Si quieres, puedo expandir alguno (la lógica completa de TDST y reciclaje en Sequential, por ejemplo, que es donde están la mitad de los detalles que importan) o armar una implementación funcional en Python con pandas.