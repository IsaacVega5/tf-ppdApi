import pytest
from pydantic import ValidationError
from app.models.Auth import AuthTokenResponse, TokenData

# Fixtures para datos de prueba
@pytest.fixture
def valid_token_data():
    return {
        "access_token": "access_token_123",
        "refresh_token": "refresh_token_456",
        "token_type": "bearer"
    }

@pytest.fixture
def minimal_token_data():
    return {
        "access_token": "access_token_123"
    }

@pytest.fixture
def valid_token_data_data():
    return {
        "username": "testuser"
    }

# Tests para TokenData
class TestTokenData:
    def test_create_with_valid_data(self, valid_token_data_data):
        token_data = TokenData(**valid_token_data_data)
        assert token_data.username == "testuser"

    def test_field_optional(self):
        token_data = TokenData(username=None)
        assert token_data.username is None

    def test_invalid_types(self):
        """Test TokenData model with invalid username type"""
        with pytest.raises(ValidationError):
            TokenData(username=123)  # Debe ser string

    def test_serialization(self):
        """Test TokenData model serialization to dict"""
        token_data = TokenData(username="testuser")
        token_data_dict = token_data.model_dump()
        assert token_data_dict == {"username": "testuser"}

# Tests para AuthTokenResponse
class TestToken:
    def test_create_with_valid_data(self, valid_token_data):
        token = AuthTokenResponse(**valid_token_data)
        assert token.access_token == "access_token_123"
        assert token.refresh_token == "refresh_token_456"
        assert token.token_type == "bearer"

    def test_create_with_partial_data(self, minimal_token_data):
        token = AuthTokenResponse(**minimal_token_data)
        assert token.access_token == "access_token_123"
        assert token.refresh_token is None
        assert token.token_type is None

    def test_create_with_empty_fields(self):
        token = AuthTokenResponse()
        assert token.access_token is None
        assert token.refresh_token is None
        assert token.token_type is None

    def test_invalid_types(self):
        """Test AuthTokenResponse model with invalid field types"""
        with pytest.raises(ValidationError):
            AuthTokenResponse(
                access_token=123,  # Debe ser string
                refresh_token=["invalid"],  # Debe ser string
                token_type=456  # Debe ser string
            )

    def test_serialization(self, valid_token_data):
        """Test AuthTokenResponse model serialization to dict"""
        token = AuthTokenResponse(**valid_token_data)
        token_dict = token.model_dump()
        assert token_dict == valid_token_data
