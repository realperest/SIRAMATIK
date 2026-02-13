"""Timezone kontrol scripti"""
from database import engine
from sqlalchemy import text
from sqlalchemy.orm import Session

with Session(engine) as session:
    result = session.execute(text("SELECT current_setting('timezone') as tz, NOW() as now"))
    row = result.fetchone()
    print(f"Timezone: {row[0]}")
    print(f"NOW(): {row[1]}")
