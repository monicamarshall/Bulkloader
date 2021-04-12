from django.db import models


class Speaker(models.Model):

    speaker_id = models.AutoField(primary_key=True)
    first_name = models.TextField()
    last_name = models.TextField()
    title = models.TextField()
    company = models.TextField()
    speaker_bio = models.TextField()
    speaker_photo= models.BinaryField(default=None, blank=True, null=True);
    
    class Meta:
        db_table = "speakers"
        ordering = ('speaker_id', )


