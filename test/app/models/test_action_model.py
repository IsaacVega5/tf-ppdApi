import pytest
from uuid import UUID
# from typing import Optional
# from pydantic import ValidationError
from sqlmodel import Session, SQLModel, create_engine
from app.models.Action import Action, ActionBase
from app.models import ActionType, Ppda

# Fixtures para datos de prueba
@pytest.fixture
def valid_action_data():
    return {
        "id_ppda": "PPDA-123",
        "rut_creator": "12.345.678-9",
        "id_action_type": 1
    }

@pytest.fixture
def minimal_action_data():
    return {
        "id_action": "550e8400-e29b-41d4-a716-446655440000"
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

# Tests para ActionBase
class TestActionBase:
    def test_create_with_valid_data(self, valid_action_data):
        """Test que ActionBase se crea correctamente con datos válidos"""
        action = ActionBase(**valid_action_data)
        
        assert action.id_ppda == "PPDA-123"
        assert action.rut_creator == "12.345.678-9"
        assert action.id_action_type == 1

    def test_all_fields_optional(self):
        """Test que todos los campos de ActionBase son opcionales"""
        action = ActionBase()
        assert action.id_ppda is None
        assert action.rut_creator is None
        assert action.id_action_type is None

    @pytest.mark.parametrize("rut", [
        "12345678-9",  # Sin puntos
        "12.345.678-K",  # Con K válida
        None,  # Nulo es permitido
    ])
    def test_valid_rut_formats(self, valid_action_data, rut):
        """Test que acepta varios formatos válidos de RUT"""
        valid_action_data["rut_creator"] = rut
        action = ActionBase(**valid_action_data)
        assert action.rut_creator == rut

# Tests para Action
class TestAction:
    def test_inherits_from_actionbase(self):
        """Test que Action hereda correctamente de ActionBase"""
        assert issubclass(Action, ActionBase)
        assert issubclass(Action, SQLModel)

    def test_auto_generated_uuid(self):
        """Test que se genera automáticamente un UUID válido"""
        action = Action()
        assert action.id_action is not None
        try:
            UUID(action.id_action)
        except ValueError:
            pytest.fail("id_action no es un UUID válido")

    def test_custom_uuid(self, minimal_action_data):
        """Test que se puede establecer un UUID personalizado"""
        action = Action(**minimal_action_data)
        assert action.id_action == "550e8400-e29b-41d4-a716-446655440000"

    def test_table_configuration(self):
        """Test que la configuración de la tabla es correcta"""
        assert Action.__tablename__ == "action"
        assert Action.__table__.primary_key.columns.keys() == ["id_action"]

    def test_relationships_defined(self):
        """Test que las relaciones están correctamente definidas"""
        assert hasattr(Action, "action_type")
        assert hasattr(Action, "ppda")
        assert hasattr(Action, "deadlines")
        assert hasattr(Action, "kpi_list")
        assert hasattr(Action, "report")

# Tests de integración con base de datos
class TestActionDB:
    @pytest.fixture(autouse=True)
    def setup_db(self, session: Session):
        """Configuración para tests de DB"""
        self.session = session

    def test_save_to_database(self, valid_action_data):
        """Test guardar en DB"""
        action = Action(**valid_action_data)
        self.session.add(action)
        self.session.commit()
        self.session.refresh(action)
        
        assert action.id_action is not None
        assert UUID(action.id_action)  # Verifica que es UUID válido

    def test_retrieve_from_database(self, valid_action_data):
        """Test recuperar de DB"""
        # Crear y guardar
        action = Action(**valid_action_data)
        self.session.add(action)
        self.session.commit()
        
        # Recuperar
        retrieved = self.session.get(Action, action.id_action)
        
        # Verificaciones básicas
        assert retrieved is not None
        assert retrieved.id_action == action.id_action
        
        # Verificar todos los campos contra el fixture original
        for field in valid_action_data:
            assert getattr(retrieved, field) == valid_action_data[field]
        
        # Verificar que el UUID se mantuvo igual
        assert retrieved.id_action == action.id_action

    def test_foreign_key_constraints(self, valid_action_data):
        """Test que las FK son válidas (requiere modelos relacionados)"""
        
        # Crear registros relacionados
        action_type = ActionType(id_action_type=1, action_type="Test")
        ppda = Ppda(id_ppda="PPDA-2023-001") 
        
        self.session.add_all([action_type, ppda])
        self.session.commit()
        
        # Ahora crear el Action con relaciones válidas
        action = Action(**valid_action_data)
        self.session.add(action)
        self.session.commit()
        
        assert action.id_action is not None

    def test_relationship_operations(self):
        """Test operaciones con relaciones (ejemplo con ActionType)"""
                
        # Crear ActionType primero
        action_type = ActionType(id_action_type=1, action_type="Test Action")
        self.session.add(action_type)
        self.session.commit()
        
        # Crear Action relacionado
        action = Action(
            id_ppda="PPDA-2023-001",
            rut_creator="12.345.678-9",
            id_action_type=1
        )
        self.session.add(action)
        self.session.commit()
        
        # Verificar relación
        assert action.action_type is not None
        assert action.action_type.id_action_type == 1
        assert action.action_type.action_type == "Test Action"