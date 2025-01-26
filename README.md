# ppdAPI - Primera Entrega 🚀

API para gestión de usuarios, instituciones y roles, construida con **FastAPI** y **SQLModel**.  
*(Parte del proyecto de Planificación y Desarrollo de Aplicaciones)*

---

## 📌 Estado del Proyecto  
### **Historias de Usuario (Taiga)**  
`HU-01`: Gestión de usuarios *(Completado)*  
`HU-02`: Vinculación usuario-institución *(En progreso)*  
`HU-03`: Tipos de instituciones *(Pendiente)*  
🔗 *Tablero Taiga:* `[Enlace pendiente]`  

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

### 📡 Endpoints Implementados
- Usuarios (/user)

Método  Ruta  Descripción  Estado

- GET  /  Listar todos los usuarios  ✅ Funcional
- GET  /{id_user}  Obtener usuario por UUID  ✅ Funcional
- Instituciones (/institution)
  
[EN CONSTRUCCIÓN] (Próxima entrega)

### 📚 Documentación API
Accede a la interfaz interactiva:
- 🔗 Swagger UI: http://localhost:8000/docs
-  🔗 Redoc: http://localhost:8000/redoc

Swagger Preview

### 🛠️ Tecnologías Clave
Python 3.10+

FastAPI (Framework API)

SQLModel + Pydantic (ORM)
Alembic (DB Migrations)

PostgreSQL (Producción) / SQLite (Desarrollo)

JWT (Próxima implementación)

### ➡️ Próximos Pasos
Implementar CRUD completo para instituciones

Añadir autenticación JWT

Configurar despliegue en Docker

Documentar relaciones entre entidades


### 🔗 Enlaces externos

| Nombre | Enlace |
| --- | --- |
| HU (Taiga) | https://tree.taiga.io/project/isaacvega-monitoreo-ambiental/backloghttps://tree.taiga.io/project/isaacvega-monitoreo-ambiental/backlog  |
| Modelo de datos | https://drive.google.com/file/d/1uAn58pCjgUSUlszfrvj2FbajfV92QorS/view?usp=drive_link |