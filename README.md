software que les permita gestionar su
proceso interno de votaciones, que normalmente realizan 2 veces al año. Para ello, se
requiere realizar un módulo en odoo v18 que permita:
1.- Crear las sedes de la universidad. (CRUD)
2.- Crear estudiantes (Usando el modelo: res.partner) con su respectiva carrera y sede.
Además, que no permita duplicidad de nro de identificación.(CRUD)
3.- Crear candidatos (Usando el modelo: res.partner) no permita duplicidad de nro de
identificación.(CRUD)
4.- Crear proceso de votaciones con los siguientes datos: (CRUD)
*Descripción de la votación
*Periodo de votación en formato fecha y hora (no se podrá realizar votaciones cuando el
proceso se encuentre cerrado en el país asociado a la votación, pero se podrán realizar
votaciones desde cualquier pais)
*Candidatos (res.partner que no sean estudiantes). Una votación podrá tener N candidatos
y 1 candidato podrá estar en N votaciones.
*Cantidad de votos por candidato ( con la foto del candidato )
*Estados: (es un campo que permite saber el estado de la votación)
- Borrador: es el estado inicial que permite saber la votación se están preparando.
- En proceso: es el estado en el cual se podrán realizar votaciones.
- Cerrada: es el estado en el cual quedan las votaciones que han finalizado.
4.- Se debe agregar una acción que permita iniciar 1 o N votaciones al tiempo.
5.- En la página web de odoo, se debe agregar una opción para que los estudiantes puedan
acceder con su nro de cédula, seleccionen la votación en la que va a participar, puedan
seleccionar un candidato y finalizar la votación mediante un botón.
6.- Se debe agregar una vista pivote en el ERP, que permita ver la cantidad de votos que
obtuvo cada candidato.
7.- Se debe agregar un menú que muestre un wizard y que permita importar un archivo con
N procesos de votaciones mediante sql (insert a la base de datos). Luego de que sea

importada, los procesos importados deben quedar en estado “borrador” para que sea
iniciada manualmente mediante un botón en el ERP.
*En el wizard debe quedar una plantilla ejemplo de la estructura del archivo para que el
usuario la pueda descargar.
Consideraciones:
.- Las sedes de la universidad tienen diferente zona horaria, por lo cual se debe validar que
no se pueda realizar una votación fuera de las fechas y horas establecidas para dicha
votación en ese pais.
Ejemplo: si un proceso de votación en la sede de Venezuela está abierto hasta las 6pm,
Un estudiante de la sede de Venezuela pero que se encuentra conectado desde Colombia,
podría votar hasta las 4.59pm Hora Colombia. (GMT-5)
.- Cada estudiante podrá realizar una votación una única vez.
