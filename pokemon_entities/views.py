import folium
from django.shortcuts import render, get_object_or_404
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
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    current_time = localtime()
    filtered_pokemon = PokemonEntity.objects.filter(appeared_at__lte=current_time,
                                                    disappeared_at__gte=current_time)
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for entity in filtered_pokemon:
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
        pokemons_on_page.append({
            'pokemon_id': pokemon.pk,
            'img_url': img_url,
            'title_ru': pokemon.title})
    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon, pk=pokemon_id)

    if pokemon.evolution_from:
        pokemons_evolution_from = {
            'pokemon_id': pokemon.evolution_from.pk,
            'img_url': request.build_absolute_uri(pokemon.evolution_from.image.url),
            'title_ru': pokemon.evolution_from.title,
        }
    else:
        pokemons_evolution_from = {}
    if pokemon.evolutions.all():
        pokemons_evolution_to = {
            'pokemon_id': pokemon.evolutions.all()[0].pk,
            'img_url': pokemon.evolutions.all()[0].image.url,
            'title_ru': pokemon.evolutions.all()[0].title,
        }
    else:
        pokemons_evolution_to = {}
    img_url = request.build_absolute_uri(pokemon.image.url)
    pokemons_entities = {
        'pokemon_id': pokemon.pk,
        'img_url': img_url,
        'title_ru': pokemon.title,
        'description': pokemon.description,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'previous_evolution': pokemons_evolution_from,
        'next_evolution': pokemons_evolution_to
    }

    requested_pokemon_entities = pokemon.entities.all()
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in requested_pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            img_url
        )

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemons_entities
    })
