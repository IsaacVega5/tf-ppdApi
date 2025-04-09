# def test_login_invalid_credentials(session: Session, sample_user: User):
#     """Prueba login con credenciales inválidas."""
#     with patch('app.utils.auth.verify_password', return_value=False):
#         user_login = UserLogin(username="testuser", password="wrongpass")
        
#         with pytest.raises(HTTPException) as exc_info:
#             login(user_login, session)
        
#         assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
#         assert "Invalid user or password" in exc_info.value.detail

# def test_refresh_token_success(session: Session, sample_user: User):
#     """Prueba refresh token exitoso."""
#     with patch('app.utils.auth.generate_access_token', return_value="new_access_token"), \
#          patch('app.utils.auth.generate_refresh_token', return_value=("new_refresh_token", "new_jti", datetime.now())):
        
#         result = refresh_token("testuser", session)
        
#         assert isinstance(result, Token)
#         assert result.access_token == "new_access_token"
#         assert result.refresh_token == "new_refresh_token"

# def test_refresh_token_invalid_user(session: Session):
#     """Prueba refresh token con usuario inválido."""
#     with pytest.raises(HTTPException) as exc_info:
#         refresh_token("nonexistent", session)
    
#     assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
#     assert "Invalid username" in exc_info.value.detail

# def test_create_token_response(session: Session, sample_user: User):
#     """Prueba creación de respuesta de token."""
#     with patch('app.utils.auth.generate_access_token', return_value="access_token"), \
#          patch('app.utils.auth.generate_refresh_token', return_value=("refresh_token", "jti", datetime.now())):
        
#         result = create_token_response(sample_user, session)
        
#         assert isinstance(result, Token)
#         # Verificar que se creó el refresh token en la base de datos
#         db_token = session.exec(sql.select(RefreshToken)).first()
#         assert db_token is not None
#         assert db_token.id_user == sample_user.id_user