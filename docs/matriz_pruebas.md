# Matriz de pruebas

| ID | Prueba | Entrada/condicion | Resultado esperado | Resultado real | Estado |
|---|---|---|---|---|---|
| TP-01 | Recepcion normal | 3 tramas JSON validas | 3 aceptadas y CSV generado | 3 aceptadas | PASS |
| TP-02 | Identificacion | `device_id=SIM-001` | ID conservado en registros/reporte | Conservado | PASS |
| TP-03 | Anomalia | Temperatura 95 C | Clasificar ANOMALO sin detenerse | Clasificada | PASS |
| TP-04 | JSON corrupto | `{bad-json}` | Registrar error y continuar | Error registrado, siguiente aceptada | PASS |
| TP-05 | Rango invalido | Temperatura 999 C | Rechazar trama | Rechazada | PASS |
| TP-06 | Desconexion | Cierre del socket | Registrar comunicacion perdida | Registrada | PASS |
| TP-07 | Dispositivo ausente | Sin cliente TCP | Estado controlado `device_unavailable` | Reportado | PASS |
| TP-08 | Persistencia | CSV/JSON/log en `output/` | Archivos legibles con metricas | Generados | PASS |
