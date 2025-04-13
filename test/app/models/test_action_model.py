import pytest
from uuid import UUID
from typing import Optional
from pydantic import ValidationError
from sqlmodel import SQLModel
from app.models.Action import Action, ActionBase

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
