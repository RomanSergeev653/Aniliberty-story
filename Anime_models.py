from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AnimeType:
    value: str
    description: str


@dataclass
class AnimeName:
    main: str
    english: str
    alternative: str


@dataclass
class OptimizedPoster:
    src: str
    preview: str
    thumbnail: str


@dataclass
class Poster:
    optimized: OptimizedPoster


@dataclass
class AgeRating:
    value: str
    label: str
    is_adult: bool
    description: str


@dataclass
class Season:
    value: str
    description: str


@dataclass
class Genre:
    id: int
    name: str

@dataclass
class Anime:
    id: int
    type: AnimeType
    year: int
    name: AnimeName
    alias: str
    season: Season
    poster: Poster
    created_at: str
    is_ongoing: bool
    age_rating: AgeRating
    description: str
    episodes_total: int
    added_in_users_favorites: int
    added_in_planned_collection: int
    added_in_watched_collection: int
    added_in_watching_collection: int
    added_in_postponed_collection: int
    added_in_abandoned_collection: int
    genres: List[Genre]
    franchises: List[int]

    @classmethod
    def from_json(cls, json_data: Dict[str,Any]) -> 'Anime':
        genres_arr = []

        for gen in json_data['genres']:
            genres_arr.append(Genre(id=gen['id'],name=gen['name']))

        return cls(
            id=json_data['id'],
            type=AnimeType(
                value=json_data['type']['value'],
                description=json_data['type']['description']
            ),
            year=json_data['year'],
            name=AnimeName(
                main=json_data['name']['main'],
                english=json_data['name']['english'],
                alternative=json_data['name']['alternative']
            ),
            alias=json_data['alias'],
            season=Season(
                value=json_data['season']['value'],
                description=json_data['season']['description']
            ),
            poster=Poster(
                optimized=OptimizedPoster(
                    src=json_data['poster']['optimized']['src'],
                    preview=json_data['poster']['optimized']['preview'],
                    thumbnail=json_data['poster']['optimized']['thumbnail']
                )
            ),
            created_at=json_data['created_at'],
            is_ongoing=json_data['is_ongoing'],
            age_rating=AgeRating(
                value=json_data['age_rating']['value'],
                label=json_data['age_rating']['label'],
                is_adult=json_data['age_rating']['is_adult'],
                description=json_data['age_rating']['description'],
            ),
            description=json_data['description'],
            genres=genres_arr,
            episodes_total=json_data['episodes_total'],
            added_in_users_favorites=json_data['added_in_users_favorites'],
            added_in_planned_collection=json_data['added_in_planned_collection'],
            added_in_watched_collection=json_data['added_in_watched_collection'],
            added_in_watching_collection=json_data['added_in_watching_collection'],
            added_in_postponed_collection=json_data['added_in_postponed_collection'],
            added_in_abandoned_collection=json_data['added_in_abandoned_collection'],
            franchises=[]
        )

