from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0001_initial'),
        ('bugs', '0002_initial'),
    ]

    operations = [
        # 先删除旧的CharField字段
        migrations.RemoveField(
            model_name='bug',
            name='module',
        ),
        # 添加新的ForeignKey字段
        migrations.AddField(
            model_name='bug',
            name='module',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='bugs',
                to='modules.module',
                verbose_name='所属模块'
            ),
        ),
    ]
