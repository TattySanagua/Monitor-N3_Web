# Monitor-N3_Web

**Monitor N3** es una aplicación web integral para el monitoreo de niveles, gestión de instrumentos y análisis predictivo de la Presa Lateral Nº 3 del Dique de El Cadillal. Este sistema está diseñado para registrar, visualizar y analizar datos obtenidos de instrumentos como piezómetros, freatímetros y aforadores, así como datos climáticos y de embalse.


---

## Características principales

- Registro y consulta de mediciones de diferentes instrumentos.
- Generación de gráficos personalizados y predefinidos.
- Cálculos estadísticos y análisis de auscultación.
- Gestión de usuarios con roles diferenciados: Administrador, Técnico e Invitado.
- Acceso mediante login seguro con autenticación.
- Visualización de resultados en tablas, reportes y gráficos.

---

## Tecnologías utilizadas

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Gráficos:** Plotly
- **Base de datos:** MySQL
- **Despliegue:** Servidor local con opción de acceso remoto (ngrok)

---

## Estructura del sistema

- **Instrumentos:** Piezómetros, Freatímetros, Aforadores volumétricos y Parshall
- **Mediciones:** Ingreso de lectrura, cálculo de magnitud física y persistencia en la base de datos
- **Visualización:** Tablas, gráficos, y auscultación estadística
- **Procesos principales:**
  - Administración de instrumentos
  - Registro y consulta de mediciones, nivel de embalse y precipitaciones
  - Generación de gráficos predefinidos y personalizados
  - Generación de estadísticas de la auscultación y predicción
  - Generación de reportes de mediciones

---

## Roles y permisos

| Rol         | Funciones principales                                                                          |
|-------------|------------------------------------------------------------------------------------------------|
| **Administrador** | Lectura y escritura, Gestión completa del sistema                                              |
| **Técnico**       | Lectura y escritura, carga de nuevas mediciones, consulta de datos, reportes y visualizaciones |
| **Invitado**      | Lectrura, consulta de datos, reportes y visualizaciones                                        |

---

## Documentación técnica

- Documento de Especificación de Requisitos
- Diagrama de Flujo de Datos (DFD) – Niveles 0, 1 y 2
- Modelo Entidad-Relación (ER)
- Diseño de Interfaces
- Pruebas manuales (UAT)
- Pruebas manuales funcionales

---

### Autoría

Este proyecto fue desarrollado por Tatiana Sanagua como parte del Proyecto Final de la carrera de Ingeniería en Informática de la Facultad de Ciencias Exactas y Tecnología de Tucumán - Universidad Nacional de Tucumán.

---

### Contacto

Podés comunicarte conmigo a través de:

- 📧 Email: tatiana_sanagua@hotmail.com ó tati.sanagua@gmail.com  
- 💼 LinkedIn: https://www.linkedin.com/in/maría-tatiana-sanagua-349701215/  
- 🐙 GitHub: https://github.com/TattySanagua