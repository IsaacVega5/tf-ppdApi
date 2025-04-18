import pytest
from sqlmodel import Session, SQLModel, create_engine
from app.models.ActionType import ActionType, ActionTypeBase

# Fixtures para datos de prueba
@pytest.fixture
def valid_action_type_data():
    return {
        "action_type": "Login"
    }

@pytest.fixture
def minimal_action_type_data():
    return {
        "id_action_type": 1
    }

# Configuración de base de datos en memoria
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(name="session", scope="function")
def session_fixture():
    """Fixture para sesión de base de datos con transacción aislada por test."""
    # Crear todas las tablas
    SQLModel.metadata.create_all(engine)
    
    # Iniciar una nueva transacción
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session  # Proporcionar la sesión al test

    # Limpieza post-test
    session.close()
    transaction.rollback()  # Deshacer cualquier cambio
    connection.close()

# Tests para ActionTypeBase
class TestActionTypeBase:
    def test_create_with_valid_data(self, valid_action_type_data):
        action_type = ActionTypeBase(**valid_action_type_data)
        assert action_type.action_type == "Login"

    def test_field_optional(self):
        action_type = ActionTypeBase(action_type=None)
        assert action_type.action_type is None

# Tests para ActionType
class TestActionType:
    def test_inherits_from_actiontypebase(self):
        """Verifica la herencia correcta"""
        assert issubclass(ActionType, ActionTypeBase)
        assert issubclass(ActionType, SQLModel)

    def test_table_configuration(self):
        """Verifica configuración de tabla"""
        assert ActionType.__tablename__ == "action_type"
        assert hasattr(ActionType, "__table__")
        # Verifica que id_action_type es la primary key
        assert ActionType.__table__.primary_key.columns.keys() == ["id_action_type"]

    def test_primary_key_autoincrement(self, minimal_action_type_data):
        """Test que id_action_type es llave primaria autoincremental"""
        action_type = ActionType(**minimal_action_type_data)
        assert action_type.id_action_type == 1

    def test_relationship_defined(self):
        """Test que la relación con Action está definida"""
        assert hasattr(ActionType, "action")
        # Verifica el back_populates si es necesario
        relationship = ActionType.__sqlmodel_relationships__["action"]
        assert relationship.back_populates == "action_type"

    def test_relationship_empty_by_default(self):
        """Test que la relación con Action viene vacía por defecto"""
        action_type = ActionType()
        assert action_type.action == []

# Tests de integración con base de datos
class TestActionTypeDB:
    def test_save_to_database(self, session: Session, valid_action_type_data):
        """Test que se puede guardar en base de datos"""
        action_type = ActionType(**valid_action_type_data)
        session.add(action_type)
        session.commit()
        session.refresh(action_type)
        
        assert action_type.id_action_type is not None
        assert action_type.action_type == "Login"

    def test_retrieve_from_database(self, session: Session, valid_action_type_data):
        """Test que se puede recuperar de la base de datos"""
        # Crear y guardar
        action_type = ActionType(**valid_action_type_data)
        session.add(action_type)
        session.commit()
        
        # Recuperar
        retrieved = session.get(ActionType, action_type.id_action_type)
        assert retrieved is not None
        assert retrieved.action_type == "Login"
        assert retrieved.id_action_type == action_type.id_action_type

    def test_update_action_type(self, session: Session, valid_action_type_data):
        """Test que se puede actualizar un ActionType"""
        # Crear
        action_type = ActionType(**valid_action_type_data)
        session.add(action_type)
        session.commit()
        
        # Actualizar
        new_type = "Logout"
        action_type.action_type = new_type
        session.commit()
        session.refresh(action_type)
        
        # Verificar
        updated = session.get(ActionType, action_type.id_action_type)
        assert updated.action_type == new_type

    def test_delete_action_type(self, session: Session, valid_action_type_data):
        """Test que se puede eliminar un ActionType"""
        action_type = ActionType(**valid_action_type_data)
        session.add(action_type)
        session.commit()
        
        # Eliminar
        session.delete(action_type)
        session.commit()
        
        # Verificar
        deleted = session.get(ActionType, action_type.id_action_type)
        assert deleted is None