from django.db import migrations, models, transaction
from django.db.migrations import RunSQL

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_alter_project_keywords"),
    ]

    operations = [
        # Custom SQL to convert data to jsonb format
        RunSQL(
            sql="""
                BEGIN;
                ALTER TABLE core_project ALTER COLUMN keywords TYPE jsonb USING keywords::text::jsonb;
                COMMIT;
            """,
            reverse_sql="""
                BEGIN;
                ALTER TABLE core_project ALTER COLUMN keywords TYPE character varying[] USING keywords::text::character varying[];
                COMMIT;
            """,
            state_operations=[
                migrations.AlterField(
                    model_name='project',
                    name='keywords',
                    field=models.JSONField(blank=True, null=True),
                ),
            ]
        ),

        # Alter field to JSONField
        migrations.AlterField(
            model_name="project",
            name="keywords",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
