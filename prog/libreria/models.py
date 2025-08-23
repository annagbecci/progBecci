from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static


class Tag(models.Model):
    nome = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.nome


class Comune(models.Model):
    cap = models.CharField(max_length=10)
    comune = models.CharField(max_length=50)
    provincia = models.CharField(max_length=2)

    def save(self, *args, **kwargs):
        self.provincia = self.provincia.upper()  # trasforma in maiuscolo prima di salvare
        super().save(*args, **kwargs)

    def __str__(self):
        return self.comune

    class Meta:
        verbose_name_plural = 'Comuni'


class Autore(models.Model):
    nome = models.CharField(max_length=100)
    biografia = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = 'Autori'


class Link(models.Model):
    nome = models.CharField(max_length=50)  # ad esempio: Instagram, Facebook, Discord, ...
    link_social = models.URLField()

    def __str__(self):
        return self.nome


class Utente(AbstractUser):
    links = models.ManyToManyField('Link', blank=True)
    immagine = models.ImageField(upload_to='profili/', blank=True, null=True)
    comune = models.ForeignKey(Comune, on_delete=models.CASCADE, blank=True, null=True)
    # Nel form fai in modo che il comune sia compilato sempre: necessario per lo scambio
    inprovincia = models.BooleanField(default=False)  # Se impostato a True, l'utente scambia in tutta la provincia
    tags = models.ManyToManyField('Tag')
    autore = models.OneToOneField(Autore, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Utenti'

    @property
    def immagine_url(self):
        if self.immagine:
            return self.immagine.url
        return static('img/iconadefault.jpg')


class Libro(models.Model):
    titolo = models.CharField(max_length=100)
    autori = models.ManyToManyField('Autore', related_name='libri')
    tags = models.ManyToManyField('Tag')
    trama = models.TextField(null=True, blank=True)
    numerovoti = models.IntegerField(default=0)
    mediavoti = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])

    class Meta:
        verbose_name_plural = 'Libri'

    def __str__(self):
        return self.titolo

    def aggiorna_valutazione(self, voto: int):
        self.numerovoti += 1
        self.mediavoti = ((self.mediavoti * (self.numerovoti - 1)) + voto) / self.numerovoti
        self.save()


class Recensione(models.Model):
    idlibro = models.ForeignKey(Libro, on_delete=models.PROTECT, related_name="recensioni")
    nomeutente = models.ForeignKey(Utente, on_delete=models.PROTECT)
    voto = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    commento = models.TextField(blank=True, null=True)
    data_aggiunta = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Recensioni'


class Nota(models.Model):
    nomeutente = models.ForeignKey(Utente, on_delete=models.CASCADE)
    idlibro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    messaggio = models.TextField()

    class Meta:
        verbose_name_plural = 'Note'


class ListaDesideri(models.Model):
    idlibro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    nomeutente = models.ForeignKey(Utente, on_delete=models.CASCADE)
    data_aggiunta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        intestazione = f'{self.idlibro},  {self.nomeutente}'
        return intestazione

    class Meta:
        unique_together = (('idlibro', 'nomeutente'),)
        verbose_name_plural = 'ListeDesideri'


class ListaScambio(models.Model):
    idlibro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    nomeutente = models.ForeignKey(Utente, on_delete=models.CASCADE)

    def __str__(self):
        intestazione = f'{self.idlibro},  {self.nomeutente}'
        return intestazione

    class Meta:
        unique_together = (('idlibro', 'nomeutente'),)
        verbose_name_plural = 'ListeScambio'


class Luogo(models.Model):
    via = models.CharField(max_length=50)
    comune = models.ForeignKey(Comune, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('via', 'comune'),)
        verbose_name_plural = 'Luoghi'

    def __str__(self):
        return f"{self.via}, {self.comune}, ({self.comune.provincia})"


class Evento(models.Model):
    idlibro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    autore = models.ForeignKey(Utente, on_delete=models.CASCADE)
    luogo = models.ForeignKey(Luogo, on_delete=models.CASCADE)
    date = models.DateField()
    descrizione = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Eventi'
