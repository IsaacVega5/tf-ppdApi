import sqlmodel as sql
from fastapi import HTTPException, status
from app.models.Report import Report

async def get_all(session: sql.Session):
    """
    Retrieve all reports from the database.
    Args:
        session (sql.Session): Database session for operations.
    Returns:
        List[Report]: List of all report objects.
    """
    statement = sql.select(Report)
    reports = session.exec(statement).all()
    return reports

async def get_by_id(id: str, session: sql.Session):
    """
    Retrieve a single report by its unique identifier.
    Args:
        id (str): The UUID of the report to retrieve.
        session (sql.Session): Database session for operations.
    Returns:
        Report: The requested report object.
    Raises:
        HTTPException: 404 if report is not found.
    """
    statement = sql.select(Report).where(Report.id_report == id)
    report = session.exec(statement).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report

async def create_report(report_data, session: sql.Session):
    """
    Create a new report in the database.
    Args:
        report_data: Data for the new report (should be compatible with Report model).
        session (sql.Session): Database session for operations.
    Returns:
        Report: The newly created report object.
    """
    report = Report(**report_data.model_dump()) if hasattr(report_data, 'model_dump') else Report(**dict(report_data))
    session.add(report)
    session.commit()
    session.refresh(report)
    return report

async def update_report(id: str, report_data, session: sql.Session):
    """
    Update an existing report in the database.
    Args:
        id (str): The UUID of the report to update.
        report_data: Partial or full data to update (should be compatible with Report model).
        session (sql.Session): Database session for operations.
    Returns:
        Report: The updated report object.
    Raises:
        HTTPException: 404 if report is not found.
    """
    statement = sql.select(Report).where(Report.id_report == id)
    report = session.exec(statement).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    update_dict = report_data.model_dump(exclude_unset=True) if hasattr(report_data, 'model_dump') else dict(report_data)
    for key, value in update_dict.items():
        setattr(report, key, value)
    session.commit()
    session.refresh(report)
    return report

async def delete_report(id: str, session: sql.Session):
    """
    Delete a report from the database by its ID.
    Args:
        id (str): The UUID of the report to delete.
        session (sql.Session): Database session for operations.
    Returns:
        dict: Confirmation message with deleted report ID.
    Raises:
        HTTPException: 404 if report is not found.
    """
    statement = sql.select(Report).where(Report.id_report == id)
    report = session.exec(statement).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    session.delete(report)
    session.commit()
    return {"detail": "Report deleted", "id": id}
