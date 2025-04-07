# ppdAPI - Primera Entrega 🚀

API para gestión de usuarios, instituciones y roles, construida con **FastAPI** y **SQLModel**.  
*(Parte del proyecto de Planificación y Desarrollo de Aplicaciones)*

---

## 📌 Estado del Proyecto  
### **Historias de Usuario (Taiga)**  
`HU-01`: Dashboard
`HU-02`: Registro de medidas  
`HU-04`: Cálculos de KPI  
`HU-03`: Generación de reportes  
`HU-06`: Definición de dead lines  
`HU-05`: Sistema de alertas de tiempo dead line


🔗 *Tablero Taiga:* `https://tree.taiga.io/project/isaacvega-monitoreo-ambiental/backlog`  

---

### 🗃️ Modelo de Datos  
```plaintext
User (Usuario)                Institution (Institución)
├─ UUID id_user               ├─ UUID id_institution
├─ username                   ├─ institution_name
├─ email (único)              └─ FK id_institution_type
└─ password (hash)

UserInstitution (Relación M:N)       InstitutionType (Tipo)
├─ PK id_user (FK)                   ├─ PK id_institution_type
├─ PK id_institution (FK)            └─ institution_type
└─ FK id_user_rol
```	

### ⚙️ Instalación Rápida
Clonar repositorio:
```	bash
git clone https://github.com/IsaacVega5/tf-ppdApi.git
```	
cd tf-ppdApi
Configurar entorno:
```	bash
cp .env.example .env  # Editar con tus credenciales
pip install -r requirements.txt
```	

Iniciar API:

```	bash
uvicorn app.main:app --reload
```	

Run Tests:

```	bash
python -m pytest
```	

### 📚 Documentación API
Accede a la interfaz interactiva:
- 🔗 Swagger UI: https://tf-ppdapi.onrender.com/docs
-  🔗 Redoc: https://tf-ppdapi.onrender.com/redoc

Swagger Preview

### 🛠️ Tecnologías Clave
- Python 3.10+
- FastAPI (Framework API)
- SQLModel + Pydantic (ORM)
- Alembic (DB Migrations)
- PostgreSQL (Producción) / SQLite (Desarrollo)
- Render (Despliegue)
- Neon (Host de PostgreSQL)
- JWT (Próxima implementación)

### ➡️ Próximos Pasos

Actualizar y extender cobertura de tests

Implementación de roles por institución

Configurar despliegue en Docker

### 🔗 Enlaces externos

| Nombre | Enlace |
| --- | --- |
| HU (Taiga) | https://tree.taiga.io/project/isaacvega-monitoreo-ambiental/backloghttps://tree.taiga.io/project/isaacvega-monitoreo-ambiental/backlog  |
| Modelo de datos | https://drive.google.com/file/d/1uAn58pCjgUSUlszfrvj2FbajfV92QorS/view?usp=drive_link |
|api host | https://tf-ppdapi.onrender.com/ |
