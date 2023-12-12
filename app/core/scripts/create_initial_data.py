"""Module for function-based creation of initial data

Intended to run after a new migration; not intended to be particularly efficient
Meant to be used instead of a fixture, in case table structure changes, as
functions can be re-written more easily than JSON files, and I don't want to
rely on dumpdata/loaddata if that happens.
"""

from core.models import *


def create_initial_records():
    """Creates minimal common data for a variety of models."""
    data = {
        'MusicAlbum': {},
        'MusicArtist': {},
        'Song': {},
        'Vehicle': {},
        'VehicleMake': {},
        'VehicleModel': {},
        'VehicleTrim': {},
        'VehicleYear': {}
    }
    data['VehicleMake'][1], _ = VehicleMake.objects.get_or_create(
        name='Toyota'
    )
    data['VehicleMake'][2], _ = VehicleMake.objects.get_or_create(
        name='Kia'
    )
    data['VehicleModel'][1], _ = VehicleModel.objects.get_or_create(
        name='Supra',
        vehicle_make=data['VehicleMake'][1]
    )
    data['VehicleModel'][2], _ = VehicleModel.objects.get_or_create(
        name='Forte',
        vehicle_make=data['VehicleMake'][2]
    )
    data['VehicleTrim'][1], _ = VehicleTrim.objects.get_or_create(
        name='Turbo',
        vehicle_model=data['VehicleModel'][1]
    )
    data['VehicleTrim'][2], _ = VehicleTrim.objects.get_or_create(
        name='EX',
        vehicle_model=data['VehicleModel'][2]
    )
    data['VehicleYear'][1], _ = VehicleYear.objects.get_or_create(
        vehicle_trim=data['VehicleTrim'][1],
        year=1997
    )
    data['VehicleYear'][2], _ = VehicleYear.objects.get_or_create(
        vehicle_trim=data['VehicleTrim'][2],
        year=2013
    )
    data['Vehicle'][1], _ = Vehicle.objects.get_or_create(
        vehicle_year=data['VehicleYear'][1],
        vin='JT2DE82A1V0038795'
    )
    data['Vehicle'][2], _ = Vehicle.objects.get_or_create(
        vehicle_year=data['VehicleYear'][2],
        vin='KNAFU4A21D5680051'
    )
    # Not uniquely constrained
    try:
        data['MusicAlbum'][1], _ = MusicAlbum.objects.get_or_create(
            title='Into The Electric Castle'
        )
    except MusicAlbum.MultipleObjectsReturned:
        pass
    try:
        data['MusicArtist'][1], _ = MusicArtist.objects.get_or_create(
            name='Ayreon'
        )
    except MusicArtist.MultipleObjectsReturned:
        pass
    try:
        data['Song'][1], _ = Song.objects.get_or_create(
            title='Isis And Osiris'
        )
    except Song.MultipleObjectsReturned:
        pass
