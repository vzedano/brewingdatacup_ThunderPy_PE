
1. Para cumplir con el enunciado del reto, necesitamos un dataframe que represente las ventas con la información del cliente por cada venta y un target que represtaría si esta venta es venta por promoción o no.
    - Para esto tenemos que intersectar información histórica de ventas y de promociones ejecutadas (`executed_promo`). Como vemos que la información de las promoción ejecutadas tiene duplicados en conjunto de todas las columnas menos la columna `CodigoDC` (`Cliente`,`Marca`,`Cupo`), primero procederemos a eliminar los duplicados del dataframe de promociones ejecutadas.
    - Para poder marcar las ventas que aplicaron a alguna promoción, agregaremos una columna "ES_PROMO" que servirá de target más explícito, si bien la presencia de un valor en la columna `CodigoDC` igual indicaba eso.

