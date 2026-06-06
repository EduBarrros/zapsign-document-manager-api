import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0005_document_extracted_text'),
        ('signers', '0003_signer_sign_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signer',
            name='document',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='signers',
                to='documents.document',
            ),
        ),
    ]
