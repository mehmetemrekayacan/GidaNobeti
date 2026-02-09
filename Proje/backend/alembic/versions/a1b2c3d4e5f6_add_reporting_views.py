"""Add reporting views (view_daily_statistics, view_risky_restaurants)

Revision ID: a1b2c3d4e5f6
Revises: 6cd1533566ec
Create Date: 2026-02-09

SPEC.md 3.3 uyumlu - Admin dashboard raporlama için.
"""
from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "6cd1533566ec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Dashboard için günlük özet (yurt bazlı)
    op.execute("""
        CREATE VIEW view_daily_statistics AS
        SELECT
            d.id AS dorm_id,
            d.name AS dorm_name,
            DATE(o.declared_at) AS date,
            COUNT(DISTINCT o.id) AS total_orders,
            COUNT(DISTINCT o.user_id) AS active_students,
            COUNT(DISTINCT o.restaurant_id) AS unique_restaurants,
            COUNT(DISTINCT hi.id) AS total_incidents,
            SUM(o.total_amount) AS total_spent
        FROM dormitories d
        LEFT JOIN users u ON u.dorm_id = d.id
        LEFT JOIN orders o ON o.user_id = u.id
        LEFT JOIN health_incidents hi ON hi.user_id = u.id
            AND DATE(hi.report_date) = DATE(o.declared_at)
        WHERE o.declared_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY d.id, d.name, DATE(o.declared_at)
    """)

    # Riskli restoranlar raporu (PostgreSQL VIEW'da ORDER BY yok - sorgu sırasında uygulanır)
    op.execute("""
        CREATE VIEW view_risky_restaurants AS
        SELECT
            r.id,
            r.name,
            r.current_risk_status,
            r.total_complaints,
            r.total_orders,
            ROUND((r.total_complaints::DECIMAL / NULLIF(r.total_orders, 0)) * 100, 2) AS complaint_rate,
            COUNT(DISTINCT hi.id) AS confirmed_incidents,
            MAX(hi.report_date) AS last_incident_date
        FROM restaurants r
        LEFT JOIN orders o ON o.restaurant_id = r.id
        LEFT JOIN health_incidents hi ON hi.suspected_order_id = o.id
            AND hi.status = 'CONFIRMED'
        WHERE r.current_risk_status IN ('RED_FLAG', 'BLACKLISTED')
        GROUP BY r.id, r.name, r.current_risk_status, r.total_complaints, r.total_orders
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS view_risky_restaurants")
    op.execute("DROP VIEW IF EXISTS view_daily_statistics")
