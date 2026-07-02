"""
python manage.py train_ml_models

Generates 2 years of synthetic Kigali restaurant demand data,
trains a Random Forest volume regressor and peak classifier,
and saves artefacts to ml/saved_models/.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Train ML order-volume and peak-period prediction models."

    def handle(self, *args, **options):
        from ml.train import train_and_save
        self.stdout.write("Starting ML training pipeline …\n")
        train_and_save(stdout=self.stdout)
        self.stdout.write(self.style.SUCCESS("\nModels trained and saved successfully."))
