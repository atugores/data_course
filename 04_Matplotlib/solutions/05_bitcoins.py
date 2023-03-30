plt.figure(figsize=(16,7))

# Creamos una línea negra de la serie temporal
plt.plot(precio_index, precio, linestyle="--", color="black")

# Marcamos con puntos rojos los días donde el Bitcoin perdió valor respecto al día anterior
plt.plot(cambio_neg_index, cambio_neg,  marker="o", linestyle="",label="Pérdidas", color="red")

# Marcamos con puntos verdes los días donde el Bitcoin ganó valor respecto al día anterior
plt.plot(cambio_pos_index, cambio_pos,  marker="o", linestyle="",label="Ganancias", color="green")

# Resaltamos la zona que va del precio máximo del Bitcoin hasta la mitad de su précio máximo
plt.axhspan(precio_mitad, precio_maximo, alpha = 0.1)  

# Marcamos los puntos en los que el bitcoin se mantuvo en un 75% del precio máximo o más
plt.plot(precio_index[precio > precio_cuarto], precio[precio > precio_cuarto],marker=".", linestyle="",
         label = 'Precio > Precio max * 0.75', color="yellow")  

# Asignamos las fechas correspondientes en el eje X, y rotamos 45º
plt.xticks(xticks_val, xticks_text,rotation=45)

# Colocamos la leyenda en la parte superior izquierda del gráfico
plt.legend(loc="upper left")  

# Colocamos la etiqueta en el eje x
plt.xlabel('Fecha')  

# Colocamos la etiqueta en el eje y
plt.ylabel('Precio en dolares($)')  

# Dibujamos la rejilla 
plt.grid()

# Colocamos el título del gráfico
plt.title(u'Precio Bitcoin Agosto 2017 - Junio 2018')
