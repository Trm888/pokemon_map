import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils.timezone import localtime

from .models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    pokemon_entity = PokemonEntity.objects.all() # Берем все экземпляры класса PokemonEntity
    current_time = localtime() # Текущее локальное время

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for entity in pokemon_entity:  # Перебираем все каждый экземляр в цикле
        # appeared_at = localtime(entity.appeared_at)
        # disappeared_at = localtime(entity.disappeared_at)
        # if current_time >= appeared_at and current_time <= disappeared_at:
        if PokemonEntity.objects.filter(appeared_at__lte=current_time, disappeared_at__gte=current_time): # фильтр для отображения действующих покемонов
            add_pokemon(
                folium_map, entity.lat,
                entity.lon,
                request.build_absolute_uri(entity.pokemon.image.url)
            )

    pokemons_on_page = []
    pokemons = Pokemon.objects.all()
    for pokemon in pokemons:
        if pokemon.image:
            img_url = request.build_absolute_uri(pokemon.image.url)
        else:
            img_url = pokemon.image
        pokemons_on_page.append({
            'pokemon_id': pokemon.pk,
            'img_url': img_url,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):

    pokemon = Pokemon.objects.get(pk=pokemon_id)

    if pokemon.id == int(pokemon_id):
        requested_pokemon = pokemon
    else:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    if requested_pokemon.evolution_from:
        pokemons_evolution_from_info = {
            'pokemon_id': requested_pokemon.evolution_from.pk,
            'img_url': request.build_absolute_uri(requested_pokemon.evolution_from.image.url),
            'title_ru': requested_pokemon.evolution_from.title,
        }
    else:
        pokemons_evolution_from_info = {}

    img_url = request.build_absolute_uri(requested_pokemon.image.url)
    pokemons_info = {
        'pokemon_id': requested_pokemon.pk,
        'img_url': img_url,
        'title_ru': requested_pokemon.title,
        'description': requested_pokemon.description,
        'title_en': requested_pokemon.title_en,
        'title_jp': requested_pokemon.title_jp,
        'previous_evolution': pokemons_evolution_from_info
    }



    requested_pokemon_entities = PokemonEntity.objects.filter(pokemon=requested_pokemon)
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in requested_pokemon_entities:

        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            img_url
        )

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemons_info
    })
